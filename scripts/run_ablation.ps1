# run_ablation.ps1 — Run all three APOLLO configs (native Windows)
# Usage: powershell -File scripts/run_ablation.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $Root "scripts\verify_one.py"))) {
    $Root = (Get-Location).Path
}

$REGLIB = Join-Path $Root "Reglib_gold"
$PROBE  = Join-Path $Root "Reglib_gold\Reglib\ICDR\GoldProbe.lean"
$RULES  = Join-Path $Root "data\gold_standard\gold_standard_regs_4_23.jsonl"
$DEFS   = Join-Path $Root "data\processed\definitions_icdr_reg2.jsonl"
$OUTDIR = Join-Path $Root "reports"

New-Item -ItemType Directory -Force -Path $OUTDIR | Out-Null

Write-Host "========================================"
Write-Host "Config A: ladder (deterministic, no LLM)"
Write-Host "========================================"
py -3.12 (Join-Path $Root "scripts\verify_one.py") `
    --reglib $REGLIB --probe $PROBE --rules $RULES --defs $DEFS `
    --config ladder --out (Join-Path $OUTDIR "proof_results_ladder.jsonl")

Write-Host ""
Write-Host "========================================"
Write-Host "Config B: extended (+ decide / aesop)"
Write-Host "========================================"
py -3.12 (Join-Path $Root "scripts\verify_one.py") `
    --reglib $REGLIB --probe $PROBE --rules $RULES --defs $DEFS `
    --config extended --out (Join-Path $OUTDIR "proof_results_extended.jsonl")

Write-Host ""
Write-Host "========================================"
Write-Host "Config C: qwen (extended + Qwen2.5:14b)"
Write-Host "========================================"
py -3.12 (Join-Path $Root "scripts\verify_one.py") `
    --reglib $REGLIB --probe $PROBE --rules $RULES --defs $DEFS `
    --config qwen --max-llm-rounds 3 `
    --out (Join-Path $OUTDIR "proof_results_qwen.jsonl")

Write-Host ""
Write-Host "========================================"
Write-Host "Ablation summary"
Write-Host "========================================"
py -3.12 (Join-Path $Root "scripts\analyze_ablation.py") `
    --ladder (Join-Path $OUTDIR "proof_results_ladder.jsonl") `
    --extended (Join-Path $OUTDIR "proof_results_extended.jsonl") `
    --qwen (Join-Path $OUTDIR "proof_results_qwen.jsonl")
