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

    # SSRF & Private IP rejection checks
    assert validate_url("http://127.0.0.1:10000/api/health") is False
    assert validate_url("http://localhost:8000") is False
    assert validate_url("http://169.254.169.254/latest/meta-data") is False
    assert validate_url("http://10.0.0.1/admin") is False
    assert validate_url("http://192.168.1.1/secret") is False
    assert validate_url("http://0.0.0.0/") is False
    assert validate_url("http://server.local/video") is False


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
        assert "domain\tTRUE\t/\tFALSE\t0\tname\tvalue" in created_path.read_text(encoding="utf-8")

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


def test_base_opts_youtube_bot_bypass_and_mp4() -> None:
    client = YTClient()
    opts = client._build_base_opts()

    # YouTube JS challenge and signature solving options
    assert "remote_components" in opts
    assert "ejs:github" in opts["remote_components"]

    # File size limit and socket timeout for Render stability
    assert opts["max_filesize"] == settings.MAX_FILE_SIZE_MB * 1024 * 1024
    assert opts["socket_timeout"] == 30

    # MP4 Output Enforcement when FFmpeg is present
    if client.ffmpeg_location:
        assert opts.get("merge_output_format") == "mp4"
        assert opts.get("remuxvideo") == "mp4"


@patch("yt_dlp.YoutubeDL")
def test_extract_metadata_video_resolution_and_audio_tiers(
    mock_ydl_class: MagicMock, sample_metadata: dict
) -> None:
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = sample_metadata
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    result = client.extract_metadata("https://youtube.com/watch?v=123")

    formats = result["formats"]
    format_ids = [f["format_id"] for f in formats]

    # Video options
    assert "best" in format_ids
    assert "video-720p" in format_ids
    assert "video-360p" in format_ids

    # 720p should appear before 360p (descending order)
    idx_720 = format_ids.index("video-720p")
    idx_360 = format_ids.index("video-360p")
    assert idx_720 < idx_360

    # Audio options
    assert "audio-m4a" in format_ids
    if client.ffmpeg_location:
        assert "audio-mp3-320" in format_ids
        assert "audio-mp3-192" in format_ids
        assert "audio-mp3-128" in format_ids


@patch("yt_dlp.YoutubeDL")
def test_download_media_video_resolution(mock_ydl_class: MagicMock) -> None:
    mock_instance = MagicMock()
    dummy_file = settings.TEMP_DIR / "test_download_720p.mp4"
    dummy_file.write_text("dummy 720p video content")

    mock_instance.extract_info.return_value = {
        "id": "vid720",
        "title": "720p Video",
    }
    mock_instance.prepare_filename.return_value = str(dummy_file)
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    file_path, display_name = client.download_media(
        url="https://youtube.com/watch?v=vid720",
        format_id="video-720p",
        is_audio=False,
    )

    # Verify that yt-dlp was called with format containing height<=720
    called_opts = mock_ydl_class.call_args[0][0]
    assert "height<=720" in called_opts["format"]
    assert display_name == "720p Video.mp4"

    if dummy_file.exists():
        dummy_file.unlink()


@patch("yt_dlp.YoutubeDL")
def test_download_media_audio_bitrate_selection(mock_ydl_class: MagicMock) -> None:
    mock_instance = MagicMock()
    dummy_file = settings.TEMP_DIR / "test_audio_320.mp3"
    dummy_file.write_text("dummy 320k mp3 content")

    mock_instance.extract_info.return_value = {
        "id": "aud320",
        "title": "My 320k Audio Track",
    }
    mock_instance.prepare_filename.return_value = str(dummy_file.with_suffix(".webm"))
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    client.ffmpeg_location = "/mock/ffmpeg"  # Mock FFmpeg availability
    file_path, display_name = client.download_media(
        url="https://youtube.com/watch?v=aud320",
        format_id="audio-mp3-320",
        is_audio=True,
    )

    called_opts = mock_ydl_class.call_args[0][0]
    assert called_opts["postprocessors"][0]["preferredquality"] == "320"
    assert called_opts["postprocessors"][0]["preferredcodec"] == "mp3"
    assert display_name == "My 320k Audio Track.mp3"

    if dummy_file.exists():
        dummy_file.unlink()


@patch("yt_dlp.YoutubeDL")
def test_download_media_audio_m4a_selection(mock_ydl_class: MagicMock) -> None:
    mock_instance = MagicMock()
    dummy_file = settings.TEMP_DIR / "test_audio_native.m4a"
    dummy_file.write_text("dummy m4a content")

    mock_instance.extract_info.return_value = {
        "id": "aud_m4a",
        "title": "Native M4A Audio",
    }
    mock_instance.prepare_filename.return_value = str(dummy_file)
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    file_path, display_name = client.download_media(
        url="https://youtube.com/watch?v=aud_m4a",
        format_id="audio-m4a",
        is_audio=True,
    )

    called_opts = mock_ydl_class.call_args[0][0]
    assert "bestaudio[ext=m4a]" in called_opts["format"]
    assert "postprocessors" not in called_opts
    assert display_name == "Native M4A Audio.m4a"

    if dummy_file.exists():
        dummy_file.unlink()


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


def test_base_opts_youtube_player_clients_and_proxy() -> None:
    client = YTClient()
    opts = client._build_base_opts()

    # YouTube Innertube client fallback
    assert "extractor_args" in opts
    assert "youtube" in opts["extractor_args"]
    assert "player_client" in opts["extractor_args"]["youtube"]
    clients = opts["extractor_args"]["youtube"]["player_client"]
    assert "default" in clients
    assert "-tv" in clients
    assert "web_embedded" in clients


def test_normalize_netscape_cookies() -> None:
    from app.core.yt_client import normalize_netscape_cookies
    raw = ".youtube.com TRUE / TRUE 1899999999 TEST 123"
    normalized = normalize_netscape_cookies(raw)
    assert "# Netscape HTTP Cookie File" in normalized
    assert ".youtube.com\tTRUE\t/\tTRUE\t1899999999\tTEST\t123" in normalized


def test_format_metadata_float_duration() -> None:
    client = YTClient()
    info = {
        "id": "float_dur",
        "title": "Float Duration Media",
        "duration": 213.886,
        "extractor": "soundcloud",
        "formats": [],
    }
    result = client._format_metadata(info)
    assert isinstance(result["duration"], int)
    assert result["duration"] == 214
