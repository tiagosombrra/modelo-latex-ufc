# ufctex

Classe LaTeX para trabalhos acadêmicos da Universidade Federal do Ceará, baseada em `abntexto`.

Versão publicada atual: **2.1.0**.

A linha 2.x reorganiza a implementação em módulos, preserva a API pública da V1 quando possível e acompanha a base normativa vigente auditada em agosto de 2026.

## Requisitos

- TeX Live 2026 recomendado para desenvolvimento e CI;
- `abntexto` 1.1 ou superior;
- `biblatex` + `biber`;
- pacotes opcionais apenas quando os módulos correspondentes forem ativados.

O bundle específico `modelo-latex-ufc-overleaf-2.1.0.zip` inclui uma cópia íntegra e pinada de `abntexto.cls` 1.1 para manter compatibilidade com ambientes que ainda não o ofereçam. O smoke real no Overleaf, realizado em 21/08/2026, compilou com sucesso em pdfLaTeX sobre TeX Live 2026; o proxy de CI em TeX Live 2025 permanece como verificação adicional de compatibilidade.

## Estrutura

```text
ufctex.cls
ufctex/
├── core.def
├── fontes.def
├── layout.def
├── modulos.def
├── pretextuais.def
├── institucional.def
├── trabalhos.def
├── projetos.def
├── objetos.def
├── bibliografia.def
├── compat-nbr6023-2025.def
├── postextuais.def
└── compat-v1.def
```

Cada responsabilidade fica concentrada em um módulo. `compat-v1.def` é a única camada destinada à transição de APIs da linha 1.x.

## Configuração básica

Exemplo para uma tese:

```tex
\documentclass{ufctex}

\ufcsetup{
  tipo = tese,
  impressao = anverso,
  capa = auto,
  ficha-catalografica = nao,
  brasao = sim,
  fonte = times,
  fonte-estrita = nao,
  programa-doutorado = {Programa de Pós-Graduação em Ciência da Computação},
  titulo-doutor = {Ciência da Computação},
  area-doutorado = {Computação Gráfica},
  autor = {Nome Sobrenome},
  titulo = {Título do Trabalho},
  local = {Fortaleza},
  ano = {2026},
  orientador = {Prof. Dr. Nome do Orientador},
  volume = {},
  pagina-inicial = 1,
  tabelas = nativo,
  codigo = nenhum,
  algoritmos = nenhum,
  glossario = nenhum,
  indice = nenhum
}
```

## Perfis

| Perfil | Uso |
|---|---|
| `tccgraduacao` | trabalho de graduação |
| `tccespecializacao` | trabalho de especialização |
| `dissertacao` | dissertação de mestrado |
| `tese` | tese de doutorado |
| `projeto` | projeto de pesquisa identificado |
| `projetoanonimizado` | projeto de pesquisa com dados pessoais suprimidos |

A impressão pode ser `anverso` ou `frente-verso`.

## Tipografia

O Guia UFC admite **Times New Roman ou Arial**. A V2 oferece:

```tex
\ufcsetup{
  fonte = times,
  fonte-estrita = nao
}
```

Valores de `fonte`:

- `times` → Times New Roman;
- `arial` → Arial.

A chave `fonte-estrita` define a política de identidade:

- `sim`: exige a família literal solicitada e falha quando ela não está disponível;
- `nao`: permite fallback de compatibilidade para portabilidade e desenvolvimento.

Fallbacks não são apresentados como fontes literais:

- pdfLaTeX + `times`: NewTX;
- pdfLaTeX + `arial`: TeX Gyre Heros;
- LuaLaTeX + `times`: TeX Gyre Termes;
- LuaLaTeX + `arial`: TeX Gyre Heros.

No LuaLaTeX, Times New Roman e Arial literais são resolvidas pelo `fontspec`. No pdfLaTeX, o modo estrito usa o suporte local produzido por `tools/prepare-windows-fonts.ps1` a partir das fontes Microsoft já instaladas no Windows. As fontes proprietárias não são redistribuídas pelo projeto.

O PDF certificado deve ter todas as fontes efetivamente usadas incorporadas (`emb=yes`). A incorporação por subconjunto é aceita. O Gate T também valida PDF/A-2b com veraPDF.

A matemática usa uma família matemática complementar; ela não é apresentada como Times New Roman ou Arial.

## Trabalhos em mais de um volume

```tex
\ufcsetup{
  volume = {2},
  pagina-inicial = 101
}
```

`volume` é impresso na capa e na folha de rosto. `pagina-inicial` permite manter a paginação contínua entre volumes.

## Frente e verso

No modo `frente-verso`, a V2 aplica margens espelhadas:

- anverso: esquerda/superior 3 cm; direita/inferior 2 cm;
- verso: direita/superior 3 cm; esquerda/inferior 2 cm;
- paginação à direita no anverso e à esquerda no verso;
- pré-textuais, exceto ficha catalográfica, iniciam em anverso;
- seções textuais primárias e pós-textuais controlados pela V2 iniciam no anverso.

