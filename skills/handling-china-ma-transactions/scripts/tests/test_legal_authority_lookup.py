import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "legal_authority_lookup.py"


class LookupTests(unittest.TestCase):
    def run_lookup(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_effective_merger_control_records_exclude_other_statuses(self):
        result = self.run_lookup(
            "--topic", "merger-control", "--status", "effective", "--json"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        self.assertTrue(records)
        self.assertTrue(all(item["status"] == "effective" for item in records))

    def test_effective_only_never_returns_drafts(self):
        result = self.run_lookup("--topic", "listed-issuance", "--effective-only", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        self.assertTrue(records)
        self.assertTrue(all(item["status"] == "effective" for item in records))

    def test_route_filter_is_stable(self):
        result = self.run_lookup("--route", "L-CONTROL", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        self.assertTrue(records)
        self.assertTrue(all("L-CONTROL" in item["routes"] for item in records))

    def test_as_of_excludes_later_instruments(self):
        result = self.run_lookup("--topic", "company-law", "--as-of", "2022-12-31", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        self.assertTrue(records)
        self.assertNotIn("PRC-COMPANY-LAW-2023", {item["authority_id"] for item in records})
        historical = next(
            item for item in records if item["authority_id"] == "PRC-COMPANY-LAW-2018"
        )
        self.assertEqual(historical["status"], "repealed")
        self.assertEqual(historical["status_as_of"], "effective")

    def test_as_of_future_activates_published_not_yet_effective_instrument(self):
        result = self.run_lookup(
            "--topic", "intellectual-property", "--as-of", "2027-01-02", "--json"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        ids = {item["authority_id"] for item in records}
        self.assertIn("PRC-TRADEMARK-LAW-2026", ids)
        self.assertNotIn("PRC-TRADEMARK-LAW-2019", ids)
        current = next(
            item for item in records if item["authority_id"] == "PRC-TRADEMARK-LAW-2026"
        )
        self.assertEqual(current["status"], "not-yet-effective")
        self.assertEqual(current["status_as_of"], "effective")

    def test_as_of_status_filter_uses_computed_status(self):
        result = self.run_lookup(
            "--id",
            "PRC-TRADEMARK-LAW-2026",
            "--as-of",
            "2027-01-02",
            "--status",
            "effective",
            "--json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status_as_of"], "effective")

    def test_unknown_topic_returns_nonzero_with_available_topics(self):
        result = self.run_lookup("--topic", "not-a-topic")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Available topics", result.stderr)


if __name__ == "__main__":
    unittest.main()
