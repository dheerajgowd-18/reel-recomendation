"""Unit tests for ScrollSense Phase 5 safety/quality/hype gate."""

import unittest
from pathlib import Path

from src.gate import (
    gate_candidate,
    load_or_generate_gate_cache,
    run_all_checkpoint_gates,
    run_gate_for_case,
    run_gate_for_reels,
)
from src.loaders import load_tech_reels


class TestPhase5Gate(unittest.TestCase):
    def setUp(self):
        self.tech_reels_map = {c["id"]: c for c in load_tech_reels()}

    def test_01_t99_is_rejected(self):
        """1. T99 is rejected by the gate."""
        cand = self.tech_reels_map["T99"]
        res = gate_candidate(cand)
        self.assertTrue(res["effective_reject"])
        self.assertIn("job", res["rejection_reason"].lower())

    def test_02_t99_rejected_even_with_zero_reference_hype(self):
        """2. T99 is rejected even if its reference hype_score is artificially set to 0.0."""
        cand = dict(self.tech_reels_map["T99"])
        cand["hype_score"] = 0.0
        res = gate_candidate(cand)
        self.assertTrue(res["effective_reject"])

    def test_03_t99_rejected_even_with_max_reference_quality(self):
        """3. T99 is rejected even if its reference quality_score is artificially set to 1.0."""
        cand = dict(self.tech_reels_map["T99"])
        cand["quality_score"] = 1.0
        res = gate_candidate(cand)
        self.assertTrue(res["effective_reject"])

    def test_04_t1_passes_gate(self):
        """4. T1 passes the gate."""
        cand = self.tech_reels_map["T1"]
        res = gate_candidate(cand)
        self.assertFalse(res["effective_reject"])
        self.assertEqual(res["rejection_reason"], "")

    def test_05_t24_passes_gate(self):
        """5. T24 passes the gate."""
        cand = self.tech_reels_map["T24"]
        res = gate_candidate(cand)
        self.assertFalse(res["effective_reject"])

    def test_06_t97_passes_gate(self):
        """6. T97 ('10 AI tools worth learning') passes the gate due to strong concept anchors."""
        if "T97" in self.tech_reels_map:
            cand = self.tech_reels_map["T97"]
            res = gate_candidate(cand)
            self.assertFalse(res["effective_reject"])
            self.assertGreaterEqual(res["quality"]["concept_anchor_score"], 0.35)

    def test_07_hard_denylist_causes_immediate_rejection(self):
        """7. Hard denylist match causes immediate rejection."""
        fake_cand = {
            "id": "F1",
            "title": "Secret tools to get you a job without coding",
            "category": "Career",
            "concept_tags": ["python", "career"],
            "difficulty": "Beginner",
        }
        res = gate_candidate(fake_cand)
        self.assertTrue(res["hard_denylist_match"])
        self.assertTrue(res["effective_reject"])

    def test_08_weak_concept_anchor_plus_high_hype_causes_rejection(self):
        """8. Weak concept anchor plus high hype causes rejection."""
        fake_cand = {
            "id": "F2",
            "title": "Top 10 fast tricks and secrets for your career",
            "category": "Career",
            "concept_tags": ["tips", "tricks", "shortcuts"],
            "difficulty": "Beginner",
        }
        res = gate_candidate(fake_cand)
        self.assertTrue(res["effective_reject"])

    def test_09_strong_concept_anchor_with_mild_listicle_passes(self):
        """9. Strong concept anchor plus mild listicle wording passes."""
        fake_cand = {
            "id": "F3",
            "title": "Top 5 debugging tools in Linux with gdb and strace",
            "category": "Other",
            "concept_tags": ["debugging", "linux", "tools"],
            "difficulty": "Intermediate",
        }
        res = gate_candidate(fake_cand)
        self.assertFalse(res["effective_reject"])

    def test_10_rejection_reason_is_non_empty_when_rejected(self):
        """10. Rejection reason is non-empty when effective_reject is true."""
        cand = self.tech_reels_map["T99"]
        res = gate_candidate(cand)
        self.assertTrue(len(res["rejection_reason"]) > 0)

    def test_11_gate_result_schema_valid(self):
        """11. Gate result schema is valid."""
        gate_res = run_gate_for_case("trap_java_to_swe")
        req_keys = [
            "phase",
            "case",
            "reel_ids",
            "gate_version",
            "passed_candidates",
            "rejected_candidates",
            "passed_count",
            "rejected_count",
            "requires_fallback",
            "generated_at",
        ]
        for k in req_keys:
            self.assertIn(k, gate_res)
        self.assertEqual(gate_res["phase"], "phase_5_gate")

    def test_12_gate_cache_regeneration(self):
        """12. Gate cache can be regenerated cleanly with force_refresh."""
        cache = load_or_generate_gate_cache(force_refresh=True)
        self.assertIn("T1", cache)
        self.assertIn("T99", cache)
        self.assertEqual(cache["T1"]["score_source"], "computed")

    def test_13_gate_is_deterministic(self):
        """13. Gate execution is deterministic across multiple calls."""
        res1 = run_gate_for_case("trap_java_to_swe")
        res2 = run_gate_for_case("trap_java_to_swe")
        p1 = [c["candidate_id"] for c in res1["passed_candidates"]]
        p2 = [c["candidate_id"] for c in res2["passed_candidates"]]
        self.assertEqual(p1, p2)

    def test_14_unknown_reel_id_raises_error(self):
        """14. Unknown reel ID raises an error."""
        with self.assertRaises(Exception):
            run_gate_for_reels(["UNKNOWN_REEL_999"])

    def test_15_unknown_case_name_raises_error(self):
        """15. Unknown case name raises an error."""
        with self.assertRaises(ValueError):
            run_gate_for_case("invalid_case_foo")


if __name__ == "__main__":
    unittest.main()
