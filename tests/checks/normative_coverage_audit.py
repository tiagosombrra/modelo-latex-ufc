#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from normative_catalog import load_catalog
from normative_full import full_rule_map, load_full_contract

AUDIT = ROOT / "normativa" / "coverage-audit.json"
PROMOTIONS_GLOB = "coverage-promotions*.json"
SOURCE_AUDIT = ROOT / "normativa" / "source-audit.json"

REQUIRED_DOMAINS = {
    "page-geometry",
    "typography",
    "paragraphs",
    "sections",
    "pretextual",
    "pagination",
    "footnotes",
    "toc",
    "citations",
    "references",
    "objects",
    "equations",
    "code-algorithms",
    "posttextual",
    "multivolume",
    "project",
    "deposit",
    "accessibility-distribution",
}

PRIORITY_GAPS = {
    "pagination.pretextual.counted-not-numbered",
    "pagination.catalog-data.not-counted",
    "pagination.textual.display-start",
    "footnote.separator.length",
    "footnote.hanging-alignment",
    "cover.required-fields",
    "title-page.required-fields",
    "approval.required-fields",
    "summary.required-elements",
    "summary.keywords.format",
    "section.primary.recto-duplex",
    "section.multiline.hanging",
    "citation.direct-short.presentation",
    "references.doi-url-access",
    "equation.numbering.right",
    "project.nbr15287.structure",
    "spine.presentation",
}


def fail(message: str) -> None:
    raise SystemExit(f"Normative coverage audit failed: {message}")


