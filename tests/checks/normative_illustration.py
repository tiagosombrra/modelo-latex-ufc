#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from normative_full import load_full_contract
from pdf_measurement import PDFMeasurementError, Box, bbox_pages, normalize, typography_runs

SCENARIO = ROOT / "standards" / "illustration-final-pdf-scenario.json"
LOCATOR_TYPOGRAPHY = ROOT / "standards" / "locator-audit-typography-paragraphs.json"
LOCATOR_OBJECTS = ROOT / "standards" / "locator-audit-objects-equations.json"
LOCATOR_FINAL = ROOT / "standards" / "locator-audit-final.json"
VALIDATION_POLICY = ROOT / "standards" / "validation-reference-policy.json"

RULES = [
    "illustration.identification.font-size",
    "font.size.reduced.illustration-source",
    "illustration.caption.bounds",
    "illustration.source.bounds",
    "illustration.note.bounds",
    "illustration.identification.position",
    "illustration.source.position",
    "illustration.note.position",
]

EXPECTED = {
    "illustration.identification.font-size": {"pt": 12},
    "font.size.reduced.illustration-source": {"pt": 10},
    "illustration.caption.bounds": {"caption_within_object_width": True},
    "illustration.source.bounds": {"source_within_object_width": True},
    "illustration.note.bounds": {"note_within_object_width": True},
    "illustration.identification.position": {"position": "above"},
    "illustration.source.position": {"position": "below-object"},
    "illustration.note.position": {"position": "after-source"},
}


def fail(message: str) -> None:
    raise SystemExit(f"illustration validation failed: {message}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} must contain an object")
    return value


def ruleset(document: dict[str, Any], ruleset_id: str) -> dict[str, Any]:
    matches = [
        item for item in document.get("rulesets", [])
        if isinstance(item, dict) and item.get("id") == ruleset_id
    ]
    if len(matches) != 1:
        fail(f"locator ruleset {ruleset_id}: expected one match, found {len(matches)}")
    return matches[0]


def unique_word(pages: list[Any], marker: str) -> tuple[Any, Any]:
    wanted = normalize(marker)
    matches = [
        (page, word) for page in pages for word in page.words
        if normalize(word.text) == wanted
    ]
    if len(matches) != 1:
        fail(f"marker {marker!r}: expected one word, found {len(matches)}")
    return matches[0]


def unique_run(runs: list[Any], marker: str) -> Any:
    wanted = normalize(marker)
    matches = [run for run in runs if wanted in normalize(run.text)]
    if len(matches) != 1:
        fail(f"typography marker {marker!r}: expected one run, found {len(matches)}")
    return matches[0]


def block_box(pages: list[Any], start_marker: str, end_marker: str) -> tuple[Any, Box]:
    page_a, start = unique_word(pages, start_marker)
    page_b, end = unique_word(pages, end_marker)
    if page_a.index != page_b.index:
        fail(f"block markers {start_marker}/{end_marker} must share one page")
    top = min(start.box.y_min, end.box.y_min)
    bottom = max(start.box.y_max, end.box.y_max)
    words = [
        word for word in page_a.words
        if top - 0.5 <= word.box.center_y <= bottom + 0.5
    ]
    if not words:
        fail(f"block {start_marker}/{end_marker}: no words found")
    return page_a, Box(
        min(word.box.x_min for word in words),
        min(word.box.y_min for word in words),
        max(word.box.x_max for word in words),
        max(word.box.y_max for word in words),
    )


