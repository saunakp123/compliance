#!/usr/bin/env bash
# run_verify_wsl.sh — Run verify_one / ablation inside WSL (LeanDojo tracing).
# Windows: lake build Reglib_gold first, then:
#   wsl bash scripts/run_verify_wsl.sh smoke
#   wsl bash scripts/run_verify_wsl.sh ablation
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# elan/lake/lean (install: curl https://elan.lean-lang.org/elan-init.sh -sSf | sh)
export PATH="${HOME}/.elan/bin:${PATH}"
if ! command -v lake &>/dev/null; then
  echo "[run_verify_wsl] lake not found. In WSL run:"
  echo "  curl https://elan.lean-lang.org/elan-init.sh -sSf | sh"
  echo "  source ~/.profile"
  exit 1
fi

VENV="${COMPLIANCE_VENV:-$HOME/.venv-compliance-lean}"
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "[run_verify_wsl] Missing venv at $VENV"
  echo "  Run once: wsl bash scripts/wsl_setup_venv.sh"
  exit 1
fi
PY="$VENV/bin/python"

REGLIB="$ROOT/Reglib_gold"
PROBE="$ROOT/Reglib_gold/Reglib/ICDR/GoldProbe.lean"
RULES="$ROOT/data/gold_standard/gold_standard_regs_4_23.jsonl"
DEFS="$ROOT/data/processed/definitions_icdr_reg2.jsonl"
OUTDIR="$ROOT/reports"
mkdir -p "$OUTDIR"

if [[ ! -d "$REGLIB/.git" ]]; then
  echo "[run_verify_wsl] Reglib_gold must be a git repo (LeanDojo requirement)."
  exit 1
fi

# Ensure Lean toolchain matches Reglib_gold (reads lean-toolchain via elan).
if command -v elan &>/dev/null; then
  (cd "$REGLIB" && elan toolchain install "$(cat lean-toolchain)" 2>/dev/null || true)
fi

MODE="${1:-smoke}"
shift || true

case "$MODE" in
  smoke)
    echo "[run_verify_wsl] Smoke test: gold_reg_5_1_a"
    "$PY" "$ROOT/scripts/verify_one.py" \
      --reglib "$REGLIB" --probe "$PROBE" --rules "$RULES" --defs "$DEFS" \
      --config ladder --only gold_reg_5_1_a \
      --out "$OUTDIR/smoke_test.jsonl" "$@"
    ;;
  ablation)
    export PY
    exec "$ROOT/scripts/run_ablation.sh"
    ;;
  *)
    echo "Usage: $0 [smoke|ablation] [extra verify_one args...]"
    exit 2
    ;;
esac
