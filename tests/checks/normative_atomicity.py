#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "normativa" / "catalog.json"
PLAN = ROOT / "normativa" / "atomicity-plan.json"
ATOMIC = ROOT / "normativa" / "atomic-rules.json"


def fail(message: str) -> None:
    raise SystemExit(f"Normative atomicity plan failed: {message}")


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    atomic = json.loads(ATOMIC.read_text(encoding="utf-8"))

    if plan.get("schema_version") != 1 or atomic.get("schema_version") != 1:
        fail("unsupported schema_version")
    if plan.get("statuses") != ["keep-atomic", "split", "retire-in-n4"]:
        fail("unexpected status vocabulary")

    catalog_ids = {rule["id"] for rule in catalog["rules"]}
    entries = plan.get("rules")
    if not isinstance(entries, dict) or set(entries) != catalog_ids:
        fail("atomicity plan must cover the current catalog exactly")

    manifest_parents = (
        set(atomic.get("keep_atomic", []))
        | set(atomic.get("groups", {}))
        | set(atomic.get("retire_in_n4", {}))
    )
    if manifest_parents != catalog_ids:
        fail("atomic manifest must cover the current catalog exactly")

    target_owner: dict[str, str] = {}
    split_count = 0
    target_count = 0
    for parent, entry in entries.items():
        status = entry.get("status")
        if status not in plan["statuses"]:
            fail(f"{parent}: invalid status {status}")
        targets = entry.get("targets", [])
        if status == "split":
            split_count += 1
            specs = atomic["groups"].get(parent)
            if not isinstance(specs, list) or len(specs) < 2:
                fail(f"{parent}: split group missing from atomic manifest")
            manifest_targets = [spec.get("id") for spec in specs]
            if targets != manifest_targets:
                fail(f"{parent}: plan and manifest targets differ")
            if len(targets) != len(set(targets)):
                fail(f"{parent}: duplicate targets")
            for target in targets:
                if target in catalog_ids:
                    fail(f"{parent}: atomic target collides with catalog parent {target}")
                owner = target_owner.get(target)
                if owner:
                    fail(f"atomic target {target} assigned to both {owner} and {parent}")
                target_owner[target] = parent
            target_count += len(targets)
        elif targets:
            fail(f"{parent}: only split entries may declare targets")

        if status == "retire-in-n4":
            reason = entry.get("reason")
            if not reason or atomic["retire_in_n4"].get(parent) != reason:
                fail(f"{parent}: retirement reason mismatch")

    if entries["deposit.pdfa"]["targets"] != [
        "deposit.pdfa.required",
        "pdfa.profile.project",
    ]:
        fail("PDF/A institutional requirement and project profile must be separated")
    if entries["summary.word-count"]["status"] != "split":
        fail("summary word count and keyword presence must be separate rules")
    if entries["project.standard"]["status"] != "retire-in-n4":
        fail("project.standard must be replaced by individual NBR 15287 rules")

    keep_count = sum(entry["status"] == "keep-atomic" for entry in entries.values())
    if keep_count + target_count != 100:
        fail("N3 contract must resolve to exactly 100 atomic rules before N4")

    print(
        "Normative atomicity plan passed: "
        f"{len(entries)} parent rules, {split_count} composite rules, "
        f"{target_count} split targets, {keep_count} already atomic."
    )


if __name__ == "__main__":
    main()
