#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from normative_full import load_full_contract

TARGET_CATEGORIES = {"objects", "equations", "code-algorithms"}
CROSS_CUTTING_RULE_IDS = {
    "font.size.reduced.illustration-source",
    "font.size.reduced.table-source",
}
EXPECTED_PROJECT_POLICY = {
    "code.listing.project-policy",
    "algorithm.project-policy",
}


def fail(message: str) -> None:
    raise SystemExit(f"Objects scope integrity failed: {message}")


def runner_ids() -> set[str]:
    source = (ROOT / "tests" / "run.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    result: set[str] = set()
    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "Check":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        if isinstance(node.args[0].value, str):
            result.add(node.args[0].value)
    return result


def main() -> None:
    contract = load_full_contract()
    rules = {rule["id"]: rule for rule in contract["rules"]}
    scoped = {
        rule_id
        for rule_id, rule in rules.items()
        if rule.get("category") in TARGET_CATEGORIES
    } | CROSS_CUTTING_RULE_IDS

    if len(scoped) != 23:
        fail(f"expected 23 current scoped rules, got {len(scoped)}")
    missing_cross = sorted(CROSS_CUTTING_RULE_IDS - set(rules))
    if missing_cross:
        fail("missing cross-cutting rules: " + ", ".join(missing_cross))

    for rule_id in CROSS_CUTTING_RULE_IDS:
        if rules[rule_id].get("values") != {"pt": 10}:
            fail(f"{rule_id}: expected 10 pt current contract")

    observed_project_policy = {
        rule_id for rule_id in scoped if rules[rule_id].get("authority") == "project-policy"
    }
    if observed_project_policy != EXPECTED_PROJECT_POLICY:
        fail("project-policy boundary drifted: " + repr(sorted(observed_project_policy)))
    for rule_id in EXPECTED_PROJECT_POLICY:
        if rules[rule_id].get("values") != {"supported": True, "normative_claim": False}:
            fail(f"{rule_id}: project-policy values drifted")
    for rule_id in sorted(scoped - EXPECTED_PROJECT_POLICY):
        if rules[rule_id].get("authority") != "normative":
            fail(f"{rule_id}: unexpected non-normative authority")

    gates = runner_ids()
    uncovered = sorted(
        rule_id
        for rule_id in scoped
        if not (set(rules[rule_id]["validation"]["checks"]) & gates)
    )
    if uncovered:
        fail("current scoped rules without unified validation gate: " + ", ".join(uncovered))

    print(
        "OBJECTS-SCOPE-EVIDENCE "
        f"rules={len(scoped)} project_policy={len(EXPECTED_PROJECT_POLICY)} "
        f"cross_cutting={len(CROSS_CUTTING_RULE_IDS)} uncovered=0"
    )


if __name__ == "__main__":
    main()
