"""Relocation and evidence-integrity checks, independent of installed location."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_package", ROOT / "scripts/check_package.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PortablePackage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.copy = Path(self.temp.name) / "different-root" / "huaxiaolao-skill"
        shutil.copytree(ROOT, self.copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    def tearDown(self):
        self.temp.cleanup()
    def test_relocated_package_links_and_images(self):
        result = module.check(self.copy)
        self.assertEqual(result["errors"], [])
    def test_evidence_change_is_detected(self):
        path = self.copy / "references/evidence/peanut-F000417.jpg"
        path.write_bytes(path.read_bytes() + b"modified")
        self.assertFalse(module.check(self.copy)["pass"])
    def test_missing_reference_is_detected(self):
        (self.copy / "references/drawing-states.md").unlink()
        self.assertFalse(module.check(self.copy)["pass"])


if __name__ == "__main__":
    unittest.main()
