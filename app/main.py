from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.features.download.router import router as download_router
from app.features.extract.router import router as extract_router
from app.features.settings.router import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: sweep orphaned temp files from previous container sessions
    if settings.TEMP_DIR.exists():
        for f in settings.TEMP_DIR.glob("*"):
            if f.is_file() and not f.name.startswith("."):
                try:
                    f.unlink()
                except OSError:
                    pass
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Universal media downloader backend powered by FastAPI & yt-dlp",
    lifespan=lifespan,
)

# Enable CORS (allow_credentials=False ensures W3C compliance with wildcard origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (CSS, JS, PWA icons, manifest.json)
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Standard FastAPI Jinja2 Templates
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# Register Feature Routers
app.include_router(extract_router)
app.include_router(download_router)
app.include_router(settings_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Serve the primary HTML5 client interface using standard FastAPI templating."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
        },
    )
