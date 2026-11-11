---
name: binding-docs
description: >
  Use in an OpenSpec project when creating, editing, auditing or reviewing its
  binding docs in the repository root — `VISION.md`, `ARCHITECTURE.md` and
  `GLOSSARY.yaml` (a DDD-inspired ubiquitous language) — e.g. "set up the
  project docs", "which doc does this belong in", "is this a non-goal", "add
  this term to the glossary", "is this an invariant", "write the architecture
  overview", or when docs drift from specs or code.
metadata:
  author: Stefan Fleck
  version: "1.1.0"
---

# Binding Docs

Binding docs hold the few facts about a project that agents and humans must
respect and that rarely change: what the product is for and not for, the shape
of the system and its invariants, and the domain vocabulary. Everything else
lives in OpenSpec specs, archived changes, the code or ordinary project docs.

This skill assumes the project uses OpenSpec. Behavior lives in
`openspec/specs/`; the reasoning behind a decision lives in the archived
change that made it, under `openspec/changes/archive/`.

## What "binding" means

The binding facts are:

- the **purpose statement** and the **non-goals** in VISION;
- the **priorities** and **invariants** in ARCHITECTURE;
- each existing glossary **term and its meaning**.

Adding, changing or removing a purpose statement, non-goal, priority or
invariant, and renaming, retiring or changing the meaning of a glossary term,
goes through an OpenSpec change (see
[Changing a binding fact](#changing-a-binding-fact)).

Free, and reported to the user: adding a glossary term, adding to `avoid` or
`see`, editing anything in ARCHITECTURE other than Priorities and Invariants,
and rewording anything without changing its meaning.

A task **collides** with a binding fact when it would break an invariant, go
against the purpose or a non-goal, or use a glossary term against its meaning.
Priorities guide choices; they do not block work, but reversing or reordering
one is a binding change. On a collision the agent stops and reports it to the
user, offering a proposal; it neither works around the fact nor starts a
proposal unasked.

## The Set

All three live in the repository root, where humans and agents look first and
no documentation tool claims the space. Exclude them from package builds where
the ecosystem requires it (e.g. `.Rbuildignore`).

| Doc | Owns | Template |
|---|---|---|
| `VISION.md` | What the product is for and what it deliberately is not | `assets/VISION.md` |
| `ARCHITECTURE.md` | Bird's eye view, code map, priorities, invariants | `assets/ARCHITECTURE.md` |
| `GLOSSARY.yaml` | Domain terms and their meanings | `assets/GLOSSARY.yaml` |

Copy the template when creating a doc: keep its header, drop pointers to docs
the project does not have, replace every `<placeholder>` and delete the
example entries.

The header is one notice for readers that never load this skill. It names
what is binding in that doc, that changing it needs an approved OpenSpec
change, and that colliding work stops and is raised with the user. It does not
restate the change procedure or the free changes; those stay here. Keep
navigation, such as ARCHITECTURE's pointers to the other docs, on its own line
below the notice.

Create only what the project needs. A small project may have only VISION.
Create the glossary at the first naming collision or disputed term; never
create an empty doc to fill a template.

Agents must find the set without this skill. Make sure whatever instructions
file the project's agent harness loads, and OpenSpec's project context
(`openspec/config.yaml` `context:`, or `openspec/project.md` in older layouts),
point to these files and do not restate them.

## One Fact, One Home

Ask in order; stop at the first yes.

1. Does it **define what a domain word means**? → `GLOSSARY.yaml`.
2. Is it about **what users get or don't get** — purpose or a scope boundary?
   → `VISION.md`.
3. Is it **observable from outside the system** — behavior a user, client or
   operator can see (commands, config fields, endpoints, failure classes)? →
   the owning OpenSpec spec, even when it holds across capabilities ("every
   endpoint requires authentication").
4. Is it about **how the system is built** and holds across capabilities —
   layering, dependency direction, ownership of state, a boundary, a trade-off
   priority? → `ARCHITECTURE.md`.
5. Is it **why** a decision was made? → the change that made it.
6. Is it a rule for **how agents work** in the repo? → the agent instructions
   file.
7. Anything else → manifests, CI, ordinary project docs or git history.

Tie-breaker for 2 vs 4: "we never store card data" is a non-goal when it limits
what the product offers, an invariant when it constrains how the code is built.
Pick one; the other doc may link.

When two places state the same fact, the owner keeps it and the other gets one
line plus a link at most. Before deleting a fact, move it to its home or
confirm it is obsolete.

## The Stability Rule

Write at a level of abstraction that survives months of feature work without
an edit. If a routine change — a new command, a new module, a dependency bump —
would force an edit, the doc is too detailed: move that detail to its owner.
No versions, package lists or `Status:`/date headers; git records when a doc
changed.

## Changing a Binding Fact

1. The OpenSpec change that needs it quotes the new or changed wording in
   `proposal.md` under Impact, and says why under Why (or in `design.md` when
   the change has one).
2. The user's approval of the proposal is the confirmation. A direct user
   instruction to make that change counts too. Without either — including in
   non-interactive runs — stop and report.
3. The binding doc is edited in the same change, before archive. When the
   change has a `tasks.md`, the edit is a task in it; apply works only through
   tasks.
4. An invariant names the change that established it: `Why: <change-name>`
   (archived as `openspec/changes/archive/<date>-<change-name>/`). When a later
   change supersedes it, the name moves to the newer change. Keep change names
   unique so the reference stays unambiguous.

A binding change with no behavior change is its own docs-only change. Its
minimum is `proposal.md` (Why, and Impact quoting the wording) plus
`skip_specs: true` in the change's `.openspec.yaml`; no specs, design or tasks
are needed. Edit the doc, run `openspec validate`, and archive once the user
approves. The archive step flags design and tasks as incomplete; that is
expected, confirm it.

The first version of the set lands the same way: one docs-only change whose
proposal quotes the purpose statement, non-goals, priorities and invariants.
Glossary terms need no quoting. Invariants with no earlier recorded change name
this one.

## VISION

A broad statement of what the product is designed to do; typically ten to
twenty lines, not a limit.

- The **purpose statement** says what the product does, for whom, and the
  problem it solves.
- **Non-goals are the guardrail.** Write the ones that block plausible scope
  creep, not obvious ones.
- Do not list capabilities; `openspec/specs/` is that list.
- No roadmap, milestones or success metrics; they date quickly.

## ARCHITECTURE

Follows matklad's ARCHITECTURE.md convention
(<https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html>): a short map for
a newcomer, written so it rarely needs an update. This skill adds Priorities,
pulls the invariants out of the code map into one list, and makes both
binding. Typically 40–100 lines, not a limit.

- **Bird's Eye View** says what problem the system solves and its overall
  shape, including the external systems it talks to.
- **Code Map** stays at top-level areas and answers "where is the thing that
  does X?" and "what does this thing do?". Name areas, modules and key types;
  do not link source files or line numbers. Below that level, the code is the
  map.
- **Cross-Cutting Concerns** is optional and descriptive: how errors are
  reported and where they are handled, how configuration flows. Any
  *must / never / only* rule belongs under Invariants instead.
- **Priorities** are the trade-offs the system makes on purpose, phrased as
  "A over B" ("correctness over latency"). They guide agents where no
  invariant applies.
- **Invariants are the point.** Phrase them as *must / never / only* so a change
  can be checked against them; call out absences ("nothing in `core` depends on
  `ui`"). Reasoning stays in the change each one names.
- Enforce an invariant mechanically where possible (import linter, architecture
  test, lint rule) and name the tool or rule, not a file path.
- Do not summarize specs; cross-capability structure is the one thing no spec
  owns.

## GLOSSARY

`GLOSSARY.yaml` is a ubiquitous language inspired by domain-driven design: one
vocabulary used identically by domain experts and developers, in
conversation, specs, docs and code. It is not full DDD; bounded contexts and
context maps are out of scope. `assets/GLOSSARY.yaml` shows the form.

| Key | Required | Content |
|---|---|---|
| `term` | yes | The canonical word or phrase |
| `meaning` | yes | One or two sentences: what it is, not how it is implemented |
| `avoid` | no | List of words people drift toward for this concept |
| `see` | no | List of related terms, each an existing `term` |

`retired` entries have `term` and either `replacement` (an existing `term`) or,
when there is none, a `meaning` saying what the word used to mean.

A new glossary starts from the template with its header and the first real
entry; add `retired:` only when the first term is retired.

Rules:

- **Admission.** A term earns an entry when domain experts use the word and it
  is easy to confuse with a nearby word or means something narrower than
  everyday usage. Verbs, events and states qualify, not just nouns. Generic
  technical vocabulary (cache, request, queue) stays out.
- **One term per concept.** Synonyms go under `avoid`, never as their own
  entries.
- **One meaning per term.** When a word has two meanings in the project, make
  two qualified terms ("Billing account", "User account") and put the bare
  word under `avoid` in both.
- **Code follows the glossary.** Code names for a domain concept derive from
  its term (`BillingAccount`). The glossary records no code names; grep finds
  them. In an existing codebase, report mismatches once as a finding rather
  than renaming in passing.
- **Rename completely.** The old word goes to `retired` if it was ever a code
  name or appeared in specs or issues, otherwise to `avoid`.
- **Retire, don't delete**, so old issues and commits stay readable.
- **YAML form.** Sort `terms` and `retired` by `term`, case-insensitive.
  Prefer plain scalars; quote or use `>-` where a parser would misread them,
  and parse the file after every edit.

## Audit

When creating the set, reviewing a change that touches it, or on request,
check what the rules above do not make obvious:

- [ ] Every invariant still holds in the code and names its change.
- [ ] Every other binding change traces to a change whose proposal quotes it:
      in the change under review, or across the doc's `git log` on a full
      audit.
- [ ] `see` and `replacement` name existing terms; no `avoid` word is used for
      its concept in new code or specs.
- [ ] Each doc keeps a header notice as described in [The Set](#the-set); the
      agent instructions file and the OpenSpec
      project context point to the set.

Report findings; binding facts change only as described above.
