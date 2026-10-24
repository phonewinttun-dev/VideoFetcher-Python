from fastapi import APIRouter, HTTPException, status
from yt_dlp.utils import DownloadError, ExtractorError

from app.core.yt_client import yt_client
from app.features.extract.schemas import ExtractRequest, MediaMetadataResponse

router = APIRouter(prefix="/api/extract", tags=["Extraction"])


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
        # Provide a clean error message without traceback dumps
        clean_msg = str(e).split("ERROR:")[-1].strip()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=clean_msg or "Failed to extract media information from this URL.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during extraction: {str(e)}",
        )
