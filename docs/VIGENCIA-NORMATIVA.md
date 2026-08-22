# Política de vigência normativa

Última revisão: **2026-08-22**.

## Regra mandatória

O UFCtex deve seguir a **edição vigente mais recente da norma técnica aplicável**. Uma edição ABNT substituída não pode governar uma regra ativa apenas porque ainda aparece citada em um Guia de Normalização da UFC.

Esta decisão não é uma preferência editorial do projeto. Ela decorre de duas fontes institucionais da própria UFC:

1. a **Resolução nº 17/CEPE, de 02 de outubro de 2017**, cujo art. 1º determina que a normalização dos trabalhos acadêmicos da UFC seja realizada de acordo com as normas técnicas de informação e documentação da ABNT, ressalvados modelos específicos formalmente aprovados no âmbito previsto pela resolução;
2. a página vigente **Normalização de trabalhos acadêmicos — Sistema de Bibliotecas UFC**, atualizada em 04/03/2026, que declara que os Guias de Normalização da UFC estão de acordo com as **normas vigentes** da ABNT.

Fontes institucionais:

- Resolução nº 17/CEPE: https://ufc.br/images/_files/a_universidade/cepe/resolucao_cepe_2017/resolucao17_cepe_2017.pdf
- Página de Normalização do SiBi/UFC: https://biblioteca.ufc.br/pt/servicos-e-produtos/normalizacao-de-trabalhos-academicos/
- Relação oficial das Resoluções CEPE de 2017: https://www.ufc.br/a-universidade/documentos-oficiais/9285-resolucoes-do-conselho-de-ensino-pesquisa-e-extensao-cepe-2017

## Regra de decisão

Para requisito técnico:

**norma ABNT vigente → requisito UFC compatível/complementar → guia UFC → implementação**.

Para requisito institucional:

**ato UFC vigente → requisito institucional UFC vigente → guia UFC → norma técnica, quando aplicável → implementação**.

Um guia UFC que contenha uma citação técnica antiga continua podendo fornecer orientação institucional compatível, mas **não reativa** a edição ABNT substituída.

Se duas fontes atuais e aplicáveis forem realmente incompatíveis, o requisito recebe `review-required`; o projeto não escolhe silenciosamente uma delas.

A única exceção à regra técnica geral é um modelo específico de curso formalmente aprovado nos termos da Resolução nº 17/CEPE. Esse modelo deve ser cadastrado como fonte institucional vigente, com escopo explícito, antes de alterar o comportamento do template.

## Mapeamento explícito de edições citadas pela UFC

As referências antigas abaixo são mantidas nesta documentação **apenas para explicar a divergência de vigência**. Elas não pertencem à base técnica ativa.

| Documento UFC | Edição ainda citada | Edição técnica adotada pelo UFCtex | Decisão |
|---|---|---|---|
| Guia de Trabalhos Acadêmicos, 2022 | ABNT NBR 14724:2011 | **ABNT NBR 14724:2024** (versão corrigida em 01/04/2025) | usa a edição vigente |
| Guia de Trabalhos Acadêmicos, 2022 | ABNT NBR 6023:2018 | **ABNT NBR 6023:2025** | usa a edição vigente |
| Guia de Trabalhos Acadêmicos, 2022 | ABNT NBR 10520:2002 | **ABNT NBR 10520:2023** | usa a edição vigente |
| Guia de Trabalhos Acadêmicos, 2022 | ABNT NBR 12225:2004 | **ABNT NBR 12225:2023** | usa a edição vigente |
| Guia de Citações, 2025 | ABNT NBR 6023:2018 | **ABNT NBR 6023:2025** | a NBR 10520:2023 do próprio guia continua vigente; somente a referência à 6023 foi substituída |
| Guia de Referências, 2023 | ABNT NBR 6023:2018 | **ABNT NBR 6023:2025** | usa a edição vigente |
| Guia de Projetos de Pesquisa, 2019 | ABNT NBR 15287:2011 | **ABNT NBR 15287:2025** | usa a edição vigente |
| Guia de Projetos de Pesquisa, 2019 | ABNT NBR 6023:2018 | **ABNT NBR 6023:2025** | usa a edição vigente |
| Guia de Projetos de Pesquisa, 2019 | ABNT NBR 10520:2002 | **ABNT NBR 10520:2023** | usa a edição vigente |
| Guia de Projetos de Pesquisa, 2019 | ABNT NBR 12225:2004 | **ABNT NBR 12225:2023** | usa a edição vigente |

As normas que continuam atuais, mesmo que tenham ano antigo, permanecem ativas. O critério é **vigência**, não o número do ano.

## Normas técnicas vigentes atualmente adotadas

| Assunto | Norma |
|---|---|
| Trabalhos acadêmicos | ABNT NBR 14724:2024, versão corrigida em 01/04/2025 |
| Citações | ABNT NBR 10520:2023 |
| Referências | ABNT NBR 6023:2025 |
| Projetos de pesquisa | ABNT NBR 15287:2025 |
| Resumo, resenha e recensão | ABNT NBR 6028:2021 |
| Numeração progressiva de seções | ABNT NBR 6024:2012 |
| Sumário | ABNT NBR 6027:2012 |
| Índice | ABNT NBR 6034:2004 |
| Lombada | ABNT NBR 12225:2023 |
| Tabelas numéricas | Normas de apresentação tabular do IBGE, 3. ed., 1993, quando aplicável |

## Como uma atualização futura é tratada

Quando uma nova edição técnica for identificada:

1. a nova edição não altera automaticamente valores no template;
2. a fonte é marcada para revisão;
3. os requisitos afetados são confrontados com a nova edição;
4. regras alteradas são atualizadas e retestadas;
5. a edição substituída é removida da base técnica ativa;
6. se um guia UFC ainda citar a edição antiga, a divergência é acrescentada a este mapa;
7. CI, CLI, Web e documentação devem convergir para a mesma decisão.

O arquivo máquina-legível correspondente é `normativa/version-policy.json`. O gate `tests/checks/normative_currency.py` impede que uma edição mapeada como substituída volte a governar arquivos normativos ativos.
