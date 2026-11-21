# Decision Log

Timestamped records of scope, architecture, and experiment decisions for the
compliance / formal-verification project. Prefer this over chat history.

## When to add an entry

- Paper scope or demo-corpus changes (ICDR vs ITA/ITR-2, Stage cutoffs)
- Framing choices (e.g. Option B Lean + LLM judge)
- Experiment design freezes (adversarial set, models, metrics)
- Material “do not reverse” pipeline decisions
- State audits that correct handoff claims against the repo

## File naming

```
YYYY-MM-DD_short-kebab-topic.md
```

Examples: `2026-08-22_tax-paper-scope-and-state-audit.md`

## Entry template

```markdown
# Title

- **Timestamp:** YYYY-MM-DDTHH:MM:SS±HH:MM  (local time)
- **Author / agent:** …
- **Status:** decided | audit | superseded by YYYY-MM-DD_…

## Decisions

1. …

## Context

…

## Evidence / gap findings

| Claim | Status | Notes |
|-------|--------|-------|
| … | EXISTS / PARTIAL / MISSING | … |

## Files touched

- …

## Follow-ups

- [ ] …
```

## Conventions

- Use **real local timestamps** (ISO 8601 with offset), not UTC-only guesses.
- Do **not** delete old entries; mark them `superseded by …` and link the new file.
- Keep ICDR extraction Current State in `CLAUDE.md`; put cross-cutting paper/tax
  narrative in `docs/Compliance_context.md` and point here for decisions.
- Do not edit `.cursor/plans/*.plan.md` as a substitute for this log.
