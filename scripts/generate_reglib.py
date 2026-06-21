#!/usr/bin/env python3
"""Generate a Lean Reglib directory from enriched rules JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROMAN = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
    "XI": 11,
    "XII": 12,
}

# Set by main() before generation; gates ICDR-specific behaviour
_ACTIVE_FRAMEWORK: str = "SEBI_ICDR_2018"


def load_definitions(path: str) -> list[dict]:
    """Load definition records JSONL (Regulation 2 sub-clauses)."""
    defs: list[dict] = []
    p = Path(path)
    if not p.exists():
        return defs
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                print(f"[WARN] definitions JSON parse failed at line {i}: {e}", file=sys.stderr)
                continue
            if isinstance(rec, dict):
                defs.append(rec)
    return defs


def load_rules(path: str) -> list[dict]:
    rules: list[dict] = []
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                print(f"[WARN] JSON parse failed at line {i}: {e}", file=sys.stderr)
                continue
            if isinstance(rec, dict):
                rules.append(rec)
    return rules


def chapter_part_key(rule: dict) -> tuple[str, str]:
    chapter = (rule.get("chapter") or {}).get("number") if isinstance(rule.get("chapter"), dict) else None
    part = (rule.get("part") or {}).get("number") if isinstance(rule.get("part"), dict) else None
    reg_num = str(rule.get("regulation_number", "") or "")
    m = re.match(r"(\d+)", reg_num)
    reg_top = int(m.group(1)) if m else None

    # Data hygiene override: Regulations 4-23 are always Chapter II in ICDR 2018.
    # Do NOT apply this override for other frameworks (e.g. ITA_1961).
    if _ACTIVE_FRAMEWORK == "SEBI_ICDR_2018" and reg_top is not None and 4 <= reg_top <= 23:
        chapter = "II"

    return str(chapter or "II"), str(part or "I")


def part_file_name(chapter_number: str, part_number: str) -> str:
    ch = ROMAN.get(str(chapter_number), chapter_number)
    pt = ROMAN.get(str(part_number), part_number)
    ch_safe = re.sub(r"[^a-zA-Z0-9]", "_", str(ch))
    pt_safe = re.sub(r"[^a-zA-Z0-9]", "_", str(pt))
    return f"Chapter{ch_safe}_Part{pt_safe}"


def _lean_slug(s: str) -> str:
    """Sanitize chapter/part tokens for Lean identifiers (no hyphens)."""
    return re.sub(r"[^a-zA-Z0-9]", "_", str(s))


def sanitize_def_name(rule_id: str) -> str:
    name = str(rule_id or "").lower().replace("icdr_", "reg_").replace("ita_", "reg_")
    name = re.sub(r"[^a-z0-9_]", "_", name)
    return name.strip("_")


def lean_field_name(field: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(field or "")).strip("_").lower()


def definition_lean_type(lean_type_hint: str, maps_to_field: str) -> str:
    """Map definition lean_type_hint to a Lean field type."""
    h = str(lean_type_hint or "String").strip()
    f = lean_field_name(maps_to_field)
    if h == "Bool":
        return "Bool"
    if h == "Nat":
        return "Nat"
    if h == "String":
        return "String"
    if h == "Inductive":
        if "security" in f:
            return "SecurityType"
        return "IssueType"
    if h == "Structure":
        if f == "promoter" or "promoter" in f:
            return "Promoter"
        return "Issuer"
    return "String"


def inductive_lean_type_name(term: str) -> str:
    """PascalCase Lean type name from a statutory term (e.g. 'specified securities' -> SpecifiedSecurities)."""
    words = re.sub(r"[^a-zA-Z0-9\s]", " ", term or "").split()
    return "".join(w.capitalize() for w in words if w) or "UnknownInductive"


# Merged into canonical SpecifiedSecurities / IssueType (not separate inductives).
_MERGED_INDUCTIVE_RULE_IDS = frozenset({
    "ICDR_2_eee",
    "ICDR_2_eeea",
    "ICDR_2_h",
    "ICDR_2_rr",
})

# Issuer uses specified_securities_type instead of per-definition inductive fields.
_ISSUER_CANONICAL_TYPE_FIELDS = frozenset({
    "specified_securities",
    "sr_equity_shares",
})


def _emit_canonical_inductive_types() -> list[str]:
    """Hardcoded Reg 2 inductives that subsume several JSONL definitions."""
    return [
        "/-! ## Inductive Types — grounded in Reg 2 statutory definitions -/",
        "",
        "/-- Reg 2(eee), 2(eeea): specified securities -/",
        "inductive SpecifiedSecurities where",
        "  | equityShares          -- Reg 2(eee)",
        "  | convertibleSecurities -- Reg 2(eee)",
        "  | srEquityShares        -- Reg 2(eeea): superior voting rights",
        "deriving Repr, DecidableEq",
        "",
        "/-- Combined issue type — Reg 2(w),(q),(h),(xx),(nn),(tt) -/",
        "inductive IssueType where",
        "  | initialPublicOffer  -- Reg 2(w)",
        "  | furtherPublicOffer  -- Reg 2(q)",
        "  | compositeIssue      -- Reg 2(h): public-cum-rights simultaneously",
        "  | rightsIssue         -- Reg 2(xx)",
        "  | preferentialIssue   -- Reg 2(nn)",
        "  | qualifiedPlacement  -- Reg 2(tt)",
        "deriving Repr, DecidableEq",
        "",
    ]


def best_lean_type(field: str, type_hint: str) -> str:
    f = str(field or "").lower()
    t = str(type_hint or "")

    if t == "Bool":
        return "Bool"
    if t == "String":
        return "String"
    if "months" in f:
        return "List Months" if t == "List Nat" else "Months"
    if "years" in f:
        return "List Years" if t == "List Nat" else "Years"
    if t in ("Nat", "List Nat") and any(k in f for k in ["pct", "ratio", "min", "max"]):
        return "Nat"
    if t in ("Nat", "List Nat") and any(k in f for k in ["crore", "worth", "profit", "assets", "value", "threshold", "cost"]):
        return "INR_Crore" if t == "Nat" else "List INR_Crore"
    if t == "List Nat":
        return "List INR_Crore"
    if t == "Nat":
        return "Nat"
    return t or "Bool"


def default_value(field: str, type_hint: str) -> str:
    f = str(field or "").lower()
    t = str(type_hint or "")
    if t == "Bool" and any(k in f for k in ["debarred", "defaulter", "fugitive", "outstanding", "pledged", "wilful", "fraudulent"]):
        return "false"
    if t == "Bool":
        return "true"
    if t == "String":
        return '"direct"'
    if t == "List Nat":
        return "[10, 12, 15]"
    if "pct" in f or "ratio" in f:
        return "20"
    if "months" in f:
        return "12"
    if "years" in f:
        return "1"
    if any(k in f for k in ["crore", "worth", "profit", "assets"]):
        return "10"
    return "1"


def reg_sort_key(reg_str: str) -> tuple[int, str]:
    m = re.match(r"(\d+)", str(reg_str or ""))
    return (int(m.group(1)) if m else 10**9, str(reg_str or ""))


def _iter_maps_to(rule: dict) -> list[dict]:
    mt = rule.get("maps_to", [])
    if isinstance(mt, list):
        return [x for x in mt if isinstance(x, dict)]
    return []


def generate_core_lean(
    rules: list[dict],
    framework: str,
    def_by_field: dict[str, dict] | None = None,
    defs: list[dict] | None = None,
    subdir: str = "ICDR",
    struct_name: str = "Issuer",
) -> str:
    """Generate definitions/Core.lean.

    If def_by_field is provided (from definitions JSONL), type hints are grounded
    in Reg 2 statutory definitions instead of reverse-engineered from maps_to.
    """
    def_by_field = def_by_field or {}
    defs = defs or []

    fields: dict[str, dict] = {}
    for rule in rules:
        reg = rule.get("regulation_number", rule.get("rule_id", ""))
        for m in rule.get("maps_to") or []:
            field = lean_field_name(m.get("field", ""))
            if not field or field in fields:
                continue
            if field in def_by_field:
                type_hint = def_by_field[field]["lean_type_hint"]
                source_reg = def_by_field[field]["regulation_number"]
                source_note = f"Reg {source_reg} (statutory definition)"
            else:
                type_hint = m.get("type_hint", "Bool")
                source_reg = reg
                source_note = f"Reg {reg} (maps_to inference)"
            fields[field] = {
                "type_hint": type_hint,
                "rule_id": rule.get("rule_id", ""),
                "reg": source_reg,
                "note": source_note,
                "text": rule.get("text", "")[:80],
            }

    lines = [
        f"-- Reglib/{subdir}/definitions/Core.lean",
        f"-- Core regulatory types for {framework}",
        f"-- Auto-generated by generate_reglib.py",
        f"-- Sources: rules JSONL + definitions JSONL (Reg 2 statutory definitions)",
        f"-- DO NOT EDIT MANUALLY — re-run the generator after updating either JSONL",
        f"",
        f"namespace Reglib.{subdir}",
        f"",
    ]

    lines += [
        "/-! ## Primitive Type Aliases -/",
        "",
        "/-- Indian Rupee amount in crore (1 crore = 10 million) -/",
        "abbrev INR_Crore := Nat",
        "",
        "/-- Percentage value as integer (0–100) -/",
        "abbrev Pct := Nat",
        "",
        "/-- Duration in months -/",
        "abbrev Months := Nat",
        "",
        "/-- Duration in years -/",
        "abbrev Years := Nat",
        "",
    ]

    if subdir == "ICDR":
        lines += _emit_canonical_inductive_types()

        if defs:
            for d in sorted(defs, key=lambda x: x.get("sub_clause", "")):
                if d.get("lean_type_hint") != "Inductive":
                    continue
                if d.get("rule_id", "") in _MERGED_INDUCTIVE_RULE_IDS:
                    continue

                constructors = d.get("constructors", [])
                if not constructors:
                    lines.append(f"-- TODO: add constructors for {d['rule_id']} ({d['term']})")
                    lines.append(f"-- definition_text: {d.get('definition_text', '')[:80]}")
                    lines.append("")
                    continue

                type_name = inductive_lean_type_name(d.get("term", ""))
                reg = d.get("regulation_number", "")
                term = d.get("term", "")

                lines.append(f"/-- Reg {reg}: {term} -/")
                lines.append(f"inductive {type_name} where")
                for c in constructors:
                    lines.append(f"  | {c}")
                lines.append("deriving Repr, DecidableEq")
                lines.append("")

        lines += [
            "/-! ## Promoter — Reg 2(oo) -/",
            "",
            "/-- A person included as promoter under any limb of Reg 2(oo)(i–iii) -/",
            "structure Promoter where",
            "  /-- Reg 2(oo)(i): named in offer doc or annual return (s.92 Companies Act) -/",
            "  named_in_offer_doc                : Bool",
            "  /-- Reg 2(oo)(ii): control as shareholder/director/otherwise -/",
            "  has_control                       : Bool",
            "  /-- Reg 2(oo)(iii): board accustomed to act on their advice -/",
            "  board_acts_on_instructions        : Bool",
            "  /-- Reg 2(oo) proviso: professional capacity only → excluded from promoter status -/",
            "  acting_only_professionally        : Bool",
            "  holding_pct                       : Pct",
            "  is_debarred                       : Bool",
            "  /-- Reg 2(lll) -/",
            "  is_wilful_defaulter_or_fraudulent : Bool",
            "  /-- Reg 2(p) -/",
            "  is_fugitive_economic_offender     : Bool",
            "deriving Repr",
            "",
        ]

    struct_heading = (
        "/-! ## Issuer — Reg 2(aa) -/"
        if struct_name == "Issuer"
        else f"/-! ## {struct_name} -/"
    )
    struct_doc = (
        '/-- "a company or a body corporate authorized to issue specified securities" -/'
        if struct_name == "Issuer"
        else f"/-- Primary entity struct for {framework} compliance checks -/"
    )
    lines += [
        struct_heading,
        "",
        struct_doc,
        f"structure {struct_name} where",
    ]

    SKIP_FIELDS = {"issuer", "promoter", "promoter_group", "taxpayer", "assessee"}
    INR_FIELDS = {
        "net_worth",
        "net_tangible_assets",
        "issue_size",
        "paid_up_capital",
        "distributable_profits",
    }

    for field, info in sorted(fields.items()):
        if field in SKIP_FIELDS or field in _ISSUER_CANONICAL_TYPE_FIELDS:
            continue
        hint = info["type_hint"]
        lt = best_lean_type(field, hint)
        if field in def_by_field and def_by_field[field].get("lean_type_hint") == "Inductive":
            ctors = def_by_field[field].get("constructors") or []
            if ctors:
                lt = inductive_lean_type_name(def_by_field[field].get("term", ""))
        if field in INR_FIELDS and lt == "Nat":
            lt = "INR_Crore"
        note = info.get("note", "")
        lines.append(f"  /-- {note} -/")
        lines.append(f"  {field:<48s} : {lt}")

    if subdir == "ICDR":
        lines += [
            "  /-- What kind of issue this filing is for -/",
            "  issue_type                                         : IssueType",
            "  /-- Type of securities being issued — Reg 2(eee) -/",
            "  specified_securities_type                          : SpecifiedSecurities",
            "  /-- Reg 2(oo) -/",
            "  promoters                                          : List Promoter",
        ]
    lines += [
        "deriving Repr",
        "",
        f"end Reglib.{subdir}",
    ]

    return "\n".join(lines)


def _top_reg(rule_id: str) -> str:
    s = str(rule_id or "")
    m = re.match(r"ICDR_(\d+)", s)
    if m:
        return m.group(1)
    m = re.match(r"ITA_([0-9]+[a-z]?)", s, re.I)
    return m.group(1).lower() if m else ""


def _is_proviso_or_explanation(rule_id: str) -> bool:
    s = str(rule_id or "").lower()
    return ("proviso" in s) or ("explanation" in s)


def _rule_body(rule: dict) -> str:
    maps = _iter_maps_to(rule)
    if not maps:
        return "sorry  -- TODO: no fields extracted"

    text_l = str(rule.get("text", "") or "").lower()
    parts: list[str] = []
    for m in maps:
        raw = m.get("field", "")
        field = lean_field_name(raw)
        if not field:
            continue
        hint = str(m.get("type_hint", "") or "")
        if hint == "Bool":
            neg = any(k in text_l for k in [
                "shall not", "not be eligible", "debarred", "defaulter",
                "fugitive", "pledged", "prohibited",
            ])
            parts.append(f"issuer.{field} = {'false' if neg else 'true'}")
        elif hint == "List Nat":
            n = 3
            m_year = re.search(r"preceding\s+(\d+)\s+years", text_l)
            if m_year:
                try:
                    n = int(m_year.group(1))
                except Exception:
                    n = 3
            parts.append(f"(issuer.{field}.length = {n} ∧ issuer.{field}.all (· ≥ 1))")
        elif hint == "Nat":
            parts.append(f"issuer.{field} ≥ 0  -- TODO: set correct threshold")
        elif hint == "String":
            parts.append(f'issuer.{field} ≠ ""')
        else:
            parts.append(f"issuer.{field} = issuer.{field}")

    return "\n  ∧ ".join(parts) if parts else "sorry  -- TODO: unmapped"


def _dedupe_rules_by_def_name(group: list[dict]) -> list[dict]:
    """Keep one rule per Lean def name; prefer entries with maps_to and longer text."""
    by_dname: dict[str, dict] = {}
    for r in group:
        dname = sanitize_def_name(str(r.get("rule_id", "") or ""))
        existing = by_dname.get(dname)
        if existing is None:
            by_dname[dname] = r
            continue

        def _score(rule: dict) -> tuple[int, int]:
            return (len(_iter_maps_to(rule)), len(str(rule.get("text", "") or "")))

        if _score(r) > _score(existing):
            by_dname[dname] = r
    return list(by_dname.values())


def generate_rules_lean(
    rules: list[dict],
    chapter: str,
    part: str,
    part_title: str,
    file_name: str,
    subdir: str = "ICDR",
    struct_name: str = "Issuer",
) -> str:
    filtered = [r for r in rules if chapter_part_key(r) == (chapter, part)]
    regs: dict[str, list[dict]] = defaultdict(list)
    for r in filtered:
        regs[_top_reg(r.get("rule_id", ""))].append(r)

    ch_int = ROMAN.get(chapter, chapter)
    pt_int = ROMAN.get(part, part)
    ch_slug = _lean_slug(ch_int)
    pt_slug = _lean_slug(pt_int)

    lines: list[str] = []
    lines.append(f"-- Auto-generated rules file: {file_name}.lean")
    lines.append(f"-- Chapter {chapter}, Part {part}: {part_title}")
    lines.append("")
    lines.append(f"import Reglib.{subdir}.definitions.Core")
    lines.append("")
    lines.append(f"namespace Reglib.{subdir}.Rules")
    lines.append("")
    lines.append(f"open Reglib.{subdir}")
    lines.append("")

    composite_regs: list[str] = []
    for reg in sorted(regs.keys(), key=lambda x: int(x) if str(x).isdigit() else 10**9):
        if not reg:
            continue
        lines.append(f"/-! ## Regulation {reg} -/")
        group = _dedupe_rules_by_def_name(regs[reg])
        def_names: list[str] = []
        for r in sorted(group, key=lambda x: str(x.get("rule_id", ""))):
            rid = str(r.get("rule_id", "") or "")
            dname = sanitize_def_name(rid)
            def_names.append(dname)
            text = re.sub(r"\s+", " ", str(r.get("text", "") or "")).strip()
            lines.append(f"/-- Reg {r.get('regulation_number', '')}: {text[:120]}... -/")
            lines.append(f"def {dname} (issuer : {struct_name}) : Prop :=")
            lines.append(f"  {_rule_body(r)}")
            lines.append("")

        eligible_defs = [
            sanitize_def_name(str(r.get("rule_id", "") or ""))
            for r in group
            if _iter_maps_to(r) and not _is_proviso_or_explanation(r.get("rule_id", ""))
        ]
        if len(eligible_defs) >= 2:
            gate = f"reg_{reg}_eligible"
            composite_regs.append(gate)
            lines.append(f"/-- Combined Regulation {reg} gate -/")
            lines.append(f"def {gate} (issuer : {struct_name}) : Prop :=")
            lines.append("  " + "\n  ∧ ".join(f"{d} issuer" for d in eligible_defs))
            lines.append("")

    lines.append(f"/-! ## Composite Chapter {chapter} Part {part} Gate -/")
    lines.append("")
    lines.append(f"def chapter{ch_slug}_part{pt_slug}_eligible (issuer : {struct_name}) : Prop :=")
    if composite_regs:
        lines.append("  " + "\n  ∧ ".join(f"{g} issuer" for g in composite_regs))
    else:
        lines.append("  True")
    lines.append("")
    lines.append(f"end Reglib.{subdir}.Rules")
    lines.append("")
    return "\n".join(lines)


def generate_compliance_lean(
    rules: list[dict],
    part_files: list[str],
    defs: list[dict] | None = None,
    subdir: str = "ICDR",
    struct_name: str = "Issuer",
    instance_name: str = "sample_compliant_issuer",
) -> str:
    field_types: dict[str, str] = {}
    for r in rules:
        for m in _iter_maps_to(r):
            f = lean_field_name(m.get("field", ""))
            if f and f not in field_types:
                field_types[f] = str(m.get("type_hint", "") or "Nat")

    lines: list[str] = []
    lines.append("-- Auto-generated compliance gate file.")
    lines.append("")
    for pf in part_files:
        lines.append(f"import Reglib.{subdir}.rules.{pf}")
    lines.append(f"import Reglib.{subdir}.definitions.Core")
    lines.append("")
    lines.append(f"namespace Reglib.{subdir}.Rules")
    lines.append(f"open Reglib.{subdir}")
    lines.append("")
    gate_title = "Full IPO Compliance Gate" if subdir == "ICDR" else "Full Compliance Gate"
    lines.append(f"/-! ## {gate_title} -/")
    lines.append("")
    lines.append(f"def compliance_eligible (issuer : {struct_name}) : Prop :=")
    gates = []
    for pf in part_files:
        m = re.match(r"Chapter(.+)_Part(.+)", pf)
        if m:
            gates.append(f"chapter{m.group(1)}_part{m.group(2)}_eligible issuer")
    lines.append("  " + ("\n  ∧ ".join(gates) if gates else "True"))
    lines.append("")
    sample_heading = (
        "Sample Compliant Issuer" if struct_name == "Issuer" else f"Sample {struct_name}"
    )
    lines.append(f"/-! ## {sample_heading} -/")
    lines.append("")
    lines.append(f"def {instance_name} : {struct_name} := {{")
    for f in sorted(field_types.keys()):
        lines.append(f"  {f} := {default_value(f, field_types[f])},")
    if subdir == "ICDR":
        lines.append("  issue_type := IssueType.initialPublicOffer,")
        lines.append("  specified_securities_type := SpecifiedSecurities.equityShares,")
        lines.append("  promoters := [")
        lines.append("    { named_in_offer_doc := true")
        lines.append("      has_control := true")
        lines.append("      board_acts_on_instructions := false")
        lines.append("      acting_only_professionally := false")
        lines.append("      holding_pct := 25")
        lines.append("      is_debarred := false")
        lines.append("      is_wilful_defaulter_or_fraudulent := false")
        lines.append("      is_fugitive_economic_offender := false }")
        lines.append("  ]")
    lines.append("}")
    lines.append("")
    lines.append("/-! ## Smoke-Test Proofs -/")
    lines.append("")
    # Smoke-test theorem — ICDR only (the ITA equivalent is in TaxProbe.lean)
    if subdir == "ICDR":
        lines.append("theorem sample_passes_reg5 :")
        lines.append(f"    reg_5_eligible {instance_name} := by")
        lines.append(
            "  unfold reg_5_eligible reg_5_1_a reg_5_1_b reg_5_1_c reg_5_1_d reg_5_2"
        )
        lines.append(f"  simp [{instance_name}]")
    lines.append("")
    lines.append(f"end Reglib.{subdir}.Rules")
    lines.append("")
    return "\n".join(lines)


def generate_root_import(part_files: list[str], subdir: str = "ICDR") -> str:
    lines = [
        "-- Reglib.lean",
        "-- Root import -- auto-generated by generate_reglib.py",
        "",
        f"import Reglib.{subdir}.definitions.Core",
    ]
    for pf in part_files:
        lines.append(f"import Reglib.{subdir}.rules.{pf}")
    lines.append(f"import Reglib.{subdir}.rules.Compliance")
    lines.append("")
    return "\n".join(lines)


def generate_lakefile(include_copilot: bool = False) -> str:
    if include_copilot:
        return """-- Reglib/lakefile.lean
