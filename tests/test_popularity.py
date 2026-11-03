import copy
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("popularity", ROOT / "tools/update-popularity.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BASE = "c8a39aafd55200f7f9b8635c4702af5992fbff4a"

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class PopularityTests(unittest.TestCase):
    def setUp(self):
        self.index = read("api/v1/terminal/index.json")
        self.snapshot = read("metadata/gogh-popular.json")

    def test_reproducible_exact_membership_and_order(self):
        result = module.build(self.index, self.snapshot)
        self.assertEqual(result, self.index["popularity"])
        names = {r["id"]: r["name"] for r in self.index["entries"]}
        self.assertEqual([names[i] for i in result["order"]], self.snapshot["names"])
        self.assertEqual(sum(result["flags"].values()), 48)
        self.assertEqual(len(result["flags"]), 1251)
        self.assertEqual(result["unmatched"], [])
        self.assertEqual(result["unavailable"], [])

    def test_existing_index_fields_unchanged(self):
        old = json.loads(subprocess.check_output(["git", "show", f"{BASE}:api/v1/terminal/index.json"], cwd=ROOT))
        current = copy.deepcopy(self.index)
        current.pop("popularity")
        self.assertEqual(current, old)

    def test_no_editor_classification_or_withheld_flags(self):
        self.assertNotIn("popularity", read("api/v1/editor/index.json"))
        self.assertEqual(len(self.index["excluded"]), 112)
        for row in self.index["excluded"]:
            self.assertNotIn(row["id"], self.index["popularity"]["flags"])
            self.assertNotIn("path", row)

    def test_absent_ambiguous_and_withheld_are_explicit(self):
        name = self.snapshot["names"][0]
        item = next(r for r in self.index["entries"] if r["name"] == name)
        self.index["entries"].remove(item)
        result = module.build(self.index, self.snapshot)
        self.assertEqual(result["unmatched"][0], {"name": name, "position": 1, "reason": "absent"})
        self.index["excluded"].append(dict(item, reason="distribution-license-unverified"))
        result = module.build(self.index, self.snapshot)
        self.assertEqual(result["unavailable"][0]["id"], item["id"])
        duplicate = dict(item, id="gogh/ambiguous")
        self.index["entries"].append(duplicate)
        result = module.build(self.index, self.snapshot)
        self.assertEqual(result["unmatched"][0]["reason"], "ambiguous")
        self.assertNotIn(item["id"], result["flags"])
        self.assertNotIn(duplicate["id"], result["flags"])

    def test_pinned_source_rejects_unreviewed_source(self):
        with self.assertRaises(ValueError):
            module.extract("const POPULAR_THEME_NAMES = new Set(['Fake']);")

if __name__ == "__main__":
    unittest.main()
