"""Unit tests for ScrollSense Phase 7 demo harness, baselines, and reports."""

import unittest

from src.demo import (
    DEMO_HTML_PATH,
    DEMO_REPORT_PATH,
    PITCH_LINE,
    run_demo,
)


class TestPhase7Demo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo_trace = run_demo(all_cases=True)
        cls.trap_data = cls.demo_trace["cases"]["trap_java_to_swe"]
        cls.gaming_data = cls.demo_trace["cases"]["non_trap_gaming_only"]

    def test_01_baseline1_runs_for_final_trap(self):
        """1. Baseline 1 runs for final trap."""
        self.assertIn("topic_only", self.trap_data["baselines"])

    def test_02_baseline2_runs_for_final_trap(self):
        """2. Baseline 2 runs for final trap."""
        self.assertIn("keyword_similarity", self.trap_data["baselines"])

    def test_03_baseline1_final_trap_recommends_shallow_java(self):
        """3. Baseline 1 final trap recommends shallow Java content."""
        b1_rec = self.trap_data["baselines"]["topic_only"]["recommended_candidate_id"]
        b1_cat = self.trap_data["baselines"]["topic_only"]["category"]
        self.assertTrue(b1_rec == "T96" or b1_cat == "Java")

    def test_04_baseline1_final_trap_does_not_recommend_t1(self):
        """4. Baseline 1 final trap does not recommend T1."""
        self.assertNotEqual(self.trap_data["baselines"]["topic_only"]["recommended_candidate_id"], "T1")

    def test_05_baseline2_final_trap_does_not_recommend_t1(self):
        """5. Baseline 2 final trap does not recommend T1."""
        self.assertNotEqual(self.trap_data["baselines"]["keyword_similarity"]["recommended_candidate_id"], "T1")

    def test_06_scrollsense_final_trap_recommends_t1(self):
        """6. ScrollSense final trap recommends T1."""
        self.assertEqual(self.trap_data["scrollsense"]["recommended_candidate_id"], "T1")

    def test_07_scrollsense_final_trap_rejects_t99(self):
        """7. ScrollSense final trap rejects T99."""
        rejs = [r["candidate_id"] for r in self.trap_data["scrollsense"]["gate_rejections"]]
        self.assertIn("T99", rejs)

    def test_08_scrollsense_gaming_recommends_t24(self):
        """8. ScrollSense gaming recommends T24."""
        self.assertEqual(self.gaming_data["scrollsense"]["recommended_candidate_id"], "T24")

    def test_09_scrollsense_gaming_does_not_recommend_t1(self):
        """9. ScrollSense gaming does not recommend T1."""
        self.assertNotEqual(self.gaming_data["scrollsense"]["recommended_candidate_id"], "T1")

    def test_10_scrollsense_gaming_does_not_recommend_t5(self):
        """10. ScrollSense gaming does not recommend T5."""
        self.assertNotEqual(self.gaming_data["scrollsense"]["recommended_candidate_id"], "T5")

    def test_11_scrollsense_gaming_does_not_recommend_t23(self):
        """11. ScrollSense gaming does not recommend T23."""
        self.assertNotEqual(self.gaming_data["scrollsense"]["recommended_candidate_id"], "T23")

    def test_12_demo_trace_includes_baselines_and_scrollsense(self):
        """12. Demo trace includes baselines and ScrollSense results."""
        self.assertIn("baselines", self.trap_data)
        self.assertIn("scrollsense", self.trap_data)

    def test_13_demo_report_includes_required_sections(self):
        """13. Demo report includes required sections and pitch line."""
        report_text = DEMO_REPORT_PATH.read_text(encoding="utf-8")
        self.assertIn("## Executive Summary", report_text)
        self.assertIn("## Part 1: The Trap Case", report_text)
        self.assertIn("## Part 2: Non-Trap Gaming Case", report_text)
        self.assertIn(PITCH_LINE, report_text)

    def test_14_demo_html_exists_and_no_cdns(self):
        """14. Demo HTML exists and contains no external CDN links or http scripts."""
        html_text = DEMO_HTML_PATH.read_text(encoding="utf-8")
        self.assertNotIn("http://", html_text)
        self.assertNotIn("https://", html_text)
        self.assertIn("ScrollSense: Recommendation Agent Demo", html_text)

    def test_15_demo_is_deterministic(self):
        """15. Demo execution is strictly deterministic."""
        trace2 = run_demo(all_cases=True)
        self.assertEqual(self.demo_trace, trace2)


if __name__ == "__main__":
    unittest.main()