import Lake
open Lake DSL

package Reglib where
  moreLinkArgs := #[
    "-L./.lake/packages/LeanCopilot/.lake/build/lib",
    "-lctranslate2",
  ]

require LeanCopilot from git
  "https://github.com/lean-dojo/LeanCopilot" @ "main"

@[default_target]
lean_lib Reglib where
  roots := #[`Reglib]

lean_lib CopilotProbe where
  roots := #[`Reglib.ICDR.CopilotProbe]
  moreLinkArgs := #[
    "-L./.lake/packages/LeanCopilot/.lake/build/lib",
    "-lctranslate2",
  ]
"""
    return """-- Reglib/lakefile.lean
import Lake
open Lake DSL

package Reglib where

@[default_target]
lean_lib Reglib where
  roots := #[`Reglib]
"""


def write_text(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        print(f"[SKIP] {path}", file=sys.stderr)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"[WRITE] {path}", file=sys.stderr)
    return True


def _part_sort_key(k: tuple[str, str]) -> tuple[int, int, str, str]:
    ch, pt = k
    ch_i = int(ROMAN.get(ch, 999)) if str(ROMAN.get(ch, "")).isdigit() else 999
    pt_i = int(ROMAN.get(pt, 999)) if str(ROMAN.get(pt, "")).isdigit() else 999
    return ch_i, pt_i, ch, pt


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Reglib Lean files from enriched JSONL rules.")
    ap.add_argument("--rules", required=True, help="Path to enriched rules JSONL file")
    ap.add_argument(
        "--defs",
        type=str,
        default="",
        help="Path to definitions JSONL (definitions_icdr_reg2.jsonl). "
             "When provided, type hints in Core.lean are grounded in Reg 2 "
             "statutory definitions instead of reverse-engineered from maps_to.",
    )
    ap.add_argument("--out-dir", default="Reglib", help="Root output directory for the Lean library")
    ap.add_argument("--framework", default="SEBI_ICDR_2018", help="Regulation framework identifier string")
    ap.add_argument("--year", default="2018", help="Regulation year used as subdirectory name")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files (default: skip if exists)")
    ap.add_argument(
        "--with-copilot",
        action="store_true",
        help="Emit lakefile with LeanCopilot + CopilotProbe targets (main Reglib only)",
    )
    ap.add_argument(
        "--subdir",
        default="ICDR",
        help="Subdirectory name under Reglib/ for definitions and rules (default: ICDR). "
             "Use ITA for Income Tax Act.",
    )
    ap.add_argument(
        "--struct-name",
        default="Issuer",
        help="Name of the Lean struct type (default: Issuer). Use Taxpayer for ITA.",
    )
    ap.add_argument(
        "--instance-name",
        default="sample_compliant_issuer",
        help="Name of the sample instance (default: sample_compliant_issuer). "
             "Use sample_taxpayer for ITA.",
    )
    args = ap.parse_args()

    # Set the active framework so chapter_part_key behaves correctly
    global _ACTIVE_FRAMEWORK
    _ACTIVE_FRAMEWORK = args.framework

    rules = load_rules(args.rules)

    defs: list[dict] = []
    if args.defs:
        defs_path = Path(args.defs)
        if not defs_path.exists():
            print(f"[WARN] --defs path not found: {defs_path}", file=sys.stderr)
        else:
            defs = load_definitions(str(defs_path))
            print(f"[INFO] Loaded {len(defs)} definitions from {defs_path}", file=sys.stderr)

    def_by_field: dict[str, dict] = {}
    for d in defs:
        field = (d.get("maps_to_field") or "").strip()
        if field:
            def_by_field[lean_field_name(field)] = d

    def_by_term: dict[str, dict] = {}
    for d in defs:
        term = (d.get("term") or "").strip().lower()
        if term:
            def_by_term[term] = d
    out_dir = Path(args.out_dir)
    lib_dir = out_dir / "Reglib"
    definitions_dir = lib_dir / args.subdir / "definitions"
    rules_dir       = lib_dir / args.subdir / "rules"
    lib_dir.mkdir(parents=True, exist_ok=True)
    definitions_dir.mkdir(parents=True, exist_ok=True)
    rules_dir.mkdir(parents=True, exist_ok=True)

    subdir        = args.subdir
    struct_name   = args.struct_name
    instance_name = args.instance_name

    writes = 0
    writes += int(
        write_text(
            definitions_dir / "Core.lean",
            generate_core_lean(
                rules, args.framework,
                def_by_field=def_by_field, defs=defs,
                subdir=subdir, struct_name=struct_name,
            ),
            args.overwrite,
        )
    )

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    titles: dict[tuple[str, str], str] = {}
    for r in rules:
        key = chapter_part_key(r)
        groups[key].append(r)
        part_title = (r.get("part") or {}).get("title") if isinstance(r.get("part"), dict) else ""
        if key not in titles:
            titles[key] = str(part_title or "")

    part_files: list[str] = []
    for key in sorted(groups.keys(), key=_part_sort_key):
        ch, pt = key
        fname = part_file_name(ch, pt)
        part_files.append(fname)
        content = generate_rules_lean(
            rules, ch, pt, titles.get(key, ""), fname,
            subdir=subdir, struct_name=struct_name,
        )
        writes += int(write_text(rules_dir / f"{fname}.lean", content, args.overwrite))

    # If overwriting, remove stale Chapter*_Part*.lean files not regenerated this run.
    if args.overwrite:
        keep = {f"{name}.lean" for name in part_files}
        for old in rules_dir.glob("Chapter*_Part*.lean"):
            if old.name not in keep:
                old.unlink(missing_ok=True)
                print(f"[WRITE] removed stale {old}", file=sys.stderr)

    compliance = generate_compliance_lean(
        rules, part_files, defs=defs,
        subdir=subdir, struct_name=struct_name, instance_name=instance_name,
    )
    writes += int(write_text(rules_dir / "Compliance.lean", compliance, args.overwrite))

    root_import = generate_root_import(part_files, subdir=subdir)
    writes += int(write_text(out_dir / "Reglib.lean", root_import, args.overwrite))
    if args.with_copilot or out_dir.name != "Reglib_gold":
        writes += int(
            write_text(
                out_dir / "lakefile.lean",
                generate_lakefile(include_copilot=args.with_copilot),
                args.overwrite,
            )
        )

    if out_dir.name == "Reglib_gold" and args.overwrite:
        # Pantograph (LeanDojo-v2 prover) requires this toolchain version.
        writes += int(
            write_text(
                out_dir / "lean-toolchain",
                "leanprover/lean4:v4.29.1\n",
                overwrite=True,
            )
        )

    print(
        f"[DONE] Processed {len(rules)} rules"
        + (f", {len(defs)} definitions" if defs else "")
        + f"; wrote {writes} files.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

