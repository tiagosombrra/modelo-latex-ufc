#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, tempfile, unicodedata, xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path

from normative_catalog import get_rule, load_catalog, rule_map, source_label

PASS='APROVADO'; FAIL='REPROVADO'; WARN='ALERTA'; REVIEW='REVISÃO MANUAL'; NA='NÃO APLICÁVEL'
MM=72/25.4
CATALOG=load_catalog(); RULES=rule_map(CATALOG)
PAGE=RULES['page.a4']['values']; RECTO=RULES['margin.recto']['values']
A4=(PAGE['width_mm']*MM,PAGE['height_mm']*MM); A4_TOLERANCE=PAGE.get('tolerance_pt',1.8)
LEFT=RECTO['left_mm']*MM; RIGHT=RECTO['right_mm']*MM

@dataclass
class Check:
    id:str; category:str; rule:str; source:str; status:str; evidence:str; correction:str=''; mandatory:bool=True; level:str='automático'; normative_rule:str=''; locator:str=''; normativity:str=''

def run(cmd, check=True): return subprocess.run(cmd,text=True,capture_output=True,check=check)
def tool(name):
    p=shutil.which(name)
    if not p: raise SystemExit(f'Ferramenta obrigatória não encontrada: {name}')
    return p

def norm_source(rule_id):
    rule=get_rule(CATALOG,rule_id)
    return f"{source_label(CATALOG,rule)} · {rule['locator']}"

def norm_check(check_id,rule_id,category,label,status,evidence,correction='',mandatory=True,level='automático'):
    rule=get_rule(CATALOG,rule_id)
    return Check(check_id,category,label,norm_source(rule_id),status,evidence,correction,mandatory,level,rule_id,rule['locator'],rule['normativity'])

def info(pdf):
    out={}
    for line in run([tool('pdfinfo'),str(pdf)]).stdout.splitlines():
        if ':' in line:
            k,v=line.split(':',1); out[k.strip()]=v.strip()
    return out

def fonts(pdf):
    rows=[]
    for line in run([tool('pdffonts'),str(pdf)]).stdout.splitlines()[2:]:
        parts=line.split()
        if len(parts)>=8:
            rows.append({'name':parts[0],'emb':parts[-5],'uni':parts[-3]})
    return rows

def text(pdf):
    with tempfile.NamedTemporaryFile(suffix='.txt',delete=False) as f: p=Path(f.name)
    try:
        run([tool('pdftotext'),'-layout',str(pdf),str(p)])
        return p.read_text(encoding='utf-8',errors='replace')
    finally: p.unlink(missing_ok=True)

def bbox(pdf):
    with tempfile.NamedTemporaryFile(suffix='.html',delete=False) as f: p=Path(f.name)
    try:
        run([tool('pdftotext'),'-bbox-layout',str(pdf),str(p)])
        root=ET.parse(p).getroot()
    finally: p.unlink(missing_ok=True)
    ln=lambda t:t.rsplit('}',1)[-1]
    pages=[]
    for pg in (n for n in root.iter() if ln(n.tag)=='page'):
        words=[]
        for w in (n for n in pg.iter() if ln(n.tag)=='word'):
            words.append((''.join(w.itertext()),float(w.attrib['xMin']),float(w.attrib['yMin']),float(w.attrib['xMax']),float(w.attrib['yMax'])))
        pages.append((float(pg.attrib['width']),float(pg.attrib['height']),words))
    return pages

def norm(s):
    s=unicodedata.normalize('NFKD',s)
    s=''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'\s+',' ',s.upper()).strip()
def compact(s): return re.sub(r'[^a-z0-9]','',norm(s).lower())
def verdict(cs):
    if any(c.mandatory and c.status==FAIL for c in cs): return FAIL
    if any(c.mandatory and c.status==REVIEW for c in cs): return 'REVISÃO NECESSÁRIA'
    if any(c.status in (WARN,REVIEW) for c in cs): return 'APROVADO NOS CHECKS AUTOMÁTICOS, COM RESSALVAS'
    return 'APROVADO NOS CHECKS AUTOMÁTICOS'

