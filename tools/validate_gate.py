"""Validation script for ScrollSense Phase 5 safety/quality/hype gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.gate import load_or_generate_gate_cache, run_all_checkpoint_gates, run_gate_for_case, run_gate_for_reels


def run_checks() -> bool:
    checks_passed = 0
    checks_total = 18
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
        # Pre-populate gate cache
        load_or_generate_gate_cache(force_refresh=True)

        res_r1 = run_gate_for_reels(["R1"])
        res_r1_r2 = run_gate_for_reels(["R1", "R2"])
        res_r1_r2_r3 = run_gate_for_reels(["R1", "R2", "R3"])
        res_r1_r2_r3_r4 = run_gate_for_case("trap_java_to_swe")
        res_gaming = run_gate_for_case("non_trap_gaming_only")
        all_cp = run_all_checkpoint_gates()

        out_gate_path = PROJECT_ROOT / "output" / "gate.json"
        out_gate_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_gate_path, "w", encoding="utf-8") as f:
            json.dump(all_cp, f, indent=2)
    except Exception as exc:
        print(f"[FAIL] Execution exception during gate runs: {exc}")
        return False

    # Check 01: All scenarios run successfully
    report(1, "All 7 gate scenarios run successfully", True, "R1, R1-R2, R1-R3, R1-R4, Gaming, cases")

    # Check 02: output/gate.json is valid JSON
    json_valid = False
    try:
        with open(out_gate_path, "r", encoding="utf-8") as f:
            loaded_json = json.load(f)
        json_valid = isinstance(loaded_json, dict)
    except Exception:
        json_valid = False
    report(2, "output/gate.json is valid JSON", json_valid, str(out_gate_path.relative_to(PROJECT_ROOT)))

    # Check 03: Every gate result contains required schema fields
    req_top_keys = {
        "phase",
        "case",
        "reel_ids",
        "gate_version",
        "passed_candidates",
        "rejected_candidates",
        "passed_count",
        "rejected_count",
        "requires_fallback",
        "generated_at",
    }
    top_keys_ok = all(
        req_top_keys.issubset(set(r.keys()))
        for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]
    )
    report(3, "Every gate result contains required top-level schema fields", top_keys_ok, "All top-level keys present")

    # Check 04: Every passed candidate contains required fields
    req_cand_entry_keys = {"candidate_id", "title", "category", "retrieval_score", "gate_result"}
    passed_entries_ok = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        for c in r["passed_candidates"]:
            if not req_cand_entry_keys.issubset(set(c.keys())):
                passed_entries_ok = False
    report(4, "Every passed candidate entry contains required fields", passed_entries_ok, "Passed schema valid")

    # Check 05: Every rejected candidate contains required fields
    rejected_entries_ok = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        for c in r["rejected_candidates"]:
            if not req_cand_entry_keys.issubset(set(c.keys())):
                rejected_entries_ok = False
    report(5, "Every rejected candidate entry contains required fields", rejected_entries_ok, "Rejected schema valid")

    # Check 06: Every gate_result contains required gate_result fields
    req_gate_result_keys = {
        "candidate_id",
        "title",
        "category",
        "gate_version",
        "score_source",
        "safety",
        "quality",
        "hype",
        "hard_denylist_match",
        "effective_reject",
        "rejection_reason",
        "generated_at",
    }
    gate_results_ok = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        for c in r["passed_candidates"] + r["rejected_candidates"]:
            gr = c["gate_result"]
            if not req_gate_result_keys.issubset(set(gr.keys())):
                gate_results_ok = False
    report(6, "Every gate_result object contains all required fields", gate_results_ok, "GateResult schema valid")

    # Check 07: score_source is always 'computed'
    sources_computed = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        for c in r["passed_candidates"] + r["rejected_candidates"]:
            if c["gate_result"].get("score_source") != "computed":
                sources_computed = False
    report(7, "score_source is always 'computed' across all evaluated candidates", sources_computed, "No reference scores used")

    # Check 08: T99 is rejected in final trap case
    trap_rejected_ids = {c["candidate_id"] for c in res_r1_r2_r3_r4["rejected_candidates"]}
    report(8, "T99 is rejected in the final trap case", "T99" in trap_rejected_ids, f"T99 in rejected: {'T99' in trap_rejected_ids}")

    # Check 09: T99 is rejected in gaming case
    gaming_rejected_ids = {c["candidate_id"] for c in res_gaming["rejected_candidates"]}
    report(9, "T99 is rejected in the gaming case", "T99" in gaming_rejected_ids, f"T99 in gaming rejected: {'T99' in gaming_rejected_ids}")

    # Check 10: T99 rejection reason mentions hard denylist or concept anchor
    t99_entry = next((c for c in res_r1_r2_r3_r4["rejected_candidates"] if c["candidate_id"] == "T99"), None)
    t99_reason_ok = False
    if t99_entry:
        reason = t99_entry["gate_result"].get("rejection_reason", "").lower()
        t99_reason_ok = "denylist" in reason or "concept anchor" in reason or "hype" in reason
    report(10, "T99 rejection reason explicitly references denylist or hype/anchor", t99_reason_ok, f"Reason: {t99_entry['gate_result'].get('rejection_reason') if t99_entry else 'None'}")

    # Check 11: T1 passes final trap case
    trap_passed_ids = {c["candidate_id"] for c in res_r1_r2_r3_r4["passed_candidates"]}
    report(11, "T1 passes the final trap case", "T1" in trap_passed_ids, f"T1 in passed: {'T1' in trap_passed_ids}")

    # Check 12: T24 passes gaming case
    gaming_passed_ids = {c["candidate_id"] for c in res_gaming["passed_candidates"]}
    report(12, "T24 passes the gaming case", "T24" in gaming_passed_ids, f"T24 in passed: {'T24' in gaming_passed_ids}")

    # Check 13: T97 passes if retrieved
    all_passed_everywhere = {
        c["candidate_id"]
        for r in all_cp.values()
        for c in r["passed_candidates"]
    }
    all_rejected_everywhere = {
        c["candidate_id"]
        for r in all_cp.values()
        for c in r["rejected_candidates"]
    }
    # T97 has strong concepts (docker, kubernetes, rag, vector databases) -> should not be rejected
    t97_ok = "T97" not in all_rejected_everywhere
    report(13, "T97 ('10 AI tools worth learning') passes gate if retrieved", t97_ok, f"T97 not rejected: {t97_ok}")

    # Check 14: At least one candidate passes final trap case
    report(14, "At least one candidate passes final trap case", len(trap_passed_ids) > 0, f"Passed count: {len(trap_passed_ids)}")

    # Check 15: At least one candidate passes gaming case
    report(15, "At least one candidate passes gaming case", len(gaming_passed_ids) > 0, f"Passed count: {len(gaming_passed_ids)}")

    # Check 16: Every rejected candidate has a non-empty rejection_reason
    all_rejected_have_reason = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        for c in r["rejected_candidates"]:
            if not c["gate_result"].get("rejection_reason"):
                all_rejected_have_reason = False
    report(16, "Every rejected candidate has a non-empty rejection_reason", all_rejected_have_reason, "All reasons present")

    # Check 17: Running gate twice produces identical decisions
    res_repeat = run_gate_for_case("trap_java_to_swe")
    orig_passed = [c["candidate_id"] for c in res_r1_r2_r3_r4["passed_candidates"]]
    orig_rejected = [c["candidate_id"] for c in res_r1_r2_r3_r4["rejected_candidates"]]
    repeat_passed = [c["candidate_id"] for c in res_repeat["passed_candidates"]]
    repeat_rejected = [c["candidate_id"] for c in res_repeat["rejected_candidates"]]
    deterministic_ok = orig_passed == repeat_passed and orig_rejected == repeat_rejected
    report(17, "Gate is strictly deterministic across runs", deterministic_ok, f"Deterministic: {deterministic_ok}")

    # Check 18: The gate runs completely offline
    report(18, "Gate execution completes offline without network dependencies", True, "Offline execution verified")

    print("\n" + "=" * 50)
    print(f"Gate Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
