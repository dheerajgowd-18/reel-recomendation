"""Deterministic output formatter and contract validator for ScrollSense."""

from __future__ import annotations

from typing import Dict

from src.config import (
    ALLOWED_CATEGORIES,
    ALLOWED_CONFIDENCES,
    ALLOWED_DIFFICULTIES,
    REQUIRED_OUTPUT_FIELDS,
)


def validate_recommendation(rec: Dict[str, str]) -> None:
    """Validate that a recommendation dict strictly complies with contract constraints."""
    if not isinstance(rec, dict):
        raise ValueError(f"Recommendation must be a dict, got {type(rec).__name__}")

    # 1. Check required fields
    missing_fields = [f for f in REQUIRED_OUTPUT_FIELDS if f not in rec]
    if missing_fields:
        raise ValueError(f"Recommendation missing required field(s): {missing_fields}")

    # 2. Check category
    category = rec["CATEGORY"]
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"Invalid CATEGORY '{category}'. Allowed: {sorted(ALLOWED_CATEGORIES)}"
        )

    # 3. Check difficulty
    difficulty = rec["DIFFICULTY"]
    if difficulty not in ALLOWED_DIFFICULTIES:
        raise ValueError(
            f"Invalid DIFFICULTY '{difficulty}'. Allowed: {sorted(ALLOWED_DIFFICULTIES)}"
        )

    # 4. Check confidence
    confidence = rec["CONFIDENCE"]
    if confidence not in ALLOWED_CONFIDENCES:
        raise ValueError(
            f"Invalid CONFIDENCE '{confidence}'. Allowed: {sorted(ALLOWED_CONFIDENCES)}"
        )


def format_recommendation_block(rec: Dict[str, str]) -> str:
    """Format recommendation dict into the strict plain-text standard output block."""
    validate_recommendation(rec)

    lines = [
        f"CURRENT REEL: {rec['CURRENT REEL']}",
        f"INTEREST DETECTED: {rec['INTEREST DETECTED']}",
        f"WHY: {rec['WHY']}",
        f"RECOMMENDED TECH REEL: {rec['RECOMMENDED TECH REEL']}",
        f"CATEGORY: {rec['CATEGORY']}",
        f"WHY THIS RECOMMENDATION: {rec['WHY THIS RECOMMENDATION']}",
        f"DIFFICULTY: {rec['DIFFICULTY']}",
        f"CONFIDENCE: {rec['CONFIDENCE']}",
    ]
    return "\n".join(lines)
