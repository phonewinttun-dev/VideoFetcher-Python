import platform
import yt_dlp
from fastapi import APIRouter

from app.core.config import settings
from app.features.settings.schemas import (
    CookieValidateRequest,
    CookieValidateResponse,
    VersionResponse,
)

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("/version", response_model=VersionResponse)
def get_version_info() -> VersionResponse:
    """Return runtime information: app version, yt-dlp version, and FFmpeg detection status."""
    return VersionResponse(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        ytdlp_version=yt_dlp.version.__version__,
        python_version=platform.python_version(),
        ffmpeg_available=bool(settings.ffmpeg_location),
        ffmpeg_path=settings.ffmpeg_location,
    )


@router.post("/cookies/validate", response_model=CookieValidateResponse)
def validate_cookies(payload: CookieValidateRequest) -> CookieValidateResponse:
    """
    Validate whether the provided string conforms to the Netscape cookie file format.
    Extracts the list of associated domains.
    """
    raw = payload.cookies.strip()
    if not raw:
        return CookieValidateResponse(
            valid=False,
            entries_count=0,
            domains=[],
            message="Cookie text is empty.",
        )

    lines = raw.splitlines()
    valid_entries = 0
    domains = set()

    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        parts = line_str.split("\t")
        # Netscape standard requires 7 tab-separated fields:
        # domain, flag, path, secure, expiration, name, value
        if len(parts) >= 7:
            domain = parts[0].lstrip(".")
            if domain:
                domains.add(domain)
                valid_entries += 1
        elif len(line_str.split()) >= 7:
            # Fallback for space-separated copies
            domain = line_str.split()[0].lstrip(".")
            if domain:
                domains.add(domain)
                valid_entries += 1

    if valid_entries > 0:
        return CookieValidateResponse(
            valid=True,
            entries_count=valid_entries,
            domains=sorted(list(domains)),
            message=f"Valid Netscape cookies parsed: {valid_entries} entries across {len(domains)} domain(s).",
        )

    return CookieValidateResponse(
        valid=False,
        entries_count=0,
        domains=[],
        message="No valid Netscape format cookie entries found. Ensure values are tab-delimited.",
    )
