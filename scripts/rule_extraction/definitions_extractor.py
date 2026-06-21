"""Pass 1 / Pass 2 extraction for ICDR Regulation 2 statutory definitions."""

from __future__ import annotations

import re
import sys
from typing import Any

from .ollama_client import OllamaClient, coerce_rules_from_parsed

_PASS1_DEFINITIONS_SYSTEM = (
    "You are extracting statutory definitions from an Indian regulatory document (SEBI ICDR).\n"
    "The text contains definition sub-clauses of Regulation 2, typically formatted as:\n"
    '  (a) "advertisement" means ...;\n'
    '  (b) "anchor investor" means ...;\n'
    '  (za) "promoter" means ...;\n\n'
    "Each lettered sub-clause is ONE definition. Return them all as separate entries.\n"
    "Do NOT merge multiple definitions into one object.\n"
    "Ignore footnote citation numbers and footnote definition lines.\n"
    "Return JSON only: {\"definitions\": [{\"sub_clause\": \"a\", \"term\": \"...\", "
    "\"definition_text\": \"...\"}, ...]}\n"
    "If no definitions appear in the text, return {\"definitions\": []}.\n"
)

_PASS1_DEFINITIONS_USER_TEMPLATE = """\
Extract every statutory definition visible in the text below.

For each definition return:
  "sub_clause"       : letter(s) only, e.g. "a", "z", "za", "zb" (no parentheses)
  "term"           : the defined term without surrounding quotes
  "definition_text": full definition text starting from "means" (or equivalent)

Rules:
- Each (a), (b), ... (za) item is a SEPARATE definition — never merge two into one.
- Include definitions that continue from a previous page without repeating the "2." header.
- Skip editorial footnote lines ("Substituted by...", "Inserted by...").
- Return {{"definitions": [...]}} only.

TEXT:
{page_text}
"""

_PASS2_DEFINITIONS_SYSTEM = (
    "You are a legal analyst structuring statutory definitions from Indian securities "
    "regulations. Return valid JSON only — a single object with the requested fields."
)

_PASS2_DEFINITIONS_USER_TEMPLATE = """\
Structure this statutory definition into a typed record.

TERM: {term}
SUB-CLAUSE: {sub_clause}
DEFINITION TEXT: {definition_text}

Output JSON with these fields:
  "rule_id"          : "ICDR_2_{{sub_clause}}" (e.g. "ICDR_2_za" for sub-clause za)
  "term"             : the defined term (without quotes)
  "definition_text"  : full statutory definition text
  "lean_type_hint"   : suggested Lean type for formalization:
                       - "Bool" if the term is a yes/no status or eligibility flag
                       - "Nat"  if the term is a numeric quantity or threshold
                       - "String" if it is a name, label, or free-text identifier
                       - "Structure" if it requires its own Lean struct
                         (e.g. "promoter", "anchor investor")
                       - "Inductive" if it is an enumerated category
                         (e.g. types of securities or issue types)
  "cross_references" : list of regulation numbers referenced in the definition (strings)
  "maps_to_field"    : snake_case field name for Issuer or a sub-struct
                       (e.g. "promoter", "specified_securities", "anchor_investor")
  "notes"            : any ambiguity or multi-part meaning worth flagging (or "")
  "confidence"       : 0.0-1.0
"""


def coerce_definitions_from_parsed(obj: Any) -> list[dict]:
    """Normalize LLM JSON into a list of definition inventory dicts."""
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        if "definitions" in obj and isinstance(obj["definitions"], list):
            return [x for x in obj["definitions"] if isinstance(x, dict)]
        if obj.get("sub_clause") or obj.get("term"):
            return [obj]
    return []


def normalize_sub_clause(raw: str) -> str:
    """'(za)' -> 'za', 'ZA' -> 'za'."""
    s = str(raw or "").strip().lower()
    s = s.strip("()")
    return re.sub(r"[^a-z]", "", s)


def definition_rule_id(sub_clause: str) -> str:
    sc = normalize_sub_clause(sub_clause)
    return f"ICDR_2_{sc}" if sc else "ICDR_2_unknown"


def normalize_term(raw: str) -> str:
    t = str(raw or "").strip()
    t = re.sub(r'^["\']+|["\']+$', "", t)
    return t.strip()


def build_definitions_extraction_prompt(
    term: str,
    sub_clause: str,
    definition_text: str,
) -> str:
    return _PASS2_DEFINITIONS_USER_TEMPLATE.format(
        term=term,
        sub_clause=normalize_sub_clause(sub_clause),
        definition_text=definition_text[:1200],
    )


