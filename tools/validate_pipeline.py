"""Validation script for ScrollSense Phase 6 pipeline, ranking, explanations, and exact outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ALLOWED_CATEGORIES, ALLOWED_CONFIDENCES, ALLOWED_DIFFICULTIES, REQUIRED_OUTPUT_FIELDS
from src.loaders import load_expected_outputs
from src.pipeline import run_all_checkpoint_pipelines, run_pipeline_for_case, run_pipeline_for_reels


def parse_output_block(text: str) -> Dict[str, str]:
    """Parse key-value pairs from formatted output block."""
    result: Dict[str, str] = {}
    for line in text.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            result[key.strip()] = val.strip()
    return result


def run_checks() -> bool:
    checks_passed = 0
    checks_total = 25
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
        # Run real mode pipelines
        txt_r1, trace_r1 = run_pipeline_for_reels(["R1"], mode="real")
        txt_r1_r2, trace_r1_r2 = run_pipeline_for_reels(["R1", "R2"], mode="real")
        txt_r1_r2_r3, trace_r1_r2_r3 = run_pipeline_for_reels(["R1", "R2", "R3"], mode="real")
        txt_trap, trace_trap = run_pipeline_for_case("trap_java_to_swe", mode="real")
        txt_gaming, trace_gaming = run_pipeline_for_case("non_trap_gaming_only", mode="real")
        all_cp = run_all_checkpoint_pipelines(mode="real")

        out_res_path = PROJECT_ROOT / "output" / "result.txt"
        out_trace_path = PROJECT_ROOT / "output" / "pipeline_trace.json"

        with open(out_res_path, "w", encoding="utf-8") as f:
            f.write(txt_trap + "\n")
        with open(out_trace_path, "w", encoding="utf-8") as f:
            json.dump(trace_trap, f, indent=2)

        expected_data = load_expected_outputs()
        expected_cps = expected_data.get("checkpoints", expected_data)
    except Exception as exc:
        print(f"[FAIL] Execution exception during pipeline validation: {exc}")
        return False

    parsed_r1 = parse_output_block(txt_r1)
    parsed_r1_r2 = parse_output_block(txt_r1_r2)
    parsed_r1_r2_r3 = parse_output_block(txt_r1_r2_r3)
    parsed_trap = parse_output_block(txt_trap)
    parsed_gaming = parse_output_block(txt_gaming)
    all_parsed = [parsed_r1, parsed_r1_r2, parsed_r1_r2_r3, parsed_trap, parsed_gaming]
    all_traces = [trace_r1, trace_r1_r2, trace_r1_r2_r3, trace_trap, trace_gaming]

    # Check 01: Pipeline runs successfully in real mode
    report(1, "Pipeline runs successfully in real mode across all cases", True, "All executions succeeded")

    # Check 02: No fallback used in real mode
    no_fallback = all(not t.get("fallback_used", True) for t in all_traces)
    report(2, "No fallback triggered in real mode validation", no_fallback, "Real mode execution verified")

    # Check 03: output/result.txt exists and is valid text
    res_exists = out_res_path.is_file() and len(out_res_path.read_text(encoding="utf-8").strip()) > 0
    report(3, "output/result.txt exists and contains formatted output", res_exists, str(out_res_path.relative_to(PROJECT_ROOT)))

    # Check 04: output/pipeline_trace.json exists and is valid JSON
    trace_json_valid = False
    try:
        with open(out_trace_path, "r", encoding="utf-8") as f:
            loaded_trace = json.load(f)
        trace_json_valid = isinstance(loaded_trace, dict)
    except Exception:
        trace_json_valid = False
    report(4, "output/pipeline_trace.json exists and is valid JSON", trace_json_valid, str(out_trace_path.relative_to(PROJECT_ROOT)))

    # Check 05: Every output contains all required labels
    req_labels_ok = all(
        all(label in p for label in REQUIRED_OUTPUT_FIELDS)
        for p in all_parsed
    )
    report(5, "Every output contains all 8 required contract labels", req_labels_ok, "All fields present")

    # Check 06: Every CATEGORY is valid
    cats_valid = all(p.get("CATEGORY") in ALLOWED_CATEGORIES for p in all_parsed)
    report(6, "Every recommended CATEGORY is in allowed set", cats_valid, f"Categories: {[p.get('CATEGORY') for p in all_parsed]}")

    # Check 07: Every DIFFICULTY is valid
    diffs_valid = all(p.get("DIFFICULTY") in ALLOWED_DIFFICULTIES for p in all_parsed)
    report(7, "Every recommended DIFFICULTY is in allowed set", diffs_valid, f"Difficulties: {[p.get('DIFFICULTY') for p in all_parsed]}")

    # Check 08: Every CONFIDENCE is valid
    confs_valid = all(p.get("CONFIDENCE") in ALLOWED_CONFIDENCES for p in all_parsed)
    report(8, "Every recommendation CONFIDENCE is in allowed set", confs_valid, f"Confidences: {[p.get('CONFIDENCE') for p in all_parsed]}")

    # Check 09: R1 output recommends T22
    r1_rec = parsed_r1.get("RECOMMENDED TECH REEL", "")
    report(9, "R1 output recommends T22 ('Beginner programming concepts explained with memes')", "memes" in r1_rec.lower() or "programming concepts" in r1_rec.lower(), f"Recommended: '{r1_rec}'")

    # Check 10: R1 confidence is Low
    r1_conf = parsed_r1.get("CONFIDENCE", "")
    report(10, "R1 confidence is Low", r1_conf == "Low", f"Confidence: {r1_conf}")

    # Check 11: R1+R2 output recommends T23
    r2_rec = parsed_r1_r2.get("RECOMMENDED TECH REEL", "")
    report(11, "R1+R2 output recommends T23 ('What software engineers actually do all day')", "software engineers actually do" in r2_rec.lower(), f"Recommended: '{r2_rec}'")

    # Check 12: R1+R2 confidence is Medium
    r2_conf = parsed_r1_r2.get("CONFIDENCE", "")
    report(12, "R1+R2 confidence is Medium", r2_conf == "Medium", f"Confidence: {r2_conf}")

    # Check 13: R1+R2+R3 output recommends T5
    r3_rec = parsed_r1_r2_r3.get("RECOMMENDED TECH REEL", "")
    report(13, "R1+R2+R3 output recommends T5 ('What a coding interview is really testing')", "coding interview" in r3_rec.lower(), f"Recommended: '{r3_rec}'")

    # Check 14: R1+R2+R3 confidence is High
    r3_conf = parsed_r1_r2_r3.get("CONFIDENCE", "")
    report(14, "R1+R2+R3 confidence is High", r3_conf == "High", f"Confidence: {r3_conf}")

    # Check 15: R1+R2+R3+R4 output recommends T1
    trap_rec = parsed_trap.get("RECOMMENDED TECH REEL", "")
    report(15, "Final trap output recommends T1 ('How a junior software engineer ships a small feature')", "ships a small feature" in trap_rec.lower(), f"Recommended: '{trap_rec}'")

    # Check 16: R1+R2+R3+R4 confidence is High
    trap_conf = parsed_trap.get("CONFIDENCE", "")
    report(16, "Final trap confidence is High", trap_conf == "High", f"Confidence: {trap_conf}")

    # Check 17: R5+R6+R7 output recommends T24
    gaming_rec = parsed_gaming.get("RECOMMENDED TECH REEL", "")
    report(17, "Gaming output recommends T24 ('How game AI decides enemy behavior')", "game ai" in gaming_rec.lower(), f"Recommended: '{gaming_rec}'")

    # Check 18: R5+R6+R7 confidence is Medium
    gaming_conf = parsed_gaming.get("CONFIDENCE", "")
    report(18, "Gaming confidence is Medium", gaming_conf == "Medium", f"Confidence: {gaming_conf}")

    # Check 19: T99 is never recommended
    all_recs = [p.get("RECOMMENDED TECH REEL", "") for p in all_parsed]
    t99_never = all("10 ai tools that will get you a job" not in r.lower() for r in all_recs)
    report(19, "T99 is never recommended across any pipeline execution", t99_never, "T99 completely absent")

    # Check 20: Final trap INTEREST DETECTED contains software engineering wording
    trap_interest = parsed_trap.get("INTEREST DETECTED", "")
    report(20, "Final trap INTEREST DETECTED contains software engineering wording", "software engineering" in trap_interest.lower(), f"Interest: '{trap_interest}'")

    # Check 21: Gaming INTEREST DETECTED contains gaming wording
    gaming_interest = parsed_gaming.get("INTEREST DETECTED", "")
    report(21, "Gaming INTEREST DETECTED contains gaming wording", "gaming" in gaming_interest.lower(), f"Interest: '{gaming_interest}'")

    # Check 22: Gaming INTEREST DETECTED does not contain software engineering wording
    report(22, "Gaming INTEREST DETECTED does not contain software engineering wording", "software engineer" not in gaming_interest.lower(), f"Interest: '{gaming_interest}'")

    # Check 23: Final trap matches expected output fields
    exp_trap = expected_cps.get("trap_after_R1_R2_R3_R4", {})
    trap_match_ok = (
        parsed_trap.get("CURRENT REEL") == exp_trap.get("CURRENT REEL")
        and parsed_trap.get("RECOMMENDED TECH REEL") == exp_trap.get("RECOMMENDED TECH REEL")
        and parsed_trap.get("CATEGORY") == exp_trap.get("CATEGORY")
        and parsed_trap.get("DIFFICULTY") == exp_trap.get("DIFFICULTY")
        and parsed_trap.get("CONFIDENCE") == exp_trap.get("CONFIDENCE")
    )
    report(23, "Final trap output matches expected fields in expected_outputs.json", trap_match_ok, "Exact match on key contract fields")

    # Check 24: Gaming matches expected output fields
    exp_gaming = expected_cps.get("non_trap_gaming_only", {})
    gaming_match_ok = (
        parsed_gaming.get("CURRENT REEL") == exp_gaming.get("CURRENT REEL")
        and parsed_gaming.get("RECOMMENDED TECH REEL") == exp_gaming.get("RECOMMENDED TECH REEL")
        and parsed_gaming.get("CATEGORY") == exp_gaming.get("CATEGORY")
        and parsed_gaming.get("DIFFICULTY") == exp_gaming.get("DIFFICULTY")
        and parsed_gaming.get("CONFIDENCE") == exp_gaming.get("CONFIDENCE")
    )
    report(24, "Gaming output matches expected fields in expected_outputs.json", gaming_match_ok, "Exact match on key contract fields")

    # Check 25: Pipeline is strictly deterministic
    txt_repeat, _ = run_pipeline_for_case("trap_java_to_swe", mode="real")
    report(25, "Pipeline output is strictly deterministic on repeated execution", txt_trap == txt_repeat, f"Deterministic: {txt_trap == txt_repeat}")

    print("\n" + "=" * 50)
    print(f"Pipeline Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
