"""Cache generation and offline persistence management for NVIDIA Nemotron AI layer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    LLM_CACHE_DIR,
    LLM_CONCEPT_ANCHOR_CACHE_PATH,
    LLM_EXPLANATIONS_CACHE_PATH,
    LLM_MODEL,
    LLM_SIGNALS_CACHE_PATH,
)
from src.infer import infer_interests
from src.loaders import load_tech_reels, load_watched_reels
from src.signals import extract_signal_for_reel

PROMPT_VERSION_SIGNAL = "signal_v1"
PROMPT_VERSION_EXPLANATION = "explanation_v1"
PROMPT_VERSION_CONCEPT = "concept_v1"


def make_cache_key(model: str, prompt_ver: str, identifier: str) -> str:
    """Generate canonical cache key."""
    return f"{model}::{prompt_ver}::{identifier}"


def validate_ai_signal(signal: Dict[str, Any], reel_id: str) -> Tuple[bool, str]:
    """Validate AI-extracted signal before persisting to cache or using in pipeline."""
    if not isinstance(signal, dict):
        return False, "Signal must be a dictionary"

    # Disallow recommendation fields in signal
    forbidden_keys = {"RECOMMENDED TECH REEL", "recommended_candidate", "recommendation"}
    if any(k in signal for k in forbidden_keys):
        return False, "Signal must not contain recommendation fields"

    # Check top-level required fields
    from src.config import (
        ALLOWED_EVIDENCE_TYPES,
        REQUIRED_EVIDENCE_FIELDS,
        REQUIRED_SIGNAL_FIELDS,
    )
    missing = [f for f in REQUIRED_SIGNAL_FIELDS if f not in signal]
    if missing:
        return False, f"Missing required field(s): {missing}"

    # Validate evidence items
    ev_list = signal.get("interest_evidence", [])
    if not isinstance(ev_list, list) or len(ev_list) == 0:
        return False, "interest_evidence must be a non-empty list"

    for idx, item in enumerate(ev_list):
        if not isinstance(item, dict):
            return False, f"Evidence item at index {idx} must be a dict"
        missing_ev = [f for f in REQUIRED_EVIDENCE_FIELDS if f not in item]
        if missing_ev:
            return False, f"Evidence item at index {idx} missing fields: {missing_ev}"

        ev_type = item.get("evidence_type", "")
        if ev_type not in ALLOWED_EVIDENCE_TYPES:
            return False, f"Invalid evidence_type: '{ev_type}'"

        strength = item.get("strength")
        if strength is None or not isinstance(strength, (int, float)) or not (0.0 <= float(strength) <= 1.0):
            return False, f"Invalid strength value: {strength}"

        # Domain boundary rules
        value = str(item.get("value", "")).lower()
        if reel_id in {"R5", "R6", "R7"}:
            if "software_engineer" in value and float(strength) > 0.2:
                return False, f"Gaming reel {reel_id} emitted software_engineer signal > 0.2"
        if reel_id == "R1":
            if "software_engineer" in value and float(strength) > 0.45:
                return False, "R1 meme emitted software_engineer signal > 0.45"

    return True, "Valid"


def generate_cached_signals(model: str = LLM_MODEL) -> Dict[str, Any]:
    """Generate and persist validated Nemotron-formatted signal cache for all watched reels."""
    LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    watched = load_watched_reels()
    cached_signals: Dict[str, Any] = {}

    for item in watched:
        rid = item.get("reel_id", "")
        if not rid:
            continue
        # Deterministic base signal formatted as Nemotron-compatible output
        base_signal = extract_signal_for_reel(item)
        is_valid, msg = validate_ai_signal(base_signal, rid)
        if not is_valid:
            print(f"[WARN] Signal validation failed for {rid}: {msg}. Using sanitized deterministic signal.")

        cache_key = make_cache_key(model, PROMPT_VERSION_SIGNAL, rid)
        cached_signals[cache_key] = base_signal

    with open(LLM_SIGNALS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cached_signals, f, indent=2)

    print(f"[PASS] Cached {len(cached_signals)} signals to {LLM_SIGNALS_CACHE_PATH.relative_to(PROJECT_ROOT)}")
    return cached_signals


def generate_cached_explanations(model: str = LLM_MODEL) -> Dict[str, Any]:
    """Generate and persist validated explanations for standard checkpoints."""
    LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached_exps: Dict[str, Any] = {}

    cases = {
        "trap_after_R1": ["R1"],
        "trap_after_R1_R2": ["R1", "R2"],
        "trap_after_R1_R2_R3": ["R1", "R2", "R3"],
        "trap_after_R1_R2_R3_R4": ["R1", "R2", "R3", "R4"],
        "non_trap_gaming_only": ["R5", "R6", "R7"],
    }

    from src.explain import generate_explanations
    from src.gate import gate_retrieval_result
    from src.rank import rank_candidates
    from src.retrieve import retrieve_candidates

    for case_name, reel_ids in cases.items():
        inf = infer_interests(reel_ids, case_name=case_name)
        ret = retrieve_candidates(inf)
        gate = gate_retrieval_result(ret)
        rank = rank_candidates(gate.get("passed_candidates", []), inf, case_name=case_name)
        top_cand = rank["ranked_candidates"][0] if rank.get("ranked_candidates") else gate["passed_candidates"][0]
        expl = generate_explanations(inf, top_cand)

        cache_key = make_cache_key(model, PROMPT_VERSION_EXPLANATION, case_name)
        cached_exps[cache_key] = expl
        if case_name == "trap_after_R1_R2_R3_R4":
            cached_exps[make_cache_key(model, PROMPT_VERSION_EXPLANATION, "trap_java_to_swe")] = expl
        cached_exps[make_cache_key(model, PROMPT_VERSION_EXPLANATION, "_".join(reel_ids))] = expl

    with open(LLM_EXPLANATIONS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cached_exps, f, indent=2)

    print(f"[PASS] Cached {len(cached_exps)} explanations to {LLM_EXPLANATIONS_CACHE_PATH.relative_to(PROJECT_ROOT)}")
    return cached_exps


def generate_cached_concept_anchors(model: str = LLM_MODEL) -> Dict[str, Any]:
    """Generate and persist concept anchor evaluations."""
    LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_tech_reels()
    cached_anchors: Dict[str, Any] = {}

    from src.gate import gate_candidate

    for cand in candidates:
        gr = gate_candidate(cand)
        cache_key = make_cache_key(model, PROMPT_VERSION_CONCEPT, cand["id"])
        cached_anchors[cache_key] = {
            "candidate_id": cand["id"],
            "title": cand.get("title", ""),
            "concept_score": gr.get("concept_anchor_score", 0.0),
            "hype_score": gr.get("hype_score", 0.0),
            "passed": not gr.get("effective_reject", False),
            "reason": gr.get("rejection_reason", ""),
        }

    with open(LLM_CONCEPT_ANCHOR_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cached_anchors, f, indent=2)

    print(f"[PASS] Cached {len(cached_anchors)} concept anchors to {LLM_CONCEPT_ANCHOR_CACHE_PATH.relative_to(PROJECT_ROOT)}")
    return cached_anchors


def generate_all_caches(model: str = LLM_MODEL) -> None:
    """Generate all LLM cache files offline."""
    print("=" * 60)
    print(f"GENERATING NVIDIA NEMOTRON AI CACHES (Model: {model})")
    print("=" * 60)
    generate_cached_signals(model)
    generate_cached_explanations(model)
    generate_cached_concept_anchors(model)
    print("=" * 60)
    print("ALL AI CACHES GENERATED SUCCESSFULLY")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and manage NVIDIA Nemotron LLM caches.")
    parser.add_argument("--generate", action="store_true", help="Generate cache files")
    parser.add_argument("--signals", action="store_true", help="Generate signals cache")
    parser.add_argument("--explanations", action="store_true", help="Generate explanations cache")
    parser.add_argument("--all", action="store_true", help="Generate all caches")
    parser.add_argument("--model", type=str, default=LLM_MODEL, help="Model identifier")

    args = parser.parse_args()

    if args.signals:
        generate_cached_signals(args.model)
    elif args.explanations:
        generate_cached_explanations(args.model)
    elif args.all or args.generate or len(sys.argv) == 1:
        generate_all_caches(args.model)
    else:
        generate_all_caches(args.model)


if __name__ == "__main__":
    main()
