#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE_ROOTS = (
    "tests/checks/",
    "tests/integration/",
    "tests/smoke/",
    "tools/",
    "validator/",
    ".github/workflows/",
)
SOURCE_SUFFIXES = {".py", ".sh", ".js", ".yml", ".yaml", ".ps1"}
DIAGNOSTIC_MARKERS = (
    "echo ",
    "printf ",
    "raise SystemExit",
    "fail_semantic",
    "errors.append",
    "print(",
    "ArgumentParser(",
    "help=",
    "description=",
    "throw new Error",
    "console.",
)
MULTILINE_MARKERS = (
    "raise SystemExit",
    "errors.append",
    "print(",
    "ArgumentParser(",
    "throw new Error",
)
PORTUGUESE_TECHNICAL_TERMS = re.compile(
    r"\b(?:auditoria|validando|falhou|conclu[ií]d[oa]|ausente(?:s)?|incorret[oa]|"
    r"desconhecid[oa]|evid[eê]ncia|p[aá]gina(?:s)?|r[oó]tulo(?:s)?|descri[cç][aã]o|"
    r"desalinhad[oa]|marcador(?:es)?|m[eé]trica(?:s)?|comando(?:s)?|conte[uú]do|"
    r"t[ií]tulo(?:s)?|refer[eê]ncia(?:s)?|cita[cç][aã]o|espa[cç]amento|se[cç][aã]o|"
    r"perfil(?:s)?|sum[aá]rio|capa|orientador|identificador|navega[cç][aã]o|"
    r"fotografia(?:s)?|ap[eê]ndice|anexo|[ií]ndice|gloss[aá]rio|dedicat[oó]ria|"
    r"ep[ií]grafe|agradecimentos|bras[aã]o|contexto|caixas|bibliogr[aá]fic[oa]|"
    r"desambigua[cç][aã]o|ordem|cronol[oó]gica|autoria|hom[oô]nim[oa]|simult[aâ]neos|"
    r"jur[ií]dica|iniciado|consultada|evento|cidade|indevidamente|licenciada|"
    r"divergente|esperad[oa]s?|exatamente|encontrad[oa]s?|entrada(?:s)?|l[ií]der|"
    r"pontilhad[oa]|resolvida|apareceu|quando|obrigat[oó]ri[oa]s?|banca|"
    r"inteiramente|folha|preservad[oa]|convertid[oa]|alta|principal|fim|antes|"
    r"primeir[oa]|poucas|paginadas|comentad[oa]|intervalo|f[ií]sico|excede|prim[aá]ri[oa]|"
    r"introdu[cç][aã]o|metodologia|an[oô]mal[oa]|asterisco|sem[aâ]ntic[oa]|estrutural|"
    r"cap[ií]tulo|reapareceu|vazou|dado|protegid[oa]|acad[eê]mic[oa]|declara[cç][aã]o|"
    r"documento|completo|gerou|apenas|reportou|julgamento|complementar|entidade|"
    r"submiss[aã]o|impresso|impressa|apesar|p[uú]blico|pr[eé]-textual|prefixo)\b",
    re.IGNORECASE,
)
MIXED_PORTUGUESE_TECHNICAL_PHRASES = re.compile(
    r"(?:\bap[oó]s\s+a\s+(?:capa|cover)\b|"
    r"\bconte[uú]do\s+textual\s+n[aã]o\b|"
    r"\bp[aá]gina\s+l[oó]gica\b|"
    r"\bpage\s+l[oó]gica\s+textual\b|"
    r"\bpages?\s+f[ií]sicas?\b|"
    r"\bidentifica[cç][aã]o\s+completa\b|"
    r"\bvolume\s+n[aã]o\s+aparece\b|"
    r"\b(?:entry\s+of|entrada\s+de)\s+teste\b|"
    r"\bdata\s+(?:of|de|do)\s+julgamento\b|"
    r"\bsuplemento\s+n[aã]o\s+est[aá]\s+posicionado\b|"
    r"\bc[oó]digo\s+mudou\s+de\s+fam[ií]lia\b|"
    r"\bn[uú]mero\s+de\s+linha\b|"
    r"\blinha\s+numerada\b|"
    r"\bsequ[eê]ncia\s+numerada\b|"
    r"\bsem\s+numera[cç][aã]o\b|"
    r"\bdeveria\s+tornar\b|"
    r"\bwarning\s+ou\s+overflow\s+n[aã]o\s+reconhecido\b|"
    r"\bficha\s+(?:externa|desabilitada)\b|"
    r"\bmarker\s+textual\b.*\bduplicad[oa]\b|"
    r"\bp[oó]s-textua(?:l|is)\b|"
    r"\biniciou\s+in\s+the\s+verso\b|"
    r"\bcalibra[cç][aã]o\s+for\b|"
    r"\btipografia\s+(?:e|and)\s+geometria\b)",
    re.IGNORECASE,
)
RETIRED_PROFILE_IDS = re.compile(
    r"(?<![A-Za-z0-9_-])(?:tccgraduacao|tccespecializacao|dissertacao|tese|"
    r"projetoanonimizado|projeto)(?![A-Za-z0-9_-])"
)
MACHINE_JSON_FILES = (
    "standards/catalog.json",
    "standards/coverage-rules-frontmatter.json",
    "standards/coverage-rules-project.json",
    "standards/frontmatter-approval-scenario.json",
    "standards/frontmatter-cover-scenario.json",
)
MACHINE_SOURCE_FILES = (
    "tests/checks/normative_frontmatter_title_page.py",
    "tests/integration/frontmatter-approval-evidence.sh",
)
RETIRED_PROFILE_VALUES = {
    "tccgraduacao",
    "tccespecializacao",
    "dissertacao",
    "tese",
    "projeto",
    "projetoanonimizado",
}
ACADEMIC_LITERAL_ALLOWLIST = (
    "SUMÁRIO",
    "REFERÊNCIAS",
    "APÊNDICE",
    "ANEXO",
    "ÍNDICE REMISSIVO",
)


