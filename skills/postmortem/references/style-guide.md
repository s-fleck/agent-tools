# Postmortem Style Guide

Form and evidence rules for a project's postmortem registry. The parent
`SKILL.md` is the lifecycle procedure; this guide defines the triggers, the
seed format, and the registry entry.

## Registry contract

- **One path per project**, named in the project's `AGENTS.md`. Default:
  `POSTMORTEMS.md` at the repository root. A project that keeps it under
  `docs/` must list it in the docs map as a non-binding record and exempt it
  from `Status:` bumps and binding-docs sync.
- **Non-binding.** It carries no `Status:` line and is not part of the binding
  docs. A rule change goes through the binding docs; the registry records why
  the work was hard, not what the rule is.
- **Append-only, newest first.** Add new entries below the file header. Never
  rewrite a historical entry; to correct one, add a new entry that supersedes it
  and links back.
- **One entry per landmark event**, not per session or per issue.
- **Follow-ups are real issues.** The registry is not a todo list.
- **No secrets, personal data, tokens, or customer data.**

## Triggers

Write an entry when at least one row applies.

| Trigger | Entry when | Examples |
|---|---|---|
| Policy or contract change | A binding doc, schema, public contract, or dependency baseline changed | a renamed config key, a new required stage, a toolchain migration |
| Escaped defect or incident | Something reached the base branch, or a revert/hotfix was needed | a merged bug, a security or data issue, a rollback |
| Repeated friction | The same finding, check failure, or agent mistake happened at least twice | two review rounds on one paragraph, the same test failure after two fixes |
| Reversed decision | A recorded decision was undone after being treated as settled | a reversal in the issue's rulings, a spec rewritten after approval |
| Scope surprise | The approved scope changed materially | a new subsystem, a dropped requirement, a moved boundary |
| Novel landing failure | The normal landing path failed in a new way | red base, a near-miss merge, a manual repair after a broken push |
| Operator intervention | A human had to unblock, re-run, or repair the work | manual rebase, repeated CI reruns, an out-of-band fix |

Do **not** write an entry for:

- routine work with no decisions, rework, or surprise;
- a single review finding fixed immediately;
- a transient failure the process already handles, unless it exposed a gap;
- work that never landed and left no durable record — record the gap instead.

## Seed format

A seed is a short, append-only note written when the trigger fires. It is not
the final entry.

```md
- 2026-10-25T14:03Z trigger=repeated-friction stage=review
  observation: the same YAML-shape finding appeared in two review rounds
  evidence: #42 comment 123456, PR #43 review 789
  lesson-so-far: validate the shape before the second review round
```

Rules:

- Use ISO-8601 UTC time, a trigger slug from the table, and the stage or phase.
- Keep `observation` to one line; `evidence` links the durable record.
- `lesson-so-far` is optional and may be revised in the final entry.
- Never put secrets, personal data, or speculation in a seed.
- Write the seed into the change directory so it travels with the change.

## Entry template

```md
## YYYY-MM-DD — <kind> `<change>` (issue #N, PR #M)

Context: <one sentence: what landed and why this is a landmark.>

### Friction
- <what fought the work; include counts or rounds.>

### Late-caught defects
- <what escaped which gate; how it was caught; follow-up #N.>

### Scope surprises
- <what changed after approval; who authorised it; where it is recorded.>

### Learnings
- <generalisable rule, one line each.>

### Follow-ups filed
- #N `title` (priority) — or "None."
```

`<kind>` is one of `policy`, `defect`, `incident`, `friction`, `scope`, or
`landing`. Use the most specific kind.

Rules:

- **Evidence only.** Every claim links an issue, PR, commit, check run,
  archived change, or `file:line`. "I think" is not evidence.
- **One to three bullets per section.** Omit a section with nothing to say.
- **At most 250 words.** The registry is an index of lessons, not a report.
- **Describe systems and decisions, not people.** No blame and no personal
  data. A human decision is cited by its record, not by the person.
- **Do not restate the issue, spec, or changelog.** Link them.
- **Do not put binding decisions here.** If the work changed a rule, update the
  binding docs and cite them; the entry records why it was difficult.
- **No TODOs.** File follow-ups before the entry lands, or write "None."
- **Unknown is allowed.** If the evidence does not settle a point, say so.
  Invented detail is worse than a gap.
- **Do not copy the post-solve comment.** The comment is the per-issue report;
  the entry is the cross-issue lesson.

## Example

```md
## 2026-01-14 — policy `typed-tooling` (issue #12, PR #18)

Context: The repository moved to typed Python and a pinned toolchain in one
change.

### Friction
- Three review rounds for one policy reversal because the docs, the contract
  tests, and a bundled skill each carried a copy of the old rule.

### Late-caught defects
- The contract test banned a directory the docs allowed; caught only when the
  archive flow touched it. Follow-up: #19.

### Learnings
- Retire every mirror of a rule — docs, tests, bundled skills — in one pass.

### Follow-ups filed
- #19 `ci: align the contract test with the directory rule` (P2)
```

## Review checklist

Before the entry is committed:

1. Does a trigger from the table actually apply?
2. Is every claim linked to durable evidence?
3. Are follow-ups filed as issues, or explicitly "None"?
4. Is it at most 250 words with empty sections removed?
5. Did any rule change go into the binding docs instead?
6. Does it avoid blame, personal data, tokens, and secrets?
7. Is it appended newest-first, with no historical entry rewritten?
