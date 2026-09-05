#!/bin/sh
set -eu

fixture="tests/documents/mainmatter-long-quotation-test.tex"
job="long-quotation-evidence"
evidence="artifacts/normative/mainmatter/long-quotation.json"
reduced_evidence="artifacts/normative/mainmatter/long-quotation-reduced-size.json"
log="/tmp/abntexto-ufc-long-quotation.log"

cleanup() {
  rm -f "$job.aux" "$job.log" "$job.out" "$job.pdf" "$job.toc"
}
trap cleanup EXIT INT TERM

for pass in 1 2; do
  pdflatex \
    -jobname="$job" \
    -interaction=nonstopmode \
    -halt-on-error \
    -file-line-error \
    "$fixture" > "$log" 2>&1 || {
      cat "$log"
      exit 1
    }
done

warnings=$(grep -E 'LaTeX Warning:|Package [^ ]+ Warning:|Class [^ ]+ Warning:|Overfull \\hbox|Overfull \\vbox' "$job.log" | \
  grep -vF -e 'Class abntexto-ufc Warning: Times New Roman not found; using TeX Gyre Termes' || true)
if [ -n "$warnings" ]; then
  printf '%s\n' "$warnings"
  echo "Long-quotation validation failed: unrecognized warning or overflow in $fixture."
  exit 1
fi

mkdir -p "$(dirname "$evidence")"
python3 tests/checks/normative_long_quotation.py \
  "$job.pdf" \
  --json "$evidence" \
  --commit-sha "${SOURCE_COMMIT_SHA:-${GITHUB_SHA:-}}"

test -s "$evidence" || {
  echo 'Long-quotation validation failed: JSON evidence was not generated.'
  exit 1
}

python3 tests/checks/normative_long_quote_reduced_size.py \
  "$evidence" \
  --json "$reduced_evidence" \
  --commit-sha "${SOURCE_COMMIT_SHA:-${GITHUB_SHA:-}}"

test -s "$reduced_evidence" || {
  echo 'Long-quotation reduced-size validation failed: JSON evidence was not generated.'
  exit 1
}

echo 'LONG-QUOTATION-EVIDENCE-GATE status=PASS'

# Keep reviewer-specific citation/locator evidence separate from the geometric normative scenario.
sh tests/integration/long-quotation-citation-evidence.sh
