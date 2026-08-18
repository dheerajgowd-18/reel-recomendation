"""Candidate retrieval engine for ScrollSense Phase 4."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CASE_MAPPING, CONCEPT_ALIAS_MAP, OUTPUT_DIR
from src.infer import infer_interests
from src.loaders import load_tech_reels


def map_tag(tag: str) -> str:
    """Map a raw concept tag to standard canonical ontology term using alias map."""
    clean = tag.strip().lower()
    return CONCEPT_ALIAS_MAP.get(clean, clean)


def retrieve_candidates(
    inference_result: Dict[str, Any], candidate_pool: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Retrieve candidate Tech Reels using topical and identity-adjacent graph signals."""
    if candidate_pool is None:
        candidate_pool = load_tech_reels()

    interest_state = inference_result.get("interest_state", {})
    domains = interest_state.get("domains", {})
    goals = interest_state.get("goals", {})
    traversal = inference_result.get("graph_traversal", {})
    activated_nodes = {a["node"]: float(a["activation"]) for a in traversal.get("activated_nodes", [])}
    seed_nodes = {s["node"]: float(s["weight"]) for s in traversal.get("seed_nodes", [])}

    # Combine activated and seed nodes for identity matching
    node_activations: Dict[str, float] = {}
    for k, v in seed_nodes.items():
        node_activations[k] = max(node_activations.get(k, 0.0), v)
    for k, v in activated_nodes.items():
        node_activations[k] = max(node_activations.get(k, 0.0), v)

    topical_matches: List[Dict[str, Any]] = []
    identity_matches: List[Dict[str, Any]] = []
    combined_candidates: List[Dict[str, Any]] = []

    for cand in candidate_pool:
        cand_id = cand["id"]
        title = cand["title"]
        category = cand["category"]
        difficulty = cand["difficulty"]
        raw_tags = cand.get("concept_tags", [])
        canonical_tags = [map_tag(t) for t in raw_tags]
        tag_set = set(canonical_tags)

        # 1. Source A: Topical matching
        matched_terms: List[str] = []
        topical_accum = 0.0
        for t in tag_set:
            if t in domains:
                topical_accum += float(domains[t])
                matched_terms.append(t)
            elif t in goals:
                topical_accum += float(goals[t]) * 0.8
                matched_terms.append(t)

        # Compute normalized topical score
        topical_score = 0.0
        if matched_terms:
            # Base match + small bonus for multiple matched terms
            topical_score = min(1.0, (topical_accum / (len(matched_terms) ** 0.5)) * 0.7 + 0.1 * len(matched_terms))
            topical_score = round(topical_score, 3)
            topical_matches.append({
                "candidate_id": cand_id,
                "title": title,
                "category": category,
                "score": topical_score,
                "matched_terms": sorted(matched_terms),
            })

        # 2. Source B: Identity-adjacent graph matching
        matched_nodes: List[str] = []
        identity_accum = 0.0
        for t in tag_set:
            if t in node_activations:
                act = node_activations[t]
                identity_accum += act
                matched_nodes.append(t)

        identity_score = 0.0
        if matched_nodes:
            identity_score = min(1.0, (identity_accum / (len(matched_nodes) ** 0.5)) * 0.75 + 0.1 * len(matched_nodes))
            identity_score = round(identity_score, 3)
            identity_matches.append({
                "candidate_id": cand_id,
                "title": title,
                "category": category,
                "score": identity_score,
                "matched_nodes": sorted(matched_nodes),
            })

        # 3. Combined retrieval score
        if topical_score > 0.0 or identity_score > 0.0:
            retrieval_score = round(min(1.0, 0.45 * topical_score + 0.55 * identity_score), 3)
            sources_list: List[str] = []
            if topical_score > 0.0:
                sources_list.append("topical")
            if identity_score > 0.0:
                sources_list.append("identity_adjacent")

            combined_candidates.append({
                "candidate_id": cand_id,
                "title": title,
                "category": category,
                "difficulty": difficulty,
                "concept_tags": raw_tags,
                "retrieval_score": retrieval_score,
                "sources": sources_list,
                "matched_terms": sorted(matched_terms),
                "matched_nodes": sorted(matched_nodes),
            })

    # Sort sources and combined candidates
    topical_matches.sort(key=lambda x: x["score"], reverse=True)
    identity_matches.sort(key=lambda x: x["score"], reverse=True)
    combined_candidates.sort(key=lambda x: x["retrieval_score"], reverse=True)

    # Interest summary
    interest_summary = {
        "top_professional_identity": inference_result.get("top_professional_identity", ""),
        "top_domains": inference_result.get("top_domains", []),
        "top_goals": inference_result.get("top_goals", []),
        "top_career_stage": inference_result.get("top_career_stage", ""),
        "confidence": inference_result.get("confidence", "Low"),
    }

    return {
        "phase": "phase_4_retrieval",
        "case": inference_result.get("case", ""),
        "reel_ids": inference_result.get("reel_ids", []),
        "interest_summary": interest_summary,
        "sources": {
            "topical": topical_matches,
            "identity_adjacent": identity_matches,
        },
        "candidates": combined_candidates,
        "candidate_count": len(combined_candidates),
        "generated_at": "2026-08-18T00:00:00Z",
    }


