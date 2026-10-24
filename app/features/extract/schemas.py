from pydantic import BaseModel, HttpUrl, Field


class ExtractRequest(BaseModel):
    url: str = Field(..., description="Target video or media URL")
    cookies: str | None = Field(default=None, description="Optional Netscape format cookies")
    user_agent: str | None = Field(default=None, description="Optional custom User-Agent string")


class FormatItem(BaseModel):
    format_id: str
    label: str
    resolution: str
    ext: str
    filesize_approx: int | None = None
    is_audio: bool = False


class MediaMetadataResponse(BaseModel):
    id: str
    title: str
    thumbnail: str | None = None
    duration: int = 0
    extractor: str
    webpage_url: str = ""
    formats: list[FormatItem] = []
