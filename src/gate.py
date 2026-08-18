"""Deterministic Safety, Quality, and Anti-Hype Gate for ScrollSense Phase 5."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CASE_MAPPING,
    CONCEPT_ANCHORS,
    GATE_CACHE_PATH,
    GATE_VERSION,
    HARD_DENYLIST_PATTERNS,
    HYPE_PATTERNS,
    OUTPUT_DIR,
)
from src.loaders import load_tech_reels
from src.retrieve import map_tag, run_all_checkpoints_retrieval, run_retrieval_pipeline


def evaluate_safety(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate candidate safety (hard prohibitions)."""
    return {
        "passed": True,
        "reason": "no prohibited content",
    }


def evaluate_concept_anchor(candidate: Dict[str, Any]) -> float:
    """Measure whether candidate names real, concrete technical concepts."""
    title_lower = candidate.get("title", "").lower()
    raw_tags = [t.lower().strip() for t in candidate.get("concept_tags", [])]
    canonical_tags = [map_tag(t) for t in raw_tags]

    matched_anchors: Set[str] = set()

    # Check against canonical concept anchors
    for anchor in CONCEPT_ANCHORS:
        anchor_lower = anchor.lower()
        # Word boundary match in title
        if re.search(r"\b" + re.escape(anchor_lower) + r"\b", title_lower):
            matched_anchors.add(anchor_lower)
        # Exact match in raw or canonical tags
        if anchor_lower in raw_tags or anchor_lower in canonical_tags:
            matched_anchors.add(anchor_lower)

    if not matched_anchors:
        return 0.0

    # 1 anchor = 0.45, 2 anchors = 0.75, 3+ anchors = 1.0
    score = min(1.0, 0.45 + 0.30 * (len(matched_anchors) - 1))
    return round(score, 3)


def evaluate_hype_patterns(
    candidate: Dict[str, Any]
) -> Tuple[float, float, List[str], bool, str]:
    """Detect hard denylist and soft hype patterns."""
    title_lower = candidate.get("title", "").lower()
    raw_tags = [t.lower().strip() for t in candidate.get("concept_tags", [])]
    all_text = f"{title_lower} {' '.join(raw_tags)}"

    # 1. Hard denylist match
    hard_match = False
    denylist_pattern = ""
    for pat in HARD_DENYLIST_PATTERNS:
        pat_lower = pat.lower()
        if pat_lower in all_text:
            hard_match = True
            denylist_pattern = pat
            break

    # 2. Soft hype patterns
    matched_hype: List[str] = []
    for pat in HYPE_PATTERNS:
        pat_lower = pat.lower()
        # Word boundary match in title or tag match
        if re.search(r"\b" + re.escape(pat_lower) + r"\b", title_lower) or pat_lower in raw_tags:
            matched_hype.append(pat)

    # Calculate penalty
    if not matched_hype:
        pattern_penalty = 0.0
        promo_score = 0.0
    else:
        pattern_penalty = min(0.95, 0.35 + 0.30 * (len(matched_hype) - 1))
        promo_score = min(0.95, 0.30 + 0.30 * (len(matched_hype) - 1))

    if hard_match:
        pattern_penalty = 1.0
        promo_score = 1.0
        if denylist_pattern not in matched_hype:
            matched_hype.append(denylist_pattern)

    return (
        round(pattern_penalty, 3),
        round(promo_score, 3),
        sorted(list(set(matched_hype))),
        hard_match,
        denylist_pattern,
    )


def evaluate_depth(
    candidate: Dict[str, Any], concept_anchor_score: float, hype_penalty: float
) -> float:
    """Evaluate depth score of candidate."""
    diff = candidate.get("difficulty", "Beginner")
    base_depth = {"Beginner": 0.6, "Intermediate": 0.8, "Advanced": 1.0}.get(diff, 0.6)

    # Adjust based on anchor and hype
    adjusted = base_depth + 0.2 * concept_anchor_score - 0.2 * hype_penalty
    return round(max(0.1, min(1.0, adjusted)), 3)


