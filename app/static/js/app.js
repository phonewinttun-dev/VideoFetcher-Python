/**
 * VideoFetcher Client Application
 * Built with Vanilla Modern ES6 & Emil Kowalski Design Engineering Principles.
 */

(function () {
  "use strict";

  // State Management
  const state = {
    metadata: null,
    currentMode: "video", // "video" | "audio"
    selectedFormatId: "best",
    isLoading: false,
    isDownloading: false,
  };

  // DOM Elements
  const el = {
    html: document.documentElement,
    themeToggle: document.getElementById("theme-toggle"),
    themeIconSun: document.getElementById("theme-icon-sun"),
    themeIconMoon: document.getElementById("theme-icon-moon"),
    urlInput: document.getElementById("url-input"),
    pasteBtn: document.getElementById("paste-btn"),
    extractBtn: document.getElementById("extract-btn"),
    extractBtnText: document.getElementById("extract-btn-text"),
    extractBtnSpinner: document.getElementById("extract-btn-spinner"),
    extractForm: document.getElementById("extract-form"),
    previewSection: document.getElementById("preview-section"),
    previewThumbnail: document.getElementById("preview-thumbnail"),
    previewDuration: document.getElementById("preview-duration"),
    previewTitle: document.getElementById("preview-title"),
    previewExtractor: document.getElementById("preview-extractor"),
    previewLink: document.getElementById("preview-link"),
    modeVideoBtn: document.getElementById("mode-video-btn"),
    modeAudioBtn: document.getElementById("mode-audio-btn"),
    formatsGrid: document.getElementById("formats-grid"),
    downloadBtn: document.getElementById("download-btn"),
    downloadBtnText: document.getElementById("download-btn-text"),
    downloadIcon: document.getElementById("download-icon"),
    downloadSpinner: document.getElementById("download-spinner"),
    settingsModal: document.getElementById("settings-modal"),
    settingsOpenBtn: document.getElementById("settings-open-btn"),
    settingsCloseBtn: document.getElementById("settings-close-btn"),
    cookiesInput: document.getElementById("cookies-input"),
    cookiesFile: document.getElementById("cookies-file"),
    cookiesUploadBtn: document.getElementById("cookies-upload-btn"),
    cookiesValidateBtn: document.getElementById("cookies-validate-btn"),
    cookiesClearBtn: document.getElementById("cookies-clear-btn"),
    cookiesStatus: document.getElementById("cookies-status"),
    uaInput: document.getElementById("ua-input"),
    uaResetBtn: document.getElementById("ua-reset-btn"),
    uaSaveBtn: document.getElementById("ua-save-btn"),
    engineYtdlp: document.getElementById("engine-ytdlp"),
    enginePython: document.getElementById("engine-python"),
    engineFfmpeg: document.getElementById("engine-ffmpeg"),
    toastContainer: document.getElementById("toast-container"),
  };

  // -------------------------------------------------------------
  // 1. Toast Notification System (Sonner Principles)
  // -------------------------------------------------------------
  function showToast(message, type = "info", duration = 3500) {
    if (!el.toastContainer) return;

    const toast = document.createElement("div");
    toast.className =
      "toast-item pointer-events-auto flex items-center gap-2.5 px-4 py-3 rounded-xl border text-xs sm:text-sm font-medium shadow-lg backdrop-blur-md transition-all " +
      (type === "error"
        ? "bg-rose-50/95 dark:bg-rose-950/90 text-rose-900 dark:text-rose-200 border-rose-200 dark:border-rose-900/50"
        : type === "success"
        ? "bg-emerald-50/95 dark:bg-emerald-950/90 text-emerald-900 dark:text-emerald-200 border-emerald-200 dark:border-emerald-900/50"
        : "bg-white/95 dark:bg-slate-900/90 text-slate-800 dark:text-slate-200 border-slate-200 dark:border-slate-800");

    const icon = document.createElement("span");
    icon.className = "flex-shrink-0";
    if (type === "error") {
      icon.innerHTML = `<svg class="w-4 h-4 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    } else if (type === "success") {
      icon.innerHTML = `<svg class="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>`;
    } else {
      icon.innerHTML = `<svg class="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    }

    const text = document.createElement("span");
    text.className = "flex-1 leading-snug";
    text.textContent = message;

    const closeBtn = document.createElement("button");
    closeBtn.className = "btn-press text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-0.5";
    closeBtn.innerHTML = `<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`;

    toast.appendChild(icon);
    toast.appendChild(text);
    toast.appendChild(closeBtn);
    el.toastContainer.appendChild(toast);

    let dismissTimer;
    const startTimer = () => {
      dismissTimer = setTimeout(() => dismiss(), duration);
    };
    const pauseTimer = () => clearTimeout(dismissTimer);

    const dismiss = () => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px) scale(0.95)";
      setTimeout(() => toast.remove(), 220);
    };

    closeBtn.addEventListener("click", dismiss);
    toast.addEventListener("mouseenter", pauseTimer);
    toast.addEventListener("mouseleave", startTimer);

    startTimer();
  }

  // -------------------------------------------------------------
  // 2. Theme Management (Dark / Light)
  // -------------------------------------------------------------
  function initTheme() {
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = saved === "dark" || (!saved && prefersDark);

    applyTheme(isDark);

    el.themeToggle?.addEventListener("click", () => {
      const willBeDark = !el.html.classList.contains("dark");
      applyTheme(willBeDark);
      localStorage.setItem("theme", willBeDark ? "dark" : "light");
    });
  }

  function applyTheme(isDark) {
    if (isDark) {
      el.html.classList.add("dark");
      el.themeIconSun?.classList.remove("hidden");
      el.themeIconMoon?.classList.add("hidden");
    } else {
      el.html.classList.remove("dark");
      el.themeIconSun?.classList.add("hidden");
      el.themeIconMoon?.classList.remove("hidden");
    }
  }

  // -------------------------------------------------------------
  // 3. Duration & Size Formatters
  // -------------------------------------------------------------
  function formatDuration(seconds) {
    if (!seconds || seconds <= 0) return "Live / N/A";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) {
      const remMins = mins % 60;
      return `${hrs}:${remMins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }

  function formatBytes(bytes) {
    if (!bytes || bytes <= 0) return "Variable size";
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  }

  // -------------------------------------------------------------
  // 4. Clipboard Paste Handler
  // -------------------------------------------------------------
  async function handlePaste() {
    try {
      if (!navigator.clipboard?.readText) {
        showToast("Clipboard access not supported. Please paste manually.", "error");
        return;
      }
      const text = await navigator.clipboard.readText();
      if (text && text.trim()) {
        el.urlInput.value = text.trim();
        showToast("Link pasted from clipboard", "success", 2000);
        // Automatically trigger extraction on valid link paste
        triggerExtract();
      } else {
        showToast("Clipboard is empty", "info", 2000);
      }
    } catch (err) {
      showToast("Clipboard permission denied", "error", 2500);
    }
  }

  // -------------------------------------------------------------
  // 5. Metadata Extraction Flow
  // -------------------------------------------------------------
  async function triggerExtract() {
    const rawUrl = el.urlInput?.value?.trim();
    if (!rawUrl) {
      showToast("Please enter a valid media URL", "error");
      el.urlInput?.focus();
      return;
    }

    setExtractLoading(true);

    try {
      const cookies = localStorage.getItem("vf_cookies") || null;
      const userAgent = localStorage.getItem("vf_ua") || null;

      const resp = await fetch("/api/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: rawUrl,
          cookies: cookies,
          user_agent: userAgent,
        }),
      });

      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.detail || "Failed to extract media information.");
      }

      state.metadata = data;
      renderPreview(data);
      showToast("Media details extracted successfully", "success", 2500);
    } catch (err) {
      showToast(err.message || "Failed to fetch media details", "error", 4000);
      el.previewSection?.classList.add("hidden");
    } finally {
      setExtractLoading(false);
    }
  }

  function setExtractLoading(isLoading) {
    state.isLoading = isLoading;
    if (el.extractBtn) el.extractBtn.disabled = isLoading;
    if (el.extractBtnText) el.extractBtnText.textContent = isLoading ? "Fetching..." : "Fetch Info";
    if (el.extractBtnSpinner) el.extractBtnSpinner.classList.toggle("hidden", !isLoading);
  }

  // -------------------------------------------------------------
  // 6. Preview Rendering & Format List Cascade
  // -------------------------------------------------------------
  function renderPreview(data) {
    if (!el.previewSection) return;

    el.previewThumbnail.src = data.thumbnail || "";
    el.previewDuration.textContent = formatDuration(data.duration);
    el.previewTitle.textContent = data.title || "Untitled";
    el.previewExtractor.textContent = data.extractor || "Media";
    el.previewLink.href = data.webpage_url || el.urlInput.value;

    // Reset mode to video default
    setMode("video");

    el.previewSection.classList.remove("hidden");
    el.previewSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function setMode(mode) {
    state.currentMode = mode;
    const isVideo = mode === "video";

    if (isVideo) {
      el.modeVideoBtn.className =
        "btn-press flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all text-slate-900 dark:text-white bg-white dark:bg-slate-800 shadow-sm";
      el.modeAudioBtn.className =
        "btn-press flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white";
    } else {
      el.modeAudioBtn.className =
        "btn-press flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all text-slate-900 dark:text-white bg-white dark:bg-slate-800 shadow-sm";
      el.modeVideoBtn.className =
        "btn-press flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white";
    }

    renderFormatOptions();
  }

  function renderFormatOptions() {
    if (!el.formatsGrid || !state.metadata?.formats) return;

    el.formatsGrid.innerHTML = "";
    const isAudioMode = state.currentMode === "audio";

    const filtered = state.metadata.formats.filter((f) =>
      isAudioMode ? f.is_audio : !f.is_audio
    );

    if (filtered.length === 0) {
      el.formatsGrid.innerHTML = `<p class="col-span-2 text-center text-xs text-slate-400 py-4">No specific ${state.currentMode} streams found. Will download default best stream.</p>`;
      state.selectedFormatId = isAudioMode ? "bestaudio" : "best";
      return;
    }

    // Default selection
    state.selectedFormatId = filtered[0].format_id;

    filtered.forEach((fmt, index) => {
      const card = document.createElement("button");
      card.type = "button";
      // Staggered cascade entrance (Emil Kowalski principle)
      card.className =
        "cascade-item btn-press p-3 rounded-xl border text-left flex items-center justify-between transition-all " +
        (fmt.format_id === state.selectedFormatId
          ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/40 text-slate-900 dark:text-white shadow-sm ring-1 ring-indigo-500"
          : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900/60 text-slate-700 dark:text-slate-300");

      card.style.animationDelay = `${index * 40}ms`;

      card.innerHTML = `
        <div class="space-y-0.5">
          <div class="text-xs sm:text-sm font-semibold">${fmt.label}</div>
          <div class="text-[11px] text-slate-400">${fmt.resolution} &bull; .${fmt.ext.toUpperCase()}</div>
        </div>
        <div class="text-right">
          <span class="text-xs font-mono font-medium text-slate-500 dark:text-slate-400">${formatBytes(fmt.filesize_approx)}</span>
        </div>
      `;

      card.addEventListener("click", () => {
        state.selectedFormatId = fmt.format_id;
        renderFormatOptions();
      });

      el.formatsGrid.appendChild(card);
    });
  }

  // -------------------------------------------------------------
  // 7. Download Flow
  // -------------------------------------------------------------
  async function triggerDownload() {
    const rawUrl = state.metadata?.webpage_url || el.urlInput?.value?.trim();
    if (!rawUrl) {
      showToast("No active media URL to download", "error");
      return;
    }

    setDownloadLoading(true);
    showToast("Preparing media download...", "info", 3000);

    try {
      const cookies = localStorage.getItem("vf_cookies") || null;
      const userAgent = localStorage.getItem("vf_ua") || null;

      const resp = await fetch("/api/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: rawUrl,
          format_id: state.selectedFormatId,
          is_audio: state.currentMode === "audio",
          cookies: cookies,
          user_agent: userAgent,
        }),
      });

      if (!resp.ok) {
        const errorJson = await resp.json().catch(() => ({}));
        throw new Error(errorJson.detail || "Download failed on server.");
      }

      // Extract filename from Content-Disposition header
      const disposition = resp.headers.get("Content-Disposition");
      let filename = "media_download";
      if (disposition) {
        const matchUtf8 = disposition.match(/filename\*=UTF-8''([^;]+)/i);
        const matchStandard = disposition.match(/filename="?([^";]+)"?/i);
        if (matchUtf8) {
          filename = decodeURIComponent(matchUtf8[1]);
        } else if (matchStandard) {
          filename = matchStandard[1];
        }
      }

      const blob = await resp.blob();
      const objectUrl = window.URL.createObjectURL(blob);

      // Trigger standard browser download / iOS Files app dialog
      const tempLink = document.createElement("a");
      tempLink.href = objectUrl;
      tempLink.download = filename;
      document.body.appendChild(tempLink);
      tempLink.click();
      document.body.removeChild(tempLink);

      // Clean up object URL
      setTimeout(() => window.URL.revokeObjectURL(objectUrl), 1000);

      showToast(`Downloaded: ${filename}`, "success", 4000);
    } catch (err) {
      showToast(err.message || "Download failed", "error", 4000);
    } finally {
      setDownloadLoading(false);
    }
  }

  function setDownloadLoading(isDownloading) {
    state.isDownloading = isDownloading;
    if (el.downloadBtn) el.downloadBtn.disabled = isDownloading;
    if (el.downloadBtnText) el.downloadBtnText.textContent = isDownloading ? "Processing..." : "Download Now";
    if (el.downloadIcon) el.downloadIcon.classList.toggle("hidden", isDownloading);
    if (el.downloadSpinner) el.downloadSpinner.classList.toggle("hidden", !isDownloading);
  }

  // -------------------------------------------------------------
  // 8. Settings & Cookies Management
  // -------------------------------------------------------------
  function initSettings() {
    // Open/Close modal
    el.settingsOpenBtn?.addEventListener("click", () => {
      loadSettingsUI();
      el.settingsModal?.classList.remove("hidden");
    });

    el.settingsCloseBtn?.addEventListener("click", () => {
      el.settingsModal?.classList.add("hidden");
    });

    el.settingsModal?.addEventListener("click", (e) => {
      if (e.target === el.settingsModal) {
        el.settingsModal.classList.add("hidden");
      }
    });

    // File upload handler for cookies.txt
    el.cookiesUploadBtn?.addEventListener("click", () => el.cookiesFile?.click());
    el.cookiesFile?.addEventListener("change", (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (event) => {
        el.cookiesInput.value = event.target?.result || "";
        validateAndSaveCookies();
      };
      reader.readAsText(file);
    });

    // Cookie validate & clear
    el.cookiesValidateBtn?.addEventListener("click", validateAndSaveCookies);
    el.cookiesClearBtn?.addEventListener("click", () => {
      localStorage.removeItem("vf_cookies");
      el.cookiesInput.value = "";
      el.cookiesStatus.classList.add("hidden");
      showToast("Cookies cleared from browser", "info", 2000);
    });

    // User-Agent Save & Reset
    el.uaSaveBtn?.addEventListener("click", () => {
      const val = el.uaInput?.value?.trim();
      if (val) {
        localStorage.setItem("vf_ua", val);
        showToast("Custom User-Agent saved", "success", 2000);
      } else {
        localStorage.removeItem("vf_ua");
        showToast("User-Agent reset to default", "info", 2000);
      }
    });

    el.uaResetBtn?.addEventListener("click", () => {
      localStorage.removeItem("vf_ua");
      if (el.uaInput) el.uaInput.value = "";
      showToast("User-Agent reset to default", "info", 2000);
    });
  }

  function loadSettingsUI() {
    const savedCookies = localStorage.getItem("vf_cookies") || "";
    if (el.cookiesInput) el.cookiesInput.value = savedCookies;
    if (savedCookies) {
      el.cookiesStatus.textContent = "Cookies currently saved in this browser.";
      el.cookiesStatus.classList.remove("hidden");
    }

    const savedUA = localStorage.getItem("vf_ua") || "";
    if (el.uaInput) el.uaInput.value = savedUA;

    fetchEngineVersion();
  }

  async function validateAndSaveCookies() {
    const raw = el.cookiesInput?.value?.trim();
    if (!raw) {
      showToast("Please paste or upload cookies first", "error");
      return;
    }

    try {
      const resp = await fetch("/api/settings/cookies/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cookies: raw }),
      });
      const data = await resp.json();

      if (data.valid) {
        localStorage.setItem("vf_cookies", raw);
        el.cookiesStatus.textContent = data.message;
        el.cookiesStatus.classList.remove("hidden");
        showToast(`Saved ${data.entries_count} cookies for ${data.domains.join(", ")}`, "success", 3000);
      } else {
        showToast(data.message || "Invalid Netscape cookie format", "error", 3500);
      }
    } catch (err) {
      showToast("Failed to validate cookies with server", "error");
    }
  }

  async function fetchEngineVersion() {
    try {
      const resp = await fetch("/api/settings/version");
      if (!resp.ok) return;
      const data = await resp.json();
      if (el.engineYtdlp) el.engineYtdlp.textContent = `v${data.ytdlp_version}`;
      if (el.enginePython) el.enginePython.textContent = `Python ${data.python_version}`;
      if (el.engineFfmpeg) {
        el.engineFfmpeg.textContent = data.ffmpeg_available ? "Enabled (Available)" : "Fallback Mode (Not in PATH)";
        el.engineFfmpeg.className = data.ffmpeg_available
          ? "font-medium text-emerald-600 dark:text-emerald-400"
          : "font-medium text-amber-600 dark:text-amber-400";
      }
    } catch {
      // Ignore background stats failure
    }
  }

  // -------------------------------------------------------------
  // 9. Quick Share & iOS Shortcuts URL Parameters Handler (US 2.3)
  // -------------------------------------------------------------
  function handleUrlParameters() {
    const params = new URLSearchParams(window.location.search);
    const targetUrl = params.get("url");
    const targetType = params.get("type"); // "video" | "audio"

    if (targetUrl) {
      el.urlInput.value = targetUrl;
      if (targetType === "audio") {
        state.currentMode = "audio";
      }
      // Instant extraction on link share
      triggerExtract();
    }
  }

  // -------------------------------------------------------------
  // 10. Service Worker Registration (PWA)
  // -------------------------------------------------------------
  function registerServiceWorker() {
    if ("serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker.register("/static/sw.js").catch(() => {
          // SW registration failed silently
        });
      });
    }
  }

  // -------------------------------------------------------------
  // Initialization
  // -------------------------------------------------------------
  function init() {
    initTheme();
    initSettings();
    registerServiceWorker();

    // Event Listeners
    el.pasteBtn?.addEventListener("click", handlePaste);
    el.extractForm?.addEventListener("submit", triggerExtract);
    el.modeVideoBtn?.addEventListener("click", () => setMode("video"));
    el.modeAudioBtn?.addEventListener("click", () => setMode("audio"));
    el.downloadBtn?.addEventListener("click", triggerDownload);

    // Check for query parameters (?url=...)
    handleUrlParameters();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
