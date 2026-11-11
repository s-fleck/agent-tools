# Architecture

> Binding. Priorities and invariants are added, changed or removed only
> through an approved OpenSpec change; rewording without changing the meaning
> is free, and so is the rest of this document. Work that would break an
> invariant stops and is raised with the user. Behavior: openspec/specs/.
> Decisions: openspec/changes/archive/. Vocabulary: GLOSSARY.yaml.
> Scope: VISION.md.

## Bird's Eye View

<What problem the system solves and its overall shape: the main parts, how
they connect, and the external systems they talk to. A small diagram is
welcome; stay at the level of layers or top-level areas.>

## Code Map

### <area>

<What it owns; the key modules or types to search for.>

## Cross-Cutting Concerns

<Optional and descriptive, e.g. how errors are reported and where they are
handled. Rules go under Invariants. Delete this section if there is nothing to
say.>

## Priorities

- <Quality A> over <quality B>: <one clause on what that means in practice>.

## Invariants

- <Area> never <does/depends on X>. Why: <change-name>.
- Only <area> writes <durable state>. Why: <change-name>. Checked by: <tool or
  rule name>.
