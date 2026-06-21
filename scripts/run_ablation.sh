#!/usr/bin/env bash
# run_ablation.sh — Run all three configs (Git Bash / WSL / Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGLIB="$ROOT/Reglib_gold"
PROBE="$ROOT/Reglib_gold/Reglib/ICDR/GoldProbe.lean"
RULES="$ROOT/data/gold_standard/gold_standard_regs_4_23.jsonl"
DEFS="$ROOT/data/processed/definitions_icdr_reg2.jsonl"
OUTDIR="$ROOT/reports"

mkdir -p "$OUTDIR"

PY="${PY:-$HOME/.venv-compliance-lean/bin/python}"
if [[ ! -x "$PY" ]]; then
  PY=python3.12
  command -v "$PY" &>/dev/null || PY=python3
fi

echo "Config A: ladder"
ENGINE="--engine pantograph"

echo "Config A: ladder"
"$PY" "$ROOT/scripts/verify_one.py" $ENGINE \
    --reglib "$REGLIB" --probe "$PROBE" --rules "$RULES" --defs "$DEFS" \
    --config ladder --out "$OUTDIR/proof_results_ladder.jsonl"

echo "Config B: extended"
"$PY" "$ROOT/scripts/verify_one.py" $ENGINE \
    --reglib "$REGLIB" --probe "$PROBE" --rules "$RULES" --defs "$DEFS" \
    --config extended --out "$OUTDIR/proof_results_extended.jsonl"

echo "Config C: qwen"
"$PY" "$ROOT/scripts/verify_one.py" $ENGINE \
    --reglib "$REGLIB" --probe "$PROBE" --rules "$RULES" --defs "$DEFS" \
    --config qwen --max-llm-rounds 3 --out "$OUTDIR/proof_results_qwen.jsonl"

"$PY" "$ROOT/scripts/analyze_ablation.py" \
    --ladder "$OUTDIR/proof_results_ladder.jsonl" \
    --extended "$OUTDIR/proof_results_extended.jsonl" \
    --qwen "$OUTDIR/proof_results_qwen.jsonl"
