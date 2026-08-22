#!/bin/sh
set -eu

fixture="tests/normativa/tipografia-codigo.tex"
tmp="ufctex-code-typography.tex"
flags="-interaction=nonstopmode -halt-on-error -file-line-error"

cleanup() {
  rm -f "$tmp" tipografia-codigo-*.aux tipografia-codigo-*.log tipografia-codigo-*.out tipografia-codigo-*.pdf
  rm -f tipografia-codigo-*.loa tipografia-codigo-*.loc
}
trap cleanup EXIT INT TERM

for engine in pdflatex lualatex; do
  for family in times arial; do
    sed "s/@UFC_FONT@/$family/g" "$fixture" > "$tmp"
    job="tipografia-codigo-$family-$engine"
    echo "Validando tipografia de código/algoritmo $family com $engine..."

    "$engine" -jobname="$job" $flags "$tmp" > "/tmp/$job.out" 2>&1 || {
      cat "/tmp/$job.out"
      exit 1
    }

    python3 - "$job.log" <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')


def marker(name):
    match = re.search(rf'{re.escape(name)}=([^\r\n]+)', text)
    if not match:
        raise SystemExit(f'marcador ausente: {name}')
    return match.group(1).strip()


def scalar(name):
    value = marker(name)
    try:
        return float(value)
    except ValueError as exc:
        raise SystemExit(f'{name}: valor inválido: {value}') from exc


def normalize_family(value):
    return re.sub(r'\([0-9]+\)$', '', value)

text_family = normalize_family(marker('UFC-TEXT-FAMILY'))
code_family = normalize_family(marker('UFC-CODE-FAMILY'))
algorithm_family = normalize_family(marker('UFC-ALGORITHM-FAMILY'))

if code_family != text_family:
    raise SystemExit(f'código mudou de família: texto={text_family}, código={code_family}')
if algorithm_family != text_family:
    raise SystemExit(f'algoritmo mudou de família: texto={text_family}, algoritmo={algorithm_family}')

for name in ('UFC-TEXT-FONTSIZE', 'UFC-CODE-FONTSIZE', 'UFC-ALGORITHM-FONTSIZE'):
    actual = scalar(name)
    if abs(actual - 12.0) > 0.1:
        raise SystemExit(f'{name}: esperado 12 pt nominal, obtido {actual:.4f}')
PY

    pdftotext -bbox-layout "$job.pdf" "/tmp/$job-bbox.html"
    python3 - "/tmp/$job-bbox.html" <<'PY'
import re
import sys
import xml.etree.ElementTree as ET

A4_WIDTH = 595.276
CM = 72.0 / 2.54
LEFT = 3 * CM
RIGHT = 2 * CM
TOL = 1.5
Y_TOL = 3.0

root = ET.parse(sys.argv[1]).getroot()
local = lambda tag: tag.rsplit('}', 1)[-1]


def compact(value):
    return re.sub(r'[^A-Z0-9]', '', value.upper())


words = []
for node in root.iter():
    if local(node.tag) != 'word':
        continue
    words.append({
        'text': ''.join(node.itertext()),
        'x0': float(node.attrib['xMin']),
        'y0': float(node.attrib['yMin']),
        'x1': float(node.attrib['xMax']),
        'y1': float(node.attrib['yMax']),
    })


def locate_marker_line(marker):
    target = compact(marker)
    for line in (node for node in root.iter() if local(node.tag) == 'line'):
        line_words = [node for node in line if local(node.tag) == 'word']
        if not line_words:
            continue
        text = ''.join(''.join(word.itertext()) for word in line_words)
        if target not in compact(text):
            continue
        data = [{
            'text': ''.join(word.itertext()),
            'x0': float(word.attrib['xMin']),
            'y0': float(word.attrib['yMin']),
            'x1': float(word.attrib['xMax']),
            'y1': float(word.attrib['yMax']),
        } for word in line_words]
        content = [word for word in data if not re.fullmatch(r'\d+:?', word['text'].strip())]
        if not content:
            raise SystemExit(f'marcador geométrico sem conteúdo: {marker}')
        return {
            'content_x0': min(word['x0'] for word in content),
            'y0': min(word['y0'] for word in data),
            'x1': max(word['x1'] for word in data),
            'y1': max(word['y1'] for word in data),
        }
    raise SystemExit(f'marcador geométrico ausente: {marker}')


def line_number_for(marker_box):
    center = (marker_box['y0'] + marker_box['y1']) / 2
    candidates = []
    for word in words:
        word_center = (word['y0'] + word['y1']) / 2
        if abs(word_center - center) > Y_TOL:
            continue
        if word['x1'] > marker_box['content_x0'] + 0.5:
            continue
        if re.fullmatch(r'\d+:?', word['text'].strip()):
            candidates.append(word)
    if not candidates:
        raise SystemExit('número de linha não localizado junto ao marcador geométrico')
    return min(candidates, key=lambda word: word['x0'])


for marker in ('UFC-CODE-GEOMETRY-MARKER', 'UFC-ALGORITHM-GEOMETRY-MARKER'):
    box = locate_marker_line(marker)
    number = line_number_for(box)
    if number['x0'] < LEFT - TOL:
        raise SystemExit(
            f"{marker}: número de linha invade margem esquerda: "
            f"x={number['x0']:.2f}, limite={LEFT:.2f}"
        )
    if box['x1'] > A4_WIDTH - RIGHT + TOL:
        raise SystemExit(
            f"{marker}: conteúdo invade margem direita: "
            f"x={box['x1']:.2f}, limite={A4_WIDTH - RIGHT:.2f}"
        )
PY

    sh tests/v2-font-embedding-check.sh "$job.pdf"
  done
done

echo 'Gate V2 de tipografia e geometria de código e algoritmos concluído.'
