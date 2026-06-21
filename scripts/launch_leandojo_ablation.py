#!/usr/bin/env python3
"""Write LF bash script and run LeanDojo v1 ladder ablation in WSL."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WSL_ROOT = "/mnt/c/Users/sauna/OneDrive - University Of Houston/UHDSI/Compliance Project/compliance"
RUN_SH = ROOT / "scripts" / ".run_leandojo_ablation_wsl.sh"

SCRIPT = f"""#!/usr/bin/env bash
set -euo pipefail
export PATH="${{HOME}}/.elan/bin:${{PATH}}"
cd "{WSL_ROOT}"
REG="{WSL_ROOT}/Reglib_gold"
# LeanDojo v1 tracing breaks on Lean 4.29; use 4.14 for trace+Dojo, restore 4.29 for Pantograph after.
TOOLCHAIN_BAK="$REG/lean-toolchain.pantograph.bak"
if [[ ! -f "$TOOLCHAIN_BAK" ]]; then
  cp "$REG/lean-toolchain" "$TOOLCHAIN_BAK"
fi
echo "leanprover/lean4:v4.14.0" > "$REG/lean-toolchain"
lake -d "$REG" build GoldProbe
"${{HOME}}/.venv-compliance-lean/bin/python" scripts/verify_one.py \\
  --engine leandojo \\
  --reglib Reglib_gold \\
  --probe Reglib_gold/Reglib/ICDR/GoldProbe.lean \\
  --rules data/gold_standard/gold_standard_regs_4_23.jsonl \\
  --defs data/processed/definitions_icdr_reg2.jsonl \\
  --config ladder \\
  --out reports/proof_results_leandojo.jsonl
cp "$TOOLCHAIN_BAK" "$REG/lean-toolchain"
lake -d "$REG" build GoldProbe
"""


def main() -> int:
    RUN_SH.write_text(SCRIPT, encoding="utf-8", newline="\n")
    wsl_path = f"{WSL_ROOT}/scripts/.run_leandojo_ablation_wsl.sh"
    print(f"[launch] WSL script: {wsl_path}")
    return subprocess.call(["wsl", "bash", wsl_path])


if __name__ == "__main__":
    raise SystemExit(main())