def check_layout(pages):
    bad=[i for i,(w,h,_) in enumerate(pages,1) if abs(w-A4[0])>A4_TOLERANCE or abs(h-A4[1])>A4_TOLERANCE]
    cs=[norm_check('layout.a4','page.a4','Layout','Papel A4',PASS if not bad else FAIL,'Todas as páginas em A4.' if not bad else f'Páginas fora de A4: {bad}','Configure papel A4 em todas as páginas.' if bad else '')]
    out=[]
    for i,(w,h,ws) in enumerate(pages,1):
        for s,x0,y0,x1,y1 in ws:
            s=s.strip()
            if not s: continue
            if re.fullmatch(r'\d+',s) and y0<70: continue
            if x0<LEFT-A4_TOLERANCE or x1>w-RIGHT+3: out.append((i,s[:24],round(x0,1),round(x1,1)))
    cs.append(norm_check('layout.margins','margin.recto','Layout','Margens horizontais do anverso: 3 cm / 2 cm',PASS if not out else FAIL,'Nenhum texto ultrapassa as margens.' if not out else f'Exemplos: {out[:8]}','Recuar o elemento para dentro da mancha gráfica.' if out else '',level='geométrico'))
    return cs

def is_text_fallback(name):
    x=re.sub(r'[^a-z0-9]','',name.lower())
    return ('texgyretermesx' in x or ('texgyretermes' in x and 'math' not in x) or 'texgyreheros' in x)

def check_fonts(fs,profile):
    cs=[]; unemb=[f['name'] for f in fs if f['emb']!='yes']
    cs.append(Check('font.embedded','Tipografia','Todas as fontes incorporadas','PDF/A / preservação',PASS if fs and not unemb else FAIL,'Todas incorporadas.' if fs and not unemb else f'Não incorporadas/indeterminadas: {unemb or "nenhuma fonte analisável"}','Recompile incorporando todas as fontes.' if unemb or not fs else ''))
    names=[re.sub(r'^[A-Z]{6}\+','',f['name']) for f in fs]; nn=[re.sub(r'[^a-z0-9]','',n.lower()) for n in names]
    allowed=RULES['font.family.body']['values']['allowed']; allowed_compact=[compact(name) for name in allowed]
    literal=[n for n,x in zip(names,nn) if any(key in x for key in allowed_compact)]
    fallback=[n for n in names if is_text_fallback(n)]
    ok=bool(literal) and not fallback
    st=PASS if ok else (WARN if profile=='portable' else FAIL)
    allowed_label=' ou '.join(allowed)
    cs.append(norm_check('font.literal','font.family.body','Tipografia',f'{allowed_label} literal',st,f'Literais: {literal or "nenhuma"}; fallback textual: {fallback or "nenhum"}',f'Use fonte-estrita=sim com {allowed_label} literal.' if not ok else '',mandatory=profile!='portable',level='tipográfico'))
    return cs

def check_structure(t):
    u=norm(t); cs=[]
    req=[('cover','Capa','UNIVERSIDADE FEDERAL DO CEARA'),('approval','Folha de aprovação','BANCA EXAMINADORA'),('resumo','Resumo','RESUMO'),('abstract','Abstract','ABSTRACT'),('toc','Sumário','SUMARIO'),('refs','Referências','REFERENCIAS')]
    for k,label,token in req:
        ok=token in u; cs.append(Check('structure.'+k,'Estrutura',label,'ABNT/UFC',PASS if ok else FAIL,'Elemento localizado.' if ok else 'Elemento não localizado.',f'Inclua {label.lower()}.' if not ok else ''))
    summary_source=norm_source('summary.paragraph')
    for k,token in [('keywords','PALAVRAS-CHAVE'),('keywords-en','KEYWORDS')]:
        ok=token in u; cs.append(Check('structure.'+k,'Resumo',token.title(),summary_source,PASS if ok else FAIL,'Campo localizado.' if ok else 'Campo ausente.',f'Inclua {token.lower()}.' if not ok else '',normative_rule='summary.paragraph',locator=RULES['summary.paragraph']['locator'],normativity=RULES['summary.paragraph']['normativity']))
    cs.append(norm_check('catalog.optional','deposit.catalog-card','Depósito UFC','Ficha catalográfica visual',NA,'A representação visual é facultativa.',mandatory=False))
    cs.append(norm_check('approval.signatures','deposit.approval-signatures','Depósito UFC','Folha de aprovação sem assinaturas digitalizadas',REVIEW,'Exige inspeção visual.','No arquivo de depósito, use a folha de aprovação sem assinaturas.',mandatory=False,level='manual'))
    cs.append(norm_check('capes','deposit.capes','Depósito UFC','Agradecimento CAPES quando aplicável',REVIEW,'Depende do financiamento.','Inclua a redação obrigatória se houver financiamento CAPES.',mandatory=False,level='condicional'))
    return cs

