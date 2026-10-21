---
name: skill-update
description: Use when changing a skill — amending a project copy with project-specific rules, marking a copy as a variant, bumping a skill's version, renaming or forking a skill, writing its changelog entry, or syncing a project's amendments back into the canonical skill repo.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

# Skill Update

A skill exists in two places: the **canonical copy** in the skill repo (upstream) and the **project copy** a project vendored from it. This skill is the procedure for changing a skill without losing the difference between the two.

## When To Use

- Amending a project copy of a skill with a project-specific rule, example, or path.
- Syncing a project's amendments back into the canonical copy.
- Renaming or forking a skill.
- Bumping a skill's version and recording it in the changelog.

## The Two Copies

| Role | Lives in | Frontmatter |
|------|----------|-------------|
| Canonical | `agent-tools/skills/<name>/` | `author` + `version` only |
| Project copy | `<project>/.opencode/skills/<name>/` | `author` + `version`, plus `variant`/`upstream`/`local_changes` once amended |

- The canonical copy is upstream. A project copy is upstream **plus** local amendments, and says so in its metadata.
- An unamended project copy is byte-identical to the canonical copy. Do not touch it.
- Never edit a canonical copy from inside a project: amend the project copy, sync back later.
- A project copy that no longer matches its upstream is a **variant** (see [Metadata Contract](#metadata-contract)).

## Anatomy

A skill is a directory `skills/<name>/` holding `SKILL.md`, plus optional `references/`, scripts, and assets. `SKILL.md` opens with YAML frontmatter:

```yaml
---
name: r-package-style-guide          # required; matches the folder name, lowercase-hyphenated
description: Use when ...            # required; third person, covers what it does + when to trigger
license: MIT                        # optional
compatibility: Requires R >= 4.2    # optional
metadata:                           # optional; flat string → string map, no nesting
  author: Stefan Fleck
  version: 2.3.0
---
```

- `name` must match the folder name — opencode resolves a skill by its folder.
- `description` is what an agent matches against. Without it the skill is never surfaced; keep the trigger keywords in the first sentence.
- `metadata` values are strings, not lists or maps. A new field is a new key, never a nested structure.

## Metadata Contract

Canonical copy — no project markers:

```yaml
metadata:
  author: Stefan Fleck
  version: 2.3.0
```

Project copy with local amendments — three extra keys:

```yaml
metadata:
  author: Stefan Fleck
  version: 2.3.0+fire.1
  variant: fire
  upstream: r-package-style-guide@2.3.0
  local_changes: "Problem: repro stamp and symbol refs; Lifecycle: OpenSpec change link"
```

- `variant` — the project that owns the amendments. Its presence is the signal that this copy is not upstream.
- `upstream` — `<canonical-skill-name>@<version>` this copy was forked from. It also carries the canonical name when the project copy was **renamed**.
- `local_changes` — one line of plain text: what differs from upstream. Update it in the same edit as the change it describes.
- `version` — the upstream version plus a build suffix `+<project>.<n>` counting local amendments. Semver ignores build metadata when comparing precedence, so the suffix is a local counter, not a precedence claim.

## Attribution

- `metadata.author` lists the skill's authors, comma-separated, **original author first**:

  ```yaml
  metadata:
    author: "Garrick Aden-Buie (@gadenbuie), Stefan Fleck"
  ```

- A fork **keeps** the original author's credit. Amendments add the amending author to the list; they never replace the original.
- A skill that was rewritten from scratch names only its own author — say so in the changelog entry.
- Carry the upstream `license:` line into the fork (e.g. `license: MIT` for a skill from a MIT-licensed collection) and never change it.
- Look the original author up before you credit them: the upstream file, the project's skill lock file, and the upstream repository are the sources. A fork that ships without frontmatter has no recorded author — do not guess one.

## Versioning

Every change to a skill bumps its version. Nothing ships unbumped.

| Change | Bump | Example |
|--------|------|---------|
| Typo, wording, formatting, a clarification that does not change guidance | PATCH | 2.3.0 → 2.3.1 |
| New guidance, new section, new option — additive, contradicts nothing | MINOR | 2.3.0 → 2.4.0 |
| A rule changed or was removed, the frontmatter contract changed, the skill was renamed or forked | MAJOR | 2.3.0 → 3.0.0 |

- Bump only the part that changed; leave the other components alone.
- Never reuse a version number, not even after a revert.
- A project copy's local amendments bump the suffix: `2.3.0+fire.1` → `2.3.0+fire.2`. The base still tracks upstream.
- Re-vendoring resets the suffix: after pulling upstream 2.4.0 in and re-applying the local amendments, the copy is `2.4.0+fire.1`.
- A rename in the canonical repo is a MAJOR bump; the changelog entry names the old skill.

## Changelog

- The canonical repo keeps one `CHANGELOG.md` at its root, in Keep a Changelog + semver form, per the `changelog-style-guide` skill.
- Every skill version bump gets an entry under `[Unreleased]`, with the skill name as the area prefix.
- Entry shape: `- **<skill>:** <imperative summary> (<new version>)`.
- A project copy's local amendments are recorded in the **project's** changelog, not the canonical one. The canonical changelog records only what landed upstream.

## Amending a Project Copy

1. Read the canonical copy and the project copy; diff them before editing.
2. Make the smallest edit that states the project's rule. Keep the generic part generic — a project rule belongs in the project copy, not in every copy of the skill.
3. Bump the suffix, set `upstream` to the canonical version, refresh `local_changes`.
4. If the amendment is a project-wide rule, add a one-line pointer to it in the project's `AGENTS.md` — the skill holds the detail, AGENTS.md points at the skill.
5. Do not copy project specifics back into the canonical copy from inside the project.

## Syncing Back to Canonical

1. Diff: `diff -ru agent-tools/skills/<name> <project>/.opencode/skills/<name>`.
2. Classify every hunk:
   - **Generic** — the rule holds for any project → move to the canonical copy.
   - **Project-specific** — names a project file, function, path, token, or convention → stays in the project. Genericize the *lesson* into the canonical copy (keep the rule, drop the names) and keep the names in the project copy.
   - **Project-only artifact** — a skill that only makes sense in that project → do not sync it.
3. Apply to the canonical copy: minimal diff, generic wording, no project names, no tokens.
4. Bump the canonical version per the table above and add the changelog entry.
5. Re-vendor the canonical copy into the project and re-apply the local amendments: reset the suffix to `+<project>.1`, refresh `upstream` and `local_changes`.
6. Verify: `Rscript scripts/check-docs.R` in the canonical repo, then grep the canonical copy for project names, paths, and tokens.

## Renaming and Forking

- A renamed project copy: rename the folder **and** the frontmatter `name` together, and keep the canonical name in `upstream`. The canonical repo keeps its own name; a rename in the canonical repo is a MAJOR bump.
- A fork that outgrew the canonical skill gets its own name, its own directory, and its own canonical entry in the skill repo. The original stays as it is.
- A fork is not a variant: variants carry `variant`/`upstream`; a fork is a separate skill with its own history.

## Creating a Skill

1. Directory `skills/<name>/` with `SKILL.md`; `name` matches the folder, `description` leads with the trigger keywords.
2. `metadata.version: 1.0.0`, `metadata.author` set.
3. Changelog entry under `[Unreleased]`.

## Validation

Before finishing any skill change:

1. Frontmatter has `name` (matching the folder) and `description`; `metadata` values are strings.
2. The version is bumped, correctly classified, and not reused.
3. A project copy carries `variant`, `upstream`, `local_changes`; a canonical copy carries none of them.
4. A changelog entry exists under `[Unreleased]`.
5. The canonical copy is free of project-specific names, paths, and tokens.
6. `Rscript scripts/check-docs.R` reports no errors.
7. Project copies that were re-vendored have an updated `upstream` and a reset suffix.

## Red Flags — Stop And Reconsider

- You are editing the canonical copy while working inside a project.
- A project copy diverges from upstream but carries no `variant` marker — the next sync will not know what to pull back.
- The version changed but no changelog entry was written.
- A project path, function name, or token reached the canonical copy.
- You bumped PATCH for a rule change, or MINOR for a rule that contradicts an existing one.
- A version number was reused, or a skill's `name` no longer matches its folder.
