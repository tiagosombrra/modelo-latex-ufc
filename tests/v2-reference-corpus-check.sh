#!/bin/sh
set -eu

[ -s documento.pdf ] || {
  echo 'Corpus V2 falhou: documento.pdf ausente.'
  exit 1
}

for file in documento.loi documento.lot documento.loc documento.loa documento.toc; do
  [ -s "$file" ] || {
    echo "Corpus V2 falhou: arquivo de navegação ausente: $file"
    exit 1
  }
done

if [ "${UFC_REQUIRE_REFERENCE_IMAGES:-0}" = 1 ]; then
  python3 <<'PY'
import hashlib
from pathlib import Path

expected = {
    Path('figuras/ufc-campus-pici.jpg'): '5f431612cdbfbb088c37c685a0e3c93852e96ccd',
    Path('figuras/ufc-reitoria.jpg'): 'b6746bb53d82dae52330805ca0a08f029b773b2e',
}
for path, digest in expected.items():
    if not path.is_file():
        raise SystemExit(f'Corpus V2 falhou: fotografia licenciada ausente: {path}')
    actual = hashlib.sha1(path.read_bytes()).hexdigest()
    if actual != digest:
        raise SystemExit(f'Corpus V2 falhou: SHA-1 divergente em {path}: {actual}')
PY
fi

pdftotext -layout documento.pdf /tmp/ufctex-v2-reference-corpus.txt
pdftotext -bbox-layout documento.pdf /tmp/ufctex-v2-reference-corpus-bbox.html

python3 <<'PY'
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def normalize_pdf_text(value):
    value = value.replace('\u00ad', '')
    value = re.sub(r'-[ \t]*\r?\n[ \t]*(?=\w)', '', value)
    return re.sub(r'\s+', ' ', value)


def spaced_leader_pattern():
    return r'(?:\.\s+){1,}\.\s*\d+\s*$'


def require_dotted_entry(source, start, end, marker):
    start_at = source.find(start)
    end_at = source.find(end, start_at + len(start))
    if start_at < 0 or end_at < 0:
        raise SystemExit(f'Corpus V2 falhou: bloco de lista não localizado: {start}.')
    block = source[start_at:end_at]
    pattern = re.compile(re.escape(marker) + r'[^\n]*' + spaced_leader_pattern(), re.M)
    if not pattern.search(block):
        raise SystemExit(f'Corpus V2 falhou: líder pontilhado espaçado ausente em {start}: {marker}')


text = Path('/tmp/ufctex-v2-reference-corpus.txt').read_text(encoding='utf-8', errors='replace')
flat = normalize_pdf_text(text)
required = (
    'CATÁLOGO DE EXEMPLOS E VALIDAÇÃO VISUAL',
    'Normas e diretrizes adotadas',
    'Referências bibliográficas e recursos eletrônicos',
    'Figura estreita com legenda curta',
    'Figura de largura intermediária',
    'Figura larga próxima à largura útil',
    'Fluxo de processamento em arquivo PNG raster',
    'Campus do Pici',
    'Vista da Lagoa do Pici no Campus do Pici',
    'Reitoria da Universidade Federal do Ceará',
    'Distribuição sintética de três categorias',
    'Comparação de configurações editoriais',
    'Indicadores sintéticos com linhas alternadas',
    'Função de média em Python com números de linha',
    'Função de máximo em C++ sem números de linha',
    'Arquivo Python externo com números de linha',
    'Método Java com numeração a cada duas linhas',
    'Máximo divisor comum com números de linha',
    'Seleção do maior valor sem números de linha',
    'Nome do Quinto Membro',
    'Nome do Sexto Membro',
    'ABNT NBR 14724:2024',
    'ABNT NBR 6023:2025',
    'HTTP Semantics',
    'APÊNDICE A',
    'APÊNDICE B',
    'APÊNDICE C',
    'APÊNDICE D',
    'ANEXO A',
    'ANEXO B',
)
missing = [marker for marker in required if marker not in flat]
if missing:
    raise SystemExit('Corpus V2 falhou: marcadores ausentes no PDF: ' + ', '.join(missing))
if '??' in text:
    raise SystemExit('Corpus V2 falhou: referência não resolvida encontrada no PDF.')
if 'Execute make reference-assets' in text:
    raise SystemExit('Corpus V2 falhou: fallback de fotografia apareceu no PDF de CI.')

pages = [normalize_pdf_text(page) for page in text.split('\f')]
committee_pages = [page for page in pages if 'BANCA EXAMINADORA' in page]
if len(committee_pages) != 1:
    raise SystemExit(f'Corpus V2 falhou: esperado exatamente um bloco de banca, encontrados {len(committee_pages)}.')
committee = committee_pages[0]
committee_members = (
    'Nome do Orientador',
    'Nome do Segundo Membro',
    'Nome do Terceiro Membro',
    'Nome do Quarto Membro',
    'Nome do Quinto Membro',
    'Nome do Sexto Membro',
)
missing_committee = [name for name in committee_members if name not in committee]
if missing_committee:
    raise SystemExit('Corpus V2 falhou: banca não cabe integralmente na folha de aprovação: ' + ', '.join(missing_committee))

