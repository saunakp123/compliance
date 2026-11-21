#!/usr/bin/env python3
"""Sanity-check kernel adversarial results vs predicate_mirror and GT."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

KERNEL = Path("reports/adversarial_lean_results_kernel_2026-10.jsonl")
MIRROR = Path("reports/adversarial_lean_results.jsonl")
GT = Path("data/tax/adversarial/ground_truth.jsonl")
TOOLCHAIN = Path("Reglib_tax/lean-toolchain")


def main() -> None:
    thm_rows, case_rows = [], []
    for line in KERNEL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "theorem_name" in r:
            thm_rows.append(r)
        elif "verdict" in r and "id" in r:
            case_rows.append(r)

    pkg_tc = TOOLCHAIN.read_text(encoding="utf-8").strip() if TOOLCHAIN.exists() else "?"
    print("Package lean-toolchain:", pkg_tc)
    print("Theorem rows:", len(thm_rows))
    print("Proved:", sum(1 for r in thm_rows if r["status"] == "proved"))
    print("Case verdict rows:", len(case_rows))

    by: dict[str, dict] = defaultdict(lambda: {"pos": None, "neg": None, "pos_tac": None, "neg_tac": None})
    for r in thm_rows:
        cid = r["theorem_name"][len("gold_") :]
        is_neg = cid.endswith("_negated")
        if is_neg:
            cid = cid[: -len("_negated")]
            by[cid]["neg"] = r["status"] == "proved"
            by[cid]["neg_tac"] = r.get("tactic")
        else:
            by[cid]["pos"] = r["status"] == "proved"
            by[cid]["pos_tac"] = r.get("tactic")

    both, neither, ok = [], [], []
    for cid, s in sorted(by.items()):
        if s["pos"] and s["neg"]:
            both.append(cid)
        elif (not s["pos"]) and (not s["neg"]):
            neither.append(cid)
        else:
            ok.append(cid)

    print("\n=== SANITY (exactly one of pos/neg) ===")
    print("OK pairs:", len(ok))
    print("BOTH proved (BUG):", both or "none")
    print("NEITHER proved (ladder gap):", neither or "none")

    mirror_by = {}
    for line in MIRROR.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "id" in r and "verdict" in r:
            mirror_by[r["id"]] = r["verdict"]

    gt_by = {}
    for line in GT.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        gt_by[r["id"]] = r["ground_truth_verdict"]

    dm = [
        (r["id"], r["verdict"], mirror_by.get(r["id"]))
        for r in case_rows
        if r["verdict"] != mirror_by.get(r["id"])
    ]
    dg = [
        (r["id"], r["verdict"], gt_by.get(r["id"]))
        for r in case_rows
        if r["verdict"] != gt_by.get(r["id"])
    ]
    print("\n=== KERNEL vs PREDICATE_MIRROR / GT ===")
    print("Kernel vs mirror disagreements:", len(dm), dm or "")
    print("Kernel vs GT disagreements:", len(dg), dg or "")
    print(f"\n{'ID':<42} {'Kernel':<8} {'Mirror':<8} {'GT':<8}")
    for r in case_rows:
        cid = r["id"]
        print(
            f"{cid:<42} {str(r['verdict']):<8} "
            f"{str(mirror_by.get(cid)):<8} {str(gt_by.get(cid)):<8}"
        )


if __name__ == "__main__":
    main()
