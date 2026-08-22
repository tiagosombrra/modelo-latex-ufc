#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path
from typing import Any

from normative_catalog import CatalogError, load_catalog, rule_map

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATOMIC_RULES = ROOT / "normativa" / "atomic-rules.json"
DEFAULT_ATOMICITY_PLAN = ROOT / "normativa" / "atomicity-plan.json"


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"cannot load {label}: {exc}") from exc
    if not isinstance(data, dict):
        raise CatalogError(f"{label} must be an object")
    return data


def _select_parent_keys(
    parent: dict[str, Any],
    keys: list[str],
    *,
    rename: dict[str, str] | None = None,
    label: str,
) -> dict[str, Any]:
    parent_values = parent["values"]
    rename = rename or {}
    values: dict[str, Any] = {}
    for key in keys:
        if key not in parent_values:
            raise CatalogError(f"{label}: parent {parent['id']} has no value key {key}")
        values[rename.get(key, key)] = copy.deepcopy(parent_values[key])
    return values


def _selected_values(parent: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    rule_id = spec.get("id")
    rename = spec.get("rename", {})
    if not isinstance(rename, dict):
        raise CatalogError(f"atomic rule {rule_id}: rename must be an object")
    keys = spec.get("keys", [])
    if not isinstance(keys, list):
        raise CatalogError(f"atomic rule {rule_id}: keys must be a list")
    values = _select_parent_keys(parent, keys, rename=rename, label=f"atomic rule {rule_id}")

    explicit = spec.get("values", {})
    if not isinstance(explicit, dict):
        raise CatalogError(f"atomic rule {rule_id}: values must be an object")
    for key, value in explicit.items():
        if key in values and values[key] != value:
            raise CatalogError(f"atomic rule {rule_id}: conflicting value for {key}")
        values[key] = copy.deepcopy(value)

    if not values:
        raise CatalogError(f"atomic rule {rule_id}: no expected value declared")
    return values


def _applicability(parent: dict[str, Any], spec: dict[str, Any], rule_id: str) -> dict[str, Any]:
    applicability: dict[str, Any] = {}
    keys = spec.get("applicability_keys", [])
    if not isinstance(keys, list):
        raise CatalogError(f"atomic rule {rule_id}: applicability_keys must be a list")
    for key in keys:
        if key not in parent["values"]:
            raise CatalogError(
                f"atomic rule {rule_id}: parent {parent['id']} has no applicability key {key}"
            )
        applicability[key] = copy.deepcopy(parent["values"][key])
    explicit = spec.get("applicability", {})
    if not isinstance(explicit, dict):
        raise CatalogError(f"atomic rule {rule_id}: applicability must be an object")
    applicability.update(copy.deepcopy(explicit))
    return applicability


def _build_child(parent: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    rule_id = spec.get("id")
    requirement = spec.get("requirement")
    if not isinstance(rule_id, str) or not rule_id:
        raise CatalogError(f"atomic child of {parent['id']}: missing id")
    if not isinstance(requirement, str) or not requirement:
        raise CatalogError(f"atomic rule {rule_id}: missing requirement")

    authority = spec.get("authority", "normative")
    if authority not in {"normative", "project-policy"}:
        raise CatalogError(f"atomic rule {rule_id}: invalid authority {authority}")

    child = {
        "id": rule_id,
        "category": spec.get("category", parent["category"]),
        "requirement": requirement,
        "locator": spec.get("locator", parent["locator"]),
        "normativity": spec.get("normativity", parent["normativity"]),
        "kind": spec.get("kind", parent["kind"]),
        "values": _selected_values(parent, spec),
        "validation": copy.deepcopy(parent["validation"]),
        "parent_rule": parent["id"],
        "authority": authority,
    }

    applicability = _applicability(parent, spec, rule_id)
    if applicability:
        child["applicability"] = applicability

    if authority == "project-policy":
        child["sources"] = []
        child["resolution"] = None
    else:
        child["sources"] = copy.deepcopy(parent["sources"])
        child["resolution"] = copy.deepcopy(parent["resolution"])

    return child


def _build_keep(
    parent: dict[str, Any],
    parent_id: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    rule = copy.deepcopy(parent)
    rule["parent_rule"] = parent_id
    rule["authority"] = "normative"

    key_map = manifest.get("keep_value_keys", {})
    explicit_map = manifest.get("keep_explicit_values", {})
    applicability_map = manifest.get("keep_applicability_keys", {})
    parameter_map = manifest.get("keep_validation_parameter_keys", {})
    for label, mapping in (
        ("keep_value_keys", key_map),
        ("keep_explicit_values", explicit_map),
        ("keep_applicability_keys", applicability_map),
        ("keep_validation_parameter_keys", parameter_map),
    ):
        if not isinstance(mapping, dict):
            raise CatalogError(f"atomic-rules {label} must be an object")

    if parent_id in key_map:
        keys = key_map[parent_id]
        if not isinstance(keys, list):
            raise CatalogError(f"atomic keep rule {parent_id}: keep_value_keys must be a list")
        values = _select_parent_keys(parent, keys, label=f"atomic keep rule {parent_id}")
        explicit = explicit_map.get(parent_id, {})
        if not isinstance(explicit, dict):
            raise CatalogError(f"atomic keep rule {parent_id}: explicit values must be an object")
        values.update(copy.deepcopy(explicit))
        if not values:
            raise CatalogError(f"atomic keep rule {parent_id}: no expected value declared")
        rule["values"] = values
    elif parent_id in explicit_map:
        rule["values"] = copy.deepcopy(explicit_map[parent_id])

    applicability_keys = applicability_map.get(parent_id, [])
    if applicability_keys:
        if not isinstance(applicability_keys, list):
            raise CatalogError(f"atomic keep rule {parent_id}: applicability keys must be a list")
        rule["applicability"] = _select_parent_keys(
            parent,
            applicability_keys,
            label=f"atomic keep rule {parent_id} applicability",
        )

    parameter_keys = parameter_map.get(parent_id, [])
    if parameter_keys:
        if not isinstance(parameter_keys, list):
            raise CatalogError(f"atomic keep rule {parent_id}: validation parameter keys must be a list")
        rule["validation_parameters"] = _select_parent_keys(
            parent,
            parameter_keys,
            label=f"atomic keep rule {parent_id} validation parameters",
        )

    return rule


def load_atomic_contract(
    catalog: dict[str, Any] | None = None,
    path: Path = DEFAULT_ATOMIC_RULES,
    plan_path: Path = DEFAULT_ATOMICITY_PLAN,
) -> dict[str, Any]:
    if catalog is None:
        catalog = load_catalog()

    manifest = _load_json(path, "atomic normative rules")
    plan = _load_json(plan_path, "atomicity plan")

    if manifest.get("schema_version") != 1:
        raise CatalogError("unsupported atomic-rules schema_version")
    if plan.get("schema_version") != 1:
        raise CatalogError("unsupported atomicity-plan schema_version")

    try:
        atomic_reviewed = date.fromisoformat(manifest["reviewed_at"])
        catalog_reviewed = date.fromisoformat(catalog["reviewed_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CatalogError("catalog and atomic-rules reviewed_at must be ISO dates") from exc
    if atomic_reviewed < catalog_reviewed:
        raise CatalogError("atomic rule contract is older than the catalog review")

    parents = rule_map(catalog, allow_review=True)
    keep = manifest.get("keep_atomic")
    groups = manifest.get("groups")
    retire = manifest.get("retire_in_n4")
    if not isinstance(keep, list) or not isinstance(groups, dict) or not isinstance(retire, dict):
        raise CatalogError("atomic-rules requires keep_atomic, groups and retire_in_n4")

    declared_parents = set(keep) | set(groups) | set(retire)
    if declared_parents != set(parents):
        missing = sorted(set(parents) - declared_parents)
        extra = sorted(declared_parents - set(parents))
        raise CatalogError(f"atomic parent coverage mismatch; missing={missing}, extra={extra}")
    if (set(keep) & set(groups)) or (set(keep) & set(retire)) or (set(groups) & set(retire)):
        raise CatalogError("atomic parent classifications must be disjoint")

    plan_rules = plan.get("rules")
    if not isinstance(plan_rules, dict) or set(plan_rules) != set(parents):
        raise CatalogError("atomicity plan does not cover the current catalog exactly")

    atomic: list[dict[str, Any]] = []
    seen: set[str] = set()

    for parent_id in keep:
        if plan_rules[parent_id].get("status") != "keep-atomic":
            raise CatalogError(f"atomicity plan disagrees for {parent_id}")
        rule = _build_keep(parents[parent_id], parent_id, manifest)
        if rule["id"] in seen:
            raise CatalogError(f"duplicate atomic rule id: {rule['id']}")
        seen.add(rule["id"])
        atomic.append(rule)

    for parent_id, specs in groups.items():
        plan_entry = plan_rules[parent_id]
        if plan_entry.get("status") != "split":
            raise CatalogError(f"atomicity plan disagrees for {parent_id}")
        if not isinstance(specs, list) or len(specs) < 2:
            raise CatalogError(f"atomic group {parent_id} must contain at least two rules")

        expected_targets = plan_entry.get("targets")
        actual_targets = [spec.get("id") for spec in specs]
        if actual_targets != expected_targets:
            raise CatalogError(f"atomicity target order/content mismatch for {parent_id}")

        parent = parents[parent_id]
        for spec in specs:
            child = _build_child(parent, spec)
            if child["id"] in seen or child["id"] in parents:
                raise CatalogError(f"duplicate/colliding atomic rule id: {child['id']}")
            seen.add(child["id"])
            atomic.append(child)

    for parent_id, reason in retire.items():
        plan_entry = plan_rules[parent_id]
        if plan_entry.get("status") != "retire-in-n4":
            raise CatalogError(f"atomicity plan disagrees for retired rule {parent_id}")
        if not reason or plan_entry.get("reason") != reason:
            raise CatalogError(f"retirement reason mismatch for {parent_id}")

    for rule in atomic:
        for field in ("id", "category", "requirement", "locator", "normativity", "kind"):
            if not rule.get(field):
                raise CatalogError(f"atomic rule {rule.get('id')}: missing {field}")
        if not isinstance(rule.get("values"), dict) or not rule["values"]:
            raise CatalogError(f"atomic rule {rule['id']}: expected values are required")
        validation = rule.get("validation")
        if not isinstance(validation, dict) or not validation.get("checks"):
            raise CatalogError(f"atomic rule {rule['id']}: validation evidence is required")
        if rule["authority"] == "project-policy":
            if rule.get("sources") or rule.get("resolution") is not None:
                raise CatalogError(
                    f"atomic project policy {rule['id']}: must not claim external normative authority"
                )
        else:
            if not rule.get("sources") or not isinstance(rule.get("resolution"), dict):
                raise CatalogError(f"atomic rule {rule['id']}: normative provenance is required")

    return {
        "schema_version": manifest["schema_version"],
        "reviewed_at": manifest["reviewed_at"],
        "catalog_reviewed_at": catalog["reviewed_at"],
        "rules": atomic,
        "retired_in_n4": copy.deepcopy(retire),
        "compatibility_aliases": {
            parent_id: [spec["id"] for spec in specs]
            for parent_id, specs in groups.items()
        },
    }


def atomic_rule_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {rule["id"]: rule for rule in contract["rules"]}


def main() -> None:
    contract = load_atomic_contract()
    rules = atomic_rule_map(contract)
    project = sum(rule["authority"] == "project-policy" for rule in rules.values())
    print(
        "Atomic normative contract valid: "
        f"{len(rules)} atomic rules, {project} project-policy rule, "
        f"{len(contract['retired_in_n4'])} umbrella rule deferred to N4."
    )


if __name__ == "__main__":
    main()
