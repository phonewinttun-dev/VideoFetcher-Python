from unittest.mock import patch
from fastapi.testclient import TestClient
from yt_dlp.utils import DownloadError


def test_extract_endpoint_success(client: TestClient) -> None:
    fake_extracted = {
        "id": "123",
        "title": "FastAPI Video",
        "thumbnail": "https://example.com/pic.jpg",
        "duration": 60,
        "extractor": "youtube",
        "webpage_url": "https://youtube.com/watch?v=123",
        "formats": [
            {
                "format_id": "best",
                "label": "Best Available",
                "resolution": "Original / Best",
                "ext": "mp4",
                "filesize_approx": 1000000,
                "is_audio": False,
            }
        ],
    }

    with patch("app.core.yt_client.yt_client.extract_metadata", return_value=fake_extracted):
        resp = client.post(
            "/api/extract",
            json={"url": "https://www.youtube.com/watch?v=123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "FastAPI Video"
        assert data["duration"] == 60
        assert len(data["formats"]) == 1


def test_extract_endpoint_invalid_url(client: TestClient) -> None:
    resp = client.post("/api/extract", json={"url": "ftp://not-supported"})
    assert resp.status_code == 400
    assert "Invalid URL format" in resp.json()["detail"]


def test_extract_endpoint_download_error(client: TestClient) -> None:
    with patch(
        "app.core.yt_client.yt_client.extract_metadata",
        side_effect=DownloadError("ERROR: Video is private or deleted"),
    ):
        resp = client.post(
            "/api/extract",
            json={"url": "https://youtube.com/watch?v=private"},
        )
        assert resp.status_code == 400
        assert "Video is private or deleted" in resp.json()["detail"]


def test_extract_endpoint_youtube_player_response_error(client: TestClient) -> None:
    with patch(
        "app.core.yt_client.yt_client.extract_metadata",
        side_effect=DownloadError("ERROR: [youtube] 5B-8lHmi74k: Failed to extract any player response"),
    ):
        resp = client.post(
            "/api/extract",
            json={"url": "https://youtube.com/watch?v=5B-8lHmi74k"},
        )
        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert "YouTube blocked requests from this server's cloud IP" in detail
        assert "Settings" in detail