## Ficha catalográfica

O padrão da versão 2.1.0 é:

```tex
\ufcsetup{ficha-catalografica = nao}
```

Quando a ficha for aplicável:

```tex
\ufcsetup{ficha-catalografica = sim}
\imprimirfichacatalografica{caminho/para/ficha}
```

A ficha é tratada como PDF externo. Sua tipografia e conformidade PDF/A devem ser verificadas no documento final.

## Estrutura textual

A V2 usa `\section` como nível textual primário:

```tex
\section{Introdução}
\subsection{Fundamentação}
\subsubsection{Detalhamento}
```

`\chapter` não faz parte do perfil normativo V2.

## Elementos pré-textuais

```tex
\pretextual

\imprimircapa
\imprimirfolhaderosto
\imprimirerrata{1-pre-textuais/errata}
\imprimirfolhadeaprovacao
\imprimirdedicatoria{1-pre-textuais/dedicatoria}
\imprimiragradecimentos{1-pre-textuais/agradecimentos}
\imprimirepigrafe{1-pre-textuais/epigrafe}
\imprimirresumo{1-pre-textuais/resumo}
\imprimirabstract{1-pre-textuais/abstract}
\imprimirlistadeilustracoes
\imprimirlistadetabelas
\imprimirlistadecodigos
\imprimirlistadealgoritmos
\imprimirlistadeabreviaturasesiglas{1-pre-textuais/lista-de-abreviaturas-e-siglas}
\imprimirlistadesimbolos{1-pre-textuais/lista-de-simbolos}
\imprimirsumario
```

A folha de aprovação gerada pela classe não incorpora imagens de assinatura. O resumo e o abstract distribuídos permanecem na faixa de 150 a 500 palavras.

Quando o trabalho decorrer de atividade financiada total ou parcialmente pela CAPES, consulte a orientação em `1-pre-textuais/agradecimentos.tex`.

## Figuras, gráficos e quadros

A API principal usa a infraestrutura de objetos do `abntexto`:

```tex
\legend{figure}{Título da figura}
\ufcfonte{Elaboração própria.}
\ufcnota{Nota opcional.}
\label{fig:exemplo}
\begin{ufcobjeto}[here]
  \centering
  \includegraphics[width=.8\linewidth]{figuras/exemplo}
\end{ufcobjeto}
```

O primeiro argumento de `\legend` pode ser `figure`, `grafico`, `quadro`, `codigo` ou `algoritmo`, conforme o objeto. Título, Fonte e Nota são limitados à largura física do objeto e usam o tamanho reduzido definido pelo perfil.

A Lista de Ilustrações agrega figuras, gráficos e quadros. Tabelas permanecem em lista própria.

## Tabelas

Para tabelas numéricas com `tabularray-abnt`:

```tex
\ufcsetup{tabelas = tabularray}
```

Exemplo com linhas alternadas opcionais:

```tex
\begin{tallabnttblr}
[
  caption={Indicadores},
  label={tab:indicadores},
  remark{Fonte}={Elaboração própria.},
  remark{Nota}={Valores sintéticos.},
]
{
  colspec={XX[r]},
  row{even}={bg=black!5},
}
\toprule
Item & Valor \\
\midrule
A & 10 \\
B & 12 \\
\bottomrule
\end{tallabnttblr}
```

O corpo permanece em tamanho 12. Legenda, Fonte e Nota usam tamanho reduzido. A alternância de linhas é editorial e não é aplicada automaticamente.

## Código-fonte

Ative um único módulo:

```tex
\ufcsetup{codigo = listings}
```

ou:

```tex
\ufcsetup{codigo = minted}
```

Com `listings`, linguagem e números de linha continuam configuráveis pelo próprio pacote:

```tex
\lstset{language=Python,numbers=left}

\legend{codigo}{Função em Python com números de linha}
\ufcfonte{Elaboração própria.}
\begin{ufclisting}[here]
def dobro(valor):
    return 2 * valor
\end{ufclisting}
```

Para remover a numeração:

```tex
\lstset{numbers=none}
```

O documento de referência da V2 exerce C++, Python e Java, com diferentes políticas de números de linha. O fluxo `minted` permanece em fixture própria porque exige o toolchain externo correspondente.

## Algoritmos

```tex
\ufcsetup{algoritmos = algpseudocodex}
```

Com números de linha:

```tex
\legend{algoritmo}{Busca linear}
\ufcfonte{Elaboração própria.}
\begin{ufcalgoritmo}[here][1]
  \State $i \gets 1$
  \State \Return $i$
\end{ufcalgoritmo}
```

Sem números de linha:

```tex
\legend{algoritmo}{Busca linear sem numeração}
\ufcfonte{Elaboração própria.}
\begin{ufcalgoritmo}[here][0]
  \State $i \gets 1$
  \State \Return $i$
\end{ufcalgoritmo}
```