def record(rule_id: str, passed: bool, measured: Any, tool: str, tolerance: float | None = None) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "status": "PASS" if passed else "FAIL",
        "expected": EXPECTED[rule_id],
        "measured": measured,
        "tool": tool,
        "tolerance": tolerance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure bounded illustration evidence.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--commit-sha")
    args = parser.parse_args()
    if not args.pdf.is_file():
        fail(f"PDF not found: {args.pdf}")

    scenario = load_json(SCENARIO)
    loc_typ = load_json(LOCATOR_TYPOGRAPHY)
    loc_obj = load_json(LOCATOR_OBJECTS)
    loc_final = load_json(LOCATOR_FINAL)
    validation = load_json(VALIDATION_POLICY)

    if scenario.get("schema_version") != 1 or scenario.get("component") != "illustration-final-pdf" or scenario.get("rules") != RULES:
        fail("invalid scenario schema/component/scope")


    reduced = ruleset(loc_typ, "typography.reduced-font").get("rule_ids", [])
    title_size = ruleset(loc_typ, "typography.illustration-identification-title").get("rule_ids", [])
    if RULES[1] not in set(reduced):
        fail("illustration source reduced-font locator scope drift")
    if RULES[0] not in set(title_size):
        fail("illustration identification/title locator scope drift")
    if ruleset(loc_final, "objects.illustration-bounds").get("rule_ids") != RULES[2:5]:
        fail("illustration bounds locator scope drift")
    if ruleset(loc_obj, "objects.illustration-presentation").get("rule_ids") != RULES[5:8]:
        fail("illustration presentation locator scope drift")

    contract = load_full_contract()
    contract_rules = {rule["id"]: rule for rule in contract["rules"]}
    values = {rule_id: contract_rules[rule_id]["values"] for rule_id in RULES}
    if values != EXPECTED:
        fail(f"illustration contract values drifted: {values}")

    tolerances = validation.get("tolerances", {})
    try:
        font_tol = float(tolerances["font_size_pt"])
        horiz_tol = float(tolerances["horizontal_position_pt"])
        vert_tol = float(tolerances["vertical_position_pt"])
    except (KeyError, TypeError, ValueError) as exc:
        fail(f"invalid validation tolerances: {exc}")
    allowed_tools = set(validation.get("tools", {}).values())
    if not {"pdftotext -bbox-layout", "pdftohtml -xml -zoom 1.0"} <= allowed_tools:
        fail("required illustration tools left validation policy")

    fixture = scenario.get("fixture", {})
    markers = scenario.get("markers", {})
    if fixture.get("engine") != "pdflatex" or fixture.get("passes") != 2:
        fail("fixture engine/pass contract drift")
    try:
        expected_width = float(fixture["object_width_mm"]) * 72.0 / 25.4
    except (KeyError, TypeError, ValueError) as exc:
        fail(f"invalid controlled object width: {exc}")

    try:
        pages = bbox_pages(args.pdf)
        runs = typography_runs(args.pdf)
    except PDFMeasurementError as exc:
        fail(str(exc))
    if len(pages) != 1:
        fail(f"fixture must contain one page, got {len(pages)}")

    page_l, left = unique_word(pages, markers["object_left_top"])
    page_r, right = unique_word(pages, markers["object_right_bottom"])
    if page_l.index != page_r.index:
        fail("object edge markers must share one page")
    object_box = Box(
        left.box.x_min,
        min(left.box.y_min, right.box.y_min),
        right.box.x_max,
        max(left.box.y_max, right.box.y_max),
    )
    width_delta = abs(object_box.width - expected_width)
    if width_delta > horiz_tol:
        fail(f"controlled object-width calibration drift: delta={width_delta:.4f}pt")

    cap_page, cap_box = block_box(pages, markers["caption_start"], markers["caption_end"])
    src_page, src_box = block_box(pages, markers["source_start"], markers["source_end"])
    note_page, note_box = block_box(pages, markers["note_start"], markers["note_end"])
    if len({page_l.index, cap_page.index, src_page.index, note_page.index}) != 1:
        fail("fixture blocks must share one page")

    cap_run = unique_run(runs, markers["caption_start"])
    src_run = unique_run(runs, markers["source_start"])
    cap_font_delta = abs(cap_run.font_size - 12.0)
    src_font_delta = abs(src_run.font_size - 10.0)

    def within(box: Box) -> tuple[bool, dict[str, float]]:
        left_over = max(0.0, object_box.x_min - box.x_min)
        right_over = max(0.0, box.x_max - object_box.x_max)
        return left_over <= horiz_tol and right_over <= horiz_tol, {
            "block_x_min_pt": round(box.x_min, 4),
            "block_x_max_pt": round(box.x_max, 4),
            "object_x_min_pt": round(object_box.x_min, 4),
            "object_x_max_pt": round(object_box.x_max, 4),
            "left_overflow_pt": round(left_over, 4),
            "right_overflow_pt": round(right_over, 4),
        }

    cap_within, cap_bounds = within(cap_box)
    src_within, src_bounds = within(src_box)
    note_within, note_bounds = within(note_box)

    evidence = [
        record(RULES[0], cap_font_delta <= font_tol, {"font_pt": round(cap_run.font_size, 4), "delta_pt": round(cap_font_delta, 4), "family_observation": cap_run.family}, "pdftohtml -xml -zoom 1.0", font_tol),
        record(RULES[1], src_font_delta <= font_tol, {"font_pt": round(src_run.font_size, 4), "delta_pt": round(src_font_delta, 4), "family_observation": src_run.family}, "pdftohtml -xml -zoom 1.0", font_tol),
        record(RULES[2], cap_within, cap_bounds, "pdftotext -bbox-layout", horiz_tol),
        record(RULES[3], src_within, src_bounds, "pdftotext -bbox-layout", horiz_tol),
        record(RULES[4], note_within, note_bounds, "pdftotext -bbox-layout", horiz_tol),
        record(RULES[5], cap_box.y_max <= object_box.y_min + vert_tol, {"caption_y_max_pt": round(cap_box.y_max, 4), "object_y_min_pt": round(object_box.y_min, 4), "exact_gap_not_frozen": True}, "pdftotext -bbox-layout", vert_tol),
        record(RULES[6], src_box.y_min >= object_box.y_max - vert_tol, {"source_y_min_pt": round(src_box.y_min, 4), "object_y_max_pt": round(object_box.y_max, 4), "exact_gap_not_frozen": True}, "pdftotext -bbox-layout", vert_tol),
        record(RULES[7], note_box.y_min >= src_box.y_max - vert_tol, {"note_y_min_pt": round(note_box.y_min, 4), "source_y_max_pt": round(src_box.y_max, 4), "exact_gap_not_frozen": True}, "pdftotext -bbox-layout", vert_tol),
    ]

    counts = Counter(item["status"] for item in evidence)
    result = "PASS" if counts.get("FAIL", 0) == 0 else "FAIL"
    payload = {
        "schema_version": 1,
        "component": "illustration-final-pdf",
        "source_commit_sha": args.commit_sha or "",
        "pdf": str(args.pdf),
        "result": result,
        "object_calibration": {"expected_width_pt": round(expected_width, 4), "measured_width_pt": round(object_box.width, 4), "delta_pt": round(width_delta, 4)},
        "evidence": evidence,
        "proof_state_changed": False,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"VALIDATION-EVIDENCE illustration-final-pdf-summary PASS={counts.get('PASS', 0)} FAIL={counts.get('FAIL', 0)} object_width_pt={object_box.width:.4f}")
    for item in evidence:
        print(f"VALIDATION-EVIDENCE rule={item['rule_id']} status={item['status']} expected={json.dumps(item['expected'], ensure_ascii=False, sort_keys=True)} measured={json.dumps(item['measured'], ensure_ascii=False, sort_keys=True)}")
    if result != "PASS":
        fail("one or more illustration predicates failed")


if __name__ == "__main__":
    main()
