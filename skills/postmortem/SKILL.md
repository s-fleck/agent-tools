---
name: postmortem
description: >
  Use when a change triggers a postmortem — a binding-doc, contract, schema,
  or dependency-baseline change; an escaped defect, revert, or incident;
  repeated friction; a reversed scope decision; or a novel landing failure —
  and when finalizing a change at archive. Covers trigger detection, durable
  seed capture, registry consolidation, follow-up filing, and the evidence
  rules for POSTMORTEMS.md entries.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

# Postmortem

A postmortem is a **landmark learning record**, not a session diary. It
explains why a piece of work was harder or riskier than it should have been,
and what should change next time. It is not a restatement of the issue, the
spec, or the changelog.

Read `references/style-guide.md` before writing or reviewing an entry. It holds
the trigger table, seed format, registry contract, entry template, and evidence
rules.

## Two artifacts, one word

Do not conflate them:

| Artifact | Audience | When | Content |
|---|---|---|---|
| **Post-solve comment** | the issue thread | after merge | shipped, checks, rulings, deviations, follow-ups |
| **Postmortem entry** | future maintainers | landmark events only | friction, late-caught defects, scope surprises, learnings |

The comment is per issue and routine. The entry is cross-issue and
exceptional. A routine solved issue gets a comment, not a registry entry.

## Lifecycle

### 1. Detect the trigger

Use the trigger table in `references/style-guide.md`. If no trigger fires, do
nothing. Do not write a postmortem for routine work.

### 2. Seed immediately

Write the seed when the event happens, not at the end of the session. Later
stages and later sessions start fresh and cannot recover the conversation.

- **Sink:** a file in the change directory. For OpenSpec changes, use
  `openspec/changes/<id>/postmortem.md`; otherwise use the path the project's
  `AGENTS.md` names, or a note that travels with the change.
- **If the change does not exist yet:** create the seed at the first durable
  point after the change exists, and record the earlier event with its evidence
  links.
- **Shape:** append-only and short — timestamp, trigger, stage, one-line
  observation, evidence. The format is in the style guide.
- **Persistence:** write it into the change directory so the apply/archive flow
  commits it with the change. Never leave it only in conversation or in an
  untracked scratch file.

### 3. Consolidate at archive

The archive boundary — the last pre-merge step that can commit — is the
**only writer** of the registry.

Before the archiving commit:

1. Read every seed for the change.
2. Re-check the durable record: issue, pull request, commits, checks, archived
   change. Seeds are pointers, not proof.
3. File agreed follow-ups as issues. Nothing survives in scratch; no TODOs.
4. Append one entry to the registry, newest first.
5. Commit the registry with the archive and changelog.
6. Leave the seed in the archived change as provenance; the registry entry is
   the curated summary.

If the archive already happened and the entry was not written, do not
reconstruct it from memory. Record the gap and stop; a later human may add an
evidence-based entry.

### 4. Publish after merge

If the workflow has a post-merge stage, it publishes the post-solve comment and
may propose follow-ups. It **does not** write the registry: it runs after
merge, has no session memory, and must not modify the base. The archive entry
is the durable record.

## What belongs in an entry

- **Friction** — where the process fought the work; include counts or rounds.
- **Late-caught defects** — what escaped which gate, how it was caught,
  follow-up.
- **Scope surprises** — what changed after approval, who authorised it, where
  it is recorded.
- **Learnings** — generalisable rules, not a restatement.
- **Follow-ups** — actual issue numbers, or "none".

Omit empty sections. Link evidence. Never blame people, include personal data,
tokens, or secrets. A rule change goes into the binding docs; the postmortem
records why the rule was hard to get right, then cites the doc.

## When to skip

- Routine feature or bug fix with no decisions, rework, or surprise.
- A single review finding fixed immediately.
- A mechanical failure the process already handles (transient CI retry, flaky
  network) unless it revealed a real gap.
- Work that never landed and has no durable record; record the gap instead of
  inventing history.

## Red flags

- Writing the entry at the end of a session from memory.
- Writing the registry after merge.
- A per-issue entry for every issue.
- An entry without links to the issue, PR, commit, or archived change.
- A "learning" that is actually a decision that belongs in a binding doc.
- Follow-ups described but not filed.
- Blame, personal data, tokens, or secrets.
