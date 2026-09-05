#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "release" / "v3-roadmap.json"
AGENTS = ROOT / "AGENTS.md"
HANDOFF = ROOT / "docs" / "HANDOFF-V3.0.0.md"
ROADMAP = ROOT / "docs" / "ROADMAP-V3.0.0.md"
CORRECTION_PLAN = ROOT / "docs" / "V3-CORRECTION-PLAN.md"

EXPECTED_PHASES = [
    "regression-audit",
    "core-corrections",
    "reference-pdf-validation",
    "scientific-article",
    "final-certification",
    "release",
]


def fail(message: str) -> int:
    print(f"Phase governance contract failed: {message}")
    return 1


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Phase governance contract failed: cannot read {path}: {exc}")
    if not isinstance(value, dict):
        raise SystemExit(f"Phase governance contract failed: {path} must contain an object")
    return value


def require_document_contract(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Phase governance contract failed: missing {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    folded = text.casefold()
    for concept in ("material advance", "phase-end regression"):
        if concept not in folded:
            raise SystemExit(
                f"Phase governance contract failed: {path.relative_to(ROOT)} "
                f"does not encode required concept {concept!r}"
            )
    return text


def main() -> int:
    state = load_json(STATE)
    if state.get("schema_version", 0) < 8:
        return fail("v3-roadmap schema must protect progress/regression governance")

    policies = state.get("policies")
    if not isinstance(policies, dict):
        return fail("policies object is missing")

    required_true = {
        "documentation_updated_on_every_material_advance",
        "phase_end_regression_required",
        "phase_transition_requires_recorded_regression_checkpoint",
    }
    for key in sorted(required_true):
        if policies.get(key) is not True:
            return fail(f"policy {key} must be true")
    if policies.get("targeted_checks_replace_phase_end_regression") is not False:
        return fail("targeted checks must not replace the phase-end regression")

    regression = state.get("phase_end_regression")
    if not isinstance(regression, dict):
        return fail("phase_end_regression object is missing")
    for key in (
        "required",
        "must_complete_before_phase_closure",
        "must_complete_before_next_phase_activation",
        "documentation_must_be_updated_after_result",
    ):
        if regression.get(key) is not True:
            return fail(f"phase_end_regression.{key} must be true")
    if regression.get("candidate") != "one-immutable-sha":
        return fail("phase-end regression must bind to one immutable SHA")
    minimum_checks = regression.get("minimum_checks")
    if not isinstance(minimum_checks, list):
        return fail("phase-end regression minimum_checks must be a list")
    for required in (
        "Static contract",
        "full relevant Linux integration",
        "phase-specific acceptance checks",
    ):
        if required not in minimum_checks:
            return fail(f"phase-end regression is missing minimum check: {required}")

    phases = state.get("phases")
    if not isinstance(phases, list):
        return fail("phases must be a list")
    phase_ids = [item.get("id") for item in phases if isinstance(item, dict)]
    if phase_ids != EXPECTED_PHASES:
        return fail(f"unexpected phase order/content: {phase_ids}")
    for phase in phases:
        if not isinstance(phase, dict):
            return fail("phase entry must be an object")
        if phase.get("phase_end_regression_required") is not True:
            return fail(f"phase {phase.get('id')} does not require an end regression")

    active = [phase for phase in phases if phase.get("status") == "ACTIVE"]
    if len(active) != 1:
        return fail(f"expected exactly one active phase, found {len(active)}")
    if active[0].get("id") != state.get("phase") or state.get("stage") != state.get("phase"):
        return fail("machine phase/stage does not match the active phase entry")

    branch = state.get("active_branch")
    if not isinstance(branch, str) or not branch.strip():
        return fail("active_branch must identify the current working branch")

    documents = {
        "AGENTS.md": require_document_contract(AGENTS),
        "docs/HANDOFF-V3.0.0.md": require_document_contract(HANDOFF),
        "docs/ROADMAP-V3.0.0.md": require_document_contract(ROADMAP),
        "docs/V3-CORRECTION-PLAN.md": require_document_contract(CORRECTION_PLAN),
    }

    if branch not in documents["docs/HANDOFF-V3.0.0.md"]:
        return fail("handoff does not record the machine-state active branch")
    if "Core Corrections" not in documents["docs/HANDOFF-V3.0.0.md"]:
        return fail("handoff does not record the active readable phase")
    if "Core Corrections" not in documents["docs/ROADMAP-V3.0.0.md"]:
        return fail("roadmap does not record the active readable phase")

    print(
        "PHASE-GOVERNANCE-EVIDENCE status=PASS "
        f"schema={state['schema_version']} phases={len(phases)} "
        f"active={state['phase']} branch={branch} "
        "material_advance_docs=required phase_end_regression=required"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
