"""Unit tests for Phase 9B: Local Live Demo UI server and API contracts."""

import unittest
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from ui.server import app

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPhase9UI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_ui_server_starts(self):
        """1. UI server starts and responds."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)

    def test_02_get_root_returns_html(self):
        """2. GET / returns HTML content."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("<title>ScrollSense Live Demo UI</title>", res.text)

    def test_03_get_health_returns_ok(self):
        """3. GET /api/health returns OK."""
        res = self.client.get("/api/health")
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["pipeline"], "ready")

    def test_04_get_cases_returns_cases(self):
        """4. GET /api/cases returns valid cases."""
        res = self.client.get("/api/cases")
        data = res.json()
        self.assertIn("trap_java_to_swe", data)
        self.assertIn("non_trap_gaming_only", data)

    def test_05_post_run_works_for_trap(self):
        """5. POST /api/run works for trap_java_to_swe."""
        res = self.client.post("/api/run", json={"case": "trap_java_to_swe", "run_baselines": True})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["case"], "trap_java_to_swe")

    def test_06_post_run_works_for_gaming(self):
        """6. POST /api/run works for non_trap_gaming_only."""
        res = self.client.post("/api/run", json={"case": "non_trap_gaming_only", "run_baselines": True})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["case"], "non_trap_gaming_only")

    def test_07_final_trap_recommends_t1(self):
        """7. Final trap result recommends T1."""
        res = self.client.post("/api/run", json={"case": "trap_java_to_swe"})
        data = res.json()
        self.assertEqual(data["scrollsense"]["recommended_candidate_id"], "T1")

    def test_08_gaming_recommends_t24(self):
        """8. Gaming result recommends T24."""
        res = self.client.post("/api/run", json={"case": "non_trap_gaming_only"})
        data = res.json()
        self.assertEqual(data["scrollsense"]["recommended_candidate_id"], "T24")

    def test_09_t99_appears_in_gate_rejections(self):
        """9. T99 appears in gate rejections for final trap."""
        res = self.client.post("/api/run", json={"case": "trap_java_to_swe"})
        data = res.json()
        rejs = [r["candidate_id"] for r in data["scrollsense"]["gate_rejections"]]
        self.assertIn("T99", rejs)

    def test_10_baselines_present_when_requested(self):
        """10. Baselines are present when run_baselines=true."""
        res = self.client.post("/api/run", json={"case": "trap_java_to_swe", "run_baselines": True})
        data = res.json()
        self.assertIn("topic_only", data["baselines"])
        self.assertIn("keyword_similarity", data["baselines"])

    def test_11_ui_does_not_require_live_llm(self):
        """11. UI execution runs offline using cached mode."""
        res = self.client.post("/api/run", json={"case": "trap_java_to_swe", "llm_provider": "cache"})
        self.assertEqual(res.status_code, 200)

    def test_12_ui_does_not_reference_external_cdns(self):
        """12. UI does not reference external CDN URLs in HTML."""
        index_path = PROJECT_ROOT / "ui" / "static" / "index.html"
        html = index_path.read_text(encoding="utf-8")
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)

    def test_13_ai_status_panel_data_present(self):
        """13. AI status panel data is present in response."""
        res = self.client.post("/api/run", json={"case": "trap_java_to_swe"})
        data = res.json()
        ai_data = data["scrollsense"].get("ai", {})
        self.assertIn("model", ai_data)
        self.assertIn("llm_status", ai_data)
        self.assertEqual(ai_data["model"], "nvidia/nemotron-3.5-lightning-30b-a3b")

    def test_14_cached_ai_mode_works_without_api_key(self):
        """14. Cached AI mode works cleanly without an API key."""
        res = self.client.post("/api/run", json={"case": "trap_java_to_swe", "llm_provider": "cache"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["scrollsense"]["ai"]["llm_provider"], "cache")


if __name__ == "__main__":
    unittest.main()
