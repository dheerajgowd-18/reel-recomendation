"""Validation script for ScrollSense Phase 4 candidate retrieval."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieve import run_all_checkpoints_retrieval, run_retrieval_pipeline


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
        res_r1 = run_retrieval_pipeline(["R1"])
        res_r1_r2 = run_retrieval_pipeline(["R1", "R2"])
        res_r1_r2_r3 = run_retrieval_pipeline(["R1", "R2", "R3"])
        res_r1_r2_r3_r4 = run_retrieval_pipeline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        res_gaming = run_retrieval_pipeline(["R5", "R6", "R7"], case_name="non_trap_gaming_only")
        all_cp = run_all_checkpoints_retrieval()

        out_retrieval_path = PROJECT_ROOT / "output" / "retrieval.json"
        out_retrieval_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_retrieval_path, "w", encoding="utf-8") as f:
            json.dump(all_cp, f, indent=2)
    except Exception as exc:
        print(f"[FAIL] Execution exception during retrieval runs: {exc}")
        return False

    # Check 01: All scenarios run successfully
    report(1, "All 7 retrieval scenarios run successfully", True, "R1, R1-R2, R1-R3, R1-R4, Gaming, cases")

    # Check 02: output/retrieval.json is valid JSON
    json_valid = False
    try:
        with open(out_retrieval_path, "r", encoding="utf-8") as f:
            loaded_json = json.load(f)
        json_valid = isinstance(loaded_json, dict)
    except Exception:
        json_valid = False
    report(2, "output/retrieval.json is valid JSON", json_valid, str(out_retrieval_path.relative_to(PROJECT_ROOT)))

    # Check 03: Every retrieval result contains required top-level keys
    req_top_keys = {
        "phase",
        "case",
        "reel_ids",
        "interest_summary",
        "sources",
        "candidates",
        "candidate_count",
        "generated_at",
    }
    top_keys_ok = all(
        req_top_keys.issubset(set(r.keys()))
        for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]
    )
    report(3, "Every retrieval result contains required schema fields", top_keys_ok, "All top-level keys present")

    # Check 04: Every candidate entry contains required candidate fields
    req_cand_keys = {
        "candidate_id",
        "title",
        "category",
        "difficulty",
        "retrieval_score",
        "sources",
        "matched_terms",
        "matched_nodes",
    }
    cand_keys_ok = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        for c in r["candidates"]:
            if not req_cand_keys.issubset(set(c.keys())):
                cand_keys_ok = False
    report(4, "Every candidate entry contains all required candidate fields", cand_keys_ok, "Candidate schema valid")

    # Check 05: retrieval_score is between 0.0 and 1.0
    scores_valid = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        for c in r["candidates"]:
            score = float(c["retrieval_score"])
            if not (0.0 <= score <= 1.0):
                scores_valid = False
    report(5, "Every candidate retrieval_score is between 0.0 and 1.0", scores_valid, "Scores in bounds")

    # Check 06: Final trap case retrieves at least 8 candidates
    trap_count = len(res_r1_r2_r3_r4["candidates"])
    report(6, "Final trap case retrieves at least 8 candidates", trap_count >= 8, f"Found {trap_count} candidates")

    # Check 07: Final trap case retrieves T1
    trap_ids = {c["candidate_id"] for c in res_r1_r2_r3_r4["candidates"]}
    report(7, "Final trap case retrieves T1 ('How a junior software engineer ships a small feature')", "T1" in trap_ids, f"T1 present: {'T1' in trap_ids}")

    # Check 08: Final trap case top 5 candidates include at least one Career-category candidate
    top5_trap = res_r1_r2_r3_r4["candidates"][:5]
    top5_trap_cats = [c["category"] for c in top5_trap]
    report(8, "Final trap case top 5 candidates include at least one Career candidate", "Career" in top5_trap_cats, f"Top 5 categories: {top5_trap_cats}")

    # Check 09: Final trap case top 5 candidates are not all Java-category candidates
    not_all_java = any(c["category"] != "Java" for c in top5_trap)
    report(9, "Final trap case top 5 candidates are not all Java candidates", not_all_java, f"Categories: {top5_trap_cats}")

    # Check 10: Final trap case identity_adjacent source contains at least 5 candidates
    id_adj_count = len(res_r1_r2_r3_r4["sources"]["identity_adjacent"])
    report(10, "Final trap case identity_adjacent source contains at least 5 candidates", id_adj_count >= 5, f"Found {id_adj_count} candidates")

    # Check 11: T99 is not top-ranked retrieved candidate for final trap case
    top_trap_cand = top5_trap[0]["candidate_id"] if top5_trap else ""
    report(11, "T99 is not top-ranked for final trap case", top_trap_cand != "T99", f"Top candidate: {top_trap_cand}")

    # Check 12: T99 is not top-ranked retrieved candidate for gaming case
    top5_gaming = res_gaming["candidates"][:5]
    top_gaming_cand = top5_gaming[0]["candidate_id"] if top5_gaming else ""
    report(12, "T99 is not top-ranked for gaming case", top_gaming_cand != "T99", f"Top gaming candidate: {top_gaming_cand}")

    # Check 13: Gaming case retrieves at least 5 candidates
    gaming_count = len(res_gaming["candidates"])
    report(13, "Gaming case retrieves at least 5 candidates", gaming_count >= 5, f"Found {gaming_count} candidates")

    # Check 14: Gaming case retrieves at least one of T24, T25, T26
    gaming_ids = {c["candidate_id"] for c in res_gaming["candidates"]}
    found_gaming_expected = bool(gaming_ids.intersection({"T24", "T25", "T26"}))
    report(14, "Gaming case retrieves at least one of T24, T25, T26", found_gaming_expected, f"Retrieved gaming targets: {gaming_ids.intersection({'T24', 'T25', 'T26'})}")

    # Check 15: Gaming top 5 does not include T1
    top5_gaming_ids = [c["candidate_id"] for c in top5_gaming]
    report(15, "Gaming case top 5 candidates do not include T1", "T1" not in top5_gaming_ids, f"Top 5 gaming IDs: {top5_gaming_ids}")

    # Check 16: Gaming top 5 does not include T5
    report(16, "Gaming case top 5 candidates do not include T5", "T5" not in top5_gaming_ids, f"Top 5 gaming IDs: {top5_gaming_ids}")

    # Check 17: Gaming top 5 does not include T23
    report(17, "Gaming case top 5 candidates do not include T23", "T23" not in top5_gaming_ids, f"Top 5 gaming IDs: {top5_gaming_ids}")

    # Check 18: Running retrieval twice produces identical candidate ordering
    res_repeat = run_retrieval_pipeline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
    order_orig = [c["candidate_id"] for c in res_r1_r2_r3_r4["candidates"]]
    order_repeat = [c["candidate_id"] for c in res_repeat["candidates"]]
    report(18, "Retrieval is strictly deterministic on repeated execution", order_orig == order_repeat, f"Deterministic: {order_orig == order_repeat}")

    print("\n" + "=" * 50)
    print(f"Retrieval Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
