# abntexto-ufc v3 — Regression Audit

Updated: 2026-09-05
Status: CLOSED
Baseline SHA: `c4bf51b574647226ee488440579ec2a204c16c79`
Closeout checkpoint: `ee2ab6e6404cbeb15447f694e998c78a9d5d8dc2`

## Closeout

Regression Audit closed after the shared V3 foundation was rechecked before scientific-article runtime work.

Evidence at closeout: the two reviewed PDFs are represented by exactly 34 tracked requirements in `docs/UFC-LIBRARIAN-REVIEW.md`; `docs/V3-CORRECTION-PLAN.md` contains the executable correction queue; the active roadmap uses readable phase names; object typography and selected NBR 6023:2025 disputes had explicit unresolved authority status at audit closeout; Static `33937439818` passed; full Linux `33937439846` passed; scientific-article runtime had not started before the regression reset.

The project therefore advanced to **Core Corrections**. This closeout does not mean the 34 review items were already corrected.

## Initial 34-item baseline

- `PASS`: 19
- `PARTIAL`: 11
- `FAIL`: 1
- `NORMATIVE-REVIEW`: 3

These are historical audit closeout facts.

## Post-audit disposition in Core Corrections

The object-title authority conflict is resolved and accepted. Checkpoint `3f47081cbbd00a44b9ee86a6b406580e79b593c0` passed Static `33965794475` and full Linux `33965794519`; review item 21 is PASS.

Canonical-reference generated-PDF checkpoint `c4c59f83b67cb152ed9a88345541457b8f18021c` passed Static `33969505681` and full Linux `33969505614`, closing review items 11, 16 and 28.

Engineering-language false-negative hardening is resolved. Checkpoint `edeb14b7a96d1cab3ad9551701087ddf4dff059a` passed Static `33972111694` and full Linux `33972111696`; permanent evidence reports `portuguese_technical_diagnostics=0`.

Bounded reference evidence implementation `63d20de2894e6ba4149bac0b2aba3efeb1aef27f`, synchronized at `bcd851b3176b516091a254bc57b5ae4e8add9358`, passed Static `33974062993` and full Linux `33974063103`. Reviewer-specific evidence for items 30, 31 and 32 passed without changing normative runtime; item 32 is closed.

Current librarian-review state is therefore **29 PASS / 4 PARTIAL / 0 FAIL / 1 NORMATIVE-REVIEW**. The remaining PARTIAL items are 1, 2, 7 and 34. Item 33 remains fail-closed pending authoritative current NBR 6023:2025 evidence.

Scientific Article remains deferred until Core Corrections and Reference PDF Validation close.

## Regression discipline retained after audit

Every material advance continues to update the active execution documentation. Every phase requires a phase-end regression on one immutable candidate before closure; targeted correction checks never replace that phase-level regression.
