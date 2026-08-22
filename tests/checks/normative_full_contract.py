#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from normative_catalog import load_catalog
from normative_full import full_rule_map, load_full_contract


def fail(message: str) -> None:
    raise SystemExit(f"Full normative contract failed: {message}")


def main() -> None:
    catalog = load_catalog()
    contract = load_full_contract(catalog)
    rules = full_rule_map(contract)

    if contract["n3_rule_count"] != 100:
        fail(f"expected 100 certified N3 atomic rules, got {contract['n3_rule_count']}")
    if len(rules) != contract["n3_rule_count"] + len(contract["promoted_rule_ids"]):
        fail("full contract count is inconsistent with N3 + N4 promotions")
    if len(contract["promoted_rule_ids"]) < 23:
        fail("N4 contract lost the certified first promotion block")
    if "project.standard" in rules:
        fail("retired project.standard umbrella returned to the active contract")

    expected = {
        "pagination.pretextual.counted-not-numbered": {"counted": True, "number_visible": False},
        "pagination.catalog-data.not-counted": {"counted": False, "number_visible": False},
        "pagination.recto.position": {"position": "upper-right"},
        "pagination.verso.position": {"position": "upper-left"},
        "footnote.line-spacing": {"factor": 1.0},
        "footnote.separator.length": {"length_mm": 50, "origin": "left-margin"},
        "footnote.hanging-alignment": {"enabled": True},
        "section.indicator.alignment": {"alignment": "left"},
        "section.indicator.separator": {"separator": "single-character-space"},
        "section.primary.recto-duplex": {"start_side": "recto"},
        "section.multiline.hanging": {"enabled": True},
        "nature.line-spacing": {"factor": 1.0},
        "nature.block.alignment": {"horizontal_extent": "mid-text-block-to-right-margin"},
    }
    for rule_id, values in expected.items():
        rule = rules.get(rule_id)
        if not rule:
            fail(f"certified N4 rule disappeared: {rule_id}")
        if rule["values"] != values:
            fail(f"{rule_id}: unexpected values {rule['values']}")

    for rule_id in contract["promoted_rule_ids"]:
        rule = rules[rule_id]
        authority = rule.get("authority")
        if authority == "normative":
            resolution = rule.get("resolution")
            if not isinstance(resolution, dict) or resolution.get("status") != "resolved":
                fail(f"{rule_id}: unresolved normative provenance")
            if not resolution.get("governing_sources"):
                fail(f"{rule_id}: missing governing source")
        elif authority in {"project-policy", "technical-profile"}:
            if rule.get("sources") or rule.get("resolution") is not None:
                fail(f"{rule_id}: non-normative rule claims external authority")
        else:
            fail(f"{rule_id}: invalid authority {authority}")

    indicator = rules["section.indicator.alignment"]
    if set(indicator["resolution"]["governing_sources"]) != {
        "abnt-nbr-14724-2024",
        "abnt-nbr-6024-2012",
    }:
        fail("section indicator must be jointly governed by current NBR 14724 and NBR 6024")

    runner = (ROOT / "tests" / "run.py").read_text(encoding="utf-8")
    gates = set(re.findall(r'Check\("([^"]+)"', runner))
    uncovered = sorted(
        rule_id
        for rule_id in contract["promoted_rule_ids"]
        if not (set(rules[rule_id]["validation"]["checks"]) & gates)
    )
    if uncovered:
        fail("promoted N4 rules without unified evidence: " + ", ".join(uncovered))

    print(
        "Full normative contract passed: "
        f"{len(rules)} atomic rules, {len(contract['promoted_rule_ids'])} N4 promotions "
        f"across {len(contract.get('coverage_manifests', []))} manifests, "
        "current-source precedence preserved."
    )


if __name__ == "__main__":
    main()
