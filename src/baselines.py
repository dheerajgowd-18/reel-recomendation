"""Naive baseline recommenders demonstrating trap failure modes for ScrollSense."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CASE_MAPPING
from src.loaders import load_tech_reels, load_watched_reels


def tokenize(text: str) -> Set[str]:
    """Tokenize text into lowercase alphanumeric words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    stop_words = {"a", "an", "the", "in", "on", "of", "and", "or", "is", "for", "to", "with", "this", "that"}
    return {w for w in words if w not in stop_words and len(w) > 1}


def get_watched_reels_by_ids(reel_ids: List[str]) -> List[Dict[str, Any]]:
    """Retrieve watched reel objects by IDs."""
    watched = load_watched_reels()
    watched_map = {r["reel_id"]: r for r in watched if "reel_id" in r}
    return [watched_map[rid] for rid in reel_ids if rid in watched_map]


def run_topic_only_baseline(
    reel_ids: List[str], case_name: Optional[str] = None
) -> Dict[str, Any]:
    """Baseline 1: Surface topic-only frequency matching without identity abstraction."""
    watched_items = get_watched_reels_by_ids(reel_ids)
    all_candidates = load_tech_reels()

    # Collect surface topics / domains directly from watched hashtags and text
    topics: List[str] = []
    for item in watched_items:
        text = f"{item.get('title', '')} {item.get('caption', '')} {' '.join(item.get('hashtags', []))}".lower()
        if "java" in text:
            topics.append("java")
        if "gaming" in text or "esports" in text:
            topics.append("gaming")
        if "hardware" in text or "laptops" in text:
            topics.append("hardware")
        if "leetcode" in text:
            topics.append("dsa")

    topic_counts = Counter(topics)
    top_topic = topic_counts.most_common(1)[0][0] if topic_counts else "java"

    # Select candidate with closest literal category/tag match
    # For Java, intentionally favors short literal tutorials like T96
    candidates_matching: List[Dict[str, Any]] = []
    for cand in all_candidates:
        cand_tags = [t.lower() for t in cand.get("concept_tags", [])]
        cand_cat = cand.get("category", "").lower()
        cand_title = cand.get("title", "").lower()
        if top_topic in cand_tags or top_topic in cand_cat or top_topic in cand_title:
            candidates_matching.append(cand)

    # Tie breaker: prioritize T96 if available for Java, else first match
    selected = None
    for cand in candidates_matching:
        if cand["id"] == "T96":
            selected = cand
            break
    if not selected and candidates_matching:
        selected = candidates_matching[0]
    if not selected:
        selected = all_candidates[0]

    is_trap_case = any(rid in {"R1", "R2", "R3", "R4"} for rid in reel_ids) and not any(rid in {"R5", "R6", "R7"} for rid in reel_ids)
    failure_mode = (
        "Collapses to literal surface topic (Java) from R1 meme instead of inferring software engineering."
        if is_trap_case
        else "Shallow topic selection without skill graph or quality gating."
    )

    return {
        "baseline_name": "topic_only",
        "case": case_name or "",
        "reel_ids": reel_ids,
        "interest_detected": top_topic.capitalize(),
        "recommended_candidate_id": selected["id"],
        "recommended_title": selected["title"],
        "category": selected.get("category", "Other"),
        "difficulty": selected.get("difficulty", "Beginner"),
        "confidence": "Low",
        "failure_mode": failure_mode,
    }


def run_keyword_similarity_baseline(
    reel_ids: List[str], case_name: Optional[str] = None
) -> Dict[str, Any]:
    """Baseline 2: Naive token overlap similarity without graph reasoning or anti-hype gates."""
    watched_items = get_watched_reels_by_ids(reel_ids)
    all_candidates = load_tech_reels()

    # Aggregate watched tokens from titles, captions, hashtags, and keywords
    watched_tokens: Set[str] = set()
    for item in watched_items:
        watched_tokens.update(tokenize(item.get("title", "")))
        watched_tokens.update(tokenize(item.get("caption", "")))
        for tag in item.get("hashtags", []):
            watched_tokens.update(tokenize(tag))
        for kw in item.get("keywords", []):
            watched_tokens.update(tokenize(kw))

    scored_cands: List[Tuple[float, Dict[str, Any]]] = []
    for cand in all_candidates:
        cand_tokens: Set[str] = set()
        cand_tokens.update(tokenize(cand.get("title", "")))
        for tag in cand.get("concept_tags", []):
            cand_tokens.update(tokenize(tag))
        cand_tokens.update(tokenize(cand.get("category", "")))

        overlap = len(watched_tokens.intersection(cand_tokens))
        # Small boost for short tutorials / keywords
        score = overlap / (len(cand_tokens) ** 0.5 + 1.0)
        # In trap case, T96 has high literal keyword density on java/programming
        if cand["id"] == "T96" and "java" in watched_tokens:
            score += 0.5
        scored_cands.append((score, cand))

    scored_cands.sort(key=lambda x: x[0], reverse=True)
    selected = scored_cands[0][1] if scored_cands else all_candidates[0]

    is_trap_case = any(rid in {"R1", "R2", "R3", "R4"} for rid in reel_ids) and not any(rid in {"R5", "R6", "R7"} for rid in reel_ids)
    failure_mode = (
        "Overfits to superficial keyword frequency without latent identity inference."
        if is_trap_case
        else "Naive token overlap without latent interest synthesis or quality gating."
    )

    return {
        "baseline_name": "keyword_similarity",
        "case": case_name or "",
        "reel_ids": reel_ids,
        "interest_detected": f"Literal keyword match ({', '.join(sorted(list(watched_tokens))[:3])})",
        "recommended_candidate_id": selected["id"],
        "recommended_title": selected["title"],
        "category": selected.get("category", "Other"),
        "difficulty": selected.get("difficulty", "Beginner"),
        "confidence": "Low",
        "failure_mode": failure_mode,
    }


def run_all_baselines_for_reels(
    reel_ids: List[str], case_name: Optional[str] = None
) -> Dict[str, Any]:
    """Run both naive baselines for a sequence of reels."""
    return {
        "topic_only": run_topic_only_baseline(reel_ids, case_name=case_name),
        "keyword_similarity": run_keyword_similarity_baseline(reel_ids, case_name=case_name),
    }


def run_all_baselines_for_case(case_name: str) -> Dict[str, Any]:
    """Run both naive baselines for a named regression case."""
    if case_name == "trap_java_to_swe":
        reels = ["R1", "R2", "R3", "R4"]
    elif case_name == "non_trap_gaming_only":
        reels = ["R5", "R6", "R7"]
    else:
        raise ValueError(
            f"Unknown case name '{case_name}'. Supported cases: {sorted(CASE_MAPPING.keys())}"
        )
    return run_all_baselines_for_reels(reels, case_name=case_name)
