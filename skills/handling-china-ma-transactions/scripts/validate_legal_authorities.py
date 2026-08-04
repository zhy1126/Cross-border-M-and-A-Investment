#!/usr/bin/env python3
"""Validate the structured PRC M&A legal-authority registry."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable, List, Optional
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "references" / "legal-authorities.json"

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
ALLOWED_STATUSES = {
    "effective",
    "not-yet-effective",
    "draft",
    "repealed",
    "status-unverified",
}
ALLOWED_ROUTES = {"L-CONTROL", "P-EQUITY", "P-ASSET"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(value: Any, field: str, authority_id: str, errors: List[str]) -> Optional[date]:
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        errors.append(f"{authority_id}: {field} must be YYYY-MM-DD or null")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{authority_id}: {field} is not a valid calendar date")
        return None


def _as_string_list(value: Any, field: str, authority_id: str, errors: List[str]) -> List[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"{authority_id}: {field} must be a list of non-empty strings")
        return []
    return value


def _host_is_allowed(url: str, allowlist: Iterable[str]) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    return any(hostname == domain.lower() for domain in allowlist)


def validate_index(path: Path = DEFAULT_INDEX) -> List[str]:
    """Return all registry errors. An empty list means the registry is valid."""

    errors: List[str] = []
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"index does not exist: {path}"]
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]

    if not isinstance(payload, dict):
        return ["top level must be an object"]

    missing_top = REQUIRED_TOP_LEVEL - set(payload)
    if missing_top:
        errors.append(f"missing top-level fields: {', '.join(sorted(missing_top))}")

    allowlist = payload.get("official_domain_allowlist", [])
    topics = payload.get("coverage_topics", [])
    matrix = payload.get("coverage_matrix", {})
    records = payload.get("authorities", [])

    if not isinstance(allowlist, list) or not allowlist or any(
        not isinstance(item, str) or not item for item in allowlist
    ):
        errors.append("official_domain_allowlist must be a non-empty string list")
        allowlist = []
    if not isinstance(topics, list) or not topics or any(
        not isinstance(item, str) or not item for item in topics
    ):
        errors.append("coverage_topics must be a non-empty string list")
        topics = []
    if len(topics) != len(set(topics)):
        errors.append("coverage_topics contains duplicates")
    if not isinstance(matrix, dict):
        errors.append("coverage_matrix must be an object")
        matrix = {}
    if not isinstance(records, list) or not records:
        errors.append("authorities must be a non-empty list")
        records = []

    audit_date = _parse_date(
        payload.get("registry_last_audited"),
        "registry_last_audited",
        "registry",
        errors,
    )

    seen_ids = set()
    all_ids = set()
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("authority_id"), str):
            all_ids.add(record["authority_id"])

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"record[{index}] must be an object")
            continue
        authority_id = record.get("authority_id") or f"record[{index}]"
        missing = REQUIRED_AUTHORITY_FIELDS - set(record)
        if missing:
            errors.append(f"{authority_id}: missing fields: {', '.join(sorted(missing))}")
            continue

        if not isinstance(record["authority_id"], str) or not record["authority_id"].strip():
            errors.append(f"{authority_id}: authority_id must be a non-empty string")
        elif record["authority_id"] in seen_ids:
            errors.append(f"{authority_id}: duplicate authority_id")
        else:
            seen_ids.add(record["authority_id"])

        for field in (
            "jurisdiction",
            "title",
            "authority_level",
            "issuer",
            "document_number",
            "pinpoint",
            "proposition",
            "short_excerpt",
            "official_url",
            "last_verified",
            "caveat",
        ):
            if not isinstance(record[field], str) or not record[field].strip():
                errors.append(f"{authority_id}: {field} must be a non-empty string")

        routes = _as_string_list(record["routes"], "routes", authority_id, errors)
        unknown_routes = set(routes) - ALLOWED_ROUTES
        if unknown_routes:
            errors.append(f"{authority_id}: unknown routes: {', '.join(sorted(unknown_routes))}")
        record_topics = _as_string_list(record["topics"], "topics", authority_id, errors)
        unknown_topics = set(record_topics) - set(topics)
        if unknown_topics:
            errors.append(f"{authority_id}: undeclared topics: {', '.join(sorted(unknown_topics))}")

        status = record["status"]
        if status not in ALLOWED_STATUSES:
            errors.append(f"{authority_id}: invalid status {status!r}")
        if status != "effective" and not record["caveat"].strip():
            errors.append(f"{authority_id}: non-effective records require a caveat")

        published = _parse_date(record["published_date"], "published_date", authority_id, errors)
        effective = _parse_date(record["effective_date"], "effective_date", authority_id, errors)
        repealed = _parse_date(record["repealed_date"], "repealed_date", authority_id, errors)
        verified = _parse_date(record["last_verified"], "last_verified", authority_id, errors)

        if published and effective and effective < published:
            errors.append(f"{authority_id}: effective_date precedes published_date")
        if effective and repealed and repealed <= effective:
            errors.append(f"{authority_id}: repealed_date must follow effective_date")
        if audit_date and verified and verified > audit_date:
            errors.append(f"{authority_id}: last_verified is after registry_last_audited")
        if status == "effective":
            if not effective:
                errors.append(f"{authority_id}: effective record requires effective_date")
            if audit_date and effective and effective > audit_date:
                errors.append(f"{authority_id}: effective record starts after audit date")
            if audit_date and repealed and repealed <= audit_date:
                errors.append(f"{authority_id}: effective record was already repealed")
        elif status == "not-yet-effective":
            if not effective:
                errors.append(f"{authority_id}: not-yet-effective record requires effective_date")
            elif audit_date and effective <= audit_date:
                errors.append(f"{authority_id}: not-yet-effective date is not after audit date")
        elif status == "draft" and effective:
            errors.append(f"{authority_id}: draft must not assert an effective_date")
        elif status == "repealed":
            if not effective or not repealed:
                errors.append(f"{authority_id}: repealed record requires effective and repealed dates")

        url = record["official_url"]
        if isinstance(url, str):
            if not url.startswith("https://"):
                errors.append(f"{authority_id}: official_url must use https")
            elif allowlist and not _host_is_allowed(url, allowlist):
                errors.append(f"{authority_id}: official_url host is not allowlisted")

        for relation in ("supersedes", "superseded_by"):
            related = _as_string_list(record[relation], relation, authority_id, errors)
            for related_id in related:
                if related_id not in all_ids:
                    errors.append(f"{authority_id}: {relation} references unknown id {related_id}")

        if re.search(r"\d", record["proposition"]):
            if not re.search(r"第.+条|Article|条、|章|附件|第.+项", record["pinpoint"]):
                errors.append(f"{authority_id}: numerical proposition lacks a provision-level pinpoint")
            if not record["caveat"].strip():
                errors.append(f"{authority_id}: numerical proposition requires a caveat")

    for route in ALLOWED_ROUTES:
        covered = matrix.get(route)
        if not isinstance(covered, list) or not covered:
            errors.append(f"coverage_matrix.{route} must be a non-empty topic list")
            continue
        unknown = set(covered) - set(topics)
        if unknown:
            errors.append(f"coverage_matrix.{route} has undeclared topics: {', '.join(sorted(unknown))}")

    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--json", action="store_true", help="emit machine-readable results")
    args = parser.parse_args(argv)
    errors = validate_index(args.path)
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print(f"OK: {args.path}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
