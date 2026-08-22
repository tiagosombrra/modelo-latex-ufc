# Base normativa da V2

Última auditoria normativa: **2026-08-22**.  
Estado de implementação tipográfica: **Fase 2 concluída em 2026-08-21; Gate T encerrado**.

Este arquivo é a fonte única do projeto para política normativa, classificação de conformidade e vínculo entre requisito, implementação e teste.

## Política normativa

A V2 adota a edição vigente mais recente de cada norma aplicável. Quando um guia institucional ainda citar edição substituída, a decisão segue esta ordem:

1. legislação, regulamento, instrução normativa ou resolução institucional aplicável;
2. edição vigente da norma ABNT;
3. requisito institucional específico da UFC compatível com a norma vigente;
4. Guia de Normalização da UFC mais recente aplicável;
5. comportamento de `abntexto` e demais pacotes.

O comportamento de um pacote nunca prevalece sobre requisito normativo ou institucional aplicável.

## Auditoria institucional de 2026-08-20

A página de Normalização de Trabalhos Acadêmicos do Sistema de Bibliotecas da UFC foi atualizada em 4 de março de 2026 e declara que os guias institucionais estão de acordo com as normas ABNT vigentes. Os PDFs vinculados, porém, possuem datas e bases normativas diferentes.

| Documento UFC atualmente vinculado | Base declarada no PDF | Situação na auditoria |
|---|---|---|
| Guia de Normalização de Trabalhos Acadêmicos, 2022 | NBR 14724:2011, NBR 6023:2018, NBR 10520:2002 e NBR 12225:2004 | preservar requisitos institucionais somente quando compatíveis com as normas vigentes |
| Guia de Normalização para Elaboração de Citações, 2025 | NBR 10520:2023 e NBR 6023:2018 | NBR 10520:2023 atual; referência à NBR 6023:2018 superada pela edição de 2025 |
| Guia de Normalização para Elaboração de Referências | NBR 6023:2018 | superado pela NBR 6023:2025 |
| Guia de Normalização de Projetos de Pesquisa | NBR 15287:2011 e outras edições históricas | superado pela NBR 15287:2025 e pelas demais normas vigentes aplicáveis |

A Instrução Normativa Conjunta nº 2/2026/SIBI/PROGRAD/PRPPG, de 10 de fevereiro de 2026, tem precedência sobre disposições técnicas conflitantes de guias anteriores. Ela torna facultativa a ficha catalográfica visual para TCC, dissertação e tese depositados no Repositório Institucional.

A Portaria CAPES nº 206/2018 permanece vigente. O agradecimento CAPES é obrigatório quando o trabalho resultar de atividade financiada total ou parcialmente pela CAPES; essa condição deve ser informada pelo autor e não pode ser inferida pela classe.

A data de um PDF institucional não é tratada como prova isolada de vigência normativa.

## Normas e atos adotados

| Assunto | Referência | Uso principal |
|---|---|---|
| Trabalhos acadêmicos | **ABNT NBR 14724:2024**, versão corrigida de 01/04/2025 | estrutura, apresentação, paginação e elementos documentais |
| Citações | **ABNT NBR 10520:2023** | citações diretas, indiretas, autor-data e `apud` |
| Referências | **ABNT NBR 6023:2025** | elaboração e apresentação das referências |
| Projetos de pesquisa | **ABNT NBR 15287:2025** | perfis `projeto` e `projetoanonimizado` |
| Resumos | **ABNT NBR 6028:2021** | resumo, abstract e palavras-chave |
| Numeração progressiva | **ABNT NBR 6024:2012** | seções e subdivisões |
| Sumário | **ABNT NBR 6027:2012** | composição e hierarquia do Sumário |
| Índice | **ABNT NBR 6034:2004** | índice remissivo opcional |
| Lombada | **ABNT NBR 12225:2023** | requisito condicional |
| Tabelas numéricas | **IBGE, Normas de apresentação tabular, 3. ed., 1993** | estrutura de tabelas numéricas |
| Ficha catalográfica | **IN Conjunta UFC nº 2/2026** | caráter facultativo da representação visual no depósito |
| Agradecimento CAPES | **Portaria CAPES nº 206/2018** | requisito condicional ao financiamento CAPES |

