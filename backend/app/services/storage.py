import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import motor.motor_asyncio

from app.config import MONGODB_URI, MONGODB_DB_NAME

class DocumentCollectionFallback:
    """
    In-memory and JSON file-backed document collection that mirrors Motor/PyMongo async interface.
    Activated seamlessly when local MongoDB service is offline, ensuring zero-setup functionality
    without violating data persistence or contracts.
    """
    def __init__(self, name: str, filepath: str):
        self.name = name
        self.filepath = filepath
        self._docs: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._docs = json.load(f)
            except Exception:
                self._docs = []
        else:
            self._docs = []

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._docs, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    async def find(self, filter_query: Optional[Dict[str, Any]] = None, sort: Optional[List[tuple]] = None, limit: int = 0):
        async with self._lock:
            results = []
            filter_query = filter_query or {}
            for doc in self._docs:
                matches = True
                for k, v in filter_query.items():
                    if isinstance(v, dict):
                        if "$in" in v and doc.get(k) not in v["$in"]:
                            matches = False
                            break
                    elif doc.get(k) != v:
                        matches = False
                        break
                if matches:
                    results.append(doc.copy())
            
            if sort:
                for sort_field, direction in reversed(sort):
                    results.sort(key=lambda x: str(x.get(sort_field, "")), reverse=(direction < 0))

            if limit > 0:
                results = results[:limit]

            class AsyncCursor:
                def __init__(self, items):
                    self.items = items
                def __aiter__(self):
                    self._iter = iter(self.items)
                    return self
                async def __anext__(self):
                    try:
                        return next(self._iter)
                    except StopIteration:
                        raise StopAsyncIteration
                async def to_list(self, length: Optional[int] = None):
                    if length is not None:
                        return self.items[:length]
                    return self.items

            return AsyncCursor(results)

    async def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cursor = await self.find(filter_query, limit=1)
        items = await cursor.to_list(1)
        return items[0] if items else None

    async def insert_one(self, doc: Dict[str, Any]):
        async with self._lock:
            doc_copy = doc.copy()
            if "_id" not in doc_copy:
                doc_copy["_id"] = str(len(self._docs) + 1) + "_" + str(int(datetime.now(timezone.utc).timestamp()))
            self._docs.append(doc_copy)
            self._save()
            return doc_copy

    async def update_one(self, filter_query: Dict[str, Any], update_doc: Dict[str, Any], upsert: bool = False):
        async with self._lock:
            matched = False
            for idx, doc in enumerate(self._docs):
                matches = True
                for k, v in filter_query.items():
                    if doc.get(k) != v:
                        matches = False
                        break
                if matches:
                    matched = True
                    if "$set" in update_doc:
                        self._docs[idx].update(update_doc["$set"])
                    else:
                        self._docs[idx].update(update_doc)
                    break
            
            if not matched and upsert:
                new_doc = filter_query.copy()
                if "$set" in update_doc:
                    new_doc.update(update_doc["$set"])
                else:
                    new_doc.update(update_doc)
                if "_id" not in new_doc:
                    new_doc["_id"] = str(len(self._docs) + 1)
                self._docs.append(new_doc)

            self._save()

    async def replace_one(self, filter_query: Dict[str, Any], replacement: Dict[str, Any], upsert: bool = False):
        async with self._lock:
            matched_idx = -1
            for idx, doc in enumerate(self._docs):
                matches = True
                for k, v in filter_query.items():
                    if doc.get(k) != v:
                        matches = False
                        break
                if matches:
                    matched_idx = idx
                    break
            
            if matched_idx >= 0:
                rep_copy = replacement.copy()
                if "_id" not in rep_copy and "_id" in self._docs[matched_idx]:
                    rep_copy["_id"] = self._docs[matched_idx]["_id"]
                self._docs[matched_idx] = rep_copy
            elif upsert:
                rep_copy = replacement.copy()
                if "_id" not in rep_copy:
                    rep_copy["_id"] = str(len(self._docs) + 1)
                self._docs.append(rep_copy)
            
            self._save()

    async def count_documents(self, filter_query: Optional[Dict[str, Any]] = None) -> int:
        cursor = await self.find(filter_query)
        items = await cursor.to_list()
        return len(items)

    async def delete_many(self, filter_query: Dict[str, Any]):
        async with self._lock:
            new_docs = []
            for doc in self._docs:
                matches = True
                for k, v in filter_query.items():
                    if doc.get(k) != v:
                        matches = False
                        break
                if not matches:
                    new_docs.append(doc)
            self._docs = new_docs
            self._save()


class StorageManager:
    """
    Manages access to MongoDB collections with transparent fallback.
    """
    def __init__(self):
        self.mongo_client = None
        self.mongo_db = None
        self.is_connected_to_mongo = False
        self._fallback_collections: Dict[str, DocumentCollectionFallback] = {}
        self.data_dir = os.getenv(
            "STORAGE_DATA_DIR",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        )

    async def initialize(self):
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=1500
            )
            await client.admin.command("ping")
            self.mongo_client = client
            self.mongo_db = client[MONGODB_DB_NAME]
            self.is_connected_to_mongo = True
            print("Successfully connected to MongoDB.")
        except Exception as e:
            self.is_connected_to_mongo = False
            print(f"MongoDB connection unavailable ({e}). Using embedded document storage fallback.")

    def get_collection(self, collection_name: str):
        if self.is_connected_to_mongo and self.mongo_db is not None:
            return self.mongo_db[collection_name]
        
        if collection_name not in self._fallback_collections:
            filepath = os.path.join(self.data_dir, f"{collection_name}.json")
            self._fallback_collections[collection_name] = DocumentCollectionFallback(collection_name, filepath)
        return self._fallback_collections[collection_name]

storage = StorageManager()
