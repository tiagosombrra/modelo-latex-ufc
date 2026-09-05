#!/bin/sh
set -eu

fixture="tests/documents/mainmatter-direct-citation-source-test.tex"
job="validation-direct-citation-source"
evidence="artifacts/normative-textual/direct-citation-source.json"
latex_log="/tmp/abntexto-ufc-v3-direct-citation-source.log"
biber_log="/tmp/abntexto-ufc-v3-direct-citation-source-biber.log"

cleanup() {
  rm -f "$job.aux" "$job.bbl" "$job.bcf" "$job.blg" "$job.log" \
        "$job.out" "$job.pdf" "$job.run.xml" "$job.toc"
}
trap cleanup EXIT INT TERM

pdflatex \
  -jobname="$job" \
  -interaction=nonstopmode \
  -halt-on-error \
  -file-line-error \
  "$fixture" > "$latex_log" 2>&1 || {
    cat "$latex_log"
    exit 1
  }

biber "$job" > "$biber_log" 2>&1 || {
  cat "$biber_log"
  exit 1
}

for pass in 1 2; do
  pdflatex \
    -jobname="$job" \
    -interaction=nonstopmode \
    -halt-on-error \
    -file-line-error \
    "$fixture" > "$latex_log" 2>&1 || {
      cat "$latex_log"
      exit 1
    }
done

warnings=$(grep -E 'LaTeX Warning:|Package [^ ]+ Warning:|Class [^ ]+ Warning:|Overfull \\hbox|Overfull \\vbox' "$job.log" | \
  grep -vF -e 'Class abntexto-ufc Warning: Times New Roman not found; using TeX Gyre Termes' || true)
if [ -n "$warnings" ]; then
  printf '%s\n' "$warnings"
  echo "Direct-citation source audit failed: unrecognized warning or overflow in $fixture."
  exit 1
fi

mkdir -p "$(dirname "$evidence")"
python3 tests/checks/normative_direct_citation_source.py \
  "$job.pdf" \
  --json "$evidence" \
  --commit-sha "${SOURCE_COMMIT_SHA:-${GITHUB_SHA:-}}"

test -s "$evidence" || {
  echo 'Direct-citation source audit failed: JSON evidence was not generated.'
  exit 1
}

echo 'Direct-citation source evidence gate completed.'
