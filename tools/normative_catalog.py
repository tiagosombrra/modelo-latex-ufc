#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "normativa" / "catalog.json"
DEFAULT_PRECEDENCE = ROOT / "normativa" / "precedence.json"

ACTIVE_STATUSES = {
    "current",
    "current-with-superseded-norm-references",
    "current-for-tabular-presentation",
}
INACTIVE_STATUSES = {"superseded", "historical"}
RESOLUTION_STATUSES = {"resolved", "review-required"}


class CatalogError(ValueError):
    pass


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"cannot load {label}: {exc}") from exc
    if not isinstance(data, dict):
        raise CatalogError(f"{label} must be an object")
    return data


def load_catalog(
    path: Path = DEFAULT_CATALOG,
    precedence_path: Path = DEFAULT_PRECEDENCE,
) -> dict[str, Any]:
    data = _load_json(path, "normative catalog")
    precedence = _load_json(precedence_path, "normative precedence")
    return merge_precedence(data, precedence)


def merge_precedence(
    catalog: dict[str, Any],
    precedence: dict[str, Any],
) -> dict[str, Any]:
    data = json.loads(json.dumps(catalog))
    policy = validate_precedence_document(precedence, data)

    source_roles = precedence["source_roles"]
    for source in data["sources"]:
        source["role"] = source_roles[source["id"]]

    resolutions = precedence["rules"]
    for rule in data["rules"]:
        resolution = resolutions[rule["id"]]
        rule["resolution"] = resolution
        ordered = (
            resolution["governing_sources"]
            + resolution.get("constraint_sources", [])
            + resolution.get("supporting_sources", [])
        )
        rule["sources"] = ordered + [source_id for source_id in rule["sources"] if source_id not in ordered]

    data["policy"] = policy
    data["precedence_schema_version"] = precedence["schema_version"]
    data["precedence_reviewed_at"] = precedence["reviewed_at"]
    validate_catalog(data)
    return data


