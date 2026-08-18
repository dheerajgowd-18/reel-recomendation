"""Deterministic interest inference and graph traversal coordinator for ScrollSense Phase 3."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import CASE_MAPPING, CHECKPOINT_MAPPING, OUTPUT_DIR
from src.graph import traverse_identity_graph
from src.persona import aggregate_interest_state
from src.signals import generate_signals


def determine_confidence(
    reel_ids: List[str], interest_state: Dict[str, Any]
) -> str:
    """Determine confidence level deterministically based on evidence depth and agreement."""
    num_reels = len(reel_ids)
    identities = interest_state.get("professional_identity", {})
    stages = interest_state.get("career_stage", {})
    goals = interest_state.get("goals", {})

    has_strong_swe = identities.get("software_engineer", 0.0) >= 0.70
    has_strong_candidate = stages.get("candidate", 0.0) >= 0.70
    has_strong_prep = goals.get("career_prep", 0.0) >= 0.70 or goals.get("career_curiosity", 0.0) >= 0.70

    if num_reels >= 3 and has_strong_swe and (has_strong_candidate or has_strong_prep):
        return "High"

    if num_reels >= 2:
        return "Medium"

    return "Low"


def generate_inferred_interest_label(
    interest_state: Dict[str, Any], confidence: str
) -> str:
    """Generate human-readable explainable interest label deterministically from state."""
    domains = interest_state.get("domains", {})
    stages = interest_state.get("career_stage", {})
    goals = interest_state.get("goals", {})

    # Check for gaming-specific domain
    if domains.get("gaming", 0.0) >= 0.70:
        return "Gaming systems, game AI, and gaming hardware curiosity"

    # Single meme / low evidence
    if confidence == "Low":
        return "Programming humor and early technology curiosity"

    # Multi-reel early software engineering interest
    if confidence == "Medium":
        if "lifestyle" in interest_state.get("content_preference", {}):
            return "Software technology curiosity and developer lifestyle interest"
        return "Software engineering curiosity and foundational technology interest"

    # High confidence SWE + career preparation
    if confidence == "High":
        if stages.get("candidate", 0.0) >= 0.70 or goals.get("career_prep", 0.0) >= 0.70:
            return "Software engineering culture and early career preparation"
        return "Software engineering practices and advanced system design"

    return "General technology and programming exploration"


def infer_interests(
    reel_ids: List[str], case_name: Optional[str] = None
) -> Dict[str, Any]:
    """Execute complete Phase 3 inference pipeline for given reel IDs."""
    if not reel_ids:
        raise ValueError("Reel IDs list cannot be empty.")

    if case_name:
        valid_cases = set(CASE_MAPPING.keys()).union(set(CHECKPOINT_MAPPING.values()))
        if case_name not in valid_cases:
            raise ValueError(
                f"Unknown case name '{case_name}'. Supported cases: {sorted(valid_cases)}"
            )

    # 1. Load or extract signals
    signals_map = generate_signals(reel_ids=reel_ids)
    ordered_signals = [signals_map[r_id] for r_id in reel_ids]

    # 2. Aggregate into InterestState
    interest_state = aggregate_interest_state(signals=ordered_signals)

    # 3. Traverse Identity/Skill Graph
    graph_traversal = traverse_identity_graph(interest_state=interest_state)

    # 4. Extract top dimensions
    sorted_identities = sorted(
        interest_state.get("professional_identity", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    )
    top_identity = sorted_identities[0][0] if sorted_identities else ""

    sorted_domains = sorted(
        interest_state.get("domains", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    )
    top_domains = [d[0] for d in sorted_domains[:3]]

    sorted_goals = sorted(
        interest_state.get("goals", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    )
    top_goals = [g[0] for g in sorted_goals[:3]]

    sorted_stages = sorted(
        interest_state.get("career_stage", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    )
    top_stage = sorted_stages[0][0] if sorted_stages else ""

    # 5. Determine confidence & label
    confidence = determine_confidence(reel_ids, interest_state)
    inferred_label = generate_inferred_interest_label(interest_state, confidence)

    # 6. Build InferenceResult
    return {
        "phase": "phase_3_inference",
        "case": case_name or "",
        "reel_ids": reel_ids,
        "interest_state": interest_state,
        "top_professional_identity": top_identity,
        "top_domains": top_domains,
        "top_goals": top_goals,
        "top_career_stage": top_stage,
        "inferred_interest_label": inferred_label,
        "confidence": confidence,
        "graph_traversal": graph_traversal,
        "evidence_reel_ids": reel_ids,
        "generated_at": "2026-08-18T00:00:00Z",
    }


def run_all_checkpoints() -> Dict[str, Any]:
    """Run inference across all defined cumulative benchmarks and return dictionary."""
    checkpoint_suites = {
        "trap_after_R1": (["R1"], "trap_after_R1"),
        "trap_after_R1_R2": (["R1", "R2"], "trap_after_R1_R2"),
        "trap_after_R1_R2_R3": (["R1", "R2", "R3"], "trap_after_R1_R2_R3"),
        "trap_after_R1_R2_R3_R4": (["R1", "R2", "R3", "R4"], "trap_java_to_swe"),
        "non_trap_gaming_only": (["R5", "R6", "R7"], "non_trap_gaming_only"),
    }
    all_results: Dict[str, Any] = {}
    for key, (reels, c_name) in checkpoint_suites.items():
        all_results[key] = infer_interests(reels, case_name=c_name)
    return all_results


def main() -> None:
    parser = argparse.ArgumentParser(description="ScrollSense Phase 3 Inference Engine")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reels", type=str, help="Comma-separated watched reel IDs (e.g. R1,R2,R3,R4)")
    group.add_argument("--case", type=str, help="Named test case (e.g. trap_java_to_swe, non_trap_gaming_only)")
    group.add_argument("--all-checkpoints", action="store_true", help="Execute inference across all standard checkpoints")
    parser.add_argument(
        "--out",
        type=str,
        default=str(OUTPUT_DIR / "inference.json"),
        help="Path to write the inference result JSON.",
    )

    args = parser.parse_args()
    out_file = Path(args.out)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if args.all_checkpoints:
            results = run_all_checkpoints()
            print(json.dumps(results, indent=2))
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        elif args.case:
            if args.case == "trap_java_to_swe":
                reels = ["R1", "R2", "R3", "R4"]
            elif args.case == "non_trap_gaming_only":
                reels = ["R5", "R6", "R7"]
            else:
                raise ValueError(
                    f"Unknown case name '{args.case}'. Supported cases: {sorted(CASE_MAPPING.keys())}"
                )
            result = infer_interests(reels, case_name=args.case)
            print(json.dumps(result, indent=2))
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        elif args.reels:
            reels = [r.strip() for r in args.reels.split(",") if r.strip()]
            result = infer_interests(reels)
            print(json.dumps(result, indent=2))
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
