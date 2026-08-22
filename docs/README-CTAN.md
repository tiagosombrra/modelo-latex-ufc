# ufctex

`ufctex` is a LaTeX class for academic works at the Federal University of Ceará (UFC), Brazil. It is based on `abntexto` and provides institutional profiles for undergraduate works, specialization works, dissertations, theses, and research proposals.

Version: 2.1.0

Maintainer: Tiago Sombra (`tiagosombrra`)

## Requirements

Core requirements:

- LaTeX2e;
- `abntexto` 1.1 or newer;
- `babel`, `iftex`, `microtype`, `etoolbox`;
- `biblatex` with the ABNT style and `biber`.

Optional modules may additionally use `tabularray-abnt`, `xcolor`, `listings`, `minted`, `algpseudocodex`, `glossaries` and `imakeidx`. `minted` also requires its external Python/Pygments toolchain.

TeX Live 2026 is the reference distribution used by the project CI.

## Fonts

UFC documents may use Times New Roman or Arial. Literal Microsoft font files are not distributed by this package.

LuaLaTeX can use locally installed Times New Roman and Arial through `fontspec`. For pdfLaTeX, the project provides PowerShell helpers that prepare local metrics from Microsoft fonts already installed on Windows.

Portable fallback fonts are available when strict literal-font mode is disabled, but they are not presented as literal Times New Roman or Arial.

## Documentation

The CTAN submission candidate contains:

- the complete reference document in PDF;
- the source of the reference document;
- the normative implementation matrix in `NORMAS.md`;
- a TDS archive for installation testing.

The full editable UFC template is distributed separately in the project releases.

## License and institutional mark

The `ufctex` source code and project documentation are subject to the LaTeX Project Public License 1.3c or any later version, as stated in `LICENSE`.

The UFC coat of arms is an official institutional mark published by the Federal University of Ceará and governed by the University's visual identity rules. It is not declared to be covered by the LPPL. Its redistribution classification must be confirmed before a CTAN submission.

Official visual identity source: https://www.ufc.br/a-universidade/identidade-visual-da-ufc

The pinned `abntexto` class used by the dedicated Overleaf compatibility bundle is upstream public-domain software and is not included in this CTAN package.

## Release state

Version 2.1.0 has completed Gate T, deterministic distribution preflight and the real Overleaf import smoke test. It is the stable GitHub/Overleaf release line.

The CTAN archive remains a submission candidate until the redistribution classification of the UFC institutional mark is confirmed. The package name `ufctex` must also be reconfirmed in the CTAN catalogue immediately before upload.

## Project

Repository: https://github.com/tiagosombrra/modelo-latex-ufc

Issues and source releases are maintained in the repository above.
