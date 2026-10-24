from pydantic import BaseModel, Field


class VersionResponse(BaseModel):
    app_name: str
    app_version: str
    ytdlp_version: str
    python_version: str
    ffmpeg_available: bool
    ffmpeg_path: str | None = None


class CookieValidateRequest(BaseModel):
    cookies: str = Field(..., description="Netscape-format cookies text content")


class CookieValidateResponse(BaseModel):
    valid: bool
    entries_count: int = 0
    domains: list[str] = []
    message: str
