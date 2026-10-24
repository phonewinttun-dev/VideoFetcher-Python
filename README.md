# VideoFetcher (Python + FastAPI)

Universal media downloader backend powered by **FastAPI** and **yt-dlp**.

## Key Features
- **In-process extraction & download:** Direct programmatic integration with `yt-dlp` (no subprocess shell overhead).
- **Resource Efficient:** Automatically cleans up temporary files after delivery, preventing server storage overload.
- **Privacy & Security:** Cookies (Netscape format) are ephemeral, processed per-request, and deleted immediately.
- **iOS & Shortcut Friendly:** Supports direct downloading via `GET /api/download?url=...` with forced attachment headers (`Content-Disposition: attachment`).
- **Feature-driven Architecture:** Clear, modular separation between `extract`, `download`, and `settings`.

---

## Directory Structure
```text
VideoFetcher-Python/
├── app/
│   ├── core/                       # Shared configuration & yt-dlp client wrapper
│   │   ├── config.py               # App configuration & FFmpeg detection
│   │   └── yt_client.py            # Direct yt-dlp extraction & download logic
│   │
│   ├── features/                   # Feature-driven domain modules
│   │   ├── extract/                # URL validation & metadata extraction
│   │   │   ├── router.py           # POST /api/extract
│   │   │   └── schemas.py
│   │   │
│   │   ├── download/               # Media downloading & auto-cleanup streaming
│   │   │   ├── router.py           # POST /api/download, GET /api/download
│   │   │   └── schemas.py
│   │   │
│   │   └── settings/               # Cookie validation & runtime versions
│   │       ├── router.py           # /api/settings/version, /api/settings/cookies/validate
│   │       └── schemas.py
│   │
│   ├── static/                     # Static assets (HTML5 UI, CSS, PWA in Phase 2)
│   ├── templates/                  # Frontend templates
│   └── main.py                     # FastAPI entry point
│
├── tests/                          # Pytest test suite (19 test cases)
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive Swagger documentation is available at: `http://127.0.0.1:8000/docs`

### 3. Run Unit Tests
```bash
pytest tests -v
```
