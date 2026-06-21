#!/usr/bin/env python3
"""Patch 3 missing Reg 2 definitions into definitions_icdr_reg2.jsonl."""

import json
from pathlib import Path
from datetime import datetime

PATCHES = [
    {
        "rule_id": "ICDR_2_oa",
        "sub_clause": "oa",
        "term": "financial year",
        "definition_text": (
            "shall have the same meaning as assigned to it under "
            "sub-section (41) of section 2 of the Companies Act, 2013"
        ),
        "lean_type_hint": "Nat",
        "cross_references": ["section 2(41) of the Companies Act, 2013"],
        "maps_to_field": "financial_year",
        "regulation_number": "2(oa)",
        "domain": "SEBI_ICDR",
        "regulation_framework": "SEBI_ICDR_2018",
        "status": "accepted",
        "confidence": 1.0,
        "notes": "Inserted by 2025 amendment; manually patched post-extraction",
        "source": {"pdf": "SEBI_ICDR_2018_definitions.pdf", "reg": "2(oa)"},
    },
    {
        "rule_id": "ICDR_2_bbbb",
        "sub_clause": "bbbb",
        "term": "senior management",
        "definition_text": (
            "shall mean the officers and personnel of the issuer who are members "
            "of its core management team, excluding the Board of Directors, and "
            "shall also comprise all the members of the management one level below "
            "the Chief Executive Officer or Managing Director or Whole Time Director "
            "or Manager (including Chief Executive Officer and Manager, in case they "
            "are not part of the Board of Directors) and shall specifically include "
            "the functional heads, by whatever name called and the Company Secretary "
            "and the Chief Financial Officer"
        ),
        "lean_type_hint": "Structure",
        "cross_references": [],
        "maps_to_field": "senior_management",
        "regulation_number": "2(bbbb)",
        "domain": "SEBI_ICDR",
        "regulation_framework": "SEBI_ICDR_2018",
        "status": "accepted",
        "confidence": 1.0,
        "notes": "Inserted by 2023 amendment; manually patched post-extraction",
        "source": {"pdf": "SEBI_ICDR_2018_definitions.pdf", "reg": "2(bbbb)"},
    },
    {
        "rule_id": "ICDR_2_eeea",
        "sub_clause": "eeea",
        "term": "SR equity shares",
        "definition_text": (
            "means the equity shares of an issuer having superior voting rights "
            "compared to all other equity shares issued by that issuer"
        ),
        "lean_type_hint": "Inductive",
        "cross_references": [],
        "maps_to_field": "sr_equity_shares",
        "regulation_number": "2(eeea)",
        "domain": "SEBI_ICDR",
        "regulation_framework": "SEBI_ICDR_2018",
        "status": "accepted",
        "confidence": 1.0,
        "notes": "Inserted by Third Amendment Regulations 2019; manually patched",
        "source": {"pdf": "SEBI_ICDR_2018_definitions.pdf", "reg": "2(eeea)"},
    },
]


def main():
    path = Path("data/processed/definitions_icdr_reg2.jsonl")
    assert path.exists(), f"Not found: {path}"

    existing = []
    existing_ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            existing.append(d)
            existing_ids.add(d["rule_id"])

    ts = datetime.utcnow().isoformat() + "Z"
    added = 0
    for patch in PATCHES:
        if patch["rule_id"] in existing_ids:
            print(f"[SKIP] {patch['rule_id']} already present")
            continue
        patch["extraction_timestamp"] = ts
        patch["extraction_model"] = "manual_patch"
        existing.append(patch)
        existing_ids.add(patch["rule_id"])
        added += 1
        print(f"[ADD]  {patch['rule_id']} — {patch['term']}")

    path.write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in existing) + "\n",
        encoding="utf-8",
    )
    print(f"\n[DONE] {added} patches written. Total definitions: {len(existing)}")


if __name__ == "__main__":
    main()
