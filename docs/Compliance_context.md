# Project Handoff Document
## SEBI ICDR Automated Compliance Pipeline
*Last updated: May 16, 2026 — Paste this at the start of a new chat to restore full context.*

---

## 1. Research Goal

Build the **first formally verified regulatory compliance system for financial documents**. Specifically: an end-to-end pipeline that takes a SEBI ICDR 2018 regulation PDF and an IPO filing (Red Herring Prospectus / RHP), extracts structured compliance rules from the regulation, extracts issuer data from the RHP, and produces machine-verified compliance proofs in **Lean 4**.

This is novel because existing systems (APOLLO, Compliance-to-Code) use LLM judges or Python executors as the verification oracle. This project uses a formal proof kernel (Lean 4) — making compliance verdicts formally verifiable, not just plausible.

**Target publication venues:** ICAIL, FinNLP, or a formal methods venue.

**The SEBI ICDR corpus, once complete, would be the first publicly available dataset mapping real regulatory text to executable compliance logic in the financial sector.**

---

## 2. System Architecture (7 Stages)

```
Stage 1: Extract atomic rules from ICDR PDF
         → rules_refactored_vX.jsonl (structured JSONL with maps_to hints)

Stage 2: Build provisional Issuer schema from maps_to fields
         → generate_reglib.py → Reglib/ (Lean 4 library)

Stage 3: Extract rule-anchored evidence from RHP
         → table-aware extraction, not just narrative

Stage 4: Reconcile field types using evidence
         → evidence-first, never LLM-trusted types

Stage 5: Freeze schema → generate partial Issuer candidate

Stage 6: Completeness pass over RHP using frozen schema

Stage 7: Generate Lean 4 code → run formal compliance checks
```

**Key architectural decisions (do not reverse):**
- `maps_to` structured fields over free-text notes
- Evidence-reconciled types over LLM-guessed types
- Tables as first-class evidence
- Deterministic guards around all LLM outputs (judge loop, bounded retries, quarantine)
- Local models (Qwen2.5:14b-instruct) for bulk extraction — privacy-first
- Extract all 301 regulations first, then build definitions/amendment layers

---

## 3. Codebase Map

```
rule_extraction/
  regulation_identifier.py   ← Pass 1 logic, regex patterns, _PASS1_SYSTEM prompt,
                               pre_identify_regulations(), detect_allowed_regs(),
                               identify_regulations(), split_merged_lettered_items()

llm_extract_rules.py         ← Main extraction loop: windowing, carryover hint,
                               anchoring, expand_detected_regs(), KNOWN_ID_RENAMES

rule_extractor.py            ← Pass 2 targeted extraction per identified clause
                               WARNING: clause_text truncation caps live here

scripts/
  generate_reglib.py         ← Reads rules JSONL → generates full Lean 4 Reglib/
  score_extraction.py        ← Precision/Recall/F1 scorer vs gold standard

data/
  gold_standard/
    gold_standard_regs_4_23.jsonl    ← 143-rule gold standard, Regs 4–23
  processed/
    rules_refactored_v6.jsonl        ← v6 BASELINE: F1=81.3%
    rules_refactored_v7.jsonl        ← v7 REGRESSION: F1=68.8%
  debug_refactored_v7/
    pass2_pre_judge.jsonl            ← Pass 2 input (inspect for truncation)
  schema/
    icdr_structure.json              ← Chapter/part assignments (verified correct)

Reglib/
  ICDR/2018/
    definitions/Core.lean            ← Issuer struct (generated from maps_to, NOT Reg 2)
    rules/Chapter2_Part*.lean        ← One file per chapter/part
    rules/Compliance.lean            ← ipo_eligible gate + sample_compliant_issuer
  lakefile.lean
  Reglib.lean
```

---

## 4. Extraction Pipeline — How It Works

### Two-Pass LLM Architecture

**Pass 1 (`regulation_identifier.py`):** Given a 2-page window of PDF text, a local LLM identifies which regulation clauses are present. Returns `{reg_number, clause_text, span_hint, is_proviso}` per clause. Regex pre-scan (`pre_identify_regulations`) gives the model a hint about which regulation numbers are visible.

**Pass 2 (`rule_extractor.py`):** For each clause identified in Pass 1, a targeted LLM call extracts the full structured rule: `rule_id`, `text`, `maps_to` (field name + type hint for the Issuer struct), `amendment_history`, `confidence`.

### Key Mechanisms

