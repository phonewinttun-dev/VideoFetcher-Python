from pydantic import BaseModel, Field


class DownloadRequest(BaseModel):
    url: str = Field(..., description="Target video or media URL")
    format_id: str | None = Field(default=None, description="Requested format ID (e.g. 'best', '137', or 'bestaudio')")
    is_audio: bool = Field(default=False, description="Whether to extract audio only")
    cookies: str | None = Field(default=None, description="Optional Netscape format cookies")
    user_agent: str | None = Field(default=None, description="Optional custom User-Agent string")
