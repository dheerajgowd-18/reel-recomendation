"""Validation script for ScrollSense Phase 2 signal extraction module and cache."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ALLOWED_EVIDENCE_TYPES = {
    "topic_exposure",
    "domain_signal",
    "professional_identity_signal",
    "career_stage_signal",
    "goal_signal",
    "skill_signal",
    "tooling_signal",
    "content_preference_signal",
}

REQUIRED_SIGNAL_FIELDS = {
    "reel_id",
    "signal_version",
    "ontology_version",
    "model_version",
    "generated_at",
    "topic",
    "format",
    "tone",
    "depth",
    "concept_tags",
    "interest_evidence",
}

REQUIRED_EVIDENCE_FIELDS = {
    "evidence_type",
    "value",
    "strength",
    "source_hint",
}

GAMING_REEL_IDS = {"R5", "R6", "R7"}


def load_json(path: Path) -> Tuple[bool, Any, str]:
    if not path.is_file():
        return False, None, f"File does not exist: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data, "Valid JSON"
    except Exception as exc:
        return False, None, f"JSON parse error: {exc}"


def run_checks() -> bool:
    root_dir = Path(__file__).resolve().parent.parent
    cache_file = root_dir / "cache" / "signals.json"
    watched_file = root_dir / "data" / "watched_reels.json"

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

    # Check 01: cache/signals.json exists and is valid JSON
    c_ok, cache_data, c_msg = load_json(cache_file)
    report(1, "cache/signals.json exists and is valid JSON", c_ok, c_msg)

    w_ok, watched_data, _ = load_json(watched_file)
    watched_ids = {r["reel_id"] for r in watched_data if isinstance(r, dict) and "reel_id" in r} if w_ok and isinstance(watched_data, list) else set()

    # Normalize extracted signals map from cache
    signals_map: Dict[str, Dict[str, Any]] = {}
    if c_ok and isinstance(cache_data, dict):
        for k, v in cache_data.items():
            if isinstance(v, dict) and "signal" in v and isinstance(v["signal"], dict):
                signals_map[k] = v["signal"]
            elif isinstance(v, dict):
                signals_map[k] = v

    # Check 02: Every watched reel has a signal
    if c_ok and watched_ids:
        missing = watched_ids - set(signals_map.keys())
        report(2, "Every watched reel in watched_reels.json has a signal", len(missing) == 0, f"Missing: {missing}" if missing else f"Found signals for all {len(watched_ids)} reels")
    else:
        report(2, "Every watched reel in watched_reels.json has a signal", False, "Invalid cache or watched reels data")

    # Check 03: Every signal contains required fields
    if c_ok and signals_map:
        missing_sig_fields = []
        for r_id, sig in signals_map.items():
            diff = REQUIRED_SIGNAL_FIELDS - set(sig.keys())
            if diff:
                missing_sig_fields.append((r_id, str(diff)))
        report(3, "Every signal contains required fields", len(missing_sig_fields) == 0, f"Invalid signals: {missing_sig_fields}" if missing_sig_fields else "All required signal fields present")
    else:
        report(3, "Every signal contains required fields", False, "Invalid cache data")

    # Check 04: Every evidence item contains required fields
    if c_ok and signals_map:
        missing_ev_fields = []
        for r_id, sig in signals_map.items():
            ev_list = sig.get("interest_evidence", [])
            if not isinstance(ev_list, list) or len(ev_list) == 0:
                missing_ev_fields.append((r_id, "Empty evidence list"))
                continue
            for idx, ev in enumerate(ev_list):
                diff = REQUIRED_EVIDENCE_FIELDS - set(ev.keys())
                if diff:
                    missing_ev_fields.append((f"{r_id}[{idx}]", str(diff)))
        report(4, "Every evidence item contains required fields", len(missing_ev_fields) == 0, f"Invalid evidence items: {missing_ev_fields}" if missing_ev_fields else "All evidence fields present")
    else:
        report(4, "Every evidence item contains required fields", False, "Invalid cache data")

    # Check 05: Every evidence_type is allowed
    if c_ok and signals_map:
        invalid_ev_types = []
        for r_id, sig in signals_map.items():
            for ev in sig.get("interest_evidence", []):
                t = ev.get("evidence_type")
                if t not in ALLOWED_EVIDENCE_TYPES:
                    invalid_ev_types.append((r_id, t))
        report(5, "Every evidence_type is allowed", len(invalid_ev_types) == 0, f"Invalid types: {invalid_ev_types}" if invalid_ev_types else "All evidence_type values valid")
    else:
        report(5, "Every evidence_type is allowed", False, "Invalid cache data")

    # Check 06: Every strength is between 0.0 and 1.0
    if c_ok and signals_map:
        invalid_strengths = []
        for r_id, sig in signals_map.items():
            for ev in sig.get("interest_evidence", []):
                s = ev.get("strength")
                if not isinstance(s, (int, float)) or not (0.0 <= float(s) <= 1.0):
                    invalid_strengths.append((r_id, s))
        report(6, "Every strength is between 0.0 and 1.0", len(invalid_strengths) == 0, f"Invalid strengths: {invalid_strengths}" if invalid_strengths else "All strength values within [0.0, 1.0]")
    else:
        report(6, "Every strength is between 0.0 and 1.0", False, "Invalid cache data")

    # Check 07: R1 contains java topic exposure
    r1_sig = signals_map.get("R1", {})
    r1_ev = r1_sig.get("interest_evidence", [])
    has_r1_java = any(ev.get("evidence_type") == "topic_exposure" and ev.get("value") == "java" and 0.5 <= float(ev.get("strength", 0)) <= 0.8 for ev in r1_ev)
    report(7, "R1 contains java topic exposure (strength 0.5-0.8)", has_r1_java, "Found java topic exposure" if has_r1_java else "Missing valid java topic exposure in R1")

    # Check 08: R1 software_engineer professional_identity_signal <= 0.45
    r1_swe_ev = [ev for ev in r1_ev if ev.get("evidence_type") == "professional_identity_signal" and ev.get("value") == "software_engineer"]
    r1_swe_ok = all(float(ev.get("strength", 0)) <= 0.45 for ev in r1_swe_ev)
    report(8, "R1 software_engineer professional identity signal strength <= 0.45", r1_swe_ok, f"R1 SWE strength: {[ev.get('strength') for ev in r1_swe_ev]}" if r1_swe_ev else "No SWE signal in R1 (valid)")

    # Check 09: R2 contains software_engineer professional_identity_signal >= 0.75
    r2_sig = signals_map.get("R2", {})
    r2_ev = r2_sig.get("interest_evidence", [])
    has_r2_swe = any(ev.get("evidence_type") == "professional_identity_signal" and ev.get("value") == "software_engineer" and float(ev.get("strength", 0)) >= 0.75 for ev in r2_ev)
    report(9, "R2 contains software_engineer professional identity signal >= 0.75", has_r2_swe, "Found strong software_engineer signal in R2" if has_r2_swe else "Missing/weak software_engineer signal in R2")

    # Check 10: R3 contains career_stage_signal candidate
    r3_sig = signals_map.get("R3", {})
    r3_ev = r3_sig.get("interest_evidence", [])
    has_r3_cand = any(ev.get("evidence_type") == "career_stage_signal" and ev.get("value") == "candidate" and float(ev.get("strength", 0)) >= 0.7 for ev in r3_ev)
    report(10, "R3 contains career_stage_signal candidate >= 0.7", has_r3_cand, "Found candidate career stage in R3" if has_r3_cand else "Missing candidate career stage in R3")

    # Check 11: R3 contains software_engineer professional_identity_signal >= 0.6
    has_r3_swe = any(ev.get("evidence_type") == "professional_identity_signal" and ev.get("value") == "software_engineer" and float(ev.get("strength", 0)) >= 0.6 for ev in r3_ev)
    report(11, "R3 contains software_engineer professional identity signal >= 0.6", has_r3_swe, "Found SWE identity in R3" if has_r3_swe else "Missing/weak SWE identity in R3")

    # Check 12: R4 contains tooling_signal developer_hardware
    r4_sig = signals_map.get("R4", {})
    r4_ev = r4_sig.get("interest_evidence", [])
    has_r4_tooling = any(ev.get("evidence_type") == "tooling_signal" and ev.get("value") == "developer_hardware" and float(ev.get("strength", 0)) >= 0.5 for ev in r4_ev)
    report(12, "R4 contains tooling_signal developer_hardware >= 0.5", has_r4_tooling, "Found developer_hardware tooling signal in R4" if has_r4_tooling else "Missing developer_hardware signal in R4")

    # Check 13: R5 contains gaming domain_signal >= 0.75
    r5_sig = signals_map.get("R5", {})
    r5_ev = r5_sig.get("interest_evidence", [])
    has_r5_gaming = any(ev.get("evidence_type") == "domain_signal" and ev.get("value") == "gaming" and float(ev.get("strength", 0)) >= 0.75 for ev in r5_ev)
    report(13, "R5 contains gaming domain_signal >= 0.75", has_r5_gaming, "Found gaming domain signal in R5" if has_r5_gaming else "Missing gaming domain signal in R5")

    # Check 14: R6 contains game_ai skill_signal >= 0.65
    r6_sig = signals_map.get("R6", {})
    r6_ev = r6_sig.get("interest_evidence", [])
    has_r6_game_ai = any(ev.get("evidence_type") == "skill_signal" and ev.get("value") == "game_ai" and float(ev.get("strength", 0)) >= 0.65 for ev in r6_ev)
    report(14, "R6 contains game_ai skill_signal >= 0.65", has_r6_game_ai, "Found game_ai skill signal in R6" if has_r6_game_ai else "Missing game_ai skill signal in R6")

    # Check 15: R7 contains gaming_hardware tooling_signal >= 0.65
    r7_sig = signals_map.get("R7", {})
    r7_ev = r7_sig.get("interest_evidence", [])
    has_r7_gh = any(ev.get("evidence_type") == "tooling_signal" and ev.get("value") == "gaming_hardware" and float(ev.get("strength", 0)) >= 0.65 for ev in r7_ev)
    report(15, "R7 contains gaming_hardware tooling_signal >= 0.65", has_r7_gh, "Found gaming_hardware tooling signal in R7" if has_r7_gh else "Missing gaming_hardware tooling signal in R7")

    # Check 16: R5, R6, R7 do not contain software_engineer identity > 0.2
    gaming_swe_violations = []
    for g_id in GAMING_REEL_IDS:
        sig = signals_map.get(g_id, {})
        for ev in sig.get("interest_evidence", []):
            if ev.get("evidence_type") == "professional_identity_signal" and ev.get("value") == "software_engineer":
                if float(ev.get("strength", 0)) > 0.2:
                    gaming_swe_violations.append((g_id, ev.get("strength")))
    report(16, "R5, R6, R7 do not contain software_engineer identity > 0.2", len(gaming_swe_violations) == 0, f"Violations: {gaming_swe_violations}" if gaming_swe_violations else "All gaming reels clean of SWE identity")

    # Check 17: R5, R6, R7 do not contain career_stage_signal candidate
    gaming_cand_violations = []
    for g_id in GAMING_REEL_IDS:
        sig = signals_map.get(g_id, {})
        for ev in sig.get("interest_evidence", []):
            if ev.get("evidence_type") == "career_stage_signal" and ev.get("value") == "candidate":
                gaming_cand_violations.append(g_id)
    report(17, "R5, R6, R7 do not contain career_stage_signal candidate", len(gaming_cand_violations) == 0, f"Violations: {gaming_cand_violations}" if gaming_cand_violations else "All gaming reels clean of candidate stage")

    # Check 18: R5, R6, R7 do not contain goal_signal career_prep
    gaming_prep_violations = []
    for g_id in GAMING_REEL_IDS:
        sig = signals_map.get(g_id, {})
        for ev in sig.get("interest_evidence", []):
            if ev.get("evidence_type") == "goal_signal" and ev.get("value") == "career_prep":
                gaming_prep_violations.append(g_id)
    report(18, "R5, R6, R7 do not contain goal_signal career_prep", len(gaming_prep_violations) == 0, f"Violations: {gaming_prep_violations}" if gaming_prep_violations else "All gaming reels clean of career_prep goal")

    print("\n" + "=" * 50)
    print(f"Signal Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
