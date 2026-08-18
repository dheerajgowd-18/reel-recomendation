"""Unit tests for ScrollSense Phase 7 naive baselines."""

import unittest

from src.baselines import (
    run_keyword_similarity_baseline,
    run_topic_only_baseline,
)


class TestPhase7Baselines(unittest.TestCase):
    def test_01_baseline1_runs_for_final_trap(self):
        """1. Topic-only baseline runs for final trap case."""
        res = run_topic_only_baseline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        self.assertEqual(res["baseline_name"], "topic_only")
        self.assertEqual(res["category"], "Java")

    def test_02_baseline2_runs_for_final_trap(self):
        """2. Keyword similarity baseline runs for final trap case."""
        res = run_keyword_similarity_baseline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        self.assertEqual(res["baseline_name"], "keyword_similarity")
        self.assertEqual(res["category"], "Java")

    def test_03_baseline1_final_trap_recommends_shallow_java(self):
        """3. Baseline 1 final trap recommends shallow Java content (T96)."""
        res = run_topic_only_baseline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        self.assertEqual(res["recommended_candidate_id"], "T96")
        self.assertEqual(res["recommended_title"], "Learn Java in 60 seconds")

    def test_04_baseline1_final_trap_does_not_recommend_t1(self):
        """4. Baseline 1 final trap does not recommend T1."""
        res = run_topic_only_baseline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        self.assertNotEqual(res["recommended_candidate_id"], "T1")

    def test_05_baseline2_final_trap_does_not_recommend_t1(self):
        """5. Baseline 2 final trap does not recommend T1."""
        res = run_keyword_similarity_baseline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        self.assertNotEqual(res["recommended_candidate_id"], "T1")

    def test_06_baseline_failure_modes_are_populated(self):
        """6. Baselines include explicit failure_mode explanations."""
        res1 = run_topic_only_baseline(["R1", "R2", "R3", "R4"])
        res2 = run_keyword_similarity_baseline(["R1", "R2", "R3", "R4"])
        self.assertTrue(len(res1["failure_mode"]) > 0)
        self.assertTrue(len(res2["failure_mode"]) > 0)


if __name__ == "__main__":
    unittest.main()
