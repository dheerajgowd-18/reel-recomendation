"""Unit tests for ScrollSense Phase 3 inference, InterestState aggregation, and graph traversal."""

import unittest
from pathlib import Path

from src.graph import select_seed_nodes, traverse_identity_graph
from src.infer import determine_confidence, generate_inferred_interest_label, infer_interests, run_all_checkpoints
from src.persona import aggregate_interest_state
from src.signals import generate_signals


class TestPhase3Inference(unittest.TestCase):
    def setUp(self):
        self.all_signals = generate_signals()

    def test_01_aggregate_interest_state_valid_schema(self):
        """1. aggregate_interest_state produces valid schema with required fields."""
        signals = [self.all_signals["R1"], self.all_signals["R2"]]
        state = aggregate_interest_state(signals)
        required_keys = [
            "student_id",
            "session_id",
            "reel_ids",
            "professional_identity",
            "career_stage",
            "domains",
            "goals",
            "depth",
            "content_preference",
            "evidence",
            "updated_at",
        ]
        for key in required_keys:
            self.assertIn(key, state)
        self.assertEqual(state["reel_ids"], ["R1", "R2"])

    def test_02_r1_alone_inference(self):
        """2. R1 produces weak SWE identity (<= 0.45) and Low confidence."""
        res = infer_interests(["R1"])
        self.assertEqual(res["confidence"], "Low")
        swe = res["interest_state"]["professional_identity"].get("software_engineer", 0.0)
        self.assertLessEqual(swe, 0.45)
        self.assertIn("Programming humor", res["inferred_interest_label"])

    def test_03_r1_r2_inference(self):
        """3. R1+R2 produces Medium confidence and meaningful SWE identity (>= 0.75)."""
        res = infer_interests(["R1", "R2"])
        self.assertEqual(res["confidence"], "Medium")
        swe = res["interest_state"]["professional_identity"].get("software_engineer", 0.0)
        self.assertGreaterEqual(swe, 0.75)

    def test_04_r1_r2_r3_inference(self):
        """4. R1+R2+R3 produces High confidence, candidate stage >= 0.70, and SWE identity >= 0.85."""
        res = infer_interests(["R1", "R2", "R3"])
        self.assertEqual(res["confidence"], "High")
        swe = res["interest_state"]["professional_identity"].get("software_engineer", 0.0)
        cand = res["interest_state"]["career_stage"].get("candidate", 0.0)
        self.assertGreaterEqual(swe, 0.85)
        self.assertGreaterEqual(cand, 0.70)

    def test_05_final_trap_case_and_graph_traversal(self):
        """5. Final trap case produces High confidence and activates SWE competency nodes."""
        res = infer_interests(["R1", "R2", "R3", "R4"], case_name="trap_java_to_swe")
        self.assertEqual(res["confidence"], "High")
        swe = res["interest_state"]["professional_identity"].get("software_engineer", 0.0)
        self.assertGreaterEqual(swe, 0.85)

        activated_nodes = {a["node"] for a in res["graph_traversal"]["activated_nodes"]}
        for node in ["career", "git", "debugging", "system_design", "dsa", "cloud"]:
            self.assertIn(node, activated_nodes, f"Node {node} should be activated for trap case")

    def test_06_gaming_non_trap_case_isolation(self):
        """6. Gaming non-trap case produces Medium confidence, gaming domain >= 0.75, no SWE identity."""
        res = infer_interests(["R5", "R6", "R7"], case_name="non_trap_gaming_only")
        self.assertEqual(res["confidence"], "Medium")
        gaming_dom = res["interest_state"]["domains"].get("gaming", 0.0)
        self.assertGreaterEqual(gaming_dom, 0.75)

        swe_ident = res["interest_state"]["professional_identity"].get("software_engineer", 0.0)
        cand_stage = res["interest_state"]["career_stage"].get("candidate", 0.0)
        self.assertLessEqual(swe_ident, 0.20)
        self.assertEqual(cand_stage, 0.0)

    def test_07_gaming_graph_traversal_activations(self):
        """7. Gaming graph traversal activates gaming nodes without activating software_engineer."""
        res = infer_interests(["R5", "R6", "R7"])
        activated_nodes = {a["node"] for a in res["graph_traversal"]["activated_nodes"]}
        for g_node in ["game_development", "graphics", "game_ai", "game_developer"]:
            self.assertIn(g_node, activated_nodes, f"Node {g_node} should be activated for gaming")
        self.assertNotIn("software_engineer", activated_nodes)

    def test_08_confidence_sequence_is_non_decreasing(self):
        """8. Confidence progression is strictly non-decreasing across trap sequence."""
        c1 = infer_interests(["R1"])["confidence"]
        c2 = infer_interests(["R1", "R2"])["confidence"]
        c3 = infer_interests(["R1", "R2", "R3"])["confidence"]
        c4 = infer_interests(["R1", "R2", "R3", "R4"])["confidence"]

        c_map = {"Low": 0, "Medium": 1, "High": 2}
        self.assertLessEqual(c_map[c1], c_map[c2])
        self.assertLessEqual(c_map[c2], c_map[c3])
        self.assertLessEqual(c_map[c3], c_map[c4])

    def test_09_gaming_label_does_not_mention_swe(self):
        """9. Inferred interest label for gaming mentions gaming and does not mention software engineering."""
        res = infer_interests(["R5", "R6", "R7"])
        label = res["inferred_interest_label"].lower()
        self.assertIn("gaming", label)
        self.assertNotIn("software engineer", label)

    def test_10_trap_label_mentions_software_engineering(self):
        """10. Inferred interest label for trap case mentions software engineering and career prep."""
        res = infer_interests(["R1", "R2", "R3", "R4"])
        label = res["inferred_interest_label"].lower()
        self.assertIn("software engineering", label)
        self.assertIn("career preparation", label)

    def test_11_empty_reels_raises_value_error(self):
        """11. infer_interests raises error for empty reel IDs."""
        with self.assertRaises(ValueError):
            infer_interests([])

    def test_12_run_all_checkpoints_contains_all_cases(self):
        """12. run_all_checkpoints returns all 5 standard checkpoint keys."""
        all_res = run_all_checkpoints()
        for expected_key in [
            "trap_after_R1",
            "trap_after_R1_R2",
            "trap_after_R1_R2_R3",
            "trap_after_R1_R2_R3_R4",
            "non_trap_gaming_only",
        ]:
            self.assertIn(expected_key, all_res)
            self.assertEqual(all_res[expected_key]["phase"], "phase_3_inference")


if __name__ == "__main__":
    unittest.main()
