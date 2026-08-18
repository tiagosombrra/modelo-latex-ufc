# Modelo de Trabalho Acadêmico UFC em LaTeX

Template LaTeX comunitário e modernizado para elaboração de trabalhos acadêmicos na Universidade Federal do Ceará (UFC).

**Versão comunitária atual: 1.1.2 — 18/08/2026**

> [!IMPORTANT]
> Este é um projeto comunitário e não oficial. A conformidade deve ser conferida com os guias vigentes do Sistema de Bibliotecas da UFC e com as regras específicas do curso, programa, processo seletivo ou edital aplicável.

A página de normalização do SiBi-UFC informa que os Guias de Normalização da UFC reúnem os requisitos institucionais adotados para trabalhos acadêmicos e estão de acordo com as normas ABNT vigentes. O modelo LaTeX/Overleaf disponibilizado pela Biblioteca aparece atualmente como **“Em atualização”**. Por isso, este repositório deve ser tratado como uma atualização comunitária do template histórico, não como um modelo oficialmente homologado pela Biblioteca.

## Uso rápido

1. Clique em **Use this template** no GitHub ou importe o projeto no Overleaf.
2. Edite `documento.tex`.
3. Configure o trabalho em `\ufcsetup{...}`.
4. Ajuste os elementos pré-textuais e capítulos conforme sua modalidade.
5. Compile no Overleaf ou localmente com `make`.
6. Antes da entrega, execute `make preflight` quando estiver em ambiente local compatível.

## Modalidades suportadas

- `tccgraduacao`: TCC de graduação;
- `tccespecializacao`: TCC/monografia de especialização;
- `dissertacao`: dissertação de mestrado;
- `tese`: tese de doutorado;
- `projeto`: projeto de pesquisa identificado;
- `projetoanonimizado`: projeto de pesquisa sem identificação pessoal, quando exigido pelo regulamento ou edital.

`projetocego` permanece apenas como alias legado e emite aviso de depreciação.

## Precedência normativa

A ordem de decisão adotada pelo template é:

1. regra específica do curso, programa, edital ou processo seletivo;
2. orientação institucional mais específica e mais recente da UFC para o assunto;
3. Guias de Normalização da UFC;
4. convenções tipográficas do template quando a UFC não fixa um valor numérico ou uma implementação específica.

O template auxilia a composição; ele não substitui a conferência final das normas aplicáveis ao documento.

## O que mudou na v1.1.2

A v1.1.2 é uma release de manutenção da linha `abntex2`/`memoir` antes da futura migração de plataforma.

- opção pública de idioma atualizada de `brazil` para `brazilian`;
- correção do espaçamento duplicado antes de `Fonte`/`Nota`, preservando o afastamento já fornecido pela composição do objeto;
- preflight automatizado em GitHub Actions com TeX Live 2026;
- `make preflight` passa a reconhecer explicitamente duas depreciações upstream inevitáveis do `abntex2` 1.9.7, sem liberar outros warnings;
- versão do template atualizada nos arquivos principais e no `Makefile`.

A correção de espaçamento remove afastamento vertical redundante e pode alterar a paginação de documentos que estejam no limite de uma página, sem modificar seu conteúdo textual.

### v1.1.1

A v1.1.1 consolidou a documentação e os metadados da política introduzida na v1.1.0, preservando a retrocompatibilidade e a base `abntex2`/`memoir`.

### v1.1.0

A v1.1.0 introduziu uma política uniforme para identificação, objeto e fonte/nota em figuras, tabelas, quadros e demais objetos legendados.

## Política de figuras, tabelas, quadros e outros objetos

Os guias UFC determinam, para ilustrações e tabelas, identificação acima do objeto, fonte abaixo, tipografia reduzida e espaçamento simples nos elementos de identificação/fonte. Os guias consultados não fixam uma distância vertical numérica entre identificação, objeto e fonte.

O template adota, portanto, a seguinte convenção tipográfica uniforme:

