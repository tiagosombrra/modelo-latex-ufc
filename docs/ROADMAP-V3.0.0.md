# abntexto-ufc v3.0.0 — Engineering Roadmap

Updated: 2026-09-05

## Current status

**Core Corrections is ACTIVE.**

Regression Audit is closed. Object/Core Corrections checkpoint `3f47081cbbd00a44b9ee86a6b406580e79b593c0` passed Static `33965794475` and Linux `33965794519`, closing review item 21.

Canonical-reference generated-PDF checkpoint `c4c59f83b67cb152ed9a88345541457b8f18021c` passed Static `33969505681` and full Linux `33969505614`, with `PASS=31 FAIL=0 SKIP=0`, closing review items 11, 16 and 28.

Engineering-language hardening checkpoint `edeb14b7a96d1cab3ad9551701087ddf4dff059a` passed Static `33972111694` and full Linux `33972111696`; permanent evidence reports `portuguese_technical_diagnostics=0`.

Reference evidence checkpoint `bcd851b3176b516091a254bc57b5ae4e8add9358` passed Static `33974062993` and full Linux `33974063103`, with `PASS=31 FAIL=0 SKIP=0`. Reviewer-specific items 30, 31 and 32 evidence passed; item 32 is closed.

Current 34-point state is **29 PASS / 4 PARTIAL / 0 FAIL / 1 NORMATIVE-REVIEW**. The remaining PARTIAL items are 1, 2, 7 and 34. Item 33 remains fail-closed pending authoritative current NBR 6023:2025 evidence.

Machine authority: `release/v3-roadmap.json`.
Canonical handoff: `docs/HANDOFF-V3.0.0.md`.
Correction queue: `docs/V3-CORRECTION-PLAN.md`.
Librarian review: `docs/UFC-LIBRARIAN-REVIEW.md`.
Engineering language policy: `docs/ENGINEERING-LANGUAGE.md`.
Object typography decision: `docs/V3-OBJECT-TYPOGRAPHY-DECISION.md`.

## Operating discipline

Every **material advance** must update the relevant execution documentation and canonical handoff in the same work cycle. Changes to phase state, acceptance state, evidence state, current correction batch, or branch/checkpoint facts must also update this roadmap and `release/v3-roadmap.json`.

Every phase ends with a mandatory **phase-end regression** on one immutable candidate SHA. Targeted checks accumulated during a phase do not replace this gate.

## Phase plan

| Phase | Status | Goal | Exit gate |
|---|---|---|---|
| **Regression Audit** | CLOSED | Revalidate the shared V3 foundation and classify recovered review requirements and newly discovered defects. | Closed with 34-item contract, classified findings and green Static/full Linux phase-end regression. |
| **Core Corrections** | ACTIVE | Correct shared runtime, template, normative mapping, documentation and tests identified by the audit. | No unresolved shared FAIL; blocking P0/P1 evidence complete; authority gaps explicit/fail-closed; phase-end regression green on one immutable SHA. |
| **Reference PDF Validation** | QUEUED | Compile the corrected canonical V3 reference and inspect it page by page against accepted UFC requirements, recovered reviews and V2.1 preservation baseline where applicable. | Page-level visual checklist and reproducible presentation evidence pass, then phase-end regression green. |
| **Scientific Article** | QUEUED | Implement the article profile on the corrected shared foundation using the retained article authority contract. | Article runtime, modality, positive/negative evidence, canonical rendering and phase-end regression pass. |
| **Final Certification** | QUEUED | Run complete profile/engine/literal-font/Unicode/embedding/PDF-A/distribution certification. | Complete heavy certification matrix and phase-end regression green on one immutable candidate. |
| **Release** | QUEUED | Finalize user documentation, bundles, release assets, checksums and publication actions. | No unresolved roadmap/normative item; release checklist and final regression/verification recorded. |

## Active phase — Core Corrections

### Completed/validated work

- readable phase/control-plane migration;
- machine-protected 34-item librarian contract;
- mandatory documentation-on-material-advance and phase-end regression governance;
- advisor/co-advisor punctuation and committee/front-matter implementation support;
- first textual UFC full-name reference and stale V2/current-reference hygiene;
- reviewer-specific long-direct-quotation locator/punctuation evidence;
- external-illustration source locator evidence;
- code/body typography consistency evidence;
- object typography migration accepted by Static `33965794475` + Linux `33965794519`;
- source/generated-PDF evidence for items 11, 16 and 28 accepted through `c4c59...`;
- engineering-language false-negative hardening accepted at `edeb14...`, Static `33972111694` + Linux `33972111696`;
- bounded references evidence accepted at `bcd851b...`, Static `33974062993` + Linux `33974063103`, closing item 32 while preserving item 33 fail-closed.

### Current work — Front Matter and Annex Closeout

The remaining PARTIAL review items are 1, 2, 7 and 34. The next bounded evidence step must confirm:

1. item 1 — blank department is omitted cleanly and a filled department is rendered;
2. item 2 — the canonical complete-name author placeholder reaches generated pre-textual output;
3. item 7 — approval-page committee institution supports/render `Instituição (sigla)`;
4. item 34 — canonical annex source attribution is present together with accepted annex heading and TOC presentation.

Prefer evidence additions over runtime changes unless a test exposes a real implementation defect. Keep item 33 untouched.

### Remaining Core Corrections after this closeout batch

If items 1, 2, 7 and 34 close, no librarian-review `PARTIAL` or `FAIL` remains. Core Corrections still does **not** close automatically: prepare one immutable candidate and run the complete Core Corrections phase-end regression, with documentation synchronized to that SHA. Only then may Reference PDF Validation become ACTIVE.

## Gate before Reference PDF Validation

Core Corrections closes only when all shared blocking P0/P1 corrections have implementation/reference behavior and evidence, affected normative mappings/tests are updated atomically where authority changed, no shared runtime FAIL remains, remaining NORMATIVE-REVIEW items are explicitly fail-closed/non-contradictory or resolved, documentation/review matrices match the candidate SHA, and Static plus full Linux pass on the same immutable phase-end candidate.

## Gate before Scientific Article

Scientific Article starts only after Core Corrections closes and the corrected canonical V3 reference PDF passes Reference PDF Validation, including its own phase-end regression.

## Naming policy

Use descriptive work names such as `Core Corrections — Front Matter and Annex Closeout`, `Reference PDF Validation — Pre-textual Pages`. Do not create new opaque nested letter/number identifiers. GitHub issue/PR numbers and immutable SHAs provide traceability.

## Retained checkpoints

- certified non-article foundation: `c79f3c73f1d51a30175e8259269504d029442a1c`;
- article source-contract implementation: `4d018a92697e8f39e3a53b034c451e55996c84fb`;
- article pre-runtime checkpoint: `7a7562d23e8bf6c92abb635718639d617a2ed6ff`;
- pre-regression `main` baseline: `c4bf51b574647226ee488440579ec2a204c16c79`;
- accepted object/Core Corrections checkpoint: `3f47081cbbd00a44b9ee86a6b406580e79b593c0`;
- accepted canonical-reference PDF checkpoint: `c4c59f83b67cb152ed9a88345541457b8f18021c`;
- accepted engineering-language hardening checkpoint: `edeb14b7a96d1cab3ad9551701087ddf4dff059a`;
- accepted bounded references checkpoint: `bcd851b3176b516091a254bc57b5ae4e8add9358`.
