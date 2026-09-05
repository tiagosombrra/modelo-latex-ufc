#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CHECKS = (
    "tests/checks/canonical_identity.py",
    "tests/checks/repository_contract.py",
    "tests/checks/phase_governance.py",
    "tests/checks/engineering_language.py",
    "tests/checks/validator_source.py",
    "tests/checks/normative_rule_migrations.py",
    "tests/checks/normative_objects_scope.py",
    "tests/checks/reference_guide_contract.py",
    "tests/checks/profile_matrix_contract.py",
    "tests/checks/test_surface_integrity.py",
    "tests/checks/v3_api_residual.py",
    "tests/checks/librarian_review_contract.py",
)


def fail(message: str) -> None:
    raise SystemExit(f"Static gate failed: {message}")


def require_command(command: str) -> None:
    if shutil.which(command) is None:
        fail(f"required command is unavailable: {command}")


def tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        fail(completed.stderr.decode("utf-8", errors="replace").strip() or "git ls-files failed")
    return [ROOT / item.decode("utf-8") for item in completed.stdout.split(b"\0") if item]


def repository_status() -> bytes:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        fail(completed.stderr.decode("utf-8", errors="replace").strip() or "git status failed")
    return completed.stdout


def run(command: list[str], label: str) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.returncode != 0:
        fail(f"{label} exited with {completed.returncode}")


def check_python(paths: Iterable[Path]) -> int:
    count = 0
    for path in paths:
        if path.suffix != ".py":
            continue
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path.relative_to(ROOT)), "exec")
        except (OSError, UnicodeError, SyntaxError) as exc:
            fail(f"Python source error in {path.relative_to(ROOT)}: {exc}")
        count += 1
    return count


def check_json(paths: Iterable[Path]) -> int:
    count = 0
    for path in paths:
        if path.suffix != ".json":
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            fail(f"JSON parse error in {path.relative_to(ROOT)}: {exc}")
        count += 1
    return count


def check_shell(paths: Iterable[Path]) -> int:
    count = 0
    for path in paths:
        if path.suffix != ".sh":
            continue
        run(["sh", "-n", str(path)], f"shell syntax: {path.relative_to(ROOT)}")
        count += 1
    return count


def check_javascript(paths: Iterable[Path]) -> int:
    count = 0
    for path in paths:
        if path.suffix != ".js":
            continue
        run(["node", "--check", str(path)], f"JavaScript syntax: {path.relative_to(ROOT)}")
        count += 1
    return count


def execute_checks() -> tuple[int, int, int, int]:
    files = tracked_files()

    python_count = check_python(files)
    json_count = check_json(files)
    shell_count = check_shell(files)
    javascript_count = check_javascript(files)

    run(["git", "diff", "--check"], "working-tree diff integrity")
    run(["git", "diff", "--cached", "--check"], "index diff integrity")

    for relative in SOURCE_CHECKS:
        path = ROOT / relative
        if not path.is_file():
            fail(f"required source check is missing: {relative}")
        run([sys.executable, relative], relative)

    return python_count, json_count, shell_count, javascript_count


def main() -> None:
    for command in ("git", "sh", "node"):
        require_command(command)

    before = repository_status()
    try:
        python_count, json_count, shell_count, javascript_count = execute_checks()
    except BaseException:
        if repository_status() != before:
            fail("gate execution changed repository status while another check failed")
        raise

    if repository_status() != before:
        fail("gate execution changed repository status")

    print(
        "STATIC-GATE-EVIDENCE status=PASS "
        f"python={python_count} json={json_count} shell={shell_count} javascript={javascript_count} "
        f"source_checks={len(SOURCE_CHECKS)} side_effects=0 tex_pdf=0 network=0"
    )


if __name__ == "__main__":
    main()