```text
Identificação — Título
        ↓ 6 pt
      OBJETO
        ↓ 6 pt
Fonte: ...
```

Os **6 pt não são uma exigência numérica da UFC**. São uma decisão tipográfica do template para impedir que o título fique visualmente colado ao objeto e para manter consistência entre tipos de elementos.

A implementação centraliza os valores em:

```tex
\UFCCaptionObjectSep
\UFCObjectSourceSep
```

ambos configurados em `6pt` por padrão.

Essa política é aplicada a:

| Objeto | Tratamento do template |
|---|---|
| Figuras, gráficos, diagramas e fluxogramas | identificação acima, 6 pt, objeto, 6 pt, fonte/nota |
| Tabelas | mesma política, respeitando a apresentação tabular aplicável |
| Quadros | tratados como ilustrações com helper próprio |
| Subfiguras/subtabelas | fonte reduzida e espaço simples, com separação consistente |
| `longabnttblr` / `talltblr` | separadores internos alinhados à política de 6 pt |
| `algorithm` / `algpseudocodex` | mesma convenção visual por consistência |
| `algorithm2e` | normalização explícita do mecanismo próprio de caption |
| `listings` | caption acima e separação consistente do código |

Algoritmos e códigos-fonte não possuem, nos guias UFC consultados, uma regra específica equivalente à de ilustrações e tabelas; nesses casos, o template estende a mesma convenção visual para manter consistência editorial.

Não é necessário inserir `\vspace` manualmente em cada figura ou tabela. Ajustes locais devem ser evitados, salvo quando um caso excepcional exigir tratamento específico.

## Arquitetura

A classe-base continua sendo `abntex2`, baseada em `memoir`. A modernização ocorre ao redor dessa base para preservar a camada institucional e a retrocompatibilidade.

```text
documento.tex
    |
    +-- \ufcsetup{...}              configuração pública
    |
    +-- lib/preambulo.tex           infraestrutura LaTeX
    |       +-- engines/tipografia
    |       +-- matemática/unidades
    |       +-- captions/objetos
    |       +-- tabelas
    |       +-- bibliografia
    |       +-- referências cruzadas
    |
    +-- lib/ufctex.sty              regras UFC + compatibilidade
            +-- LaTeX3/l3keys
            +-- modalidades
            +-- anonimização
            +-- módulos opcionais
            +-- wrappers legados
```

A interface recomendada para documentos novos é `\ufcsetup{...}`. Os comandos históricos (`\trabalhoacademico`, `\ies`, `\centro`, `\autor`, `\titulo`, etc.) continuam disponíveis.

## Exemplo de configuração

```tex
\ufcsetup{
    tipo = tese,
    ies = {Universidade Federal do Ceará},
    sigla = {UFC},
    centro = {Centro, Faculdade, Instituto ou Campus},
    departamento = {Departamento ou Unidade Acadêmica},

    programa-doutorado = {Nome do Programa},
    nome-doutorado = {Nome do Doutorado},
    titulo-doutor = {Área do título},
    area-doutorado = {Área de Concentração},

    autor = {Nome Sobrenome},
    titulo = {Título do Trabalho},
    local = {Fortaleza},
    ano = {2026},

    orientador = {Prof. Dr. Nome do Orientador},
    ficha-catalografica = nao,
    links = discretos,

    algoritmos = nenhum,
    codigo = listings,
    graficos = nao,
    caixas = nao,
    teoremas = basico
}
```

## Núcleo LaTeX modernizado

