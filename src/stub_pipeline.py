"""Deterministic end-to-end stub pipeline for ScrollSense Phase 1."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.config import (
    CASE_MAPPING,
    CHECKPOINT_MAPPING,
    DEFAULT_RESULT_PATH,
    DEFAULT_TRACE_PATH,
)
from src.formatter import format_recommendation_block, validate_recommendation
from src.loaders import load_expected_outputs, load_watched_reels


def normalize_input(
    reels_input: Optional[Union[str, List[str]]] = None
) -> Tuple[List[str], str]:
    """Normalize input reels to a list of validated reel IDs and canonical join key."""
    if reels_input is None:
        return [], ""

    if isinstance(reels_input, str):
        raw_ids = [r.strip() for r in reels_input.split(",") if r.strip()]
    elif isinstance(reels_input, list):
        raw_ids = [str(r).strip() for r in reels_input if str(r).strip()]
    else:
        raise ValueError(f"Invalid reels input type: {type(reels_input).__name__}")

    if not raw_ids:
        raise ValueError("Reels input cannot be empty.")

    # Validate against known watched reels
    watched_data = load_watched_reels()
    valid_ids = {r["reel_id"] for r in watched_data if "reel_id" in r}
    unknown = [r for r in raw_ids if r not in valid_ids]
    if unknown:
        raise ValueError(f"Unknown reel ID(s): {unknown}. Valid IDs: {sorted(valid_ids)}")

    join_key = ",".join(raw_ids)
    return raw_ids, join_key


def resolve_expected_key(
    reel_ids: Optional[List[str]] = None,
    join_key: Optional[str] = None,
    case_name: Optional[str] = None,
) -> str:
    """Resolve expected checkpoint key from reel sequence or case name."""
    if case_name:
        if case_name not in CASE_MAPPING:
            raise ValueError(
                f"Unknown case name '{case_name}'. Supported cases: {sorted(CASE_MAPPING.keys())}"
            )
        return CASE_MAPPING[case_name]

    if join_key:
        if join_key not in CHECKPOINT_MAPPING:
            raise ValueError(
                f"No deterministic stub checkpoint mapped for reel sequence '{join_key}'. "
                f"Supported sequences: {sorted(CHECKPOINT_MAPPING.keys())}"
            )
        return CHECKPOINT_MAPPING[join_key]

    raise ValueError("Either reels sequence or case name must be provided.")


def infer_interest_stub(expected_entry: Dict[str, str]) -> Dict[str, str]:
    """Stub representation of the interest detection stage."""
    return {
        "interest_detected": expected_entry["INTEREST DETECTED"],
        "why": expected_entry["WHY"],
    }


def recommend_stub(expected_entry: Dict[str, str]) -> Dict[str, str]:
    """Stub representation of candidate retrieval and ranking stage."""
    return dict(expected_entry)


def build_trace(
    input_reels: List[str],
    case_name: Optional[str],
    mapped_key: str,
    recommendation: Dict[str, str],
    formatted_block: str,
    output_file: str,
    trace_file: str,
) -> Dict[str, Any]:
    """Construct structured JSON execution trace for Phase 1 stub."""
    return {
        "phase": "phase_1_stub",
        "mode": "deterministic_stub",
        "input_reels": input_reels,
        "case": case_name or "",
        "mapped_expected_key": mapped_key,
        "stages": {
            "normalize_input": {
                "input_reels": input_reels,
                "status": "completed",
            },
            "resolve_expected_key": {
                "mapped_key": mapped_key,
                "status": "completed",
            },
            "interest_stub": {
                "interest_detected": recommendation["INTEREST DETECTED"],
                "why": recommendation["WHY"],
                "status": "completed",
            },
            "recommend_stub": {
                "recommended_reel": recommendation["RECOMMENDED TECH REEL"],
                "category": recommendation["CATEGORY"],
                "confidence": recommendation["CONFIDENCE"],
                "difficulty": recommendation["DIFFICULTY"],
                "status": "completed",
            },
            "formatter": {
                "lines_count": len(formatted_block.splitlines()),
                "status": "completed",
            },
        },
        "output_file": output_file,
        "trace_file": trace_file,
    }


def run_stub_pipeline(
    reels: Optional[Union[str, List[str]]] = None,
    case: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    trace_path: Optional[Union[str, Path]] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Execute end-to-end stub pipeline run."""
    if reels and case:
        raise ValueError("Cannot specify both --reels and --case. Choose one.")

    if not reels and not case:
        raise ValueError("Must specify either --reels or --case.")

    out_file = Path(out_path) if out_path else DEFAULT_RESULT_PATH
    tr_file = Path(trace_path) if trace_path else DEFAULT_TRACE_PATH

    input_reels: List[str] = []
    join_key: str = ""

    if reels:
        input_reels, join_key = normalize_input(reels)
    elif case:
        if case == "trap_java_to_swe":
            input_reels = ["R1", "R2", "R3", "R4"]
        elif case == "non_trap_gaming_only":
            input_reels = ["R5", "R6", "R7"]

    mapped_key = resolve_expected_key(
        reel_ids=input_reels,
        join_key=join_key,
        case_name=case,
    )

    expected_outputs = load_expected_outputs()
    if mapped_key not in expected_outputs:
        raise KeyError(f"Expected output key '{mapped_key}' not found in expected_outputs.json")

    rec_data = expected_outputs[mapped_key]
    validate_recommendation(rec_data)
    formatted_block = format_recommendation_block(rec_data)

    trace_data = build_trace(
        input_reels=input_reels,
        case_name=case,
        mapped_key=mapped_key,
        recommendation=rec_data,
        formatted_block=formatted_block,
        output_file=str(out_file),
        trace_file=str(tr_file),
    )

    # Ensure output parent directory exists
    out_file.parent.mkdir(parents=True, exist_ok=True)
    tr_file.parent.mkdir(parents=True, exist_ok=True)

    # Write output files
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(formatted_block + "\n")

    import json
    with open(tr_file, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2)

    return formatted_block, trace_data