O segundo argumento opcional controla a frequência de numeração do `algorithmic`: `1` numera cada linha e `0` suprime os números.

## Glossário e índice

```tex
\ufcsetup{
  glossario = glossaries,
  indice = imakeidx
}
```

A V2 cria glossário e índice somente quando os módulos são ativados.

## Referências

```tex
\ufcbibliografia{3-pos-textuais/referencias.bib}
```

A bibliografia usa `biblatex-abnt` e `biber`. Ajustes necessários ao escopo testado da NBR 6023:2025 ficam isolados em `ufctex/compat-nbr6023-2025.def`.

## Apêndices e anexos

```tex
\appendix{Instrumento elaborado pelo autor}
\input{3-pos-textuais/apendices/apendice-a}

\annex{Documento externo}
\input{3-pos-textuais/anexos/anexo-a}
```

O documento de referência compila todos os quatro apêndices e os dois anexos distribuídos.

## PDF/A

O documento de referência usa:

```tex
\DocumentMetadata{
  lang = pt-BR,
  pdfstandard = A-2b,
  pdfversion = 1.7
}
```

PDF/A-2b é uma escolha técnica verificável do projeto, não uma exigência específica atribuída à UFC.

## Build

Compilação padrão:

```bash
make compile
```

LuaLaTeX:

```bash
make compile ENGINE=lualatex
```

Limpeza:

```bash
make clean
```

Auditoria integral do repositório:

```bash
make v2-repository-audit
```

Validação do documento/corpus de referência:

```bash
make v2-reference-corpus-check
```

Preflight completo:

```bash
make preflight
```

Preflight de release com PDF/A:

```bash
make release-preflight
```

Geração dos bundles:

```bash
make package
```

Preflight automatizado de distribuição:

```bash
make distribution-preflight
```

`distribution-preflight` cobre a parte automatizada do Gate D. O processo final também inclui smoke real no Overleaf, revisão dos metadados e publicação da tag imutável/GitHub Release. A submissão ao CTAN permanece uma etapa separada.

## Corpus de referência e auditoria

A versão 2.1.0 transforma `documento.tex` em um corpus visual e semântico de regressão. Ele compila, entre outros casos:

- errata e demais pré-textuais;
- figuras estreita, intermediária e larga;
- gráfico e quadros;
- tabela nativa e `tabularray-abnt` com zebra opcional;
- C++, Python e Java com diferentes políticas de números de linha;
- algoritmos com e sem numeração;
- equação e citação longa;
- trabalhos relacionados;
- referências, glossário e índice;
- quatro apêndices e dois anexos.

Casos incompatíveis entre si ou dependentes do ambiente continuam em fixtures dedicadas: `minted`, fontes Microsoft literais, duplex, ficha catalográfica externa e matriz de perfis.

`tests/v2-repository-audit.py` percorre todos os arquivos rastreados pelo Git e bloqueia, entre outros problemas, resíduos V1 fora da camada de compatibilidade, chaves públicas inexistentes em exemplos, caminhos absolutos, artefatos gerados versionados e divergências de versão.

O histórico da auditoria da V2 está em `docs/AUDITORIA-V2.md`.

## Distribuição

A versão 2.1.0 produz:

- `ufctex-2.1.0.zip`: classe, módulos, ativos necessários, licença e documentação;
- `modelo-latex-ufc-2.1.0.zip`: template completo para uso local;
- `modelo-latex-ufc-overleaf-2.1.0.zip`: template para Overleaf com `abntexto` 1.1 pinado;
- `ufctex-ctan-2.1.0.zip`: candidato CTAN com arquivo TDS interno;
- `ufctex-2.1.0-reference.pdf`: documento de referência;
- `SHA256SUMS`: hashes SHA-256 dos artefatos.

As fontes Microsoft não são incluídas. O brasão da UFC é um ativo institucional oficial e não deve ser interpretado como coberto automaticamente pela LPPL da classe. Sua classificação para redistribuição deve ser confirmada antes de uma submissão ao CTAN.

## CI

O workflow principal é `.github/workflows/latex-preflight.yml`. O Gate T obrigatório cobre o documento de referência, a matriz de perfis, PDF/A, fontes incorporadas, Times New Roman/Arial literais no Windows e o proxy Overleaf.

A Fase 4 acrescenta `.github/workflows/reference-validation.yml` e o status `ufctex/reference-audit`, responsável pela auditoria integral e pelo corpus de referência.

O workflow `.github/workflows/distribution.yml` exige o Gate T do mesmo SHA, executa o release preflight, gera/verifica os bundles, testa o ZIP de Overleaf no proxy TeX Live 2025 e publica `ufctex/distribution-preflight`.

## Compatibilidade V1

A V2 não replica internamente a arquitetura 1.x. `ufctex/compat-v1.def` existe apenas para reduzir o custo de migração de documentos antigos. Resíduos estruturais da V1 não são permitidos nos demais módulos.

## Licença

Consulte `LICENSE`.
