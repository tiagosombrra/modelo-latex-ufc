#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = ROOT / "standards"
MAP_PATH = STANDARDS_DIR / "reference-guide-map.json"
CATALOG_PATH = STANDARDS_DIR / "catalog.json"
ATOMIC_PATH = STANDARDS_DIR / "atomic-rules.json"
REFERENCE_ROOT = ROOT / "template"
ALLOWED_CLASSIFICATIONS = {"normative", "institutional", "model-policy", "example"}
RETIRED_REFERENCE_TOKENS = (
    "tccgraduacao",
    "tccespecializacao",
    "projetoanonimizado",
    "ficha-catalografica",
    "fonte-estrita",
    "backmatter/referencias.bib",
    "frontmatter/dedicatoria.tex",
)
REVIEWED_LEGACY_HEADINGS = (
    "Usando Fórmulas Matemáticas",
    "Usando Código-fonte",
    "Usando Teoremas, Proposições, etc",
    "Usando Questões",
    "Resultados do Experimento A",
    "Resultados do Experimento B",
)
REVIEWED_LEGACY_OBJECT_TITLES = (
    "Gráfico da Atmosfera Superior",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_declared_rule_ids(value: Any) -> set[str]:
    rule_ids: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"rule_id", "expected_rule_id"} and isinstance(item, str):
                rule_ids.add(item)
            elif key == "rule_ids" and isinstance(item, list):
                rule_ids.update(entry for entry in item if isinstance(entry, str))
            else:
                rule_ids.update(collect_declared_rule_ids(item))
    elif isinstance(value, list):
        for item in value:
            rule_ids.update(collect_declared_rule_ids(item))
    return rule_ids


def collect_rule_ids(catalog: dict[str, Any], atomic: dict[str, Any]) -> set[str]:
    rule_ids = {rule["id"] for rule in catalog.get("rules", []) if "id" in rule}
    rule_ids.update(atomic.get("keep_atomic", []))
    for group in atomic.get("groups", {}).values():
        for rule in group:
            if "id" in rule:
                rule_ids.add(rule["id"])

    for path in sorted(STANDARDS_DIR.glob("*.json")):
        if path == MAP_PATH:
            continue
        rule_ids.update(collect_declared_rule_ids(load_json(path)))
    return rule_ids


def audit_reference_hygiene() -> list[str]:
    failures: list[str] = []
    tex_files = sorted(REFERENCE_ROOT.rglob("*.tex"))
    for path in tex_files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        if re.search(r"\bV2\b", text):
            failures.append(f"{rel}: stale V2 wording remains in the canonical V3 reference")
        for token in RETIRED_REFERENCE_TOKENS:
            if token in text:
                failures.append(f"{rel}: retired V3 reference token remains: {token}")
        if re.search(r"\\texttt\{tipo\}", text):
            failures.append(f"{rel}: retired public profile key is still documented: tipo")

    main = (REFERENCE_ROOT / "main.tex").read_text(encoding="utf-8")
    intro = (REFERENCE_ROOT / "chapters" / "1-introduction.tex").read_text(encoding="utf-8")
    annex = (REFERENCE_ROOT / "backmatter" / "annexes" / "annex-a.tex").read_text(
        encoding="utf-8"
    )

    required = {
        "template/main.tex": (
            "department = {}",
            "author = {Nome Completo do Autor}",
            "Universidade Federal do Ceará (UFC)",
        ),
        "template/chapters/1-introduction.tex": (
            "Universidade Federal do Ceará (UFC)",
            "\\texttt{undergraduate-capstone}",
        ),
        "template/backmatter/annexes/annex-a.tex": ("\\textbf{Fonte:}",),
    }
    sources = {
        "template/main.tex": main,
        "template/chapters/1-introduction.tex": intro,
        "template/backmatter/annexes/annex-a.tex": annex,
    }
    for rel, markers in required.items():
        for marker in markers:
            if marker not in sources[rel]:
                failures.append(f"{rel}: required V3 reference marker missing: {marker}")

    return failures


