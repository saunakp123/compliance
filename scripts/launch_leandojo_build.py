#!/usr/bin/env python3
"""Build Reglib_gold on Lean 4.14 for LeanDojo tracing."""
from __future__ import annotations

import subprocess
from pathlib import Path

WSL_ROOT = "/mnt/c/Users/sauna/OneDrive - University Of Houston/UHDSI/Compliance Project/compliance"
RUN_SH = Path(__file__).resolve().parent / ".run_leandojo_build_414.sh"

SCRIPT = f"""#!/usr/bin/env bash
set -euo pipefail
export PATH="${{HOME}}/.elan/bin:${{PATH}}"
cd "{WSL_ROOT}/Reglib_gold"
echo "toolchain: $(cat lean-toolchain)"
lean --version
lake build GoldProbe
"""


def main() -> int:
    RUN_SH.write_text(SCRIPT, encoding="utf-8", newline="\n")
    return subprocess.call(["wsl", "bash", f"{WSL_ROOT}/scripts/.run_leandojo_build_414.sh"])


if __name__ == "__main__":
    raise SystemExit(main())
