#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from normative_full import load_full_contract

MIGRATIONS = ROOT / "standards" / "rule-migrations.json"
EXPECTED = {
    "font.size.reduced.illustration-caption": "illustration.identification.font-size",
    "font.size.reduced.table-caption": "table.identification.font-size",
}


def fail(message: str) -> None:
    raise SystemExit(f"Normative rule migration failed: {message}")


def main() -> None:
    data = json.loads(MIGRATIONS.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        fail("unsupported migration schema")
    rows = data.get("migrations")
    if not isinstance(rows, list) or len(rows) != 2:
        fail("object-title migration must contain exactly two rows")
    observed = {row.get("retired_id"): row.get("replacement_id") for row in rows}
    if observed != EXPECTED:
        fail(f"unexpected migration mapping: {observed}")

    rules = {rule["id"]: rule for rule in load_full_contract()["rules"]}
    for row in rows:
        retired = row["retired_id"]
        replacement = row["replacement_id"]
        if retired in rules:
            fail(f"retired rule remains active: {retired}")
        if replacement not in rules:
            fail(f"replacement rule is missing: {replacement}")
        if row.get("retired_value") != {"pt": 10}:
            fail(f"retired value provenance drifted: {retired}")
        if row.get("replacement_value") != {"pt": 12}:
            fail(f"replacement value provenance drifted: {replacement}")
        if rules[replacement].get("values") != {"pt": 12}:
            fail(f"active replacement value drifted: {replacement}")
        if row.get("status") != "semantic-correction":
            fail(f"migration status drifted: {retired}")
        if row.get("decision") != "docs/V3-OBJECT-TYPOGRAPHY-DECISION.md":
            fail(f"migration decision provenance drifted: {retired}")

    print("RULE-MIGRATION-EVIDENCE status=PASS retired=2 replacements=2 semantic_corrections=2")


if __name__ == "__main__":
    main()
