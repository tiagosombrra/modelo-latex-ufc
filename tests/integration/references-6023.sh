#!/bin/sh
set -eu

fixture="tests/documents/references-6023-2025.tex"
job="referencias-6023-2025"

cleanup_job() {
  rm -f "$job".aux "$job".bbl "$job".bcf "$job".blg "$job".log \
        "$job".out "$job".pdf "$job".run.xml "$job".toc
}

for engine in pdflatex lualatex; do
  cleanup_job
  echo "Validating $fixture with $engine + Biber..."

  "$engine" -jobname="$job" -interaction=nonstopmode -halt-on-error -file-line-error "$fixture" > /tmp/abntexto-ufc-6023.log 2>&1 || {
    cat /tmp/abntexto-ufc-6023.log
    exit 1
  }

  biber "$job" > /tmp/abntexto-ufc-6023-biber.log 2>&1 || {
    cat /tmp/abntexto-ufc-6023-biber.log
    exit 1
  }

  "$engine" -jobname="$job" -interaction=nonstopmode -halt-on-error -file-line-error "$fixture" > /tmp/abntexto-ufc-6023.log 2>&1 || {
    cat /tmp/abntexto-ufc-6023.log
    exit 1
  }
  "$engine" -jobname="$job" -interaction=nonstopmode -halt-on-error -file-line-error "$fixture" > /tmp/abntexto-ufc-6023.log 2>&1 || {
    cat /tmp/abntexto-ufc-6023.log
    exit 1
  }

  warnings=$(grep -E 'LaTeX Warning:|Package [^ ]+ Warning:|Class [^ ]+ Warning:|Overfull \\hbox|Overfull \\vbox' "$job.log" | \
    grep -vF -e 'Class abntexto-ufc Warning: Times New Roman not found; using TeX Gyre Termes' || true)
  if [ -n "$warnings" ]; then
    printf '%s\n' "$warnings"
    echo "Preflight failed: NBR 6023:2025 regression contains an unrecognized warning or overflow."
    exit 1
  fi

done

if command -v pdftotext >/dev/null 2>&1; then
  pdftotext -layout "$job.pdf" /tmp/abntexto-ufc-6023.txt
  python3 - <<'PY'
import re
import unicodedata
from pathlib import Path

text = Path('/tmp/abntexto-ufc-6023.txt').read_text(encoding='utf-8')
text = unicodedata.normalize('NFC', text)
chunks = [re.sub(r'\s+', ' ', part).strip() for part in re.split(r'\n\s*\n', text) if part.strip()]

def entry(marker):
    marker_fold = marker.casefold()
    matches = [part for part in chunks if marker_fold in part.casefold()]
    if not matches:
        raise SystemExit(f'test entry missing: {marker}\n{text}')
    return ' '.join(matches)

event = entry('Congresso Brasileiro de Teste')
if re.search(r'\[\s*[Ss]\.\s*[Ll]\.\s*\]', event):
    raise SystemExit('NBR 6023:2025: event without a city received a sine loco marker.')

article = entry('Preservação digital em ambientes acadêmicos')
if 'e202501' not in article:
    raise SystemExit('NBR 6023:2025: e-location missing.')

judgment = entry('Recurso extraordinário de teste')
if 'julgado em' not in judgment.casefold() or '2025' not in judgment:
    raise SystemExit('NBR 6023:2025: judgment date missing.')

online = entry('Preservação de documentos digitais')
if re.search(r'\[\s*[Ss]\.\s*[Ll]\.', online) or re.search(r'\[\s*[Ss]\.\s*[Nn]\.', online):
    raise SystemExit('NBR 6023:2025: electronic document received an unknown publication marker.')

printed = entry('Preservação de documentos impressos')
if not re.search(r'[Ss]\.\s*[Ll]\.', printed) or not re.search(r'[Ss]\.\s*[Nn]\.', printed):
    raise SystemExit('NBR 6023:2025: print document without publication data lost [S. l.] or [s. n.].')

