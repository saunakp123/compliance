#!/usr/bin/env python3
"""
analyze_ablation.py
===================
Reads the three proof_results jsonl files and prints a comparison table.

Usage:
    python scripts/analyze_ablation.py \
        --ladder   reports/proof_results_ladder.jsonl \
        --extended reports/proof_results_extended.jsonl \
        --qwen     reports/proof_results_qwen.jsonl
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_results(path: Path) -> list[dict]:
    results = []
    if not path.exists():
        return results
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def summarize(results: list[dict], label: str) -> dict:
    total = len(results)
    proved = sum(1 for r in results if r["status"] == "proved")
    comp_p = sum(1 for r in results if r["is_composite"] and r["status"] == "proved")
    comp_t = sum(1 for r in results if r["is_composite"])
    sub_p = proved - comp_p
    sub_t = total - comp_t
    phases = Counter(r["phase"] for r in results if r["status"] == "proved")
    avg_t = sum(r.get("time_s", 0) for r in results) / total if total else 0
    llm_calls = sum(r.get("llm_rounds", 0) for r in results)

    return {
        "label": label,
        "total": total,
        "proved": proved,
        "pct": 100 * proved / total if total else 0,
        "sub_p": sub_p,
        "sub_t": sub_t,
        "comp_p": comp_p,
        "comp_t": comp_t,
        "phases": dict(phases),
        "avg_time_s": round(avg_t, 2),
        "llm_calls": llm_calls,
    }


def print_table(summaries: list[dict]) -> None:
    sep = "+" + "-" * 16 + "+" + "-" * 12 + "+" + "-" * 18 + "+" + "-" * 16 + "+" + "-" * 14 + "+"
    print(sep)
    print(f"| {'Config':<14} | {'Proved':<10} | {'Sub-clauses':<16} | {'Composites':<14} | {'LLM calls':<12} |")
    print(sep)
    for s in summaries:
        proved_str = f"{s['proved']}/{s['total']} ({s['pct']:.1f}%)"
        sub_str = f"{s['sub_p']}/{s['sub_t']}"
        comp_str = f"{s['comp_p']}/{s['comp_t']}"
        llm_str = str(s["llm_calls"])
        print(f"| {s['label']:<14} | {proved_str:<10} | {sub_str:<16} | {comp_str:<14} | {llm_str:<12} |")
    print(sep)

    print("\nPhase breakdown (proved theorems):")
    for s in summaries:
        phases_str = ", ".join(f"{k}={v}" for k, v in s["phases"].items())
        print(f"  {s['label']:<14}: {phases_str}")


def print_unproved(results: list[dict]) -> None:
    unproved = [r for r in results if r["status"] != "proved"]
    if not unproved:
        print("  (none — 100% success!)")
        return
    for r in unproved:
        err = (r.get("error") or "")[:60]
        print(f"  {r['theorem_name']}  [{r['def_name']}]  err={err}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ladder", required=True, type=Path)
    parser.add_argument("--extended", required=True, type=Path)
    parser.add_argument("--qwen", required=True, type=Path)
    args = parser.parse_args()

    r_ladder = load_results(args.ladder)
    r_extended = load_results(args.extended)
    r_qwen = load_results(args.qwen)

    summaries = [
        summarize(r_ladder, "A: ladder"),
        summarize(r_extended, "B: extended"),
        summarize(r_qwen, "C: qwen"),
    ]

    print("\n" + "=" * 80)
    print("ABLATION RESULTS — SEBI ICDR GoldProbe Formal Verification")
    print("=" * 80 + "\n")
    print_table(summaries)
    print()
    print("Unproved theorems (Config C — Qwen):")
    print_unproved(r_qwen)
    print()

    summary_path = args.qwen.parent / "ablation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)
    print(f"Summary written to: {summary_path}")


if __name__ == "__main__":
    main()
