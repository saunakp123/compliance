#!/usr/bin/env python3
"""
llm_judge_baseline.py
=====================
LLM judge baseline for the adversarial ITR-2 experiment.

Robustness protocol (per paper expansion):
  - Run A: temperature=0, k=1 (deterministic single pass)
  - Run B: temperature=0.7, k=5 (stochastic majority + consistency)

Default model: qwen2.5:14b-instruct via local Ollama (privacy-first).
A 32b model needs ~20GB VRAM; on 8GB GPUs keep 14b only — k=5 repeats
matter more than a second model scale. Do not wire cloud APIs.

Framing (ACL): LLM judge reliability at rule-boundary conditions.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import ollama

JUDGE_SYSTEM_PROMPT = (
    "You are a tax compliance assistant. You are given a taxpayer's financial "
    "facts and the text of one Income Tax Act provision. Decide whether the "
    "provision's condition is satisfied for this taxpayer. "
    "Respond ONLY as JSON: {\"verdict\": true|false, \"rationale\": \"<one sentence>\"}"
)


def build_user_prompt(taxpayer: dict, rule_text_hint: str) -> str:
    return (
        f"Provision text:\n{rule_text_hint}\n\n"
        f"Taxpayer facts:\n{json.dumps(taxpayer, indent=2)}\n\n"
        "Does the provision's condition hold for this taxpayer? Respond with the JSON only."
    )


def query(model: str, system: str, user: str, temperature: float) -> str:
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        options={"temperature": temperature},
    )
    return resp["message"]["content"]


def parse_verdict(raw: str) -> dict:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"verdict": None, "rationale": f"UNPARSEABLE: {raw[:200]}"}
    try:
        parsed = json.loads(match.group(0))
        v = parsed.get("verdict")
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("true", "yes", "eligible", "satisfied"):
                v = True
            elif v_low in ("false", "no", "ineligible", "not satisfied"):
                v = False
        return {
            "verdict": v if isinstance(v, bool) else None,
            "rationale": parsed.get("rationale", ""),
        }
    except json.JSONDecodeError:
        return {"verdict": None, "rationale": f"JSON_ERROR: {raw[:200]}"}


def run_case(model: str, case: dict, taxpayer: dict, temperature: float, k: int) -> dict:
    prompt = build_user_prompt(taxpayer, case["rule_text_hint"])
    trials = []
    for i in range(k):
        raw = query(model, JUDGE_SYSTEM_PROMPT, prompt, temperature)
        parsed = parse_verdict(raw)
        trials.append({
            "trial": i,
            "verdict": parsed.get("verdict"),
            "rationale": parsed.get("rationale"),
            "raw": raw,
        })
    verdicts = [t["verdict"] for t in trials if t["verdict"] is not None]
    majority = Counter(verdicts).most_common(1)[0][0] if verdicts else None
    consistency = (verdicts.count(majority) / len(verdicts)) if verdicts else 0.0
    return {
        "id": case["id"],
        "section": case["section"],
        "model": model,
        "temperature": temperature,
        "k": k,
        "majority_verdict": majority,
        # Back-compat with older compare script
        "llm_verdict": majority,
        "llm_rationale": trials[0]["rationale"] if trials else "",
        "consistency": consistency,
        "trials": trials,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ground-truth", default="data/tax/adversarial/ground_truth.jsonl")
    ap.add_argument(
        "--models",
        default="qwen2.5:14b-instruct",
        help="Comma-separated Ollama model tags. Default: 14b only "
             "(32b needs ~20GB VRAM; skip if GPU is smaller).",
    )
    ap.add_argument("--out-dir", default="reports")
    ap.add_argument(
        "--model",
        default=None,
        help="Deprecated single-model alias; prefer --models. "
             "If set, also writes reports/adversarial_llm_verdicts.jsonl (temp0).",
    )
    args = ap.parse_args()

    cases = [
        json.loads(l)
        for l in Path(args.ground_truth).read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if args.model:
        if args.model not in models:
            models.insert(0, args.model)

    for model in models:
        safe = model.replace(":", "_").replace("/", "_")

        # Run A — deterministic single pass (temperature=0)
        out_a = out_dir / f"adversarial_llm_{safe}_temp0.jsonl"
        with out_a.open("w", encoding="utf-8") as f:
            for case in cases:
                taxpayer = json.loads(
                    Path(case["taxpayer_file"]).read_text(encoding="utf-8")
                )
                print(f"[{model}][temp0] {case['id']} ...")
                result = run_case(model, case, taxpayer, temperature=0.0, k=1)
                f.write(json.dumps(result) + "\n")
                print(f"[{model}][temp0] {case['id']}: {result['majority_verdict']}")

        # Legacy single-file alias for the first / --model run
        if args.model == model or (not args.model and model == models[0]):
            legacy = out_dir / "adversarial_llm_verdicts.jsonl"
            legacy.write_text(out_a.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"[legacy] Copied temp0 -> {legacy}")

        # Run B — stochastic k=5
        out_b = out_dir / f"adversarial_llm_{safe}_k5.jsonl"
        with out_b.open("w", encoding="utf-8") as f:
            for case in cases:
                taxpayer = json.loads(
                    Path(case["taxpayer_file"]).read_text(encoding="utf-8")
                )
                print(f"[{model}][k5] {case['id']} ...")
                result = run_case(model, case, taxpayer, temperature=0.7, k=5)
                f.write(json.dumps(result) + "\n")
                print(
                    f"[{model}][k5] {case['id']}: majority={result['majority_verdict']} "
                    f"consistency={result['consistency']:.0%}"
                )

    print(f"\nWrote per-model temp0 and k5 result files to {out_dir}/")


if __name__ == "__main__":
    main()
