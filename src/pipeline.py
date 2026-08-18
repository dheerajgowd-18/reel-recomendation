"""Deterministic pipeline orchestrator for ScrollSense Phase 6."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ai_explainer import generate_explanations_hybrid
from src.config import (
    LLM_MODE,
    LLM_MODEL,
)
from src.formatter import format_output, validate_output_fields
from src.gate import gate_retrieval_result
from src.infer import infer_interests
from src.rank import rank_candidates
from src.retrieve import retrieve_candidates
from src.stub_pipeline import run_stub_pipeline


def run_pipeline_for_reels(
    reel_ids: List[str],
    mode: str = "real",
    case_name: Optional[str] = None,
    extractor: str = "hybrid",
    explainer: str = "hybrid",
) -> Tuple[str, Dict[str, Any]]:
    """Execute ScrollSense recommendation pipeline for a sequence of watched reels."""
    if not reel_ids:
        raise ValueError("Reel IDs list cannot be empty.")

    if mode == "stub":
        formatted_txt, trace_dict = run_stub_pipeline(
            reels=reel_ids if not case_name else None, case=case_name
        )
        trace_dict["mode"] = "stub"
        trace_dict["fallback_used"] = False
        return formatted_txt, trace_dict

    # Real pipeline execution
    try:
        # 1. Infer interests & graph traversal
        inf_res = infer_interests(reel_ids, case_name=case_name)

        # 2. Retrieve candidates
        ret_res = retrieve_candidates(inf_res)

        # 3. Gate candidates
        gate_res = gate_retrieval_result(ret_res)
        passed_cands = gate_res.get("passed_candidates", [])

        if not passed_cands:
            raise RuntimeError("All candidates rejected by safety/quality gate. Fallback required.")

        # 4. Rank candidates
        rank_res = rank_candidates(passed_cands, inf_res, case_name=case_name)
        ranked_cands = rank_res.get("ranked_candidates", [])
        top_cand = ranked_cands[0] if ranked_cands else passed_cands[0]

        # 5. Generate explanations (via safe AI layer with deterministic fallback)
        explanations, expl_fallback, expl_status = generate_explanations_hybrid(
            inf_res, top_cand, case_name=case_name, explainer_mode=explainer
        )

        # 6. Format exact output fields
        current_reel_label = (
            reel_ids[0] if len(reel_ids) == 1 else f"session: {', '.join(reel_ids)}"
        )
        out_fields = {
            "CURRENT REEL": current_reel_label,
            "INTEREST DETECTED": explanations["interest_detected"],
            "WHY": explanations["why"],
            "RECOMMENDED TECH REEL": top_cand["title"],
            "CATEGORY": top_cand["category"],
            "WHY THIS RECOMMENDATION": explanations["why_recommendation"],
            "DIFFICULTY": top_cand["difficulty"],
            "CONFIDENCE": inf_res["confidence"],
        }

        validate_output_fields(out_fields)
        formatted_txt = format_output(out_fields)

        # 7. Build pipeline trace
        pipeline_trace = {
            "phase": "phase_6_pipeline",
            "mode": "real",
            "case": case_name or "",
            "reel_ids": reel_ids,
            "inference_summary": {
                "top_professional_identity": inf_res.get("top_professional_identity", ""),
                "top_domains": inf_res.get("top_domains", []),
                "top_goals": inf_res.get("top_goals", []),
                "confidence": inf_res.get("confidence", "Low"),
            },
            "retrieval_summary": {
                "retrieved_count": ret_res.get("candidate_count", 0),
                "top_retrieved": [c["candidate_id"] for c in ret_res.get("candidates", [])[:5]],
            },
            "gate_summary": {
                "passed_count": gate_res.get("passed_count", 0),
                "rejected_count": gate_res.get("rejected_count", 0),
                "rejected_ids": [c["candidate_id"] for c in gate_res.get("rejected_candidates", [])],
            },
            "ranking_summary": {
                "top_candidate_id": rank_res.get("top_candidate_id", ""),
                "top_candidate_title": top_cand.get("title", ""),
                "final_score": top_cand.get("final_score", 0.0),
                "score_breakdown": top_cand.get("score_breakdown", {}),
            },
            "explanation_summary": {
                "interest_label": explanations["interest_detected"],
                "why_source": "signal_evidence",
                "why_recommendation_source": "candidate_match",
            },
            "ai": {
                "model": LLM_MODEL,
                "extractor": extractor,
                "explainer": explainer,
                "llm_mode": os.getenv("LLM_MODE", LLM_MODE),
                "llm_status": expl_status,
                "fallback_used": expl_fallback,
            },
            "fallback_used": expl_fallback,
            "generated_at": "2026-08-18T00:00:00Z",
        }

        return formatted_txt, pipeline_trace

    except Exception as exc:
        if mode == "auto":
            # Fallback to stub mode in auto mode
            formatted_txt, trace_dict = run_stub_pipeline(
                reels=reel_ids if not case_name else None, case=case_name
            )
            trace_dict["mode"] = "auto"
            trace_dict["fallback_used"] = True
            trace_dict["fallback_reason"] = str(exc)
            return formatted_txt, trace_dict
        raise exc


def run_pipeline_for_case(
    case_name: str,
    mode: str = "real",
    extractor: str = "hybrid",
    explainer: str = "hybrid",
) -> Tuple[str, Dict[str, Any]]:
    """Execute pipeline for a named regression case or checkpoint."""
    all_cases = {
        "trap_java_to_swe": ["R1", "R2", "R3", "R4"],
        "non_trap_gaming_only": ["R5", "R6", "R7"],
        "trap_after_R1": ["R1"],
        "trap_after_R1_R2": ["R1", "R2"],
        "trap_after_R1_R2_R3": ["R1", "R2", "R3"],
        "trap_after_R1_R2_R3_R4": ["R1", "R2", "R3", "R4"],
    }
    if case_name in all_cases:
        reels = all_cases[case_name]
    else:
        raise ValueError(
            f"Unknown case name '{case_name}'. Supported cases: {sorted(all_cases.keys())}"
        )
    return run_pipeline_for_reels(
        reels, mode=mode, case_name=case_name, extractor=extractor, explainer=explainer
    )


def run_all_checkpoint_pipelines(
    mode: str = "real",
    extractor: str = "hybrid",
    explainer: str = "hybrid",
) -> Dict[str, Any]:
    """Run pipeline across all defined standard benchmarks."""
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
            "non_trap_gaming_only" if key == "non_trap_gaming_only" else None
        )
        out_txt, trace = run_pipeline_for_reels(
            reels, mode=mode, case_name=c_name, extractor=extractor, explainer=explainer
        )
        all_results[key] = {
            "output_text": out_txt,
            "trace": trace,
        }
    return all_results
