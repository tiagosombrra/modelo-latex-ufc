#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from normative_atomic import load_atomic_contract
from normative_catalog import ACTIVE_STATUSES, CatalogError, load_catalog, source_map

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COVERAGE_DIR = ROOT / "normativa"
DEFAULT_COVERAGE_GLOB = "coverage-rules*.json"

NON_NORMATIVE_AUTHORITIES = {"project-policy", "technical-profile"}
ALLOWED_VALIDATION_MODES = {
    "automatic",
    "automatic-deep",
    "automatic-partial",
    "automatic-policy",
    "manual",
    "conditional-manual",
    "conditional",
    "not-applicable",
}


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"cannot load {label}: {exc}") from exc
    if not isinstance(data, dict):
        raise CatalogError(f"{label} must be an object")
    return data


def _default_coverage_paths() -> list[Path]:
    paths = sorted(DEFAULT_COVERAGE_DIR.glob(DEFAULT_COVERAGE_GLOB))
    if not paths:
        raise CatalogError("no N4 coverage rule manifests found")
    return paths


def _resolve_sources(
    rule_id: str,
    refs: list[str],
    scope: str,
    catalog: dict[str, Any],
) -> dict[str, Any]:
    sources = source_map(catalog)
    unknown = sorted(set(refs) - set(sources))
    if unknown:
        raise CatalogError(f"coverage rule {rule_id}: unknown sources: {', '.join(unknown)}")

    inactive = sorted(
        source_id for source_id in refs if sources[source_id]["status"] not in ACTIVE_STATUSES
    )
    if inactive:
        raise CatalogError(
            f"coverage rule {rule_id}: inactive sources cannot govern a current rule: "
            + ", ".join(inactive)
        )

    scope_precedence = catalog["policy"]["scope_precedence"]
    if scope not in scope_precedence:
        raise CatalogError(f"coverage rule {rule_id}: unknown scope {scope}")
    ranks = {role: index for index, role in enumerate(scope_precedence[scope])}

    ranked: list[tuple[int, str]] = []
    for source_id in refs:
        role = sources[source_id].get("role")
        if role not in ranks:
            raise CatalogError(
                f"coverage rule {rule_id}: source {source_id} role {role} is invalid for scope {scope}"
            )
        ranked.append((ranks[role], source_id))

    best = min(rank for rank, _ in ranked)
    governing = [source_id for rank, source_id in ranked if rank == best]
    supporting = [source_id for rank, source_id in ranked if rank != best]
    resolution: dict[str, Any] = {
        "scope": scope,
        "status": "resolved",
        "governing_sources": governing,
    }
    if supporting:
        resolution["supporting_sources"] = supporting
    return resolution


