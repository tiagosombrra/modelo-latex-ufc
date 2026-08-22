#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "normativa" / "source-audit.json"
CATALOG = ROOT / "normativa" / "catalog.json"


def fail(message: str) -> None:
    raise SystemExit(f"Normative source audit failed: {message}")


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    if audit.get("schema_version") != 1:
        fail("unsupported schema_version")
    if audit.get("scope") != "ufctex-v2.1.0-current-sources":
        fail("unexpected audit scope")

    reviewed = date.fromisoformat(audit["reviewed_at"])
    sources = audit.get("sources")
    if not isinstance(sources, list) or not sources:
        fail("sources must be a non-empty list")

    by_id = {}
    for source in sources:
        source_id = source.get("id")
        if not source_id or source_id in by_id:
            fail(f"invalid or duplicate source id: {source_id}")
        by_id[source_id] = source
        for field in ("kind", "title", "publisher", "status", "checked_at"):
            if not source.get(field):
                fail(f"source {source_id}: missing {field}")
        if date.fromisoformat(source["checked_at"]) > reviewed:
            fail(f"source {source_id}: checked after audit review date")
        if source["status"] in {"superseded", "historical"}:
            fail(f"legacy source must not remain in current inventory: {source_id}")

    catalog_ids = {source["id"] for source in catalog["sources"]}
    missing = sorted(catalog_ids - set(by_id))
    if missing:
        fail("runtime catalog sources missing from N2 inventory: " + ", ".join(missing))

    expected_technical = {
        "abnt-nbr-14724-2024",
        "abnt-nbr-10520-2023",
        "abnt-nbr-6023-2025",
        "abnt-nbr-15287-2025",
        "abnt-nbr-6028-2021",
        "abnt-nbr-6024-2012",
        "abnt-nbr-6027-2012",
        "abnt-nbr-6034-2004",
        "abnt-nbr-12225-2023",
    }
    if set(audit.get("current_technical_sources", [])) != expected_technical:
        fail("current technical standard set changed without N2 review")

    institutional_guides = {
        "ufc-guia-trabalhos-2022",
        "ufc-guia-citacoes-2025",
        "ufc-guia-referencias-2023",
        "ufc-guia-projetos-2019",
    }
    for source_id in institutional_guides:
        source = by_id.get(source_id)
        if not source:
            fail(f"missing current UFC guide: {source_id}")
        if source.get("status") != "current-institutional-with-stale-technical-citations":
            fail(f"UFC guide must be restricted from technical edition authority: {source_id}")
        if source.get("technical_authority") is not False:
            fail(f"UFC guide cannot define the active ABNT edition: {source_id}")

    in_2024 = by_id.get("ufc-in-2-2024")
    in_2026 = by_id.get("ufc-in-2-2026")
    if not in_2024 or not in_2026:
        fail("current UFC deposit instructions are incomplete")
    if in_2024.get("status") != "current-with-superseded-provisions":
        fail("IN 2/2024 must record partial supersession")
    overrides = in_2026.get("overrides", [])
    if not any(item.get("source") == "ufc-in-2-2024" and item.get("scope") == "visual-catalog-card-requirement" for item in overrides):
        fail("IN 2/2026 must explicitly override the old visual catalog-card requirement")

    required_ufc = {
        "ufc-res-17-cepe-2017",
        "ufc-res-05-consuni-2023",
        "ufc-in-2-2024",
        "ufc-in-2-2026",
        "ufc-deposito-tcc-2026",
        "ufc-deposito-pos-2026",
        "ufc-ficha-catalografica-2026",
    }
    missing_ufc = sorted(required_ufc - set(by_id))
    if missing_ufc:
        fail("missing current UFC institutional sources: " + ", ".join(missing_ufc))

    forbidden_ids = {
        "abnt-nbr-14724-2011",
        "abnt-nbr-10520-2002",
        "abnt-nbr-6023-2018",
        "abnt-nbr-15287-2011",
        "abnt-nbr-12225-2004",
    }
    leaked = sorted(forbidden_ids & set(by_id))
    if leaked:
        fail("superseded ABNT sources retained as active inventory entries: " + ", ".join(leaked))

    print(
        "Normative source audit passed: "
        f"{len(sources)} current/restricted sources, "
        f"{len(expected_technical)} current ABNT standards, "
        f"{len(institutional_guides)} UFC guides restricted from edition authority."
    )


if __name__ == "__main__":
    main()
