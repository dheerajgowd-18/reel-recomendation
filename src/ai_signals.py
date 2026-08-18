"""NVIDIA Nemotron-assisted AI signal extraction layer with validation and offline fallback."""

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

from src.ai_cache import PROMPT_VERSION_SIGNAL, make_cache_key, validate_ai_signal
from src.config import (
    LLM_CACHE_DIR,
    LLM_MODEL,
    LLM_MODE,
    LLM_PROVIDER,
    LLM_SIGNALS_CACHE_PATH,
)
from src.llm_client import LLMClient
from src.signals import extract_signal


def load_cached_llm_signals() -> Dict[str, Any]:
    """Load cached LLM signals if available."""
    if not LLM_SIGNALS_CACHE_PATH.is_file():
        return {}
    try:
        with open(LLM_SIGNALS_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def extract_signal_hybrid(
    reel: Dict[str, Any],
    extractor_mode: str = "hybrid",
    model: str = LLM_MODEL,
    llm_client: Optional[LLMClient] = None,
) -> Tuple[Dict[str, Any], bool, str]:
    """Extract signal using hybrid AI layer (Cache -> Live LLM -> Deterministic fallback).

    Returns: (signal_dict, fallback_used, status_str)
    """
    reel_id = reel.get("reel_id", "")
    if extractor_mode == "deterministic":
        return extract_signal(reel), False, "deterministic"

    cache_key = make_cache_key(model, PROMPT_VERSION_SIGNAL, reel_id)
    cached_signals = load_cached_llm_signals()

    # 1. Check cache first
    if cache_key in cached_signals:
        candidate_sig = cached_signals[cache_key]
        is_valid, _ = validate_ai_signal(candidate_sig, reel_id)
        if is_valid:
            return candidate_sig, False, "cached"

    # 2. If in live mode, attempt live Nemotron API call
    current_mode = os.getenv("LLM_MODE", LLM_MODE)
    current_provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER)
    if extractor_mode in ("ai", "hybrid") and current_mode == "live" and current_provider == "openai_compatible":
        client = llm_client or LLMClient()
        prompt_path = PROJECT_ROOT / "prompts" / "nemotron_signal_extraction.md"
        sys_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else "Extract signals into strict JSON."

        user_content = f"Analyze watched Reel:\nTitle: {reel.get('title')}\nCaption: {reel.get('caption')}\nHashtags: {reel.get('hashtags')}\nContent Type: {reel.get('content_type')}"
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content},
        ]

        live_res, is_fb = client.complete_json(messages)
        if not is_fb and live_res:
            # Inject required schema fields if LLM returned partial dict
            det_sig = extract_signal(reel)
            merged = dict(det_sig)
            if "interest_evidence" in live_res:
                merged["interest_evidence"] = live_res["interest_evidence"]

            is_valid, _ = validate_ai_signal(merged, reel_id)
            if is_valid:
                # Save to cache
                cached_signals[cache_key] = merged
                LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                try:
                    with open(LLM_SIGNALS_CACHE_PATH, "w", encoding="utf-8") as f:
                        json.dump(cached_signals, f, indent=2)
                except Exception:
                    pass
                return merged, False, "live"

    # 3. Fallback to deterministic signal extraction
    return extract_signal(reel), True, "fallback"
