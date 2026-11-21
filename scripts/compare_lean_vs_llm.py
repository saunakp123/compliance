#!/usr/bin/env python3
"""
compare_lean_vs_llm.py
======================
Joins Lean proof results, LLM judge verdicts (temp0 + k5), and ground truth
into a paper-ready comparison table across the full adversarial set.

Outputs:
  reports/adversarial_comparison_full.jsonl
  reports/adversarial_comparison.jsonl  (slim back-compat: Lean + first model temp0)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

GROUND_TRUTH = Path("data/tax/adversarial/ground_truth.jsonl")
LEAN_RESULTS = Path("reports/adversarial_lean_results.jsonl")
OUT_FULL = Path("reports/adversarial_comparison_full.jsonl")
OUT_SLIM = Path("reports/adversarial_comparison.jsonl")
DEFAULT_MODELS = ["qwen2.5:14b-instruct"]


def run_lean_verification() -> None:
    cmd = [
        sys.executable, "scripts/verify_one_lake.py",
        "--reglib", "Reglib_tax",
        "--rules", "data/tax/tax_rules_gold.jsonl",
        "--defs", "data/tax/taxpayer_fields.json",
        "--config", "ladder",
        "--adversarial",
        "--out", str(LEAN_RESULTS),
    ]
    print("[compare] Running Lean verification:\n ", " ".join(cmd))
    subprocess.run(cmd, check=True)


def load_jsonl_by_id(path: Path) -> dict:
    out: dict = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if "id" not in rec:
            continue
        # Prefer collapsed case rows (have verdict) over raw theorem rows
        if "verdict" in rec or "majority_verdict" in rec or "llm_verdict" in rec:
            out[rec["id"]] = rec
        elif rec["id"] not in out:
            out[rec["id"]] = rec
    return out


def load_ground_truth(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["id"]] = rec
    return out


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--skip-lean",
        action="store_true",
        help="Reuse existing reports/adversarial_lean_results.jsonl",
    )
    ap.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated models matching llm_judge_baseline --models",
    )
    args = ap.parse_args()

    if args.skip_lean:
        if not LEAN_RESULTS.exists():
            raise SystemExit(f"--skip-lean set but {LEAN_RESULTS} missing")
        print(f"[compare] Reusing existing Lean results: {LEAN_RESULTS}")
    else:
        run_lean_verification()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    gt = load_ground_truth(GROUND_TRUTH)
    lean = load_jsonl_by_id(LEAN_RESULTS)

    per_model = {}
    for model in models:
        safe = model.replace(":", "_").replace("/", "_")
        per_model[model] = {
            "temp0": load_jsonl_by_id(Path(f"reports/adversarial_llm_{safe}_temp0.jsonl")),
            "k5": load_jsonl_by_id(Path(f"reports/adversarial_llm_{safe}_k5.jsonl")),
        }

    rows = []
    for case_id, g in gt.items():
        lean_r = lean.get(case_id, {})
        lean_verdict = lean_r.get("verdict")
        row = {
            "id": case_id,
            "section": g["section"],
            "type": g["type"],
            "statute_year": g.get("statute_year", "FY_2024_25"),
            "ground_truth": g["ground_truth_verdict"],
            "lean_verdict": lean_verdict,
            "lean_correct": lean_verdict == g["ground_truth_verdict"],
            "lean_source": lean_r.get("source", "lake"),
        }
        for model in models:
            t0 = per_model[model]["temp0"].get(case_id, {})
            k5 = per_model[model]["k5"].get(case_id, {})
            prefix = model.replace(":", "_").replace("/", "_")
            t0v = t0.get("majority_verdict", t0.get("llm_verdict"))
            k5v = k5.get("majority_verdict", k5.get("llm_verdict"))
            row[f"{prefix}_temp0_verdict"] = t0v
            row[f"{prefix}_temp0_correct"] = t0v == g["ground_truth_verdict"]
            row[f"{prefix}_k5_majority"] = k5v
            row[f"{prefix}_k5_consistency"] = k5.get("consistency")
            row[f"{prefix}_k5_correct"] = k5v == g["ground_truth_verdict"]
        rows.append(row)

    OUT_FULL.parent.mkdir(parents=True, exist_ok=True)
    OUT_FULL.write_text(
        "\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )

    # Slim back-compat table (first model temp0)
    m0 = models[0]
    p0 = m0.replace(":", "_").replace("/", "_")
    slim = []
    for r in rows:
        slim.append({
            "id": r["id"],
            "section": r["section"],
            "type": r["type"],
            "ground_truth": r["ground_truth"],
            "lean_verdict": r["lean_verdict"],
            "lean_correct": r["lean_correct"],
            "llm_verdict": r.get(f"{p0}_temp0_verdict"),
            "llm_correct": r.get(f"{p0}_temp0_correct"),
            "disagreement": r["lean_verdict"] != r.get(f"{p0}_temp0_verdict"),
            "model": m0,
            "k5_majority": r.get(f"{p0}_k5_majority"),
            "k5_consistency": r.get(f"{p0}_k5_consistency"),
            "k5_correct": r.get(f"{p0}_k5_correct"),
            "statute_year": r["statute_year"],
            "lean_source": r["lean_source"],
        })
    OUT_SLIM.write_text(
        "\n".join(json.dumps(r) for r in slim) + ("\n" if slim else ""),
        encoding="utf-8",
    )

    n = len(rows)
    lean_acc = sum(1 for r in rows if r["lean_correct"]) / n if n else 0
    print(f"\nLean accuracy: {lean_acc:.0%}  (n={n}, source={rows[0].get('lean_source') if rows else '?'})")
    for model in models:
        prefix = model.replace(":", "_").replace("/", "_")
        t0_acc = sum(1 for r in rows if r.get(f"{prefix}_temp0_correct")) / n if n else 0
        k5_acc = sum(1 for r in rows if r.get(f"{prefix}_k5_correct")) / n if n else 0
        avg_c = sum((r.get(f"{prefix}_k5_consistency") or 0) for r in rows) / n if n else 0
        print(
            f"{model}  temp0: {t0_acc:.0%}   "
            f"k5-majority: {k5_acc:.0%}   avg consistency: {avg_c:.0%}"
        )

    print(f"\n{'ID':<42} {'GT':<6} {'Lean':<6} {'t0':<6} {'k5':<6} {'cons':<6}")
    print("-" * 78)
    for r in rows:
        prefix = p0
        cons = r.get(f"{prefix}_k5_consistency")
        cons_s = f"{cons:.0%}" if cons is not None else "?"
        print(
            f"{r['id']:<42} {str(r['ground_truth']):<6} {str(r['lean_verdict']):<6} "
            f"{str(r.get(f'{prefix}_temp0_verdict')):<6} "
            f"{str(r.get(f'{prefix}_k5_majority')):<6} {cons_s:<6}"
        )

    print(f"\nWrote {OUT_FULL}")
    print(f"Wrote {OUT_SLIM}")


if __name__ == "__main__":
    main()
