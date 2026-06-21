#!/usr/bin/env python3
"""Write LF bash script and run Qwen ablation in WSL."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WSL_ROOT = "/mnt/c/Users/sauna/OneDrive - University Of Houston/UHDSI/Compliance Project/compliance"
RUN_SH = ROOT / "scripts" / ".run_qwen_ablation_wsl.sh"

SCRIPT = f"""#!/usr/bin/env bash
set -euo pipefail
export OLLAMA_USE_WINDOWS_PROXY=1
export PATH="${{HOME}}/.elan/bin:${{PATH}}"
cd "{WSL_ROOT}"
exec "${{HOME}}/.venv-compliance-lean/bin/python" scripts/verify_one.py \\
  --engine pantograph \\
  --reglib Reglib_gold \\
  --probe Reglib_gold/Reglib/ICDR/GoldProbe.lean \\
  --rules data/gold_standard/gold_standard_regs_4_23.jsonl \\
  --defs data/processed/definitions_icdr_reg2.jsonl \\
  --config qwen --max-llm-rounds 3 \\
  --out reports/proof_results_qwen.jsonl
"""


def main() -> int:
    RUN_SH.write_text(SCRIPT, encoding="utf-8", newline="\n")
    wsl_path = f"{WSL_ROOT}/scripts/.run_qwen_ablation_wsl.sh"
    print(f"[launch] WSL script: {wsl_path}")
    return subprocess.call(["wsl", "bash", wsl_path])


if __name__ == "__main__":
    raise SystemExit(main())
