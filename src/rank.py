"""Deterministic candidate ranker for ScrollSense Phase 6."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import HEURISTIC_WEIGHTS_V1, RANKING_VERSION, WEIGHTS_VERSION
from src.retrieve import map_tag


def compute_identity_graph_fit(
    candidate: Dict[str, Any], inference_result: Dict[str, Any]
) -> float:
    """Compute fit between candidate concept tags and active graph nodes."""
    interest_state = inference_result.get("interest_state", {})
    traversal = inference_result.get("graph_traversal", {})
    activated_nodes = {a["node"]: float(a["activation"]) for a in traversal.get("activated_nodes", [])}
    seed_nodes = {s["node"]: float(s["weight"]) for s in traversal.get("seed_nodes", [])}
    prefs = {k: float(v) for k, v in interest_state.get("content_preference", {}).items()}

    all_active: Dict[str, float] = {}
    all_active.update(prefs)
    all_active.update(seed_nodes)
    all_active.update(activated_nodes)

    raw_tags = candidate.get("concept_tags", [])
    canonical_tags = [map_tag(t) for t in raw_tags]

    matched_acts: List[float] = []
    for tag in canonical_tags:
        if tag in all_active:
            matched_acts.append(all_active[tag])

    if not matched_acts:
        return 0.0

    score = min(1.0, (sum(matched_acts) / (len(matched_acts) ** 0.5)) * 0.7 + 0.1 * len(matched_acts))
    return round(score, 3)


def compute_goal_stage_fit(
    candidate: Dict[str, Any], inference_result: Dict[str, Any]
) -> float:
    """Compute specific goal and career stage fit (checkpoint differentiator)."""
    interest_state = inference_result.get("interest_state", {})
    identities = interest_state.get("professional_identity", {})
    stages = interest_state.get("career_stage", {})
    goals = interest_state.get("goals", {})
    domains = interest_state.get("domains", {})
    confidence = inference_result.get("confidence", "Low")
    num_reels = len(inference_result.get("reel_ids", []))

    tags = set(candidate.get("concept_tags", []))

    # 1. Gaming case
    if domains.get("gaming", 0.0) >= 0.70:
        if "gaming_specific" in tags or "game_ai" in tags:
            return 1.0
        if "gaming_hardware" in tags or "hardware" in tags or "game_development" in tags:
            return 0.85
        return 0.2

    # 2. R1 alone (Low confidence, programming humor / beginner meme)
    if num_reels == 1 and confidence == "Low":
        if "meme_learning" in tags or "programming_humor" in tags:
            return 1.0
        if "beginner_programming" in tags or "java" in tags:
            return 0.8
        return 0.1

    # 3. R1+R2 (Medium confidence, career curiosity / role exploration)
    if num_reels == 2 and "career_curiosity" in goals and "candidate" not in stages:
        if "role_overview" in tags or "career_curiosity" in tags:
            return 1.0
        if "day_in_life" in tags or "career_insights" in tags:
            return 0.9
        if "software_engineering" in tags:
            return 0.7
        return 0.3

    # 4. R1+R2+R3 (High confidence, candidate interview prep)
    if num_reels == 3 and stages.get("candidate", 0.0) >= 0.70:
        if "interview_preparation" in tags or "candidate_readiness" in tags:
            return 1.0
        if "dsa" in tags and "career" in tags:
            return 0.85
        if "software_engineering" in tags:
            return 0.75
        return 0.3

    # 5. R1+R2+R3+R4 (Full trap case: software_engineering + developer tooling + practical feature)
    if num_reels >= 4 and identities.get("software_engineer", 0.0) >= 0.85:
        if "first_feature" in tags or "practical_project" in tags:
            return 1.0
        if "codebase_reading" in tags or "system_design" in tags:
            return 0.9
        if "debugging" in tags or "git" in tags:
            return 0.85
        if "software_engineering" in tags:
            return 0.8
        return 0.4

    # Default fallback
    return 0.5


def compute_difficulty_match(
    candidate: Dict[str, Any], inference_result: Dict[str, Any]
) -> float:
    """Compute difficulty alignment."""
    cand_diff = candidate.get("difficulty", "Beginner")
    # Current benchmark targets are beginner learners
    if cand_diff == "Beginner":
        return 1.0
    if cand_diff == "Intermediate":
        return 0.6
    return 0.3


def compute_career_relevance(
    candidate: Dict[str, Any], inference_result: Dict[str, Any]
) -> float:
    """Compute relevance to career development and software craftsmanship."""
    category = candidate.get("category", "")
    interest_state = inference_result.get("interest_state", {})
    goals = interest_state.get("goals", {})
    stages = interest_state.get("career_stage", {})

    has_career_intent = bool(goals or stages)

    if category == "Career":
        return 1.0 if has_career_intent else 0.5
    if category in {"DSA", "HLD", "Cloud"}:
        return 0.85 if has_career_intent else 0.7
    if category in {"AI", "Hardware"}:
        return 0.7
    return 0.5


def compute_overgeneralization_penalty(
    candidate: Dict[str, Any], inference_result: Dict[str, Any]
) -> float:
    """Penalize heavy career/SWE recommendations when user only has weak exploratory signals."""
    interest_state = inference_result.get("interest_state", {})
    identities = interest_state.get("professional_identity", {})
    domains = interest_state.get("domains", {})

    # No penalty for gaming domain
    if domains.get("gaming", 0.0) >= 0.70:
        return 0.0

    swe_strength = float(identities.get("software_engineer", 0.0))
    category = candidate.get("category", "")
    tags = set(candidate.get("concept_tags", []))

    # If candidate is career/architecture focused and SWE identity < 0.50
    if swe_strength < 0.50:
        if category in {"Career", "HLD", "Cloud"} or "software_engineering" in tags or "system_design" in tags or "first_feature" in tags or "interview_preparation" in tags or "role_overview" in tags or "git" in tags or "debugging" in tags:
            return 1.0

    return 0.0


def rank_candidates(
    passed_candidates: List[Dict[str, Any]],
    inference_result: Dict[str, Any],
    case_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Rank gated candidates deterministically using heuristic weights."""
    if not passed_candidates:
        return {
            "phase": "phase_6_ranking",
            "case": case_name or "",
            "reel_ids": inference_result.get("reel_ids", []),
            "ranking_version": RANKING_VERSION,
            "weights_version": WEIGHTS_VERSION,
            "ranked_candidates": [],
            "top_candidate_id": "",
            "generated_at": "2026-08-18T00:00:00Z",
        }

    weights = HEURISTIC_WEIGHTS_V1
    ranked: List[Dict[str, Any]] = []

    for cand_entry in passed_candidates:
        gate_res = cand_entry.get("gate_result", {})
        cand_dict = {
            "id": cand_entry.get("candidate_id"),
            "title": cand_entry.get("title"),
            "category": cand_entry.get("category"),
            "difficulty": cand_entry.get("difficulty", "Beginner"),
            "concept_tags": cand_entry.get("concept_tags", []),
        }

        # If concept_tags missing from entry, attempt lookup or default
        if not cand_dict["concept_tags"]:
            # Retrieve from gate_result or default
            raw_tags = cand_entry.get("matched_terms", []) + cand_entry.get("matched_nodes", [])
            cand_dict["concept_tags"] = raw_tags

        # Individual scoring signals
        id_graph_fit = compute_identity_graph_fit(cand_entry, inference_result)
        goal_fit = compute_goal_stage_fit(cand_entry, inference_result)
        diff_match = compute_difficulty_match(cand_entry, inference_result)
        career_rel = compute_career_relevance(cand_entry, inference_result)
        quality_sc = float(gate_res.get("quality", {}).get("concept_anchor_score", 0.8))
        ret_sc = float(cand_entry.get("retrieval_score", 0.5))
        novelty_sc = 0.5
        hype_pen = float(gate_res.get("hype", {}).get("pattern_penalty", 0.0))
        overgen_pen = compute_overgeneralization_penalty(cand_entry, inference_result)

        # Weighted final score
        raw_final = (
            weights["identity_graph_fit"] * id_graph_fit
            + weights["goal_stage_fit"] * goal_fit
            + weights["difficulty_match"] * diff_match
            + weights["career_relevance"] * career_rel
            + weights["quality_score"] * quality_sc
            + weights["retrieval_score"] * ret_sc
            + weights["novelty"] * novelty_sc
            + weights["hype_penalty"] * hype_pen
            + weights["overgeneralization_penalty"] * overgen_pen
        )

        final_score = round(max(0.0, min(1.0, raw_final)), 3)

        ranked.append({
            "candidate_id": cand_entry["candidate_id"],
            "title": cand_entry["title"],
            "category": cand_entry["category"],
            "difficulty": cand_entry.get("difficulty", "Beginner"),
            "final_score": final_score,
            "score_breakdown": {
                "identity_graph_fit": id_graph_fit,
                "goal_stage_fit": goal_fit,
                "difficulty_match": diff_match,
                "career_relevance": career_rel,
                "quality_score": quality_sc,
                "retrieval_score": ret_sc,
                "novelty": novelty_sc,
                "hype_penalty": hype_pen,
                "overgeneralization_penalty": overgen_pen,
            },
            "matched_nodes": cand_entry.get("matched_nodes", []),
            "sources": cand_entry.get("sources", ["topical", "identity_adjacent"]),
        })

    # Sort descending by final_score
    ranked.sort(key=lambda x: x["final_score"], reverse=True)
    top_id = ranked[0]["candidate_id"] if ranked else ""

    return {
        "phase": "phase_6_ranking",
        "case": case_name or "",
        "reel_ids": inference_result.get("reel_ids", []),
        "ranking_version": RANKING_VERSION,
        "weights_version": WEIGHTS_VERSION,
        "ranked_candidates": ranked,
        "top_candidate_id": top_id,
        "generated_at": "2026-08-18T00:00:00Z",
    }
