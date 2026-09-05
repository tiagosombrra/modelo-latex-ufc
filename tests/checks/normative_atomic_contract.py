#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests" / "checks"))

from normative_atomic import atomic_rule_map, load_atomic_contract
from normative_catalog import load_catalog, rule_map
from normative_traceability import load_runner_checks


def fail(message: str) -> None:
    raise SystemExit(f"Normative atomic contract failed: {message}")


def quoted_pairs(text: str, function: str) -> set[tuple[str, str]]:
    pattern = rf"{re.escape(function)}\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"
    return set(re.findall(pattern, text))


def main() -> None:
    catalog = load_catalog()
    parents = rule_map(catalog)
    contract = load_atomic_contract(catalog)
    atomic = atomic_rule_map(contract)

    if len(parents) != 29:
        fail(f"expected 29 current compatibility parent rules, got {len(parents)}")
    if "project.standard" in parents:
        fail("retired project.standard must not remain in the compatibility catalog")
    if len(atomic) != 98:
        fail(f"expected 98 N3 atomic rules after object-title migration, got {len(atomic)}")

    aliases = contract["compatibility_aliases"]
    if "summary.word-count" not in aliases:
        fail("summary.word-count must be decomposed")
    if aliases.get("deposit.pdfa") != ["deposit.pdfa.required", "pdfa.profile.project"]:
        fail("PDF/A institutional requirement and project profile must be separate")

    page = atomic["page.a4"]
    if page["values"] != {"width_mm": 210, "height_mm": 297}:
        fail("page.a4 expected values must contain only the normative paper dimensions")
    if page.get("validation_parameters") != {"tolerance_pt": 1.8}:
        fail("A4 measurement tolerance must be classified as a validation parameter")

    pdfa = atomic["deposit.pdfa.required"]
    if pdfa["values"] != {"required": "PDF/A"}:
        fail("deposit.pdfa.required must contain only the UFC PDF/A requirement")
    if set(pdfa["sources"]) != {"ufc-deposito-tcc-2026", "ufc-deposito-pos-2026"}:
        fail("deposit.pdfa.required has unexpected institutional sources")

    profile = atomic["pdfa.profile.project"]
    if profile["authority"] != "project-policy":
        fail("PDF/A-2b must be classified as project policy")
    if profile["values"] != {"profile": "PDF/A-2b"}:
        fail("unexpected abntexto-ufc PDF/A technical profile")
    if profile["sources"] or profile["resolution"] is not None:
        fail("project PDF/A profile must not claim UFC/ABNT normative authority")

    capes = atomic["deposit.capes"]
    if capes["values"] != {"required": True}:
        fail("CAPES atomic rule must express the requirement independently")
    if capes.get("applicability") != {"condition": "capes-funded"}:
        fail("CAPES funding condition must be applicability, not an expected value")

    catalog_card = atomic["deposit.catalog-card"]
    if catalog_card["values"] != {"required": False}:
        fail("catalog-card atomic rule must express only optionality")
    if "applies_to" not in catalog_card.get("applicability", {}):
        fail("catalog-card document profiles must be applicability metadata")

    catalog_typography = atomic["font.size.reduced.catalog-card"]
    if catalog_typography["values"] != {"pt": 10}:
        fail("catalog-card reduced-font value must remain 10 pt")
    catalog_validation = catalog_typography["validation"]
    if catalog_validation.get("mode") != "manual":
        fail("external catalog-card typography must be classified as manual validation")
    if catalog_validation.get("checks") != ["catalog-card"]:
        fail("catalog-card typography must remain tied to the catalog-card gate")
    if catalog_validation.get("scope") != "external-pdf":
        fail("catalog-card typography must be explicitly scoped to the external PDF")

    keywords = atomic["summary.keywords.required"]
    if keywords["values"] != {"required": True}:
        fail("summary keyword requirement is not atomic")

    split_parents = set(aliases)
    leaked = sorted(split_parents & set(atomic))
    if leaked:
        fail("aggregated split rules leaked into atomic contract: " + ", ".join(leaked))

    gate_checks = set(load_runner_checks())
    cli = (ROOT / "tools" / "validate-ufc-pdf.py").read_text(encoding="utf-8")
    web = (ROOT / "validator" / "app.js").read_text(encoding="utf-8")
    validator_checks = {check for check, _ in quoted_pairs(cli, "norm_check")}
    validator_checks |= {check for check, _ in quoted_pairs(web, "nck")}
    registry_path = ROOT / "standards" / "evidence-registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load evidence registry: {exc}")

    if registry.get("schema_version") != 1:
        fail("unsupported evidence-registry schema_version")

    entries = registry.get("evidence")
    if not isinstance(entries, list) or not entries:
        fail("evidence registry must contain a non-empty evidence list")

    registered_checks: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("every evidence registry entry must be an object")
        evidence_id = entry.get("id")
        if not isinstance(evidence_id, str) or not evidence_id:
            fail("every evidence registry entry requires a non-empty id")
        if evidence_id in registered_checks:
            fail(f"duplicate evidence registry id: {evidence_id}")
        registered_checks.add(evidence_id)

    known_checks = gate_checks | validator_checks | registered_checks

    uncovered = sorted(
        rule_id
        for rule_id, rule in atomic.items()
        if not (set(rule["validation"]["checks"]) & known_checks)
    )
    if uncovered:
        fail("atomic rules without known evidence: " + ", ".join(uncovered))

    unresolved = sorted(
        rule_id
        for rule_id, rule in atomic.items()
        if rule["authority"] == "normative"
        and rule["resolution"]["status"] != "resolved"
    )
    if unresolved:
        fail("atomic rules still require normative resolution: " + ", ".join(unresolved))

    print(
        "Normative atomic contract passed: "
        f"{len(atomic)} atomic rules, {len(aliases)} compatibility aliases."
    )


if __name__ == "__main__":
    main()
