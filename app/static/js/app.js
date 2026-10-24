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
    urlInput: document.getElementById("url-input"),
    pasteBtn: document.getElementById("paste-btn"),
    extractBtn: document.getElementById("extract-btn"),
    extractBtnIcon: document.getElementById("extract-btn-icon"),
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
  // 1. Toast Notification System (Apple HUD / Dynamic Island Style)
  // -------------------------------------------------------------
  function showToast(message, type = "info", duration = 3500) {
    if (!el.toastContainer) return;

    const toast = document.createElement("div");
    toast.className =
      "apple-toast pointer-events-auto flex items-center gap-2.5 px-4 py-2.5 rounded-full text-xs sm:text-[13px] font-medium transition-all " +
      (type === "error"
        ? "border-rose-500/30 text-rose-200"
        : type === "success"
        ? "border-emerald-500/30 text-emerald-200"
        : "border-white/15 text-neutral-200");

    const icon = document.createElement("span");
    icon.className = "flex-shrink-0";
    if (type === "error") {
      icon.innerHTML = `<svg class="w-4 h-4 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    } else if (type === "success") {
      icon.innerHTML = `<svg class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>`;
    } else {
      icon.innerHTML = `<svg class="w-4 h-4 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    }

    const text = document.createElement("span");
    text.className = "flex-1 leading-snug";
    text.textContent = message;

    toast.appendChild(icon);
    toast.appendChild(text);

    if (message.includes("Settings") || message.includes("cookies")) {
      duration = Math.max(duration, 6000);
      const settingsAction = document.createElement("button");
      settingsAction.className =
        "btn-press ml-1 px-2.5 py-1 text-[11px] font-semibold bg-white/10 hover:bg-white/20 active:bg-white/30 text-white rounded-lg cursor-pointer whitespace-nowrap transition-all border border-white/15";
      settingsAction.textContent = "Open Settings";
      settingsAction.addEventListener("click", () => {
        loadSettingsUI();
        el.settingsModal?.classList.remove("hidden");
        dismiss();
      });
      toast.appendChild(settingsAction);
    }

    const closeBtn = document.createElement("button");
    closeBtn.className = "btn-press text-neutral-400 hover:text-white p-0.5";
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
      toast.style.transform = "translateY(8px) scale(0.96)";
      setTimeout(() => toast.remove(), 220);
    };

    closeBtn.addEventListener("click", dismiss);
    toast.addEventListener("mouseenter", pauseTimer);
    toast.addEventListener("mouseleave", startTimer);

    startTimer();
  }

  // -------------------------------------------------------------
  // 2. Theme Enforcement (Pure Dark Mode)
  // -------------------------------------------------------------
  function initTheme() {
    el.html.classList.add("dark");
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
    if (el.extractBtnText) el.extractBtnText.textContent = isLoading ? "Loading..." : "Download";
    if (el.extractBtnIcon) el.extractBtnIcon.classList.toggle("hidden", isLoading);
    if (el.extractBtnSpinner) el.extractBtnSpinner.classList.toggle("hidden", !isLoading);
  }

  // -------------------------------------------------------------
  // Official Platform Brand Vector Icons & Metadata
  // -------------------------------------------------------------
  const PLATFORMS = {
    youtube: {
      name: "YouTube",
      color: "text-red-500",
      svg: `<svg class="w-3.5 h-3.5 text-red-500 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>`,
    },
    facebook: {
      name: "Facebook",
      color: "text-[#1877F2]",
      svg: `<svg class="w-3.5 h-3.5 text-[#1877F2] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>`,
    },
    instagram: {
      name: "Instagram",
      color: "text-[#E4405F]",
      svg: `<svg class="w-3.5 h-3.5 text-[#E4405F] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`,
    },
    tiktok: {
      name: "TikTok",
      color: "text-[#25F4EE]",
      svg: `<svg class="w-3.5 h-3.5 text-[#25F4EE] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.27 1.76-.23.99-.04 2.09.6 2.85.73.91 1.96 1.34 3.1 1.11.97-.16 1.81-.79 2.22-1.67.26-.54.34-1.15.34-1.75.02-4.34.01-8.69.01-13.03z"/></svg>`,
    },
    twitter: {
      name: "X",
      color: "text-white",
      svg: `<svg class="w-3 h-3 text-neutral-200 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`,
    },
    x: {
      name: "X",
      color: "text-white",
      svg: `<svg class="w-3 h-3 text-neutral-200 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`,
    },
  };

  function getPlatformInfo(extractor) {
    if (!extractor) return null;
    const lower = extractor.toLowerCase();
    for (const key of Object.keys(PLATFORMS)) {
      if (lower.includes(key)) {
        return PLATFORMS[key];
      }
    }
    return null;
  }

  // -------------------------------------------------------------
  // 6. Preview Rendering & Format List Cascade
  // -------------------------------------------------------------
  function renderPreview(data) {
    if (!el.previewSection) return;

    el.previewThumbnail.src = data.thumbnail || "";
    el.previewDuration.textContent = formatDuration(data.duration);
    el.previewTitle.textContent = data.title || "Untitled";

    // Set platform logo and name
    const platform = getPlatformInfo(data.extractor);
    if (platform) {
      el.previewExtractor.innerHTML = `${platform.svg}<span>${platform.name}</span>`;
    } else {
      el.previewExtractor.innerHTML = `<svg class="w-3.5 h-3.5 text-neutral-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg><span>${data.extractor || "Media"}</span>`;
    }

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
        "btn-press flex-1 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all text-white bg-neutral-800 shadow-2xs";
      el.modeAudioBtn.className =
        "btn-press flex-1 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all text-neutral-400 hover:text-white";
    } else {
      el.modeAudioBtn.className =
        "btn-press flex-1 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all text-white bg-neutral-800 shadow-2xs";
      el.modeVideoBtn.className =
        "btn-press flex-1 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all text-neutral-400 hover:text-white";
    }

    renderFormatOptions();
  }

  function updateFormatSelection(newFormatId) {
    state.selectedFormatId = newFormatId;
    if (!el.formatsGrid) return;

    const cards = el.formatsGrid.querySelectorAll("button[data-format-id]");
    cards.forEach((card) => {
      const isSelected = card.getAttribute("data-format-id") === newFormatId;
      card.setAttribute("aria-checked", isSelected ? "true" : "false");

      // Apple subtle selection: calm highlight, no harsh white ring, no shifting
      if (isSelected) {
        card.className =
          "btn-press p-3 rounded-xl border text-left flex items-center justify-between transition-colors duration-150 border-white/30 bg-white/[0.08] text-white shadow-2xs";
      } else {
        card.className =
          "btn-press p-3 rounded-xl border text-left flex items-center justify-between transition-colors duration-150 border-white/[0.08] hover:border-white/[0.16] bg-white/[0.02] text-neutral-300";
      }

      const radio = card.querySelector(".radio-dot");
      if (radio) {
        if (isSelected) {
          radio.className =
            "radio-dot w-4 h-4 rounded-full border border-white bg-white flex items-center justify-center flex-shrink-0 transition-colors duration-150";
          radio.innerHTML = '<div class="w-1.5 h-1.5 rounded-full bg-neutral-900"></div>';
        } else {
          radio.className =
            "radio-dot w-4 h-4 rounded-full border border-neutral-600 flex items-center justify-center flex-shrink-0 transition-colors duration-150";
          radio.innerHTML = "";
        }
      }
    });
  }

  function renderFormatOptions() {
    if (!el.formatsGrid || !state.metadata?.formats) return;

    el.formatsGrid.innerHTML = "";
    const isAudioMode = state.currentMode === "audio";

    const filtered = state.metadata.formats.filter((f) =>
      isAudioMode ? f.is_audio : !f.is_audio
    );

    if (filtered.length === 0) {
      el.formatsGrid.innerHTML = `<p class="col-span-2 text-center text-xs text-neutral-400 py-4">No specific ${state.currentMode} streams found. Will download default stream.</p>`;
      state.selectedFormatId = isAudioMode ? "bestaudio" : "best";
      return;
    }

    // Default selection if current selection is not in filtered list
    if (!filtered.some((f) => f.format_id === state.selectedFormatId)) {
      state.selectedFormatId = filtered[0].format_id;
    }

    filtered.forEach((fmt, index) => {
      const isSelected = fmt.format_id === state.selectedFormatId;
      const card = document.createElement("button");
      card.type = "button";
      card.setAttribute("data-format-id", fmt.format_id);
      card.setAttribute("role", "radio");
      card.setAttribute("aria-checked", isSelected ? "true" : "false");

      // Initial staggered entrance animation
      card.className =
        "cascade-item btn-press p-3 rounded-xl border text-left flex items-center justify-between transition-colors duration-150 " +
        (isSelected
          ? "border-white/30 bg-white/[0.08] text-white shadow-2xs"
          : "border-white/[0.08] hover:border-white/[0.16] bg-white/[0.02] text-neutral-300");

      card.style.animationDelay = `${index * 35}ms`;

      card.innerHTML = `
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="radio-dot w-4 h-4 rounded-full border flex items-center justify-center flex-shrink-0 transition-colors duration-150 ${
            isSelected
              ? "border-white bg-white"
              : "border-neutral-600"
          }">
            ${isSelected ? '<div class="w-1.5 h-1.5 rounded-full bg-neutral-900"></div>' : ''}
          </div>
          <div class="space-y-0.5 truncate">
            <div class="text-xs sm:text-[13px] font-semibold text-white">${fmt.label}</div>
            <div class="text-[11px] text-neutral-400 font-tabular">${fmt.resolution} &bull; .${fmt.ext.toUpperCase()}</div>
          </div>
        </div>
        <div class="text-right flex-shrink-0 pl-2">
          <span class="text-xs font-mono font-medium text-neutral-300 font-tabular">${formatBytes(fmt.filesize_approx)}</span>
        </div>
      `;

      card.addEventListener("click", () => {
        updateFormatSelection(fmt.format_id);
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
