"""Unit tests for ScrollSense Phase 6 pipeline, ranking, and exact output generation."""

import unittest
from pathlib import Path

from src.formatter import validate_output_fields
from src.pipeline import run_pipeline_for_case, run_pipeline_for_reels
from tools.validate_pipeline import parse_output_block


class TestPhase6Pipeline(unittest.TestCase):
    def setUp(self):
        self.trap_txt, self.trap_trace = run_pipeline_for_case("trap_java_to_swe", mode="real")
        self.gaming_txt, self.gaming_trace = run_pipeline_for_case("non_trap_gaming_only", mode="real")
        self.r1_txt, self.r1_trace = run_pipeline_for_reels(["R1"], mode="real")
        self.r1_r2_txt, self.r1_r2_trace = run_pipeline_for_reels(["R1", "R2"], mode="real")
        self.r1_r2_r3_txt, self.r1_r2_r3_trace = run_pipeline_for_reels(["R1", "R2", "R3"], mode="real")

        self.trap_fields = parse_output_block(self.trap_txt)
        self.gaming_fields = parse_output_block(self.gaming_txt)
        self.r1_fields = parse_output_block(self.r1_txt)
        self.r1_r2_fields = parse_output_block(self.r1_r2_txt)
        self.r1_r2_r3_fields = parse_output_block(self.r1_r2_r3_txt)

    def test_01_final_trap_recommends_t1(self):
        """1. Real pipeline final trap recommends T1 ('How a junior software engineer ships a small feature')."""
        self.assertIn("ships a small feature", self.trap_fields["RECOMMENDED TECH REEL"])

    def test_02_final_trap_exact_required_labels(self):
        """2. Real pipeline final trap output contains all 8 required labels and passes validation."""
        validate_output_fields(self.trap_fields)
        for label in [
            "CURRENT REEL",
            "INTEREST DETECTED",
            "WHY",
            "RECOMMENDED TECH REEL",
            "CATEGORY",
            "WHY THIS RECOMMENDATION",
            "DIFFICULTY",
            "CONFIDENCE",
        ]:
            self.assertIn(label, self.trap_fields)

    def test_03_final_trap_category_is_career(self):
        """3. Real pipeline final trap CATEGORY is Career."""
        self.assertEqual(self.trap_fields["CATEGORY"], "Career")

    def test_04_final_trap_difficulty_is_beginner(self):
        """4. Real pipeline final trap DIFFICULTY is Beginner."""
        self.assertEqual(self.trap_fields["DIFFICULTY"], "Beginner")

    def test_05_final_trap_confidence_is_high(self):
        """5. Real pipeline final trap CONFIDENCE is High."""
        self.assertEqual(self.trap_fields["CONFIDENCE"], "High")

    def test_06_r1_recommends_t22(self):
        """6. Real pipeline R1 recommends T22 ('Beginner programming concepts explained with memes')."""
        self.assertIn("memes", self.r1_fields["RECOMMENDED TECH REEL"].lower())

    def test_07_r1_does_not_recommend_t1(self):
        """7. Real pipeline R1 does not recommend T1."""
        self.assertNotIn("ships a small feature", self.r1_fields["RECOMMENDED TECH REEL"])

    def test_08_r1_r2_recommends_t23(self):
        """8. Real pipeline R1+R2 recommends T23 ('What software engineers actually do all day')."""
        self.assertIn("software engineers actually do", self.r1_r2_fields["RECOMMENDED TECH REEL"].lower())

    def test_09_r1_r2_r3_recommends_t5(self):
        """9. Real pipeline R1+R2+R3 recommends T5 ('What a coding interview is really testing')."""
        self.assertIn("coding interview", self.r1_r2_r3_fields["RECOMMENDED TECH REEL"].lower())

    def test_10_gaming_recommends_t24(self):
        """10. Real pipeline gaming recommends T24 ('How game AI decides enemy behavior')."""
        self.assertIn("game ai", self.gaming_fields["RECOMMENDED TECH REEL"].lower())

    def test_11_gaming_does_not_recommend_t1(self):
        """11. Real pipeline gaming does not recommend T1."""
        self.assertNotIn("ships a small feature", self.gaming_fields["RECOMMENDED TECH REEL"])

    def test_12_gaming_does_not_recommend_t5(self):
        """12. Real pipeline gaming does not recommend T5."""
        self.assertNotIn("coding interview", self.gaming_fields["RECOMMENDED TECH REEL"].lower())

    def test_13_gaming_does_not_recommend_t23(self):
        """13. Real pipeline gaming does not recommend T23."""
        self.assertNotIn("actually do all day", self.gaming_fields["RECOMMENDED TECH REEL"].lower())

    def test_14_t99_is_never_recommended(self):
        """14. T99 is never recommended across any pipeline run."""
        for p in [self.r1_fields, self.r1_r2_fields, self.r1_r2_r3_fields, self.trap_fields, self.gaming_fields]:
            self.assertNotIn("10 ai tools that will get you a job", p["RECOMMENDED TECH REEL"].lower())

    def test_15_fallback_not_used_in_real_validation(self):
        """15. Fallback is not used in real mode validation."""
        self.assertFalse(self.trap_trace["fallback_used"])
        self.assertFalse(self.gaming_trace["fallback_used"])

    def test_16_stub_mode_still_works(self):
        """16. Stub mode still produces the Phase 1 golden output."""
        stub_txt, stub_trace = run_pipeline_for_case("trap_java_to_swe", mode="stub")
        stub_fields = parse_output_block(stub_txt)
        self.assertEqual(stub_fields["RECOMMENDED TECH REEL"], "How a junior software engineer ships a small feature")
        self.assertEqual(stub_trace["mode"], "stub")

    def test_17_pipeline_trace_structure(self):
        """17. Pipeline trace contains inference, retrieval, gate, ranking, and explanation summaries."""
        required_keys = [
            "phase",
            "mode",
            "case",
            "reel_ids",
            "inference_summary",
            "retrieval_summary",
            "gate_summary",
            "ranking_summary",
            "explanation_summary",
            "fallback_used",
            "generated_at",
        ]
        for k in required_keys:
            self.assertIn(k, self.trap_trace)

    def test_18_pipeline_output_is_deterministic(self):
        """18. Pipeline output is strictly deterministic across repeated runs."""
        txt2, _ = run_pipeline_for_case("trap_java_to_swe", mode="real")
        self.assertEqual(self.trap_txt, txt2)


if __name__ == "__main__":
    unittest.main()
