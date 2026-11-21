#!/usr/bin/env python3
"""Build Reglib_gold on Lean 4.14 for LeanDojo tracing."""
from __future__ import annotations

import subprocess
from pathlib import Path

def _wsl_repo_root() -> str:
    root = Path(__file__).resolve().parents[1]
    s = str(root)
    if len(s) >= 2 and s[1] == ":":
        return f"/mnt/{s[0].lower()}{s[2:].replace(chr(92), '/')}"
    return s.replace(chr(92), "/")



WSL_ROOT = _wsl_repo_root()
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
