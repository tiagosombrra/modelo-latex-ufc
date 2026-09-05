#!/bin/sh
set -eu

python3 tests/checks/normative_objects_scope.py

fixture="tests/documents/object-geometry.tex"
flags="-interaction=nonstopmode -halt-on-error -file-line-error"

cleanup() {
  rm -f objeto-geometria-*.aux objeto-geometria-*.log objeto-geometria-*.out objeto-geometria-*.pdf
}
trap cleanup EXIT INT TERM

for engine in pdflatex lualatex; do
  job="objeto-geometria-$engine"
  echo "Validating object geometry with $engine..."

  for pass in 1 2; do
    "$engine" -jobname="$job" $flags "$fixture" > /tmp/abntexto-ufc-object-geometry.log 2>&1 || {
      cat /tmp/abntexto-ufc-object-geometry.log
      exit 1
    }
  done

  warnings=$(grep -E 'LaTeX Warning:|Package [^ ]+ Warning:|Class [^ ]+ Warning:|Overfull \\hbox|Overfull \\vbox' "$job.log" | \
    grep -vF -e 'Class abntexto-ufc Warning: Times New Roman not found; using TeX Gyre Termes' || true)
  if [ -n "$warnings" ]; then
    printf '%s\n' "$warnings"
    echo "$job: unrecognized warning or overflow."
    exit 1
  fi

  python3 - "$job.log" <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')

def dim(name):
    match = re.search(rf'{re.escape(name)}=([0-9.]+)pt', text)
    if not match:
        raise SystemExit(f'metric missing: {name}')
    return float(match.group(1))

def scalar(name):
    match = re.search(rf'{re.escape(name)}=([0-9.]+)', text)
    if not match:
        raise SystemExit(f'metric missing: {name}')
    return float(match.group(1))

def close(name, actual, expected, tolerance=0.06):
    if abs(actual - expected) > tolerance:
        raise SystemExit(f'{name}: expected {expected:.4f}, measured {actual:.4f}')

pt_per_cm = 72.27 / 2.54
pt_per_bp = 72.27 / 72.0
expected_width = 6.0 * pt_per_cm
expected_body = 12.0 * pt_per_bp
expected_small = 10.0 * pt_per_bp

close('object physical width', dim('UFC-OBJECT-CONTENT-WIDTH'), expected_width)
for name in ('UFC-OBJECT-TITLE-WIDTH', 'UFC-OBJECT-SOURCE-WIDTH', 'UFC-OBJECT-NOTE-WIDTH'):
    close(name, dim(name), expected_width)
close('UFC-OBJECT-TITLE-FONTSIZE', scalar('UFC-OBJECT-TITLE-FONTSIZE'), expected_body)
for name in ('UFC-OBJECT-SOURCE-FONTSIZE', 'UFC-OBJECT-NOTE-FONTSIZE'):
    close(name, scalar(name), expected_small)
PY

done

sh tests/integration/illustration-evidence.sh
sh tests/integration/table-typography-equation-evidence.sh
sh tests/integration/table-ibge-vector-evidence.sh

echo 'Object geometry gate completed.'
