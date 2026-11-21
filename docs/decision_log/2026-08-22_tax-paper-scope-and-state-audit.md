# Tax / paper scope freeze and state audit

- **Timestamp:** 2026-08-22T22:31:14-05:00
- **Author / agent:** Cursor subagent (handoff completion after 661047bc)
- **Status:** decided + audit

## Decisions

1. **Paper demo corpus = ITA / ITR-2 end-to-end.** Full ICDR RHP→Lean E2E deferred for this paper.
2. **Narrative architecture cut at Stage 4** (schema / type reconciliation story); Lean verification shown on the tax track.
3. **Framing Option B (complementary):** Lean yields deterministic True/False via positive + negated predicates; LLM judge answers the same boundary questions from structured facts + rule text. Not a replacement for the kernel.
4. **Adversarial set frozen at five cases:** LTCG ₹1,25,000 (112A); total income ₹5,00,000 (87A); 111A STT precondition; 80D senior-citizen cap mis-application; residency exactly 182 days (§6(1)).
5. **Optional frontier comparison** remains optional — not required for the demo claim; no frontier artifacts in repo as of this audit.
6. **ICDR v8 extraction work continues in parallel** but must not overwrite these paper-scope decisions; v8 extract remains blocked on venv/Ollama (see `CLAUDE.md` Current State). Priorities 2/3/6 already applied by another agent.

## Context

Handoff claimed tools, reports, ablation 25/28, and Category-A scale (764 rules). This entry records what the workspace actually contains on 2026-08-22 after a fast gap audit (glob/grep + report inspection). No `.cursor/plans/*.plan.md` files were edited.

## Evidence / gap findings

| Claim | Status | Notes |
|-------|--------|-------|
| `generate_adversarial_taxpayers.py` + 5 JSON taxpayers | EXISTS | `data/tax/adversarial/adv_01`…`adv_05` + `ground_truth.jsonl` |
| Lean instances for all 5 | EXISTS | `Reglib_tax/Reglib/ITA/Adversarial_adv_0*.lean` |
| `verify_one_lake.py --adversarial` | EXISTS | Collapses pos/neg → per-case verdict |
| `llm_judge_baseline.py --model` | EXISTS | Default `qwen2.5:14b-instruct` |
| `compare_lean_vs_llm.py` orchestrator | EXISTS | |
| Adversarial Lean / LLM / comparison reports | EXISTS | 5/5 Lean correct, 5/5 LLM correct, 0 disagreements |
| Symmetric predicates | PARTIAL | In `AdversarialRules.lean` + `AdversarialProbe.lean`; **not** in `TaxProbe.lean` (gold-only 28 thms) |
| `TaxProbe` / `Core` / `Compliance` under Reglib_tax | EXISTS | |
| `generate_gold_probe.py`, `generate_reglib.py`, `schema_to_struct.py` | EXISTS | |
| ITR-2 Lean struct (`Reglib_itr2` Core) | EXISTS | From `schema_to_struct.py` + ITR-2 schema |
| ITA ablation 25/28 (89.3%) | EXISTS | `proof_results_tax_ladder.jsonl`; unproved: composite 6, 112A, 80D |
| ICDR Reg 2 definitions = 68 | EXISTS | `data/processed/definitions_icdr_reg2.jsonl` (ICDR, not ITA) |
| `parse_validation_rules.py` | MISSING | Not in `scripts/` |
| `generate_itr2_predicates.py` | MISSING | Not in `scripts/` |
| 764 Category A ITR-2 rules | MISSING | No Category-A dump/count located in repo |
| Frontier LLM comparison run | MISSING | Optional; no artifacts |

## Files touched

- `docs/Compliance_context.md` — refreshed §0 paper/tax scope + gap table; updated §1/§13; preserved ICDR body
- `CLAUDE.md` — light Paper/Tax Track pointer + next-session lines; ICDR v8 Current State left intact
- `docs/decision_log/README.md` — how to append entries
- `docs/decision_log/2026-08-22_tax-paper-scope-and-state-audit.md` — this entry

## Follow-ups

- [ ] Repair Python `.venv` + restore Ollama/`qwen2.5:14b-instruct` for ICDR v8 extract+score
- [ ] Close open ITA composite gates: `gold_reg_6_eligible`, `gold_reg_112a_eligible`, `gold_reg_80d_eligible`
- [ ] Locate or regenerate Category-A ITR-2 validation corpus; restore/create `parse_validation_rules.py` / `generate_itr2_predicates.py` if scaling beyond the 5-case demo
- [ ] Optional: frontier judge pass for comparison table in the paper
- [ ] Keep paper figures/tables aligned with `reports/adversarial_comparison.jsonl` (5/5 agree)
