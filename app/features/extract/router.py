from fastapi import APIRouter, HTTPException, status
from yt_dlp.utils import DownloadError, ExtractorError

from app.core.yt_client import yt_client
from app.features.extract.schemas import ExtractRequest, MediaMetadataResponse

router = APIRouter(prefix="/api/extract", tags=["Extraction"])


def format_extractor_error(err: Exception) -> str:
    """Format yt-dlp error into a clean, actionable message."""
    raw = str(err)
    clean_msg = raw.split("ERROR:")[-1].strip()
    msg_lower = clean_msg.lower()

    if (
        "failed to extract any player response" in msg_lower
        or "confirm you're not a bot" in msg_lower
        or "sign in to confirm" in msg_lower
        or "bot detection" in msg_lower
    ):
        return (
            "YouTube blocked requests from this server's cloud IP (common on Render / AWS). "
            "To resolve: Open Settings (gear icon) in the header to add your browser cookies, "
            "or configure YOUTUBE_COOKIES / PROXY in your server's environment variables."
        )

    return clean_msg or "Failed to extract media information from this URL."


@router.post("", response_model=MediaMetadataResponse)
def extract_metadata(payload: ExtractRequest) -> MediaMetadataResponse:
    """
    Extract title, thumbnail, duration, and available format options from a media URL.
    Supports optional Netscape cookies and custom User-Agent.
    """
    try:
        data = yt_client.extract_metadata(
            url=payload.url,
            cookies=payload.cookies,
            user_agent=payload.user_agent,
        )
        return MediaMetadataResponse(**data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except (DownloadError, ExtractorError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=format_extractor_error(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during extraction: {str(e)}",
        )
