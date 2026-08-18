/**
 * ScrollSense Local Live Demo UI Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  const caseSelect = document.getElementById("case-select");
  const extractorSelect = document.getElementById("extractor-select");
  const explainerSelect = document.getElementById("explainer-select");
  const providerSelect = document.getElementById("provider-select");
  const optLiveLLM = document.getElementById("opt-live-llm");

  const btnRunFull = document.getElementById("btn-run-full");
  const btnRunScrollSense = document.getElementById("btn-run-scrollsense");
  const btnRunBaselines = document.getElementById("btn-run-baselines");
  const btnLoadCached = document.getElementById("btn-load-cached");
  const btnCopyOutput = document.getElementById("btn-copy-output");

  const safetyBanner = document.getElementById("safety-banner");
  const bannerMessage = document.getElementById("banner-message");

  const watchedList = document.getElementById("watched-list");
  const baselinesContent = document.getElementById("baselines-content");
  const scrollSenseContent = document.getElementById("scrollsense-content");
  const graphContent = document.getElementById("graph-content");
  const gateContent = document.getElementById("gate-content");
  const outputBlockText = document.getElementById("output-block-text");
  const traceJsonText = document.getElementById("trace-json-text");

  const aiEvidenceMode = document.getElementById("ai-evidence-mode");
  const aiFallbackStatus = document.getElementById("ai-fallback-status");

  // Initial Health Check
  fetch("/api/health")
    .then((r) => r.json())
    .then((data) => {
      if (!data.api_key_configured && optLiveLLM) {
        optLiveLLM.disabled = true;
        optLiveLLM.text = "Live API (Key Not Configured)";
      }
    })
    .catch((err) => {
      showError("Could not reach local server health endpoint: " + err.message);
    });

  function showError(msg) {
    if (safetyBanner && bannerMessage) {
      bannerMessage.textContent = msg;
      safetyBanner.classList.remove("hidden");
    }
  }

  function clearError() {
    if (safetyBanner) {
      safetyBanner.classList.add("hidden");
    }
  }

  async function executeRun(runBaselines = true) {
    clearError();
    const payload = {
      case: caseSelect.value,
      extractor: extractorSelect.value,
      explainer: explainerSelect.value,
      llm_provider: providerSelect.value,
      run_baselines: runBaselines,
    };

    setLoading(true);
    try {
      const response = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned ${response.status}`);
      }

      const data = await response.json();
      renderDashboard(data);
    } catch (err) {
      showError(`Execution error: ${err.message}. You can load cached demo data instead.`);
    } finally {
      setLoading(false);
    }
  }

  async function loadCachedDemo() {
    clearError();
    setLoading(true);
    try {
      const res = await fetch("/api/cached-demo");
      if (!res.ok) throw new Error("Could not fetch cached demo trace.");
      const traceData = await res.json();
      const caseName = caseSelect.value;
      const caseData = traceData.cases ? (traceData.cases[caseName] || traceData.cases["trap_java_to_swe"]) : null;

      if (caseData) {
        renderDashboard({
          case: caseName,
          watched_reels: caseData.watched_reels || [],
          baselines: caseData.baselines || {},
          scrollsense: caseData.scrollsense || {},
          trace: traceData,
        });
      } else {
        throw new Error("No matching case data in cached demo trace.");
      }
    } catch (err) {
      showError(`Failed loading cached demo: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  function setLoading(isLoading) {
    const btns = [btnRunFull, btnRunScrollSense, btnRunBaselines];
    btns.forEach((b) => {
      if (b) b.disabled = isLoading;
    });
    if (isLoading) {
      outputBlockText.textContent = "Running ScrollSense recommendation pipeline...";
    }
  }

  function renderDashboard(data) {
    // 1. Watched Reels
    if (data.watched_reels && data.watched_reels.length > 0) {
      watchedList.innerHTML = data.watched_reels
        .map(
          (r) => `
          <div class="reel-item">
            <div><strong>${r.reel_id}</strong>: ${r.title}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
              Format: <span class="badge badge-tag">${r.content_type || "reel"}</span>${r.topic ? ` | Topic: <span class="badge badge-tag">${r.topic}</span>` : ""}
            </div>
          </div>
        `
        )
        .join("");
    } else {
      watchedList.innerHTML = `<p class="placeholder-text">No watched reels loaded.</p>`;
    }

    // 2. Baselines
    if (data.baselines && Object.keys(data.baselines).length > 0) {
      const b1 = data.baselines.topic_only || {};
      const b2 = data.baselines.keyword_similarity || {};
      baselinesContent.innerHTML = `
        <div class="baseline-entry">
          <strong>Baseline 1 (Topic-Only):</strong>
          <p style="margin-top: 0.25rem;">Recommends: <code>${b1.recommended_candidate_id}</code> — <em>${b1.recommended_title}</em></p>
          <p style="font-size: 0.8rem; color: var(--danger); margin-top: 0.25rem;">❌ ${b1.failure_mode || "Fails trap"}</p>
        </div>
        <div class="baseline-entry" style="margin-top: 0.5rem;">
          <strong>Baseline 2 (Keyword Overlap):</strong>
          <p style="margin-top: 0.25rem;">Recommends: <code>${b2.recommended_candidate_id}</code> — <em>${b2.recommended_title}</em></p>
          <p style="font-size: 0.8rem; color: var(--danger); margin-top: 0.25rem;">❌ ${b2.failure_mode || "Overfits to literal tokens"}</p>
        </div>
      `;
    } else {
      baselinesContent.innerHTML = `<p class="placeholder-text">Baselines omitted in this run.</p>`;
    }

    // 3. ScrollSense Winner
    const ss = data.scrollsense || {};
    scrollSenseContent.innerHTML = `
      <div class="scrollsense-winner">
        <div class="winner-title">${ss.recommended_title || "Recommendation Generated"}</div>
        <p><strong>Candidate ID:</strong> <code>${ss.recommended_candidate_id || "T1"}</code> | <strong>Category:</strong> <span class="badge badge-info">${ss.category || "Career"}</span></p>
        <p style="margin-top: 0.4rem;"><strong>Inferred Identity:</strong> <span style="color: var(--primary); font-weight: 600;">${ss.top_identity || "software_engineer"}</span> (${ss.confidence || "High"} Confidence)</p>
        <p style="margin-top: 0.4rem; font-size: 0.85rem; color: var(--text-muted);">${ss.interest_detected || ""}</p>
      </div>
    `;

    // 4. Graph Activations
    if (ss.graph_activations && ss.graph_activations.length > 0) {
      graphContent.innerHTML = `
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Activated Skills & Tooling Nodes:</p>
        <div class="tag-cloud">
          ${ss.graph_activations.map((a) => `<span class="badge badge-tag">${a}</span>`).join("")}
        </div>
      `;
    } else {
      graphContent.innerHTML = `<p class="placeholder-text">No active nodes.</p>`;
    }

    // 5. Anti-Hype Gate
    if (ss.gate_rejections && ss.gate_rejections.length > 0) {
      gateContent.innerHTML = `
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Filtered Hype & Clickbait Candidates:</p>
        ${ss.gate_rejections
          .map(
            (rej) => `
            <div class="rejection-item" style="margin-bottom: 0.5rem;">
              <strong>${rej.candidate_id}</strong>: <em>${rej.title}</em>
              <div style="font-size: 0.8rem; color: var(--danger); margin-top: 0.2rem;">${rej.rejection_reason}</div>
            </div>
          `
          )
          .join("")}
      `;
    } else {
      gateContent.innerHTML = `<p class="placeholder-text">Zero candidates rejected by gate for this session.</p>`;
    }

    // 6. AI Status
    if (ss.ai) {
      aiEvidenceMode.textContent = ss.ai.llm_status === "cached" ? "Reads each Reel & writes structured evidence" : (ss.ai.llm_status === "live" ? "Live NVIDIA API evidence extraction" : "Rule-based signal extractor");
      aiFallbackStatus.textContent = ss.ai.fallback_used ? "AI fallback triggered (Rules used)" : "Yes (pre-checked AI signals)";
      aiFallbackStatus.style.color = ss.ai.fallback_used ? "var(--warning)" : "var(--success)";
    }

    // 7. Output block
    outputBlockText.textContent = ss.output_block || "No formatted block generated.";

    // 8. Trace JSON
    traceJsonText.textContent = JSON.stringify(data.trace || data, null, 2);
  }

  // Event Listeners
  btnRunFull.addEventListener("click", () => executeRun(true));
  btnRunScrollSense.addEventListener("click", () => executeRun(false));
  btnRunBaselines.addEventListener("click", () => executeRun(true));
  if (btnLoadCached) btnLoadCached.addEventListener("click", loadCachedDemo);

  if (btnCopyOutput) {
    btnCopyOutput.addEventListener("click", () => {
      const text = outputBlockText.textContent;
      navigator.clipboard.writeText(text).then(() => {
        const orig = btnCopyOutput.textContent;
        btnCopyOutput.textContent = "Copied!";
        setTimeout(() => (btnCopyOutput.textContent = orig), 1500);
      });
    });
  }

  // Run automatically on initial load
  executeRun(true);
});