list_blocks = (
    ('LISTA DE ILUSTRAÇÕES', 'LISTA DE TABELAS', 'Figura 1 — Exemplo de figura no padrão V2'),
    ('LISTA DE TABELAS', 'LISTA DE CÓDIGOS', 'Tabela 1 — Etapas do procedimento'),
    ('LISTA DE CÓDIGOS', 'LISTA DE ALGORITMOS', 'Código 1 — Função de soma em C++'),
    ('LISTA DE ALGORITMOS', 'LISTA DE ABREVIATURAS E SIGLAS', 'Algoritmo 1 — Busca linear'),
)
for start, end, marker in list_blocks:
    start_at = flat.find(start)
    end_at = flat.find(end, start_at + len(start))
    if start_at < 0 or end_at < 0:
        raise SystemExit(f'Corpus V2 falhou: bloco de lista não localizado: {start}.')
    block = flat[start_at:end_at]
    if marker not in block:
        raise SystemExit(f'Corpus V2 falhou: entrada com caixa preservada ausente de {start}: {marker}')
    if marker.upper() in block:
        raise SystemExit(f'Corpus V2 falhou: entrada indevidamente convertida para caixa alta em {start}.')
    require_dotted_entry(text, start, end, marker)

raw_pages = text.split('\f')
toc_starts = [
    index for index, page in enumerate(raw_pages)
    if 'SUMÁRIO' in page and 'INTRODUÇÃO' in page
]
if len(toc_starts) != 1:
    raise SystemExit(f'Corpus V2 falhou: esperado um sumário principal, encontrados {len(toc_starts)}.')

toc_start = toc_starts[0]
toc_end = None
for index in range(toc_start + 1, len(raw_pages)):
    if re.search(r'^\s*1\s+INTRODUÇÃO\s*$', raw_pages[index], re.M):
        toc_end = index
        break
if toc_end is None:
    raise SystemExit('Corpus V2 falhou: fim do sumário não localizado antes da seção INTRODUÇÃO.')

toc = '\n'.join(raw_pages[toc_start:toc_end])
toc_flat = normalize_pdf_text(toc)
for marker in (
    'INTRODUÇÃO',
    'Normas e diretrizes adotadas',
    'CONCLUSÃO',
    'REFERÊNCIAS',
    'GLOSSÁRIO',
    'APÊNDICE A',
    'APÊNDICE D',
    'ANEXO A',
    'ANEXO B',
    'ÍNDICE REMISSIVO',
):
    if marker not in toc_flat:
        raise SystemExit(f'Corpus V2 falhou: entrada obrigatória ausente do sumário: {marker}.')

entry_lines = [line for line in toc.splitlines() if re.search(r'\d+\s*$', line)]
if len(entry_lines) < 20:
    raise SystemExit(f'Corpus V2 falhou: poucas entradas paginadas no sumário: {len(entry_lines)}.')
undotted = [
    line.strip() for line in entry_lines
    if not re.search(spaced_leader_pattern(), line)
]
if undotted:
    sample = ' | '.join(undotted[:8])
    raise SystemExit(
        f'Corpus V2 falhou: {len(undotted)} entrada(s) do sumário sem líder pontilhado espaçado: {sample}'
    )

root = ET.parse('/tmp/ufctex-v2-reference-corpus-bbox.html').getroot()
local = lambda tag: tag.rsplit('}', 1)[-1]


def toc_title_x(marker):
    matches = []
    for line in (node for node in root.iter() if local(node.tag) == 'line'):
        words = [node for node in line if local(node.tag) == 'word']
        if not words:
            continue
        raw = ' '.join(''.join(word.itertext()) for word in words)
        if not raw.startswith(marker):
            continue
        if not any(''.join(word.itertext()).strip() == '.' for word in words):
            continue
        matches.append((raw, float(words[0].attrib['xMin'])))
    if len(matches) != 1:
        raise SystemExit(
            f'Corpus V2 falhou: esperado um título primário no sumário para {marker}; encontrados {len(matches)}.'
        )
    return matches[0][1]

reference_x = toc_title_x('INTRODUÇÃO')
for marker in ('CONCLUSÃO', 'REFERÊNCIAS', 'GLOSSÁRIO', 'ÍNDICE REMISSIVO'):
    actual_x = toc_title_x(marker)
    if abs(actual_x - reference_x) > 1.5:
        raise SystemExit(
            f'Corpus V2 falhou: {marker} desalinhado no sumário: '
            f'x={actual_x:.2f}, referência={reference_x:.2f}'
        )
PY

check_list() {
  file="$1"
  shift
  for marker in "$@"; do
    grep -Fq "$marker" "$file" || {
      echo "Corpus V2 falhou: '$marker' ausente de $file"
      exit 1
    }
  done
}

check_list documento.loi \
  'Figura estreita com legenda curta' \
  'Figura de largura intermediária' \
  'Figura larga próxima à largura útil' \
  'Fluxo de processamento em arquivo PNG raster' \
  'Campus do Pici, onde se localiza o Departamento de Computação da UFC' \
  'Reitoria da Universidade Federal do Ceará' \
  'Distribuição sintética de três categorias' \
  'Comparação de configurações editoriais'

check_list documento.lot \
  'Etapas do procedimento' \
  'Indicadores sintéticos com linhas alternadas'

check_list documento.loc \
  'Função de soma em C++' \
  'Função de média em Python com números de linha' \
  'Função de máximo em C++ sem números de linha' \
  'Arquivo Python externo com números de linha' \
  'Método Java com numeração a cada duas linhas' \
  'Código C++ apresentado como apêndice'

check_list documento.loa \
  'Busca linear' \
  'Máximo divisor comum com números de linha' \
  'Seleção do maior valor sem números de linha'

echo 'Corpus visual e semântico do documento de referência validado.'
