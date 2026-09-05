# AGENTS.md — Repository Bootstrap and Control Rules

This repository uses fail-closed state reconciliation for v3 development.

## Mandatory session bootstrap

Before changing code, tests, standards, workflows, documentation, or release metadata:

1. Identify the actual Git branch and HEAD.
2. Read `release/v3-roadmap.json`.
3. Read `docs/HANDOFF-V3.0.0.md`.
4. Read `docs/ROADMAP-V3.0.0.md`.
5. During **Core Corrections**, also read `docs/V3-CORRECTION-PLAN.md`, `docs/V3-REGRESSION-AUDIT.md`, `docs/UFC-LIBRARIAN-REVIEW.md`, and `docs/ENGINEERING-LANGUAGE.md`.
6. Compare Git facts, machine state, handoff, and roadmap.
7. If phase, checkpoint, acceptance state, or temporary-artifact state disagrees, reconcile the control plane before feature work.

Memory, prior chats, historical branch names, old pull requests, and workflow names never override current repository state.

## Current state

- Target version: `3.0.0`.
- Active phase: **Core Corrections**.
- Regression baseline `c4bf51b574647226ee488440579ec2a204c16c79`: Static `33937439818` and Linux `33937439846` success.
- Object/Core checkpoint `3f47081cbbd00a44b9ee86a6b406580e79b593c0`: Static `33965794475` and Linux `33965794519` success, `PASS=31 FAIL=0 SKIP=0`.
- Canonical-reference generated-PDF checkpoint `c4c59f83b67cb152ed9a88345541457b8f18021c`: Static `33969505681` and Linux `33969505614` success, `PASS=31 FAIL=0 SKIP=0`; items 11, 16 and 28 closed.
- Engineering-language hardening checkpoint `edeb14b7a96d1cab3ad9551701087ddf4dff059a`: Static `33972111694` and Linux `33972111696` success; permanent audit reports `portuguese_technical_diagnostics=0`.
- Reference evidence checkpoint `bcd851b3176b516091a254bc57b5ae4e8add9358`: Static `33974062993` and Linux `33974063103` success, `PASS=31 FAIL=0 SKIP=0`; items 30, 31 and 32 reviewer-specific evidence passed and item 32 closed.
- Current 34-item state: **29 PASS / 4 PARTIAL / 0 FAIL / 1 NORMATIVE-REVIEW**.
- Current bounded batch: **Core Corrections — Front Matter and Annex Closeout** for items 1, 2, 7 and 34.
- Item 33 remains fail-closed pending authoritative current NBR 6023:2025 evidence.
- Scientific Article runtime remains deferred until Core Corrections and Reference PDF Validation are complete.

## Readable phase model

1. **Regression Audit** — closed
2. **Core Corrections** — active
3. **Reference PDF Validation** — queued
4. **Scientific Article** — queued
5. **Final Certification** — queued
6. **Release** — queued

Do not create new opaque work identifiers such as nested letter/number codes. GitHub issue/PR numbers and immutable SHAs provide traceability. Historical labels may appear only to identify old evidence.

## Engineering rules

- Project-owned technical surfaces are English. Portuguese is allowed only in academic/rendered content, bibliography data, official wording, literal Portuguese output under test, or explicit upstream/current-runtime boundaries.
- Treat an engineering-language gate that misses known project-owned Portuguese diagnostics as a false-negative defect. Fix the detector and diagnostics; do not weaken the policy or flag legitimate academic Portuguese.
- Preserve the closed v3 public API unless a current requirement explicitly authorizes a change.
- Do not silently change normative rule IDs, expected values, tolerances, locators, applicability, source precedence, or proof-state semantics.
- A green test proves only the contract encoded by that test. Current authority and presentation acceptance remain separate obligations.
- Reviewer comments are evidence, not automatic normative authority. Reconcile them against current institutional acts, current ABNT editions, compatible UFC requirements, and project precedence before changing normative behavior.
- For every automatically enforceable correction, add positive evidence and a negative case where practical.
- Presentation requirements require canonical PDF evidence in addition to source-level checks.
- Do not weaken tests merely to recover green CI. Correct the rule, generator, observer, or fixture according to the classified finding.
- Temporary workflow/executor lifecycle must be atomic: create -> execute -> validate -> remove before checkpoint closeout.
- Permanent workflows remain `Static contract`, `Linux integration`, and `Linux release check`.
- Heavy Windows/literal-font/PDF-A/distribution checks belong to Final Certification or an explicitly justified correction task.
- Do not redistribute proprietary Microsoft fonts.
- Do not perform actual CTAN submission before **Release**.

## Progress documentation discipline

A **material advance** is any change that alters runtime behavior, normative classification, test/evidence coverage, canonical reference content, phase status, acceptance status, or release/certification state.

For every material advance, update the relevant execution document/review matrix and canonical handoff in the same work cycle; synchronize roadmap/machine state whenever phase, acceptance, evidence, batch, or branch facts change.

## Mandatory phase-end regression

No phase may transition to `CLOSED`, and no subsequent phase may become `ACTIVE`, until one immutable candidate SHA passes the complete relevant **phase-end regression** and the result is recorded.

At minimum this includes Static contract, full relevant Linux integration, phase-specific acceptance evidence, and canonical-PDF checks when presentation is in scope. Final Certification additionally requires the heavy literal-font/Windows/PDF-A/distribution matrix. Any unexplained failure keeps the phase open.

## Core Corrections acceptance model

A correction closes only when the applicable combination is established: current authority/project classification, correct runtime/reference behavior, automated positive evidence or explicit manual review, negative evidence where practical, and canonical-PDF evidence when presentation is part of the requirement.

For the active Front Matter and Annex Closeout batch, prefer canonical/source evidence over runtime changes because the current implementation already supports the reviewed forms. Add explicit evidence for blank/filled department behavior, complete-author-name presentation, committee `Instituição (sigla)` rendering, and annex source/heading/TOC presentation. Item 33 remains fail-closed.

## Branch governance and fail-closed rule

The steady state is `main` plus short-lived task branches. Releases are preserved by immutable tags and GitHub Releases, not permanent audit branches.

If a required fact cannot be established from the current Git repository, canonical state files, current normative evidence, or reviewed source material, record the ambiguity and stop advancement to the next phase. Do not infer closure from naming, memory, historical intent, or partial certification evidence.