As edições devem ser reconfirmadas antes de cada nova versão principal do template.

## Estados da matriz

- **CONFORME**: requisito implementado e sustentado por evidência/teste compatível;
- **CONFORME NO ESCOPO TESTADO**: requisito amplo cuja parcela exercitada possui evidência suficiente;
- **DIVERGENTE**: implementação atual contraria requisito vigente;
- **INCOMPLETO**: regra conhecida, mas falta decisão técnica, cobertura ou evidência exigida para a próxima release;
- **NÃO APLICÁVEL**: requisito condicional fora do escopo da distribuição corrente.

Um fallback de compatibilidade não transforma um PDF em tipograficamente conforme. Para a família textual, conformidade final exige **Arial ou Times New Roman literais** no PDF produzido.

O PDF certificado também deve ser **autocontido para renderização**: todas as fontes efetivamente utilizadas devem estar incorporadas (`emb=yes` em `pdffonts`). Incorporação por subconjunto é aceita, pois os glifos utilizados permanecem dentro do arquivo; qualquer fonte com `emb=no` reprova o artefato.

## Matriz requisito → implementação → teste

| Requisito | Estado | Evidência / decisão |
|---|---|---|
| papel A4 | **CONFORME** | `tests/v2-pdf-geometry-check.sh` mede o PDF real |
| margens anverso 3 cm esquerda/superior e 2 cm direita/inferior | **CONFORME** | `ufctex/layout.def` + gate geométrico |
| margens espelhadas no frente-verso | **CONFORME** | `ufctex/layout.def` + gate geométrico |
| fonte-base em tamanho 12 | **CONFORME** | `abntexto` carregado em 12 pt; gates tipográficos medem o tamanho nominal |
| seleção pública `fonte=times|arial` | **CONFORME NO ESCOPO TESTADO** | `ufctex/fontes.def` + `tests/v2-font-config-check.sh` |
| política `fonte-estrita=sim|nao` | **CONFORME NO ESCOPO TESTADO** | modo estrito rejeita fonte literal ausente; modo não estrito registra fallback explicitamente |
| Times New Roman/Arial literais no PDF final | **CONFORME NO ESCOPO TESTADO** | Gate T Windows certifica as duas famílias em modo estrito, pdfLaTeX e LuaLaTeX, com identidade literal, extração Unicode, `emb=yes` e PDF/A-2b |
| variantes regular/negrito/itálico/negrito-itálico das fontes literais | **CONFORME NO ESCOPO TESTADO** | Gate T exerce e identifica as quatro variantes de Times New Roman e Arial nos dois motores |
| todas as fontes usadas incorporadas ao PDF final | **CONFORME NO ESCOPO TESTADO** | `tests/v2-font-embedding-check.sh` reprova `emb=no` ou ausência de fontes; documento de referência, matriz de perfis e POC Windows usam o mesmo gate |
| `rmfamily`, `sffamily` e `ttfamily` preservando a família institucional | **CONFORME NO ESCOPO TESTADO** | `fontes.def` mapeia os três slots; gate tipográfico exerce os três |
| tamanhos reduzidos uniformes nas exceções controladas pela classe | **CONFORME NO ESCOPO TESTADO** | citação longa, notas, paginação, epígrafe, títulos/fontes/notas de objetos e tabelas usam tamanho reduzido; gates tipométricos cobrem os casos controláveis |
| ficha catalográfica externa em tamanho normativo | **NÃO APLICÁVEL à tipografia interna da classe** | quando incluída, é PDF externo; deve ser gerada conforme a fonte institucional e revalidada no PDF/A final |
| recuo da primeira linha do parágrafo em 2 cm | **CONFORME** | `layout.def` + `tests/v2-layout-check.sh` |
| ausência de espaço adicional entre parágrafos | **CONFORME** | `\parskip=0pt` |
| espaço 1,5 no corpo | **CONFORME** | `\onehalfsp` aplicado no início do documento |
| natureza do trabalho em espaço simples | **CONFORME** | capa/folha de rosto usam bloco em `\singlesp` |
| notas de rodapé em tamanho reduzido e espaço simples | **CONFORME** | `\abntsmall\singlesp` + gate de tamanho/entrelinha |
| filete de 5 cm das notas de rodapé | **CONFORME** | `\footnoterule` redefine largura para 5 cm |
| linhas subsequentes da nota alinhadas sob a primeira letra do texto | **CONFORME** | recuo suspenso medido em `tests/v2-layout-check.sh` |
| estrutura principal baseada em seções, sem capítulos | **CONFORME** | `\usechapters` gera erro e distribuição bloqueia `\chapter` |
| cinco níveis de seção e correspondência no Sumário | **CONFORME** | hierarquia definida em `layout.def` e TOC exercitado nos gates |
| início de seção primária em nova página/anverso | **CONFORME** | `\ufcPrimarySectionBreak` + testes duplex |
| alinhamento de títulos de seção com mais de uma linha | **CONFORME** | composição suspensa do `abntexto`, auditada |
| capa e folha de rosto | **CONFORME** | perfis e pré-textuais exercitados nos dois motores |
| natureza/orientação a partir do meio da mancha gráfica | **CONFORME** | bloco textual deslocado conforme política UFC |
| folha de aprovação sem imagens de assinatura para depósito | **CONFORME** | classe não incorpora assinaturas digitalizadas |
| ficha catalográfica visual facultativa | **CONFORME** | `ficha-catalografica=nao` é o padrão conforme IN Conjunta 2/2026 |
| ficha catalográfica não contada nem numerada | **CONFORME** | contador lógico e paridade física testados em dois motores e dois modos |
| contagem dos pré-textuais e numeração somente a partir do textual | **CONFORME** | gates de paginação, ficha e geometria |
| posição da paginação anverso/frente-verso | **CONFORME** | gate geométrico mede canto superior direito/esquerdo; `abntexto` aplica `\abntsmall` à paginação |
| paginação contínua em apêndices e anexos | **CONFORME** | pós-textuais preservam a sequência |
| trabalhos em mais de um volume | **CONFORME** | `volume` e `pagina-inicial` com regressão própria |
| dedicatória sem título | **CONFORME** | gate pré-textual verifica ausência de título |
| agradecimentos, errata, resumo, abstract e listas | **CONFORME** | presença e títulos exercitados nos gates |
| agradecimento CAPES quando aplicável | **CONFORME NO ESCOPO DO TEMPLATE** | `1-pre-textuais/agradecimentos.tex` orienta o autor e `tests/v2-capes-guidance-check.sh` protege a orientação; a condição depende do financiamento |
| epígrafe iniciando abaixo do meio da folha/página | **CONFORME** | `pretextuais.def` posiciona o bloco na metade inferior e `tests/v2-pretextual-check.sh` mede a coordenada no PDF |
| epígrafe longa em 10 pt, espaço simples e recuo de 4 cm | **CONFORME** | implementação explícita em `pretextuais.def` |
| resumo e abstract sem recuo de primeira linha | **CONFORME** | `\parindent=0pt` nos dois elementos |
| resumo/abstract entre 150 e 500 palavras | **CONFORME** | `tests/v2-reference-check.sh` conta palavras |
| palavras-chave/keywords | **CONFORME** | API e documento de referência exercitados |
| pré-textuais fora do Sumário | **CONFORME** | gate verifica que não entram no TOC |
| pré-textuais iniciando em anverso no duplex | **CONFORME** | `tests/v2-duplex-pretextual-check.sh` |
| citação autor-data, autores múltiplos, pessoa jurídica, homônimos e `apud` | **CONFORME** | `tests/v2-bibliography-check.sh` |
| citação direta longa: fonte menor, simples, sem aspas, recuo de 4 cm e separação vertical | **CONFORME** | `v2-normative-complement-check.sh` + comportamento auditado de `\Enquote` |
| referências em espaço simples | **CONFORME** | gate mede o espaçamento efetivo |
| uma linha simples entre referências | **CONFORME** | gate mede `bibitemsep`/`itemsep` |
| NBR 6023:2025 | **CONFORME NO ESCOPO TESTADO** | regressões cobrem os casos implementados pelo projeto |
| referências próprias de anexo no próprio anexo | **CONFORME NO ESCOPO TESTADO** | `tests/v2-documentary-source-check.sh` usa referência bibliográfica completa em nota dentro do anexo |
| título de ilustração limitado à largura real do objeto | **CONFORME** | `objetos.def` usa `min(legendmaxwidth,savedplacewidth)`; gate mede objeto de 6 cm |
| título de ilustração em tamanho reduzido | **CONFORME** | `\abntsmall\singlesp` + gate tipométrico de objeto |
| fonte e nota de ilustração dentro dos limites do objeto | **CONFORME** | `tests/v2-object-geometry-check.sh` mede largura real e tamanho de título, Fonte e Nota |
| indicação de fonte de elaboração própria | **CONFORME** | fixtures e gate verificam `Fonte:` |
| fonte externa de ilustração/tabela conforme NBR 10520 | **CONFORME NO ESCOPO TESTADO** | `tests/v2-documentary-source-check.sh` usa citação autor-data real em `Fonte:` |
| Lista de Ilustrações agregando figuras, gráficos e quadros | **CONFORME** | regressão verifica conteúdo e exclui tabelas |
| tabelas em lista própria | **CONFORME** | regressões exercitam lista de tabelas |
| apresentação tabular segundo IBGE | **CONFORME NO ESCOPO TESTADO** | `tests/v2-table-ibge-check.sh` exige tabela numérica aberta nas laterais, sem grade no corpo, com regras superior/cabeçalho/inferior, Fonte e incorporação de fontes |
| corpo de tabela em tamanho 12 e elementos descritivos em tamanho reduzido | **CONFORME NO ESCOPO TESTADO** | módulo `tabularray` mantém corpo em `\normalsize` e aplica `\abntsmall` a legenda/Fonte/Nota; gate mede os tamanhos |
| linhas alternadas em tabelas | **CONFORME COMO OPÇÃO EDITORIAL** | `xcolor` é carregado pelo módulo e `tabularray` aceita `row{even}`; não é aplicado por padrão |
| equações numeradas e referência resolvida | **CONFORME** | fixture normativa específica |
| número da equação alinhado à direita da mancha gráfica | **CONFORME NO ESCOPO TESTADO** | `tests/v2-math-check.sh` mede coordenada no PDF real |
| tipografia de código com `listings` | **CONFORME NO ESCOPO TESTADO** | default `\ttfamily\normalsize`; `ttfamily` é remapeada à família institucional; gate próprio |
| tipografia de código com `minted` | **CONFORME NO ESCOPO TESTADO** | default `fontfamily=tt, fontsize=\normalsize`; gate consulta a fonte renderizada via `pdffonts` |
| tipografia de algoritmos | **CONFORME NO ESCOPO TESTADO** | `ufcalgoritmo` usa tamanho normal e família textual institucional; gate próprio |
| tipografia matemática | **CONFORME NO ESCOPO TESTADO** | matemática é complementar e testada separadamente; não é declarada como Times/Arial textual |
| estrutura de projetos NBR 15287:2025 | **CONFORME NO ESCOPO TESTADO** | fixture cobre elementos exigidos no escopo do template |
| projeto anonimizado sem vazamento de autor/orientador | **CONFORME** | gate semântico específico |
| glossário, apêndice, anexo e índice | **CONFORME NO ESCOPO TESTADO** | ordem, presença, TOC e início no anverso verificados |
| ênfase tipográfica de títulos de apêndices/anexos igual à seção primária | **CONFORME** | `abntexto` reutiliza a política tipográfica da seção primária |
| lombada NBR 12225:2023 | **NÃO APLICÁVEL à distribuição eletrônica corrente** | extensão condicional futura |
| PDF/A para depósito | **CONFORME** | `\DocumentMetadata` + validação independente com veraPDF |
| PDF/A-2b | **CONFORME COMO ESCOLHA TÉCNICA DO PROJETO** | subtipo técnico do projeto, não imposição atribuída à UFC |

