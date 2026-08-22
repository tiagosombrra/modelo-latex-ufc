#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    label: str
    command: tuple[str, ...]
    modes: tuple[str, ...] = ("pr", "release")
    depends: tuple[str, ...] = ()


@dataclass
class Result:
    name: str
    label: str
    status: str
    command: list[str]
    duration_seconds: float
    exit_code: int | None
    log: str
    reason: str = ""


CHECKS = (
    Check("repository", "Repository audit", ("python3", "tests/v2-repository-audit.py")),
    Check("validator-source", "PDF validator sources", ("python3", "tests/checks/validator_source.py")),
    Check("reference", "Reference document", ("sh", "tests/v2-reference-check.sh")),
    Check("reference-corpus", "Reference corpus", ("sh", "tests/v2-reference-corpus-check.sh"), depends=("reference",)),
    Check("pdf-validator", "UFC PDF validator", ("sh", "tests/v2-pdf-validator-check.sh", "documento.pdf"), depends=("reference",)),
    Check("pdfa", "Reference PDF/A-2b", ("sh", "tests/v2-pdfa-check.sh", "documento.pdf"), modes=("release",), depends=("reference",)),
    Check("distribution-source", "Distribution source", ("sh", "tests/v2-distribution-check.sh")),
    Check("layout", "Layout", ("sh", "tests/v2-layout-check.sh")),
    Check("font-config", "Font configuration", ("sh", "tests/v2-font-config-check.sh")),
    Check("pdf-geometry", "PDF geometry", ("sh", "tests/v2-pdf-geometry-check.sh")),
    Check("math", "Mathematics", ("sh", "tests/v2-math-check.sh")),
    Check("normative-complement", "Normative complement", ("sh", "tests/v2-normative-complement-check.sh")),
    Check("pretextual", "Pre-textual elements", ("sh", "tests/v2-pretextual-check.sh")),
    Check("duplex-pretextual", "Duplex pre-textual elements", ("sh", "tests/v2-duplex-pretextual-check.sh")),
    Check("object-geometry", "Object geometry", ("sh", "tests/v2-object-geometry-check.sh")),
    Check("code-typography", "Code typography", ("sh", "tests/v2-code-typography-check.sh")),
    Check("table-ibge", "IBGE tables", ("sh", "tests/v2-table-ibge-check.sh")),
    Check("objects", "Academic objects", ("sh", "tests/v2-object-check.sh")),
    Check("minted", "Minted objects", ("sh", "tests/v2-minted-check.sh")),
    Check("algorithm-numbering", "Algorithm numbering", ("sh", "tests/v2-algorithm-numbering-check.sh")),
    Check("documentary-source", "Documentary sources", ("sh", "tests/v2-documentary-source-check.sh")),
    Check("bibliography", "Bibliography", ("sh", "tests/v2-bibliography-check.sh")),
    Check("reference-spacing", "Reference spacing", ("sh", "tests/v2-reference-spacing-check.sh")),
    Check("project", "Research project", ("sh", "tests/v2-project-check.sh")),
    Check("profiles", "Document profiles", ("sh", "tests/v2-profile-matrix-check.sh")),
    Check("profile-pdfa", "Profile PDF/A-2b", ("sh", "tests/v2-profile-pdfa-check.sh"), modes=("release",), depends=("profiles",)),
    Check("posttextual-compat", "Post-textual compatibility", ("sh", "tests/v2-posttextual-compat-check.sh")),
    Check("duplex-posttextual", "Duplex post-textual elements", ("sh", "tests/v2-duplex-posttextual-check.sh")),
    Check("build-path", "Build path", ("sh", "tests/v2-build-path-check.sh")),
    Check("multivolume", "Multi-volume documents", ("sh", "tests/v2-multivolume-check.sh")),
    Check("catalog-card", "Catalog card", ("sh", "tests/v2-catalog-card-check.sh")),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run UFCtex validation as one coordinated gate.")
    parser.add_argument("--mode", choices=("pr", "release"), default="pr")
    parser.add_argument("--only", help="Comma-separated check names.")
    parser.add_argument("--report-dir", default="artifacts/validation")
    parser.add_argument("--list", action="store_true", help="List checks and exit.")
    return parser.parse_args()


def selected_checks(mode: str, only: str | None) -> list[Check]:
    available = [check for check in CHECKS if mode in check.modes]
    if not only:
        return available

    requested = {item.strip() for item in only.split(",") if item.strip()}
    known = {check.name for check in available}
    unknown = sorted(requested - known)
    if unknown:
        raise SystemExit("Unknown checks: " + ", ".join(unknown))

    by_name = {check.name: check for check in available}

    def add_with_dependencies(name: str, target: set[str]) -> None:
        if name in target:
            return
        for dependency in by_name[name].depends:
            if dependency in by_name:
                add_with_dependencies(dependency, target)
        target.add(name)

    expanded: set[str] = set()
    for name in requested:
        add_with_dependencies(name, expanded)
    return [check for check in available if check.name in expanded]


def run_check(check: Check, report_dir: Path, results: dict[str, Result]) -> Result:
    blocked = [dependency for dependency in check.depends if dependency in results and results[dependency].status != "PASS"]
    log_path = report_dir / "checks" / f"{check.name}.log"
    if blocked:
        result = Result(
            name=check.name,
            label=check.label,
            status="SKIP",
            command=list(check.command),
            duration_seconds=0.0,
            exit_code=None,
            log=str(log_path),
            reason="blocked by: " + ", ".join(blocked),
        )
        log_path.write_text(result.reason + "\n", encoding="utf-8")
        return result

    start = time.monotonic()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    try:
        completed = subprocess.run(
            check.command,
            cwd=Path.cwd(),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
        output = completed.stdout
        exit_code = completed.returncode
    except FileNotFoundError as error:
        output = f"{error}\n"
        exit_code = 127

    duration = time.monotonic() - start
    log_path.write_text(output, encoding="utf-8")
    return Result(
        name=check.name,
        label=check.label,
        status="PASS" if exit_code == 0 else "FAIL",
        command=list(check.command),
        duration_seconds=round(duration, 3),
        exit_code=exit_code,
        log=str(log_path),
    )


def write_reports(report_dir: Path, mode: str, results: list[Result], complete: bool) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    failed = any(item.status == "FAIL" for item in results)
    skipped = any(item.status == "SKIP" for item in results)
    state = "FAIL" if complete and (failed or skipped) else "PASS" if complete else "RUNNING"
    payload = {
        "mode": mode,
        "complete": complete,
        "result": state,
        "checks": [asdict(item) for item in results],
    }
    (report_dir / "validation-report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# UFCtex validation",
        "",
        f"- Mode: `{mode}`",
        f"- Complete: `{str(complete).lower()}`",
        f"- Result: **{state}**",
        "",
        "| Status | Check | Duration |",
        "|---|---|---:|",
    ]
    for item in results:
        duration = f"{item.duration_seconds:.1f}s" if item.duration_seconds else "-"
        lines.append(f"| {item.status} | {item.label} | {duration} |")
    failures = [item for item in results if item.status == "FAIL"]
    skipped_results = [item for item in results if item.status == "SKIP"]
    if failures:
        lines.extend(["", "## Failures", ""])
        for item in failures:
            lines.append(f"- `{item.name}`: exit {item.exit_code}; log `{item.log}`")
    if skipped_results:
        lines.extend(["", "## Skipped", ""])
        for item in skipped_results:
            lines.append(f"- `{item.name}`: {item.reason}")
    (report_dir / "validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_failure_tail(result: Result, lines: int = 35) -> None:
    path = Path(result.log)
    if not path.is_file():
        return
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"\n--- {result.name}: last {min(lines, len(content))} log lines ---")
    for line in content[-lines:]:
        print(line)


def main() -> int:
    args = parse_args()
    checks = selected_checks(args.mode, args.only)

    if args.list:
        for check in checks:
            print(f"{check.name:24} {check.label}")
        return 0

    report_dir = Path(args.report_dir)
    (report_dir / "checks").mkdir(parents=True, exist_ok=True)

    results_by_name: dict[str, Result] = {}
    ordered_results: list[Result] = []
    write_reports(report_dir, args.mode, ordered_results, complete=False)

    print(f"UFCtex validation: mode={args.mode}, checks={len(checks)}")
    for index, check in enumerate(checks, 1):
        print(f"[{index:02}/{len(checks):02}] {check.label} ...", flush=True)
        result = run_check(check, report_dir, results_by_name)
        results_by_name[check.name] = result
        ordered_results.append(result)
        write_reports(report_dir, args.mode, ordered_results, complete=False)
        suffix = f" ({result.duration_seconds:.1f}s)" if result.duration_seconds else ""
        print(f"         {result.status}{suffix}")
        if result.status == "FAIL":
            print_failure_tail(result)

    write_reports(report_dir, args.mode, ordered_results, complete=True)

    passed = sum(item.status == "PASS" for item in ordered_results)
    failed = sum(item.status == "FAIL" for item in ordered_results)
    skipped = sum(item.status == "SKIP" for item in ordered_results)
    print("\nValidation summary")
    print(f"PASS={passed} FAIL={failed} SKIP={skipped}")
    print(f"Report: {report_dir / 'validation-report.md'}")
    return 1 if failed or skipped else 0


if __name__ == "__main__":
    sys.exit(main())
