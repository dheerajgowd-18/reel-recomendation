"""NVIDIA Nemotron-assisted AI explanation module with validation and offline fallback."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ai_cache import PROMPT_VERSION_EXPLANATION, make_cache_key
from src.config import (
    LLM_CACHE_DIR,
    LLM_EXPLANATIONS_CACHE_PATH,
    LLM_MODEL,
    LLM_MODE,
    LLM_PROVIDER,
)
from src.explain import generate_explanations
from src.llm_client import LLMClient


def load_cached_llm_explanations() -> Dict[str, Any]:
    """Load cached LLM explanations if available."""
    if not LLM_EXPLANATIONS_CACHE_PATH.is_file():
        return {}
    try:
        with open(LLM_EXPLANATIONS_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def generate_explanations_hybrid(
    inference_result: Dict[str, Any],
    top_candidate: Dict[str, Any],
    case_name: Optional[str] = None,
    explainer_mode: str = "hybrid",
    model: str = LLM_MODEL,
    llm_client: Optional[LLMClient] = None,
) -> Tuple[Dict[str, str], bool, str]:
    """Generate explainable text using hybrid AI layer (Cache -> Live LLM -> Deterministic fallback).

    Strictly preserves candidate choice, category, difficulty, and confidence.
    Returns: (explanation_dict, fallback_used, status_str)
    """
    if explainer_mode == "deterministic":
        return generate_explanations(inference_result, top_candidate), False, "deterministic"

    reel_ids = inference_result.get("reel_ids", [])
    possible_ids = [
        case_name,
        "_".join(reel_ids),
        "trap_java_to_swe" if set(reel_ids) == {"R1", "R2", "R3", "R4"} else None,
        "trap_after_R1_R2_R3_R4" if set(reel_ids) == {"R1", "R2", "R3", "R4"} else None,
        "non_trap_gaming_only" if set(reel_ids) == {"R5", "R6", "R7"} else None,
    ]
    cached_exps = load_cached_llm_explanations()

    # 1. Check cache first
    for pid in possible_ids:
        if not pid:
            continue
        cache_key = make_cache_key(model, PROMPT_VERSION_EXPLANATION, pid)
        if cache_key in cached_exps:
            c_exp = cached_exps[cache_key]
            if isinstance(c_exp, dict) and "interest_detected" in c_exp and "why" in c_exp:
                return c_exp, False, "cached"

    # 2. Live LLM mode
    current_mode = os.getenv("LLM_MODE", LLM_MODE)
    current_provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER)
    if explainer_mode in ("ai", "hybrid") and current_mode == "live" and current_provider == "openai_compatible":
        client = llm_client or LLMClient()
        prompt_path = PROJECT_ROOT / "prompts" / "nemotron_explanation.md"
        sys_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else "Synthesize explanation into strict JSON."

        cand_title = top_candidate.get("title", "")
        cand_cat = top_candidate.get("category", "")
        user_content = (
            f"Inference: {json.dumps(inference_result.get('interest_state', {}))}\n"
            f"Recommended Reel: '{cand_title}' (Category: {cand_cat})\n"
            f"Reel IDs: {inference_result.get('reel_ids')}"
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content},
        ]

        live_res, is_fb = client.complete_json(messages)
        if not is_fb and live_res:
            int_det = live_res.get("interest_detected")
            why_txt = live_res.get("why")
            why_rec = live_res.get("why_this_recommendation") or live_res.get("why_recommendation")
            if int_det and why_txt and why_rec:
                out_dict = {
                    "interest_detected": str(int_det),
                    "why": str(why_txt),
                    "why_recommendation": str(why_rec),
                }
                # Cache valid explanation
                cached_exps[cache_key] = out_dict
                LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                try:
                    with open(LLM_EXPLANATIONS_CACHE_PATH, "w", encoding="utf-8") as f:
                        json.dump(cached_exps, f, indent=2)
                except Exception:
                    pass
                return out_dict, False, "live"

    # 3. Fallback to deterministic explanation
    return generate_explanations(inference_result, top_candidate), True, "fallback"
