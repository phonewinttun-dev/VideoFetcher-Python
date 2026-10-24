<div align="center">

# VideoFetcher

**A modern, lightweight, privacy-focused media downloader powered by FastAPI, yt-dlp, and Tailwind CSS.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![yt-dlp](https://img.shields.io/badge/Powered_by-yt--dlp-red?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br />

<p align="center">
  <a href="#-inspiration--attribution">Inspiration</a> &bull;
  <a href="#-key-features">Key Features</a> &bull;
  <a href="#-architecture">Architecture</a> &bull;
  <a href="#-quick-start">Quick Start</a> &bull;
  <a href="#-api-reference">API Docs</a> &bull;
  <a href="#-ios-shortcuts-integration">iOS Shortcuts</a> &bull;
  <a href="#-configuration">Configuration</a>
</p>

</div>

---

> [!NOTE]
> ### 💡 Inspiration & Attribution
> This project is an inspired **web and Progressive Web App (PWA) version** of the open-source Android app [**VideoFetcher**](https://github.com/Isnotavailble/VideoFetcher) created by [**Isnotavailble**](https://github.com/Isnotavailble). 
> 
> While the original application delivers an exceptional native experience on Android, this Python/FastAPI rewrite brings the same universal media extraction capabilities and privacy-first ethos to **iOS (via full-screen PWA), macOS, Windows, Linux, and any modern web browser**.

---

## 🛡️ Privacy-First & Zero-Disk-Leak Philosophy

Traditional web downloaders often store user files indefinitely, track URLs, or retain authentication credentials. **VideoFetcher Web** is architected with strict privacy and resource-safety guarantees:

* **Ephemeral Cookies:** Netscape `cookies.txt` entries are saved solely in your browser's local storage (`localStorage`). They are forwarded per-request, written to isolated temporary memory on the server, and immediately deleted once extraction or download finishes.
* **Automatic Server Cleanup:** Downloaded media streams are piped directly to your device via `Content-Disposition: attachment`. FastAPI's `BackgroundTasks` automatically purges temporary disk files immediately after transmission.
* **Resource-Constrained Optimization:** Specifically tuned to run smoothly within free-tier cloud containers (512 MB RAM limits) without memory exhaustion.

---

## ✨ Key Features

* **Universal Website Extraction:** Seamlessly download video and audio from YouTube, TikTok, Instagram, Facebook, X (Twitter), and hundreds of other platforms backed directly by [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).
* **In-Process Python Integration:** Zero shell subprocess overhead. Interacts natively with `yt-dlp`'s Python APIs for faster extraction and lower latency.
* **Progressive Web App (PWA):** Installable directly to your iPhone or iPad Home Screen via Safari, hiding the browser URL bar for a native application feel.
* **Emil Kowalski Design Engineering:**
  * **Tactile Press Feedback:** Interactive buttons scale to `0.97` on press (`160ms cubic-bezier(0.23, 1, 0.32, 1)`).
  * **Natural Scale Entrances:** Metadata cards reveal smoothly from `scale(0.95)` with zero abrupt pops.
  * **Staggered Cascade:** Format options cascade into view sequentially with `40ms` stagger intervals.
  * **Sonner-Style Toasts:** Non-intrusive, interruptible floating notifications.
  * **Surface Depth:** Rich dark slate palette (`#090d16`) with subtle `1px` inner top highlights.
* **iOS Shortcuts & Quick Share Integration:** Direct URL parameter execution (`?url=...&type=video`) allows one-tap downloads from the iOS Share Sheet without manual copy-pasting.
* **Smart Format Separation:** One-click toggling between **Video (.mp4)** with custom resolution tiers (1080p, 720p, 480p, 360p) and **Audio Only (.mp3 / .m4a)**.
* **Standalone Tailwind CSS:** Fully compiled, minified static stylesheet (`style.css`) with zero runtime Node.js dependency.
* **Light & Dark Mode:** Native system preference detection with seamless manual toggle persisted in local storage.

---

## 🏛️ Architecture & Folder Structure

VideoFetcher uses a **feature-driven architecture** keeping related routes, schemas, and logic colocated:

```text
VideoFetcher-Python/
├── app/
│   ├── core/                       # Shared configuration, settings & yt-dlp wrapper
│   │   ├── config.py               # Environment configuration & FFmpeg detection
│   │   └── yt_client.py            # In-process yt-dlp extraction & download logic
│   │
│   ├── features/                   # Domain features
│   │   ├── extract/                # Metadata extraction & format discovery
│   │   │   ├── router.py           # POST /api/extract
│   │   │   └── schemas.py
│   │   │
│   │   ├── download/               # Media download, streaming & auto-cleanup
│   │   │   ├── router.py           # POST /api/download, GET /api/download
│   │   │   └── schemas.py
│   │   │
│   │   └── settings/               # Cookie validation & runtime engine inspection
│   │       ├── router.py           # /api/settings/version, /api/settings/cookies/validate
│   │       └── schemas.py
│   │
│   ├── static/                     # Standalone frontend assets (no runtime Node.js)
│   │   ├── css/
│   │   │   ├── input.css           # Tailwind source & Emil Kowalski design tokens
│   │   │   └── style.css           # Compiled, minified production CSS (44 KB)
│   │   ├── js/
│   │   │   └── app.js              # Vanilla ES6 application logic & toast system
│   │   ├── icons/
│   │   │   └── icon.svg            # Scalable PWA vector glyph
│   │   ├── manifest.json           # PWA web manifest
│   │   └── sw.js                   # Service Worker (offline app shell cache)
│   │
│   ├── templates/                  # Standard FastAPI Jinja2 template
│   │   └── index.html              # Responsive single-page client interface
│   │
│   └── main.py                     # FastAPI application entrypoint
│
├── tests/                          # Comprehensive pytest test suite (20 tests)
├── .env.example                    # Configuration template (no hardcoded secrets)
├── package.json                    # Tailwind CLI build scripts
├── requirements.txt                # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
* **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13, 3.14)
* **FFmpeg** (Optional but strongly recommended for audio extraction and merging separate high-res video/audio streams).

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/<your-username>/VideoFetcher-Python.git
cd VideoFetcher-Python

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Development Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)** to view the application.

---

## ⚙️ Configuration

Copy `.env.example` to `.env` to customize your environment:

```bash
cp .env.example .env
```

| Variable | Description | Default |
| --- | --- | --- |
| `DEBUG` | Enable debug logging | `false` |
| `TEMP_DIR` | Directory for ephemeral download and cookie files | `./temp_downloads` |
| `FFMPEG_PATH` | Path to custom `ffmpeg` binary (auto-detected from `PATH` if empty) | Auto-detected |
| `MAX_FILE_SIZE_MB` | Maximum allowed download size limit | `500` |
| `ALLOWED_ORIGINS` | Allowed CORS origins (comma-separated) | `*` |
| `DEFAULT_USER_AGENT` | Default User-Agent string used for extraction | Chrome 124 desktop UA |

---

## 📡 REST API Reference

Interactive API documentation is automatically generated by FastAPI:
* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Summary of Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Serves the HTML5 web client via standard FastAPI templating |
| `POST` | `/api/extract` | Extracts video metadata, thumbnail, duration, and available format options |
| `POST` | `/api/download` | Downloads media and streams the file as an attachment |
| `GET` | `/api/download` | Direct query-parameter download (ideal for iOS Shortcuts) |
| `GET` | `/api/settings/version` | Reports runtime versions (`yt-dlp`, Python, FFmpeg status) |
| `POST` | `/api/settings/cookies/validate` | Validates Netscape-formatted cookie syntax and domain count |
| `GET` | `/api/health` | Health check endpoint |

---

## 📱 iOS Shortcuts Integration

VideoFetcher is engineered to work directly with Apple Shortcuts on iOS:

1. Create a new Shortcut on your iPhone named **"Download Video"**.
2. Configure the Shortcut to accept URLs from the **Share Sheet**.
3. Add an action: **Open URL**:
   ```text
   https://your-videofetcher-domain.com/?url=[Shortcut Input]&type=video
   ```
4. Now, whenever you browse YouTube, TikTok, or Instagram, tap **Share** &rarr; **Download Video**. VideoFetcher will open, automatically fetch the video, and save it directly into your device's **Files** app!

---

## 🧪 Running Automated Tests

VideoFetcher includes a full suite of unit tests covering URL validation, filename sanitization, ephemeral cookie handling, mocked `yt-dlp` extractions, download streaming headers, and template rendering:

```bash
pytest tests -v
```

```text
======================== 20 passed in 0.72s ========================
```

---

## 🎨 Frontend Styling (Tailwind CLI)

The production stylesheet (`app/static/css/style.css`) is pre-built and committed. If you modify `app/static/css/input.css` or the templates, rebuild the CSS using:

```bash
npm run build:css
```

---

## ⚠️ Responsible Use & Cookie Notice

* **Respect Copyright:** Only download content that you own, have permission to download, or is licensed under Creative Commons.
* **Social Media Cookies:** When uploading Netscape cookies to access private or age-restricted content, `yt-dlp` authenticates with your session. Social platforms (specifically Meta/Facebook) monitor high-frequency automated requests. Exercise caution and avoid aggressive downloading on personal accounts.

---

## 📄 License

This project is open-source and released under the [MIT License](LICENSE).

---

<div align="center">
  <sub>Crafted with care &bull; Inspired by <a href="https://github.com/Isnotavailble/VideoFetcher">VideoFetcher (Android)</a></sub>
</div>
