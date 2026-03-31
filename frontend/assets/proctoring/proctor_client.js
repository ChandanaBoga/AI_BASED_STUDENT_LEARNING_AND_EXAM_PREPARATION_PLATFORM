/**
 * proctor_client.js
 * =================
 * Quiz Proctoring Client using Moondream LLM backend.
 *
 * Features
 *  - Accesses webcam via getUserMedia
 *  - Captures a frame every CAPTURE_INTERVAL_MS milliseconds
 *  - POSTs the frame (base64 JPEG) to the local Moondream backend
 *  - On distraction: increments warning counter, shows popup with chances left
 *  - After MAX_WARNINGS strikes, resets the active quiz from the beginning
 *  - Shows a small Picture-in-Picture webcam preview in the corner
 *
 * Usage (added automatically to combined_app.html):
 *   Proctor.start()  – call when quiz section becomes active
 *   Proctor.stop()   – call when user leaves quiz section
 *   Proctor.reset()  – full reset (warnings back to 0)
 */

(function (global) {
    "use strict";

    // ── Configuration ─────────────────────────────────────────────────────
    const getBaseUrl = () => {
        if (typeof AI_BASE_URL !== "undefined") return AI_BASE_URL;
        return window.location.protocol === 'file:' ? 'http://localhost:8001' : '';
    };

    const CONFIG = {
        backendUrl        : getBaseUrl() + "/analyze",
        captureIntervalMs : 5000,       // check every 5 s
        maxWarnings       : 5,
        jpegQuality       : 0.7,        // slightly higher quality
        captureWidth      : 640,
        captureHeight     : 480,
    };

    // ── Internal state ─────────────────────────────────────────────────────
    let warningCount   = 0;
    let intervalId     = null;
    let stream         = null;
    let videoEl        = null;
    let canvasEl       = null;
    let isAnalyzing    = false;
    let isRunning      = false;
    let overlayVisible = false;
    let backendHealthy = true; // Assume true until check fails

    // ── Inject CSS once ────────────────────────────────────────────────────
    function injectCSS() {
        if (document.getElementById("proctor-css")) return;
        const link = document.createElement("link");
        link.id   = "proctor-css";
        link.rel  = "stylesheet";
        link.href = getBaseUrl() + "/assets/proctoring/proctor_ui.css";
        document.head.appendChild(link);
    }

    // ── Build DOM elements ─────────────────────────────────────────────────
    function buildUI() {
        if (document.getElementById("proctor-overlay")) return;

        // Warning overlay (hidden by default)
        const overlay = document.createElement("div");
        overlay.id    = "proctor-overlay";
        overlay.setAttribute("style", "display: none !important");
        overlay.innerHTML = `
            <div id="proctor-card">
                <div id="proctor-icon-wrap">
                    <span class="material-symbols-outlined">warning</span>
                </div>
                <div id="proctor-title">⚠️ Activity Detected!</div>
                <div id="proctor-message">
                    Our system detected you may not be focused on the quiz.<br>
                    Please keep your attention on the screen.
                </div>
                <div id="proctor-chances"></div>
                <button id="proctor-ok-btn">OK</button>
            </div>`;
        document.body.appendChild(overlay);

        // PiP webcam preview
        const pip = document.createElement("div");
        pip.id = "proctor-pip";
        pip.innerHTML = `<video id="proctor-video" autoplay muted playsinline></video>
                         <div id="proctor-pip-label">🔴 Proctored</div>`;
        document.body.appendChild(pip);
    }

    // ── Update the chance-dots strip ───────────────────────────────────────
    function renderChances() {
        const container = document.getElementById("proctor-chances");
        if (!container) return;
        container.innerHTML = "";
        for (let i = 0; i < CONFIG.maxWarnings; i++) {
            const dot = document.createElement("div");
            dot.className = "proctor-dot " + (i < warningCount ? "used" : "ok");
            container.appendChild(dot);
        }
    }

    // ── Show warning popup ─────────────────────────────────────────────────
    function showWarning(isFinal, type = "distraction") {
        if (overlayVisible) return;
        overlayVisible = true;

        const overlay  = document.getElementById("proctor-overlay");
        if (!overlay) {
            console.error("[Proctor] Overlay element missing!");
            overlayVisible = false;
            return;
        }

        const title    = document.getElementById("proctor-title");
        const message  = document.getElementById("proctor-message");
        const btn      = document.getElementById("proctor-ok-btn");

        renderChances();

        if (isFinal) {
            console.error("[Proctor] Final reset triggered.");
            title.textContent   = "🚫 Quiz Reset!";
            message.innerHTML   =
                `You have used all <strong>${CONFIG.maxWarnings} chances</strong>.<br>
                 The quiz will restart in 5 seconds...`;
            btn.textContent     = "Restart Now";
            btn.onclick         = handleFinalReset;

            // Auto-reset after 5 seconds if they don't click
            setTimeout(() => {
                if (overlayVisible && title.textContent === "🚫 Quiz Reset!") {
                    handleFinalReset();
                }
            }, 5000);
        } else {
            const remaining = CONFIG.maxWarnings - warningCount;
            title.textContent   = "⚠️ Activity Detected!";
            
            if (type === "multi_person") {
                message.innerHTML =
                    `<strong>Multiple people detected in frame!</strong><br>
                     Please ensure you are alone while taking the quiz.<br>
                     <strong>${remaining} chance${remaining !== 1 ? "s" : ""} remaining</strong>.`;
            } else {
                message.innerHTML =
                    `Our system detected you may not be focused on the quiz.<br>
                     <strong>${remaining} chance${remaining !== 1 ? "s" : ""} remaining</strong>.`;
            }

            btn.innerHTML = `I Understand`;
            btn.onclick   = dismissWarning;
        }

        // Force visibility
        overlay.setAttribute("style", "display: flex !important");
    }

    // ── Dismiss non-final warning ──────────────────────────────────────────
    function dismissWarning() {
        const overlay = document.getElementById("proctor-overlay");
        if (overlay) overlay.setAttribute("style", "display: none !important");
        overlayVisible = false;
    }

    // ── Handle final reset ─────────────────────────────────────────────────
    function handleFinalReset() {
        dismissWarning();
        resetQuiz();
        warningCount = 0;
        renderChances();
    }

    // ── Reset the active quiz to the beginning ─────────────────────────────
    function resetQuiz() {
        console.info("[Proctor] Executing full quiz reset.");
        
        // 1. Close ANY active quiz-related modals
        const modalsToHide = ["quiz-modal-container", "quiz-modal", "results-modal", "review-modal", "ai-topic-modal"];
        modalsToHide.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.add("hidden");
                el.classList.remove("flex");
            }
        });

        // 2. Click the first semester button to reload the quiz cards (visual reset)
        const firstSemBtn = document.querySelector("[data-ai-sem='1']");
        if (firstSemBtn) firstSemBtn.click();

        // 3. Scroll the study-with-ai section to top
        const section = document.getElementById("study-with-ai");
        if (section) section.scrollTop = 0;

        showToast("Quiz has been reset due to illegal activity.", "error");
    }

    // ── Lightweight toast notification ────────────────────────────────────
    function showToast(msg, type) {
        const t = document.createElement("div");
        t.style.cssText = `
            position:fixed; bottom:24px; left:50%; transform:translateX(-50%);
            background:${type === "error" ? "#dc2626" : "#0066cc"};
            color:#fff; padding:12px 24px; border-radius:12px;
            font-size:13px; font-weight:700; z-index:9999;
            box-shadow:0 4px 20px rgba(0,0,0,0.25);
            animation: proctor-fade-in 0.3s ease;`;
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 3500);
    }

    // ── Capture a single frame from the webcam as base64 JPEG ─────────────
    function captureFrame() {
        if (!videoEl || !canvasEl) return null;
        const ctx = canvasEl.getContext("2d");
        ctx.drawImage(videoEl, 0, 0, CONFIG.captureWidth, CONFIG.captureHeight);
        return canvasEl.toDataURL("image/jpeg", CONFIG.jpegQuality);
    }

    // ── Backend Health Check ───────────────────────────────────────────────
    async function checkBackendHealth() {
        try {
            const healthUrl = CONFIG.backendUrl.replace("/analyze", "/proctor/health");
            const resp = await fetch(healthUrl, { method: "GET" }).catch(e => { throw e; });
            
            const data = await resp.json().catch(() => ({ status: "error", message: "Invalid JSON response" }));
            backendHealthy = resp.ok && data.status === "ok";

            if (!backendHealthy) {
                console.warn("[Proctor] Backend health check failed:", data.message || "Unknown error");
                const errorMsg = data.message ? `Proctoring AI: ${data.message}` : "Proctoring AI backend is unreachable.";
                showToast(errorMsg, "error");
            } else {
                console.info("[Proctor] Backend is healthy and model is ready.");
            }
        } catch (err) {
            backendHealthy = false;
            console.warn("[Proctor] Backend health check failed:", err.message);
            showToast("Proctoring AI backend unreachable or offline.", "error");
        }
    }

    // ── Send frame to Moondream backend ────────────────────────────────────
    async function analyzeFrame() {
        if (isAnalyzing || !isRunning || overlayVisible || !backendHealthy) return; // Skip if backend is unhealthy
        isAnalyzing = true;

        const frame = captureFrame();
        if (!frame) { isAnalyzing = false; return; }

        try {
            const resp = await fetch(CONFIG.backendUrl, {
                method  : "POST",
                headers : { "Content-Type": "application/json" },
                body    : JSON.stringify({ image: frame }),
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            
            console.debug("[Proctor] AI Reaction:", data);

            if (data.is_distracted || data.is_multi_person) {
                warningCount++;
                const violationType = data.is_multi_person ? "multi_person" : "distraction";
                console.warn(`[Proctor] Warning ${warningCount} - Type: ${violationType} - Reason: ${data.description}`);
                showWarning(warningCount >= CONFIG.maxWarnings, violationType);
            }
        } catch (err) {
            console.warn("[Proctor] Backend communication failed:", err.message);
        } finally {
            isAnalyzing = false;
        }
    }

    // ── Detect Tab/Window switching ─────────────────────────────────────────
    function handleIllegalActivity(type) {
        if (!isRunning || overlayVisible) return;
        warningCount++;
        console.warn(`[Proctor] Illegal activity detected (${type}). Warning ${warningCount}/${CONFIG.maxWarnings}`);
        showWarning(warningCount >= CONFIG.maxWarnings);
    }

    // ── Illegal Activity Handlers ──────────────────────────────────────────
    function onBlur() { handleIllegalActivity("window transition"); }
    function onVisibilityChange() {
        if (document.visibilityState === "hidden") handleIllegalActivity("tab switch");
    }

    // ── Public API ─────────────────────────────────────────────────────────
    const Proctor = {

        async start() {
            if (isRunning) return;
            console.info("[Proctor] Starting proctoring session...");
            
            warningCount = 0; // Reset warnings on new session
            injectCSS();
            buildUI();
            
            // Initial health check
            await checkBackendHealth();

            // Request webcam access
            try {
                stream  = await navigator.mediaDevices.getUserMedia({
                    video: { width: CONFIG.captureWidth, height: CONFIG.captureHeight, facingMode: "user" },
                    audio: false,
                });
            } catch (err) {
                console.warn("[Proctor] Webcam access denied:", err.message);
                let msg = "Webcam access denied – proctoring disabled.";
                if (window.location.protocol === 'file:') {
                    msg = "ACCESS DENIED: Please use 'http://localhost:8001' instead of opening the file directly.";
                }
                showToast(msg, "error");
                return;
            }

            // Attach stream to hidden video + PiP
            videoEl       = document.getElementById("proctor-video");
            videoEl.srcObject = stream;
            await videoEl.play().catch(() => {});

            // Off-screen canvas for frame capture
            canvasEl        = document.createElement("canvas");
            canvasEl.width  = CONFIG.captureWidth;
            canvasEl.height = CONFIG.captureHeight;

            // Show PiP
            const pip = document.getElementById("proctor-pip");
            if (pip) pip.style.display = "block";

            isRunning  = true;
            intervalId = setInterval(analyzeFrame, CONFIG.captureIntervalMs);
            
            // Events for tab/window switching
            window.addEventListener("blur", onBlur);
            document.addEventListener("visibilitychange", onVisibilityChange);

            if (backendHealthy) {
                showToast("🔴 Proctoring active – stay focused!", "info");
            }
        },

        stop() {
            if (!isRunning) return;
            console.info("[Proctor] Stopping proctoring session.");
            clearInterval(intervalId);
            intervalId = null;
            isRunning  = false;

            if (stream) {
                stream.getTracks().forEach(t => t.stop());
                stream = null;
            }

            const pip = document.getElementById("proctor-pip");
            if (pip) pip.style.display = "none";
            
            // Remove event listeners
            window.removeEventListener("blur", onBlur);
            document.removeEventListener("visibilitychange", onVisibilityChange);
        },

        reset() {
            this.stop();
            warningCount = 0;
            overlayVisible = false;
        },
    };

    global.Proctor = Proctor;

})(window);
