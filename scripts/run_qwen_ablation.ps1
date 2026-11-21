# Run full Qwen ablation in WSL (Ollama on Windows via PowerShell proxy).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$drive = ($Root.Substring(0,1)).ToLower()
$rest = ($Root.Substring(2) -replace '\\','/')
$WslRoot = "/mnt/$drive$rest"
$Cmd = @"
set -euo pipefail
export OLLAMA_USE_WINDOWS_PROXY=1
export PATH="`${HOME}/.elan/bin:`${PATH}"
cd '$WslRoot'
exec "`${HOME}/.venv-compliance-lean/bin/python" scripts/verify_one.py \
  --engine pantograph \
  --reglib Reglib_gold \
  --probe Reglib_gold/Reglib/ICDR/GoldProbe.lean \
  --rules data/gold_standard/gold_standard_regs_4_23.jsonl \
  --defs data/processed/definitions_icdr_reg2.jsonl \
  --config qwen --max-llm-rounds 3 \
  --out reports/proof_results_qwen.jsonl
"@
Write-Host "[run_qwen_ablation] Starting WSL Qwen ablation..."
wsl bash -lc $Cmd