## Gate N — encerrado

A auditoria normativa de 2026 está **fechada em 20/08/2026**. Não há requisito crítico sem origem normativa ou decisão explícita.

O fechamento do Gate N identificou as divergências e lacunas que foram encaminhadas à Fase 2. A certificação tipográfica correspondente foi concluída posteriormente no Gate T.

## Fase 2 — Tipografia e fontes — encerrada

### Implementado

1. módulo `ufctex/fontes.def` separado de `layout.def`;
2. API pública `fonte=times|arial`;
3. API pública `fonte-estrita=sim|nao`;
4. política explícita de fallback sem declarar substituto como Times New Roman/Arial;
5. unificação de `rmfamily`, `sffamily` e `ttfamily` na família institucional selecionada;
6. política de código `listings` e `minted` em tamanho 12 por padrão;
7. política de algoritmos em tamanho 12 por padrão;
8. política matemática complementar explícita;
9. título, Fonte e Nota de objetos limitados à largura física da ilustração e em tamanho reduzido;
10. fonte externa de objeto e referência bibliográfica local de anexo com regressão própria;
11. subconjunto tabular IBGE com corpo 12, legenda/Fonte/Nota reduzidas e suporte opcional a linhas alternadas;
12. orientação CAPES condicional protegida por gate;
13. gates tipográficos específicos para seleção de fonte, código, `minted`, algoritmos, matemática, objetos e tabelas;
14. gate geral de incorporação que exige `emb=yes` para todas as fontes utilizadas no PDF;
15. Gate T Windows obrigatório para Times New Roman e Arial literais, com geração local do suporte pdfLaTeX e certificação em pdfLaTeX/LuaLaTeX;
16. proxy Overleaf em TeX Live 2025 com `abntexto` 1.1 íntegro e pinado, integrado ao Gate T das branches V2.

