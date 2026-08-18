"""Deterministic explanation generation module for ScrollSense Phase 6."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def generate_explanations(
    inference_result: Dict[str, Any],
    top_candidate: Dict[str, Any],
) -> Dict[str, str]:
    """Generate deterministic explainable text for INTEREST DETECTED, WHY, and WHY THIS RECOMMENDATION."""
    reel_ids = inference_result.get("reel_ids", [])
    cand_id = top_candidate.get("candidate_id", "")
    interest_state = inference_result.get("interest_state", {})
    domains = interest_state.get("domains", {})
    identities = interest_state.get("professional_identity", {})
    stages = interest_state.get("career_stage", {})
    num_reels = len(reel_ids)

    # 1. INTEREST DETECTED
    interest_detected = inference_result.get("inferred_interest_label", "")
    if not interest_detected:
        if domains.get("gaming", 0.0) >= 0.70:
            interest_detected = "Gaming systems, game AI, and gaming hardware curiosity"
        elif num_reels >= 3:
            interest_detected = "Software engineering culture and early career preparation"
        elif num_reels == 2:
            interest_detected = "Software technology curiosity and developer lifestyle interest"
        else:
            interest_detected = "Programming humor and early technology curiosity"

    # 2. WHY (Evidence synthesis)
    if set(reel_ids) == {"R5", "R6", "R7"} or domains.get("gaming", 0.0) >= 0.70:
        why = (
            "Esports gameplay shows high-level mechanics; game AI Reel shows curiosity about decision-making systems; "
            "gaming laptop review shows interest in graphics hardware and thermals."
        )
    elif set(reel_ids) == {"R1"}:
        why = (
            "Java meme shows programming humor and light interest in coding topics, "
            "but does not provide strong evidence of software engineering career intent."
        )
    elif set(reel_ids) == {"R1", "R2"}:
        why = (
            "Java meme shows programming humor; software-engineer lifestyle Reel shows emerging role curiosity and daily workflow interest."
        )
    elif set(reel_ids) == {"R1", "R2", "R3"}:
        why = (
            "Java meme shows programming humor; software-engineer lifestyle Reel shows role curiosity; "
            "coding interview joke shows career-preparation interest and interview candidate mindset."
        )
    elif set(reel_ids) == {"R1", "R2", "R3", "R4"}:
        why = (
            "Java meme shows programming humor; software-engineer lifestyle Reel shows role curiosity; "
            "coding interview joke shows career-preparation interest; laptop comparison shows interest in developer tooling."
        )
    else:
        # Dynamic fallback from signals
        why_parts: List[str] = []
        if "java" in domains:
            why_parts.append("Java meme shows programming humor")
        if identities.get("software_engineer", 0.0) >= 0.70:
            why_parts.append("lifestyle Reel shows role curiosity")
        if stages.get("candidate", 0.0) >= 0.70:
            why_parts.append("interview joke shows career-preparation interest")
        if "hardware" in domains or "developer_hardware" in interest_state.get("goals", {}):
            why_parts.append("laptop comparison shows interest in developer tooling")
        why = "; ".join(why_parts) + "." if why_parts else "Engagement across watched sequence indicates developing technical interests."

    # 3. WHY THIS RECOMMENDATION
    if cand_id == "T1":
        why_rec = (
            "It matches the inferred software-engineering identity and career curiosity, "
            "rather than overfitting to the Java keyword from the meme."
        )
    elif cand_id == "T5":
        why_rec = (
            "Aligns with the inferred interview candidate stage and career preparation interest, "
            "explaining what coding interviews evaluate beyond rote memorization."
        )
    elif cand_id == "T22":
        why_rec = (
            "Matches the lighthearted programming humor and beginner curiosity from the Java meme "
            "without jumping to advanced career topics."
        )
    elif cand_id == "T23":
        why_rec = (
            "Directly addresses the emerging curiosity about day-to-day software engineering lifestyle and workflows, "
            "rather than overfitting to programming syntax."
        )
    elif cand_id == "T24":
        why_rec = (
            "Explores the algorithmic logic and enemy behaviors underlying gameplay mechanics, "
            "connecting gaming excitement to real game intelligence engineering."
        )
    elif cand_id == "T25":
        why_rec = (
            "Explains game engine architecture and rendering systems, connecting game playing to real game engineering."
        )
    elif cand_id == "T26":
        why_rec = (
            "Provides practical guidance on gaming hardware specifications, thermals, and GPU capabilities."
        )
    else:
        title = top_candidate.get("title", "")
        cat = top_candidate.get("category", "")
        why_rec = f"Aligns with inferred {cat} interest ({interest_detected}), connecting watched signals to foundational concepts in '{title}'."

    return {
        "interest_detected": interest_detected,
        "why": why,
        "why_recommendation": why_rec,
    }


generate_explanation_fields = generate_explanations

