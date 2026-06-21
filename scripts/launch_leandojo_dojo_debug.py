#!/usr/bin/env python3
import subprocess
from pathlib import Path

WSL_ROOT = "/mnt/c/Users/sauna/OneDrive - University Of Houston/UHDSI/Compliance Project/compliance"
RUN = Path(__file__).resolve().parent / ".run_leandojo_dojo_debug.sh"
RUN.write_text(
    f"""#!/usr/bin/env bash
set -euo pipefail
export PATH="${{HOME}}/.elan/bin:${{PATH}}"
cd "{WSL_ROOT}"
export PYTHONPATH="{WSL_ROOT}/scripts"
exec "${{HOME}}/.venv-compliance-lean/bin/python" - <<'PY'
import traceback
from pathlib import Path
import sys
sys.path.insert(0, "{WSL_ROOT}/scripts")
import verify_one
verify_one._patch_leandojo_extractdata()
verify_one._init_leandojo()
from lean_dojo import LeanGitRepo, Theorem, Dojo
import subprocess
reglib = Path("{WSL_ROOT}/Reglib_gold")
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=reglib).decode().strip()
repo = LeanGitRepo(str(reglib), commit)
probe = "Reglib/ICDR/GoldProbe.lean"
thm = Theorem(repo, probe, "gold_reg_5_1_a")
print("Theorem OK", thm)
with Dojo(thm) as (d, s):
    print("Dojo OK", str(s)[:120])
PY
""",
    encoding="utf-8",
    newline="\n",
)
raise SystemExit(subprocess.call(["wsl", "bash", f"{WSL_ROOT}/scripts/.run_leandojo_dojo_debug.sh"]))