**Windowing:** 2 pages per window, 1 page overlap. Sliding across the full PDF.

**Carryover hint:** When a sub-regulation spans a page boundary with no visible parent header on the next page, `prev_window_last_subclause` tracks the deepest clause from the prior window. A natural-language hint is injected into the Pass 1 prompt distinguishing: lettered items `(a)`, `(b)` → belong to `prev_window_last_subclause`; roman-numeral items `(v)`, `(vi)` → belong to `parent_of(prev_window_last_subclause)`.

**Anchoring:** Rules extracted by Pass 1 are validated against `allowed_regs` (regulation numbers visible in the window). Rules whose top-level regulation is more than 1 away from any visible regulation are dropped. Exception: rules matching the carryover hint context are exempt.

**Footnote stripping (`strip_footnotes_with_linkage`):**
- Pattern A: inline `25[text]` → strip digit, keep bracketed text (it IS the current law)
- Pattern B: `25 Substituted by SEBI...` lines → remove entirely
- Pattern C: orphaned amendment tails `(Amendment) Regulations...` → remove

### Rule ID Naming Convention

```
ICDR_{reg}_{sub}_{item}_{detail}

ICDR_6_3_iv_a        → Reg 6, sub-reg (3), item (iv), clause (a)
ICDR_14_proviso_2    → Reg 14, second "Provided that"
ICDR_8_proviso_3_c_i → Reg 8, third proviso, clause (c), item (i)
ICDR_7_explanation   → Reg 7, Explanation block
ICDR_8a_c            → Reg 8A (alphanumeric), clause (c)

Rules:
- proviso naming: _proviso, _proviso_2, _proviso_3
- explanation naming: _explanation (singular, attached to parent level)
- alphanumeric regulations: 8a (lowercase) in the ID
- NEVER use _1 as intermediate level unless (1) appears explicitly in source text
```

---

## 5. Extraction Scores — Full History

| Version | TP | FN | FP | Recall | Precision | F1 | Notes |
|---------|----|----|-----|--------|-----------|----|-------|
| v5 | 92 | 51 | 26 | 64.3% | 78.0% | 70.5% | Baseline before footnote fix |
| **v6** | **100** | **43** | **3** | **69.9%** | **97.1%** | **81.3%** | **Current best — use as baseline** |
| v7 | 88 | 55 | 25 | 61.5% | 77.9% | 68.8% | Net regression — 5 root cause bugs |
| **v8 target** | **~136** | **~7** | **~0** | **>90%** | **>95%** | **>95%** | |

**Gold standard:** `gold_standard_regs_4_23.jsonl` — 143 rules, Regulations 4–23.

**Clean regulations in v6 (these must not regress):** 4, 9, 13, 18, 19, 20, 21, 22, 23

**v6 per-regulation gaps (starting point for v8):**

| Reg | Gold | v6 TP | Key Missing |
|-----|------|--------|-------------|
| 5 | 9 | 6 | `5_1_explanation`, `5_2_proviso_2`, `5_2_proviso_3` |
| 6 | 23 | 11 | `6_3` continuation: `6_3_iv_a`–`e`, `6_3_v`–`ix` |
| 7 | 13 | 10 | `7_explanation_b_i/ii/iii` |
| 8 | 10 | 3 | `8`, `8_proviso`, `8_proviso_2`, full `8_proviso_3` block |
| 8a | 4 | 3 | `8a_explanation` |
| 14 | 13 | 9 | `14_proviso`, `14_proviso_2`, `14_a_proviso`, `14_c_proviso`, `14_4_proviso`, `14_4_proviso_2` |
| 15 | 14 | 10 | `15_1_c_proviso`, `15_1_d`, `15_1_iii`, `15_1_explanation` |
| 16 | 6 | 5 | `16_1_b_proviso` |
| 17 | 10 | 5 | `17_b_proviso`, `17_c_proviso`, `17_explanation_i/ii/iii` |

---

## 6. What v7 Broke and Why

v7 was a net regression (F1 81.3% → 68.8%). Root causes confirmed by code inspection:

### Root Cause A — 300-char truncation cap not fully patched
The 1200-char fix was applied to `llm_extract_rules.py` but the actual truncation lives in `rule_extractor.py`. `ICDR_14_b` and `ICDR_14_4` are still exactly 300 chars in v7's `pass2_pre_judge.jsonl`. This causes all 6 missing Reg 14 provisos plus Reg 22 and 23 regressions.

