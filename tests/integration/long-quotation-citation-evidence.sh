#!/bin/sh
set -eu

fixture="tests/documents/mainmatter-long-quotation-citation-test.tex"
job="long-quotation-citation-evidence"
latex_log="/tmp/abntexto-ufc-long-quotation-citation.log"
biber_log="/tmp/abntexto-ufc-long-quotation-citation-biber.log"

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
  echo "Long-quotation citation audit failed: unrecognized warning or overflow in $fixture."
  exit 1
fi

pdftotext -layout "$job.pdf" "/tmp/$job.raw"
python3 - "/tmp/$job.raw" <<'PY'
import re
import sys
import unicodedata
from pathlib import Path

raw = Path(sys.argv[1]).read_text(encoding='utf-8')
text = re.sub(r'\s+', ' ', unicodedata.normalize('NFC', raw)).strip()

expected = re.compile(
    r'LQREVCLOSE\s*\(Silva,\s*2020,\s*p\.\s*42\)\.',
    re.IGNORECASE,
)
if not expected.search(text):
    raise SystemExit(
        'Long-quotation citation audit failed: expected author-date locator and final punctuation were not rendered after the quotation.'
    )

forbidden = re.compile(
    r'LQREVCLOSE\s*\.\s*\(Silva,\s*2020,\s*p\.\s*42\)',
    re.IGNORECASE,
)
if forbidden.search(text):
    raise SystemExit(
        'Long-quotation citation audit failed: an extraneous full stop appears before the parenthetical citation.'
    )

if 'LQREVAFTER' not in text:
    raise SystemExit('Long-quotation citation audit failed: trailing control marker is missing.')
PY

echo 'LIBRARIAN-REVIEW-EVIDENCE item=19 status=PASS locator=p.42 context=long-direct-quotation'
echo 'LIBRARIAN-REVIEW-EVIDENCE item=20 status=PASS punctuation=no-full-stop-before-parenthetical-citation'
echo 'Long-quotation citation evidence gate completed.'
