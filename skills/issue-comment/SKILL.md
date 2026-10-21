---
name: issue-comment
description: Use when posting the implementation summary comment on a solved GitHub issue. Covers what to include (shipped, checks, rulings, deviations, follow-ups), what to omit, and when to skip the comment.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

When posting the implementation summary comment on a solved GitHub issue:

- One comment per solved issue. Post after implementation and checks pass, before archiving/closing.
- Terse and scannable, written for both humans and AI coding agents.
- Report verification and deltas only. Do not repeat the issue text, the spec, or the task list.
- `file:line` for code references, doc name + `§` for binding docs. No token values; no personal data beyond what the fix needs.
- Omit sections that have nothing to say.
- Decisions are recorded per the project's conventions (e.g. the issue's Rulings section) — not buried in the comment.

## Template

Implemented in change `<id>`.

- Shipped: <1–3 bullets — observable behavior + key files>
- Checks: <test/lint command(s) + result>
- Rulings: <decisions settled during implementation, recorded in the body — omit if none>
- Deviations: <done differently from the spec/tasks and why — omit if none>
- Follow-ups: #<n>, #<n> — omit if none (file follow-up work as new issues, never leave TODOs)

Always end with the traceability line (never omitted for this comment): `_<model_name> · <model_version>_` — see Signature below.

## Signature (all agent-authored GitHub content)

- **Substantive** content — comments with findings, review results, implementation plans, or implementation reports — ends with one plain-text line: `_<model_name> · <model_version>_` (only metadata actually known — never guessed). Take the pair from the session environment (the model name and exact model ID given to you); never infer it or copy it from prior commits, logs, or another session. Detailed execution metadata stays in agent logs, not GitHub.
- **Routine** posts (progress pings, clarification questions, CI/test status) stay unsigned.
- **Issues** are signed by the Problem verification stamp (model + date) — no separate end-signature.
- **Archiving commits** keep the trailer `model: …; version: …`.
- Never edit a human-authored comment without being asked — exception: `draft` issues. Never double-sign when editing or retrying a comment.

## Skip the comment when

It would add nothing beyond the issue text and the diff: mechanical change, spec followed exactly, no rulings, deviations, or follow-ups.
