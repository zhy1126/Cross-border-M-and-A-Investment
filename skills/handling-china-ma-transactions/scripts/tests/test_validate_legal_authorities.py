import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "references" / "legal-authorities.json"
VALIDATOR = ROOT / "scripts" / "validate_legal_authorities.py"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "registry_last_audited",
    "official_domain_allowlist",
    "coverage_topics",
    "coverage_matrix",
    "authorities",
}
REQUIRED_AUTHORITY_FIELDS = {
    "authority_id",
    "jurisdiction",
    "routes",
    "topics",
    "title",
    "authority_level",
    "issuer",
    "document_number",
    "published_date",
    "effective_date",
    "repealed_date",
    "status",
    "pinpoint",
    "proposition",
    "short_excerpt",
    "official_url",
    "last_verified",
    "supersedes",
    "superseded_by",
    "caveat",
}


class AuthorityIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(INDEX.read_text(encoding="utf-8"))

    def test_top_level_registry_fields_exist(self):
        self.assertFalse(REQUIRED_TOP_LEVEL - set(self.payload))

    def test_authority_records_are_unique_and_complete(self):
        records = self.payload["authorities"]
        ids = [record["authority_id"] for record in records]
        self.assertEqual(len(ids), len(set(ids)))
        for record in records:
            self.assertFalse(
                REQUIRED_AUTHORITY_FIELDS - set(record),
                f"missing fields in {record.get('authority_id')}",
            )

    def test_statuses_and_non_effective_caveats(self):
        allowed = {
            "effective",
            "not-yet-effective",
            "draft",
            "repealed",
            "status-unverified",
        }
        for record in self.payload["authorities"]:
            self.assertIn(record["status"], allowed)
            if record["status"] != "effective":
                self.assertTrue(record["caveat"].strip())

    def test_short_excerpts_are_non_empty(self):
        for record in self.payload["authorities"]:
            self.assertIsInstance(record["short_excerpt"], str, record["authority_id"])
            self.assertTrue(record["short_excerpt"].strip(), record["authority_id"])

    def test_export_control_coverage_and_core_authorities(self):
        topics = set(self.payload["coverage_topics"])
        self.assertTrue({"export-control", "technology-export"} <= topics)
        for route, covered in self.payload["coverage_matrix"].items():
            self.assertTrue(
                {"export-control", "technology-export"} <= set(covered),
                route,
            )

        records = {record["authority_id"]: record for record in self.payload["authorities"]}
        expected = {
            "PRC-EXPORT-CONTROL-LAW-2020": "export-control",
            "STATE-COUNCIL-DUAL-USE-EXPORT-CONTROL-2024": "export-control",
            "STATE-COUNCIL-TECHNOLOGY-IMPORT-EXPORT-REGULATION-2020": "technology-export",
            "MOFCOM-TECHNOLOGY-EXPORT-PROHIBITED-RESTRICTED-CATALOGUE-2023": "technology-export",
            "MOFCOM-TECHNOLOGY-EXPORT-CATALOGUE-ADJUSTMENT-2025": "technology-export",
        }
        for authority_id, topic in expected.items():
            self.assertIn(authority_id, records)
            self.assertIn(topic, records[authority_id]["topics"])
            self.assertEqual(records[authority_id]["status"], "effective")

        base = records[
            "MOFCOM-TECHNOLOGY-EXPORT-PROHIBITED-RESTRICTED-CATALOGUE-2023"
        ]
        adjustment = records["MOFCOM-TECHNOLOGY-EXPORT-CATALOGUE-ADJUSTMENT-2025"]
        self.assertIn(adjustment["authority_id"], base["superseded_by"])
        self.assertIn(base["authority_id"], adjustment["supersedes"])

    def test_official_urls_match_allowlist(self):
        domains = tuple(self.payload["official_domain_allowlist"])
        for record in self.payload["authorities"]:
            self.assertTrue(record["official_url"].startswith("https://"))
            self.assertTrue(
                any(f"//{domain}/" in record["official_url"] for domain in domains),
                record["authority_id"],
            )

    def test_validator_reports_no_errors(self):
        spec = importlib.util.spec_from_file_location("validator", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.validate_index(INDEX), [])

    def test_validator_rejects_empty_short_excerpt(self):
        spec = importlib.util.spec_from_file_location("validator_empty_excerpt", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        payload = json.loads(INDEX.read_text(encoding="utf-8"))
        payload["authorities"][0]["short_excerpt"] = "  "
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legal-authorities.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            errors = module.validate_index(path)
        self.assertIn(
            "PRC-COMPANY-LAW-2023: short_excerpt must be a non-empty string",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
