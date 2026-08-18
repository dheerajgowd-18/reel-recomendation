"""Validation script for ScrollSense Phase 3 inference, InterestState, and graph traversal."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infer import infer_interests, run_all_checkpoints


def run_checks() -> bool:
    checks_passed = 0
    checks_total = 14
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
        # Run inferences for all checkpoints
        res_r1 = infer_interests(["R1"])
        res_r1_r2 = infer_interests(["R1", "R2"])
        res_r1_r2_r3 = infer_interests(["R1", "R2", "R3"])
        res_r1_r2_r3_r4 = infer_interests(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        res_gaming = infer_interests(["R5", "R6", "R7"], case_name="non_trap_gaming_only")
        all_cp = run_all_checkpoints()
    except Exception as exc:
        print(f"[FAIL] Execution exception during inference runs: {exc}")
        return False

    # Check 01: All checkpoint runs succeed
    report(1, "All 5 inference scenarios execute successfully", True, "R1, R1-R2, R1-R3, R1-R4, Gaming")

    # Check 02: InterestState contains all required keys
    req_state_keys = {
        "student_id",
        "session_id",
        "reel_ids",
        "professional_identity",
        "career_stage",
        "domains",
        "goals",
        "depth",
        "content_preference",
        "evidence",
        "updated_at",
    }
    state_keys_ok = all(
        req_state_keys.issubset(set(r["interest_state"].keys()))
        for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]
    )
    report(2, "InterestState contains all required schema keys", state_keys_ok, "Schema verified")

    # Check 03: All InterestState weights are between 0.0 and 1.0
    weights_valid = True
    for r in [res_r1, res_r1_r2, res_r1_r2_r3, res_r1_r2_r3_r4, res_gaming]:
        st = r["interest_state"]
        for section in ["professional_identity", "career_stage", "domains", "goals", "content_preference"]:
            for k, v in st.get(section, {}).items():
                if not (0.0 <= float(v) <= 1.0):
                    weights_valid = False
    report(3, "All InterestState weights are between 0.0 and 1.0", weights_valid, "Weights in bounds")

    # Check 04: R1 alone produces Low confidence and weak SWE identity (<= 0.45)
    r1_swe = res_r1["interest_state"]["professional_identity"].get("software_engineer", 0.0)
    r1_ok = res_r1["confidence"] == "Low" and r1_swe <= 0.45
    report(4, "R1 produces Low confidence and weak SWE identity (<= 0.45)", r1_ok, f"Confidence: {res_r1['confidence']}, SWE: {r1_swe}")

    # Check 05: R1+R2 produces Medium confidence and meaningful SWE identity (>= 0.75)
    r2_swe = res_r1_r2["interest_state"]["professional_identity"].get("software_engineer", 0.0)
    r2_ok = res_r1_r2["confidence"] == "Medium" and r2_swe >= 0.75
    report(5, "R1+R2 produces Medium confidence and meaningful SWE identity (>= 0.75)", r2_ok, f"Confidence: {res_r1_r2['confidence']}, SWE: {r2_swe}")

    # Check 06: R1+R2+R3 produces High confidence and candidate career stage (>= 0.70)
    r3_cand = res_r1_r2_r3["interest_state"]["career_stage"].get("candidate", 0.0)
    r3_ok = res_r1_r2_r3["confidence"] == "High" and r3_cand >= 0.70
    report(6, "R1+R2+R3 produces High confidence and candidate career stage (>= 0.70)", r3_ok, f"Confidence: {res_r1_r2_r3['confidence']}, Candidate: {r3_cand}")

    # Check 07: Final trap case (R1-R4) produces High confidence and SWE identity >= 0.85
    r4_swe = res_r1_r2_r3_r4["interest_state"]["professional_identity"].get("software_engineer", 0.0)
    r4_ok = res_r1_r2_r3_r4["confidence"] == "High" and r4_swe >= 0.85
    report(7, "Final trap case produces High confidence and SWE identity >= 0.85", r4_ok, f"Confidence: {res_r1_r2_r3_r4['confidence']}, SWE: {r4_swe}")

    # Check 08: Confidence progression is strictly non-decreasing across trap checkpoints
    conf_seq = [res_r1["confidence"], res_r1_r2["confidence"], res_r1_r2_r3["confidence"], res_r1_r2_r3_r4["confidence"]]
    conf_map = {"Low": 0, "Medium": 1, "High": 2}
    seq_nums = [conf_map[c] for c in conf_seq]
    seq_ok = all(seq_nums[i] <= seq_nums[i + 1] for i in range(len(seq_nums) - 1))
    report(8, "Confidence progression is non-decreasing across trap sequence", seq_ok, f"Sequence: {conf_seq}")

    # Check 09: Final trap graph traversal activates software engineering core nodes
    r4_activated = {a["node"] for a in res_r1_r2_r3_r4["graph_traversal"]["activated_nodes"]}
    expected_swe_nodes = {"career", "git", "debugging", "system_design", "dsa", "cloud"}
    trap_graph_ok = expected_swe_nodes.issubset(r4_activated)
    report(9, "Trap graph traversal activates SWE core competency nodes", trap_graph_ok, f"Activated: {r4_activated}")

    # Check 10: Gaming non-trap case produces Medium confidence and gaming domain >= 0.75
    g_dom = res_gaming["interest_state"]["domains"].get("gaming", 0.0)
    g_ok = res_gaming["confidence"] == "Medium" and g_dom >= 0.75
    report(10, "Gaming non-trap produces Medium confidence and gaming domain >= 0.75", g_ok, f"Confidence: {res_gaming['confidence']}, Gaming: {g_dom}")

    # Check 11: Gaming non-trap has NO software_engineer identity > 0.2 and NO candidate stage
    g_swe = res_gaming["interest_state"]["professional_identity"].get("software_engineer", 0.0)
    g_cand = res_gaming["interest_state"]["career_stage"].get("candidate", 0.0)
    g_clean = g_swe <= 0.2 and g_cand == 0.0
    report(11, "Gaming non-trap contains no SWE identity (>0.2) or candidate career stage", g_clean, f"SWE: {g_swe}, Candidate: {g_cand}")

    # Check 12: Gaming graph traversal activates gaming branch nodes and NOT SWE
    g_activated = {a["node"] for a in res_gaming["graph_traversal"]["activated_nodes"]}
    g_expected = {"game_development", "graphics", "game_ai", "game_developer"}
    g_graph_ok = g_expected.issubset(g_activated) and "software_engineer" not in g_activated
    report(12, "Gaming graph traversal activates gaming nodes without SWE activation", g_graph_ok, f"Gaming Activated: {g_activated}")

    # Check 13: Inferred interest labels match expectation heuristics
    labels_ok = (
        "gaming" in res_gaming["inferred_interest_label"].lower()
        and "software engineer" not in res_gaming["inferred_interest_label"].lower()
        and "software engineering" in res_r1_r2_r3_r4["inferred_interest_label"].lower()
    )
    report(13, "Inferred interest labels conform to domain boundary heuristics", labels_ok, f"Trap: '{res_r1_r2_r3_r4['inferred_interest_label']}', Gaming: '{res_gaming['inferred_interest_label']}'")

    # Check 14: run_all_checkpoints returns all 5 benchmark keys
    all_keys = set(all_cp.keys())
    expected_all_keys = {
        "trap_after_R1",
        "trap_after_R1_R2",
        "trap_after_R1_R2_R3",
        "trap_after_R1_R2_R3_R4",
        "non_trap_gaming_only",
    }
    all_cp_ok = expected_all_keys.issubset(all_keys)
    report(14, "run_all_checkpoints returns all 5 standard benchmark results", all_cp_ok, f"Keys: {all_keys}")

    print("\n" + "=" * 50)
    print(f"Inference Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