### Gate T — encerrado

O Gate T foi encerrado em **21/08/2026** com as seguintes evidências:

1. Times New Roman e Arial literais compiladas em pdfLaTeX e LuaLaTeX;
2. variantes regular, negrito, itálico e negrito-itálico identificadas para as duas famílias;
3. extração Unicode correta, incluindo acentuação e caracteres usados em português;
4. todas as fontes utilizadas nos quatro PDFs estritos incorporadas (`emb=yes`);
5. quatro PDFs estritos aprovados como PDF/A-2b pelo veraPDF;
6. documento de referência e matriz de seis perfis × dois motores revalidados, totalizando 12 PDFs da matriz;
7. proxy Overleaf TeX Live 2025 + `abntexto` 1.1 aprovado;
8. jobs Windows, certificação PDF/A e proxy Overleaf integrados ao `latex-preflight` obrigatório para `main` e branches `maintenance/v2.*`.

O proxy Overleaf é evidência de compatibilidade com o ambiente público estável consultado, mas não substitui o smoke final realizado dentro do serviço Overleaf durante a fase de distribuição.

## Requisitos institucionais UFC

### Tipografia

O Guia UFC de Trabalhos Acadêmicos atualmente vinculado exige **Arial ou Times New Roman, tamanho 12**, inclusive na capa. Prevê tamanho menor e uniforme para citações longas, notas de rodapé, paginação, ficha catalográfica, legendas e fontes de ilustrações e tabelas, recomendando tamanho 10 para essas exceções.

