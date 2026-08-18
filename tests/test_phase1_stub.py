"""Unit tests for ScrollSense Phase 1 stub pipeline."""

import unittest
from pathlib import Path

from src.config import REQUIRED_OUTPUT_FIELDS
from src.formatter import format_recommendation_block, validate_recommendation
from src.loaders import load_expected_outputs
from src.stub_pipeline import normalize_input, resolve_expected_key, run_stub_pipeline


class TestPhase1StubPipeline(unittest.TestCase):
    def setUp(self):
        self.expected_outputs = load_expected_outputs()

    def test_01_trap_checkpoint_reel_sequences_mapping(self):
        """1. The four trap checkpoint reel sequences map to the correct expected keys."""
        seq_map = {
            "R1": "trap_after_R1",
            "R1,R2": "trap_after_R1_R2",
            "R1,R2,R3": "trap_after_R1_R2_R3",
            "R1,R2,R3,R4": "trap_after_R1_R2_R3_R4",
        }
        for seq, expected_key in seq_map.items():
            ids, join_key = normalize_input(seq)
            mapped = resolve_expected_key(reel_ids=ids, join_key=join_key)
            self.assertEqual(mapped, expected_key, f"Sequence {seq} should map to {expected_key}")

    def test_02_trap_case_name_mapping(self):
        """2. The case trap_java_to_swe maps to trap_after_R1_R2_R3_R4."""
        mapped = resolve_expected_key(case_name="trap_java_to_swe")
        self.assertEqual(mapped, "trap_after_R1_R2_R3_R4")

    def test_03_non_trap_case_name_mapping(self):
        """3. The case non_trap_gaming_only maps to non_trap_gaming_only."""
        mapped = resolve_expected_key(case_name="non_trap_gaming_only")
        self.assertEqual(mapped, "non_trap_gaming_only")

    def test_04_formatter_output_contains_all_required_labels(self):
        """4. The formatter output contains all required labels."""
        sample = self.expected_outputs["trap_after_R1_R2_R3_R4"]
        output = format_recommendation_block(sample)
        for field in REQUIRED_OUTPUT_FIELDS:
            label = f"{field}:"
            self.assertIn(label, output, f"Output must contain label '{label}'")

    def test_05_formatter_rejects_invalid_category(self):
        """5. The formatter rejects invalid CATEGORY values."""
        sample = dict(self.expected_outputs["trap_after_R1_R2_R3_R4"])
        sample["CATEGORY"] = "InvalidCryptoCategory"
        with self.assertRaises(ValueError) as ctx:
            validate_recommendation(sample)
        self.assertIn("Invalid CATEGORY", str(ctx.exception))

    def test_06_formatter_rejects_invalid_difficulty(self):
        """6. The formatter rejects invalid DIFFICULTY values."""
        sample = dict(self.expected_outputs["trap_after_R1_R2_R3_R4"])
        sample["DIFFICULTY"] = "ExpertLevel10"
        with self.assertRaises(ValueError) as ctx:
            validate_recommendation(sample)
        self.assertIn("Invalid DIFFICULTY", str(ctx.exception))

    def test_07_formatter_rejects_invalid_confidence(self):
        """7. The formatter rejects invalid CONFIDENCE values."""
        sample = dict(self.expected_outputs["trap_after_R1_R2_R3_R4"])
        sample["CONFIDENCE"] = "SuperHigh"
        with self.assertRaises(ValueError) as ctx:
            validate_recommendation(sample)
        self.assertIn("Invalid CONFIDENCE", str(ctx.exception))

    def test_08_unknown_reel_id_raises_clear_error(self):
        """8. An unknown reel ID raises a clear error."""
        with self.assertRaises(ValueError) as ctx:
            normalize_input("R1,R999")
        self.assertIn("Unknown reel ID", str(ctx.exception))

    def test_09_unknown_case_name_raises_clear_error(self):
        """9. An unknown case name raises a clear error."""
        with self.assertRaises(ValueError) as ctx:
            resolve_expected_key(case_name="non_existent_case_foo")
        self.assertIn("Unknown case name", str(ctx.exception))

    def test_10_gaming_non_trap_does_not_recommend_swe_trap_candidate(self):
        """10. The non_trap_gaming_only output does not recommend a software-engineering-only trap candidate."""
        formatted, trace = run_stub_pipeline(case="non_trap_gaming_only")
        recommended = trace["stages"]["recommend_stub"]["recommended_reel"]
        category = trace["stages"]["recommend_stub"]["category"]

        forbidden_titles = [
            "How a junior software engineer ships a small feature",
            "What software engineers actually do all day",
            "10 AI tools that will get you a job",
        ]
        self.assertNotIn(recommended, forbidden_titles)
        self.assertNotEqual(category, "Career")
        self.assertEqual(recommended, "How game AI decides enemy behavior")


if __name__ == "__main__":
    unittest.main()
