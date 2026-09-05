#!/bin/sh
set -eu

fixture="tests/documents/table-ibge-vector-final-pdf.tex"
job="table-ibge-vector-final-pdf"
flags="-interaction=nonstopmode -halt-on-error -file-line-error"

cleanup() {
  rm -f "$job.aux" "$job.log" "$job.out" "$job.pdf" "$job.lot"
}
trap cleanup EXIT INT TERM

python3 -m py_compile tools/pdf_vector_measurement.py \
  tests/checks/normative_vector_rule_validation.py \
  tests/checks/normative_table_ibge_vector.py

sh tests/integration/vector-rule-validation.sh

for pass in 1 2; do
  pdflatex -jobname="$job" $flags "$fixture" > "/tmp/$job.out" 2>&1 || {
    cat "/tmp/$job.out"
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

python3 tests/checks/normative_table_ibge_vector.py "$job.pdf" \
  --json artifacts/normative-layout/table-ibge-vector-final-pdf.json \
  --commit-sha "${SOURCE_COMMIT_SHA:-${GITHUB_SHA:-}}"

echo 'IBGE table vector-geometry evidence gate completed.'