A V2 distingue fonte literal de substitutos de compatibilidade. `NewTX`, `TeX Gyre Termes` e `TeX Gyre Heros` não são declarados como Times New Roman ou Arial.

`fonte-estrita=sim` é a rota de certificação tipográfica: se a família literal solicitada não estiver disponível, a compilação deve falhar. `fonte-estrita=nao` existe para portabilidade e desenvolvimento, mas um PDF produzido com fallback não deve ser apresentado como tipograficamente conforme à exigência UFC de família literal.

Não foi localizada exceção institucional de família para código. Por isso, `listings`, `minted`, URLs e demais usos de `ttfamily` permanecem dentro da família institucional selecionada. Matemática é tratada separadamente por exigir repertório tipográfico próprio.

### Matemática

A família matemática é complementar à família textual. A V2 usa NewTX Math no pdfLaTeX e uma família matemática OpenType compatível no LuaLaTeX, preferindo TeX Gyre Termes Math quando disponível. Essa família complementar não é descrita como “Times New Roman matemática” ou “Arial matemática”.

Equações numeradas usam algarismos arábicos entre parênteses e o gate geométrico verifica o alinhamento à direita da mancha gráfica.

### PDF/A

As orientações de recebimento consultadas em 2026 exigem arquivo eletrônico **PDF/A** para TCC, dissertações e teses destinados ao repositório.

