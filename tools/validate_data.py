"""Validation script for ScrollSense Phase 1 data contracts and fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Tuple

ALLOWED_CATEGORIES = {
    "AI",
    "DSA",
    "Java",
    "HLD",
    "Cybersecurity",
    "Cloud",
    "Hardware",
    "Career",
    "Other",
}

ALLOWED_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}

REQUIRED_TECH_FIELDS = {
    "id",
    "title",
    "category",
    "concept_tags",
    "difficulty",
    "quality_score",
    "hype_score",
    "utility_score",
    "score_type",
}

REQUIRED_IDENTITY_NODES = {
    "java",
    "software_engineer",
    "developer",
    "candidate",
    "system_design",
    "dsa",
    "cloud",
    "git",
    "debugging",
    "career",
}

REQUIRED_GAMING_NODES = {
    "gaming",
    "game_development",
    "game_developer",
    "game_ai",
    "graphics",
    "gaming_hardware",
    "hardware",
    "gameplay_highlight",
    "game_ai_content",
    "gaming_laptop",
}

REQUIRED_IDENTITY_EDGES = {
    ("java", "software_engineer"),
    ("swe_lifestyle", "software_engineer"),
    ("interview_humor", "candidate"),
    ("interview_humor", "software_engineer"),
    ("laptop_comparison", "developer"),
    ("developer", "software_engineer"),
    ("software_engineer", "system_design"),
    ("software_engineer", "dsa"),
    ("software_engineer", "cloud"),
    ("software_engineer", "git"),
    ("software_engineer", "debugging"),
    ("software_engineer", "career"),
}

REQUIRED_GAMING_EDGES = {
    ("gameplay_highlight", "gaming"),
    ("game_ai_content", "game_ai"),
    ("gaming_laptop", "gaming_hardware"),
    ("gaming", "game_development"),
    ("gaming_hardware", "hardware"),
}

REQUIRED_WATCHED_TRAP_IDS = {"R1", "R2", "R3", "R4"}
REQUIRED_WATCHED_GAMING_IDS = {"R5", "R6", "R7"}

REQUIRED_TRAP_CHECKPOINTS = [
    "trap_after_R1",
    "trap_after_R1_R2",
    "trap_after_R1_R2_R3",
    "trap_after_R1_R2_R3_R4",
]

REQUIRED_OUTPUT_FIELDS = {
    "CURRENT REEL",
    "INTEREST DETECTED",
    "WHY",
    "RECOMMENDED TECH REEL",
    "CATEGORY",
    "WHY THIS RECOMMENDATION",
    "DIFFICULTY",
    "CONFIDENCE",
}

CONFIDENCE_MAP = {"Low": 0, "Medium": 1, "High": 2}

FORBIDDEN_GAMING_TERMS = [
    "java",
    "coding",
    "software engineer",
    "softwareengineer",
    "programming",
    "coding interview",
    "code review",
]


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
    data_dir = root_dir / "data"

    checks_passed = 0
    checks_total = 28
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

    # Check 01: watched_reels.json exists and valid
    w_ok, watched_data, w_msg = load_json(data_dir / "watched_reels.json")
    report(1, "data/watched_reels.json exists and is valid JSON", w_ok, w_msg)

    # Check 02: tech_reels.json exists and valid
    t_ok, tech_data, t_msg = load_json(data_dir / "tech_reels.json")
    report(2, "data/tech_reels.json exists and is valid JSON", t_ok, t_msg)

    # Check 03: identity_graph.json exists and valid
    g_ok, graph_data, g_msg = load_json(data_dir / "identity_graph.json")
    report(3, "data/identity_graph.json exists and is valid JSON", g_ok, g_msg)

    # Check 04: trap_regression.json exists and valid
    r_ok, trap_data, r_msg = load_json(data_dir / "trap_regression.json")
    report(4, "data/trap_regression.json exists and is valid JSON", r_ok, r_msg)

    # Check 05: expected_outputs.json exists and valid
    e_ok, expected_data, e_msg = load_json(data_dir / "expected_outputs.json")
    report(5, "data/expected_outputs.json exists and is valid JSON", e_ok, e_msg)

    # Check 06: watched_reels count between 6 and 8
    if w_ok and isinstance(watched_data, list):
        count = len(watched_data)
        ok = 6 <= count <= 8
        report(6, "watched_reels.json contains between 6 and 8 Reels", ok, f"Found {count} Reels")
    else:
        report(6, "watched_reels.json contains between 6 and 8 Reels", False, "Invalid data structure")

    # Check 07: watched_reels contains R1, R2, R3, R4
    if w_ok and isinstance(watched_data, list):
        reel_ids = {r.get("reel_id") for r in watched_data if isinstance(r, dict)}
        missing = REQUIRED_WATCHED_TRAP_IDS - reel_ids
        report(7, "watched_reels.json contains R1, R2, R3, and R4", len(missing) == 0, f"Missing: {missing}" if missing else f"Found all: {REQUIRED_WATCHED_TRAP_IDS}")
    else:
        report(7, "watched_reels.json contains R1, R2, R3, and R4", False, "Invalid data structure")

    # Check 08: tech_reels contains at least 25 candidates
    if t_ok and isinstance(tech_data, list):
        tech_count = len(tech_data)
        report(8, "tech_reels.json contains at least 25 candidates", tech_count >= 25, f"Found {tech_count} candidates")
    else:
        report(8, "tech_reels.json contains at least 25 candidates", False, "Invalid data structure")

    # Check 09: Every candidate has required fields
    if t_ok and isinstance(tech_data, list):
        missing_fields = []
        for idx, item in enumerate(tech_data):
            if not isinstance(item, dict):
                missing_fields.append((idx, "Not a dict"))
                continue
            diff = REQUIRED_TECH_FIELDS - set(item.keys())
            if diff:
                missing_fields.append((item.get("id", f"idx_{idx}"), str(diff)))
        report(9, "Every candidate has required fields", len(missing_fields) == 0, f"Invalid candidates: {missing_fields}" if missing_fields else "All required fields present")
    else:
        report(9, "Every candidate has required fields", False, "Invalid data structure")

    # Check 10: Every candidate CATEGORY is valid
    if t_ok and isinstance(tech_data, list):
        invalid_cats = []
        for item in tech_data:
            if isinstance(item, dict):
                cat = item.get("category")
                if cat not in ALLOWED_CATEGORIES:
                    invalid_cats.append((item.get("id"), cat))
        report(10, "Every candidate CATEGORY is valid", len(invalid_cats) == 0, f"Invalid categories: {invalid_cats}" if invalid_cats else "All categories valid")
    else:
        report(10, "Every candidate CATEGORY is valid", False, "Invalid data structure")

    # Check 11: Every candidate DIFFICULTY is valid
    if t_ok and isinstance(tech_data, list):
        invalid_diffs = []
        for item in tech_data:
            if isinstance(item, dict):
                diff = item.get("difficulty")
                if diff not in ALLOWED_DIFFICULTIES:
                    invalid_diffs.append((item.get("id"), diff))
        report(11, "Every candidate DIFFICULTY is valid", len(invalid_diffs) == 0, f"Invalid difficulties: {invalid_diffs}" if invalid_diffs else "All difficulties valid")
    else:
        report(11, "Every candidate DIFFICULTY is valid", False, "Invalid data structure")

    # Check 12: Every candidate has non-empty concept_tags
    if t_ok and isinstance(tech_data, list):
        empty_tags = []
        for item in tech_data:
            if isinstance(item, dict):
                tags = item.get("concept_tags")
                if not isinstance(tags, list) or len(tags) == 0:
                    empty_tags.append(item.get("id"))
        report(12, "Every candidate has non-empty concept_tags", len(empty_tags) == 0, f"Empty tags: {empty_tags}" if empty_tags else "All concept_tags non-empty")
    else:
        report(12, "Every candidate has non-empty concept_tags", False, "Invalid data structure")

    # Check 13: Exact hype candidate T99 exists with expected fields
    if t_ok and isinstance(tech_data, list):
        t99_item = next((item for item in tech_data if isinstance(item, dict) and item.get("id") == "T99"), None)
        t99_ok = False
        t99_msg = "T99 candidate not found"
        if t99_item:
            if (
                t99_item.get("title") == "10 AI tools that will get you a job"
                and t99_item.get("category") == "AI"
                and t99_item.get("difficulty") == "Beginner"
                and t99_item.get("quality_score") == 0.15
                and t99_item.get("hype_score") == 0.95
                and t99_item.get("utility_score") == 0.10
                and t99_item.get("score_type") == "reference_only"
            ):
                t99_ok = True
                t99_msg = "T99 exact match found with reference_only score_type"
            else:
                t99_msg = f"T99 attributes mismatch: {t99_item}"
        report(13, "The exact hype candidate T99 exists", t99_ok, t99_msg)
    else:
        report(13, "The exact hype candidate T99 exists", False, "Invalid data structure")

    # Check 14: identity_graph.json contains required nodes
    if g_ok and isinstance(graph_data, dict):
        nodes = graph_data.get("nodes", [])
        node_ids = {n.get("id") for n in nodes if isinstance(n, dict)}
        missing_nodes = REQUIRED_IDENTITY_NODES - node_ids
        report(14, "identity_graph.json contains required nodes", len(missing_nodes) == 0, f"Missing nodes: {missing_nodes}" if missing_nodes else f"Found all required {len(REQUIRED_IDENTITY_NODES)} nodes")
    else:
        report(14, "identity_graph.json contains required nodes", False, "Invalid data structure")

    # Check 15: identity_graph.json contains required edges
    if g_ok and isinstance(graph_data, dict):
        edges = graph_data.get("edges", [])
        edge_pairs = {(e.get("from"), e.get("to")) for e in edges if isinstance(e, dict)}
        missing_edges = REQUIRED_IDENTITY_EDGES - edge_pairs
        report(15, "identity_graph.json contains required edges", len(missing_edges) == 0, f"Missing edges: {missing_edges}" if missing_edges else f"Found all required {len(REQUIRED_IDENTITY_EDGES)} edges")
    else:
        report(15, "identity_graph.json contains required edges", False, "Invalid data structure")

    # Check 16: trap_regression.json references R1, R2, R3, and R4 in trap_java_to_swe
    if r_ok and isinstance(trap_data, dict):
        cases = trap_data.get("cases", [])
        trap_case = next((c for c in cases if isinstance(c, dict) and c.get("case_id") == "trap_java_to_swe"), None)
        if trap_case:
            watched_in_trap = set(trap_case.get("watched_reel_ids", []))
            missing_in_trap = REQUIRED_WATCHED_TRAP_IDS - watched_in_trap
            report(16, "trap_regression.json references R1, R2, R3, and R4 in trap_java_to_swe", len(missing_in_trap) == 0, f"Missing: {missing_in_trap}" if missing_in_trap else "References R1, R2, R3, R4")
        else:
            report(16, "trap_regression.json references R1, R2, R3, and R4 in trap_java_to_swe", False, "Case trap_java_to_swe not found")
    else:
        report(16, "trap_regression.json references R1, R2, R3, and R4 in trap_java_to_swe", False, "Invalid data structure")

    # Check 17: expected_outputs.json contains valid checkpoints dictionary
    if e_ok and isinstance(expected_data, dict) and len(expected_data) >= 4:
        report(17, "expected_outputs.json contains valid checkpoints dictionary", True, f"Found {len(expected_data)} checkpoints")
    else:
        report(17, "expected_outputs.json contains valid checkpoints dictionary", False, "Invalid checkpoints structure")

    # Check 18: Every candidate in data/tech_reels.json has score_type == "reference_only"
    if t_ok and isinstance(tech_data, list):
        non_ref = [item.get("id") for item in tech_data if isinstance(item, dict) and item.get("score_type") != "reference_only"]
        report(18, "Every candidate in tech_reels.json has score_type == 'reference_only'", len(non_ref) == 0, f"Mismatched score_type in: {non_ref}" if non_ref else "All candidates have score_type='reference_only'")
    else:
        report(18, "Every candidate in tech_reels.json has score_type == 'reference_only'", False, "Invalid data structure")

    # Check 19: data/expected_outputs.json contains the 4 required trap checkpoints
    if e_ok and isinstance(expected_data, dict):
        missing_checkpoints = [cp for cp in REQUIRED_TRAP_CHECKPOINTS if cp not in expected_data]
        report(19, "data/expected_outputs.json contains the 4 required checkpoints", len(missing_checkpoints) == 0, f"Missing checkpoints: {missing_checkpoints}" if missing_checkpoints else "All 4 required trap checkpoints present")
    else:
        report(19, "data/expected_outputs.json contains the 4 required checkpoints", False, "Invalid data structure")

    # Check 20: Each expected output entry contains all required output fields
    if e_ok and isinstance(expected_data, dict):
        missing_output_fields = []
        for cp_key, entry in expected_data.items():
            if not isinstance(entry, dict):
                missing_output_fields.append((cp_key, "Not an object"))
                continue
            diff = REQUIRED_OUTPUT_FIELDS - set(entry.keys())
            if diff:
                missing_output_fields.append((cp_key, str(diff)))
        report(20, "Each expected output entry contains all required output fields", len(missing_output_fields) == 0, f"Missing fields: {missing_output_fields}" if missing_output_fields else f"All output fields present in all {len(expected_data)} entries")
    else:
        report(20, "Each expected output entry contains all required output fields", False, "Invalid data structure")

    # Check 21: Confidence sequence across the 4 trap checkpoints is non-decreasing (Low=0, Medium=1, High=2)
    if e_ok and isinstance(expected_data, dict):
        conf_values = []
        conf_valid = True
        for cp in REQUIRED_TRAP_CHECKPOINTS:
            entry = expected_data.get(cp, {})
            conf_str = entry.get("CONFIDENCE", "")
            if conf_str not in CONFIDENCE_MAP:
                conf_valid = False
                break
            conf_values.append(CONFIDENCE_MAP[conf_str])
        
        if conf_valid and len(conf_values) == len(REQUIRED_TRAP_CHECKPOINTS):
            is_non_decreasing = all(conf_values[i] <= conf_values[i + 1] for i in range(len(conf_values) - 1))
            report(21, "Confidence sequence across checkpoints is non-decreasing", is_non_decreasing, f"Confidence sequence: {[expected_data[cp].get('CONFIDENCE') for cp in REQUIRED_TRAP_CHECKPOINTS]}")
        else:
            report(21, "Confidence sequence across checkpoints is non-decreasing", False, "Invalid or missing confidence values")
    else:
        report(21, "Confidence sequence across checkpoints is non-decreasing", False, "Invalid data structure")

    # Check 22: Every RECOMMENDED TECH REEL in expected_outputs.json exists as a title in data/tech_reels.json
    if e_ok and t_ok and isinstance(expected_data, dict) and isinstance(tech_data, list):
        candidate_titles = {item.get("title") for item in tech_data if isinstance(item, dict)}
        missing_titles = []
        for cp, entry in expected_data.items():
            if isinstance(entry, dict):
                rec_title = entry.get("RECOMMENDED TECH REEL")
                if rec_title not in candidate_titles:
                    missing_titles.append((cp, rec_title))
        report(22, "Every RECOMMENDED TECH REEL exists as a title in tech_reels.json", len(missing_titles) == 0, f"Missing titles: {missing_titles}" if missing_titles else "All recommended titles found in candidate catalog")
    else:
        report(22, "Every RECOMMENDED TECH REEL exists as a title in tech_reels.json", False, "Invalid data structure")

    # Check 23: data/trap_regression.json contains a cases array with trap_java_to_swe and non_trap_gaming_only
    if r_ok and isinstance(trap_data, dict):
        cases = trap_data.get("cases", [])
        case_ids = {c.get("case_id") for c in cases if isinstance(c, dict)}
        req_cases = {"trap_java_to_swe", "non_trap_gaming_only"}
        missing_cases = req_cases - case_ids
        report(23, "data/trap_regression.json contains cases array with required cases", len(missing_cases) == 0, f"Missing cases: {missing_cases}" if missing_cases else "Found trap_java_to_swe and non_trap_gaming_only")
    else:
        report(23, "data/trap_regression.json contains cases array with required cases", False, "Invalid data structure")

    # Check 24: non_trap_gaming_only references R5, R6, and R7
    if r_ok and isinstance(trap_data, dict):
        cases = trap_data.get("cases", [])
        gaming_case = next((c for c in cases if isinstance(c, dict) and c.get("case_id") == "non_trap_gaming_only"), None)
        if gaming_case:
            watched_in_gaming = set(gaming_case.get("watched_reel_ids", []))
            missing_in_gaming = REQUIRED_WATCHED_GAMING_IDS - watched_in_gaming
            report(24, "non_trap_gaming_only references R5, R6, and R7", len(missing_in_gaming) == 0, f"Missing: {missing_in_gaming}" if missing_in_gaming else "References R5, R6, R7")
        else:
            report(24, "non_trap_gaming_only references R5, R6, and R7", False, "Case non_trap_gaming_only not found")
    else:
        report(24, "non_trap_gaming_only references R5, R6, and R7", False, "Invalid data structure")

    # Check 25: watched_reels.json contains R5, R6, and R7
    if w_ok and isinstance(watched_data, list):
        reel_ids = {r.get("reel_id") for r in watched_data if isinstance(r, dict)}
        missing_gaming_reels = REQUIRED_WATCHED_GAMING_IDS - reel_ids
        report(25, "watched_reels.json contains R5, R6, and R7", len(missing_gaming_reels) == 0, f"Missing: {missing_gaming_reels}" if missing_gaming_reels else "Found R5, R6, R7")
    else:
        report(25, "watched_reels.json contains R5, R6, and R7", False, "Invalid data structure")

    # Check 26: R5, R6, and R7 are gaming-related and do not contain forbidden software-engineering terms
    if w_ok and isinstance(watched_data, list):
        gaming_reels = [r for r in watched_data if isinstance(r, dict) and r.get("reel_id") in REQUIRED_WATCHED_GAMING_IDS]
        valid_gaming = True
        violation_details = []
        for gr in gaming_reels:
            combined_text = (
                f"{gr.get('title', '')} {gr.get('caption', '')} {' '.join(gr.get('hashtags', []))}".lower()
            )
            # Must contain gaming or game
            if "gaming" not in combined_text and "game" not in combined_text:
                valid_gaming = False
                violation_details.append(f"{gr.get('reel_id')}: Missing gaming/game term")
            # Must not contain forbidden terms
            for forbidden in FORBIDDEN_GAMING_TERMS:
                if forbidden in combined_text:
                    valid_gaming = False
                    violation_details.append(f"{gr.get('reel_id')}: Contains forbidden term '{forbidden}'")
        report(26, "R5, R6, R7 are gaming-related without forbidden software engineering signals", valid_gaming, "; ".join(violation_details) if violation_details else "All gaming reels verified clean")
    else:
        report(26, "R5, R6, R7 are gaming-related without forbidden software engineering signals", False, "Invalid data structure")

    # Check 27: data/identity_graph.json contains all 10 gaming branch nodes
    if g_ok and isinstance(graph_data, dict):
        nodes = graph_data.get("nodes", [])
        node_ids = {n.get("id") for n in nodes if isinstance(n, dict)}
        missing_gaming_nodes = REQUIRED_GAMING_NODES - node_ids
        report(27, "identity_graph.json contains the full gaming branch nodes", len(missing_gaming_nodes) == 0, f"Missing gaming nodes: {missing_gaming_nodes}" if missing_gaming_nodes else f"Found all {len(REQUIRED_GAMING_NODES)} gaming nodes")
    else:
        report(27, "identity_graph.json contains the full gaming branch nodes", False, "Invalid data structure")

    # Check 28: data/identity_graph.json contains required gaming edges
    if g_ok and isinstance(graph_data, dict):
        edges = graph_data.get("edges", [])
        edge_pairs = {(e.get("from"), e.get("to")) for e in edges if isinstance(e, dict)}
        missing_gaming_edges = REQUIRED_GAMING_EDGES - edge_pairs
        report(28, "identity_graph.json contains required gaming edges", len(missing_gaming_edges) == 0, f"Missing gaming edges: {missing_gaming_edges}" if missing_gaming_edges else f"Found all {len(REQUIRED_GAMING_EDGES)} gaming edges")
    else:
        report(28, "identity_graph.json contains required gaming edges", False, "Invalid data structure")

    print("\n" + "=" * 50)
    print(f"Validation Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 50)

    return all_success


if __name__ == "__main__":
    success = run_checks()
    if not success:
        sys.exit(1)
    sys.exit(0)