| Área | Infraestrutura | Observação |
|---|---|---|
| Classe | `abntex2` / `memoir` | preservada por compatibilidade |
| Configuração | LaTeX3 / `l3keys` | usada por `\ufcsetup` |
| Bibliografia | `biblatex` + estilo `abnt` + Biber | substitui `abntex2cite` |
| Glossários/siglas | `glossaries-extra` | mantém a API tradicional |
| Matemática | `mathtools` | extensão de `amsmath` |
| pdfLaTeX | `newtxtext` / `newtxmath` | caminho padrão |
| Lua/XeLaTeX | `fontspec` + `unicode-math` | fluxo Unicode/OpenType |
| Unidades | `siunitx` | configuração compatível com vírgula decimal |
| Microtipografia | `microtype` | habilitada |
| Figuras | `graphicx`, `adjustbox`, `subcaption` | imagens e subfiguras |
| Tabelas | `tabularray-abnt`, `booktabs`, `siunitx` | padrão recomendado para tabelas novas |
| Tabelas legadas | `array`, `tabularx`, `longtable` | retrocompatibilidade |
| Referências cruzadas | `cleveref` | API mantida |
| Código-fonte | `listings` | padrão portátil; `minted` é opcional |

## Figuras

```tex
\begin{figure}[htbp]
    \centering
    \UFCfig{
        \Caption{\label{fig:exemplo} Título da figura}
    }{
        \UFCincludegraphics[width=.8\linewidth]{figura-2}
    }{
        \Fonte{Elaboração própria.}
    }
\end{figure}
```

`\UFCincludegraphics` limita a imagem à área útil e preserva a proporção.

## Tabelas e quadros

Para conteúdo novo, prefira `tabularray-abnt` quando adequado.

```tex
\begin{table}[htbp]
    \centering
    \UFCtab{
        \Caption{\label{tab:exemplo} Resultados por configuração}
    }{
        \begin{abnttblr}[]{
            colspec = {lcc},
            row{1} = {font=\bfseries},
            hline{1,Z} = {1pt},
            hline{2} = {0.6pt}
        }
            Configuração & Métrica A & Métrica B \\
            Base         & 7,5       & 8,1       \\
            Método       & 8,7       & 9,0
        \end{abnttblr}
    }{
        \Fonte{Elaboração própria.}
    }
\end{table}
```

Os helpers `\UFCfig`, `\UFCtab` e `\UFCqua` mantêm identificação, objeto e fonte/nota sob uma largura lógica comum.

## Algoritmos

Para conteúdo novo:

```tex
algoritmos = algpseudocodex
```

`algorithm2e` permanece disponível para documentos legados:

```tex
algoritmos = algorithm2e
```

A nomenclatura e o espaçamento são configurados pelo módulo escolhido.

## Código-fonte

Padrão portátil:

```tex
codigo = listings
```

Opcional:

```tex
codigo = minted
```

`minted` exige suporte a Pygments no ambiente de compilação.

## Gráficos, caixas e teoremas

```tex
graficos = sim
caixas = sim
teoremas = avancado
```

Essas opções carregam, respectivamente, a pilha TikZ/PGFPlots, `tcolorbox` e `thmtools`. Permanecem desligadas por padrão.

## Citações e referências

O backend é Biber com estilo ABNT do ecossistema BibLaTeX.

Prefira:

```tex
\textcite{chave}
\parencite{chave}
```

Compatibilidade histórica:

```tex
\cite{chave}
\citeonline{chave}
```

Casos bibliográficos incomuns devem ser conferidos visualmente contra o guia institucional vigente.

## Projeto anonimizado

```tex
tipo = projetoanonimizado
```

Nesse modo, o template remove identificação de autoria/orientação das partes pré-textuais configuradas para projeto e deixa o campo `Author` dos metadados PDF vazio. O template não decide quais outros identificadores são permitidos; isso depende do edital ou regulamento aplicável.

## Ficha catalográfica e PDF/A

A ficha catalográfica visual permanece disponível por compatibilidade e fica desativada por padrão:

```tex
ficha-catalografica = nao
```

A geração do PDF pelo template não implica, por si só, conformidade PDF/A. Para depósito institucional, valide o arquivo conforme o fluxo vigente da UFC; as normas atuais de recebimento de teses e dissertações exigem entrega eletrônica em PDF/A.

## Compilação

No Overleaf, mantenha `documento.tex` na raiz do projeto.

