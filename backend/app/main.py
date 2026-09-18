import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.services.storage import storage
from app.services.scrapers import scraper
from app.routers.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await storage.initialize()
    asyncio.create_task(run_startup_sync())
    yield

async def run_startup_sync():
    try:
        await scraper.scrape_news()
        await scraper.scrape_insiders()
        await scraper.scrape_institutional()
        await scraper.scrape_macro()
    except Exception as e:
        print(f"Startup sync notice: {e}")

app = FastAPI(
    title="Money that matters — EGX",
    description="Mobile-first dashboard tracking smart money movements on the Egyptian Exchange",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Mount production React frontend SPA if built
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(os.path.join(dist_dir, "index.html")):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "app": "Money that matters — EGX",
            "status": "operational",
            "docs_url": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
