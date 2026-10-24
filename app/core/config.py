import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "VideoFetcher"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", str(BASE_DIR / "temp_downloads")))
    TEMPLATES_DIR: Path = BASE_DIR / "app" / "templates"
    STATIC_DIR: Path = BASE_DIR / "app" / "static"

    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    DEFAULT_USER_AGENT: str = os.getenv(
        "DEFAULT_USER_AGENT",
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    )

    ALLOWED_ORIGINS: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
            if origin.strip()
        ]
    )

    @property
    def ffmpeg_location(self) -> str | None:
        """Find FFmpeg binary from FFMPEG_PATH environment variable, project bin, system PATH, or common locations."""
        custom_path = os.getenv("FFMPEG_PATH")
        if custom_path and os.path.exists(custom_path):
            return custom_path

        # 1. Check project-local bin directory
        local_bin_exe = self.BASE_DIR / "bin" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if local_bin_exe.exists():
            return str(local_bin_exe)

        # 2. Check system PATH
        path_binary = shutil.which("ffmpeg")
        if path_binary:
            return path_binary

        # 3. Common Windows fallback paths
        if os.name == "nt":
            common_paths = [
                r"C:\Program Files (x86)\FormatFactory\FFModules\Encoder\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                r"C:\ffmpeg\bin\ffmpeg.exe",
            ]
            for p in common_paths:
                if os.path.exists(p):
                    return p

        return None


settings = Settings()
# Ensure directories exist
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
