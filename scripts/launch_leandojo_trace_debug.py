#!/usr/bin/env python3
"""Debug LeanDojo tracing on Reglib_gold (Lean 4.14)."""
from __future__ import annotations

import subprocess
from pathlib import Path

WSL_ROOT = "/mnt/c/Users/sauna/OneDrive - University Of Houston/UHDSI/Compliance Project/compliance"
RUN_SH = Path(__file__).resolve().parent / ".run_leandojo_trace_debug.sh"

SCRIPT = f"""#!/usr/bin/env bash
set -euo pipefail
export PATH="${{HOME}}/.elan/bin:${{PATH}}"
cd "{WSL_ROOT}/Reglib_gold"
EXTRACT="${{HOME}}/.venv-compliance-lean/lib/python3.12/site-packages/lean_dojo/data_extraction/ExtractData.lean"
echo "=== lake build (full) ==="
lake build
echo "=== copy ExtractData ==="
cp "$EXTRACT" ./ExtractData.lean
echo "=== trace GoldProbe only ==="
lake env lean --threads 4 --run ExtractData.lean Reglib/ICDR/GoldProbe.lean
echo "=== OK ==="
"""


def main() -> int:
    RUN_SH.write_text(SCRIPT, encoding="utf-8", newline="\n")
    return subprocess.call(["wsl", "bash", f"{WSL_ROOT}/scripts/.run_leandojo_trace_debug.sh"])


if __name__ == "__main__":
    raise SystemExit(main())