### Root Cause B — `split_merged_lettered_items()` drops parent clause
The splitter correctly splits merged `a./b./c.` items into separate objects but replaces the parent clause entirely rather than emitting it first. Reg 13 lost `ICDR_13_c` (was TP in v6) and gained spurious `ICDR_13_c_a`, `ICDR_13_c_b` (FPs).

### Root Cause C — Phantom `(1)` sub-regulation insertion
The lettered-item splitting prompt caused the model to invent intermediate numbered levels not present in the source text. `ICDR_17_1_a`, `ICDR_17_1_b` (should be `17_a`, `17_b`), `ICDR_16_1` (bare, not in gold), `ICDR_5_explanation` (missing `_1`). New in v7, not in v6.

### Root Cause D — Carryover hint overridden by `reg_context`
`reg_context` (listing visible top-level regs like `{6, 7}`) appears before the carryover hint in the prompt string. Model reads it first and anchors too strongly, producing `6(v)` instead of `6(3)(v)`. Fix: move carryover hint BEFORE `reg_context`.

### Root Cause E — Fix 4a (terminal letter strip) not firing
`prev_window_last_subclause` is still retaining terminal letters like `15(1)(a)` instead of stripping to `15(1)`. Causes Reg 15 to drop from TP=10 (v6) to TP=5 (v7) — all continuation items get assigned one level too deep (`15_1_a_c` instead of `15_1_c`).

---

## 7. v8 Work Plan (Apply in This Order)

**Rule: apply one fix, run scoring script, confirm no regressions before the next fix.**

### Priority 1 — Find ALL truncation caps (zero risk, highest yield)
```bash
grep -rn "\[:300\]\|\[:500\]\|max_chars" --include="*.py"
```
Raise every instance to `[:1200]`. Check `rule_extractor.py` specifically.
**Expected:** +8 rules (Reg 14 provisos, Reg 22 proviso, Reg 23 proviso).

### Priority 2 — Fix `split_merged_lettered_items()` to emit parent first
In `regulation_identifier.py`, before emitting children, find the intro text (everything before the first child marker), emit it as the parent object, then emit children.
**Expected:** Reg 13 returns to v6 level (+1 TP, -2 FP).

### Priority 3 — Add "no phantom sub-levels" to `_PASS1_SYSTEM`
```python
"Never insert a numbered sub-regulation level that does not appear explicitly "
"in the source text. If lettered items appear directly under a top-level "
"regulation with no visible (1), the reg_number is 'N(a)', not 'N(1)(a)'."
```
**Expected:** Reg 17, 16, 5 path errors fixed (+5 TP, -8 FP).

### Priority 4 — Move carryover hint BEFORE `reg_context` in prompt
In `identify_regulations()`, change assembly order:
```python
# BEFORE: reg_context + page_text + carryover_hint
# AFTER:  carryover_hint + reg_context + page_text
```
**Expected:** Reg 6 continuation (`6_3_v` through `6_3_ix`), Reg 15 continuation fixed.

### Priority 5 — Confirm Fix 4a (terminal letter strip) actually runs
Add temporary debug print after the `re.sub(r"\([a-e]\)$", ...)` line in `llm_extract_rules.py`. If it never prints for windows where `_nums` contains `15(1)(a)`, the code block is unreachable.
**Expected:** Reg 15 returns to v6 level.

### Priority 6 — Pass 2 deduplication
After all windows processed, before Pass 2 dispatch, deduplicate by `rule_id` keeping longest `clause_text`. Zero regression risk.

### Priority 7 — Verify `expand_detected_regs` input
Confirm it receives `visible_reg_strings` (list of strings including `"8A"`) not `detected_regs` (set of ints). Fix input if wrong.
**Expected:** Reg 8 recovery (+3–9 TP).

---

## 8. Scoring Script

```bash
python scripts/score_extraction.py \
    --extracted data/processed/rules_refactored_v8.jsonl \
    --gold      data/gold_standard/gold_standard_regs_4_23.jsonl \
    --baseline  data/processed/rules_refactored_v6.jsonl \
    --output    reports/v8_score_report.json
```

- Exit code 0 = F1 ≥ 90% target
- `--baseline` prints per-regulation delta vs v6
- Check per-regulation table — global F1 improvement can hide local regressions
- v6 is the floor: any per-regulation TP lower than v6 is a regression, stop and investigate