def check_meta(pdf,inf,profile):
    raw=pdf.read_bytes().decode('latin-1',errors='ignore')
    lang=re.search(r'/Lang\s*(?:\(([^)]*)\)|/([^\s/>]+))',raw); lang=(lang.group(1) or lang.group(2)) if lang else ''
    cs=[Check('meta.lang','Metadados','Idioma principal','WCAG PDF16 / preservação',PASS if lang else WARN,lang or 'ausente','Defina pt-BR.' if not lang else '',mandatory=False),Check('meta.title','Metadados','Título do PDF','Boa prática de repositório',PASS if inf.get('Title') else WARN,inf.get('Title') or 'ausente','Defina o título PDF/XMP.' if not inf.get('Title') else '',mandatory=False),Check('meta.author','Metadados','Autor do PDF','Boa prática de repositório',PASS if inf.get('Author') else WARN,inf.get('Author') or 'ausente','Defina o autor PDF/XMP.' if not inf.get('Author') else '',mandatory=False)]
    tagged=inf.get('Tagged','').lower()=='yes'; acc=profile=='accessibility'
    cs.append(Check('access.tagged','Acessibilidade','PDF estruturado/tagged','PDF/UA / WCAG',PASS if tagged else (FAIL if acc else WARN),f"Tagged: {inf.get('Tagged','desconhecido')}",'Gere PDF tagged.' if not tagged else '',mandatory=acc))
    outlines='/Outlines' in raw; cs.append(Check('access.bookmarks','Acessibilidade','Bookmarks','WCAG PDF2',PASS if outlines else WARN,'Detectados.' if outlines else 'Não detectados.','Adicione bookmarks hierárquicos.' if not outlines else '',mandatory=False))
    enc=inf.get('Encrypted','').lower(); cs.append(Check('security.encrypted','Integridade','Sem criptografia','Depósito/repositório',PASS if enc.startswith('no') else FAIL,inf.get('Encrypted','desconhecido'),'Remova senha/criptografia.' if not enc.startswith('no') else ''))
    meta=run([tool('pdfinfo'),'-meta',str(pdf)],check=False).stdout
    profile_name=RULES['deposit.pdfa']['values']['project_profile']; claim=bool(re.search(r'pdfaid:part[^>]*>\s*2\s*<',meta,re.I) and re.search(r'pdfaid:conformance[^>]*>\s*B\s*<',meta,re.I))
    cs.append(norm_check('pdfa.claim','deposit.pdfa','PDF/A',f'Declaração {profile_name}',PASS if claim else WARN,f'XMP declara {profile_name}.' if claim else 'Declaração não detectada.',f'Gere metadados {profile_name}.' if not claim else '',mandatory=False))
    return cs

