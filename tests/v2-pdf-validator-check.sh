#!/bin/sh
set -eu
pdf="${1:-documento.pdf}"
report="/tmp/ufctex-v2-pdf-validator.json"
[ -f "$pdf" ] || { echo "Validador PDF V2 falhou: $pdf não existe."; exit 1; }
python3 -m py_compile tools/validate-ufc-pdf.py
python3 - <<'PY'
import runpy
import sys

sys.path.insert(0, 'tools')
module = runpy.run_path('tools/validate-ufc-pdf.py', run_name='ufc_pdf_validator')

def font_status(names, profile):
    rows = [{'name': name, 'emb': 'yes', 'uni': 'yes'} for name in names]
    return module['check_fonts'](rows, profile)[-1].status

for names in (
    ['TimesNewRomanPSMT', 'NewTXMI', 'txsys'],
    ['ArialMT', 'TeXGyreTermesMath-Regular'],
):
    status = font_status(names, 'strict')
    if status != module['PASS']:
        raise SystemExit(f'fonte literal com matemática complementar deveria passar: {names}: {status}')

fallback = ['TeXGyreTermesX-Regular', 'NewTXMI']
if font_status(fallback, 'strict') != module['FAIL']:
    raise SystemExit('fallback textual deveria reprovar no perfil strict')
if font_status(fallback, 'portable') != module['WARN']:
    raise SystemExit('fallback textual deveria gerar alerta no perfil portable')
PY
set +e
python3 tools/validate-ufc-pdf.py "$pdf" --profile portable --format json --output "$report"
validator_status=$?
set -e
python3 - "$report" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8')); c={x['id']:x for x in r['checks']}
needed={'pdf.open','layout.a4','layout.margins','font.embedded','font.literal','structure.cover','structure.approval','structure.resumo','structure.abstract','structure.toc','structure.refs','pdfa.claim'}
missing=sorted(needed-c.keys())
if missing: raise SystemExit(f'checks ausentes: {missing}')
bad=[x for x in r['checks'] if x['mandatory'] and x['status']=='REPROVADO']
if bad: raise SystemExit('; '.join(f"{x['id']}: {x['evidence']}" for x in bad))
if c['layout.margins']['status']!='APROVADO': raise SystemExit(c['layout.margins']['evidence'])
if c['font.literal']['status'] not in {'APROVADO','ALERTA'}: raise SystemExit('perfil portátil não deve reprovar apenas por fallback tipográfico')
PY
if [ "$validator_status" -ne 0 ]; then
  echo "Validador PDF V2 falhou com status $validator_status sem reprovação obrigatória identificada no relatório."
  exit "$validator_status"
fi
echo 'Gate V2 do validador de PDF concluído.'
