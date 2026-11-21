# Data provenance

| Artifact | How it was produced | Review |
|---|---|---|
| `data/gold_standard/gold_standard_regs_4_23.jsonl` (143 rules, ICDR Regs 4–23) | Drafted by Claude (Anthropic) from the text of the SEBI ICDR 2018 PDF | Reviewed by Saunak against the regulation text |
| `data/processed/definitions_icdr_reg2.jsonl` (68 definitions) | Extracted by the local pipeline (Qwen2.5-14B); 3 amendment sub-clauses (oa, bbbb, eeea) patched by hand | Reviewed by Saunak |
| `data/tax/tax_rules_gold.jsonl` (20 ITA provisions) | Drafted by Claude; FY 2024–25 thresholds | Reviewed by Saunak |
| `Reglib/`, `Reglib_tax/` Lean predicates | Generated from the JSONL files by `scripts/generate_reglib.py`; adversarial predicates written in Cursor | Checked by `lake build` |
| `data/tax/sample_itr2.xml` and derived taxpayer instances | Synthetic ITR-2 filing; no real taxpayer data | n/a |
| `data/tax/adversarial/` (15 instances, 17 cases, ground truth) | Cases and ground-truth labels drafted with Claude; implemented in Cursor | Ground truth cross-checked by the Lean kernel (17/17 agree) |
| `reports/adversarial_llm_*` | Qwen2.5-14B-Instruct run locally via Ollama | n/a |

Note: the 111A/112A rates and the Rs. 1.25 lakh LTCG exemption apply to transfers on or after
23 July 2024; the corpus uses these values for the whole of FY 2024–25.
