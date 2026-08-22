########################################################################
## Modelo de Trabalho Acadêmico UFC / ufctex V2                        ##
## Revisão normativa e técnica: Tiago Guimarães Sombra (2026).         ##
########################################################################

VERSION := 2.1.0
filename ?= documento
ENGINE ?= pdflatex
LATEXFLAGS := -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all pdf compile lua version clean reference-assets \
	check release-check preflight release-preflight package distribution-preflight \
	v2-repository-audit v2-reference-check v2-reference-corpus-check v2-pdfa-check \
	v2-check v2-distribution-check v2-release-package-check \
	v2-layout-check v2-font-config-check v2-pdf-geometry-check v2-math-check v2-normative-complement-check \
	v2-pretextual-check v2-duplex-pretextual-check \
	v2-object-check v2-object-geometry-check v2-code-typography-check v2-table-ibge-check v2-minted-check \
	v2-algorithm-numbering-check v2-pdf-validator-check v2-documentary-source-check v2-bib-check v2-overleaf-stable-check \
	v2-project-check v2-profile-check v2-profile-pdfa-check \
	v2-posttextual-compat-check v2-duplex-posttextual-check \
	v2-build-check v2-multivolume-check v2-catalog-card-check

all: compile
pdf: compile

version:
	@echo "$(VERSION)"

reference-assets:
	@python3 tools/fetch-reference-images.py

compile:
	@echo "Compilando $(filename).tex com $(ENGINE)..."
	$(ENGINE) $(LATEXFLAGS) $(filename).tex
	@if [ -s "$(filename).bcf" ] && grep -q '<bcf:datasource' "$(filename).bcf"; then \
		echo "Executando Biber..."; \
		biber "$(filename)"; \
	else \
		echo "Biber não necessário."; \
	fi
	@if [ -s "$(filename).glo" ]; then \
		echo "Processando glossário..."; \
		makeglossaries "$(filename)"; \
	else \
		echo "Glossário não necessário."; \
	fi
	@if [ -s "$(filename).idx" ]; then \
		echo "Processando índice..."; \
		makeindex "$(filename)"; \
	else \
		echo "Índice não necessário."; \
	fi
	$(ENGINE) $(LATEXFLAGS) $(filename).tex
	$(ENGINE) $(LATEXFLAGS) $(filename).tex
	@echo "Processo finalizado com sucesso."

lua:
	$(MAKE) clean
	$(MAKE) ENGINE=lualatex compile

check:
	@python3 tests/run.py --mode pr

release-check:
	@python3 tests/run.py --mode release

v2-repository-audit:
	@python3 tests/v2-repository-audit.py

v2-reference-check:
	@sh tests/v2-reference-check.sh

v2-reference-corpus-check: v2-reference-check
	@sh tests/v2-reference-corpus-check.sh

v2-pdfa-check: v2-reference-check
	@sh tests/v2-pdfa-check.sh

v2-distribution-check:
	@sh tests/v2-distribution-check.sh

v2-release-package-check: release-preflight
	@python3 tests/v2-release-package-check.py

v2-layout-check:
	@sh tests/v2-layout-check.sh

v2-font-config-check:
	@sh tests/v2-font-config-check.sh

v2-pdf-geometry-check:
	@sh tests/v2-pdf-geometry-check.sh

v2-math-check:
	@sh tests/v2-math-check.sh

v2-normative-complement-check: v2-math-check
	@sh tests/v2-normative-complement-check.sh

v2-pretextual-check:
	@sh tests/v2-pretextual-check.sh

v2-duplex-pretextual-check:
	@sh tests/v2-duplex-pretextual-check.sh

v2-object-geometry-check:
	@sh tests/v2-object-geometry-check.sh

v2-code-typography-check:
	@sh tests/v2-code-typography-check.sh

v2-table-ibge-check:
	@sh tests/v2-table-ibge-check.sh

v2-object-check: v2-object-geometry-check v2-code-typography-check v2-table-ibge-check
	@sh tests/v2-object-check.sh

v2-minted-check:
	@sh tests/v2-minted-check.sh

v2-algorithm-numbering-check:
	@sh tests/v2-algorithm-numbering-check.sh

v2-pdf-validator-check: v2-reference-check
	@sh tests/v2-pdf-validator-check.sh documento.pdf

v2-documentary-source-check:
	@sh tests/v2-documentary-source-check.sh

v2-bib-check: v2-documentary-source-check
	@sh tests/v2-bibliography-check.sh
	@sh tests/v2-reference-spacing-check.sh

v2-overleaf-stable-check:
	@sh tests/v2-overleaf-stable-check.sh

v2-project-check:
	@sh tests/v2-project-check.sh

v2-profile-check:
	@sh tests/v2-profile-matrix-check.sh

