# 2026-10-03 — ITA ablation vs ChapterVI / Core changes

**Timestamp:** 2026-10-03T18:55:00-07:00  
**Status:** complete

## Did 25/28 rely on the ChapterVI files we touched?

**Yes — same `Reglib_tax` / TaxProbe path, not a separate unaffected build.**

- `TaxProbe.lean` imports `ChapterVI_A_Part1`, `ChapterVI_A_Part2`, and `Compliance`.
- June artifact: `reports/proof_results_tax_ladder.jsonl` (2026-06-13), summarized in `ablation_summary.json` as **25/28 (89.3%)**.
- The `chapterVI-A_*` hyphen bug would have blocked `lake build Reglib.ITA.TaxProbe` if present then; June must have used a then-parseable tree. Our rename to `chapterVI_A_*` was required for today’s build, but was **not** what moved the score.

## What actually changed the score

TaxProbe was resolving `sample_taxpayer` from the **Compliance stub** (dummy Nats, `is_senior_citizen := true`, `is_new_tax_regime := true`). After adversarial work we:

1. Added `dividend_tds_threshold` to `Core.lean` / fields
2. Regenerated `instances/SampleTaxpayer.lean` from real `taxpayer_fields.json` (non-senior, old regime)
3. Removed the Compliance stub and pointed TaxProbe at the real instance
4. Fixed composite identifier casing (`reg_111A_eligible`, etc.)

Re-run (Lean 4.28.0, ladder):

| Artifact | Proved |
|----------|--------|
| June `proof_results_tax_ladder.jsonl` | **25/28** |
| Oct `proof_results_tax_ladder_rerun_2026-10.jsonl` | **21/28** |

**New unproved vs June (4):**

| Theorem | Why it fails on real instance |
|---------|-------------------------------|
| `gold_ita_194a_senior_citizen` | Predicate requires `is_senior_citizen = true`; real sample is false |
| `gold_reg_194a_eligible` | Conjunction includes the senior conjunct |
| `gold_ita_87a_new_regime` | Predicate requires `is_new_tax_regime = true`; real sample is old regime |
| `gold_reg_87a_eligible` | Conjunction includes the new-regime conjunct |

Still open (same as June): `gold_reg_6_eligible`, `gold_reg_112a_eligible`, `gold_reg_80d_eligible`.

## Citation guidance for the paper

- Do **not** claim the June 25/28 is unaffected by Reglib_tax chapter files.
- Prefer citing the Oct re-run (**21/28**) on the real `sample_taxpayer`, **or** keep June 25/28 only with an explicit caveat that it used the Compliance stub instance (senior / new-regime flags set).
- Adversarial kernel results (`adversarial_lean_results_kernel_2026-10.jsonl`) are independent of TaxProbe ablation and remain valid.

## Reproduce

```bash
python scripts/verify_one_lake.py \
  --reglib Reglib_tax \
  --probe Reglib_tax/Reglib/ITA/TaxProbe.lean \
  --rules data/tax/tax_rules_gold.jsonl \
  --defs data/tax/taxpayer_fields.json \
  --instance-name sample_taxpayer \
  --config ladder \
  --out reports/proof_results_tax_ladder_rerun_2026-10.jsonl
```
