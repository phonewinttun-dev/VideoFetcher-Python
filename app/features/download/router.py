import os
import threading
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from fastapi.responses import FileResponse
from yt_dlp.utils import DownloadError, ExtractorError

from app.core.yt_client import yt_client
from app.features.download.schemas import DownloadRequest
from app.features.extract.router import format_extractor_error

router = APIRouter(prefix="/api/download", tags=["Download"])

# Restrict to strictly 1 active download at a time to prevent CPU spikes and Out-Of-Memory (OOM) crashes on Render Free Tier (512MB RAM)
DOWNLOAD_SEMAPHORE = threading.BoundedSemaphore(1)


def cleanup_temp_file(file_path: str) -> None:
    """Delete the temporary download file once the response stream finishes."""
    try:
        p = Path(file_path)
        if p.exists():
            p.unlink()
    except OSError:
        pass


def build_file_response(
    file_path: Path,
    display_filename: str,
    background_tasks: BackgroundTasks,
) -> FileResponse:
    """Create a FileResponse configured for forced attachment download on iOS and desktop."""
    background_tasks.add_task(cleanup_temp_file, str(file_path))

    # UTF-8 encoded filename for Content-Disposition header compatibility
    ascii_filename = display_filename.encode("ascii", "ignore").decode("ascii") or "media_download"
    encoded_filename = quote(display_filename)

    headers = {
        "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    return FileResponse(
        path=str(file_path),
        filename=display_filename,
        media_type="application/octet-stream",
        headers=headers,
        background=background_tasks,
    )


@router.post("")
def download_media_post(
    payload: DownloadRequest,
    background_tasks: BackgroundTasks,
) -> FileResponse:
    """
    Download media based on JSON payload and stream it directly as an attachment.
    Auto-cleans the temporary server file upon completion.
    """
    if not DOWNLOAD_SEMAPHORE.acquire(blocking=False):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Server is currently processing other downloads. Please try again shortly.",
        )

    try:
        file_path, display_filename = yt_client.download_media(
            url=payload.url,
            format_id=payload.format_id,
            is_audio=payload.is_audio,
            cookies=payload.cookies,
            user_agent=payload.user_agent,
        )
        return build_file_response(file_path, display_filename, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (DownloadError, ExtractorError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=format_extractor_error(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected download error occurred: {str(e)}",
        )
    finally:
        DOWNLOAD_SEMAPHORE.release()


@router.get("")
def download_media_get(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="Target video or media URL"),
    type: str | None = Query(default=None, description="Media type: 'video' or 'audio'"),
    format_id: str | None = Query(default=None, description="Requested format ID"),
    is_audio: bool = Query(default=False, description="Whether to extract audio only"),
    cookies: str | None = Query(default=None, description="Optional Netscape format cookies"),
    user_agent: str | None = Query(default=None, description="Optional custom User-Agent"),
) -> FileResponse:
    """
    Direct GET download endpoint for iOS Shortcuts and external URL query integrations.
    Example: /api/download?url=https://youtube.com/watch?v=...&type=video
    """
    effective_is_audio = is_audio or (type is not None and type.lower() == "audio")

    if not DOWNLOAD_SEMAPHORE.acquire(blocking=False):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Server is currently processing other downloads. Please try again shortly.",
        )

    try:
        file_path, display_filename = yt_client.download_media(
            url=url,
            format_id=format_id,
            is_audio=effective_is_audio,
            cookies=cookies,
            user_agent=user_agent,
        )
        return build_file_response(file_path, display_filename, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (DownloadError, ExtractorError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=format_extractor_error(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected download error occurred: {str(e)}",
        )
    finally:
        DOWNLOAD_SEMAPHORE.release()
