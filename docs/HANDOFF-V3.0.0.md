# abntexto-ufc v3.0.0 — Canonical Handoff

Updated: 2026-09-05

## Current checkpoint

- Repository: `tiagosombrra/abntexto-ufc`.
- Canonical branch: `main`.
- Active task branch: `plan/v3-regression-reset`.
- Active phase: **Core Corrections**.
- Regression baseline: `c4bf51b574647226ee488440579ec2a204c16c79`; Static `33937439818` and Linux `33937439846` succeeded.
- Object/Core checkpoint `3f47081cbbd00a44b9ee86a6b406580e79b593c0`: Static `33965794475` and Linux `33965794519` succeeded, `PASS=31 FAIL=0 SKIP=0`.
- Canonical-reference generated-PDF checkpoint `c4c59f83b67cb152ed9a88345541457b8f18021c`: Static `33969505681` and Linux `33969505614` succeeded, `PASS=31 FAIL=0 SKIP=0`; librarian items 11, 16 and 28 closed.
- Engineering-language hardening checkpoint `edeb14b7a96d1cab3ad9551701087ddf4dff059a`: Static `33972111694` and Linux `33972111696` succeeded; permanent detector reports zero project-owned Portuguese technical diagnostics.
- Reference evidence checkpoint `bcd851b3176b516091a254bc57b5ae4e8add9358`: Static `33974062993` and Linux `33974063103` succeeded, `PASS=31 FAIL=0 SKIP=0`; reviewer-specific items 30, 31 and 32 evidence passed and item 32 closed.
- Current 34-item state: `29 PASS / 4 PARTIAL / 0 FAIL / 1 NORMATIVE-REVIEW`.
- Current bounded batch: **Core Corrections — Front Matter and Annex Closeout** for items 1, 2, 7 and 34.
- Item 33 remains fail-closed pending authoritative current NBR 6023:2025 evidence.
- Scientific Article runtime remains deferred.

Canonical control documents: `release/v3-roadmap.json`, `docs/ROADMAP-V3.0.0.md`, `docs/V3-CORRECTION-PLAN.md`, `docs/UFC-LIBRARIAN-REVIEW.md`, `docs/V3-OBJECT-TYPOGRAPHY-DECISION.md`, `docs/V3-REGRESSION-AUDIT.md`, and `docs/ENGINEERING-LANGUAGE.md`.

Git facts, machine state, roadmap and this handoff must describe the same active phase and acceptance state. Disagreement fails closed.

## Accepted reference closeout

Implementation `63d20de...`, synchronized at `bcd851b...`, was evidence-only and did not change `abntexto-ufc/standards/nbr6023-2025.def` or any normative runtime rule.

Linux `33974063103` emitted explicit PASS evidence for:

1. item 30 — electronic unknown-publication markers omitted for the controlled online entry;
2. item 31 — thesis/dissertation work type plus a single consistent year;
3. item 32 — ABNT standard publisher/year and bibliography-specific multivolume `2 v.` physical description.

The existing `tests/integration/multivolume.sh` remains document-pagination evidence only and was not reused as bibliography evidence.

## Immediate action

Continue **Core Corrections — Front Matter and Annex Closeout**:

1. add explicit blank/filled department evidence for item 1;
2. prove the canonical complete-author-name placeholder is present in generated pre-textual output for item 2;
3. prove the approval-page committee institution renders an `Instituição (sigla)` example for item 7;
4. prove canonical annex source attribution together with annex heading and TOC presentation for item 34;
5. synchronize all affected control documents in the same material advance;
6. run Static contract and full Linux integration on the synchronized checkpoint;
7. if items 1, 2, 7 and 34 close, prepare one immutable **Core Corrections phase-end regression** candidate before activating Reference PDF Validation;
8. keep item 33 untouched/fail-closed.

## Mandatory operating discipline

Every **material advance** updates the relevant execution documentation and this handoff in the same work cycle. Phase/acceptance/evidence state and branch/checkpoint facts must remain synchronized with the roadmap and machine state.

Every phase requires a **phase-end regression** on one immutable candidate before closure. Targeted checks never authorize a phase transition by themselves.

## Hard boundaries

- Do not resume Scientific Article while Core Corrections or Reference PDF Validation are open.
- Preserve the closed V3 public API unless current evidence explicitly authorizes a change.
- Do not translate reviewer comments directly into normative runtime behavior when current authority remains unresolved.
- Do not weaken tests merely to recover green CI.
- Do not redistribute proprietary fonts.
- CTAN submission remains blocked until **Release**.