v2-profile-pdfa-check: v2-profile-check
	@sh tests/v2-profile-pdfa-check.sh

v2-posttextual-compat-check:
	@sh tests/v2-posttextual-compat-check.sh

v2-duplex-posttextual-check:
	@sh tests/v2-duplex-posttextual-check.sh

v2-build-check:
	@sh tests/v2-build-path-check.sh

v2-multivolume-check:
	@sh tests/v2-multivolume-check.sh

v2-catalog-card-check:
	@sh tests/v2-catalog-card-check.sh

v2-check: \
	v2-repository-audit \
	v2-distribution-check \
	v2-layout-check \
	v2-font-config-check \
	v2-pdf-geometry-check \
	v2-normative-complement-check \
	v2-pretextual-check \
	v2-duplex-pretextual-check \
	v2-object-check \
	v2-minted-check \
	v2-algorithm-numbering-check \
	v2-bib-check \
	v2-project-check \
	v2-profile-check \
	v2-posttextual-compat-check \
	v2-duplex-posttextual-check \
	v2-build-check \
	v2-multivolume-check \
	v2-catalog-card-check
	@echo "Gate local isolado da V2 concluído."

preflight: check
	@echo "Preflight completo da V2 concluído."

release-preflight: release-check
	@echo "Preflight de release da V2 concluído."

package: reference-assets
	@$(MAKE) release-preflight
	@python3 tools/fetch-abntexto.py --output .ufctex-abntexto.cls
	@python3 tools/build-release-bundles.py --abntexto .ufctex-abntexto.cls
	@rm -f .ufctex-abntexto.cls
	@echo "Bundles de distribuição da V2 concluídos."

distribution-preflight: package
	@python3 tests/v2-release-package-check.py
	@echo "Preflight automatizado de distribuição concluído."

clean:
	@echo "Limpando arquivos auxiliares..."
	@rm -f *.out *.aux *.alg *.acr *.dvi *.gls *.log *.bbl *.blg *.bcf *.run.xml
	@rm -f *.ntn *.not *.lof *.loi *.lot *.toc *.loa *.loc *.logr *.lsg *.nlo *.nls *.ilg *.ind
	@rm -f *.glg *.glo *.xdy *.acn *.idx *.loq *.lol *.fls *.fdb_latexmk *.synctex.gz *~
	@rm -f layout-anverso.pdf layout-frente-verso.pdf geometria-*.pdf normativa-complementar-*.pdf
	@rm -f font-config-*.pdf font-config-*.aux font-config-*.log font-config-*.out ufctex-font-config.tex
	@rm -f matematica-*.pdf matematica-*.aux matematica-*.log matematica-*.out ufctex-matematica.tex
	@rm -f objeto-geometria-*.pdf objeto-geometria-*.aux objeto-geometria-*.log objeto-geometria-*.out
	@rm -f tabela-ibge-*.pdf tabela-ibge-*.aux tabela-ibge-*.log tabela-ibge-*.out tabela-ibge-*.lot
	@rm -f tipografia-codigo-*.pdf tipografia-codigo-*.aux tipografia-codigo-*.log tipografia-codigo-*.out
	@rm -f tipografia-codigo-*.loa tipografia-codigo-*.loc ufctex-code-typography.tex
	@rm -f algoritmo-linhas-*.pdf algoritmo-linhas-*.aux algoritmo-linhas-*.log algoritmo-linhas-*.out algoritmo-linhas-*.loa
	@rm -f fontes-documentais-*.pdf fontes-documentais-*.aux fontes-documentais-*.bbl fontes-documentais-*.bcf
	@rm -f fontes-documentais-*.blg fontes-documentais-*.log fontes-documentais-*.out fontes-documentais-*.run.xml
	@rm -f pretextuais-trabalho.pdf pretextuais-projeto-anonimo.pdf pretextuais-duplex-*.pdf
	@rm -f objetos-avancados.pdf objetos-minted.pdf citacoes-referencias.pdf
	@rm -f referencias-6023-2025.pdf projeto-15287.pdf projeto-sem-capa.pdf
	@rm -f postextuais*.pdf multivolume-*.pdf ficha-catalografica-*.pdf
	@rm -f perfil-*.pdf perfil-*.aux perfil-*.log perfil-*.out perfil-*.toc
	@rm -f perfil-*.bbl perfil-*.bcf perfil-*.blg perfil-*.run.xml perfil-*.tex
	@rm -f ufctex-build-minimo.* .ufctex-v2-profile.tex .ufctex-abntexto.cls
	@rm -f overleaf-stable-pdflatex.pdf overleaf-stable-lualatex.pdf
	@rm -rf _minted-* dist
	@rm -f $(filename).pdf
	@echo "Processo finalizado com sucesso."
