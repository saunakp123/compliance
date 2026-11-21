# 2026-08-22 — Kill duplicate v8 extract

Two concurrent `llm_extract_rules.py` runs shared `rules_refactored_v8.jsonl` / `debug_refactored_v8`.

- **Kept:** older tree PID **32412** (venv) → **21108** (Python 3.12), started 22:51:13 — at window start=4 with live Pass1.
- **Killed:** newer tree PID **40780** → **8664**, started 22:51:48.
- Ollama left running; no new extract started.