def _build_rule(spec: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    rule_id = spec.get("id")
    if not isinstance(rule_id, str) or not rule_id:
        raise CatalogError("coverage rule requires a non-empty id")

    for field in ("category", "requirement", "locator", "normativity", "kind"):
        if not spec.get(field):
            raise CatalogError(f"coverage rule {rule_id}: missing {field}")

    values = spec.get("values")
    if not isinstance(values, dict) or not values:
        raise CatalogError(f"coverage rule {rule_id}: values must be a non-empty object")

    validation = spec.get("validation")
    if not isinstance(validation, dict):
        raise CatalogError(f"coverage rule {rule_id}: validation must be an object")
    if validation.get("mode") not in ALLOWED_VALIDATION_MODES:
        raise CatalogError(
            f"coverage rule {rule_id}: invalid validation mode {validation.get('mode')}"
        )
    checks = validation.get("checks")
    if not isinstance(checks, list) or not checks:
        raise CatalogError(f"coverage rule {rule_id}: validation checks are required")

    authority = spec.get("authority", "normative")
    if authority != "normative" and authority not in NON_NORMATIVE_AUTHORITIES:
        raise CatalogError(f"coverage rule {rule_id}: invalid authority {authority}")

    rule = {
        "id": rule_id,
        "category": spec["category"],
        "requirement": spec["requirement"],
        "locator": spec["locator"],
        "normativity": spec["normativity"],
        "kind": spec["kind"],
        "values": copy.deepcopy(values),
        "validation": copy.deepcopy(validation),
        "authority": authority,
        "phase": "N4",
    }
    if "applicability" in spec:
        if not isinstance(spec["applicability"], dict):
            raise CatalogError(f"coverage rule {rule_id}: applicability must be an object")
        rule["applicability"] = copy.deepcopy(spec["applicability"])

    refs = spec.get("sources", [])
    if authority == "normative":
        if not isinstance(refs, list) or not refs:
            raise CatalogError(f"coverage rule {rule_id}: normative sources are required")
        scope = spec.get("scope")
        if not isinstance(scope, str) or not scope:
            raise CatalogError(f"coverage rule {rule_id}: normative scope is required")
        rule["sources"] = list(refs)
        rule["resolution"] = _resolve_sources(rule_id, list(refs), scope, catalog)
    else:
        if refs:
            raise CatalogError(
                f"coverage rule {rule_id}: {authority} must not claim external normative sources"
            )
        rule["sources"] = []
        rule["resolution"] = None

    return rule


def load_full_contract(
    catalog: dict[str, Any] | None = None,
    coverage_paths: Iterable[Path] | None = None,
) -> dict[str, Any]:
    if catalog is None:
        catalog = load_catalog()
    n3 = load_atomic_contract(catalog)
    paths = list(coverage_paths) if coverage_paths is not None else _default_coverage_paths()
    if not paths:
        raise CatalogError("N4 coverage rule manifest list is empty")

    catalog_reviewed = date.fromisoformat(catalog["reviewed_at"])
    rules = [copy.deepcopy(rule) for rule in n3["rules"]]
    seen = {rule["id"] for rule in rules}
    promoted: list[str] = []
    manifest_names: list[str] = []
    reviewed_dates: list[date] = []

    for path in paths:
        manifest = _load_json(path, f"N4 coverage rules {path.name}")
        if manifest.get("schema_version") != 1:
            raise CatalogError(f"{path.name}: unsupported coverage-rules schema_version")
        try:
            coverage_reviewed = date.fromisoformat(manifest["reviewed_at"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CatalogError(f"{path.name}: reviewed_at must be an ISO date") from exc
        if coverage_reviewed < catalog_reviewed:
            raise CatalogError(f"{path.name}: N4 coverage rules are older than the catalog review")
        reviewed_dates.append(coverage_reviewed)
        manifest_names.append(path.name)

        specs = manifest.get("rules")
        if not isinstance(specs, list):
            raise CatalogError(f"{path.name}: rules must be a list")
        for spec in specs:
            if not isinstance(spec, dict):
                raise CatalogError(f"{path.name}: every coverage rule must be an object")
            rule = _build_rule(spec, catalog)
            if rule["id"] in seen:
                raise CatalogError(f"coverage rule id collides with existing atomic rule: {rule['id']}")
            seen.add(rule["id"])
            promoted.append(rule["id"])
            rules.append(rule)

    return {
        "schema_version": 1,
        "reviewed_at": max(reviewed_dates).isoformat(),
        "catalog_reviewed_at": catalog["reviewed_at"],
        "coverage_manifests": manifest_names,
        "n3_rule_count": len(n3["rules"]),
        "promoted_rule_ids": promoted,
        "rules": rules,
        "compatibility_aliases": copy.deepcopy(n3["compatibility_aliases"]),
        "retired_in_n4": copy.deepcopy(n3["retired_in_n4"]),
    }


def full_rule_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {rule["id"]: rule for rule in contract["rules"]}


def main() -> None:
    contract = load_full_contract()
    rules = full_rule_map(contract)
    normative = sum(rule["authority"] == "normative" for rule in rules.values())
    project = len(rules) - normative
    print(
        "Full normative contract valid: "
        f"{len(rules)} atomic rules ({contract['n3_rule_count']} N3 + "
        f"{len(contract['promoted_rule_ids'])} N4 across "
        f"{len(contract['coverage_manifests'])} manifests), {normative} normative, "
        f"{project} project/technical-profile."
    )


if __name__ == "__main__":
    main()
