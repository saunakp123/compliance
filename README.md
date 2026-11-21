# compliance

Formally verified regulatory compliance: SEBI ICDR rule extraction (pipeline) and
an Income Tax Act / ITR-2 Lean demo used for ACL experiments.

## Environment

- **Python** ≥ 3.11 (tested with 3.12)
- `pip install -r requirements.txt`
- **Ollama** with model `qwen2.5:14b-instruct` (local LLM judge / extraction)
- **elan** + Lean **v4.28.0**, pinned in `Reglib/lean-toolchain` and
  `Reglib_tax/lean-toolchain` (`leanprover/lean4:v4.28.0`)

Confirm the project toolchain (do this inside each Lean package):

```bash
cd Reglib_tax && lake env lean --version   # expect 4.28.0
cd ../Reglib && lake env lean --version    # expect 4.28.0
```

## Layout

| Path | Role |
|------|------|
| `rule_extraction/` | ICDR Pass-1 / Pass-2 extraction helpers |
| `scripts/` | Generators, `verify_one_lake.py`, adversarial judge / compare |
| `Reglib/` | Lean 4 ICDR formalization |
| `Reglib_tax/` | Lean 4 ITA / TaxProbe / adversarial formalization |
| `data/` | Gold rules, taxpayer fields, adversarial cases |
| `reports/` | Experiment result JSONL (October 2026 runs) |
| `docs/decision_log/` | Dated scope / experiment decisions |

See also `PROVENANCE.md` for how gold data and Lean predicates were produced.

## Reproduce Experiment 1 (proof coverage, 28 ITA targets)

```bash
cd Reglib_tax && lake build && cd ..
python scripts/verify_one_lake.py --reglib Reglib_tax --probe Reglib_tax/Reglib/ITA/TaxProbe.lean \
  --rules data/tax/tax_rules_gold.jsonl --defs data/tax/taxpayer_fields.json \
  --instance-name sample_taxpayer --config ladder \
  --out reports/proof_results_tax_ladder_rerun_2026-10.jsonl
python scripts/verify_one_lake.py --reglib Reglib_tax --probe Reglib_tax/Reglib/ITA/TaxProbe.lean \
  --rules data/tax/tax_rules_gold.jsonl --defs data/tax/taxpayer_fields.json \
  --instance-name sample_taxpayer --config ladder \
  --only gold_ita_194a_senior_citizen_negated,gold_reg_194a_eligible_negated,gold_ita_87a_new_regime_negated,gold_reg_87a_eligible_negated \
  --out reports/proof_results_tax_branch_negations_2026-10.jsonl
python scripts/verify_one_lake.py --reglib Reglib_tax --probe Reglib_tax/Reglib/ITA/TaxProbeSeniorNew.lean \
  --rules data/tax/tax_rules_gold.jsonl --defs data/tax/taxpayer_fields_senior_new.json \
  --instance-name sample_taxpayer_senior_new --config ladder \
  --out reports/proof_results_tax_ladder_senior_new_2026-10.jsonl
```

Expected: **21/28** on the filing-derived taxpayer; **4/4** branch negations;
**25/28** on the senior / new-regime twin.

## Reproduce Experiment 2 (17 adversarial cases)

```bash
python scripts/generate_adversarial_taxpayers.py
python scripts/build_adversarial_lean.py
cd Reglib_tax && lake build Reglib.ITA.AdversarialRules Reglib.ITA.AdversarialProbe && cd ..
python scripts/verify_one_lake.py --reglib Reglib_tax --adversarial --config ladder \
  --rules data/tax/tax_rules_gold.jsonl --defs data/tax/taxpayer_fields.json \
  --out reports/adversarial_lean_results_kernel_2026-10.jsonl
python scripts/llm_judge_baseline.py --models "qwen2.5:14b-instruct"
# compare reads reports/adversarial_lean_results.jsonl; reuse the kernel artifact:
cp reports/adversarial_lean_results_kernel_2026-10.jsonl reports/adversarial_lean_results.jsonl
python scripts/compare_lean_vs_llm.py --skip-lean --models "qwen2.5:14b-instruct"
```

Expected: Lean **17/17**; Qwen2.5-14B **15/17** (temperature 0 and 5-run majority).
LLM numbers can vary slightly between runs at temperature 0.7.

## Known issues

- `lean_version` in the October result JSONL files reads **4.34.1** because
  `verify_one_lake.py` used to call bare `lean --version` (elan default) instead of
  `lake env lean --version` in the `--reglib` directory. The proofs themselves were
  built with the pinned **4.28.0** toolchain (`lake build`). The logger is fixed in
  this branch; existing result files were left unchanged.
- ITA rule IDs in probe metadata still carry an `ICDR_` prefix (cosmetic; will be renamed).
- Composite gates for Sections **6**, **112A**, and **80D** are still unproved on both
  taxpayers.

## Where the judge prompt is

`JUDGE_SYSTEM_PROMPT` in `scripts/llm_judge_baseline.py`.

## Pipeline documentation (ICDR)

- `docs/schema_pipeline.md` — rules JSONL → mapping → issuer fields → facts schema
- `docs/run_flow.md` — copy/paste ICDR runbook
- `docs/rule_extraction_with_judge.md` — generator → judge → quarantine loop
