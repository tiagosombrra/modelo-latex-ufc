#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from normative_catalog import CatalogError, get_rule, load_catalog, validate_catalog


def fail(message: str) -> None:
    raise SystemExit(f"Normative precedence failed: {message}")


def expect_invalid(catalog: dict, label: str) -> None:
    try:
        validate_catalog(catalog)
    except CatalogError:
        return
    fail(f"{label}: invalid precedence was accepted")


def main() -> None:
    catalog = load_catalog()

    page = get_rule(catalog, "page.a4")
    if page["resolution"]["governing_sources"] != ["abnt-nbr-14724-2024"]:
        fail("page.a4 must be governed by the current NBR 14724 source")

    catalog_card = get_rule(catalog, "deposit.catalog-card")
    if catalog_card["resolution"]["governing_sources"] != ["ufc-in-2-2026"]:
        fail("catalog-card policy must be governed by the current UFC institutional act")

    epigraph = get_rule(catalog, "epigraph.short")
    if epigraph["resolution"]["governing_sources"] != ["ufc-guia-trabalhos-2022"]:
        fail("epigraph layout must be governed by the current UFC institutional requirement")
    if "abnt-nbr-10520-2023" not in epigraph["resolution"].get("constraint_sources", []):
        fail("epigraph citation behavior must remain constrained by current NBR 10520")

    precedence_path = ROOT / "normativa" / "precedence.json"
    precedence = json.loads(precedence_path.read_text(encoding="utf-8"))
    stale = copy.deepcopy(precedence)
    stale["reviewed_at"] = "2026-08-21"
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir) / "precedence.json"
        temp.write_text(json.dumps(stale), encoding="utf-8")
        try:
            load_catalog(ROOT / "normativa" / "catalog.json", temp)
        except CatalogError:
            pass
        else:
            fail("precedence older than catalog review was accepted")

    wrong_technical = copy.deepcopy(catalog)
    rule = next(item for item in wrong_technical["rules"] if item["id"] == "page.a4")
    rule["resolution"]["governing_sources"] = ["ufc-guia-trabalhos-2022"]
    rule["resolution"]["supporting_sources"] = ["abnt-nbr-14724-2024"]
    expect_invalid(wrong_technical, "current ABNT displaced by UFC guide")

    inactive = copy.deepcopy(catalog)
    source = next(item for item in inactive["sources"] if item["id"] == "ufc-guia-trabalhos-2022")
    source["status"] = "superseded"
    expect_invalid(inactive, "superseded source governs active rule")

    wrong_institutional = copy.deepcopy(catalog)
    rule = next(item for item in wrong_institutional["rules"] if item["id"] == "deposit.catalog-card")
    rule["sources"].append("ufc-normalizacao-2026")
    rule["resolution"]["governing_sources"] = ["ufc-normalizacao-2026"]
    rule["resolution"]["supporting_sources"] = ["ufc-in-2-2026"]
    expect_invalid(wrong_institutional, "institutional guidance displaced current institutional act")

    review = copy.deepcopy(catalog)
    rule = next(item for item in review["rules"] if item["id"] == "page.a4")
    rule["resolution"]["status"] = "review-required"
    validate_catalog(review)
    try:
        get_rule(review, "page.a4")
    except CatalogError:
        pass
    else:
        fail("review-required rule was exposed as resolved")

    print("Normative precedence passed: current technical and institutional authority is enforced.")


if __name__ == "__main__":
    main()
