"""InterestState aggregation and student persona modeling for ScrollSense Phase 3."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def aggregate_interest_state(
    signals: List[Dict[str, Any]],
    student_id: str = "student_001",
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Aggregate a list of ReelSignals into a structured InterestState."""
    if not signals:
        raise ValueError("Cannot aggregate empty signals list.")

    reel_ids = [s["reel_id"] for s in signals if "reel_id" in s]
    sess_id = session_id or f"session_{'_'.join(reel_ids)}"
    updated_at = "2026-08-18T00:00:00Z"

    # Aggregation buckets
    identity_evidence: Dict[str, List[float]] = {}
    stage_evidence: Dict[str, List[float]] = {}
    domain_evidence: Dict[str, List[float]] = {}
    goal_evidence: Dict[str, List[float]] = {}
    skill_evidence: Dict[str, List[float]] = {}
    tooling_evidence: Dict[str, List[float]] = {}
    pref_evidence: Dict[str, List[float]] = {}

    for sig in signals:
        fmt = sig.get("format", "")
        tone = sig.get("tone", "")

        # Format and tone preferences
        if fmt in {"meme", "humor"} or tone == "humorous":
            pref_evidence.setdefault("humor", []).append(0.70)
        if fmt == "lifestyle" or tone == "aspirational":
            pref_evidence.setdefault("lifestyle", []).append(0.75)
        if fmt == "comparison" or tone == "comparative":
            pref_evidence.setdefault("comparison", []).append(0.65)
        if fmt == "gaming" or tone == "entertainment":
            pref_evidence.setdefault("gameplay", []).append(0.80)

        for ev in sig.get("interest_evidence", []):
            etype = ev.get("evidence_type")
            val = ev.get("value")
            strength = float(ev.get("strength", 0.0))

            if not val or strength <= 0.0:
                continue

            if etype == "professional_identity_signal":
                identity_evidence.setdefault(val, []).append(strength)
            elif etype == "career_stage_signal":
                stage_evidence.setdefault(val, []).append(strength)
            elif etype == "domain_signal":
                domain_evidence.setdefault(val, []).append(strength)
            elif etype == "goal_signal":
                goal_evidence.setdefault(val, []).append(strength)
            elif etype == "skill_signal":
                skill_evidence.setdefault(val, []).append(strength)
            elif etype == "tooling_signal":
                tooling_evidence.setdefault(val, []).append(strength)
                # Tooling signal softly reinforces domain context without becoming identity
                if val == "developer_hardware":
                    domain_evidence.setdefault("software_engineering", []).append(0.40)
            elif etype == "topic_exposure":
                # Topic exposure contributes weakly to domain evidence if not already present
                domain_evidence.setdefault(val, []).append(strength * 0.7)
            elif etype == "content_preference_signal":
                pref_evidence.setdefault(val, []).append(strength)

    def _calc_aggregated_score(scores: List[float]) -> float:
        if not scores:
            return 0.0
        sorted_scores = sorted(scores, reverse=True)
        base = sorted_scores[0]
        # Reinforcement bonus for multi-reel agreement (up to +0.15)
        bonus = min(0.15, 0.05 * (len(scores) - 1))
        return round(min(1.0, base + bonus), 3)

    professional_identity = {
        k: _calc_aggregated_score(v) for k, v in identity_evidence.items()
    }
    career_stage = {
        k: _calc_aggregated_score(v) for k, v in stage_evidence.items()
    }
    domains = {
        k: _calc_aggregated_score(v) for k, v in domain_evidence.items()
    }
    goals = {
        k: _calc_aggregated_score(v) for k, v in goal_evidence.items()
    }
    content_preference = {
        k: _calc_aggregated_score(v) for k, v in pref_evidence.items()
    }

    # If career_stage candidate or career goals exist, add career to domains
    if "candidate" in career_stage or "career_prep" in goals or "career_curiosity" in goals:
        career_strength = max(
            career_stage.get("candidate", 0.0),
            goals.get("career_prep", 0.0),
            goals.get("career_curiosity", 0.0),
        )
        domains["career"] = round(career_strength, 3)

    # Determine learning depth preference
    depth_map: Dict[str, str] = {}
    for d_name in domains:
        depth_map[d_name] = "Beginner"

    return {
        "student_id": student_id,
        "session_id": sess_id,
        "reel_ids": reel_ids,
        "professional_identity": professional_identity,
        "career_stage": career_stage,
        "domains": domains,
        "goals": goals,
        "depth": depth_map,
        "content_preference": content_preference,
        "evidence": reel_ids,
        "updated_at": updated_at,
    }