def check_verapdf(pdf,profile):
    exe=shutil.which('verapdf'); required=profile!='portable'; profile_name=RULES['deposit.pdfa']['values']['project_profile']
    if not exe:
        cs=[norm_check('pdfa.deep','deposit.pdfa','PDF/A',f'Validação veraPDF {profile_name}',REVIEW,'veraPDF não instalado.','Execute o modo Deep com veraPDF.',mandatory=required,level='profundo')]
        if profile=='accessibility': cs.append(Check('access.pdfua','Acessibilidade','PDF/UA-1 com veraPDF','PDF/UA-1',REVIEW,'veraPDF não instalado.','Execute veraPDF -f ua1.',mandatory=True,level='profundo'))
        return cs
    def valid(flavour): return 'isCompliant="true"' in run([exe,'-f',flavour,str(pdf)],check=False).stdout
    ok=valid('2b'); cs=[norm_check('pdfa.deep','deposit.pdfa','PDF/A',f'Validação veraPDF {profile_name}',PASS if ok else FAIL,'Conforme.' if ok else 'Reprovado pelo veraPDF.','Corrija as violações do veraPDF.' if not ok else '',mandatory=required,level='profundo')]
    if profile=='accessibility':
        ua=valid('ua1'); cs.append(Check('access.pdfua','Acessibilidade','PDF/UA-1 com veraPDF','PDF/UA-1',PASS if ua else FAIL,'Conforme nos checks automáticos.' if ua else 'Reprovado.','Corrija tagging/estrutura.',mandatory=True,level='profundo'))
    return cs

def render_table(cs): return '\n'.join(f'{c.status:18} | {c.category:16} | {c.rule[:48]:48} | {c.evidence[:70]}' for c in cs)
def main():
    ap=argparse.ArgumentParser(description='Valida PDF acadêmico UFC/ABNT.'); ap.add_argument('pdf',type=Path); ap.add_argument('--profile',choices=('strict','portable','accessibility'),default='strict'); ap.add_argument('--format',choices=('table','json','markdown'),default='table'); ap.add_argument('--output',type=Path); a=ap.parse_args(); pdf=a.pdf.resolve()
    if not pdf.is_file(): raise SystemExit(f'Arquivo não encontrado: {pdf}')
    inf=info(pdf); fs=fonts(pdf); t=text(pdf); pages=bbox(pdf); cs=[Check('pdf.open','Integridade','PDF legível','Pré-requisito técnico',PASS,f"{inf.get('Pages','?')} páginas; PDF {inf.get('PDF version','?')}.")]; cs+=check_layout(pages)+check_fonts(fs,a.profile)+check_structure(t)+check_meta(pdf,inf,a.profile)+check_verapdf(pdf,a.profile)
    if a.profile=='accessibility': cs += [Check('access.alt','Acessibilidade','Texto alternativo adequado','PDF/UA / WCAG',REVIEW,'Qualidade exige revisão humana.','Revise /Alt e artefatos decorativos.',mandatory=True,level='manual'),Check('access.order','Acessibilidade','Ordem de leitura lógica','PDF/UA / WCAG',REVIEW,'Exige teste com tecnologia assistiva.','Revise a ordem de leitura.',mandatory=True,level='manual')]
    v=verdict(cs); base={'schema_version':CATALOG['schema_version'],'reviewed_at':CATALOG['reviewed_at']}
    if a.format=='json': out=json.dumps({'file':pdf.name,'profile':a.profile,'verdict':v,'normative_catalog':base,'checks':[asdict(c) for c in cs]},ensure_ascii=False,indent=2)+'\n'
    elif a.format=='markdown':
        esc=lambda x:str(x).replace('|','\\|').replace('\n',' '); lines=['# Relatório de validação UFC','',f'Arquivo: `{pdf.name}`',f'Perfil: `{a.profile}`',f'Veredito: **{v}**',f'Base normativa revisada em: `{CATALOG["reviewed_at"]}`','','| Status | Categoria | Regra | Fonte | Evidência | Como corrigir |','|---|---|---|---|---|---|']; lines += [f'| {esc(c.status)} | {esc(c.category)} | {esc(c.rule)} | {esc(c.source)} | {esc(c.evidence)} | {esc(c.correction)} |' for c in cs]; out='\n'.join(lines)+'\n'
    else: out=f'Arquivo: {pdf.name}\nPerfil: {a.profile}\nVeredito: {v}\nBase normativa: {CATALOG["reviewed_at"]}\n\n{render_table(cs)}\n'
    (a.output.write_text(out,encoding='utf-8') if a.output else print(out,end='')); raise SystemExit(1 if v==FAIL else 0)
if __name__=='__main__': main()