supplement = entry('Indicadores acadêmicos brasileiros')
if 'suplemento' not in supplement.casefold() or supplement.find('2025') > supplement.casefold().find('suplemento'):
    raise SystemExit('NBR 6023:2025: supplement is not positioned after the date.')

interview = entry('Eficiência e inovação na gestão')
if 'hamel' not in interview.casefold():
    raise SystemExit('NBR 6023:2025: interviewee does not appear as the primary author.')

periodical = entry('REVISTA BRASILEIRA DE TESTE. Fortaleza')
if '1234-5678' not in periodical:
    raise SystemExit('NBR 6023:2025: optional ISSN was not preserved.')

identifiers = entry('Identificadores persistentes em referências')
if '10.1234/exemplo.2025.1' not in identifiers or '0000-0002-1825-0097' not in identifiers:
    raise SystemExit('NBR 6023:2025: DOI or ORCID supplemental missing.')

thesis = entry('Malhas adaptativas em documentos acadêmicos')
thesis_fold = thesis.casefold()
if 'dissertação' not in thesis_fold or 'mestrado em ciência da computação' not in thesis_fold:
    raise SystemExit('Reviewer reference regression: thesis/dissertation work type is missing.')
if 'universidade federal do ceará' not in thesis_fold or 'fortaleza' not in thesis_fold:
    raise SystemExit('Reviewer reference regression: thesis/dissertation institution or location is missing.')
thesis_years = re.findall(r'\b20\d{2}\b', thesis)
if thesis_years != ['2024']:
    raise SystemExit(f'Reviewer reference regression: thesis/dissertation year is duplicated or contradictory: {thesis_years}')

standard = entry('ABNT NBR 6023:2025')
standard_fold = standard.casefold()
for marker in ('associação brasileira de normas técnicas', 'rio de janeiro', 'abnt'):
    if marker not in standard_fold:
        raise SystemExit(f'Reviewer reference regression: standard entry is missing: {marker}')
if not re.search(r'\b2025\b', standard):
    raise SystemExit('Reviewer reference regression: standard publication year is missing.')

multivolume = entry('Tratado de normalização acadêmica')
multivolume_fold = multivolume.casefold()
for marker in ('costa', 'fortaleza', 'editora universitária', '2025'):
    if marker not in multivolume_fold:
        raise SystemExit(f'Reviewer reference regression: multivolume entry is missing: {marker}')
if not re.search(r'\b2\s*v\.', multivolume, re.IGNORECASE):
    raise SystemExit(f'Reviewer reference regression: multivolume physical description is not rendered as 2 v.: {multivolume}')
PY

  evidence_json="${UFC_EVIDENCE_DIR:-artifacts/validation/reference-semantics}/reference-semantics.json"
  set -- python3 tests/checks/normative_reference_semantics.py \
    /tmp/abntexto-ufc-6023.txt --json "$evidence_json"
  if [ -n "${GITHUB_SHA:-}" ]; then
    set -- "$@" --commit-sha "$GITHUB_SHA"
  fi
  "$@"
  echo 'VALIDATION-EVIDENCE rule=references.nbr6023-2025.test-profile status=PASS expected=twelve-profile-cases measured=twelve-cases-validated'
  echo 'LIBRARIAN-REVIEW-EVIDENCE item=30 status=PASS context=electronic-unknown-publication-markers measured=omitted-for-controlled-online-entry'
  echo 'LIBRARIAN-REVIEW-EVIDENCE item=31 status=PASS context=thesis-dissertation measured=work-type-and-single-consistent-year'
  echo 'LIBRARIAN-REVIEW-EVIDENCE item=32 status=PASS context=standard-and-multivolume measured=publisher-year-and-2-v-physical-description'
fi

echo 'NBR 6023:2025 gate completed.'
