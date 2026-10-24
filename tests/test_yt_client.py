from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from yt_dlp.utils import DownloadError

from app.core.config import settings
from app.core.yt_client import (
    YTClient,
    ephemeral_cookie_file,
    sanitize_filename,
    validate_url,
)


def test_validate_url() -> None:
    assert validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
    assert validate_url("http://tiktok.com/@user/video/123") is True
    assert validate_url("ftp://example.com/file") is False
    assert validate_url("just a string") is False
    assert validate_url("") is False
    assert validate_url(None) is False  # type: ignore


def test_sanitize_filename() -> None:
    raw = 'Hello / World : Video * Test ? "Nice" <One> | Yeah!'
    clean = sanitize_filename(raw)
    assert "/" not in clean
    assert ":" not in clean
    assert "*" not in clean
    assert "?" not in clean
    assert '"' not in clean
    assert "<" not in clean
    assert ">" not in clean
    assert "|" not in clean
    assert clean == "Hello  World  Video  Test  Nice One  Yeah!"

    # Empty fallback
    assert sanitize_filename("...///???") == "download"


def test_ephemeral_cookie_file() -> None:
    # None or empty string does not create a file
    with ephemeral_cookie_file(None) as path:
        assert path is None

    with ephemeral_cookie_file("   ") as path:
        assert path is None

    content = "domain\tTRUE\t/\tFALSE\t0\tname\tvalue\n"
    created_path = None
    with ephemeral_cookie_file(content) as path:
        assert path is not None
        created_path = Path(path)
        assert created_path.exists()
        assert created_path.read_text(encoding="utf-8") == content

    # Should be deleted once context exits
    assert not created_path.exists()


def test_extract_metadata_invalid_url() -> None:
    client = YTClient()
    with pytest.raises(ValueError, match="Invalid URL"):
        client.extract_metadata("not-a-valid-url")


@patch("yt_dlp.YoutubeDL")
def test_extract_metadata_success(mock_ydl_class: MagicMock, sample_metadata: dict) -> None:
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = sample_metadata
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    result = client.extract_metadata("https://youtube.com/watch?v=123")

    assert result["id"] == "test_video_123"
    assert result["title"] == "Sample Test Video"
    assert result["duration"] == 120
    assert result["extractor"] == "youtube"
    assert len(result["formats"]) >= 2
    # Check that audio format option is always present
    assert any(f["is_audio"] for f in result["formats"])


@patch("yt_dlp.YoutubeDL")
def test_extract_metadata_download_error(mock_ydl_class: MagicMock) -> None:
    mock_instance = MagicMock()
    mock_instance.extract_info.side_effect = DownloadError("Video is private")
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    with pytest.raises(DownloadError):
        client.extract_metadata("https://youtube.com/watch?v=private")


@patch("yt_dlp.YoutubeDL")
def test_download_media_success(mock_ydl_class: MagicMock) -> None:
    mock_instance = MagicMock()
    # Create an actual dummy temp file
    dummy_file = settings.TEMP_DIR / "test_download.mp4"
    dummy_file.write_text("dummy media content")

    mock_instance.extract_info.return_value = {
        "id": "abc123",
        "title": "My Downloaded Video",
    }
    mock_instance.prepare_filename.return_value = str(dummy_file)
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    file_path, display_name = client.download_media(
        url="https://youtube.com/watch?v=abc123",
        format_id="best",
        is_audio=False,
    )

    assert file_path.exists()
    assert display_name == "My Downloaded Video.mp4"

    # Cleanup the dummy file
    if dummy_file.exists():
        dummy_file.unlink()
