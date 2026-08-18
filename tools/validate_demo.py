"""Validation script for ScrollSense Phase 7 demo harness, baselines, and reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.demo import (
    DEMO_HTML_PATH,
    DEMO_REPORT_PATH,
    DEMO_TRACE_PATH,
    PITCH_LINE,
    run_demo,
)


def run_checks() -> bool:
    checks_passed = 0
    checks_total = 20
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

    try:
        demo_trace1 = run_demo(all_cases=True)
    except Exception as exc:
        print(f"[FAIL] Execution exception during demo run: {exc}")
        return False

    cases = demo_trace1.get("cases", {})
    trap_case = cases.get("trap_java_to_swe", {})
    gaming_case = cases.get("non_trap_gaming_only", {})

    # Check 01: Demo runs successfully for all cases
    report(1, "Demo runs successfully for all cases", bool(cases and trap_case and gaming_case), f"Cases: {list(cases.keys())}")

    # Check 02: output/demo_trace.json exists and is valid JSON
    trace_valid = False
    try:
        with open(DEMO_TRACE_PATH, "r", encoding="utf-8") as f:
            loaded_trace = json.load(f)
        trace_valid = isinstance(loaded_trace, dict)
    except Exception:
        trace_valid = False
    report(2, "output/demo_trace.json exists and is valid JSON", trace_valid, str(DEMO_TRACE_PATH.relative_to(PROJECT_ROOT)))

    # Check 03: output/demo_report.md exists
    report_exists = DEMO_REPORT_PATH.is_file() and len(DEMO_REPORT_PATH.read_text(encoding="utf-8").strip()) > 0
    report(3, "output/demo_report.md exists and contains text", report_exists, str(DEMO_REPORT_PATH.relative_to(PROJECT_ROOT)))

    # Check 04: output/demo.html exists
    html_exists = DEMO_HTML_PATH.is_file() and len(DEMO_HTML_PATH.read_text(encoding="utf-8").strip()) > 0
    report(4, "output/demo.html exists and contains HTML", html_exists, str(DEMO_HTML_PATH.relative_to(PROJECT_ROOT)))

    # Check 05: Final trap includes Baseline 1
    has_b1 = "topic_only" in trap_case.get("baselines", {})
    report(5, "Final trap case includes Baseline 1 (topic_only)", has_b1, f"Found: {has_b1}")

    # Check 06: Final trap includes Baseline 2
    has_b2 = "keyword_similarity" in trap_case.get("baselines", {})
    report(6, "Final trap case includes Baseline 2 (keyword_similarity)", has_b2, f"Found: {has_b2}")

    # Check 07: Baseline 1 final trap recommends T96 or Java content
    b1_rec = trap_case.get("baselines", {}).get("topic_only", {}).get("recommended_candidate_id", "")
    b1_cat = trap_case.get("baselines", {}).get("topic_only", {}).get("category", "")
    b1_ok = b1_rec == "T96" or b1_cat == "Java"
    report(7, "Baseline 1 final trap recommendation is T96 or Java category", b1_ok, f"Recommended: {b1_rec} ({b1_cat})")

    # Check 08: Baseline 1 final trap recommendation is not T1
    report(8, "Baseline 1 final trap recommendation is not T1", b1_rec != "T1", f"Recommended: {b1_rec}")

    # Check 09: Baseline 2 final trap recommendation is not T1
    b2_rec = trap_case.get("baselines", {}).get("keyword_similarity", {}).get("recommended_candidate_id", "")
    report(9, "Baseline 2 final trap recommendation is not T1", b2_rec != "T1", f"Recommended: {b2_rec}")

    # Check 10: ScrollSense final trap recommendation is T1
    ss_rec = trap_case.get("scrollsense", {}).get("recommended_candidate_id", "")
    report(10, "ScrollSense final trap recommendation is T1", ss_rec == "T1", f"Recommended: {ss_rec}")

    # Check 11: ScrollSense final trap confidence is High
    ss_conf = trap_case.get("scrollsense", {}).get("confidence", "")
    report(11, "ScrollSense final trap confidence is High", ss_conf == "High", f"Confidence: {ss_conf}")

    # Check 12: ScrollSense final trap interest contains software engineering
    ss_int = trap_case.get("scrollsense", {}).get("interest_detected", "")
    report(12, "ScrollSense final trap interest contains software engineering", "software engineering" in ss_int.lower(), f"Interest: '{ss_int}'")

    # Check 13: ScrollSense final trap includes graph activations
    ss_acts = trap_case.get("scrollsense", {}).get("graph_activations", [])
    report(13, "ScrollSense final trap trace includes graph activations", len(ss_acts) > 0, f"Activations count: {len(ss_acts)}")

    # Check 14: ScrollSense final trap includes T99 rejection
    rejs = trap_case.get("scrollsense", {}).get("gate_rejections", [])
    t99_rej = any(r.get("candidate_id") == "T99" for r in rejs)
    report(14, "ScrollSense final trap trace includes T99 anti-hype rejection", t99_rej, f"T99 rejected: {t99_rej}")

    # Check 15: ScrollSense gaming recommendation is T24
    g_rec = gaming_case.get("scrollsense", {}).get("recommended_candidate_id", "")
    report(15, "ScrollSense gaming recommendation is T24", g_rec == "T24", f"Recommended: {g_rec}")

    # Check 16: ScrollSense gaming interest contains gaming
    g_int = gaming_case.get("scrollsense", {}).get("interest_detected", "")
    report(16, "ScrollSense gaming interest contains gaming wording", "gaming" in g_int.lower(), f"Interest: '{g_int}'")

    # Check 17: ScrollSense gaming interest does not contain software engineering
    report(17, "ScrollSense gaming interest does not contain software engineering", "software engineer" not in g_int.lower(), f"Interest: '{g_int}'")

    # Check 18: ScrollSense gaming recommendation is not T1, T5, or T23
    report(18, "ScrollSense gaming recommendation is not T1, T5, or T23", g_rec not in {"T1", "T5", "T23"}, f"Recommended: {g_rec}")

    # Check 19: Demo report contains exact pitch line
    report_text = DEMO_REPORT_PATH.read_text(encoding="utf-8")
    report(19, "Demo report markdown contains exact pitch line", PITCH_LINE in report_text, "Exact pitch line verified in markdown")

    # Check 20: Running demo twice produces identical demo_trace.json
    demo_trace2 = run_demo(all_cases=True)
    report(20, "Demo execution is strictly deterministic across runs", demo_trace1 == demo_trace2, f"Deterministic: {demo_trace1 == demo_trace2}")

    print("\n" + "=" * 50)
    print(f"Demo Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