def tracked() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode() for item in output.split(b"\0") if item]


def diagnostic_scopes(lines: list[str]):
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.lstrip()
        if stripped.startswith("#!"):
            index += 1
            continue
        if stripped.startswith(("#", "//", "/*", "* ")):
            yield index + 1, stripped
            index += 1
            continue

        positions = [
            (line.find(marker), marker)
            for marker in DIAGNOSTIC_MARKERS
            if line.find(marker) >= 0
        ]
        if not positions:
            index += 1
            continue
        position, marker = min(positions, key=lambda item: item[0])
        scope_lines = [line[position:]]

        if marker in MULTILINE_MARKERS:
            balance = scope_lines[0].count("(") - scope_lines[0].count(")")
            cursor = index + 1
            while balance > 0 and cursor < len(lines):
                scope_lines.append(lines[cursor])
                balance += lines[cursor].count("(") - lines[cursor].count(")")
                cursor += 1
            index = cursor
        else:
            index += 1

        yield index - len(scope_lines) + 1, "\n".join(scope_lines)


def normalized_diagnostic(scope: str) -> str:
    result = scope
    for literal in ACADEMIC_LITERAL_ALLOWLIST:
        result = result.replace(literal, "")
    return result


def contains_portuguese_engineering_text(scope: str) -> bool:
    normalized = normalized_diagnostic(scope)
    return bool(
        PORTUGUESE_TECHNICAL_TERMS.search(normalized)
        or MIXED_PORTUGUESE_TECHNICAL_PHRASES.search(normalized)
    )


