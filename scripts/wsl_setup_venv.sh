#!/usr/bin/env bash
# One-time WSL setup: Pantograph (LeanDojo-v2 prover) + ollama. Venv on Linux FS.
set -euo pipefail
VENV="${HOME}/.venv-compliance-lean"

if [[ ! -x "$VENV/bin/python" ]]; then
  python3.12 -m venv "$VENV"
fi
"$VENV/bin/pip" install -U pip
"$VENV/bin/pip" install pantograph ollama
"$VENV/bin/python" -c "from pantograph.server import Server; print('pantograph OK')"
echo "Venv ready: $VENV"
echo "Run: wsl bash scripts/run_verify_wsl.sh smoke"
