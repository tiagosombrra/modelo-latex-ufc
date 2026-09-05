# UFC Librarian Review — Consolidated 34-Point Contract

Updated: 2026-09-05

## Purpose

This document converts the union of the two annotated v1.1.1 review PDFs supplied by the project maintainer into a stable engineering contract for the v3 regression/correction cycle. Reviewer annotations are evidence, not automatic normative truth; current ABNT/UFC authority must be reconciled before normative runtime changes.

## Status vocabulary

- `PASS`: current v3 behavior and evidence satisfy the item.
- `PARTIAL`: behavior, documentation, evidence, or canonical presentation remains incomplete.
- `FAIL`: current v3 behavior/reference output contradicts the accepted requirement.
- `NORMATIVE-REVIEW`: authority remains insufficient to encode the requested behavior safely.

## Current summary

Canonical-reference generated-PDF checkpoint `c4c59f83b67cb152ed9a88345541457b8f18021c` passed Static `33969505681` and full Linux `33969505614`, with `PASS=31 FAIL=0 SKIP=0`. Explicit PDF evidence closed review items 11, 16 and 28.

Engineering-language hardening is accepted at `edeb14b7a96d1cab3ad9551701087ddf4dff059a`: Static `33972111694` and full Linux `33972111696` succeeded.

Reference evidence checkpoint `bcd851b3176b516091a254bc57b5ae4e8add9358` passed Static `33974062993` and full Linux `33974063103`, with `PASS=31 FAIL=0 SKIP=0`. Reviewer-specific bibliography evidence passed for items 30, 31 and 32; item 32 is therefore closed.

Current review state is **29 PASS, 4 PARTIAL, 0 FAIL, 1 NORMATIVE-REVIEW = 34 items**.

## Consolidated review contract