**Three post-run verification checks:**
```bash
# 1. No truncation at 300 chars
python3 -c "
import json
entries = [json.loads(l) for l in open('data/processed/debug_refactored_v8/pass2_pre_judge.jsonl') if l.strip()]
trunc = [(e['rule_id'], len(e.get('text','') or e.get('clause_text','')))
         for e in entries if len(e.get('text','') or e.get('clause_text','')) == 300]
print('Still at 300 chars (should be empty):', trunc)"

# 2. No phantom (1) levels
python3 -c "
import json, re
rules = [json.loads(l) for l in open('data/processed/rules_refactored_v8.jsonl') if l.strip()]
phantom = [r['rule_id'] for r in rules if re.search(r'_\d+_[a-e]$', r['rule_id'])
           and not any(r['rule_id'].startswith(p) for p in ['ICDR_10_1','ICDR_15_1'])]
print('Phantom sub-levels:', phantom)"

# 3. Reg 8 recovered
python3 -c "
import json
rules = [json.loads(l) for l in open('data/processed/rules_refactored_v8.jsonl') if l.strip()]
print('Reg 8:', sorted(r['rule_id'] for r in rules if r['rule_id'].startswith('ICDR_8')))"
```

---

## 9. Lean 4 Reglib — Current State

### What Exists
- `Reglib/ICDR/2018/definitions/Core.lean` — `Issuer` struct with all fields
- `Reglib/ICDR/2018/rules/Chapter2_Part*.lean` — rule definitions per chapter/part
- `Reglib/ICDR/2018/rules/Compliance.lean` — `ipo_eligible` gate, `sample_compliant_issuer`
- `lakefile.lean`, `Reglib.lean` root import

### Critical Limitation
**`Core.lean` was NOT generated from Regulation 2 (Definitions chapter).** Every field in the `Issuer` struct was reverse-engineered from the `maps_to` fields in v5/v6 rule extraction — i.e. inferred from how rules *use* terms, not from statutory *definitions* of those terms. The `Promoter` struct, `IssueType`, `SecurityType` inductives, and type aliases (`INR_Crore`, `Months`, `Years`) were hardcoded scaffolding in `cursor_generate_reglib.md`, not extracted from the PDF.

### How to Test Now (Without RHP)
```bash
cd Reglib
lake build
```
Then in VS Code with LeanCopilot installed:
```lean
theorem test_reg5 : reg_5_eligible sample_compliant_issuer := by
  unfold reg_5_eligible reg_5_1_a reg_5_1_b reg_5_1_c reg_5_1_d reg_5_2
  simp [sample_compliant_issuer]
```
This tests whether LeanCopilot/LeanDojo can navigate the schema. Most rule bodies have `sorry` stubs — that's expected; the APOLLO repair loop handles those.

### How to Test With a Real RHP (Full Pipeline)
1. `extract_issuer_from_rhp.py` reads RHP PDF → `issuer.json` (flat JSON matching `Issuer` fields)
2. Manually verify top 10 field values against actual RHP text (field name drift across versions means some mappings may be stale)
3. Orchestrator script reads `issuer.json` → generates Lean instantiation → `lake exe compliance`
4. **Important:** Field names in `Core.lean` changed across v5→v6→v7, so verify `extract_issuer_from_rhp.py` uses current field names before trusting output

### What's Needed for Proper Lean Verification
Extract Regulation 2 (60+ definition sub-clauses) using a **separate `--mode definitions`** flag in `llm_extract_rules.py`. The definitions extraction uses a different prompt schema:
- Output: `{rule_id, term, definition_text, lean_type_hint, cross_references, maps_to_field}`
- `lean_type_hint` values: `"Structure"`, `"Inductive"`, `"Bool"`, `"Nat"`, `"String"`
- Then update `generate_reglib.py` with `--definitions` flag to consume this alongside `--rules`

Key definitions that will change `Core.lean` significantly: `"promoter"` (Reg 2(1)(za)), `"specified securities"` (Reg 2(1)(zb)), `"net worth"`, `"SR equity shares"` — all currently guessed from usage context.

---

## 10. Open Questions / Unresolved Items

1. **v8 Priority 1 exact location** — the `[:300]` cap is confirmed in `rule_extractor.py` but the exact line/function has not been identified. First action in next session: `grep -rn "\[:300\]" --include="*.py"`.

2. **Reg 8 full story** — only `ICDR_8_explanation` appears in v7's `pass2_pre_judge.jsonl`. Where is the main Reg 8 body text in the PDF? Is the `8.` header at a page boundary that splits it across two windows? Needs `--debug` run examination.