def audit() -> list[str]:
    errors: list[str] = []
    for path in tracked():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix not in SOURCE_SUFFIXES or not rel.startswith(EXECUTABLE_ROOTS):
            continue
        if rel == "tests/checks/engineering_language.py":
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, scope in diagnostic_scopes(lines):
            if contains_portuguese_engineering_text(scope):
                rendered = " ".join(item.strip() for item in scope.splitlines())
                errors.append(
                    f"{rel}:{number}: Portuguese project-owned engineering text: {rendered}"
                )

    def visit_machine_values(value, location: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                visit_machine_values(item, f"{location}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit_machine_values(item, f"{location}[{index}]")
        elif isinstance(value, str) and value in RETIRED_PROFILE_VALUES:
            errors.append(
                f"{location}: retired Portuguese technical profile identifier: {value}"
            )

    for rel in MACHINE_JSON_FILES:
        payload = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        visit_machine_values(payload, rel)
    for rel in MACHINE_SOURCE_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            if RETIRED_PROFILE_IDS.search(line):
                errors.append(
                    f"{rel}:{number}: retired Portuguese technical profile identifier: {line.strip()}"
                )

    api = ROOT / "release/v3-api-migration.json"
    if not api.is_file():
        errors.append("release/v3-api-migration.json: live migration contract is missing")
    for removed in (
        ROOT / "release/v3-test-migration.json",
        ROOT / "release/v3-path-migration.json",
    ):
        if removed.exists():
            errors.append(
                f"{removed.relative_to(ROOT)}: closed unconsumed migration contract remains active"
            )
    for consumer in (
        "tests/checks/v3_api_residual.py",
        "tests/checks/profile_matrix_contract.py",
    ):
        if "release/v3-api-migration.json" not in (ROOT / consumer).read_text(
            encoding="utf-8"
        ):
            errors.append(
                f"{consumer}: expected live API migration contract consumer is missing"
            )
    return errors


def self_test() -> None:
    portuguese_lines = [
        "grep -Fq 'REFERÊNCIAS' x || echo 'Auditoria falhou: evidência ausente.'"
    ]
    portuguese = list(diagnostic_scopes(portuguese_lines))[0][1]
    assert contains_portuguese_engineering_text(portuguese)

    mixed_lines = [
        "grep -Fq 'Referências' x || echo 'References missing from the table of contents.'"
    ]
    mixed = list(diagnostic_scopes(mixed_lines))[0][1]
    assert not contains_portuguese_engineering_text(mixed)

    multiline = [
        "    raise SystemExit(",
        "        f'Validation falhou: página não localizada.'",
        "    )",
    ]
    multiline_scope = list(diagnostic_scopes(multiline))[0][1]
    assert contains_portuguese_engineering_text(multiline_scope)

    false_negative_cases = (
        "echo \"$job: initial-page was not preserved após a cover.\"",
        "raise SystemExit(f'{job}: identificação completa of the curso missing of the cover.')",
        "raise SystemExit('NBR 6023:2025: suplemento não está posicionado após a data.')",
        "raise SystemExit('código mudou de família.')",
        "raise SystemExit('número de linha duplicado 2')",
        "raise SystemExit('linha numerada vazia: 2')",
        "echo 'page lógica textual inesperada'",
        "raise SystemExit('expected title and text in 3 pages físicas')",
        "raise SystemExit('ficha externa foi incluída although disabled')",
        "echo 'Pós-textuais duplex contêm warning.'",
        "echo 'Calibração for vector geometry gate completed.'",
    )
    for line in false_negative_cases:
        scope = list(diagnostic_scopes([line]))[0][1]
        assert contains_portuguese_engineering_text(scope)

    academic = list(diagnostic_scopes(["echo 'Expected rendered heading: SUMÁRIO'"]))[0][1]
    assert not contains_portuguese_engineering_text(academic)

    assert RETIRED_PROFILE_IDS.search('\"profile\": \"tccgraduacao\"')
    assert not RETIRED_PROFILE_IDS.search('\"profile\": \"undergraduate-capstone\"')
    normative = json.loads('{"requirement":"A capa é elemento obrigatório."}')
    assert "obrigatório" in normative["requirement"]
    print("ENGINEERING-LANGUAGE-SELFTEST status=PASS cases=18")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enforce project-owned engineering language boundaries."
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    errors = audit()
    if errors:
        print("Engineering language contract failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(
            f"Engineering language contract failed with {len(errors)} issue(s)."
        )
    print(
        "ENGINEERING-LANGUAGE-EVIDENCE status=PASS "
        "portuguese_technical_diagnostics=0 retired_profile_ids=0 "
        "closed_unconsumed_contracts=0 live_api_contract_consumers=2"
    )


if __name__ == "__main__":
    main()
