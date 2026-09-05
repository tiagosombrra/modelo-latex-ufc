#!/bin/sh
set -eu

commit_sha="${SOURCE_COMMIT_SHA:-${GITHUB_SHA:-}}"
table_fixture="tests/documents/table-typography-final-pdf.tex"
equation_fixture="tests/documents/equation-display-final-pdf.tex"
table_job="table-typography-final-pdf"
equation_job="equation-display-final-pdf"
table_evidence="artifacts/normative-layout/table-typography-final-pdf.json"
equation_evidence="artifacts/normative-layout/equation-display-final-pdf.json"
flags="-interaction=nonstopmode -halt-on-error -file-line-error"

cleanup() {
  rm -f \
    "$table_job.aux" "$table_job.log" "$table_job.out" "$table_job.pdf" "$table_job.lot" \
    "$equation_job.aux" "$equation_job.log" "$equation_job.out" "$equation_job.pdf"
}
trap cleanup EXIT INT TERM

python3 -m py_compile \
  tests/checks/normative_table_typography.py \
  tests/checks/normative_equation_display.py

compile_fixture() {
  fixture="$1"
  job="$2"
  log="/tmp/$job.out"

  for pass in 1 2; do
    pdflatex -jobname="$job" $flags "$fixture" > "$log" 2>&1 || {
      cat "$log"
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
}

compile_fixture "$table_fixture" "$table_job"
compile_fixture "$equation_fixture" "$equation_job"

mkdir -p artifacts/normative-layout
python3 tests/checks/normative_table_typography.py \
  "$table_job.pdf" \
  --json "$table_evidence" \
  --commit-sha "$commit_sha"
python3 tests/checks/normative_equation_display.py \
  "$equation_job.pdf" \
  --json "$equation_evidence" \
  --commit-sha "$commit_sha"

test -s "$table_evidence" || {
  echo 'table typography evidence JSON was not generated.'
  exit 1
}
test -s "$equation_evidence" || {
  echo 'equation display evidence JSON was not generated.'
  exit 1
}

echo 'Evidence for table typography and displayed equation gate completed.'
