# Auditoria final V2.1.0

Data: 2026-08-21.

## Escopo

Segunda auditoria normativa e visual executada antes da tag `v2.1.0`, após Gate A, Gate R, Gate T, distribuição e smoke real no Overleaf. O objetivo foi revalidar o PDF de referência e distinguir conformidade institucional obrigatória, portabilidade e acessibilidade avançada.

## Base normativa reconfirmada

A política de `docs/NORMAS.md` permanece válida: normas/atos institucionais aplicáveis, edições ABNT vigentes e requisitos UFC compatíveis. Para trabalhos acadêmicos são adotadas NBR 14724:2024 (versão corrigida de 2025), NBR 10520:2023, NBR 6023:2025, NBR 6028:2021, NBR 6024:2012, NBR 6027:2012, NBR 6034:2004, NBR 12225:2023 e, para projetos, NBR 15287:2025, além das Normas de Apresentação Tabular do IBGE e atos institucionais UFC.

O SiBi-UFC exige arquivo eletrônico PDF/A da capa aos anexos e folha de aprovação sem assinaturas para depósito. A Instrução Normativa Conjunta nº 2/2026 torna facultativa a ficha catalográfica visual em TCC, dissertação e tese.

## Achados adicionais

| ID | Achado | Classificação | Ação |
|---|---|---|---|
| F1 | números de linha de códigos e algoritmos apareciam antes do limite esquerdo de 3 cm no PDF de referência | DIVERGENTE | `objetos.def` passa a reservar margem interna apenas quando existe numeração; gate geométrico mede coordenadas do PDF |
| F2 | smoke real no Overleaf compilou 41 páginas sem warnings/erros, mas usou NewTX porque Times New Roman literal não estava disponível | PORTABILIDADE CONFORME; UFC ESTRITO NÃO CONFORME | documentação e validador distinguem smoke funcional de certificação tipográfica; modo estrito exige fonte literal |
| F3 | PDF de referência é PDF/A-2b e possui idioma `pt-BR`, mas não possui tagged PDF, bookmarks nem título/autor completos nos metadados | ACESSIBILIDADE AVANÇADA INCOMPLETA | perfil de acessibilidade do validador reporta os itens; não são atribuídos como requisito de depósito UFC sem fonte institucional |
| F4 | checks automáticos anteriores não distinguiam requisito verificável, heurístico e revisão humana | LACUNA DE VALIDAÇÃO | novo validador usa estados APROVADO/REPROVADO/ALERTA/REVISÃO MANUAL/NÃO APLICÁVEL e registra nível de evidência |
| F5 | listas paginadas e entradas de nível primário do sumário podiam ser emitidas sem líder pontilhado pelo padrão do `abntexto` | DIVERGENTE | perfil UFC reativa `\extdotleaders`; regressão cobre ilustrações, figuras, tabelas, quadros, gráficos, códigos, algoritmos e entradas textuais/pós-textuais do sumário |
| F6 | CI acumulava workflows obsoletos e fragmentava a validação em muitos scripts/alvos, aumentando recompilações e tempo de diagnóstico | EFICIÊNCIA/MANUTENIBILIDADE | `concurrency` cancela runs antigos; `tests/run.py` passa a ser o orquestrador único com execução acumulativa, logs por check e relatório Markdown/JSON |

## Veredito do PDF anterior à correção F1

O PDF canônico de 41 páginas estava estruturalmente íntegro, A4, PDF/A-2b, com fontes incorporadas e Unicode, estrutura pré/textual/pós-textual completa, resumo/abstract na faixa exercitada e sem warnings/overflow. Entretanto, ele não poderia receber veredito UFC estrito porque:

1. a numeração de código/algoritmo invadia a margem esquerda;
2. a família textual era fallback portátil, não Times New Roman/Arial literal.

O primeiro ponto é defeito da classe e deve ser corrigido antes da tag. O segundo é propriedade do perfil portátil do artefato de referência: a classe possui rota estrita certificada no Gate T Windows, e o PDF destinado ao depósito deve ser validado no perfil `strict`.

## Validador de PDF

A V2 passa a incluir um validador independente do LaTeX:

- Web/Lite: GitHub Pages, execução local no navegador com PDF.js; o arquivo não é transmitido;
- CLI/Deep: Poppler para geometria/fontes/texto e veraPDF quando disponível para PDF/A-2b e PDF/UA-1;
- perfis: `strict`, `portable` e `accessibility`;
- saída: tabela, JSON ou Markdown, com evidência e orientação de correção.

O validador não presume conformidade sem evidência. Requisitos sem prova automática suficiente permanecem em revisão manual.

## Gate V — validador e regressão geométrica

Antes da tag, o PR final incorpora `tools/validate-ufc-pdf.py`, a interface `validator/` para GitHub Pages, o workflow de validação/deploy e `tests/v2-pdf-validator-check.sh`. O novo gate executa o validador no perfil portátil sobre o próprio PDF de referência e exige, entre outros itens, A4, margens horizontais, fontes incorporadas, estrutura acadêmica e declaração PDF/A.

O perfil portátil admite fallback tipográfico apenas como alerta. O perfil estrito reprova a ausência de Times New Roman/Arial literal e exige validação profunda de PDF/A para um veredito técnico completo. O perfil de acessibilidade acrescenta tagging/PDF/UA e mantém como revisão humana os requisitos sem evidência automática suficiente.

## Gate C — CI consolidado

A interface principal de validação passa a ser `python3 tests/run.py --mode pr`, também disponível por `make check` e `make preflight`. O runner executa checks independentes até o fim, bloqueia apenas dependentes cujo artefato necessário falhou e grava evidências em `artifacts/validation/`.

O modo `release` acrescenta as certificações profundas de PDF/A e é exposto por `make release-check` e `make release-preflight`. Os alvos e scripts `v2-*` permanecem temporariamente como implementação de compatibilidade durante a migração. Após equivalência comprovada no mesmo SHA, checks textuais e geométricos serão absorvidos por módulos Python e os scripts redundantes poderão ser removidos sem alterar a interface pública do CI.

O workflow de auditoria usa `concurrency` com cancelamento de execução anterior no mesmo PR. Assim, novos commits não deixam auditorias pesadas obsoletas consumindo runners enquanto o head já mudou.
