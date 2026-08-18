"""Pytest-native contract and regression test suite for ScrollSense."""

from __future__ import annotations

import pytest

from src.pipeline import run_pipeline_for_case

CASES = [
    ("trap_after_R1", "T22", "Low", "Other"),
    ("trap_after_R1_R2", "T23", "Medium", "Career"),
    ("trap_after_R1_R2_R3", "T5", "High", "Career"),
    ("trap_java_to_swe", "T1", "High", "Career"),
    ("non_trap_gaming_only", "T24", "Medium", "AI"),
]

REQUIRED_LABELS = [
    "CURRENT REEL:",
    "INTEREST DETECTED:",
    "WHY:",
    "RECOMMENDED TECH REEL:",
    "CATEGORY:",
    "WHY THIS RECOMMENDATION:",
    "DIFFICULTY:",
    "CONFIDENCE:",
]


@pytest.mark.parametrize("case,expected_id,expected_confidence,expected_category", CASES)
def test_contract_output(case: str, expected_id: str, expected_confidence: str, expected_category: str) -> None:
    """Validate that every case produces expected candidate, confidence, and category."""
    output_text, trace = run_pipeline_for_case(case, mode="real")
    top_cand_id = trace["ranking_summary"]["top_candidate_id"]
    confidence = trace["inference_summary"]["confidence"]

    assert top_cand_id == expected_id, f"Case {case} expected {expected_id}, got {top_cand_id}"
    assert confidence == expected_confidence, f"Case {case} expected confidence {expected_confidence}, got {confidence}"
    assert f"CATEGORY: {expected_category}" in output_text, f"Case {case} missing CATEGORY: {expected_category}"


@pytest.mark.parametrize("label", REQUIRED_LABELS)
def test_required_labels_present(label: str) -> None:
    """Validate that all required 8 contract labels are present in the final trap output."""
    output_text, _ = run_pipeline_for_case("trap_java_to_swe", mode="real")
    assert label in output_text, f"Required label '{label}' missing from output block"


def test_t99_rejected() -> None:
    """Validate that hype clickbait T99 is rejected by the gate in final trap."""
    _, trace = run_pipeline_for_case("trap_java_to_swe", mode="real")
    rejected_ids = trace["gate_summary"]["rejected_ids"]
    assert "T99" in rejected_ids, "T99 was not rejected by the safety gate"


def test_gaming_no_swe_leakage() -> None:
    """Validate that gaming session never leaks software engineering recommendations."""
    output_text, trace = run_pipeline_for_case("non_trap_gaming_only", mode="real")
    top_cand_id = trace["ranking_summary"]["top_candidate_id"]
    top_identity = trace["inference_summary"]["top_professional_identity"]

    assert top_cand_id == "T24", f"Gaming expected T24, got {top_cand_id}"
    assert top_identity != "software_engineer", f"Gaming leaked SWE identity: {top_identity}"
    assert "software engineer" not in output_text.lower(), "Gaming output contained SWE terminology"
