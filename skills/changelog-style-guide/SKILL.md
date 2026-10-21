---
name: changelog-style-guide
description: >
  Conventions for writing and editing CHANGELOG.md entries. Use when adding a
  changelog entry, editing the [Unreleased] section, cutting a release, or
  reviewing a changelog for style — covers Keep a Changelog structure, area
  prefixes, imperative mood, breaking changes and unreleased consolidation.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

# Changelog Style Guide

Changelogs follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Entries are written
for users reading a release, not for developers reviewing commits.

## When To Use

- Adding an entry for work just finished.
- Editing or consolidating the `[Unreleased]` section.
- Cutting a release (turning `[Unreleased]` into a version block).
- Reviewing a changelog for style conformance.

## The Unreleased Section Is Not A Development Log

**An unreleased feature is ONE entry that you rewrite as the feature evolves.**

This is the rule agents break most. Before shipping, iterations on a feature —
bug fixes, UI polish, refinements — are **not** changelog entries. They are
edits to the feature's existing `### Added` entry.

Working on something already listed under `[Unreleased]`?
**Update that entry. Do not add a second one.**

**No exceptions:**
- A pre-ship bug fix does NOT get its own `### Fixed` entry.
- A pre-ship redesign does NOT get its own `### Changed` entry.
- Not even when the fix is user-visible, or the change is large.
- Categorizing by "nature of the change" is the wrong axis here — the axis is
  *what ships*.

| Rationalization | Reality |
|---|---|
| "It's genuinely a bug fix, so it belongs under Fixed" | It's a bug the user never saw. It shipped working. One `Added` entry. |
| "Keep a Changelog says categorize by type" | Type categories apply to *released* changes. Unreleased = one entry per feature. |
| "The UI redesign is a separate change" | Same feature, same release cycle → same entry. |
| "Merging loses detail" | The detail is development history. Users want the feature. |
| "Both entries are useful to reviewers" | Reviewers read the diff. The changelog is for users. |

```markdown
✅  ### Added
    - **Rest Timer:** Add configurable rest timer with notification support

❌  ### Added
    - **Rest Timer:** Add rest timer
    ### Changed
    - **Rest Timer:** Improve timer UI
    ### Fixed
    - **Rest Timer:** Fix notification bug
```

Every time you touch `[Unreleased]`, re-read the whole section and consolidate
what the new entry supersedes.

### Merge Heuristics

| Scenario | Merge? |
|---|---|
| Same area + same feature (one refines or fixes the other) | ✅ into `Added` |
| Same feature scattered across `Added`/`Fixed`/`Changed` | ✅ into `Added` |
| Same area, genuinely different features | ❌ keep separate |
| Different areas | ❌ keep separate |
| Fix for an **already released** feature | ❌ new `Fixed` under the new version |

**Summary:** merge when entries target the same user-facing feature in the same
release cycle.

## Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Stats:** Add best sets and record display

## [0.13.0] - 2026-06-21

### Fixed

- **Stats:** Fix crash on empty workout list
```

- `[Unreleased]` is always present, always at the top.
- Version header: `## [x.y.z] - YYYY-MM-DD` — brackets, ISO date, hyphen around the date.
- Versions in reverse chronological order, each version exactly once.
- Yanked release: `## [0.5.0] - 2026-06-01 [YANKED]`.
- Only these six change types, in this order, empty ones omitted:
  `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`.
- Within a section, sort by area name alphabetically, then by importance.
  Entries with no area prefix sort first.

## Writing Entries

- **Imperative mood** — "Fix crash", never "Fixed crash" or "Fixes crash".
- **Capitalize** the first word of the entry, and the first word after `**Area:**`.
- **No trailing period** for a single sentence; use periods when there are several.
- **One logical change per bullet.**
- **Active voice, subject first** — "Add import of Strong CSV files", not
  "Strong CSV files were added", and not context or caveats up front.
- **Describe the change, not the work** — "Reduce session editor re-renders by
  40%", not "Spent time profiling render paths".
- **Aim for one line.** If context is needed, prefer a parenthetical or a
  conjunction over a second sentence.

Three accepted shapes:

1. Direct — `Fix crash on empty workout list`
2. Scoped — `**History Editor:** Fix discard workout functionality`
3. Scoped + justification — `**DB:** Change entity format from YAML to JSON to improve population speed`

Every entry must pass the **"so what?" test**: if a user can't tell why it
matters, rewrite it.

| Instead of | Write |
|---|---|
| Refactor muscle groups | **Exercises:** Reorganize muscle group hierarchy |
| Various performance improvements | **Session Editor:** Reduce re-renders in set row |
| Internal improvements | **History Editor:** Stabilize undo/redo state across navigations |
| Minor fixes | (name the actual fix) |

Never paste raw git log lines, never write vague summaries, never use ambiguous
date formats.

## Area Prefixes

Group entries by subsystem with an `**Area:**` prefix — the colon goes *inside*
the bold markers. Encouraged but optional; be consistent within a release.

```markdown
- **Stats:** Add best sets and record display
- **Stats/Heatmap:** Fix day header not scrolling horizontally with grid
- **Session & History Editor:** Enable drag-and-drop reorder of exercises
```

- `/` denotes a sub-area of a larger area.
- `&` combines areas, but only for a single atomic change affecting both —
  otherwise write separate entries.

## Breaking Changes

Prefix the entry with `**Breaking:**`, inside the relevant section. Do not
describe the break in prose instead.

```markdown
### Changed

- **Breaking:** Remove deprecated `initial_value` column from exercise metrics
```

`**Breaking:**` replaces the area prefix rather than stacking with it — name the
area in the sentence instead. Migration instructions belong in a migration
guide, not in the entry.

## Choosing A Section

Most entries are obvious. For the recurring ambiguous cases:

| Change | Section |
|---|---|
| Performance or behaviour improvement to something that already worked | `Changed` |
| Repair of something visibly broken for users | `Fixed` |
| Removal that breaks compatibility | `Changed` with `**Breaking:**`, or `Removed` for a clean removal |
| Anything on an unreleased feature already listed | none — edit its `Added` entry |

## Pre-Commit Validation

Verify before finishing any changelog edit:

1. Version header is `## [x.y.z] - YYYY-MM-DD`, hyphen included.
2. Bold area prefix is `**Area:**`, colon inside the bold markers.
3. First word after the prefix (or at the start of the entry) is capitalized.
4. Imperative mood — "Add", "Fix", "Remove".
5. No trailing period on single-sentence entries.
6. Entries within each section sorted alphabetically by area.
7. Breaking changes carry the `**Breaking:**` prefix.
8. `[Unreleased]` consolidated — one entry per feature, no pre-ship
   `Fixed`/`Changed` entries for features that haven't shipped.

## Red Flags — Stop And Reconsider

- You are adding a `### Fixed` or `### Changed` entry for a feature that is
  already listed under `[Unreleased]`.
- You are about to write "Various", "Minor", "Internal", or "Refactor".
- Your entry starts with a past-tense verb.
- You described a breaking change without the `**Breaking:**` prefix.
- You added to `[Unreleased]` without re-reading the rest of the section.
