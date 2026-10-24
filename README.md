<div align="center">

<img src="app/static/icons/logo.png" alt="VideoFetcher Logo" width="120" height="120" style="border-radius: 24px;" />

# VideoFetcher

**Universal media downloader for the web, powered by FastAPI, yt-dlp, and Tailwind CSS.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![yt-dlp](https://img.shields.io/badge/Powered_by-yt--dlp-red?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br />

<p align="center">
  <a href="#credits-and-attribution">Credits</a> &bull;
  <a href="#overview">Overview</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#getting-started">Getting Started</a> &bull;
  <a href="#configuration">Configuration</a> &bull;
  <a href="#api-reference">API Docs</a> &bull;
  <a href="#ios-shortcuts-integration">iOS Shortcuts</a>
</p>

</div>

---

## Credits and Attribution

Full credit goes to **[Isnotavailble](https://github.com/Isnotavailble)** and the original open-source project **[VideoFetcher (Android)](https://github.com/Isnotavailble/VideoFetcher)**.

This Python and web implementation is an inspired rewrite designed to expand the original application's privacy-focused, universal downloading capabilities to iOS (via Progressive Web App), Windows, macOS, Linux, and any modern web browser. The core philosophy of delivering a tracking-free, subscription-free, and user-empowered media tool originates directly from the foundational work done by Isnotavailble.

---

## Overview

VideoFetcher is an open-source media utility engineered to extract and download video and audio from popular media platforms directly to your device.

Unlike conventional web downloaders that track user submissions, retain downloaded media on servers, or inject ads, VideoFetcher enforces a strict zero-disk-leak and privacy-first model:

- **Client-Side Cookie Isolation:** User-provided Netscape cookies are stored exclusively in the browser's local storage and forwarded on a per-request basis. Ephemeral cookie files on the server are unlinked immediately after use.
- **Immediate Server Cleanup:** Downloads are streamed directly to the client as attachments. Background cleanup tasks immediately delete temporary media files from the server disk.
- **Resource Efficiency:** Designed to run reliably within low-memory environments (such as 512 MB RAM containers) without process crashes.

---

## Features

- **Multi-Platform Media Extraction:** Supports video and audio extraction from YouTube, TikTok, Instagram, Facebook, X (Twitter), and hundreds of other sites supported by yt-dlp.
- **In-Process Python Integration:** Direct programmatic integration with `yt-dlp` eliminates shell subprocess overhead, yielding faster response times and reliable error handling.
- **Progressive Web App (PWA):** Installs cleanly on iOS (via Safari Add to Home Screen) and desktop platforms with full-screen standalone display mode.
- **Emil Kowalski Design Engineering:**
  - Tactile button press feedback scaling to 0.97 on click.
  - Natural component entry transitions starting from scale 0.95 and opacity 0.
  - Staggered cascade animations for available format options.
  - Non-blocking, interruptible floating toast notifications.
  - Dark mode surface depth with subtle 1px border highlights.
- **Direct iOS Shortcuts Integration:** URL query parameters (`?url=...&type=video`) allow one-tap downloads directly from the iOS Share Sheet.
- **Format and Quality Selection:** Seamless toggle between Video (MP4) with granular resolution choices (1080p, 720p, 480p, 360p) and Audio-Only (MP3 / M4A).
- **Standalone CSS:** Precompiled, minified Tailwind CSS bundle requiring zero Node.js runtime processes in production.

---

## Architecture

VideoFetcher follows a feature-driven folder organization:

```text
VideoFetcher-Python/
|-- app/
|   |-- core/                       # Shared settings, config, and yt-dlp client
|   |   |-- config.py               # Environment configuration and FFmpeg detection
|   |   `-- yt_client.py            # In-process yt-dlp wrapper and cleanup logic
|   |
|   |-- features/                   # Domain features
|   |   |-- extract/                # Metadata extraction endpoints
|   |   |   |-- router.py           # POST /api/extract
|   |   |   `-- schemas.py
|   |   |
|   |   |-- download/               # Media download and streaming endpoints
|   |   |   |-- router.py           # POST /api/download, GET /api/download
|   |   |   `-- schemas.py
|   |   |
|   |   `-- settings/               # Cookie validation and engine diagnostics
|   |       |-- router.py           # /api/settings/version, /api/settings/cookies/validate
|   |       `-- schemas.py
|   |
|   |-- static/                     # Frontend static assets
|   |   |-- css/
|   |   |   |-- input.css           # Tailwind source with motion design tokens
|   |   |   `-- style.css           # Compiled standalone stylesheet (44 KB)
|   |   |-- js/
|   |   |   `-- app.js              # Vanilla ES6 client logic
|   |   |-- icons/
|   |   |   |-- logo.png            # Official VideoFetcher logo
|   |   |   `-- icon.svg            # Scalable vector icon
|   |   |-- manifest.json           # Web app manifest
|   |   `-- sw.js                   # Service Worker for offline shell caching
|   |
|   |-- templates/                  # FastAPI Jinja2 template
|   |   `-- index.html              # Single-page interface
|   |
|   `-- main.py                     # Application entry point
|
|-- tests/                          # Automated pytest suite (20 tests)
|-- .env.example                    # Environment configuration template
|-- package.json                    # Tailwind CLI build scripts
|-- requirements.txt                # Python dependencies
|-- LICENSE                         # MIT License
`-- README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- FFmpeg (recommended for media format merging and audio post-processing)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/VideoFetcher-Python.git
   cd VideoFetcher-Python
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. Access the web interface at `http://127.0.0.1:8000`.

---

## Configuration

Copy `.env.example` to create your local `.env` file:

```bash
cp .env.example .env
```

| Variable | Description | Default |
| --- | --- | --- |
| `DEBUG` | Enable debug mode | `false` |
| `TEMP_DIR` | Directory for temporary downloads and cookies | `./temp_downloads` |
| `FFMPEG_PATH` | Path to custom FFmpeg binary | Auto-detected from PATH |
| `MAX_FILE_SIZE_MB` | Maximum permitted download size | `500` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `*` |
| `DEFAULT_USER_AGENT` | Default User-Agent header string | Standard Chrome desktop UA |

---

## API Reference

FastAPI provides interactive documentation out of the box:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Primary Endpoints

| Method | Route | Description |
| --- | --- | --- |
| `GET` | `/` | Renders the web interface using Jinja2 templates |
| `POST` | `/api/extract` | Validates a URL and extracts media metadata and formats |
| `POST` | `/api/download` | Initiates media download and returns a streaming attachment |
| `GET` | `/api/download` | Query-parameter download route for external shortcut triggers |
| `GET` | `/api/settings/version` | Reports yt-dlp, Python, and FFmpeg detection status |
| `POST` | `/api/settings/cookies/validate` | Validates Netscape cookie syntax and extracts domain names |
| `GET` | `/api/health` | Service health status check |

---

## iOS Shortcuts Integration

VideoFetcher can be used directly from the iOS Share Sheet without manual copy-pasting:

1. Open the **Shortcuts** app on your iOS device.
2. Create a new Shortcut and enable **Show in Share Sheet**.
3. Set the accepted input type to **URLs**.
4. Add an **Open URL** action with the following address:
   ```text
   https://your-domain.com/?url=[Shortcut Input]&type=video
   ```
5. From Safari, YouTube, or TikTok, tap **Share**, select your shortcut, and the video will be fetched and sent directly to your device's Files folder.

---

## Running Automated Tests

Run the full pytest suite to verify backend and template functionality:

```bash
pytest tests -v
```

All 20 test cases should pass successfully.

---

## Responsible Use and Cookie Notice

- **Copyright Compliance:** Ensure you have the right or proper authorization to download any target media.
- **Account Safety:** When supplying account cookies to bypass bot detection or access private content, platforms like Meta or Facebook may detect automated traffic. Use cookies responsibly and delete them when they are no longer required.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <sub>VideoFetcher Web &bull; Full credit to <a href="https://github.com/Isnotavailble/VideoFetcher">Isnotavailble/VideoFetcher</a></sub>
</div>
