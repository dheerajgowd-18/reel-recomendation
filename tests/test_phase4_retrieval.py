"""Unit tests for ScrollSense Phase 4 candidate retrieval."""

import unittest
from pathlib import Path

from src.retrieve import run_all_checkpoints_retrieval, run_retrieval_pipeline


class TestPhase4Retrieval(unittest.TestCase):
    def setUp(self):
        self.trap_res = run_retrieval_pipeline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        self.gaming_res = run_retrieval_pipeline(["R5", "R6", "R7"], case_name="non_trap_gaming_only")
        self.r1_res = run_retrieval_pipeline(["R1"])

    def test_01_final_trap_retrieval_includes_t1(self):
        """1. Final trap retrieval includes T1 ('How a junior software engineer ships a small feature')."""
        cand_ids = [c["candidate_id"] for c in self.trap_res["candidates"]]
        self.assertIn("T1", cand_ids)

    def test_02_final_trap_top5_includes_career_candidate(self):
        """2. Final trap retrieval top 5 includes a Career category candidate."""
        top5 = self.trap_res["candidates"][:5]
        cats = [c["category"] for c in top5]
        self.assertIn("Career", cats)

    def test_03_final_trap_not_dominated_by_java(self):
        """3. Final trap retrieval top 5 is not dominated by Java candidates."""
        top5 = self.trap_res["candidates"][:5]
        cats = [c["category"] for c in top5]
        java_count = sum(1 for c in cats if c == "Java")
        self.assertLess(java_count, 3)

    def test_04_final_trap_uses_identity_adjacent_evidence(self):
        """4. Final trap retrieval uses Source B identity-adjacent evidence."""
        id_adj = self.trap_res["sources"]["identity_adjacent"]
        self.assertGreaterEqual(len(id_adj), 5)
        top1 = self.trap_res["candidates"][0]
        self.assertIn("identity_adjacent", top1["sources"])

    def test_05_r1_retrieval_does_not_overgeneralize(self):
        """5. R1 retrieval does not overgeneralize into a strong software-engineering career shortlist."""
        cand_ids = [c["candidate_id"] for c in self.r1_res["candidates"][:3]]
        # R1 top candidates should include beginner programming / java / humor
        self.assertTrue(any(c_id in {"T11", "T12", "T22"} for c_id in cand_ids))

    def test_06_gaming_retrieval_includes_gaming_candidates(self):
        """6. Gaming retrieval includes at least one gaming-adjacent candidate (T24, T25, T26)."""
        cand_ids = {c["candidate_id"] for c in self.gaming_res["candidates"]}
        self.assertTrue(bool(cand_ids.intersection({"T24", "T25", "T26"})))

    def test_07_gaming_top5_does_not_include_t1(self):
        """7. Gaming retrieval top 5 does not include T1."""
        top5_ids = [c["candidate_id"] for c in self.gaming_res["candidates"][:5]]
        self.assertNotIn("T1", top5_ids)

    def test_08_gaming_top5_does_not_include_t5(self):
        """8. Gaming retrieval top 5 does not include T5."""
        top5_ids = [c["candidate_id"] for c in self.gaming_res["candidates"][:5]]
        self.assertNotIn("T5", top5_ids)

    def test_09_gaming_top5_does_not_include_t23(self):
        """9. Gaming retrieval top 5 does not include T23."""
        top5_ids = [c["candidate_id"] for c in self.gaming_res["candidates"][:5]]
        self.assertNotIn("T23", top5_ids)

    def test_10_t99_not_top_ranked_in_trap(self):
        """10. T99 is not top-ranked in the final trap case."""
        top_cand = self.trap_res["candidates"][0]["candidate_id"]
        self.assertNotEqual(top_cand, "T99")

    def test_11_t99_not_top_ranked_in_gaming(self):
        """11. T99 is not top-ranked in the gaming case."""
        top_cand = self.gaming_res["candidates"][0]["candidate_id"]
        self.assertNotEqual(top_cand, "T99")

    def test_12_retrieval_result_schema_valid(self):
        """12. Retrieval result schema is valid."""
        req_keys = [
            "phase",
            "case",
            "reel_ids",
            "interest_summary",
            "sources",
            "candidates",
            "candidate_count",
            "generated_at",
        ]
        for k in req_keys:
            self.assertIn(k, self.trap_res)
        self.assertEqual(self.trap_res["phase"], "phase_4_retrieval")

    def test_13_retrieval_is_deterministic(self):
        """13. Retrieval is deterministic across runs."""
        res_repeat = run_retrieval_pipeline(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        order1 = [c["candidate_id"] for c in self.trap_res["candidates"]]
        order2 = [c["candidate_id"] for c in res_repeat["candidates"]]
        self.assertEqual(order1, order2)

    def test_14_unknown_reel_id_raises_error(self):
        """14. Unknown reel ID raises an error."""
        with self.assertRaises(Exception):
            run_retrieval_pipeline(["UNKNOWN_REEL_999"])

    def test_15_unknown_case_name_raises_error(self):
        """15. Unknown case name raises an error."""
        with self.assertRaises(ValueError):
            run_retrieval_pipeline(["R1"], case_name="unknown_case_foo")


if __name__ == "__main__":
    unittest.main()