def validate_precedence_document(
    precedence: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    if precedence.get("schema_version") != 1:
        raise CatalogError("unsupported precedence schema_version")
    if not precedence.get("reviewed_at"):
        raise CatalogError("precedence.reviewed_at is required")
    try:
        precedence_reviewed = date.fromisoformat(precedence["reviewed_at"])
        catalog_reviewed = date.fromisoformat(catalog["reviewed_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CatalogError("catalog and precedence reviewed_at must be ISO dates") from exc
    if precedence_reviewed < catalog_reviewed:
        raise CatalogError(
            "normative precedence is older than the catalog review; review precedence again"
        )
    if precedence.get("catalog_policy_mode") != "replace-embedded-policy":
        raise CatalogError("precedence.catalog_policy_mode must be replace-embedded-policy")

    source_roles = precedence.get("source_roles")
    resolutions = precedence.get("rules")
    scope_precedence = precedence.get("scope_precedence")
    if not isinstance(source_roles, dict) or not source_roles:
        raise CatalogError("precedence.source_roles must be a non-empty object")
    if not isinstance(resolutions, dict) or not resolutions:
        raise CatalogError("precedence.rules must be a non-empty object")
    if not isinstance(scope_precedence, dict) or not scope_precedence:
        raise CatalogError("precedence.scope_precedence must be a non-empty object")

    source_ids = {source["id"] for source in catalog.get("sources", [])}
    rule_ids = {rule["id"] for rule in catalog.get("rules", [])}
    if set(source_roles) != source_ids:
        missing = sorted(source_ids - set(source_roles))
        extra = sorted(set(source_roles) - source_ids)
        raise CatalogError(f"precedence source role mismatch; missing={missing}, extra={extra}")
    if set(resolutions) != rule_ids:
        missing = sorted(rule_ids - set(resolutions))
        extra = sorted(set(resolutions) - rule_ids)
        raise CatalogError(f"precedence rule mismatch; missing={missing}, extra={extra}")

    allowed_roles = {role for roles in scope_precedence.values() for role in roles}
    unknown_roles = sorted(set(source_roles.values()) - allowed_roles)
    if unknown_roles:
        raise CatalogError("precedence contains unknown source roles: " + ", ".join(unknown_roles))

    active = precedence.get("active_source_statuses")
    inactive = precedence.get("inactive_source_statuses")
    if set(active or []) != ACTIVE_STATUSES:
        raise CatalogError("precedence.active_source_statuses does not match supported statuses")
    if set(inactive or []) != INACTIVE_STATUSES:
        raise CatalogError("precedence.inactive_source_statuses does not match supported statuses")
    if precedence.get("conflict_behavior") != "review-required":
        raise CatalogError("precedence.conflict_behavior must be review-required")

    return {
        "description": precedence.get("description", ""),
        "principles": precedence.get("principles", []),
        "scope_precedence": scope_precedence,
        "conflict_behavior": precedence["conflict_behavior"],
        "source_of_truth": "normativa/catalog.json + normativa/precedence.json",
    }


def validate_catalog(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise CatalogError("unsupported schema_version")

    sources = data.get("sources")
    rules = data.get("rules")
    policy = data.get("policy")
    if not isinstance(sources, list) or not sources:
        raise CatalogError("sources must be a non-empty list")
    if not isinstance(rules, list) or not rules:
        raise CatalogError("rules must be a non-empty list")
    if not isinstance(policy, dict) or not policy.get("scope_precedence"):
        raise CatalogError("resolved policy.scope_precedence is required")

    source_ids: set[str] = set()
    source_by_id: dict[str, dict[str, Any]] = {}
    for source in sources:
        if not isinstance(source, dict):
            raise CatalogError("every source must be an object")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id:
            raise CatalogError("every source requires a non-empty id")
        if source_id in source_ids:
            raise CatalogError(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        source_by_id[source_id] = source
        for field in ("kind", "title", "publisher", "status", "checked_at", "role"):
            if not source.get(field):
                raise CatalogError(f"source {source_id}: missing {field}")
        status = source["status"]
        if status not in ACTIVE_STATUSES | INACTIVE_STATUSES:
            raise CatalogError(f"source {source_id}: unsupported status {status}")

    rule_ids: set[str] = set()
    allowed_modes = {
        "automatic",
        "automatic-deep",
        "automatic-partial",
        "automatic-policy",
        "manual",
        "conditional-manual",
    }
    for rule in rules:
        if not isinstance(rule, dict):
            raise CatalogError("every rule must be an object")
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            raise CatalogError("every rule requires a non-empty id")
        if rule_id in rule_ids:
            raise CatalogError(f"duplicate rule id: {rule_id}")
        rule_ids.add(rule_id)

        for field in ("category", "requirement", "locator", "normativity", "kind"):
            if not rule.get(field):
                raise CatalogError(f"rule {rule_id}: missing {field}")

        refs = rule.get("sources")
        if not isinstance(refs, list) or not refs:
            raise CatalogError(f"rule {rule_id}: sources must be non-empty")
        unknown = sorted(set(refs) - source_ids)
        if unknown:
            raise CatalogError(f"rule {rule_id}: unknown sources: {', '.join(unknown)}")

        values = rule.get("values")
        if not isinstance(values, dict):
            raise CatalogError(f"rule {rule_id}: values must be an object")

        validation = rule.get("validation")
        if not isinstance(validation, dict):
            raise CatalogError(f"rule {rule_id}: validation must be an object")
        mode = validation.get("mode")
        if mode not in allowed_modes:
            raise CatalogError(f"rule {rule_id}: invalid validation mode: {mode}")
        checks = validation.get("checks")
        if not isinstance(checks, list) or not checks:
            raise CatalogError(f"rule {rule_id}: validation.checks must be non-empty")

        validate_resolution(rule, source_by_id, policy["scope_precedence"])


def validate_resolution(
    rule: dict[str, Any],
    sources: dict[str, dict[str, Any]],
    scope_precedence: dict[str, list[str]],
) -> None:
    rule_id = rule["id"]
    resolution = rule.get("resolution")
    if not isinstance(resolution, dict):
        raise CatalogError(f"rule {rule_id}: resolution is required")

    scope = resolution.get("scope")
    if scope not in scope_precedence:
        raise CatalogError(f"rule {rule_id}: invalid resolution scope: {scope}")
    status = resolution.get("status")
    if status not in RESOLUTION_STATUSES:
        raise CatalogError(f"rule {rule_id}: invalid resolution status: {status}")

    governing = resolution.get("governing_sources")
    if not isinstance(governing, list) or not governing:
        raise CatalogError(f"rule {rule_id}: governing_sources must be non-empty")

    buckets = {
        "governing_sources": governing,
        "supporting_sources": resolution.get("supporting_sources", []),
        "constraint_sources": resolution.get("constraint_sources", []),
    }
    used: set[str] = set()
    rule_sources = set(rule["sources"])
    for label, refs in buckets.items():
        if not isinstance(refs, list):
            raise CatalogError(f"rule {rule_id}: {label} must be a list")
        unknown = sorted(set(refs) - rule_sources)
        if unknown:
            raise CatalogError(f"rule {rule_id}: {label} not present in rule.sources: {', '.join(unknown)}")
        duplicate = sorted(used & set(refs))
        if duplicate:
            raise CatalogError(f"rule {rule_id}: sources assigned to multiple resolution roles: {', '.join(duplicate)}")
        used.update(refs)
        inactive = sorted(ref for ref in refs if sources[ref]["status"] in INACTIVE_STATUSES)
        if inactive:
            raise CatalogError(f"rule {rule_id}: active resolution depends on inactive sources: {', '.join(inactive)}")

    if status == "review-required":
        return

    ranks = {role: index for index, role in enumerate(scope_precedence[scope])}
    active_rule_sources = [
        source_id
        for source_id in rule["sources"]
        if sources[source_id]["status"] in ACTIVE_STATUSES
    ]
    ranked = [(ranks.get(sources[source_id]["role"], 10_000), source_id) for source_id in active_rule_sources]
    best_rank = min(rank for rank, _ in ranked)
    governing_ranks = [ranks.get(sources[source_id]["role"], 10_000) for source_id in governing]
    preferred = {source_id for rank, source_id in ranked if rank == best_rank}
    if min(governing_ranks) != best_rank or set(governing) != preferred:
        raise CatalogError(
            f"rule {rule_id}: governing sources do not respect current scope precedence; "
            f"expected {sorted(preferred)}"
        )


def source_map(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {source["id"]: source for source in catalog["sources"]}


def rule_map(
    catalog: dict[str, Any],
    *,
    allow_review: bool = False,
) -> dict[str, dict[str, Any]]:
    rules = {rule["id"]: rule for rule in catalog["rules"]}
    if not allow_review:
        pending = sorted(
            rule_id
            for rule_id, rule in rules.items()
            if rule["resolution"]["status"] != "resolved"
        )
        if pending:
            raise CatalogError(
                "normative rules require review before use: " + ", ".join(pending)
            )
    return rules


def get_rule(
    catalog: dict[str, Any],
    rule_id: str,
    *,
    allow_review: bool = False,
) -> dict[str, Any]:
    try:
        rule = rule_map(catalog, allow_review=allow_review)[rule_id]
    except KeyError as exc:
        raise CatalogError(f"unknown normative rule: {rule_id}") from exc
    return rule


def source_label(catalog: dict[str, Any], rule: dict[str, Any]) -> str:
    sources = source_map(catalog)
    resolution = rule["resolution"]
    governing = " / ".join(sources[source_id]["title"] for source_id in resolution["governing_sources"])
    extra_ids = resolution.get("constraint_sources", []) + resolution.get("supporting_sources", [])
    if not extra_ids:
        return governing
    extras = " / ".join(sources[source_id]["title"] for source_id in extra_ids)
    return f"{governing} · complemento: {extras}"


def emit_web_module(catalog: dict[str, Any], output: Path) -> None:
    rule_map(catalog)
    payload = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "// Generated from normativa/catalog.json and normativa/precedence.json.\n"
        f"export const normativeCatalog={payload};\n"
        "export const normativeRules=Object.fromEntries(normativeCatalog.rules.map(rule=>[rule.id,rule]));\n"
        "export const normativeSources=Object.fromEntries(normativeCatalog.sources.map(source=>[source.id,source]));\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and export the UFC normative catalog.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--precedence", type=Path, default=DEFAULT_PRECEDENCE)
    parser.add_argument("--emit-web", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = load_catalog(args.catalog, args.precedence)
    if args.emit_web:
        emit_web_module(catalog, args.emit_web)
    print(
        f"Normative catalog valid: {len(catalog['sources'])} sources, "
        f"{len(catalog['rules'])} rules, reviewed {catalog['reviewed_at']}, "
        f"precedence reviewed {catalog['precedence_reviewed_at']}."
    )


if __name__ == "__main__":
    main()
