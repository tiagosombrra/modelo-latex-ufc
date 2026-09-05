#!/bin/sh
set -eu

fixture="tests/documents/ibge-table.tex"
flags="-interaction=nonstopmode -halt-on-error -file-line-error"

cleanup() {
  rm -f tabela-ibge-*.aux tabela-ibge-*.log tabela-ibge-*.out tabela-ibge-*.pdf tabela-ibge-*.lot
}
trap cleanup EXIT INT TERM

for token in '\toprule' '\midrule' '\bottomrule' 'row{even}' 'remark{Fonte}' 'remark{Nota}' 'tables = tabularray'; do
  grep -Fq "$token" "$fixture" || {
    echo "IBGE table: required fixture structure is missing: $token"
    exit 1
  }
done

if grep -Eq '(^|[^[:alpha:]])(vlines|hlines)([^[:alpha:]]|$)' "$fixture"; then
  echo 'IBGE table: numeric tables must not use closed side borders or a body grid.'
  exit 1
fi

for engine in pdflatex lualatex; do
  job="tabela-ibge-$engine"
  echo "Validating table IBGE with $engine..."

  for pass in 1 2; do
    "$engine" -jobname="$job" $flags "$fixture" > "/tmp/$job.out" 2>&1 || {
      cat "/tmp/$job.out"
      exit 1
    }
  done

  warnings=$(grep -E 'LaTeX Warning:|Package [^ ]+ Warning:|Class [^ ]+ Warning:|Overfull \\hbox|Overfull \\vbox' "$job.log" || true)
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

def metric(name):
    values = [float(v) for v in re.findall(rf'{re.escape(name)}=([0-9.]+)', text)]
    if not values:
        raise SystemExit(f'metric missing: {name}')
    return values

def assert_all(name, expected, tolerance=0.06):
    for value in metric(name):
        if abs(value - expected) > tolerance:
            raise SystemExit(f'{name}: expected {expected:.4f}, measured {value:.4f}')

pt_per_bp = 72.27 / 72.0
assert_all('UFC-IBGE-BODY-FONTSIZE', 12.0)
assert_all('UFC-IBGE-CAPTION-FONTSIZE', 12.0 * pt_per_bp)
assert_all('UFC-IBGE-SOURCE-FONTSIZE', 10.0 * pt_per_bp)
assert_all('UFC-IBGE-NOTE-FONTSIZE', 10.0 * pt_per_bp)
PY

  sh tests/integration/font-embedding.sh "$job.pdf"

  pdftotext -layout "$job.pdf" "/tmp/$job.txt"
  python3 - "/tmp/$job.txt" "$job" <<'PY'
import re
import sys
import unicodedata
from pathlib import Path

path, job = sys.argv[1:]
raw = Path(path).read_text(encoding='utf-8', errors='replace')
raw = re.sub(r'(?<=\w)-[ \t]*\n[ \t]*(?=\w)', '', raw)
text = re.sub(r'\s+', ' ', unicodedata.normalize('NFC', raw)).strip()

for marker in (
    'Indicadores numéricos de teste',
    'Ano',
    '2024',
    '2025',
    '2026',
    'Fonte:',
    'Elaboração própria',
    'Nota:',
    'Valores sintéticos para validação',
):
    if marker not in text:
        raise SystemExit(f'{job}: required table content is missing: {marker}')
PY
done

echo 'IBGE table subset gate completed.'
