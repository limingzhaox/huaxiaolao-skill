"""Regression cases for actual handoff failures; no renderer is exercised."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_plan", ROOT / "scripts/check_plan.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HandoffContract(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / "assets/episode-plan.example.json").read_text(encoding="utf-8"))
    def check(self, phase="handoff", root=None):
        return module.check(self.plan, root or ROOT / "assets", phase)[0]
    def test_planned_package_is_valid_plan_but_not_generated_art(self):
        self.assertEqual(self.check(), [])
        self.assertTrue(self.check("assets"))
    def test_gap_in_state_coverage_is_rejected(self):
        self.plan["scenes"][0]["states"][1]["start_frame"] += 1
        self.assertTrue(self.check())
    def test_overlap_in_state_coverage_is_rejected(self):
        self.plan["scenes"][0]["states"][1]["start_frame"] -= 1
        self.assertTrue(self.check())
    def test_missing_asset_reference_is_rejected(self):
        self.plan["scenes"][0]["states"][0]["asset_ids"] = ["missing"]
        self.assertTrue(self.check())
    def test_reaction_cannot_precede_trigger(self):
        self.plan["scenes"][0]["states"][0]["trigger_state_ids"] = ["S3-A"]
        self.assertTrue(self.check())
    def test_pending_fact_stays_draft(self):
        self.plan["claims"][0]["verification"] = "pending"
        self.plan["claims"][0]["sources"] = []
        self.assertEqual(self.check("plan"), [])
        self.assertTrue(self.check("handoff"))
    def test_source_without_locator_cannot_pass_handoff(self):
        self.plan["claims"][0]["sources"][0].pop("locator")
        self.assertTrue(self.check())
    def test_paths_cannot_escape_episode_directory(self):
        self.plan["assets"][0]["path"] = "../secret.png"
        self.assertTrue(self.check())
    def test_generated_status_requires_actual_file(self):
        for asset in self.plan["assets"]:
            asset["status"] = "generated"
        with tempfile.TemporaryDirectory() as folder:
            self.assertTrue(self.check("assets", Path(folder)))
            for asset in self.plan["assets"]:
                path = Path(folder) / asset["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"file-presence-test-only-not-art")
            self.assertEqual(self.check("assets", Path(folder)), [])


if __name__ == "__main__":
    unittest.main()