3. **`ICDR_15_1_b_proviso` and `ICDR_16_1_a_proviso`** — appear in v6/v7 output but not in gold standard. May be valid 2025 SEBI amendment insertions not yet in gold. Mark `status = "needs_review"` for now; do not delete.

4. **31 rules with empty `maps_to`** — 26% of v5 output had empty `maps_to`. Some are legitimately unmappable (procedural rules). Others (`ICDR_6_3_i`, `ICDR_22`) should have fields. Targeted re-pass with CoT prompting is planned but not yet done.

5. **LeanCopilot integration test** — has not been run yet. `lake build` has not been confirmed passing on current Reglib. This is the next Lean-side task.

6. **APOLLO repair loop** — `verify_one.py` exists but proof success rate is ~5%. The APOLLO-style repair loop (pipe Lean REPL errors back to LLM, iterate) is the biggest pending Lean improvement. Projected: 5% → 40%+ proof success.

7. **Regulation 2 extraction** — design is clear (new `--mode definitions` flag in `llm_extract_rules.py`, new prompt schema, new JSONL format) but not yet implemented. Blocked on: completing v8 rule extraction first per the "extract all 301 regulations before definitions" strategic decision.

8. **Full 301-regulation run** — the pipeline is designed for it (`--skip-existing`, `--resume` flags) but has only been run on Regulations 4–23 (Chapter II, Part I–V). All 12 chapters, 301 regulations, 475 pages not yet attempted.

9. **Gold standard coverage** — `gold_standard_regs_4_23.jsonl` covers only Regs 4–23. No gold standard exists yet for Regs 1–3 or Regs 24–301. Will need to be built as the extraction expands.

---

## 11. Constraints and Preferences

- **Privacy-first:** Use local Ollama models (Qwen2.5:14b-instruct) for all bulk extraction. Do not send regulatory text or RHP content to external APIs.
- **v6 is the floor:** Never accept a version whose per-regulation TP is lower than v6 on any regulation, even if global F1 improves.
- **Apply and score one fix at a time:** Do not batch multiple code changes and run once. Each fix gets its own scoring run before the next fix is applied.
- **No hallucinated field names in `maps_to`:** Field names like `conditions`, `exceptions`, `securities` are too generic — always prefer specific names like `promoter_min_contribution_pct`.
- **Deterministic post-processing before LLM:** The splitter (`split_merged_lettered_items`) and deduplication are deterministic safeguards that run after the LLM, not before. The LLM result is the primary source; deterministic steps are safety nets only.
- **Strategic sequencing:** Extract all 301 regulations first, THEN extract Regulation 2 definitions, THEN rebuild Core.lean with proper grounding. Do not build definitions on a partial rule corpus.
- **`cursor_v7_liverun_fixes.md` supersedes `cursor_v7_bugfixes_A_B.md`** — do not apply the old A_B file.

---

## 12. Key Files to Have Open / Reference

| File | Purpose |
|------|---------|
| `data/processed/rules_refactored_v6.jsonl` | Baseline — 100 TP rules to not regress |
| `data/processed/debug_refactored_v7/pass2_pre_judge.jsonl` | Diagnose truncation and missing rules |
| `data/gold_standard/gold_standard_regs_4_23.jsonl` | 143-rule ground truth |
| `reports/v7_score_report.json` | Full per-regulation breakdown for v7 |
| `rule_extraction/regulation_identifier.py` | Pass 1 — most changes go here |
| `rule_extractor.py` | Pass 2 — truncation cap lives here |
| `llm_extract_rules.py` | Main loop — carryover hint, anchoring |
| `scripts/score_extraction.py` | Run after every change |
| `Reglib/ICDR/2018/definitions/Core.lean` | Current Issuer struct |
| `Reglib/ICDR/2018/rules/Compliance.lean` | ipo_eligible + sample_compliant_issuer |

---

## 13. Where to Start Next Session

**Immediate next action:** Priority 1 from the v8 work plan.

```bash
grep -rn "\[:300\]\|\[:500\]\|max_chars" --include="*.py"
```

Find every truncation cap in the codebase. Raise to `[:1200]`. Run the scoring script. This is zero regression risk and recovers the most rules (+8 confirmed). Do not touch anything else until this is scored and confirmed.

After that: Priority 2 (`split_merged_lettered_items` parent emission fix), then score again.

If you want to work on the Lean side instead: run `lake build` in the `Reglib/` directory and confirm it compiles cleanly. Then try LeanCopilot on `sample_passes_reg5`. These are independent of the extraction work.
