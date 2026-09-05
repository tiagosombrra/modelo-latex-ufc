#!/bin/sh
set -eu

sh tests/integration/reference-guide-contract.sh

make clean
make compile

log="template/main.log"
pdf="template/main.pdf"
toc="template/main.toc"

warnings=$(grep -E 'LaTeX Warning:|Package [^ ]+ Warning:|Class [^ ]+ Warning:|Overfull \\hbox|Underfull \\hbox|Overfull \\vbox' "$log" || true)
if [ -n "$warnings" ]; then
  printf '%s\n' "$warnings"
  echo 'Reference document failed: review the warnings above.'
  exit 1
fi

sh tests/integration/font-embedding.sh "$pdf"

if command -v pdfinfo >/dev/null 2>&1; then
  metadata="/tmp/abntexto-ufc-reference-pdfa-meta.xml"
  pdfinfo -meta "$pdf" > "$metadata"
  grep -Eq '<pdfaid:part>2</pdfaid:part>' "$metadata" || {
    echo 'Reference document failed: PDF/A part 2 declaration is missing.'
    exit 1
  }
  grep -Eq '<pdfaid:conformance>[Bb]</pdfaid:conformance>' "$metadata" || {
    echo 'Reference document failed: PDF/A-2b conformance declaration is missing.'
    exit 1
  }
fi

python3 <<'PY'
import re
from pathlib import Path

cases = (
    ('template/frontmatter/summary.tex', r'\\ufcSummaryKeywords', 'Summary'),
    ('template/frontmatter/abstract.tex', r'\\keywords', 'Abstract'),
)

for path, marker, label in cases:
    source = Path(path).read_text(encoding='utf-8')
    body = re.split(marker, source, maxsplit=1)[0]
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*", body)
    if not 150 <= len(words) <= 500:
        raise SystemExit(f'{label} reference text outside the UFC 150–500 word range: {len(words)}')
PY

if command -v pdftotext >/dev/null 2>&1; then
  text="/tmp/abntexto-ufc-reference.txt"
  pdftotext "$pdf" "$text"
  for marker in 'RESUMO' 'ABSTRACT' 'LISTA DE ILUSTRAÇÕES' 'SUMÁRIO' 'INTRODUÇÃO' 'REFERÊNCIAS' 'GLOSSÁRIO' 'ÍNDICE'; do
    grep -Fq "$marker" "$text" || {
      echo "Reference document failed: rendered marker is missing: $marker"
      exit 1
    }
  done

  python3 - "$text" <<'PY'
import re
import sys
import unicodedata
from pathlib import Path

path = Path(sys.argv[1])
raw = unicodedata.normalize('NFC', path.read_text(encoding='utf-8', errors='replace'))
flat = re.sub(r'\s+', ' ', raw)

object_titles = (
    'Figura estreita com legenda curta',
    'Fluxo de processamento em arquivo PNG raster',
    'Distribuição sintética de três categorias',
    'Comparação de configurações editoriais do exemplo',
    'Indicadores sintéticos com linhas alternadas',
)
legacy_object_titles = (
    'Gráfico da Atmosfera Superior',
)
for marker in object_titles:
    if marker not in flat:
        raise SystemExit(f'Reference document failed: reviewed sentence-case object title is missing: {marker}')
for marker in legacy_object_titles:
    if marker in flat:
        raise SystemExit(f'Reference document failed: reviewed legacy object title casing remains: {marker}')
print(
    'LIBRARIAN-REVIEW-EVIDENCE item=11 status=PASS '
    f'context=canonical-reference-pdf sentence_case_titles={len(object_titles)} legacy_titles=0'
)

ufc_phrase = 'Universidade Federal do Ceará (UFC)'
if ufc_phrase not in flat:
    raise SystemExit('Reference document failed: full UFC name followed by acronym is missing from rendered body text.')
intro_source = Path('template/chapters/1-introduction.tex').read_text(encoding='utf-8')
phrase_at = intro_source.find(ufc_phrase)
first_ufc = re.search(r'\bUFC\b', intro_source)
expected_ufc_at = phrase_at + ufc_phrase.index('UFC') if phrase_at >= 0 else -1
if phrase_at < 0 or first_ufc is None or first_ufc.start() != expected_ufc_at:
    raise SystemExit('Reference document failed: the first source-level UFC occurrence is not the full-name introduction.')
print(
    'LIBRARIAN-REVIEW-EVIDENCE item=16 status=PASS '
    'context=canonical-reference-pdf rendered_full_name=true source_first_use=true'
)

heading_markers = (
    'Seções e subseções',
    'Equações',
    'Código-fonte',
    'Citação direta longa',
)
legacy_headings = (
    'Usando Fórmulas Matemáticas',
    'Usando Código-fonte',
    'Usando Teoremas, Proposições, etc',
    'Usando Questões',
    'Resultados do Experimento A',
    'Resultados do Experimento B',
)
for marker in heading_markers:
    if marker not in flat:
        raise SystemExit(f'Reference document failed: reviewed sentence-case heading is missing: {marker}')
for marker in legacy_headings:
    if marker in flat:
        raise SystemExit(f'Reference document failed: reviewed legacy heading remains: {marker}')
if re.search(r'\betc(?:\s*[,;:]|\s*$)', flat, flags=re.IGNORECASE):
    raise SystemExit('Reference document failed: malformed etc. punctuation remains in rendered content.')
print(
    'LIBRARIAN-REVIEW-EVIDENCE item=28 status=PASS '
    f'context=canonical-reference-pdf sentence_case_headings={len(heading_markers)} legacy_headings=0 malformed_etc=0'
)
PY
fi

grep -Eiq 'Introdu' "$toc" || {
  echo 'Reference document failed: the textual section is missing from the table of contents.'
  exit 1
}

python3 <<'PY'
import re
from pathlib import Path

toc = Path('template/main.toc').read_text(encoding='utf-8', errors='replace')
for title in ('RESUMO', 'ABSTRACT', 'LISTA DE ILUSTRAÇÕES'):
    pattern = re.compile(
        r'\\contentsline\s*\{[^}]+\}\s*\{' + re.escape(title) + r'\}\s*\{',
        re.IGNORECASE,
    )
    if pattern.search(toc):
        raise SystemExit(f'Reference document failed: front-matter element entered the table of contents: {title}')
PY

echo 'Reference document validated.'
