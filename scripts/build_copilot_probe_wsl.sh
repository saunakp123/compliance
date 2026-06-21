#!/usr/bin/env bash
# Build LeanCopilot + CopilotProbe inside WSL (Ubuntu 24.04).
# Usage (from WSL):
#   bash scripts/build_copilot_probe_wsl.sh
# Or from PowerShell:
#   wsl -d Ubuntu-24.04 -- bash "/mnt/c/.../compliance/scripts/build_copilot_probe_wsl.sh"

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGLIB="$REPO_ROOT/Reglib"
WIN_HOME="/mnt/c/Users/sauna"

export PATH="$HOME/.elan/bin:$PATH"

mkdir -p "$HOME/.cache"
if [[ -d "$WIN_HOME/.cache/lean_copilot" && ! -e "$HOME/.cache/lean_copilot" ]]; then
  ln -s "$WIN_HOME/.cache/lean_copilot" "$HOME/.cache/lean_copilot"
  echo "[OK] Symlinked model cache -> $WIN_HOME/.cache/lean_copilot"
fi

echo "[INFO] Reglib: $REGLIB"
echo "[INFO] Toolchain: $(cat "$REGLIB/lean-toolchain")"

cd "$REGLIB"
export LD_LIBRARY_PATH="$REGLIB/.lake/packages/LeanCopilot/.lake/build/lib:${LD_LIBRARY_PATH:-}"

if [[ "${1:-}" == "--fresh" ]]; then
  rm -rf .lake
  shift
  echo "[INFO] lake update..."
  lake update
  echo "[INFO] lake build LeanCopilot (may take several minutes)..."
  lake build LeanCopilot
fi

echo "[INFO] lake build CopilotProbe..."
lake build CopilotProbe

echo "[DONE] CopilotProbe build complete."