def identify_definitions(
    client: OllamaClient,
    model: str,
    page_text: str,
    page_nums: list[int],
    carryover_hint: str = "",
    system_prefix: str = "",
    timeout: int = 120,
    debug: bool = False,
) -> list[dict]:
    """Pass 1: list definition sub-clauses in a window."""
    ch = (carryover_hint or "").strip()
    base_user = _PASS1_DEFINITIONS_USER_TEMPLATE.format(page_text=page_text[:8000])
    user = (ch + "\n\n" + base_user) if ch else base_user
    system = f"{system_prefix or ''}{_PASS1_DEFINITIONS_SYSTEM}"

    if debug:
        print(f"[DefPass1] Sending {len(user)} chars, pages={page_nums}", file=sys.stderr)

    try:
        result = client.chat_json_any(model, system, user, timeout=timeout, debug=debug)
    except Exception as e:
        if debug:
            print(f"[DefPass1] model call failed: {e}", file=sys.stderr)
        return []

    items = coerce_definitions_from_parsed(result) if result else []
    out: list[dict] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        sc = normalize_sub_clause(it.get("sub_clause", ""))
        term = normalize_term(it.get("term", ""))
        text = str(it.get("definition_text", "") or "").strip()
        if not sc or not term or not text:
            continue
        out.append(
            {
                "sub_clause": sc,
                "term": term,
                "definition_text": text,
            }
        )

    if debug:
        print(
            f"[DefPass1] pages={page_nums} identified {len(out)} definitions: "
            f"{[d['sub_clause'] for d in out]}",
            file=sys.stderr,
        )
    return out


def structure_definition_record(
    client: OllamaClient,
    model: str,
    inv: dict,
    system_prefix: str = "",
    timeout: int = 120,
    debug: bool = False,
) -> dict | None:
    """Pass 2: structure one definition inventory entry."""
    term = normalize_term(inv.get("term", ""))
    sc = normalize_sub_clause(inv.get("sub_clause", ""))
    text = str(inv.get("definition_text", "") or "").strip()
    if not term or not sc or not text:
        return None

    user = build_definitions_extraction_prompt(term, sc, text)
    system = f"{system_prefix or ''}{_PASS2_DEFINITIONS_SYSTEM}"

    try:
        raw = client.chat_json_any(model, system, user, timeout=timeout, debug=debug)
    except Exception as e:
        if debug:
            print(f"[DefPass2] failed for {sc}: {e}", file=sys.stderr)
        return None

    if not raw or not isinstance(raw, dict):
        return None

    rec = dict(raw)
    rec["sub_clause"] = sc
    rec["rule_id"] = str(rec.get("rule_id") or definition_rule_id(sc))
    rec["term"] = normalize_term(rec.get("term") or term)
    rec["definition_text"] = str(rec.get("definition_text") or text).strip()
    rec.setdefault("lean_type_hint", "String")
    rec.setdefault("cross_references", [])
    rec.setdefault("maps_to_field", "")
    rec.setdefault("notes", "")
    rec.setdefault("confidence", 0.85)

    if not isinstance(rec["cross_references"], list):
        rec["cross_references"] = []
    rec["cross_references"] = [str(x) for x in rec["cross_references"]]

    # Ensure rule_id matches sub_clause
    expected = definition_rule_id(sc)
    if rec["rule_id"] != expected:
        rec.setdefault("repair_notes", []).append(f"rule_id_normalized:{rec['rule_id']}->{expected}")
        rec["rule_id"] = expected

    return rec


def extract_definitions_two_pass(
    client: OllamaClient,
    model: str,
    window_text: str,
    page_nums: list[int],
    carryover_hint: str = "",
    system_prefix: str = "",
    timeout: int = 120,
    debug: bool = False,
) -> tuple[list[dict], list[dict]]:
    """Two-pass definitions extraction for one PDF window."""
    inventory = identify_definitions(
        client,
        model,
        window_text,
        page_nums,
        carryover_hint=carryover_hint,
        system_prefix=system_prefix,
        timeout=timeout,
        debug=debug,
    )
    if not inventory:
        return [], []

    structured: list[dict] = []
    for inv in inventory:
        rec = structure_definition_record(
            client,
            model,
            inv,
            system_prefix=system_prefix,
            timeout=timeout,
            debug=debug,
        )
        if rec:
            structured.append(rec)

    if debug:
        print(
            f"[DefTwoPass] pages={page_nums}: {len(inventory)} inv -> {len(structured)} structured",
            file=sys.stderr,
        )
    return structured, inventory


def validate_definition(rec: dict) -> bool:
    """Minimal schema check for a definition record."""
    rid = str(rec.get("rule_id", "") or "")
    if not re.match(r"^ICDR_2_[a-z]+$", rid):
        return False
    if not str(rec.get("term", "") or "").strip():
        return False
    if len(str(rec.get("definition_text", "") or "").strip()) < 8:
        return False
    hint = str(rec.get("lean_type_hint", "") or "")
    if hint not in ("Bool", "Nat", "String", "Structure", "Inductive"):
        return False
    return True


def attach_definition_source(
    rec: dict,
    pdf_name: str,
    page_nums: list[int],
    sub_clause: str,
) -> dict:
    rec.setdefault("domain", "SEBI_ICDR")
    rec.setdefault("regulation_number", f"2({normalize_sub_clause(sub_clause)})")
    rec.setdefault("status", "accepted")
    if not isinstance(rec.get("source"), dict):
        rec["source"] = {}
    rec["source"].setdefault("pdf", pdf_name)
    rec["source"].setdefault("pages", page_nums)
    rec["source"].setdefault("reg", f"2({normalize_sub_clause(sub_clause)})")
    term = str(rec.get("term", "") or "")
    rec["source"].setdefault("span_hint", " ".join(term.split()[:8]))
    return rec


def sub_clause_sort_key(sc: str) -> tuple[int, str]:
    """Sort a..z, then aa, za, zb."""
    s = normalize_sub_clause(sc)
    if len(s) == 1:
        return (0, s)
    return (1, s)