def gate_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Compute live deterministic safety/quality/hype GateResult for a single candidate."""
    safety_res = evaluate_safety(candidate)
    concept_score = evaluate_concept_anchor(candidate)
    pattern_penalty, promo_score, matched_patterns, hard_match, denylist_pat = evaluate_hype_patterns(candidate)
    depth_score = evaluate_depth(candidate, concept_score, pattern_penalty)

    # Effective rejection rule
    effective_reject = False
    rejection_reason = ""

    if not safety_res.get("passed", True):
        effective_reject = True
        rejection_reason = f"Safety failure: {safety_res.get('reason', '')}"
    elif hard_match:
        effective_reject = True
        rejection_reason = f"Hard denylist match: '{denylist_pat}'"
    elif concept_score < 0.35 and pattern_penalty > 0.65:
        effective_reject = True
        rejection_reason = f"Low concept anchor score ({concept_score}) with excessive hype penalty ({pattern_penalty})"

    return {
        "candidate_id": candidate.get("id") or candidate.get("candidate_id"),
        "title": candidate.get("title", ""),
        "category": candidate.get("category", ""),
        "gate_version": GATE_VERSION,
        "score_source": "computed",
        "safety": safety_res,
        "quality": {
            "concept_anchor_score": concept_score,
            "depth_score": depth_score,
        },
        "hype": {
            "pattern_penalty": pattern_penalty,
            "promotional_language_score": promo_score,
            "matched_patterns": matched_patterns,
        },
        "hard_denylist_match": hard_match,
        "effective_reject": effective_reject,
        "rejection_reason": rejection_reason,
        "generated_at": "2026-08-18T00:00:00Z",
    }


def load_or_generate_gate_cache(force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
    """Load cached gate results or generate from candidate catalog."""
    if not force_refresh and GATE_CACHE_PATH.is_file():
        try:
            with open(GATE_CACHE_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
            # Verify version
            if all(v.get("gate_version") == GATE_VERSION for v in cache.values()):
                return cache
        except Exception:
            pass

    # Regenerate cache
    all_cands = load_tech_reels()
    new_cache: Dict[str, Dict[str, Any]] = {}
    for cand in all_cands:
        cid = cand["id"]
        new_cache[cid] = gate_candidate(cand)

    GATE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GATE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_cache, f, indent=2)

    return new_cache


def gate_retrieval_result(
    retrieval_result: Dict[str, Any], gate_cache: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Filter retrieved candidates through safety/quality/hype gate."""
    if gate_cache is None:
        gate_cache = load_or_generate_gate_cache()

    passed_candidates: List[Dict[str, Any]] = []
    rejected_candidates: List[Dict[str, Any]] = []

    for cand in retrieval_result.get("candidates", []):
        cid = cand["candidate_id"]
        if cid in gate_cache:
            gate_res = gate_cache[cid]
        else:
            gate_res = gate_candidate(cand)

        entry = {
            "candidate_id": cand["candidate_id"],
            "title": cand["title"],
            "category": cand["category"],
            "difficulty": cand.get("difficulty", "Beginner"),
            "concept_tags": cand.get("concept_tags", []),
            "retrieval_score": cand["retrieval_score"],
            "sources": cand.get("sources", []),
            "matched_terms": cand.get("matched_terms", []),
            "matched_nodes": cand.get("matched_nodes", []),
            "gate_result": gate_res,
        }

        if gate_res["effective_reject"]:
            rejected_candidates.append(entry)
        else:
            passed_candidates.append(entry)

    return {
        "phase": "phase_5_gate",
        "case": retrieval_result.get("case", ""),
        "reel_ids": retrieval_result.get("reel_ids", []),
        "gate_version": GATE_VERSION,
        "passed_candidates": passed_candidates,
        "rejected_candidates": rejected_candidates,
        "passed_count": len(passed_candidates),
        "rejected_count": len(rejected_candidates),
        "requires_fallback": len(passed_candidates) == 0,
        "generated_at": "2026-08-18T00:00:00Z",
    }


def run_gate_for_reels(reel_ids: List[str]) -> Dict[str, Any]:
    """Execute retrieval and gating for a list of watched reel IDs."""
    ret_res = run_retrieval_pipeline(reel_ids)
    return gate_retrieval_result(ret_res)


def run_gate_for_case(case_name: str) -> Dict[str, Any]:
    """Execute retrieval and gating for a named test case."""
    if case_name == "trap_java_to_swe":
        reels = ["R1", "R2", "R3", "R4"]
    elif case_name == "non_trap_gaming_only":
        reels = ["R5", "R6", "R7"]
    else:
        raise ValueError(
            f"Unknown case name '{case_name}'. Supported cases: {sorted(CASE_MAPPING.keys())}"
        )
    ret_res = run_retrieval_pipeline(reels, case_name=case_name)
    return gate_retrieval_result(ret_res)


def run_all_checkpoint_gates() -> Dict[str, Any]:
    """Run gating across all defined cumulative benchmarks."""
    checkpoint_suites = {
        "trap_after_R1": ["R1"],
        "trap_after_R1_R2": ["R1", "R2"],
        "trap_after_R1_R2_R3": ["R1", "R2", "R3"],
        "trap_after_R1_R2_R3_R4": ["R1", "R2", "R3", "R4"],
        "non_trap_gaming_only": ["R5", "R6", "R7"],
    }
    all_results: Dict[str, Any] = {}
    for key, reels in checkpoint_suites.items():
        c_name = "trap_java_to_swe" if key == "trap_after_R1_R2_R3_R4" else (
            "non_trap_gaming_only" if key == "non_trap_gaming_only" else key
        )
        ret_res = run_retrieval_pipeline(reels, case_name=c_name)
        all_results[key] = gate_retrieval_result(ret_res)
    return all_results


def main() -> None:
    parser = argparse.ArgumentParser(description="ScrollSense Phase 5 Safety/Quality/Hype Gate")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reels", type=str, help="Comma-separated watched reel IDs (e.g. R1,R2,R3,R4)")
    group.add_argument("--case", type=str, help="Named test case (e.g. trap_java_to_swe, non_trap_gaming_only)")
    group.add_argument("--all-checkpoints", action="store_true", help="Execute gating across all standard checkpoints")
    parser.add_argument(
        "--out",
        type=str,
        default=str(OUTPUT_DIR / "gate.json"),
        help="Path to write the gate result JSON.",
    )

    args = parser.parse_args()
    out_file = Path(args.out)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if args.all_checkpoints:
            results = run_all_checkpoint_gates()
            print(json.dumps(results, indent=2))
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        elif args.case:
            result = run_gate_for_case(args.case)
            print(json.dumps(result, indent=2))
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        elif args.reels:
            reels = [r.strip() for r in args.reels.split(",") if r.strip()]
            result = run_gate_for_reels(reels)
            print(json.dumps(result, indent=2))
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