def audit_librarian_reference_content() -> tuple[list[str], dict[int, dict[str, Any]]]:
    failures: list[str] = []
    chapter_paths = sorted((REFERENCE_ROOT / "chapters").glob("*.tex"))
    chapters = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in chapter_paths
    }
    corpus = "\n".join(chapters.values())
    intro_path = "template/chapters/1-introduction.tex"
    examples_path = "template/chapters/formatting-examples.tex"
    intro = chapters.get(intro_path, "")
    examples = chapters.get(examples_path, "")

    current_object_titles = (
        "Figura estreita com legenda curta",
        "Fluxo de processamento em arquivo PNG raster",
        "Distribuição sintética de três categorias",
        "Comparação de configurações editoriais do exemplo",
        "Indicadores sintéticos com linhas alternadas",
    )
    missing_object_titles = [title for title in current_object_titles if title not in examples]
    legacy_object_titles = [title for title in REVIEWED_LEGACY_OBJECT_TITLES if title in corpus]
    if missing_object_titles:
        failures.append(
            "librarian item 11: current sentence-case object examples missing: "
            + ", ".join(missing_object_titles)
        )
    if legacy_object_titles:
        failures.append(
            "librarian item 11: reviewed legacy title casing remains: "
            + ", ".join(legacy_object_titles)
        )

    ufc_phrase = "Universidade Federal do Ceará (UFC)"
    phrase_at = intro.find(ufc_phrase)
    first_ufc = re.search(r"\bUFC\b", intro)
    expected_ufc_at = phrase_at + ufc_phrase.index("UFC") if phrase_at >= 0 else -1
    first_use_ok = (
        phrase_at >= 0
        and first_ufc is not None
        and first_ufc.start() == expected_ufc_at
    )
    if not first_use_ok:
        failures.append(
            "librarian item 16: the first body-text UFC occurrence is not "
            "Universidade Federal do Ceará (UFC)"
        )

    headings: list[str] = []
    for text in chapters.values():
        headings.extend(
            re.findall(r"\\(?:section|subsection|subsubsection)\{([^{}]+)\}", text)
        )
    current_heading_markers = (
        "Formatação geral e organização da parte textual",
        "Seções e subseções",
        "Equações",
        "Código-fonte",
        "Citações, notas e referências",
    )
    missing_headings = [heading for heading in current_heading_markers if heading not in headings]
    legacy_headings = [heading for heading in REVIEWED_LEGACY_HEADINGS if heading in corpus]
    malformed_etc = [
        heading
        for heading in headings
        if re.search(r"\betc(?:\s*[,;:]|\s*$)", heading, flags=re.IGNORECASE)
    ]
    if missing_headings:
        failures.append(
            "librarian item 28: current sentence-case heading examples missing: "
            + ", ".join(missing_headings)
        )
    if legacy_headings:
        failures.append(
            "librarian item 28: reviewed legacy heading casing/punctuation remains: "
            + ", ".join(legacy_headings)
        )
    if malformed_etc:
        failures.append(
            "librarian item 28: heading has malformed etc. punctuation: "
            + ", ".join(malformed_etc)
        )

    evidence = {
        11: {
            "status": "PASS" if not missing_object_titles and not legacy_object_titles else "FAIL",
            "current_examples": len(current_object_titles),
            "legacy_titles_present": len(legacy_object_titles),
        },
        16: {
            "status": "PASS" if first_use_ok else "FAIL",
            "first_use": ufc_phrase if first_use_ok else None,
        },
        28: {
            "status": "PASS"
            if not missing_headings and not legacy_headings and not malformed_etc
            else "FAIL",
            "current_heading_markers": len(current_heading_markers),
            "legacy_headings_present": len(legacy_headings),
            "malformed_etc_headings": len(malformed_etc),
        },
    }
    return failures, evidence


def main() -> None:
    guide = load_json(MAP_PATH)
    catalog = load_json(CATALOG_PATH)
    atomic = load_json(ATOMIC_PATH)

    source_ids = {source["id"] for source in catalog.get("sources", []) if "id" in source}
    rule_ids = collect_rule_ids(catalog, atomic)

    seen_topics: set[str] = set()
    failures: list[str] = audit_reference_hygiene()
    librarian_failures, librarian_evidence = audit_librarian_reference_content()
    failures.extend(librarian_failures)
    passes = 0

    for topic in guide.get("topics", []):
        topic_id = topic.get("id", "<missing-id>")
        classification = topic.get("classification")
        topic_sources = topic.get("source_ids", [])
        topic_rules = topic.get("rule_ids", [])
        source_file = topic.get("source_file", "")
        marker = topic.get("marker", "")
        reasons: list[str] = []

        if topic_id in seen_topics:
            reasons.append("duplicate-topic-id")
        seen_topics.add(topic_id)

        if classification not in ALLOWED_CLASSIFICATIONS:
            reasons.append(f"invalid-classification:{classification}")

        if classification in {"normative", "institutional"}:
            if not topic_sources:
                reasons.append("sources-required")
            if not topic_rules:
                reasons.append("rules-required")

        missing_sources = sorted(set(topic_sources) - source_ids)
        if missing_sources:
            reasons.append("unknown-sources:" + ",".join(missing_sources))

        missing_rules = sorted(set(topic_rules) - rule_ids)
        if missing_rules:
            reasons.append("unknown-rules:" + ",".join(missing_rules))

        source_path = ROOT / source_file
        if not source_file or not source_path.is_file():
            reasons.append(f"missing-source-file:{source_file}")
        elif not marker:
            reasons.append("empty-marker")
        elif marker not in source_path.read_text(encoding="utf-8"):
            reasons.append(f"marker-not-found:{marker}")

        status = "FAIL" if reasons else "PASS"
        if reasons:
            failures.append(f"{topic_id}: {';'.join(reasons)}")
        else:
            passes += 1

        print(
            "GUIDE-EVIDENCE "
            f"topic={topic_id} status={status} classification={classification} "
            f"sources={len(topic_sources)} rules={len(topic_rules)}"
        )
        if reasons:
            print(f"GUIDE-EVIDENCE topic={topic_id} reasons={'|'.join(reasons)}")

    for item in (11, 16, 28):
        evidence = librarian_evidence[item]
        details = " ".join(
            f"{key}={json.dumps(value, ensure_ascii=False)}"
            for key, value in evidence.items()
            if key != "status"
        )
        print(
            f"LIBRARIAN-REVIEW-EVIDENCE item={item} "
            f"status={evidence['status']} context=canonical-reference-source {details}"
        )

    total = len(guide.get("topics", []))
    hygiene_failures = [item for item in failures if item.startswith("template/")]
    print(
        "GUIDE-EVIDENCE hygiene_status="
        + ("FAIL" if hygiene_failures else "PASS")
        + f" failures={len(hygiene_failures)}"
    )
    print(f"GUIDE-EVIDENCE summary PASS={passes} FAIL={len(failures)} total={total}")
    print("GUIDE-EVIDENCE normative_contract_changed=false")

    if failures:
        raise SystemExit("Reference guide contract failed:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    main()