A V2 usa **PDF/A-2b** como perfil técnico verificável. O subtipo 2b é escolha de implementação do projeto, não requisito específico atribuído à UFC.

Para a certificação da V2, o PDF final deve permanecer autocontido: todas as fontes utilizadas na renderização precisam estar incorporadas. O gate consulta `pdffonts` e reprova qualquer ocorrência `emb=no`, além da validação estrutural independente com veraPDF.

### Folha de aprovação

A versão destinada ao repositório deve apresentar a folha de aprovação sem assinaturas. A V2 produz identificação e linhas da banca, mas não incorpora assinaturas digitalizadas.

### Ficha catalográfica

A Instrução Normativa Conjunta nº 2/2026 torna facultativa a representação visual da ficha catalográfica para TCC, dissertações e teses. Por isso, `ficha-catalografica=nao` permanece o padrão.

Quando a ficha for incluída, o verso com dados catalográficos não é contado nem numerado. A implementação restaura o contador lógico e preserva a paridade física também no modo `frente-verso`.

Como a ficha é um PDF externo, sua tipografia e conformidade PDF/A devem ser verificadas no próprio arquivo e novamente no PDF final consolidado.

### Trabalhos em mais de um volume

A identificação do volume aparece quando o trabalho é dividido em mais de um volume, e a paginação permanece única e sequencial. A V2 oferece `volume` e `pagina-inicial`, com regressão própria.

### Frente e verso

No modo `frente-verso`:

- anverso: esquerda/superior 3 cm; direita/inferior 2 cm;
- verso: direita/superior 3 cm; esquerda/inferior 2 cm;
- numeração à direita no anverso e à esquerda no verso;
- elementos pré-textuais, exceto a página destinada aos dados catalográficos, iniciam no anverso;
- seções textuais primárias e elementos pós-textuais controlados pela V2 iniciam no anverso.

### Paginação

Os elementos pré-textuais são contados a partir da folha de rosto e não são numerados. O verso destinado aos dados catalográficos não é contado nem numerado. A numeração aparece a partir da primeira página textual. Apêndices, anexos e volumes mantêm sequência contínua. A paginação textual usa tamanho reduzido pelo mecanismo do `abntexto` auditado.

### Espaçamento

O Guia UFC orienta espaço 1,5 no corpo e espaço simples nas exceções institucionais. Não deve existir espaço adicional entre parágrafos. Referências consecutivas são separadas por uma linha simples em branco.

### Epígrafe

O Guia UFC orienta que a epígrafe se inicie abaixo do meio da folha/página. A V2 posiciona o bloco na metade inferior e o gate de pré-textuais mede essa coordenada no PDF. Para até três linhas, preserva recuo de 8 cm, fonte 12 e espaço 1,5; para mais de três linhas, usa recuo de 4 cm, fonte 10 e espaço simples.

### Ilustrações e tabelas

A NBR 14724:2024 determina que identificação, título, fonte, legenda e notas acompanhem os limites da própria ilustração. A fonte consultada deve seguir a NBR 10520; quando o objeto for do próprio autor, deve haver indicação equivalente a “Elaboração própria”.

A V2 limita título, Fonte e Nota à largura física real do objeto e mede esses elementos em regressão própria. Fonte externa é exercitada com citação autor-data real.

Para tabelas numéricas, o perfil `tabularray` segue o subconjunto IBGE auditado: tabela aberta nas laterais, sem grade horizontal no corpo, com regra superior, separação do cabeçalho e regra inferior. O corpo permanece em tamanho 12; legenda, Fonte e Nota usam tamanho reduzido. Linhas alternadas por cor são uma opção editorial e não são aplicadas por padrão.

A Lista de Ilustrações agrega figuras, gráficos e quadros na ordem de ocorrência. Tabelas permanecem em lista própria.

### Citações e referências

O Guia UFC de Citações de 2025 foi elaborado conforme a NBR 10520:2023. Citações diretas longas usam parágrafo distinto, letra menor, espaço simples, sem aspas e recuo de 4 cm, com separação do texto anterior/posterior.

