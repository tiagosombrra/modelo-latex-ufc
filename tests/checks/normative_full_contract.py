#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from normative_catalog import load_catalog
from normative_full import full_rule_map, load_full_contract

BASE_RULE_COUNT = 98
MINIMUM_EXTENSION_COUNT = 23

PRE_ARTICLE_RUNTIME_PHASES = {
    "regression-audit",
    "core-corrections",
    "reference-pdf-validation",
}
ARTICLE_RUNTIME_OR_LATER_PHASES = {
    "scientific-article",
    "final-certification",
    "release",
}
READABLE_V3_PHASES = PRE_ARTICLE_RUNTIME_PHASES | ARTICLE_RUNTIME_OR_LATER_PHASES


def fail(message: str) -> None:
    raise SystemExit(f"Full normative contract failed: {message}")


def main() -> None:
    catalog = load_catalog()
    contract = load_full_contract(catalog)
    rules = full_rule_map(contract)

    if contract["base_rule_count"] != BASE_RULE_COUNT:
        fail(
            f"expected {BASE_RULE_COUNT} base atomic rules, "
            f"got {contract['base_rule_count']}"
        )
    extension_ids = contract["extended_rule_ids"]
    if len(rules) != contract["base_rule_count"] + len(extension_ids):
        fail("full contract count is inconsistent with base rules + extensions")
    if len(extension_ids) < MINIMUM_EXTENSION_COUNT:
        fail("full contract lost the certified extension block")
    if "project.standard" in rules:
        fail("retired project.standard umbrella returned to the active contract")

    article_rules = sorted(rule_id for rule_id in rules if rule_id.startswith("article."))
    roadmap = json.loads((ROOT / "release" / "v3-roadmap.json").read_text(encoding="utf-8"))
    phase = roadmap.get("phase")
    if phase not in READABLE_V3_PHASES:
        fail(f"unknown readable V3 roadmap phase: {phase}")
    if not article_rules:
        fail("retained scientific-article source contract disappeared")

    # The article authority contract was reconstructed before runtime work began.
    # During shared-foundation regression/correction/reference validation, retain
    # that contract but forbid executable article validation or proof promotion.
    if phase in PRE_ARTICLE_RUNTIME_PHASES:
        for rule_id in article_rules:
            validation = rules[rule_id]["validation"]
            if validation["mode"] not in {"manual", "conditional-manual"}:
                fail(
                    f"{rule_id}: pre-article phases must not claim executable "
                    "article validation"
                )
            if validation["checks"] != ["article.source-review"]:
                fail(
                    f"{rule_id}: pre-article phases must retain source-review-only "
                    "article evidence"
                )

    expected = {
        "pagination.frontmatter.counted-not-numbered": {
            "counted": True,
            "number_visible": False,
        },
        "pagination.catalog-data.not-counted": {
            "counted": False,
            "number_visible": False,
        },
        "pagination.recto.position": {"position": "upper-right"},
        "pagination.verso.position": {"position": "upper-left"},
        "footnote.line-spacing": {"factor": 1.0},
        "footnote.separator.length": {
            "length_mm": 50,
            "origin": "left-margin",
        },
        "footnote.hanging-alignment": {"enabled": True},
        "section.indicator.alignment": {"alignment": "left"},
        "section.indicator.separator": {
            "separator": "single-character-space",
        },
        "section.primary.recto-duplex": {"start_side": "recto"},
        "section.multiline.hanging": {"enabled": True},
        "nature.line-spacing": {"factor": 1.0},
        "nature.block.alignment": {
            "horizontal_extent": "mid-text-block-to-right-margin",
        },
    }
    for rule_id, values in expected.items():
        rule = rules.get(rule_id)
        if not rule:
            fail(f"certified rule disappeared: {rule_id}")
        if rule["values"] != values:
            fail(f"{rule_id}: unexpected values {rule['values']}")

    for rule_id in extension_ids:
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
        fail(
            "section indicator must be jointly governed by current "
            "NBR 14724 and NBR 6024"
        )

    not_applicable = sorted(
        rule_id
        for rule_id in extension_ids
        if rules[rule_id]["validation"]["mode"] == "not-applicable"
    )
    for rule_id in not_applicable:
        rule = rules[rule_id]
        if rule["validation"]["checks"]:
            fail(f"{rule_id}: not-applicable validation declares executable checks")
        if not rule.get("applicability"):
            fail(f"{rule_id}: not-applicable validation lacks explicit applicability")

    runner = (ROOT / "tests" / "run.py").read_text(encoding="utf-8")
    gates = set(re.findall(r'Check\(\s*"([^"]+)"', runner))
    runner_required_modes = {"automatic", "automatic-deep", "automatic-partial", "automatic-policy", "conditional"}
    uncovered = sorted(
        rule_id
        for rule_id in extension_ids
        if rules[rule_id]["validation"]["mode"] in runner_required_modes
        and not (set(rules[rule_id]["validation"]["checks"]) & gates)
    )
    if uncovered:
        fail("extended executable rules without unified evidence: " + ", ".join(uncovered))

    print(
        "Full normative contract passed: "
        f"{len(rules)} atomic rules, {len(extension_ids)} extensions "
        f"across {len(contract.get('coverage_manifests', []))} manifests, "
        f"{len(not_applicable)} explicitly not-applicable; phase={phase}."
    )


if __name__ == "__main__":
    main()
