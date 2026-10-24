import contextlib
import re
import uuid
from pathlib import Path
from typing import Any, Generator
from urllib.parse import urlparse

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

from app.core.config import settings


def sanitize_filename(filename: str) -> str:
    """Sanitize string to be safe for filenames across operating systems."""
    # Remove control characters, quotes, and invalid filename characters
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Strip leading/trailing dots and spaces
    cleaned = cleaned.strip(". ")
    return cleaned or "download"


def validate_url(url: str) -> bool:
    """Validate if the given string is a valid HTTP/HTTPS URL."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


@contextlib.contextmanager
def ephemeral_cookie_file(cookie_content: str | None) -> Generator[str | None, None, None]:
    """
    Context manager that temporarily writes Netscape cookie content to a file
    and guarantees its deletion when the context exits.
    """
    if not cookie_content or not cookie_content.strip():
        yield None
        return

    cookie_path = settings.TEMP_DIR / f"cookie_{uuid.uuid4().hex}.txt"
    try:
        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write(cookie_content)
        yield str(cookie_path)
    finally:
        if cookie_path.exists():
            try:
                cookie_path.unlink()
            except OSError:
                pass


class YTClient:
    """Core wrapper around yt-dlp providing metadata extraction and download services."""

    def __init__(self) -> None:
        self.ffmpeg_location = settings.ffmpeg_location

    def _build_base_opts(
        self,
        cookie_path: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "user_agent": user_agent or settings.DEFAULT_USER_AGENT,
        }
        if cookie_path:
            opts["cookiefile"] = cookie_path
        if self.ffmpeg_location:
            opts["ffmpeg_location"] = self.ffmpeg_location
        return opts

    def extract_metadata(
        self,
        url: str,
        cookies: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        """
        Extract video metadata, thumbnail, duration, and clean format options.
        Raises ValueError if URL is invalid, or DownloadError if extraction fails.
        """
        if not validate_url(url):
            raise ValueError("Invalid URL format. Please provide a valid HTTP/HTTPS link.")

        with ephemeral_cookie_file(cookies) as cookie_path:
            opts = self._build_base_opts(cookie_path, user_agent)
            opts["skip_download"] = True

            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except (DownloadError, ExtractorError) as e:
                    raise e
                except Exception as e:
                    raise DownloadError(f"Extraction failed: {str(e)}")

        if not info:
            raise DownloadError("Failed to extract media information from URL.")

        # If it was a playlist or multiple entries, pick the first
        if "entries" in info and info["entries"]:
            info = info["entries"][0]

        return self._format_metadata(info)

    def _format_metadata(self, info: dict[str, Any]) -> dict[str, Any]:
        """Format raw yt-dlp info into a clean, client-ready structure."""
        title = info.get("title") or "Untitled Media"
        duration = info.get("duration") or 0
        thumbnail = info.get("thumbnail")
        extractor = info.get("extractor") or info.get("extractor_key") or "generic"
        media_id = str(info.get("id") or uuid.uuid4().hex[:8])

        # Extract & simplify formats
        formats_list: list[dict[str, Any]] = []
        raw_formats = info.get("formats", [])

        has_ffmpeg = bool(self.ffmpeg_location)

        # Standard Video Formats to offer
        # 1. Best Quality (Default)
        formats_list.append({
            "format_id": "best",
            "label": "Best Available Quality",
            "resolution": "Original / Best",
            "ext": "mp4",
            "filesize_approx": info.get("filesize") or info.get("filesize_approx"),
            "is_audio": False,
        })

        # Add distinct available video resolutions if present
        seen_heights = set()
        for f in reversed(raw_formats):
            vcodec = f.get("vcodec")
            if vcodec == "none":
                continue
            height = f.get("height")
            if not height or height in seen_heights or height < 240:
                continue
            seen_heights.add(height)

            label = f"{height}p"
            f_id = f.get("format_id", "")
            ext = f.get("ext", "mp4")
            # If no FFmpeg, prefer formats that have both video and audio
            if not has_ffmpeg and f.get("acodec") == "none":
                continue

            formats_list.append({
                "format_id": f_id or f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
                "label": f"Video ({label})",
                "resolution": label,
                "ext": ext if ext in ("mp4", "webm") else "mp4",
                "filesize_approx": f.get("filesize") or f.get("filesize_approx"),
                "is_audio": False,
            })

        # Audio-only options
        audio_ext = "mp3" if has_ffmpeg else "m4a"
        formats_list.append({
            "format_id": "bestaudio",
            "label": f"Audio Only ({audio_ext.upper()})",
            "resolution": "Audio",
            "ext": audio_ext,
            "filesize_approx": None,
            "is_audio": True,
        })

        return {
            "id": media_id,
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration,
            "extractor": extractor,
            "webpage_url": info.get("webpage_url", ""),
            "formats": formats_list,
        }

    def download_media(
        self,
        url: str,
        format_id: str | None = None,
        is_audio: bool = False,
        cookies: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[Path, str]:
        """
        Download media file to the temporary directory.
        Returns a tuple of (local_file_path, display_filename).
        """
        if not validate_url(url):
            raise ValueError("Invalid URL format.")

        download_id = uuid.uuid4().hex[:10]
        outtmpl = str(settings.TEMP_DIR / f"{download_id}_%(title).100s.%(ext)s")

        with ephemeral_cookie_file(cookies) as cookie_path:
            opts = self._build_base_opts(cookie_path, user_agent)
            opts["outtmpl"] = outtmpl
            opts["restrictfilenames"] = True

            has_ffmpeg = bool(self.ffmpeg_location)

            if is_audio:
                if has_ffmpeg:
                    opts["format"] = "bestaudio/best"
                    opts["postprocessors"] = [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }]
                else:
                    opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
            else:
                if format_id and format_id != "best":
                    if has_ffmpeg:
                        opts["format"] = f"{format_id}+bestaudio/best"
                    else:
                        opts["format"] = f"{format_id}/best[vcodec!=none][acodec!=none]/best"
                else:
                    if has_ffmpeg:
                        opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
                    else:
                        opts["format"] = "best[ext=mp4]/best[vcodec!=none][acodec!=none]/best"

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise DownloadError("Download failed: No information returned.")

                # Locate the downloaded file
                target_filename = ydl.prepare_filename(info)

                # If postprocessed (e.g. mp3 conversion), the extension might have changed
                expected_path = Path(target_filename)
                if is_audio and has_ffmpeg:
                    expected_path = expected_path.with_suffix(".mp3")

                # If not found directly, check by prefix in TEMP_DIR
                if not expected_path.exists():
                    matches = list(settings.TEMP_DIR.glob(f"{download_id}_*"))
                    if matches:
                        expected_path = matches[0]
                    else:
                        raise DownloadError("Downloaded file could not be located on server.")

                # Prepare a clean human-readable download filename
                title = sanitize_filename(info.get("title") or "download")
                display_filename = f"{title}{expected_path.suffix}"

                return expected_path, display_filename


yt_client = YTClient()
