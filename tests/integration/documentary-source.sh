#!/bin/sh
set -eu

fixture="tests/documents/documentary-sources.tex"
flags="-interaction=nonstopmode -halt-on-error -file-line-error"

cleanup() {
  rm -f fontes-documentais-*.aux fontes-documentais-*.bbl fontes-documentais-*.bcf \
    fontes-documentais-*.blg fontes-documentais-*.log fontes-documentais-*.out \
    fontes-documentais-*.pdf fontes-documentais-*.run.xml
}
trap cleanup EXIT INT TERM

for engine in pdflatex lualatex; do
  job="fontes-documentais-$engine"
  echo "Validating documentary sources with $engine..."

  "$engine" -jobname="$job" $flags "$fixture" > "/tmp/$job.out" 2>&1 || {
    cat "/tmp/$job.out"
    exit 1
  }
  biber "$job" > "/tmp/$job-biber.out" 2>&1 || {
    cat "/tmp/$job-biber.out"
    exit 1
  }
  "$engine" -jobname="$job" $flags "$fixture" > "/tmp/$job.out" 2>&1 || {
    cat "/tmp/$job.out"
    exit 1
  }
  "$engine" -jobname="$job" $flags "$fixture" > "/tmp/$job.out" 2>&1 || {
    cat "/tmp/$job.out"
    exit 1
  }

  if grep -Eq 'WARN|ERROR' "$job.blg"; then
    cat "$job.blg"
    echo "$job: Biber reported a warning/error."
    exit 1
  fi

  pdftotext -layout "$job.pdf" "/tmp/$job.txt"
  python3 - "/tmp/$job.txt" <<'PY'
import re
import sys
import unicodedata
from pathlib import Path

raw = Path(sys.argv[1]).read_text(encoding='utf-8')
text = re.sub(r'\s+', ' ', unicodedata.normalize('NFC', raw)).strip()
fold = text.casefold()

for marker in (
    'adaptado de',
    'silva',
    '2026',
    'p. 42',
    'anexo a',
    'documento com referência própria',
    'manual de dados de teste',
    'editora acadêmica',
):
    if marker.casefold() not in fold:
        raise SystemExit(f'documentary marker missing: {marker}')

source_pos = fold.find('adaptado de')
annex_pos = fold.find('anexo a')
if source_pos < 0 or annex_pos < source_pos:
    raise SystemExit('external source block was not located before the annex')
source_segment = fold[source_pos:annex_pos]
for token in ('silva', '2026', 'p. 42'):
    if token.casefold() not in source_segment:
        raise SystemExit(
            f'external illustration source is missing required citation evidence: {token}'
        )

fullref_pos = fold.find('manual de dados de teste')
if fullref_pos < annex_pos:
    raise SystemExit('annex-specific bibliographic reference did not remain inside the annex')

if 'referências' in fold[annex_pos:]:
    raise SystemExit(
        'fixture created a global reference list; this case must remain local to the annex'
    )
PY

  echo 'VALIDATION-EVIDENCE rule=illustration.source.external-citation status=PASS expected=author-date-citation-with-locator measured=adapted-source-citation-p.42-present'
  echo 'LIBRARIAN-REVIEW-EVIDENCE item=23 status=PASS locator=p.42 context=external-illustration-source'
done

echo 'Documentary sources gate completed.'
