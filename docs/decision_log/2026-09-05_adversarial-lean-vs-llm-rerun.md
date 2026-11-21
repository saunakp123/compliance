# Adversarial Lean vs LLM judge re-run (Option B)

- **Timestamp:** 2026-09-05T22:20:20-05:00
- **Author / agent:** Cursor subagent (adversarial experiment refresh)
- **Status:** audit + experiment refresh

## Decisions

1. **Inventory confirmed:** Aug 22 audit was correct — all adversarial scripts, 5 JSON cases, symmetric predicates (`AdversarialRules` / `AdversarialProbe`), `--adversarial` verify path, and compare orchestrator already existed. No ICDR changes; additive tax-track refresh only.
2. **Re-run performed:** regenerated `data/tax/adversarial/*` + Lean instance files; re-ran `llm_judge_baseline.py` (qwen2.5:14b-instruct); refreshed `reports/adversarial_comparison.jsonl`.
3. **Lean re-prove blocked on this host:** `lake` / elan not on PATH; WSL has no installed distro. Prior `reports/adversarial_lean_results.jsonl` (5/5 explicit True/False via pos/neg) reused via `compare_lean_vs_llm.py --skip-lean`. Installing Lean was attempted; external installer download was policy-blocked.
4. **Fresh LLM scores differ from Aug 22:** Qwen miss on **adv_01** (112A LTCG = ₹1,25,000) — judged taxable (`true`) vs GT `false`. Cases 02–05 correct. Honest Option B result: Lean 5/5, LLM 4/5, 1 disagreement.

## Context

Option B framing: Lean deterministic verdicts (symmetric pos + `_negated` predicates) vs LLM judge over the same structured facts + provision text. Success criteria for the paper demo: Lean 5/5; LLM may miss boundary cases (previously hoped adv_03/04) — this re-run shows the miss on the inclusive LTCG exemption boundary instead.

## Results table

| Case | Section | GT | Lean | LLM | Lean OK | LLM OK |
|------|---------|----|------|-----|---------|--------|
| adv_01_ltcg_boundary | 112A | False | False | True | yes | **no** |
| adv_02_87a_boundary | 87A | True | True | True | yes | yes |
| adv_03_stt_precondition_violation | 111A | False | False | False | yes | yes |
| adv_04_80d_senior_citizen_misclassification | 80D | False | False | False | yes | yes |
| adv_05_residency_day_count_boundary | 6(1) | True | True | True | yes | yes |

- **Lean accuracy:** 100% (5/5; reused prior lake prove)
- **LLM accuracy:** 80% (4/5; fresh Ollama run)
- **Disagreements:** 1/5 (adv_01)

## Evidence / gap findings

| Claim | Status | Notes |
|-------|--------|-------|
| Full pipeline scripts + data | EXISTS | No material gaps vs instruction specs |
| Fresh LLM verdicts | EXISTS | `reports/adversarial_llm_verdicts.jsonl` |
| Fresh comparison | EXISTS | `reports/adversarial_comparison.jsonl` |
| Fresh Lean prove this session | BLOCKED | `lake` missing; WSL empty; elan install blocked |
| Prior Lean results usable | EXISTS | Matches GT; symmetric prove pattern intact |

## Files touched

- Regenerated: `data/tax/adversarial/adv_*.json`, `ground_truth.jsonl`
- Regenerated: `Reglib_tax/Reglib/ITA/Adversarial_adv_0*.lean`
- Refreshed: `reports/adversarial_llm_verdicts.jsonl`, `reports/adversarial_comparison.jsonl`
- Docs: this entry; light updates to `docs/Compliance_context.md` §0 and `CLAUDE.md` Paper/Tax

## Follow-ups

- [ ] Install elan/`lake` (Lean 4.28.0 per `Reglib_tax/lean-toolchain`) and re-run `verify_one_lake.py --adversarial` without `--skip-lean`
- [ ] Optionally re-sample LLM judge N times for variance note on adv_01
- [ ] Close open ITA composite gates in `TaxProbe.lean` (Secs 6, 112A, 80D) — separate from adversarial demo
