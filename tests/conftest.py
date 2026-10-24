import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure VideoFetcher-Python is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_metadata() -> dict:
    return {
        "id": "test_video_123",
        "title": "Sample Test Video",
        "thumbnail": "https://example.com/thumb.jpg",
        "duration": 120,
        "extractor": "youtube",
        "webpage_url": "https://example.com/watch?v=123",
        "formats": [
            {
                "format_id": "18",
                "ext": "mp4",
                "height": 360,
                "vcodec": "avc1",
                "acodec": "mp4a",
                "filesize": 5000000,
            },
            {
                "format_id": "22",
                "ext": "mp4",
                "height": 720,
                "vcodec": "avc1",
                "acodec": "mp4a",
                "filesize": 15000000,
            },
        ],
    }


@pytest.fixture
def valid_netscape_cookie() -> str:
    return (
        "# Netscape HTTP Cookie File\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1750000000\tSID\tDUMMY_SYNTHETIC_COOKIE_VALUE_123\n"
        ".tiktok.com\tTRUE\t/\tTRUE\t1750000000\tsessionid\tDUMMY_SYNTHETIC_COOKIE_VALUE_456\n"
    )