| # | Review requirement | Current v3 assessment | Primary surfaces |
|---:|---|---|---|
| 1 | Department/unit line must be optional (`se houver`) and omitted cleanly when absent. | PARTIAL — guidance/runtime improved; canonical blank/filled confirmation remains. | `core.def`, `academic-works.def`, `template/main.tex` |
| 2 | Pre-textual author field/examples must make clear that the complete author name is required. | PARTIAL — canonical placeholder corrected; final reference-PDF confirmation remains. | `template/main.tex`, reference guidance |
| 3 | Optional subtitle must be rendered consistently on cover, title page, and approval page. | PASS | `frontmatter.def`, `academic-works.def` |
| 4 | Advisor identification on the title page must end with the requested final punctuation. | PASS — runtime correction present and full integration green. | `frontmatter.def`, `academic-works.def` |
| 5 | Co-advisor/co-advisora must be supported and rendered conditionally when present. | PASS | `core.def`, `frontmatter.def` |
| 6 | Master's and doctoral nature blocks must include area of concentration when applicable, including title and approval pages. | PASS | `core.def`, `frontmatter.def` |
| 7 | Committee member institution must support the `Instituição (sigla)` presentation where applicable. | PARTIAL — canonical examples improved; final approval-page confirmation remains. | `core.def`, `frontmatter.def`, `template/main.tex` |
| 8 | Approval-page committee must support additional members and remain variable in size. | PASS | `frontmatter.def`, `template/main.tex` |
| 9 | CAPES-funded works must carry guidance for the mandatory acknowledgment from Portaria CAPES nº 206/2018. | PASS | `template/frontmatter/acknowledgments.tex`, normative catalog |
| 10 | `RESUMO` must begin at the first usable text line/heading position instead of being vertically displaced. | PASS — retain final visual confirmation. | `frontmatter.def`, front-matter geometry tests |
| 11 | Figure/table/object titles must follow sentence-case capitalization where applicable. | PASS — source/PDF evidence accepted; Static `33969505681` and Linux `33969505614` green. | reference content, `reference_guide_contract.py`, `reference-document.sh` |
| 12 | Lists of abbreviations/acronyms and symbols must align with the 3 cm left text margin. | PASS | front-matter alignment checks |
| 13 | Pre-textual elements must not appear in the table of contents. | PASS | TOC checks |
| 14 | Do not create synthetic aggregate `APÊNDICES` or `ANEXOS` pages/TOC entries. | PASS | appendix/annex checks |
| 15 | Appendix and annex entries in the TOC must use the required uppercase/bold presentation. | PASS — retain final visual confirmation. | appendix/annex integration and checks |
| 16 | First body-text use of UFC should present the full institutional name followed by `(UFC)`. | PASS — source and canonical-PDF evidence accepted. | reference prose/examples, source/PDF reference gates |
| 17 | Academic text/code demonstrations must not accidentally change the adopted text family/nominal size. | PASS — code typography regression proves same family and nominal 12 pt across exercised body/code/algorithm paths. | `fonts.def`, `tests/integration/code-typography.sh` |
| 18 | Author/corporate-author names in citations must follow current NBR 10520 capitalization rather than legacy all-caps output. | PASS | `bibliography.def`, citation checks |
| 19 | Long direct quotations must include the page or other required locator when the source provides one. | PASS — reviewer fixture renders `p. 42`; full Linux green. | citation fixtures/checks |
| 20 | Parenthetical citation punctuation after a long direct quotation must not contain an extraneous full stop before the citation. | PASS — explicit positive/negative reviewer gate; full Linux green. | citation fixtures/checks |
| 21 | Figure/table/object upper identification/title must use body-size typography (12 pt); lower legend/source/note remain reduced where applicable. | PASS — final-PDF and IBGE evidence confirm 12 pt upper / 10 pt lower split. | `objects.def`, `modules.def`, object/IBGE final-PDF checks |
| 22 | Object title, source, and note blocks must use single spacing. | PASS | `objects.def`, object geometry checks |
| 23 | Object source indication should include a page locator when applicable. | PASS — external illustration fixture renders `p. 42`; full Linux green. | documentary-source fixture/check |
| 24 | Alínea items begin with lowercase text when grammatically continuing the introductory sentence. | PASS | `layout.def`, reference fixture |
| 25 | Alínea items use semicolons between intermediate items and appropriate final punctuation. | PASS | `layout.def`, reference fixture |
| 26 | A nested subalínea sequence is introduced with a colon and uses the required subordinate punctuation. | PASS | `layout.def`, reference fixture |
| 27 | Alíneas are ordered alphabetically, not by Arabic numerals. | PASS | `ufclettereditems`, reference fixture |
| 28 | Example section/subsection headings must follow sentence case where appropriate, including correct `etc.` punctuation. | PASS — source and generated-PDF evidence accepted. | reference content/headings, source/PDF reference gates |
| 29 | First-line paragraph indentation must be consistent with the adopted UFC body-text rule. | PASS | body-paragraph checks |
| 30 | Unknown place/publisher data must not emit obsolete/inappropriate patterns for online resources; electronic examples must follow current NBR 6023 handling. | PASS — controlled electronic case passed at `bcd851b...` / Linux `33974063103`; no normative runtime strengthening was required. | `nbr6023-2025.def`, bibliography fixtures |
| 31 | Thesis/dissertation references must use the correct work-type structure and must not duplicate or contradict the year. | PASS — controlled thesis/dissertation evidence passed with a single consistent year at `bcd851b...`. | bibliography fixtures |
| 32 | Standard and multivolume examples must use the accepted publisher/year and physical-description conventions when applicable. | PASS — controlled ABNT standard and bibliography-specific `@mvbook`/`2 v.` evidence passed at `bcd851b...` / Linux `33974063103`. | bibliography fixtures/reference guide |
| 33 | DOI/availability, repeated-author treatment, `São Paulo (Estado)` and related edge cases must be reconciled against current NBR 6023:2025 before runtime changes. | NORMATIVE-REVIEW | bibliography runtime/fixtures/locator audit |
| 34 | Appendix/annex headings must use the required bold presentation, and annexed external material must explicitly identify its source. | PARTIAL — source example and heading behavior exist; canonical visual/source confirmation remains. | appendix/annex integration, canonical annex |

## Remaining normative conflict

Review item 33 remains fail-closed. Current NBR 6023:2025 is the governing technical edition, but exact authoritative text for the disputed DOI/online/repeated-author/corporate-author cases is not available in the current evidence corpus. Do not implement older review wording as current runtime law without that authority.

## Current closeout batch

The remaining PARTIAL items are 1, 2, 7 and 34. The next bounded Core Corrections step is canonical evidence for optional department rendering, complete-author-name presentation, committee institution/acronym presentation, and annex source/heading/TOC presentation.

## Acceptance rule

No item is closed merely because source text looks plausible or a related test is green. Closure requires the applicable combination of authority/project classification, correct runtime/reference behavior, positive regression evidence, negative evidence where machine-detectable, and canonical presentation evidence when presentation is part of the requirement.