def load_promotions(audit_reviewed: date) -> tuple[dict[str, list[str]], list[str]]:
    paths = sorted((ROOT / "normativa").glob(PROMOTIONS_GLOB))
    if not paths:
        fail("no coverage promotion ledgers found")

    merged: dict[str, list[str]] = {}
    names: list[str] = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            fail(f"{path.name}: unsupported schema_version")
        try:
            reviewed = date.fromisoformat(data["reviewed_at"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit(
                f"Normative coverage audit failed: {path.name}: invalid review date: {exc}"
            ) from exc
        if reviewed < audit_reviewed:
            fail(f"{path.name}: coverage promotions are older than the N4 inventory")
        resolved = data.get("resolved_gaps")
        if not isinstance(resolved, dict):
            fail(f"{path.name}: resolved_gaps must be an object")
        duplicate = sorted(set(merged) & set(resolved))
        if duplicate:
            fail(f"duplicate gap resolutions across ledgers: {', '.join(duplicate)}")
        merged.update(resolved)
        names.append(path.name)
    return merged, names


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    source_audit = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    catalog = load_catalog()
    full_contract = load_full_contract(catalog)
    full_rules = full_rule_map(full_contract)
    known_source_ids = {source["id"] for source in catalog["sources"]}
    known_source_ids |= {source["id"] for source in source_audit.get("sources", [])}

    if audit.get("schema_version") != 1:
        fail("unsupported schema_version")
    if audit.get("phase") != "N4":
        fail("unexpected phase")
    if audit.get("phase_status") not in {"in-progress", "complete"}:
        fail("invalid phase_status")
    try:
        audit_reviewed = date.fromisoformat(audit["reviewed_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"Normative coverage audit failed: invalid review date: {exc}") from exc

    resolved, promotion_ledgers = load_promotions(audit_reviewed)

    allowed = set(audit.get("allowed_treatments", []))
    expected_allowed = {"automatic", "automatic-partial", "manual", "conditional", "not-applicable"}
    if allowed != expected_allowed:
        fail("unexpected treatment vocabulary")

    domains = audit.get("domains")
    if not isinstance(domains, dict):
        fail("domains must be an object")
    declared = set(audit.get("required_domains", []))
    if declared != REQUIRED_DOMAINS or set(domains) != REQUIRED_DOMAINS:
        missing = sorted(REQUIRED_DOMAINS - set(domains))
        extra = sorted(set(domains) - REQUIRED_DOMAINS)
        fail(f"domain coverage mismatch; missing={missing}, extra={extra}")

    runner = (ROOT / "tests" / "run.py").read_text(encoding="utf-8")
    known_gates = set(re.findall(r'Check\("([^"]+)"', runner))

    gap_ids: set[str] = set()
    for domain_id, domain in domains.items():
        existing = domain.get("existing_atomic_rules", [])
        if not isinstance(existing, list):
            fail(f"{domain_id}: existing_atomic_rules must be a list")
        unknown_atomic = sorted(set(existing) - set(full_rules))
        if unknown_atomic:
            fail(f"{domain_id}: unknown atomic rules: {', '.join(unknown_atomic)}")

        gates = domain.get("gates", [])
        if not isinstance(gates, list):
            fail(f"{domain_id}: gates must be a list")
        unknown = sorted(set(gates) - known_gates)
        if unknown:
            fail(f"{domain_id}: unknown unified gates: {', '.join(unknown)}")

        gaps = domain.get("gaps", [])
        if not isinstance(gaps, list):
            fail(f"{domain_id}: gaps must be a list")
        for gap in gaps:
            gap_id = gap.get("id")
            if not isinstance(gap_id, str) or not gap_id:
                fail(f"{domain_id}: gap without id")
            if gap_id in gap_ids:
                fail(f"duplicate gap id: {gap_id}")
            gap_ids.add(gap_id)

            if not gap.get("requirement"):
                fail(f"{gap_id}: requirement is required")
            treatment = gap.get("planned_treatment")
            if treatment not in allowed:
                fail(f"{gap_id}: invalid planned_treatment {treatment}")

            candidate_sources = gap.get("candidate_sources")
            if not isinstance(candidate_sources, list):
                fail(f"{gap_id}: candidate_sources must be a list")
            unknown_sources = sorted(set(candidate_sources) - known_source_ids)
            if unknown_sources:
                fail(f"{gap_id}: unknown candidate sources: {', '.join(unknown_sources)}")
            if not candidate_sources and gap.get("classification") not in {"project-policy", "technical-profile"}:
                fail(f"{gap_id}: source-free gap must be explicitly project-policy or technical-profile")

    missing_priority = sorted(PRIORITY_GAPS - gap_ids)
    if missing_priority:
        fail("priority N4 gaps missing from the baseline inventory: " + ", ".join(missing_priority))

    unknown_resolved = sorted(set(resolved) - gap_ids)
    if unknown_resolved:
        fail("promotions reference unknown gaps: " + ", ".join(unknown_resolved))

    promoted_targets: set[str] = set()
    for gap_id, rule_ids in resolved.items():
        if not isinstance(rule_ids, list) or not rule_ids:
            fail(f"{gap_id}: promotion must reference at least one atomic rule")
        if len(rule_ids) != len(set(rule_ids)):
            fail(f"{gap_id}: duplicate atomic rule in promotion")
        for rule_id in rule_ids:
            rule = full_rules.get(rule_id)
            if not rule:
                fail(f"{gap_id}: promoted rule does not exist: {rule_id}")
            if rule.get("phase") != "N4":
                fail(f"{gap_id}: promotion must resolve through an N4 rule: {rule_id}")
            promoted_targets.add(rule_id)

    manifest_promoted = set(full_contract["promoted_rule_ids"])
    untracked_promotions = sorted(manifest_promoted - promoted_targets)
    if untracked_promotions:
        fail("N4 atomic rules without a resolved-gap mapping: " + ", ".join(untracked_promotions))

    unresolved = gap_ids - set(resolved)
    if audit["phase_status"] == "complete" and unresolved:
        fail("N4 cannot be complete while unresolved gaps remain: " + ", ".join(sorted(unresolved)))

    print(
        "Normative coverage inventory passed: "
        f"{len(domains)} domains, {len(full_rules)} full atomic rules, "
        f"{len(gap_ids)} identified gaps, {len(resolved)} resolved through "
        f"{len(promotion_ledgers)} ledgers, {len(unresolved)} unresolved, "
        f"status={audit['phase_status']}."
    )


if __name__ == "__main__":
    main()
