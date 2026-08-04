#!/usr/bin/env python3
"""Query the structured PRC M&A legal-authority registry."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "legal-authorities.json"
ALLOWED_STATUSES = {
    "effective",
    "not-yet-effective",
    "draft",
    "repealed",
    "status-unverified",
}


def _load() -> Dict[str, Any]:
    try:
        return json.loads(INDEX.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot load authority index: {exc}", file=sys.stderr)
        raise SystemExit(1)


def _parse_iso(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        print(f"Invalid {label}: {value!r}; expected YYYY-MM-DD", file=sys.stderr)
        raise SystemExit(2)


def _unknown(label: str, value: str, available: List[str]) -> None:
    print(f"Unknown {label}: {value}", file=sys.stderr)
    plural = {"ID": "IDs", "status": "statuses"}.get(label, f"{label}s")
    print(f"Available {plural}: {', '.join(available)}", file=sys.stderr)
    raise SystemExit(2)


def _status_on(record: Dict[str, Any], as_of: date) -> str:
    """Return the instrument's computed status on a requested date.

    The registry ``status`` is the status at ``registry_last_audited``. Keep it
    unchanged for auditability and expose this separate value for historical or
    future as-of queries.
    """

    if record.get("status") in {"draft", "status-unverified"}:
        return record["status"]
    effective_text = record.get("effective_date")
    if not effective_text:
        return record.get("status", "status-unverified")
    effective = date.fromisoformat(effective_text)
    if effective > as_of:
        return "not-yet-effective"
    repealed_text = record.get("repealed_date")
    if repealed_text and as_of >= date.fromisoformat(repealed_text):
        return "repealed"
    return "effective"


def _effective_on(record: Dict[str, Any], as_of: date) -> bool:
    return _status_on(record, as_of) == "effective"


def _official(record: Dict[str, Any], allowlist: List[str]) -> bool:
    hostname = (urlparse(record.get("official_url", "")).hostname or "").lower()
    return record.get("official_url", "").startswith("https://") and hostname in {
        item.lower() for item in allowlist
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", dest="authority_id")
    parser.add_argument("--route")
    parser.add_argument("--topic")
    parser.add_argument("--status")
    parser.add_argument("--as-of", dest="as_of")
    parser.add_argument("--effective-only", action="store_true")
    parser.add_argument("--official-only", action="store_true")
    parser.add_argument("--freshness-days", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = _load()
    records = list(payload["authorities"])
    available_ids = sorted(item["authority_id"] for item in records)
    available_routes = sorted({route for item in records for route in item["routes"]})
    available_topics = sorted(payload["coverage_topics"])
    available_statuses = sorted(ALLOWED_STATUSES)

    if args.authority_id and args.authority_id not in available_ids:
        _unknown("ID", args.authority_id, available_ids)
    if args.route and args.route not in available_routes:
        _unknown("route", args.route, available_routes)
    if args.topic and args.topic not in available_topics:
        _unknown("topic", args.topic, available_topics)
    if args.status and args.status not in ALLOWED_STATUSES:
        _unknown("status", args.status, available_statuses)
    if args.freshness_days is not None and args.freshness_days < 0:
        print("--freshness-days must be zero or greater", file=sys.stderr)
        return 2

    if args.authority_id:
        records = [item for item in records if item["authority_id"] == args.authority_id]
    if args.route:
        records = [item for item in records if args.route in item["routes"]]
    if args.topic:
        records = [item for item in records if args.topic in item["topics"]]
    as_of = _parse_iso(args.as_of, "--as-of") if args.as_of else None
    if args.as_of:
        records = [
            {**item, "status_as_of": _status_on(item, as_of)}
            for item in records
            if _effective_on(item, as_of)
        ]
    if args.status:
        status_field = "status_as_of" if as_of else "status"
        records = [item for item in records if item[status_field] == args.status]
    if args.effective_only and not as_of:
        records = [item for item in records if item["status"] == "effective"]
    if args.official_only:
        records = [
            item for item in records if _official(item, payload["official_domain_allowlist"])
        ]
    if args.freshness_days is not None:
        anchor = date.today()
        records = [
            item
            for item in records
            if (anchor - date.fromisoformat(item["last_verified"])).days
            <= args.freshness_days
        ]

    records.sort(key=lambda item: (item["authority_id"], item["published_date"]))
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        for item in records:
            display_status = item.get("status_as_of", item["status"])
            print(
                f"{item['authority_id']}\t{display_status}\t{item['title']}\t"
                f"{item['pinpoint']}\t{item['official_url']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
