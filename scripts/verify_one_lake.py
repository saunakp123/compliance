#!/usr/bin/env python3
"""
verify_one_lake.py
==================
APOLLO automation loop using lake build as the proof oracle.
No LeanDojo tracing required. Works natively on Windows.

Supports both ICDR (sample_compliant_issuer) and ITA (sample_taxpayer)
via the --instance-name flag.

Usage — ICDR:
    py -3.12 scripts/verify_one_lake.py ^
        --reglib   Reglib_gold ^
        --probe    Reglib_gold/Reglib/ICDR/GoldProbe.lean ^
        --rules    data/gold_standard/gold_standard_regs_4_23.jsonl ^
        --defs     data/processed/definitions_icdr_reg2.jsonl ^
        --instance-name sample_compliant_issuer ^
        --config   ladder ^
        --out      reports/proof_results_lake_ladder.jsonl

Usage — ITA:
    py -3.12 scripts/verify_one_lake.py ^
        --reglib   Reglib_tax ^
        --probe    Reglib_tax/Reglib/ITA/TaxProbe.lean ^
        --rules    data/tax/tax_rules_gold.jsonl ^
        --defs     data/tax/taxpayer_fields.json ^
        --instance-name sample_taxpayer ^
        --config   ladder ^
        --out      reports/proof_results_tax_ladder.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Optional


# ── Tactic ladders ────────────────────────────────────────────────────────────

def make_ladder_basic(instance: str) -> list[str]:
    return [
        "decide",
        f"simp [{instance}]",
        f"simp [{instance}, List.all]",
        f"simp [{instance}, List.all, List.length]",
        "omega",
        "norm_num",
        "trivial",
        "rfl",
    ]


def make_ladder_extended(instance: str) -> list[str]:
    return make_ladder_basic(instance) + [
        "native_decide",
        f"simp [{instance}]; omega",
        f"simp [{instance}, List.all]; omega",
        f"simp [{instance}, List.all, List.length]; omega",
        "tauto",
        "aesop",
    ]


def make_decompose_tactics(instance: str, sub_clauses: list[str]) -> list[str]:
    subs_str = " ".join(sub_clauses)
    return [
        f"constructor <;> simp [{instance}]",
        f"constructor <;> (simp [{instance}]; try omega)",
        f"constructor <;> (simp [{instance}, List.all]; try omega)",
        "constructor <;> decide",
        "constructor <;> native_decide",
        f"unfold {subs_str}; simp [{instance}]",
        f"unfold {subs_str}; simp [{instance}, List.all]",
        f"unfold {subs_str}; simp [{instance}, List.all]; omega",
        "decide",
        "native_decide",
    ]


# ── Context loaders ───────────────────────────────────────────────────────────

def load_rules(path: Path) -> dict[str, dict]:
    rules = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                rules[r["rule_id"]] = r
    return rules


def load_definitions(path: Path) -> dict[str, dict]:
    """
    Load either a definitions JSONL (keyed by maps_to_field)
    or a flat taxpayer_fields.json dict.
    """
    defs = {}
    if not path.exists():
        return defs
    with open(path, encoding="utf-8") as f:
        content = f.read().strip()

    # taxpayer_fields.json is a plain JSON object, not JSONL
    if content.startswith("{"):
        data = json.loads(content)
        # Wrap each scalar as a minimal definition record
        for field, value in data.items():
            defs[field] = {"maps_to_field": field, "definition_text": str(value)}
        return defs

    # Otherwise JSONL format
    for line in content.splitlines():
        line = line.strip()
        if line:
            d = json.loads(line)
            field = d.get("maps_to_field", "")
            if field:
                defs[field] = d
    return defs


def parse_probe_theorems(probe_path: Path, instance_name: str) -> list[dict]:
    """
    Parse a probe .lean file and extract theorem metadata.
    Works for both GoldProbe (sample_compliant_issuer) and TaxProbe (sample_taxpayer).
    """
    content = probe_path.read_text(encoding="utf-8")

    # Composite gate sub-clause info from comments
    composite_subs: dict[str, list[str]] = {}
    for m in re.finditer(r"Composite gate:\s*(\w+)\s*=\s*(.+)", content):
        gate = m.group(1)
        subs_raw = re.sub(r"\s*-/\s*$", "", m.group(2))
        subs = [s.strip() for s in subs_raw.split(",")]
        composite_subs[gate] = subs

    theorems = []
    pattern = re.compile(
        rf"theorem\s+(gold_\w+)\s*:\s*(\w+)\s+{re.escape(instance_name)}\s*:=\s*by",
        re.MULTILINE,
    )
    for m in pattern.finditer(content):
        thm_name = m.group(1)
        def_name = m.group(2)
        is_comp  = def_name in composite_subs
        # Best-effort rule_id reconstruction
        rule_id = (
            def_name
            .replace("reg_", "ICDR_")
            .replace("ita_", "ITA_")
            .upper()
        )
        theorems.append({
            "theorem_name": thm_name,
            "def_name":     def_name,
            "is_composite": is_comp,
            "sub_clauses":  composite_subs.get(def_name, []),
            "rule_id":      rule_id,
        })

    return theorems


# ── Lake oracle ───────────────────────────────────────────────────────────────

class LakeOracle:
    """
    Proof oracle backed by `lake build <probe_module>`.

    For each (theorem, tactic) attempt:
      1. Replace that theorem's `sorry` with the tactic in the probe file
      2. Run `lake build <probe_module>`
      3. Exit 0 → tactic works; exit nonzero → failed
      4. Always restore probe file (even on exception)
    """

    def __init__(self, probe_path: Path, reglib_dir: Path):
        self.probe_path = probe_path
        self.reglib_dir = reglib_dir
        self._original  = probe_path.read_text(encoding="utf-8")

        # Derive lake build target from probe path
        # e.g. Reglib_tax/Reglib/ITA/TaxProbe.lean → Reglib.ITA.TaxProbe
        rel = probe_path.resolve().relative_to(reglib_dir.resolve())
        self._build_target = ".".join(rel.with_suffix("").parts)

        print(f"[oracle] Pre-building {self._build_target} (warms incremental cache)...")
        rc, _ = self._lake_build()
        if rc != 0:
            print(f"[oracle] WARNING: initial build returned {rc} — check for errors")

    def _lake_build(self) -> tuple[int, str]:
        result = subprocess.run(
            ["lake", "build", self._build_target],
            cwd=self.reglib_dir,
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stderr

    def _make_modified(self, theorem_name: str, tactic: str) -> str:
        """Replace the `sorry` line for theorem_name with tactic."""
        pattern = re.compile(
            rf"(theorem\s+{re.escape(theorem_name)}\s*:.*?:=\s*by\s*\n)"
            rf"(\s+sorry\b[^\n]*)",
            re.DOTALL,
        )
        indented = f"  {tactic}"
        modified, count = pattern.subn(rf"\1{indented}", self._original)
        if count == 0:
            raise ValueError(f"Could not locate sorry for {theorem_name}")
        return modified

    def try_tactic(self, theorem_name: str, tactic: str) -> bool:
        modified = self._make_modified(theorem_name, tactic)
        try:
            self.probe_path.write_text(modified, encoding="utf-8")
            rc, stderr = self._lake_build()
            if rc != 0:
                return False
            # Double-check: no error line naming this theorem
            if "error" in stderr.lower() and theorem_name in stderr:
                return False
            return True
        finally:
            self.probe_path.write_text(self._original, encoding="utf-8")

    def restore(self):
        self.probe_path.write_text(self._original, encoding="utf-8")


# ── Qwen fallback ─────────────────────────────────────────────────────────────

QWEN_SYSTEM = """You are an expert in Lean 4 theorem proving for regulatory compliance.

