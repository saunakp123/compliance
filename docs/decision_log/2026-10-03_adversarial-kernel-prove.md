# 2026-10-03 — Adversarial Lean kernel re-prove

**Timestamp:** 2026-10-03T18:19:00-07:00  
**Status:** complete

## Environment

- Installed **elan 4.2.4** + toolchain **leanprover/lean4:v4.28.0**
- Confirmed: `lean --version` → 4.28.0; `lake --version` → Lake 5.0.0-src+7e01a1b (Lean 4.28.0)
- No LeanCopilot in `Reglib_tax/lakefile.lean` (nothing to remove)
- Fixed invalid Lean identifiers `chapterVI-A_*` → `chapterVI_A_*` in Chapter VI-A rule files (full `lake build Reglib` now unblocked; AdversarialProbe did not need them)

## Commands

```bash
lake build Reglib.ITA.AdversarialRules   # OK
lake build Reglib.ITA.AdversarialProbe   # OK (sorry warnings expected)
python scripts/verify_one_lake.py --reglib Reglib_tax --adversarial --config ladder \
  --rules data/tax/tax_rules_gold.jsonl --defs data/tax/taxpayer_fields.json \
  --out reports/adversarial_lean_results_kernel_2026-10.jsonl
```

## Results

| Metric | Value |
|--------|-------|
| Theorems | 34 (17 pos + 17 neg) |
| Proved | **17/34 (50%)** — exactly one side of each pair |
| Config | ladder |
| Output | `reports/adversarial_lean_results_kernel_2026-10.jsonl` (does **not** overwrite mirror file) |
| Proof toolchain | `Reglib_tax/lean-toolchain` → **leanprover/lean4:v4.28.0** (via `lake build`) |

### Sanity

- BOTH pos+neg proved: **none**
- NEITHER proved: **none**
- Kernel vs `predicate_mirror`: **0 disagreements**
- Kernel vs ground truth: **0 disagreements** (17/17 case verdicts)

Prior `reports/adversarial_lean_results.jsonl` (`source=predicate_mirror`) left intact for comparison.

Paper can now cite kernel-checked Lean column from `adversarial_lean_results_kernel_2026-10.jsonl`.
