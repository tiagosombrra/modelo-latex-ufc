#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "tools" / "validate-ufc-pdf.py"
APP = ROOT / "validator" / "app.js"
INDEX = ROOT / "validator" / "index.html"
NORMATIVE_TOOL = ROOT / "tools" / "normative_catalog.py"
NORMATIVE_ATOMIC_TOOL = ROOT / "tools" / "normative_atomic.py"
NORMATIVE_FULL_TOOL = ROOT / "tools" / "normative_full.py"
NORMATIVE_COVERAGE = ROOT / "tests" / "checks" / "normative_coverage.py"
NORMATIVE_COVERAGE_AUDIT = ROOT / "tests" / "checks" / "normative_coverage_audit.py"
NORMATIVE_CURRENCY = ROOT / "tests" / "checks" / "normative_currency.py"
NORMATIVE_PRECEDENCE = ROOT / "tests" / "checks" / "normative_precedence.py"
NORMATIVE_SOURCES = ROOT / "tests" / "checks" / "normative_sources.py"
NORMATIVE_ATOMICITY = ROOT / "tests" / "checks" / "normative_atomicity.py"
NORMATIVE_ATOMIC_CONTRACT = ROOT / "tests" / "checks" / "normative_atomic_contract.py"
NORMATIVE_FULL_CONTRACT = ROOT / "tests" / "checks" / "normative_full_contract.py"


def fail(message: str) -> None:
    raise SystemExit(f"Validator source check failed: {message}")


def run_source_check(path: Path, label: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        fail(f"{label}: {completed.stdout}{completed.stderr}")
    if completed.stdout:
        print(completed.stdout.strip())


def main() -> None:
    for path in (
        CLI,
        NORMATIVE_TOOL,
        NORMATIVE_ATOMIC_TOOL,
        NORMATIVE_FULL_TOOL,
        NORMATIVE_COVERAGE,
        NORMATIVE_COVERAGE_AUDIT,
        NORMATIVE_CURRENCY,
        NORMATIVE_PRECEDENCE,
        NORMATIVE_SOURCES,
        NORMATIVE_ATOMICITY,
        NORMATIVE_ATOMIC_CONTRACT,
        NORMATIVE_FULL_CONTRACT,
    ):
        py_compile.compile(str(path), doraise=True)

    run_source_check(NORMATIVE_TOOL, "normative catalog")
    run_source_check(NORMATIVE_PRECEDENCE, "normative precedence")
    run_source_check(NORMATIVE_SOURCES, "normative sources")
    run_source_check(NORMATIVE_CURRENCY, "normative currency")
    run_source_check(NORMATIVE_ATOMICITY, "normative atomicity")
    run_source_check(NORMATIVE_ATOMIC_CONTRACT, "normative atomic contract")
    run_source_check(NORMATIVE_FULL_TOOL, "full normative loader")
    run_source_check(NORMATIVE_FULL_CONTRACT, "full normative contract")
    run_source_check(NORMATIVE_COVERAGE, "normative coverage")

    completed = subprocess.run(
        [sys.executable, str(CLI), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("CLI cannot load the normative catalog")

    app = APP.read_text(encoding="utf-8")
    cli = CLI.read_text(encoding="utf-8")
    html = INDEX.read_text(encoding="utf-8")

    if "pdfjs-dist@6.2.108" not in app:
        fail("PDF.js version is not pinned to 6.2.108")
    if 'from "./normative-catalog.js"' not in app:
        fail("Web/Lite does not consume the generated normative catalog")
    if "from normative_catalog import" not in cli:
        fail("CLI does not consume the normative catalog")
    if "A4=(595.276,841.89)" in cli or "A4=[595.276,841.89]" in app:
        fail("validator geometry is hard-coded instead of catalog-driven")

    forbidden = r"FormData\(|XMLHttpRequest|sendBeacon\(|WebSocket\("
    if re.search(forbidden, app):
        fail("browser code contains a network upload API")

    if "não é enviado para servidor" not in html:
        fail("local-processing disclosure is missing")
    for marker in ('id="normative-base"', 'id="norm-reviewed"', 'id="norm-sources"'):
        if marker not in html:
            fail(f"normative-base UI marker is missing: {marker}")

    node = shutil.which("node")
    if not node:
        fail("Node.js is required for JavaScript syntax validation")

    completed = subprocess.run([node, "--check", str(APP)], check=False)
    if completed.returncode != 0:
        fail("validator/app.js has invalid JavaScript syntax")

    with tempfile.TemporaryDirectory() as temp_dir:
        module = Path(temp_dir) / "normative-catalog.mjs"
        completed = subprocess.run(
            [sys.executable, str(NORMATIVE_TOOL), "--emit-web", str(module)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            fail("normative web catalog generation failed")
        completed = subprocess.run([node, "--check", str(module)], check=False)
        if completed.returncode != 0:
            fail("generated normative web catalog has invalid JavaScript syntax")

    print("Validator sources and normative contracts validated.")


if __name__ == "__main__":
    main()
