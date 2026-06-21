#!/usr/bin/env python3
"""LeanDojo v1 smoke (one theorem) in WSL."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WSL_ROOT = "/mnt/c/Users/sauna/OneDrive - University Of Houston/UHDSI/Compliance Project/compliance"
RUN_SH = ROOT / "scripts" / ".run_leandojo_smoke_wsl.sh"

SCRIPT = f"""#!/usr/bin/env bash
set -euo pipefail
export PATH="${{HOME}}/.elan/bin:${{PATH}}"
cd "{WSL_ROOT}"
REG="{WSL_ROOT}/Reglib_gold"
echo "leanprover/lean4:v4.14.0" > "$REG/lean-toolchain"
lake -d "$REG" build GoldProbe
exec "${{HOME}}/.venv-compliance-lean/bin/python" scripts/verify_one.py \\
  --engine leandojo \\
  --reglib Reglib_gold \\
  --probe Reglib_gold/Reglib/ICDR/GoldProbe.lean \\
  --rules data/gold_standard/gold_standard_regs_4_23.jsonl \\
  --defs data/processed/definitions_icdr_reg2.jsonl \\
  --config ladder \\
  --only gold_reg_5_1_a \\
  --out reports/leandojo_smoke.jsonl
"""


def main() -> int:
    RUN_SH.write_text(SCRIPT, encoding="utf-8", newline="\n")
    return subprocess.call(["wsl", "bash", f"{WSL_ROOT}/scripts/.run_leandojo_smoke_wsl.sh"])


if __name__ == "__main__":
    raise SystemExit(main())