Para referências, prevalece a NBR 6023:2025. Referências usam espaço simples internamente e uma linha simples de separação. Referências próprias de anexo permanecem no próprio anexo; o gate documental inclui um caso bibliográfico real em nota local.

### CAPES

Quando o trabalho decorrer de atividade financiada total ou parcialmente pela CAPES, o autor deve incluir o agradecimento exigido pela Portaria CAPES nº 206/2018. O template contém a orientação e a redação obrigatória como comentário em `1-pre-textuais/agradecimentos.tex`. A classe não tenta inferir se o requisito é aplicável.

### Projetos de pesquisa

Para `projeto` e `projetoanonimizado`, a V2 adota NBR 15287:2025 e preserva somente requisitos UFC compatíveis com a edição vigente.

## Mapa de implementação

| Parte | Norma/requisito principal | Implementação |
|---|---|---|
| configuração e perfis | política UFC + normas por tipo | `ufctex/core.def` |
| tipografia textual e matemática | NBR 14724:2024 + requisito UFC Arial/Times New Roman | `ufctex/fontes.def` |
| papel, margens e espaçamento | NBR 14724:2024 + UFC | `ufctex/layout.def` |
| duplex e início no anverso | NBR 14724:2024 + UFC | `ufctex/layout.def` + regressões geométricas |
| ativos institucionais | identidade visual UFC | `ufctex/institucional.def` + `assets/institucional/` |
| capa e folha de rosto | NBR 14724:2024 + UFC | `ufctex/pretextuais.def` + `ufctex/trabalhos.def` |
| volume e paginação contínua | NBR 14724:2024 + UFC | `ufctex/trabalhos.def` |
| ficha catalográfica | IN Conjunta 2/2026 + NBR 14724:2024 | `ufctex/trabalhos.def` + regressão dedicada |
| folha de aprovação | NBR 14724:2024 + política de depósito UFC | `ufctex/pretextuais.def` |
| dedicatória, agradecimentos, epígrafe e errata | NBR 14724:2024 + UFC + Portaria CAPES 206/2018 | `ufctex/pretextuais.def` + arquivos de conteúdo |
| resumo e abstract | NBR 6028:2021 + UFC | `ufctex/pretextuais.def` |
| listas e Sumário | NBR 14724:2024 + NBR 6027:2012 | `ufctex/pretextuais.def` + `ufctex/objetos.def` |
| seções e subdivisões | NBR 6024:2012 + UFC | `ufctex/layout.def` / `abntexto` |
| figuras, gráficos e quadros | NBR 14724:2024 + UFC | `ufctex/objetos.def` + infraestrutura `place` |
| tabelas numéricas | NBR 14724:2024 + IBGE | `ufctex/modulos.def` + `tabularray-abnt` + `tests/v2-table-ibge-check.sh` |
| código e algoritmos | requisito tipográfico UFC + extensão editorial | `ufctex/modulos.def` + `ufctex/objetos.def` |
| equações | NBR 14724:2024 | ambiente matemático + `tests/v2-math-check.sh` |
| citações | NBR 10520:2023 | `ufctex/bibliografia.def` + `abntexto` |
| referências | NBR 6023:2025 | `ufctex/bibliografia.def` + `ufctex/compat-nbr6023-2025.def` |
| projetos | NBR 15287:2025 | `ufctex/projetos.def` |
| glossário | NBR 14724:2024 | módulo opcional |
| apêndices e anexos | NBR 14724:2024 | API pública do `abntexto` + política V2 de quebra |
| índice | NBR 6034:2004 | módulo opcional |
| PDF/A e fontes autocontidas | política institucional UFC + escolha técnica do projeto | `\DocumentMetadata` + `tests/v2-font-embedding-check.sh` + veraPDF |
| compatibilidade V1 | transição de documentos | `ufctex/compat-v1.def` |

## Compatibilidade dos pacotes

`abntexto`, `biblatex-abnt`, `tabularray-abnt` e demais pacotes são infraestrutura. A versão de um pacote não define, isoladamente, conformidade normativa da V2.

