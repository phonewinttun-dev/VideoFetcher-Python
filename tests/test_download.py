from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.core.config import settings


def test_download_post_success(client: TestClient) -> None:
    # Create a real test file in TEMP_DIR
    temp_file = settings.TEMP_DIR / "test_run_post.mp4"
    temp_file.write_bytes(b"sample video bytes")

    with patch(
        "app.core.yt_client.yt_client.download_media",
        return_value=(temp_file, "Clean Title.mp4"),
    ):
        resp = client.post(
            "/api/download",
            json={
                "url": "https://www.youtube.com/watch?v=123",
                "format_id": "best",
                "is_audio": False,
            },
        )
        assert resp.status_code == 200
        assert resp.content == b"sample video bytes"
        assert 'attachment; filename="Clean Title.mp4"' in resp.headers["content-disposition"]

        # Verify background cleanup removed the temporary file
        assert not temp_file.exists()


def test_download_get_shortcut_success(client: TestClient) -> None:
    temp_file = settings.TEMP_DIR / "test_run_get.mp3"
    temp_file.write_bytes(b"sample audio bytes")

    with patch(
        "app.core.yt_client.yt_client.download_media",
        return_value=(temp_file, "Audio Track.mp3"),
    ):
        # Query parameter invocation as used by iOS Shortcuts
        resp = client.get(
            "/api/download?url=https://www.youtube.com/watch?v=123&type=audio",
        )
        assert resp.status_code == 200
        assert resp.content == b"sample audio bytes"
        assert 'attachment; filename="Audio Track.mp3"' in resp.headers["content-disposition"]

        # Background cleanup check
        assert not temp_file.exists()


def test_download_invalid_url(client: TestClient) -> None:
    resp = client.post(
        "/api/download",
        json={"url": "invalid_url"},
    )
    assert resp.status_code == 400
    assert "Invalid URL" in resp.json()["detail"]