Localmente:

```bash
make
```

Fluxo:

```text
engine -> Biber -> makeglossaries -> makeindex -> engine -> engine
```

Outros comandos:

```bash
make version
make lua
make preflight
make clean
```

`make preflight` reprova warnings LaTeX/pacote/classe e caixas `Overfull`/`Underfull` no log final, além de verificar incorporação de fontes quando `pdffonts` estiver disponível. Na série 1.x, duas depreciações upstream do `abntex2` 1.9.7 são filtradas de forma exata: o uso interno do nome Babel `brazil` e o uso de `memoir/\settocpreprocessor`. Outros warnings continuam reprovando o preflight.

## Compatibilidade com Overleaf

O fluxo principal permanece pdfLaTeX por ser o caminho mais conservador para o template histórico. LuaLaTeX também é suportado. A versão do TeX Live de projetos antigos pode ser diferente da versão corrente do Overleaf e deve ser conferida quando houver divergência de compilação.

O filtro via `silence` é restrito ao warning conhecido do `microtype`/kernel referente a `\showhyphens`; as duas exceções upstream da série 1.x são tratadas apenas pelo `make preflight`.

## Retrocompatibilidade

Foram mantidos deliberadamente:

- `\trabalhoacademico{...}` e os campos históricos;
- alias `projetocego`, com aviso de depreciação;
- `algorithm2e` para documentos antigos;
- `tabularx` e `longtable`;
- ficha catalográfica e comandos pré-textuais históricos;
- ambientes legados de teorema e código.

A estratégia é modernizar a implementação sem obrigar usuários antigos a reescrever seus documentos.

## Decisões adiadas

### Migração de `abntex2` para `abntexto`

Não foi feita nesta série 1.x. Trata-se de uma mudança de plataforma e deve ser avaliada como versão maior, com regressão normativa e visual em todas as modalidades.

### Tagged PDF / PDF-UA

O template não ativa tagging experimental por padrão. A prioridade atual é estabilidade, conformidade editorial e compatibilidade com o ecossistema usado pela UFC/Overleaf.

## Limitações

- programas e editais podem impor regras próprias;
- anonimização varia entre processos seletivos;
- referências automáticas devem ser revisadas em casos incomuns;
- módulos opcionais podem aumentar custo ou requisitos de compilação;
- o template não substitui validação institucional de PDF/A;
- em caso de conflito, prevalecem as normas e regras específicas vigentes.

## Versões recentes

- **1.1.2 — 18/08/2026:** compatibilidade com Babel atual, correção de espaçamento duplicado e preflight automatizado em TeX Live 2026;
- **1.1.1 — 17/08/2026:** documentação, metadados de versão e alinhamento da política de objetos;
- **1.1.0 — 17/08/2026:** normalização uniforme de espaçamento para objetos acadêmicos;
- **1.0.0 — 16/08/2026:** primeira versão pública modernizada do repositório.

## Créditos e licença

A modernização preserva a autoria, os créditos e a história do template UFC/abnTeX2 original, registrados também em `lib/ufctex.sty` e no histórico Git.

Atualização normativa e técnica da série modernizada: **Tiago Guimarães Sombra (2026)**.

O repositório é distribuído sob a **LaTeX Project Public License (LPPL) 1.3c**, conforme o arquivo `LICENSE`.

## Referências institucionais

- Normalização de trabalhos acadêmicos — Sistema de Bibliotecas da UFC: `https://biblioteca.ufc.br/pt/servicos-e-produtos/normalizacao-de-trabalhos-academicos/`
- Templates — Sistema de Bibliotecas da UFC: `https://biblioteca.ufc.br/pt/servicos-e-produtos/templates/`
- Normas para recebimento de teses e dissertações: `https://biblioteca.ufc.br/pt/normas-sibi/normas-para-o-recebimento-de-teses-e-dissertacoes/`

O histórico detalhado das versões antigas do template permanece disponível no histórico Git e nos comentários preservados da base original.