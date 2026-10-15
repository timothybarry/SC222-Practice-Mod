"""Regression checks for the Galaxy syntax failure and the working recovery map."""

from pathlib import Path
import hashlib
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_map
from validate_galaxy import validate


class RecoveryTests(unittest.TestCase):
    def test_galaxy_array_syntax(self):
        self.assertIn("PASS", validate(self_test=True))

    def test_bad_syntax_cannot_replace_the_playable_map(self):
        paths = [build_map.MAP / "Triggers", build_map.MAP / "MapScript.galaxy"]
        before = [hashlib.sha256(path.read_bytes()).digest() for path in paths]
        with patch.object(build_map, "source_code", return_value="int broken[3];"):
            with self.assertRaises(ValueError):
                build_map.build()
        self.assertEqual(before, [hashlib.sha256(path.read_bytes()).digest() for path in paths])

    def test_authored_and_editor_scripts_agree(self):
        source = build_map.source_code()
        self.assertIn(source, (build_map.MAP / "MapScript.galaxy").read_text(encoding="utf-8"))
        embedded = ET.parse(build_map.MAP / "Triggers").find("./Element[@Type='CustomScript']/ScriptCode").text
        self.assertEqual(embedded.strip(), source.strip())


if __name__ == "__main__":
    unittest.main()
