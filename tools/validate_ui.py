"""Validation script for ScrollSense Phase 9B/9C UI server, static assets, accessibility, and security contracts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from ui.server import app

DEMO_TRACE_FILE = PROJECT_ROOT / "output" / "demo_trace.json"


def run_ui_checks() -> bool:
    checks_passed = 0
    checks_total = 23
    all_success = True

    def report(num: int, name: str, success: bool, detail: str = ""):
        nonlocal checks_passed, all_success
        status = "PASS" if success else "FAIL"
        detail_msg = f" - {detail}" if detail else ""
        print(f"[{status}] Check {num:02d}: {name}{detail_msg}")
        if success:
            checks_passed += 1
        else:
            all_success = False

    # Check 1: requirements-ui.txt exists
    req_file = PROJECT_ROOT / "requirements-ui.txt"
    report(1, "requirements-ui.txt exists", req_file.is_file(), str(req_file.name))

    # Check 2: ui/server.py exists
    server_file = PROJECT_ROOT / "ui" / "server.py"
    report(2, "ui/server.py exists", server_file.is_file(), str(server_file.name))

    # Check 3: ui/static/index.html exists
    html_file = PROJECT_ROOT / "ui" / "static" / "index.html"
    report(3, "ui/static/index.html exists", html_file.is_file(), str(html_file.name))

    # Check 4: ui/static/styles.css exists
    css_file = PROJECT_ROOT / "ui" / "static" / "styles.css"
    report(4, "ui/static/styles.css exists", css_file.is_file(), str(css_file.name))

    # Check 5: ui/static/app.js exists
    js_file = PROJECT_ROOT / "ui" / "static" / "app.js"
    report(5, "ui/static/app.js exists", js_file.is_file(), str(js_file.name))

    client = TestClient(app)

    # Check 6: UI server can start in test mode and GET / returns HTML
    resp_root = client.get("/")
    report(6, "UI server can start and GET / returns 200 HTML", resp_root.status_code == 200 and "ScrollSense" in resp_root.text, f"Status: {resp_root.status_code}")

    # Check 7: /api/health returns OK
    resp_health = client.get("/api/health")
    h_data = resp_health.json() if resp_health.status_code == 200 else {}
    report(7, "/api/health returns OK and health metadata", h_data.get("status") == "ok", f"Status: {h_data.get('status')}")

    # Check 8: /api/run returns trap result
    resp_trap = client.post("/api/run", json={"case": "trap_java_to_swe", "run_baselines": True})
    t_data = resp_trap.json() if resp_trap.status_code == 200 else {}
    t_rec = t_data.get("scrollsense", {}).get("recommended_candidate_id")
    report(8, "/api/run returns trap result recommending T1", t_rec == "T1", f"Recommended: {t_rec}")

    # Check 9: /api/run returns gaming result
    resp_game = client.post("/api/run", json={"case": "non_trap_gaming_only", "run_baselines": True})
    g_data = resp_game.json() if resp_game.status_code == 200 else {}
    g_rec = g_data.get("scrollsense", {}).get("recommended_candidate_id")
    report(9, "/api/run returns gaming result recommending T24", g_rec == "T24", f"Recommended: {g_rec}")

    # Check 10: No external CDN links exist in index.html
    html_text = html_file.read_text(encoding="utf-8") if html_file.is_file() else ""
    no_cdn = ("http://" not in html_text) and ("https://" not in html_text)
    report(10, "No external CDN or HTTP/HTTPS links in index.html", no_cdn, "Verified 100% offline local static assets")

    # Check 11: Default UI mode does not require live LLM
    default_provider = h_data.get("llm_provider_default")
    report(11, "Default UI mode does not require live LLM", default_provider == "cache", f"Default Provider: {default_provider}")

    # Check 12: Cached demo fallback file exists
    report(12, "Cached demo fallback file exists", DEMO_TRACE_FILE.is_file(), str(DEMO_TRACE_FILE.name))

    # Check 13: AI model name appears in API response
    ai_model = t_data.get("scrollsense", {}).get("ai", {}).get("model", "")
    report(13, "NVIDIA Nemotron model appears in API response", "nemotron" in ai_model.lower(), f"Model: {ai_model}")

    # Check 14: T99 rejection appears in final trap API response
    rejs = t_data.get("scrollsense", {}).get("gate_rejections", [])
    has_t99 = any(r.get("candidate_id") == "T99" for r in rejs)
    report(14, "T99 rejection appears in final trap API response", has_t99, f"T99 Rejected: {has_t99}")

    # Check 15: Security headers present in responses
    headers_ok = (
        resp_root.headers.get("x-content-type-options") == "nosniff"
        and resp_root.headers.get("x-frame-options") == "DENY"
        and resp_root.headers.get("referrer-policy") == "no-referrer"
    )
    report(15, "Security headers present in responses", headers_ok, "nosniff, DENY, no-referrer")

    # Check 16: Invalid case returns 422
    resp_bad_case = client.post("/api/run", json={"case": "invalid_hacked_case"})
    report(16, "Invalid case name rejected with 422", resp_bad_case.status_code == 422, f"Status: {resp_bad_case.status_code}")

    # Check 17: Invalid extractor returns 422
    resp_bad_ext = client.post("/api/run", json={"case": "trap_java_to_swe", "extractor": "malicious_eval"})
    report(17, "Invalid extractor rejected with 422", resp_bad_ext.status_code == 422, f"Status: {resp_bad_ext.status_code}")

    # Check 18: index.html contains lang="en"
    has_lang = 'lang="en"' in html_text
    report(18, "index.html declares lang='en'", has_lang, "Accessibility language attribute")

    # Check 19: index.html contains semantic <main> landmark
    has_main = "<main" in html_text
    report(19, "index.html contains semantic <main> landmark", has_main, "Semantic HTML landmark")

    # Check 20: index.html contains aria-live
    has_aria_live = "aria-live" in html_text
    report(20, "index.html contains aria-live region", has_aria_live, "Screen reader dynamic updates")

    # Check 21: index.html contains role="alert"
    has_alert = 'role="alert"' in html_text
    report(21, "index.html error banner has role='alert'", has_alert, "Accessible error notification")

    # Check 22: index.html contains keyboard skip link
    has_skip = "skip-link" in html_text
    report(22, "index.html contains keyboard skip-to-content link", has_skip, "Keyboard navigation accessibility")

    # Check 23: All <select> elements have associated <label>
    select_ids = re.findall(r'<select[^>]*id="([^"]+)"', html_text)
    labels_for = re.findall(r'<label[^>]*for="([^"]+)"', html_text)
    all_labeled = bool(select_ids) and all(s_id in labels_for for s_id in select_ids)
    report(23, "All <select> elements have associated <label>", all_labeled, f"Validated select IDs: {select_ids}")

    print("\n" + "=" * 50)
    print(f"UI Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_ui_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
