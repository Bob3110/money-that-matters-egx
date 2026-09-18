import os
import re
import pytest

def test_zero_fabricated_or_mock_sample_datasets():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_dir = os.path.dirname(backend_dir)
    prohibited_filenames = [
        "sample_data.py", "mock_data.py", "dummy_data.py", "fake_data.py", "fixtures.json",
        "mock_stocks.json", "sample_stocks.json", "demo_data.json"
    ]
    
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", ".pytest_cache", "dist")]
        for file in files:
            assert file.lower() not in prohibited_filenames, f"Prohibited mock file detected: {file}"

    app_dir = os.path.join(backend_dir, "app")
    suspicious_patterns = [
        r"def generate_fake_data",
        r"def generate_sample_data",
        r"def mock_database",
        r"MOCK_STOCKS\s*="
    ]
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in suspicious_patterns:
                        assert not re.search(pattern, content), f"Fabrication pattern {pattern} found in {file}!"