def run_retrieval_pipeline(
    reel_ids: List[str], case_name: Optional[str] = None
) -> Dict[str, Any]:
    """Coordinate inference and candidate retrieval."""
    inf_res = infer_interests(reel_ids, case_name=case_name)
    return retrieve_candidates(inf_res)


def run_all_checkpoints_retrieval() -> Dict[str, Any]:
    """Run candidate retrieval across all defined cumulative benchmarks."""
    checkpoint_suites = {
        "trap_after_R1": (["R1"], "trap_after_R1"),
        "trap_after_R1_R2": (["R1", "R2"], "trap_after_R1_R2"),
        "trap_after_R1_R2_R3": (["R1", "R2", "R3"], "trap_after_R1_R2_R3"),
        "trap_after_R1_R2_R3_R4": (["R1", "R2", "R3", "R4"], "trap_java_to_swe"),
        "non_trap_gaming_only": (["R5", "R6", "R7"], "non_trap_gaming_only"),
    }
    all_results: Dict[str, Any] = {}
    for key, (reels, c_name) in checkpoint_suites.items():
        all_results[key] = run_retrieval_pipeline(reels, case_name=c_name)
    return all_results


def main() -> None:
    parser = argparse.ArgumentParser(description="ScrollSense Phase 4 Candidate Retrieval Engine")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reels", type=str, help="Comma-separated watched reel IDs (e.g. R1,R2,R3,R4)")
    group.add_argument("--case", type=str, help="Named test case (e.g. trap_java_to_swe, non_trap_gaming_only)")
    group.add_argument("--all-checkpoints", action="store_true", help="Execute retrieval across all standard checkpoints")
    parser.add_argument(
        "--out",
        type=str,
        default=str(OUTPUT_DIR / "retrieval.json"),
        help="Path to write the retrieval result JSON.",
    )

    args = parser.parse_args()
    out_file = Path(args.out)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if args.all_checkpoints:
            results = run_all_checkpoints_retrieval()
            print(json.dumps(results, indent=2))
            try:
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
            except Exception:
                pass
        elif args.case:
            if args.case == "trap_java_to_swe":
                reels = ["R1", "R2", "R3", "R4"]
            elif args.case == "non_trap_gaming_only":
                reels = ["R5", "R6", "R7"]
            else:
                raise ValueError(
                    f"Unknown case name '{args.case}'. Supported cases: {sorted(CASE_MAPPING.keys())}"
                )
            result = run_retrieval_pipeline(reels, case_name=args.case)
            print(json.dumps(result, indent=2))
            try:
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
            except Exception:
                pass
        elif args.reels:
            reels = [r.strip() for r in args.reels.split(",") if r.strip()]
            result = run_retrieval_pipeline(reels)
            print(json.dumps(result, indent=2))
            try:
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
            except Exception:
                pass
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