Os ajustes necessários para NBR 6023:2025 permanecem isolados em `ufctex/compat-nbr6023-2025.def` e possuem regressões próprias. O arquivo deve ser reduzido ou removido quando o suporte equivalente estiver disponível de forma estável no upstream.

## Build e gates

`make preflight` executa consistência da distribuição, documento de referência, layout, política de fontes, geometria, matemática/equações, pré-textuais, orientação CAPES, duplex, ficha catalográfica, multivolume, estruturas normativas complementares, objetos, geometria de objetos, subconjunto IBGE, código/algoritmos, `minted`, fontes documentais, bibliografia, projetos, matriz de seis perfis nos dois motores, pós-textuais, compatibilidade V1 e fluxo modular do Makefile.

A matriz final produz **12 PDFs**: seis perfis × dois motores. Cada PDF é verificado quanto a conteúdo específico, A4, fontes incorporadas (`emb=yes`), Sumário, ausência de `chapter`, warnings/overflow e declaração PDF/A-2b.

`make release-preflight` acrescenta veraPDF para o documento de referência e os 12 PDFs da matriz.

O `latex-preflight` obrigatório das branches V2 acrescenta ao gate Linux o proxy Overleaf e o Gate T Windows. O Windows produz os quatro PDFs estritos de Times New Roman/Arial em pdfLaTeX/LuaLaTeX; a certificação posterior verifica identidade literal, extração Unicode, incorporação das fontes e PDF/A-2b. O agregado só publica sucesso quando todos esses componentes obrigatórios concluem com sucesso.

## Fontes institucionais de verificação

- Sistema de Bibliotecas da UFC — Normalização de trabalhos acadêmicos: https://biblioteca.ufc.br/pt/servicos-e-produtos/normalizacao-de-trabalhos-academicos/
- Guia de Normalização de Trabalhos Acadêmicos atualmente vinculado: https://biblioteca.ufc.br/wp-content/uploads/2022/05/guianormalizacaotrabalhosacademicos-17.05.2022.pdf
- Guia de Normalização para Elaboração de Citações 2025: https://biblioteca.ufc.br/wp-content/uploads/2025/06/guianormalizacaocitacoes2025.pdf
- Guia de Normalização para Elaboração de Referências atualmente vinculado: https://biblioteca.ufc.br/wp-content/uploads/2023/12/guianormalizacaoreferencias.pdf
- Guia de Normalização de Projetos de Pesquisa atualmente vinculado: https://biblioteca.ufc.br/wp-content/uploads/2019/10/guia-de-projetos-06.10.2019.pdf
- Sistema de Bibliotecas da UFC — Normas para recebimento de teses e dissertações: https://biblioteca.ufc.br/pt/normas-sibi/normas-para-o-recebimento-de-teses-e-dissertacoes/
- Sistema de Bibliotecas da UFC — Normas para recebimento de TCC: https://biblioteca.ufc.br/pt/normas-sibi/normas-para-o-recebimento-de-tcc/
- Instrução Normativa Conjunta nº 2/2026: https://biblioteca.ufc.br/wp-content/uploads/2026/02/instrucao-normativa-conjunta-2.pdf
- Sistema de Bibliotecas da UFC — FAQ da ficha catalográfica: https://biblioteca.ufc.br/pt/perguntas-frequentes/ficha-catalografica-2/
- Sistema de Bibliotecas da UFC — Coleção de Normas Técnicas: https://biblioteca.ufc.br/pt/colecao-de-normas-tecnicas/
- CAPES — Portaria nº 206/2018 e Identidade Visual: https://www.gov.br/capes/pt-br/centrais-de-conteudo/portaria-no-206-de-4-de-setembro-de-2018.pdf
- ABNT Catálogo: https://www.abntcatalogo.com.br/

## Manutenção

Antes de nova versão principal:

1. reconfirmar as edições normativas;
2. revisar páginas e guias da UFC;
3. revisar políticas de depósito, ficha catalográfica e CAPES;
4. atualizar ou remover patches de compatibilidade;
5. resolver todas as divergências classificadas;
6. promover itens `INCOMPLETO` somente após evidência adequada;
7. executar `make preflight`;
8. executar `make release-preflight`;
9. confirmar `latex-preflight` no CI;
10. não declarar conformidade que não possua evidência compatível.
