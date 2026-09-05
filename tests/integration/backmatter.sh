#!/bin/sh
set -eu

modern="tests/documents/backmatter.tex"

sh tests/integration/appendix-annex-final-pdf-evidence.sh
sh tests/integration/index-glossary-final-pdf-evidence.sh

cleanup_job() {
  job="$1"
  rm -f "$job".aux "$job".bbl "$job".bcf "$job".blg "$job".glg "$job".glo \
        "$job".gls "$job".idx "$job".ilg "$job".ind "$job".ist "$job".log \
        "$job".out "$job".pdf "$job".run.xml "$job".toc
}

check_log() {
  job="$1"
  warnings=$(grep -E 'LaTeX Warning:|Package [^ ]+ Warning:|Class [^ ]+ Warning:|Overfull \\hbox|Overfull \\vbox' "$job.log" | \
    grep -vF -e 'Class abntexto-ufc Warning: Times New Roman not found; using TeX Gyre Termes' || true)
  if [ -n "$warnings" ]; then
    printf '%s\n' "$warnings"
    echo "Gate failed: $job contains unrecognized warning or overflow."
    exit 1
  fi
}

for engine in pdflatex lualatex; do
  job="backmatter-$engine"
  cleanup_job "$job"
  echo "Validating back matter with $engine..."

  "$engine" -jobname="$job" -interaction=nonstopmode -halt-on-error -file-line-error "$modern" > /tmp/abntexto-ufc-post.log 2>&1 || {
    cat /tmp/abntexto-ufc-post.log
    exit 1
  }
  biber "$job" > /tmp/abntexto-ufc-post-biber.log 2>&1 || {
    cat /tmp/abntexto-ufc-post-biber.log
    exit 1
  }
  makeglossaries "$job" > /tmp/abntexto-ufc-post-glossary.log 2>&1 || {
    cat /tmp/abntexto-ufc-post-glossary.log
    exit 1
  }
  makeindex "$job" > /tmp/abntexto-ufc-post-index.log 2>&1 || {
    cat /tmp/abntexto-ufc-post-index.log
    exit 1
  }
  for pass in 1 2 3; do
    "$engine" -jobname="$job" -interaction=nonstopmode -halt-on-error -file-line-error "$modern" > /tmp/abntexto-ufc-post.log 2>&1 || {
      cat /tmp/abntexto-ufc-post.log
      exit 1
    }
  done
  check_log "$job"

  pdftotext -layout "$job.pdf" "/tmp/$job.txt"
  python3 - "$job" <<'PY'
import re
import sys
import unicodedata
from pathlib import Path

job = sys.argv[1]
raw = Path(f'/tmp/{job}.txt').read_text(encoding='utf-8')
raw = re.sub(r'(?<=\w)-[ \t]*\n[ \t]*(?=\w)', '', raw)
text = re.sub(r'\s+', ' ', unicodedata.normalize('NFC', raw)).strip()
fold = text.casefold()

markers = [
    'referências',
    'glossário',
    'apêndice a',
    'anexo a',
    'índice',
]
positions = []
for marker in markers:
    pos = fold.find(marker)
    if pos < 0:
        raise SystemExit(f'{job}: back-matter element missing: {marker}')
    positions.append(pos)
if positions != sorted(positions):
    raise SystemExit(f'{job}: incorrect back-matter order: {list(zip(markers, positions))}')

for content in (
    'discretização de um domínio geométrico',
    'questionário produzido pelo autor',
    'documento institucional externo',
):
    if content.casefold() not in fold:
        raise SystemExit(f'{job}: back-matter content missing: {content}')

if 'capítulo' in fold or 'capitulo' in fold:
    raise SystemExit(f'{job}: chapter-based structure reappeared.')
PY

  for marker in 'Referências' 'Glossário' 'Questionário produzido pelo autor' 'Documento institucional externo' 'Remissivo'; do
    grep -Fqi "$marker" "$job.toc" || {
      echo "$job: back-matter item missing from the table of contents: $marker"
      cat "$job.toc"
      exit 1
    }
  done
done

echo 'Back-matter gate completed.'
