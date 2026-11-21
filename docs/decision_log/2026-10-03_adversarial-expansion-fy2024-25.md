# 2026-10-03 — Adversarial expansion (robustness + scale)

**Timestamp:** 2026-10-03T15:41:00-07:00  
**Status:** complete (LLM done; Lean kernel re-prove still pending lake)

## Pre-checks (applied before implementing Cursor instructions)

| Check | Decision |
|-------|----------|
| Which year's rates | **Keep FY 2024–25 / Finance Act 2024** thresholds already in `taxpayer_fields.json` / gold. Do **not** update to FA 2025 (₹10k §194, ₹50k/₹1L §194A, ₹12L new-regime §87A). Paper must state "FY 2024–25 rules". |
| adv_14 / adv_15 "True" meaning | **Split** each into two binary checks: TDS applies + 20% rate applies. Yields **17 cases** (not 15). |
| 32b VRAM | Host GPU = RTX 5060 Laptop **8 GB**. 32b needs ~20 GB → **14b only**. Prefer k=5 over second model. |
| `has_pan` field | Schema already has **`is_pan_furnished`**; §194 PAN proviso already in `tax_rules_gold.jsonl` (`ITA_194_pan_check`). No duplicate field. |
| Dividend threshold | Added `dividend_tds_threshold: 5000` to schema + `Core.lean` (FY 2024–25). |

## What changed

- `scripts/generate_adversarial_taxpayers.py` — 17 cases; `statute_year: FY_2024_25`
- `scripts/build_adversarial_lean.py` — regen instances + `AdversarialProbe.lean` + predicate mirror
- `scripts/llm_judge_baseline.py` — temp=0 (k=1) + temp=0.7 (k=5)
- `scripts/compare_lean_vs_llm.py` — full table → `adversarial_comparison_full.jsonl`
- `Reglib_tax/.../AdversarialRules.lean` — predicates for all 17
- `data/tax/taxpayer_fields.json` + `Core.lean` — `dividend_tds_threshold`

## Lean prove caveat

`lake` / `elan` still not on PATH. `reports/adversarial_lean_results.jsonl` written with `source: predicate_mirror` (Boolean mirror of `AdversarialRules.lean`, verified against GT). **Re-run** `verify_one_lake.py --adversarial` when Lean 4.28.0 is installed for kernel-checked numbers.

## Reproduce

```bash
python scripts/generate_adversarial_taxpayers.py
python scripts/build_adversarial_lean.py
python scripts/llm_judge_baseline.py --models "qwen2.5:14b-instruct"
python scripts/compare_lean_vs_llm.py --skip-lean --models "qwen2.5:14b-instruct"
```

## Results (2026-10-03, n=17, FY 2024–25)

| Oracle / model | Metric | Score |
|----------------|--------|-------|
| Lean (predicate_mirror) | accuracy | **17/17 (100%)** |
| Qwen2.5:14b temp=0 | accuracy | **15/17 (88%)** |
| Qwen2.5:14b k=5 majority | accuracy | **15/17 (88%)** |
| Qwen2.5:14b k=5 | avg consistency | **98%** |

**LLM misses (both temp0 and k5 majority):**

| Case | GT | LLM | Consistency | Trap |
|------|----|-----|-------------|------|
| `adv_11_111a_112a_holding_period_edge` | True | False | 80% | exact-12-month short-term edge |
| `adv_14_194_tds_applies` | True | False | 100% | TDS applicability with no-PAN facts present |

Note: `adv_01` (LTCG boundary) was **correct** this run (temp0 + k5 majority False); Sep 5 single-shot had missed it — report variance.

**Artifacts:** `reports/adversarial_comparison_full.jsonl`, `*_temp0.jsonl`, `*_k5.jsonl`, `adversarial_lean_results.jsonl` (`source=predicate_mirror`).

## Follow-ups

1. Install lake → re-prove AdversarialProbe (replace predicate_mirror)
2. Optional: 32b if a ≥20 GB GPU becomes available
3. Send original 5-case + this 17-case table to collaborator
