# 2026-10-03 — TaxProbe branch negations + senior/new-regime instance

**Timestamp:** 2026-10-03T20:39:00-07:00  
**Status:** complete

## What we ran

1. **Negated theorems** for the four branch rules that fail on the real non-senior / old-regime `sample_taxpayer`.
2. **Second taxpayer** `sample_taxpayer_senior_new` — same as `taxpayer_fields.json` with only `is_senior_citizen` and `is_new_tax_regime` flipped to `true`. Same 28 TaxProbe theorems via `TaxProbeSeniorNew.lean`.

## Artifacts

| Artifact | Result |
|----------|--------|
| `reports/proof_results_tax_branch_negations_2026-10.jsonl` | **4/4** negated proved |
| `reports/proof_results_tax_ladder_senior_new_2026-10.jsonl` | **25/28** (89.3%) |
| Prior real-instance ablation | **21/28** |
| June stub ablation | **25/28** |

## Negations (on `sample_taxpayer`)

| Theorem | Status |
|---------|--------|
| `gold_ita_194a_senior_citizen_negated` | proved |
| `gold_reg_194a_eligible_negated` | proved |
| `gold_ita_87a_new_regime_negated` | proved |
| `gold_reg_87a_eligible_negated` | proved |

Symmetric De Morgan duals live in `ChapterXVII_Part2.lean` / `Chapter8_Part1.lean`; composite duals are inlined so the ladder `simp` closes without nested unfolds.

## Senior / new-regime positives

All four previously stub-dependent branch positives prove on `sample_taxpayer_senior_new` (`194a_senior_citizen`, `194a_eligible`, `87a_new_regime`, `87a_eligible`). Score returns to **25/28**, matching June — confirming the Oct **21/28** gap was instance flags, not ChapterVI rename.

Still open (same three composites as June/Oct): `gold_reg_6_eligible`, `gold_reg_112a_eligible`, `gold_reg_80d_eligible`.

## Citation

- Real non-senior / old regime: **21/28** + **4/4** branch negations.
- Senior / new regime twin: **25/28**.
- Do not cite June 25/28 as the real-instance score without noting the Compliance stub.

## Reproduce

```bash
python scripts/verify_one_lake.py \
  --reglib Reglib_tax \
  --probe Reglib_tax/Reglib/ITA/TaxProbe.lean \
  --rules data/tax/tax_rules_gold.jsonl \
  --defs data/tax/taxpayer_fields.json \
  --instance-name sample_taxpayer \
  --config ladder \
  --only gold_ita_194a_senior_citizen_negated,gold_reg_194a_eligible_negated,gold_ita_87a_new_regime_negated,gold_reg_87a_eligible_negated \
  --out reports/proof_results_tax_branch_negations_2026-10.jsonl

python scripts/verify_one_lake.py \
  --reglib Reglib_tax \
  --probe Reglib_tax/Reglib/ITA/TaxProbeSeniorNew.lean \
  --rules data/tax/tax_rules_gold.jsonl \
  --defs data/tax/taxpayer_fields_senior_new.json \
  --instance-name sample_taxpayer_senior_new \
  --config ladder \
  --out reports/proof_results_tax_ladder_senior_new_2026-10.jsonl
```
