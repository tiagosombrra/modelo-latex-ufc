#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests" / "checks"))

from normative_catalog import load_catalog, rule_map
from normative_coverage_audit import main as run_coverage_audit
from normative_full import full_rule_map, load_full_contract


def fail(message: str) -> None:
    raise SystemExit(f"Normative coverage failed: {message}")


def quoted_pairs(text: str, function: str) -> set[tuple[str, str]]:
    pattern = rf"{re.escape(function)}\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"
    return set(re.findall(pattern, text))


def main() -> None:
    run_coverage_audit()

    catalog = load_catalog()
    compatibility_rules = rule_map(catalog)
    contract = load_full_contract(catalog)
    rules = full_rule_map(contract)
    reviewed = date.fromisoformat(catalog["reviewed_at"])

    for source in catalog["sources"]:
        checked = date.fromisoformat(source["checked_at"])
        if checked > reviewed:
            fail(
                f"source {source['id']} was checked on {checked} after catalog review {reviewed}; "
                "review affected rules and advance reviewed_at"
            )

    runner = (ROOT / "tests" / "run.py").read_text(encoding="utf-8")
    gate_checks = set(re.findall(r'Check\("([^"]+)"', runner))

    cli = (ROOT / "tools" / "validate-ufc-pdf.py").read_text(encoding="utf-8")
    web = (ROOT / "validator" / "app.js").read_text(encoding="utf-8")
    mappings = quoted_pairs(cli, "norm_check") | quoted_pairs(web, "nck")
    validator_checks = {check_id for check_id, _ in mappings}

    unknown_rules = sorted(
        {rule_id for _, rule_id in mappings if rule_id not in compatibility_rules}
    )
    if unknown_rules:
        fail("validator references unknown compatibility rules: " + ", ".join(unknown_rules))

    uncovered: list[str] = []
    known_checks = gate_checks | validator_checks
    for rule_id, rule in rules.items():
        evidence = set(rule["validation"]["checks"])
        if not evidence & known_checks:
            uncovered.append(rule_id)
    if uncovered:
        fail("full atomic rules without a known gate or validator check: " + ", ".join(sorted(uncovered)))

    direct_by_parent: dict[str, set[str]] = {}
    for check_id, rule_id in mappings:
        direct_by_parent.setdefault(rule_id, set()).add(check_id)

    automatic = sum(
        rule["validation"]["mode"].startswith("automatic")
        for rule in rules.values()
    )
    manual = len(rules) - automatic
    project_policy = sum(rule["authority"] in {"project-policy", "technical-profile"} for rule in rules.values())
    print(
        "Normative coverage passed: "
        f"{len(catalog['sources'])} sources, {len(rules)} full atomic rules, "
        f"{automatic} automatic/partial, {manual} manual/conditional, "
        f"{project_policy} project/technical-profile, {len(gate_checks)} unified gates, "
        f"{len(validator_checks)} direct PDF checks, "
        f"{len(direct_by_parent)} compatibility parent rules consumed directly."
    )


if __name__ == "__main__":
    main()
