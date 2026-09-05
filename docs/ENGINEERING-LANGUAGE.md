# Engineering Language Policy

Updated: 2026-09-05

`abntexto-ufc` v3 uses English for every project-owned engineering surface: repository paths and filenames, the LaTeX project API and internal identifiers, source comments, technical diagnostics, scripts, tests, workflows, validator controls/UI, JSON/schema terminology, and active engineering documentation.

Portuguese remains valid when it is academic or authoritative content rather than project engineering nomenclature: rendered academic prose and headings, sample metadata values, bibliography data, official UFC/ABNT/CAPES names or wording, literal Portuguese output under test, and identifiers owned by an upstream dependency at an explicit integration boundary.

## Permanent enforcement

`tests/checks/engineering_language.py` is the permanent static enforcement surface. It also protects canonical English v3 profile/API identifiers and rejects retired Portuguese technical identifiers in active machine/runtime contracts.

A gate that reports zero violations while known project-owned Portuguese technical diagnostics remain is itself defective. The correct response is to strengthen the detector and translate the diagnostics, not weaken the policy or reclassify project-owned technical messages as academic content.

## Core Corrections hardening — accepted

The hardening cycle intentionally ran fail-closed. Successive stronger scans exposed previously missed project-owned Portuguese/mixed diagnostics in bibliography/multivolume, algorithm numbering, catalog-card, duplex/vector and back-matter integration surfaces. The project corrected the complete related diagnostic surfaces rather than suppressing individual matches.

Accepted checkpoint: `edeb14b7a96d1cab3ad9551701087ddf4dff059a`.

Acceptance evidence:

- Static contract `33972111694`: SUCCESS;
- full Linux integration `33972111696`: SUCCESS;
- permanent audit: `ENGINEERING-LANGUAGE-EVIDENCE status=PASS portuguese_technical_diagnostics=0`;
- phase governance remained PASS;
- academic/rendered Portuguese literals remained intentionally preserved.

Historical failed Static runs are retained as evidence that the stronger detector and phase-governance contract stopped hidden debt rather than masking it.

## Scope boundary

Allowed Portuguese includes rendered academic prose/headings, bibliography and metadata data values, official wording/names, literal Portuguese output intentionally exercised by a test, and genuine upstream identifiers at a documented integration boundary.

Project-owned comments, diagnostics, CLI/UI messages, test failure messages, machine-state nomenclature and current technical documentation remain English. Broad stopword-style matching is not an acceptable substitute for diagnostic/context-aware detection.

## Canonical identifiers and phase authority

The canonical article profile identifier is `scientific-article`; `article.*` is the project-owned rule namespace. Historical Portuguese profile identifiers are not restored.

Current phase/status authority comes from `release/v3-roadmap.json`, `docs/HANDOFF-V3.0.0.md`, and `docs/ROADMAP-V3.0.0.md`. Historical opaque stage names may appear only as Git/issue/PR evidence and do not define current work.

## Ongoing guard

Engineering-language hardening is closed as a correction batch, but the detector remains a permanent regression guard. Any new material advance that reintroduces a project-owned Portuguese technical diagnostic fails closed and must be corrected before acceptance.
