# Pause ICDR v8 extract; focus tax/ITA

- **Timestamp:** 2026-08-23T13:33:09-05:00
- **Author / agent:** Cursor command subagent (user decision)
- **Status:** decided

## Decisions

1. **Pause ICDR v8 extraction mid-run.** Do not restart extract this session; Priority 1–7 code fixes remain in tree; v8 remains unscored.
2. **Focus next work on tax/ITA track** (paper demo): close open composite gates or optional frontier judge — see `docs/Compliance_context.md` §0 and `2026-08-22_tax-paper-scope-and-state-audit.md`.
3. **Leave Ollama running** (`qwen2.5:14b-instruct` present) for later tax/LLM use.
4. Prefer resume-from-stop **if supported**; audit found **no true resume**.

## Context

User redirected capacity from a live v8 `llm_extract_rules.py` run to the ITA/ITR-2 paper track. Extract processes were stopped deliberately; debug artifacts kept for forensics.

## Evidence / pause snapshot

| Item | Value |
|------|--------|
| Killed PIDs | First pair **26640** / **49984**; second pair **41060** / **756** (brief restart that truncated debug JSONL) — all `scripts/llm_extract_rules.py` |
| Ollama | Left up (`http://127.0.0.1:11434`; model `qwen2.5:14b-instruct`) |
| Last completed window | `[DEBUG] window start=5` → ACCEPTs for pages `[6, 7]` (`ICDR_8_a` … `ICDR_8a_b`) |
| Incomplete window | `[DEBUG] window start=6` → Pass1 pages `[7, 8]`; killed mid-Pass2 (last extract log: `8A(b)`) |
| `pass2_pre_judge.jsonl` | Was **61** lines at first stop; second extract restart **truncated to 0 bytes** (file still present, empty). Progress remains in `extract_detached.err.log` |
| `rules_refactored_v8.jsonl` | **Missing** (no final out file) |
| Err log | `data/processed/debug_refactored_v8/extract_detached.err.log` |

### Resume capability

**NO** — `scripts/llm_extract_rules.py` has neither `--resume` nor `--skip-existing`. Closest flags:

- `--append` — append to `--out` (default opens `--out` for overwrite)
- `--dedupe` — skip rule_ids already present in an existing `--out`
- `--max-pages` — truncate page range only (does **not** skip already-processed windows)

Because final JSONL was never written, **a full re-run is required** when ICDR resumes. `extract_detached.err.log` retains window/ACCEPT progress; `pass2_pre_judge.jsonl` was wiped by the brief restart.

### Intended full re-run (later; do not run now)

```bash
python scripts/llm_extract_rules.py \
  --pdf data/input/ICDR_rules_4_22.pdf \
  --out data/processed/rules_refactored_v8.jsonl \
  --model qwen2.5:14b-instruct \
  --window 2 --overlap 1 \
  --reg-filter 4 23 \
  --timeout 600 \
  --debug \
  --debug-dir data/processed/debug_refactored_v8
```

(Clear or use a fresh `--debug-dir` if overlapping append into `pass2_pre_judge.jsonl` is undesirable.)

## Files touched

- `docs/decision_log/2026-08-23_pause-icdr-v8-focus-tax.md` — this entry
- `CLAUDE.md` — Current State / Next session → ICDR paused; focus tax/ITA
- `docs/Compliance_context.md` — light §0 date/focus nudge

## Follow-ups

- [ ] Tax: close `gold_reg_6_eligible` / `gold_reg_112a_eligible` / `gold_reg_80d_eligible` in `Reglib_tax/Reglib/ITA/TaxProbe.lean`
- [ ] Optional: frontier LLM judge for paper comparison table
- [ ] Later: full ICDR v8 re-extract + `scripts/score_extraction.py` (no true resume)
