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
    from app.core.yt_client import _METADATA_CACHE
    _METADATA_CACHE.clear()

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


@pytest.mark.parametrize("has_ffmpeg", [True, False])
def test_base_opts_youtube_bot_bypass_and_mp4(has_ffmpeg: bool) -> None:
    client = YTClient()
    with patch.object(client, "ffmpeg_location", "/mock/ffmpeg" if has_ffmpeg else None):
        opts = client._build_base_opts()

        # File size limit, socket timeout, and HTTP chunk size for throughput
        assert opts["max_filesize"] == settings.MAX_FILE_SIZE_MB * 1024 * 1024
        assert opts["socket_timeout"] == 30
        assert opts["http_chunk_size"] == 10485760

        # Safe container format when FFmpeg is present
        if has_ffmpeg:
            assert opts.get("merge_output_format") == "mp4/mkv"
            assert "remuxvideo" not in opts
        else:
            assert "merge_output_format" not in opts
            assert "remuxvideo" not in opts


@patch("yt_dlp.YoutubeDL")
def test_extract_metadata_video_resolution_and_audio_tiers(
    mock_ydl_class: MagicMock, sample_metadata: dict
) -> None:
    from app.core.yt_client import _METADATA_CACHE
    _METADATA_CACHE.clear()

    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = sample_metadata
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    client.ffmpeg_location = "/mock/ffmpeg"  # Deterministic FFmpeg presence
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
    audio_formats = [f for f in formats if f["is_audio"]]
    for af in audio_formats:
        assert af["filesize_approx"] is not None
        assert af["filesize_approx"] > 0

    assert "audio-mp3-320" in format_ids
    assert "audio-mp3-192" in format_ids
    assert "audio-mp3-128" in format_ids

    # Check MP3 sizes follow bitrate ordering (320 > 192 > 128)
    mp3_sizes = {f["format_id"]: f["filesize_approx"] for f in audio_formats}
    assert mp3_sizes["audio-mp3-320"] > mp3_sizes["audio-mp3-192"] > mp3_sizes["audio-mp3-128"]


@patch("yt_dlp.YoutubeDL")
def test_download_media_video_resolution(
    mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "TEMP_DIR", tmp_path)
    mock_instance = MagicMock()
    dummy_file = tmp_path / "test_download_720p.mp4"
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


@patch("yt_dlp.YoutubeDL")
def test_download_media_audio_bitrate_selection(
    mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "TEMP_DIR", tmp_path)
    mock_instance = MagicMock()
    dummy_file = tmp_path / "test_audio_320.mp3"
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


@patch("yt_dlp.YoutubeDL")
def test_download_media_audio_m4a_selection(
    mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "TEMP_DIR", tmp_path)
    mock_instance = MagicMock()
    dummy_file = tmp_path / "test_audio_native.m4a"
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


@patch("yt_dlp.YoutubeDL")
def test_extract_metadata_download_error(mock_ydl_class: MagicMock) -> None:
    from app.core.yt_client import _METADATA_CACHE
    _METADATA_CACHE.clear()

    mock_instance = MagicMock()
    mock_instance.extract_info.side_effect = DownloadError("Video is private")
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    client = YTClient()
    with pytest.raises(DownloadError):
        client.extract_metadata("https://youtube.com/watch?v=private")


@patch("yt_dlp.YoutubeDL")
def test_download_media_success(
    mock_ydl_class: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "TEMP_DIR", tmp_path)
    mock_instance = MagicMock()
    dummy_file = tmp_path / "test_download.mp4"
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


def test_base_opts_youtube_player_clients_and_proxy() -> None:
    client = YTClient()
    opts = client._build_base_opts()

    # YouTube Innertube client fallback
    assert "extractor_args" in opts
    assert "youtube" in opts["extractor_args"]
    assert "player_client" in opts["extractor_args"]["youtube"]
    clients = opts["extractor_args"]["youtube"]["player_client"]
    assert "web" in clients
    assert "tv_samsung" in clients or "default" in clients


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


def test_audio_filesize_approx_calculation() -> None:
    client = YTClient()
    # Case 1: Formats with exact audio filesize
    info_with_audio_streams = {
        "id": "test_audio_sizes",
        "title": "Audio Sizing Test",
        "duration": 60,
        "extractor": "youtube",
        "formats": [
            {
                "format_id": "140",
                "ext": "m4a",
                "vcodec": "none",
                "acodec": "mp4a.40.2",
                "abr": 128,
                "filesize": 960000,
            },
            {
                "format_id": "251",
                "ext": "webm",
                "vcodec": "none",
                "acodec": "opus",
                "abr": 160,
                "filesize": 1200000,
            },
        ],
    }
    client.ffmpeg_location = "/mock/ffmpeg"  # Deterministic test
    res1 = client._format_metadata(info_with_audio_streams)
    audio_map1 = {f["format_id"]: f["filesize_approx"] for f in res1["formats"] if f["is_audio"]}

    # M4A should preserve the stream's exact filesize
    assert audio_map1["audio-m4a"] == 960000
    # MP3 320 kbps: 60s * 320 * 1000 / 8 = 2,400,000
    assert audio_map1["audio-mp3-320"] == 2400000
    # MP3 192 kbps: 60s * 192 * 1000 / 8 = 1,440,000
    assert audio_map1["audio-mp3-192"] == 1440000
    # MP3 128 kbps: 60s * 128 * 1000 / 8 = 960,000
    assert audio_map1["audio-mp3-128"] == 960000

    # Case 2: Zero duration media (e.g. live stream or unknown duration)
    info_zero_dur = {
        "id": "zero_dur",
        "title": "Live Stream",
        "duration": 0,
        "extractor": "youtube",
        "formats": [],
    }
    res2 = client._format_metadata(info_zero_dur)
    for f in res2["formats"]:
        if f["is_audio"]:
            assert f["filesize_approx"] is None
