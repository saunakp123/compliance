#!/usr/bin/env python3
"""
Post-processing pass: for every definition with lean_type_hint == "Inductive",
call the local LLM to extract a `constructors` list from definition_text and
write it back into the JSONL.

Run after definitions extraction and patching:
    python scripts/add_inductive_constructors.py \
        --defs data/processed/definitions_icdr_reg2.jsonl \
        --model qwen2.5:14b-instruct \
        --debug
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rule_extraction.ollama_client import OllamaClient

_SYSTEM = (
    "You are a Lean 4 type designer working with Indian securities regulations. "
    "Given a statutory definition that describes an enumerated type, extract the "
    "top-level constructors for a Lean 4 inductive type. "
    'Return JSON only: {"constructors": ["camelCaseName", ...]}'
)

_USER_TEMPLATE = """\
Statutory definition of "{term}" (Regulation {regulation_number}):

{definition_text}

Extract the top-level enumerated variants as Lean 4 inductive constructors.
Rules:
- camelCase names only (e.g. "mutualFund", "scheduledCommercialBank")
- Top-level items only — do NOT expand sub-categories into separate constructors
  (e.g. for infrastructure sector, "transportation" is one constructor, not
  "roads", "railSystem", "ports" etc.)
- If the definition lists named sub-types with "includes X and Y", those become constructors
- If the definition is just "means A or B", constructors are the A and B variants
- Aim for 2–20 constructors; never more than 25
- Add an "other" constructor only if the statute explicitly says "such other..."

Return ONLY: {{"constructors": ["name1", "name2", ...]}}
"""


def extract_constructors(
    client: OllamaClient,
    model: str,
    d: dict,
    timeout: int = 120,
    debug: bool = False,
) -> list[str] | None:
    term = d.get("term", "")
    reg = d.get("regulation_number", "")
    text = d.get("definition_text", "")

    user = _USER_TEMPLATE.format(
        term=term,
        regulation_number=reg,
        definition_text=text[:3000],
    )

    if debug:
        print(f"[Constructors] Calling model for {d['rule_id']} ({term})", file=sys.stderr)

    try:
        result = client.chat_json_any(model, _SYSTEM, user, timeout=timeout, debug=debug)
    except Exception as e:
        print(f"[Constructors] Model call failed for {d['rule_id']}: {e}", file=sys.stderr)
        return None

    if not result or not isinstance(result, dict):
        return None

    constructors = result.get("constructors")
    if not isinstance(constructors, list):
        return None

    cleaned = []
    for c in constructors:
        c = str(c).strip()
        if c and c.isidentifier():
            cleaned.append(c)

    return cleaned if cleaned else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--defs", required=True, help="Path to definitions JSONL")
    ap.add_argument("--model", default="qwen2.5:14b-instruct")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-extract constructors even if already present",
    )
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    path = Path(args.defs)
    if not path.exists():
        raise SystemExit(f"Not found: {path}")

    defs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    inductives = [
        d
        for d in defs
        if d.get("lean_type_hint") == "Inductive"
        and (args.overwrite or "constructors" not in d)
    ]

    if not inductives:
        print("[INFO] No Inductive definitions need constructors. Done.")
        return

    print(f"[INFO] Processing {len(inductives)} Inductive definitions...")
    client = OllamaClient(base_url=args.host, timeout=args.timeout)

    updated = 0
    for d in inductives:
        constructors = extract_constructors(
            client,
            args.model,
            d,
            timeout=args.timeout,
            debug=args.debug,
        )
        if constructors:
            d["constructors"] = constructors
            print(f"  [OK]  {d['rule_id']:20s} ({d['term']:35s}) -> {constructors}")
            updated += 1
        else:
            print(f"  [FAIL] {d['rule_id']} — no constructors extracted", file=sys.stderr)

    path.write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in defs) + "\n",
        encoding="utf-8",
    )
    print(f"\n[DONE] {updated}/{len(inductives)} Inductive definitions updated.")


if __name__ == "__main__":
    main()
