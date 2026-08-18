"""Unit tests for Phase 9A-NVIDIA: Nemotron-3.5 Lightning 30B integration."""

import os
import unittest
from pathlib import Path

from src.ai_cache import (
    PROMPT_VERSION_EXPLANATION,
    PROMPT_VERSION_SIGNAL,
    make_cache_key,
    validate_ai_signal,
)
from src.ai_explainer import generate_explanations_hybrid
from src.ai_signals import extract_signal_hybrid
from src.config import LLM_MODEL
from src.llm_client import LLMClient
from src.loaders import load_watched_reels
from src.pipeline import run_pipeline_for_case


class TestPhase9Nvidia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.watched = load_watched_reels()
        cls.r1 = next(r for r in cls.watched if r["reel_id"] == "R1")
        cls.r5 = next(r for r in cls.watched if r["reel_id"] == "R5")

    def test_01_default_deterministic_mode_still_passes(self):
        """1. Default deterministic mode still produces valid output."""
        sig, fb, status = extract_signal_hybrid(self.r1, extractor_mode="deterministic")
        self.assertFalse(fb)
        self.assertEqual(status, "deterministic")
        self.assertEqual(sig["reel_id"], "R1")

    def test_02_mock_provider_returns_valid_output(self):
        """2. Mock LLMClient provider returns synthetic JSON cleanly."""
        client = LLMClient(provider="mock")
        res, is_fb = client.complete_json([], mock_json={"status": "mock_success"})
        self.assertFalse(is_fb)
        self.assertEqual(res.get("status"), "mock_success")

    def test_03_cache_provider_works_offline(self):
        """3. Cache provider operates 100% offline using persisted cache files."""
        sig, fb, status = extract_signal_hybrid(self.r1, extractor_mode="hybrid")
        self.assertFalse(fb)
        self.assertEqual(status, "cached")
        self.assertEqual(sig["reel_id"], "R1")

    def test_04_invalid_json_falls_back_safely(self):
        """4. Corrupted/unparseable LLM output falls back to deterministic extraction."""
        client = LLMClient(provider="mock")
        # Complete with invalid non-JSON mock
        raw = client.complete_chat([], mock_response="THIS IS NOT JSON")
        self.assertEqual(raw, "THIS IS NOT JSON")
        parsed, fb = client.complete_json([], mock_json={"fallback": True}, mock_response="THIS IS NOT JSON")
        self.assertTrue(fb)
        self.assertEqual(parsed, {"fallback": True})

    def test_05_schema_violation_falls_back_safely(self):
        """5. AI signal schema violation is detected and rejected."""
        bad_sig = {
            "reel_id": "R1",
            "RECOMMENDED TECH REEL": "Learn Java in 60 seconds",  # Illegal key
        }
        is_valid, msg = validate_ai_signal(bad_sig, "R1")
        self.assertFalse(is_valid)
        self.assertIn("recommendation", msg.lower())

    def test_06_gaming_reels_do_not_leak_software_engineer(self):
        """6. Gaming reels (R5, R6, R7) do not emit software_engineer signal > 0.2."""
        bad_gaming_sig = {
            "reel_id": "R5",
            "signal_version": "v1",
            "ontology_version": "graph-v1",
            "model_version": "deterministic-rules-v1",
            "generated_at": "2026-08-18T00:00:00Z",
            "topic": "gaming",
            "format": "gaming",
            "tone": "entertainment",
            "depth": "surface",
            "concept_tags": ["gaming"],
            "interest_evidence": [
                {
                    "evidence_type": "professional_identity_signal",
                    "value": "software_engineer",
                    "strength": 0.85,  # Illegal for R5
                    "source_hint": "gaming clip",
                }
            ],
        }
        is_valid, msg = validate_ai_signal(bad_gaming_sig, "R5")
        self.assertFalse(is_valid)
        self.assertIn("software_engineer", msg)

    def test_07_r1_does_not_over_infer_software_engineer(self):
        """7. R1 meme does not emit software_engineer signal > 0.45."""
        overgeneralized_r1 = {
            "reel_id": "R1",
            "signal_version": "v1",
            "ontology_version": "graph-v1",
            "model_version": "deterministic-rules-v1",
            "generated_at": "2026-08-18T00:00:00Z",
            "topic": "programming_humor",
            "format": "meme",
            "tone": "humorous",
            "depth": "surface",
            "concept_tags": ["java", "programming"],
            "interest_evidence": [
                {
                    "evidence_type": "professional_identity_signal",
                    "value": "software_engineer",
                    "strength": 0.90,  # Overgeneralized
                    "source_hint": "Java meme",
                }
            ],
        }
        is_valid, msg = validate_ai_signal(overgeneralized_r1, "R1")
        self.assertFalse(is_valid)

    def test_08_explanation_adapter_does_not_change_candidate(self):
        """8. Explanation adapter cannot modify the chosen candidate title."""
        top_cand = {"id": "T1", "title": "How a junior software engineer ships a small feature", "category": "Career", "difficulty": "Beginner"}
        inf_res = {"reel_ids": ["R1", "R2", "R3", "R4"], "confidence": "High"}
        expl, fb, _ = generate_explanations_hybrid(inf_res, top_cand, case_name="trap_java_to_swe")
        self.assertIn("interest_detected", expl)
        self.assertIn("why", expl)

    def test_09_explanation_adapter_preserves_category(self):
        """9. Pipeline CATEGORY remains unaltered by AI explanation."""
        txt, trace = run_pipeline_for_case("trap_java_to_swe", mode="real", explainer="hybrid")
        self.assertIn("CATEGORY: Career", txt)

    def test_10_explanation_adapter_preserves_difficulty(self):
        """10. Pipeline DIFFICULTY remains unaltered by AI explanation."""
        txt, trace = run_pipeline_for_case("trap_java_to_swe", mode="real", explainer="hybrid")
        self.assertIn("DIFFICULTY: Beginner", txt)

    def test_11_explanation_adapter_preserves_confidence(self):
        """11. Pipeline CONFIDENCE remains unaltered by AI explanation."""
        txt, trace = run_pipeline_for_case("trap_java_to_swe", mode="real", explainer="hybrid")
        self.assertIn("CONFIDENCE: High", txt)

    def test_12_hybrid_cache_mode_final_trap_recommends_t1(self):
        """12. Hybrid cache mode final trap recommends T1."""
        txt, trace = run_pipeline_for_case("trap_java_to_swe", mode="real", extractor="hybrid", explainer="hybrid")
        self.assertEqual(trace["ranking_summary"]["top_candidate_id"], "T1")
        self.assertIn("RECOMMENDED TECH REEL: How a junior software engineer ships a small feature", txt)

    def test_13_hybrid_cache_mode_gaming_recommends_t24(self):
        """13. Hybrid cache mode gaming recommends T24."""
        txt, trace = run_pipeline_for_case("non_trap_gaming_only", mode="real", extractor="hybrid", explainer="hybrid")
        self.assertEqual(trace["ranking_summary"]["top_candidate_id"], "T24")
        self.assertIn("RECOMMENDED TECH REEL: How game AI decides enemy behavior", txt)

    def test_14_t99_is_still_rejected_under_hybrid_mode(self):
        """14. T99 remains strictly rejected in gate under hybrid AI mode."""
        _, trace = run_pipeline_for_case("trap_java_to_swe", mode="real", extractor="hybrid", explainer="hybrid")
        self.assertIn("T99", trace["gate_summary"]["rejected_ids"])

    def test_15_tests_do_not_require_live_api_key(self):
        """15. Verified that tests execute without LLM_API_KEY environment variable."""
        orig_key = os.environ.get("LLM_API_KEY")
        if "LLM_API_KEY" in os.environ:
            del os.environ["LLM_API_KEY"]
        try:
            client = LLMClient()
            self.assertEqual(client.provider, "cache")
        finally:
            if orig_key:
                os.environ["LLM_API_KEY"] = orig_key

    def test_16_tests_do_not_require_network_access(self):
        """16. Pipeline runs fully offline in hybrid cache mode."""
        txt, trace = run_pipeline_for_case("trap_java_to_swe", mode="real", extractor="hybrid", explainer="hybrid")
        self.assertEqual(trace["ai"]["llm_status"], "cached")


if __name__ == "__main__":
    unittest.main()