Theorems prove properties of a concrete struct instance.
All fields are concrete Bool / Nat values. Proofs close in 1-2 tactics.

Known patterns:
  Bool field       → simp [<instance_name>]
  Nat threshold    → omega  (after simp if needed)
  List fields      → simp [<instance_name>, List.all]
  Conjunction (∧)  → constructor <;> simp [<instance_name>]
  Decidable        → decide  or  native_decide

Reply with ONE Lean 4 tactic on a single line. Nothing else."""


def call_qwen(
    goal_hint: str,
    rule_text: str,
    def_texts: list[str],
    instance_name: str,
) -> Optional[str]:
    try:
        import ollama
        def_block = "\n".join(f"  - {d}" for d in def_texts) or "  (none)"
        system    = QWEN_SYSTEM.replace("<instance_name>", instance_name)
        prompt    = (
            f"Proof goal: {goal_hint}\n\n"
            f"Regulatory text: {rule_text[:300]}\n\n"
            f"Field definitions:\n{def_block}\n\n"
            f"Instance name: {instance_name}\n\n"
            f"Suggest one Lean 4 tactic:"
        )
        resp = ollama.chat(
            model="qwen2.5:14b-instruct",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            options={"temperature": 0.1, "num_predict": 80},
        )
        raw = resp["message"]["content"].strip()
        raw = re.sub(r"^```(?:lean)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$",          "", raw, flags=re.MULTILINE)
        return raw.strip().splitlines()[0].strip()
    except Exception as e:
        print(f"  [qwen] error: {e}")
        return None


# ── Per-theorem prover ────────────────────────────────────────────────────────

def prove_theorem(
    oracle:         LakeOracle,
    thm_info:       dict,
    rules_db:       dict,
    defs_db:        dict,
    config:         str,
    instance_name:  str,
    max_llm_rounds: int,
) -> dict:

    thm_name = thm_info["theorem_name"]
    def_name = thm_info["def_name"]
    rule_id  = thm_info["rule_id"]
    is_comp  = thm_info["is_composite"]
    subs     = thm_info["sub_clauses"]

    rec = {
        "theorem_name": thm_name,
        "def_name":     def_name,
        "rule_id":      rule_id,
        "is_composite": is_comp,
        "config":       config,
        "instance":     instance_name,
        "status":       "unproved",
        "tactic":       None,
        "phase":        None,
        "llm_rounds":   0,
        "time_s":       0.0,
        "error":        None,
    }

    t0 = time.time()

    base_ladder = (
        make_ladder_extended(instance_name)
        if config in ("extended", "qwen")
        else make_ladder_basic(instance_name)
    )
    # Def-specific unfolds first — required when the goal is `def_name instance`
    # and the def body is not reducible by simp alone.
    ladder = [
        f"unfold {def_name}; dsimp [{instance_name}]; omega",
        f"unfold {def_name}; simp [{instance_name}]",
        f"unfold {def_name}; simp [{instance_name}]; omega",
        f"unfold {def_name}; decide",
        f"simp [{def_name}, {instance_name}]",
    ] + base_ladder

    try:
        # ── Phase 1: Ladder ───────────────────────────────────────────────────
        print(f"  [ladder]")
        for tactic in ladder:
            print(f"    trying: {tactic[:70]}")
            if oracle.try_tactic(thm_name, tactic):
                rec.update(status="proved", tactic=tactic, phase="ladder")
                rec["time_s"] = round(time.time() - t0, 2)
                return rec

        # ── Phase 2: Decompose ────────────────────────────────────────────────
        if is_comp and subs:
            print(f"  [decompose] subs={subs}")
            for tactic in make_decompose_tactics(instance_name, subs):
                print(f"    trying: {tactic[:70]}")
                if oracle.try_tactic(thm_name, tactic):
                    rec.update(status="proved", tactic=tactic, phase="decompose")
                    rec["time_s"] = round(time.time() - t0, 2)
                    return rec

        # ── Phase 3: Qwen ─────────────────────────────────────────────────────
        if config == "qwen":
            rule      = rules_db.get(rule_id, {})
            rule_text = rule.get("text", "")
            def_texts = []
            for m in rule.get("maps_to") or []:
                field = m.get("field", "")
                defn  = defs_db.get(field)
                if defn:
                    def_texts.append(
                        f"{field}: {defn.get('definition_text', '')[:120]}"
                    )

            goal_hint = f"|- {def_name} {instance_name}"

            for round_num in range(1, max_llm_rounds + 1):
                rec["llm_rounds"] = round_num
                print(f"  [qwen round {round_num}] {goal_hint}")
                tactic = call_qwen(goal_hint, rule_text, def_texts, instance_name)
                if not tactic:
                    continue
                print(f"    suggested: {tactic[:70]}")
                if oracle.try_tactic(thm_name, tactic):
                    rec.update(
                        status="proved", tactic=tactic,
                        phase="qwen", llm_rounds=round_num,
                    )
                    rec["time_s"] = round(time.time() - t0, 2)
                    return rec

    except Exception as e:
        rec["error"] = str(e)
        print(f"  [ERROR] {thm_name}: {e}")

    rec["time_s"] = round(time.time() - t0, 2)
    return rec


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reglib",          required=True,  type=Path)
    parser.add_argument("--probe",           required=True,  type=Path)
    parser.add_argument("--rules",           required=True,  type=Path)
    parser.add_argument("--defs",            required=True,  type=Path)
    parser.add_argument("--instance-name",   default="sample_compliant_issuer",
                        help="Lean instance name used in theorems "
                             "(sample_compliant_issuer for ICDR, sample_taxpayer for ITA)")
    parser.add_argument("--config",          default="ladder",
                        choices=["ladder", "extended", "qwen"])
    parser.add_argument("--out",             required=True,  type=Path)
    parser.add_argument("--max-llm-rounds",  type=int, default=3)
    parser.add_argument("--only",            type=str, default=None,
                        help="Comma-separated theorem names for smoke test")
    args = parser.parse_args()

    instance_name = args.instance_name

    rules_db = load_rules(args.rules)
    defs_db  = load_definitions(args.defs)
    theorems = parse_probe_theorems(args.probe, instance_name)

    if args.only:
        only_set = set(args.only.split(","))
        theorems = [t for t in theorems if t["theorem_name"] in only_set]

    print(f"[verify_one_lake] Config:    {args.config}")
    print(f"[verify_one_lake] Instance:  {instance_name}")
    print(f"[verify_one_lake] Theorems:  {len(theorems)}")
    print(f"[verify_one_lake] Reglib:    {args.reglib}")

    oracle = LakeOracle(args.probe.resolve(), args.reglib.resolve())

    args.out.parent.mkdir(parents=True, exist_ok=True)
    results = []
    proved  = 0

    try:
        with open(args.out, "w", encoding="utf-8") as fout:
            for i, thm in enumerate(theorems):
                print(f"\n[{i+1}/{len(theorems)}] {thm['theorem_name']}")
                rec = prove_theorem(
                    oracle, thm, rules_db, defs_db,
                    args.config, instance_name, args.max_llm_rounds,
                )
                results.append(rec)
                fout.write(json.dumps(rec) + "\n")
                fout.flush()

                if rec["status"] == "proved":
                    proved += 1
                    print(f"  OK {rec['phase']}: {rec['tactic']}")
                else:
                    print(f"  X unproved")
    finally:
        oracle.restore()

    # ── Summary ───────────────────────────────────────────────────────────────
    total  = len(results)
    pct    = 100 * proved / total if total else 0
    phases = Counter(r["phase"] for r in results if r["status"] == "proved")
    comp_p = sum(1 for r in results if r["is_composite"] and r["status"] == "proved")
    comp_t = sum(1 for r in results if r["is_composite"])

    print(f"\n{'='*55}")
    print(f"Config:      {args.config}")
    print(f"Instance:    {instance_name}")
    print(f"Proved:      {proved}/{total}  ({pct:.1f}%)")
    print(f"Phases:      {dict(phases)}")
    print(f"Sub-clauses: {proved - comp_p}/{total - comp_t}")
    print(f"Composites:  {comp_p}/{comp_t}")
    print(f"Results:     {args.out}")


if __name__ == "__main__":
    main()
