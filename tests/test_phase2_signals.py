"""Unit tests for ScrollSense Phase 2 signal extraction module."""

import unittest

from src.loaders import load_watched_reels
from src.signals import (
    extract_signal,
    generate_signals,
    load_signal_cache,
    validate_reel_signal,
)


class TestPhase2Signals(unittest.TestCase):
    def setUp(self):
        self.watched = load_watched_reels()
        self.watched_map = {r["reel_id"]: r for r in self.watched if "reel_id" in r}

    def test_01_extract_signal_valid_structure_for_all_reels(self):
        """1. extract_signal returns valid structure for every watched reel."""
        for reel in self.watched:
            sig = extract_signal(reel)
            self.assertIsInstance(sig, dict)
            # validate_reel_signal raises ValueError if invalid
            validate_reel_signal(sig)
            self.assertEqual(sig["reel_id"], reel["reel_id"])
            self.assertGreater(len(sig["interest_evidence"]), 0)

    def test_02_r1_contains_java_topic_exposure(self):
        """2. R1 contains java topic exposure (strength 0.5 - 0.8)."""
        sig = extract_signal(self.watched_map["R1"])
        ev = sig["interest_evidence"]
        java_ev = [
            e for e in ev if e["evidence_type"] == "topic_exposure" and e["value"] == "java"
        ]
        self.assertEqual(len(java_ev), 1)
        self.assertTrue(0.5 <= java_ev[0]["strength"] <= 0.8)

    def test_03_r1_does_not_produce_strong_swe_evidence(self):
        """3. R1 does not produce strong software_engineer evidence (strength <= 0.45)."""
        sig = extract_signal(self.watched_map["R1"])
        ev = sig["interest_evidence"]
        swe_ev = [
            e for e in ev
            if e["evidence_type"] == "professional_identity_signal" and e["value"] == "software_engineer"
        ]
        for item in swe_ev:
            self.assertLessEqual(item["strength"], 0.45)

    def test_04_r2_produces_strong_swe_evidence(self):
        """4. R2 produces strong software_engineer evidence (>= 0.75)."""
        sig = extract_signal(self.watched_map["R2"])
        ev = sig["interest_evidence"]
        swe_ev = [
            e for e in ev
            if e["evidence_type"] == "professional_identity_signal" and e["value"] == "software_engineer"
        ]
        self.assertTrue(len(swe_ev) > 0)
        self.assertGreaterEqual(swe_ev[0]["strength"], 0.75)

    def test_05_r3_produces_candidate_career_stage_evidence(self):
        """5. R3 produces candidate career_stage evidence (>= 0.7) and SWE identity (>= 0.6)."""
        sig = extract_signal(self.watched_map["R3"])
        ev = sig["interest_evidence"]
        cand_ev = [
            e for e in ev
            if e["evidence_type"] == "career_stage_signal" and e["value"] == "candidate"
        ]
        swe_ev = [
            e for e in ev
            if e["evidence_type"] == "professional_identity_signal" and e["value"] == "software_engineer"
        ]
        self.assertTrue(len(cand_ev) > 0)
        self.assertGreaterEqual(cand_ev[0]["strength"], 0.70)
        self.assertTrue(len(swe_ev) > 0)
        self.assertGreaterEqual(swe_ev[0]["strength"], 0.60)

    def test_06_r4_produces_developer_hardware_tooling_evidence(self):
        """6. R4 produces developer_hardware tooling evidence (>= 0.5)."""
        sig = extract_signal(self.watched_map["R4"])
        ev = sig["interest_evidence"]
        dev_hw = [
            e for e in ev
            if e["evidence_type"] == "tooling_signal" and e["value"] == "developer_hardware"
        ]
        self.assertTrue(len(dev_hw) > 0)
        self.assertGreaterEqual(dev_hw[0]["strength"], 0.50)

    def test_07_r5_produces_gaming_domain_evidence(self):
        """7. R5 produces gaming domain evidence (>= 0.75)."""
        sig = extract_signal(self.watched_map["R5"])
        ev = sig["interest_evidence"]
        gaming_ev = [
            e for e in ev if e["evidence_type"] == "domain_signal" and e["value"] == "gaming"
        ]
        self.assertTrue(len(gaming_ev) > 0)
        self.assertGreaterEqual(gaming_ev[0]["strength"], 0.75)

    def test_08_r6_produces_game_ai_skill_evidence(self):
        """8. R6 produces game_ai skill evidence (>= 0.65)."""
        sig = extract_signal(self.watched_map["R6"])
        ev = sig["interest_evidence"]
        game_ai = [
            e for e in ev if e["evidence_type"] == "skill_signal" and e["value"] == "game_ai"
        ]
        self.assertTrue(len(game_ai) > 0)
        self.assertGreaterEqual(game_ai[0]["strength"], 0.65)

    def test_09_r7_produces_gaming_hardware_tooling_evidence(self):
        """9. R7 produces gaming_hardware tooling evidence (>= 0.65)."""
        sig = extract_signal(self.watched_map["R7"])
        ev = sig["interest_evidence"]
        gh_ev = [
            e for e in ev
            if e["evidence_type"] == "tooling_signal" and e["value"] == "gaming_hardware"
        ]
        self.assertTrue(len(gh_ev) > 0)
        self.assertGreaterEqual(gh_ev[0]["strength"], 0.65)

    def test_10_gaming_reels_do_not_leak_swe_identity(self):
        """10. Gaming reels do not leak software_engineer identity (> 0.2), candidate stage, or career_prep."""
        for g_id in ["R5", "R6", "R7"]:
            sig = extract_signal(self.watched_map[g_id])
            ev = sig["interest_evidence"]
            for e in ev:
                if e["evidence_type"] == "professional_identity_signal" and e["value"] == "software_engineer":
                    self.assertLessEqual(e["strength"], 0.20, f"{g_id} leaked SWE identity with strength {e['strength']}")
                if e["evidence_type"] == "career_stage_signal":
                    self.assertNotEqual(e["value"], "candidate", f"{g_id} leaked candidate career stage")
                if e["evidence_type"] == "goal_signal":
                    self.assertNotEqual(e["value"], "career_prep", f"{g_id} leaked career_prep goal")

    def test_11_unknown_reel_id_raises_error(self):
        """11. Unknown reel ID raises an error."""
        with self.assertRaises(ValueError) as ctx:
            generate_signals(reel_ids=["R999"])
        self.assertIn("Unknown reel ID", str(ctx.exception))

    def test_12_signal_cache_can_be_regenerated(self):
        """12. Signal cache can be regenerated cleanly with force_refresh."""
        signals = generate_signals(force_refresh=True)
        self.assertEqual(len(signals), len(self.watched))
        cache_on_disk = load_signal_cache()
        self.assertEqual(len(cache_on_disk), len(self.watched))
        for r_id in self.watched_map:
            self.assertIn(r_id, cache_on_disk)
            self.assertIn("signal", cache_on_disk[r_id])


if __name__ == "__main__":
    unittest.main()
