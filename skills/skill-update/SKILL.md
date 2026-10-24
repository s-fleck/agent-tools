---
name: skill-update
description: >
  Use when changing a skill — creating a skill, amending a project copy with
  project-specific rules, marking a copy as a variant, pulling upstream changes
  into a variant, bumping a skill's version, renaming or forking a skill,
  writing its changelog entry, or syncing a project's amendments back into the
  canonical skill repo.
metadata:
  author: Stefan Fleck
  version: "3.0.0"
---

# Skill Update

When a project vendors a skill this repo owns, the skill exists in two places: the **canonical copy** in the skill repo (upstream: <https://github.com/s-fleck/agent-tools>) and the **project copy** the project vendored from it. This skill is the procedure for changing one without losing the difference between the two.

Below, `<name>` is the canonical skill ID and `<project-name>` is the project copy's directory name; they differ only after a rename. `<project-skill-dir>` is the project's skills source that contains the copy.

## Scope

This procedure covers skills with a canonical copy in `agent-tools`. It does not cover:

- **Third-party skills** — leave their metadata alone; fork under a new name if the project needs changes.
- **Project-owned skills** — no canonical upstream and no variant markers; version them in the project, and use the fork/creation flow if one graduates to canonical.

Initial vendoring is a straight directory copy; verify the copy is byte-identical, add no markers. See the repository README for the vendoring commands.

## When To Use

- Creating a skill and adding it to the canonical repo.
- Amending a project copy of a skill with a project-specific rule, example, or path.
- Pulling upstream changes into a variant.
- Syncing a project's amendments back into the canonical copy.
- Renaming or forking a skill.
- Bumping a skill's version and recording it in the changelog.

## The Two Copies

| Role | Lives in | Metadata |
|------|----------|----------|
| Canonical | `~/workspace/agent-tools/skills/<name>/` | `author` + `version`; no variant markers |
| Project copy | `<project-skill-dir>/<project-name>/` | `author` + `version`, plus `variant`/`upstream`/`local_changes` once amended |

The project's skill sources are `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/`; a project may also add custom paths in `opencode.json`. Project `.opencode` takes precedence over the compatibility directories, and explicit `skills` entries come later still, so a duplicate ID in any source can shadow the copy you meant to edit. Never edit a global copy (`~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`) thinking it is the project copy.

The canonical copy is upstream. A project copy is in one of these states:

| Local amendments | Base current | State |
|---|---|---|
| no | yes | **in sync** — byte-identical to the canonical version it was vendored from |
| no | no | **stale** — upstream moved on; re-vendor, or amend against the old base |
| yes | yes | **variant** |
| yes | no | **variant behind upstream** — pull upstream first, or amend against the old base |
| untracked | any | **drift** — reconcile before editing |

- An in-sync copy is unamended and current. Do not touch it; the first change turns it into a variant.
- A stale copy is unamended but behind. Re-vendor to catch up; if you need a local change instead, it becomes a variant behind upstream.
- A variant has intentional local amendments and says so in its metadata.
- Drift is an unexplained difference. Diff it, decide what is local, and add the variant markers before editing further.

To check an unamended copy, diff it against current canonical:

```bash
diff -ru ~/workspace/agent-tools/skills/<name> <project-skill-dir>/<project-name>
```

A non-empty diff means the copy is stale or drifted. For a variant, diff against the base recorded in `upstream` instead; every hunk must be explained by `local_changes`, and an unexplained hunk is drift. A diff against current canonical also shows upstream drift, which is not a local amendment.

### Locating the Project Copy

Find the directory by its skill ID (the directory name, not the frontmatter display name):

```bash
find <project>/.opencode/skills <project>/.claude/skills <project>/.agents/skills \
  -name SKILL.md 2>/dev/null | grep '/<project-name>/'
```

If more than one source contains the ID, stop and resolve the duplicate before editing; OpenCode loads one by precedence.

## The Canonical Repo

The upstream location is fixed — do not parameterize it or guess another path:

- **Repository:** <https://github.com/s-fleck/agent-tools>
- **Local checkout:** `~/workspace/agent-tools`; the canonical copy of `<name>` is `~/workspace/agent-tools/skills/<name>/`.

Both paths are hard-coded on purpose. If the checkout is missing, clone it:

```bash
git clone https://github.com/s-fleck/agent-tools ~/workspace/agent-tools
```

If it is missing and cannot be cloned, stop and ask — do not substitute another checkout or a stale copy of the repo.

When working in `~/workspace/agent-tools`, you are editing canonical copies; there is no project copy in that repo. When working in a project, edit the project copy and sync the generic lesson back separately.

## Anatomy

A skill is a directory `skills/<name>/` holding `SKILL.md`, plus optional `references/`, scripts, and assets. `SKILL.md` opens with YAML frontmatter:

```yaml
---
name: code-review                    # display label; keep equal to the folder name
description: Use when ...            # required; third person, covers what it does + when to trigger
license: MIT                         # optional
compatibility: Requires <runtime> >= <version>    # optional
metadata:                            # optional; flat string → string map, no nesting
  author: Stefan Fleck
  version: "3.0.0"
---
```

- The directory name is the skill ID: case-sensitive, and the repo convention is lowercase kebab-case. The frontmatter `name` is the display label; keep it equal to the folder name.
- `description` is what an agent matches against. Without it the skill is never surfaced; keep the trigger keywords in the first sentence.
- `metadata` values are strings, not lists or maps. A new field is a new key, never a nested structure. Quote `version`.

## Metadata Contract

Canonical copy — no project markers:

```yaml
metadata:
  author: Stefan Fleck
  version: "3.0.0"
```

Project copy with local amendments — three extra keys:

```yaml
metadata:
  author: Stefan Fleck
  version: "3.0.0+acme.1"
  variant: acme
  upstream: code-review@3.0.0
  local_changes: "Package name <project> instead of <pkg>; release timing defers to the project release skill"
```

- `variant` — the project slug that owns the amendments. Its presence is the signal that this copy is a variant.
- `upstream` — `<canonical-skill-name>@<version>` the copy was **actually vendored from**, not the latest canonical version. If canonical has moved on, this stays at the old base until the variant is re-vendored. It carries the canonical name when the project copy was renamed.
- `local_changes` — one line of plain text, semicolon-separated, one clause per current amendment. Cumulative: update it whenever an amendment is added, changed, or removed. It is a summary, not a changelog.
- `version` — the base from `upstream` plus a build suffix `+<project-slug>.<n>` counting local amendment edits. Semver ignores build metadata when comparing precedence, so the suffix is a local counter, not a precedence claim. Use a lowercase, hyphenated project slug; SemVer build metadata allows only alphanumerics and hyphens.
- If the last amendment is removed, re-vendor (or confirm the copy matches its base), then drop all three markers and set `version` to that canonical version.

## Attribution

- `metadata.author` lists the skill's authors, comma-separated, **original author first**:

  ```yaml
  metadata:
    author: "Garrick Aden-Buie (@gadenbuie), Stefan Fleck"
  ```

- A fork **keeps** the original author's credit. Amendments add the amending author to the list; they never replace the original.
- A skill that was rewritten from scratch names only its own author — say so in the changelog entry.
- Carry the upstream `license:` line into the fork (e.g. `license: MIT` for a skill from a MIT-licensed collection) and never change it. If upstream has no `license` line, do not invent one.
- Look the original author up before you credit them: the upstream file, the project's skill lock file (e.g. `.agents/skills/skills-lock.json`), and the upstream repository are the sources. A fork that ships without frontmatter has no recorded author — do not guess one.

## Versioning

Every change to a skill bumps its version. Nothing ships unbumped. This is the
`semver` skill applied to skill guidance: a skill's rules are its public API,
so changing or removing one is MAJOR.

Classify the whole change set; the highest bump wins. Do not bump once per hunk.

| Change | Bump | Example |
|--------|------|---------|
| Typo, wording, formatting, a clarification that does not change guidance | PATCH | 2.3.0 → 2.3.1 |
| New guidance, new section, new option — additive, contradicts nothing | MINOR | 2.3.0 → 2.4.0 |
| A rule changed or was removed, the frontmatter contract changed, or the skill was renamed | MAJOR | 2.3.0 → 3.0.0 |

- A MAJOR bump resets MINOR and PATCH to 0; a MINOR bump resets PATCH to 0; a PATCH bump increments PATCH. Never bump a lower component without resetting the ones below it.
- Never reuse a version number, not even after a revert.
- A project copy's local amendments bump the suffix: `2.3.0+acme.1` → `2.3.0+acme.2`. The base stays at the upstream version the copy actually came from.
- Re-vendoring resets the suffix: after pulling upstream 2.4.0 in and re-applying the local amendments, the copy is `2.4.0+acme.1`.
- A rename in the canonical repo is a MAJOR bump; the changelog entry names the old skill.
- New skills and forks start at `1.0.0`; pre-1.0 versions are not used for skills. Converting a variant into a fork is a project-copy rename plus a new canonical skill, not a MAJOR bump of the original.

## Changelog

- The canonical repo keeps one changelog at `~/workspace/agent-tools/CHANGELOG.md`, in Keep a Changelog + semver form, per the `changelog-style-guide` skill.
- Every skill version bump gets an entry under `[Unreleased]`, with the skill name as the area prefix.
- Entry shape: `- **<skill>:** <imperative summary> (<new version>)`.
- If the previous version is still under `[Unreleased]`, **rewrite that entry** instead of adding a second one for the same feature.
- A project copy's local amendments are recorded in the **project's** changelog (or `NEWS.md` for R packages), not the canonical one. The canonical changelog records only what landed upstream.

## Amending a Project Copy

1. Locate the project copy (see [Locating the Project Copy](#locating-the-project-copy)); do not edit a global copy.
2. Determine the variant's base from `upstream` (for a first amendment, the copy's current version, which equals the canonical version it was vendored from). Diff the project copy against **that base**, not current canonical, to isolate local amendments. If the copy is stale and you also want the upstream changes, pull them first.
3. Make the smallest edit that states the project's rule. Keep the generic part generic — a project rule belongs in the project copy, not in every copy of the skill.
4. Add or bump the suffix: the first amendment is `+<project-slug>.1`, later amendments increment it. Keep `upstream` at the actual base; if you also pulled current canonical in, set `upstream` to that version and reset the suffix to `+<project-slug>.1`.
5. Refresh `local_changes` cumulatively.
6. If the amendment is a project-wide rule, add a one-line pointer to it in the project's `AGENTS.md` — the skill holds the detail, AGENTS.md points at the skill.
7. Record the amendment in the project's changelog.
8. Do not copy project specifics back into the canonical copy from inside the project.

## Pulling Upstream Into a Variant

1. Read `upstream` to get the base version and canonical name. If the base is already current, there is nothing to pull.
2. Find the commit that introduced the base in the canonical repo:

   ```bash
   git -C ~/workspace/agent-tools log --oneline --reverse \
     -S 'version: "<base-version>"' -- skills/<name>/SKILL.md
   ```

   The first commit in the output introduced the base. If the file does not quote its version, search for the bare version string instead. If no commit matches (shallow clone or rewritten history), fetch the full history or stop and ask.

3. Check out that snapshot and diff the variant against it to capture the local amendments:

   ```bash
   git -C ~/workspace/agent-tools worktree add --detach /tmp/opencode/skill-base-<name> <commit>
   diff -ru /tmp/opencode/skill-base-<name>/skills/<name> <project-skill-dir>/<project-name>
   ```

   Differences are expected; `diff` exits 1 when files differ. Save the local-only hunks. This is the diff you must preserve.

4. Diff the base snapshot against current canonical to see what upstream changed:

   ```bash
   diff -ru /tmp/opencode/skill-base-<name>/skills/<name> ~/workspace/agent-tools/skills/<name>
   ```

5. Re-vendor current canonical into a scratch copy, re-apply the local hunks, and resolve conflicts in favor of the project's intent. Replace the project copy only after the result is reviewed.
6. Set `version` to `<new-base>+<project-slug>.1`, set `upstream` to `<canonical-name>@<new-base>`, and refresh `local_changes`. If every local amendment was promoted upstream, do not re-apply it; remove the variant markers instead.
7. Remove the worktree, update the project changelog, and run the project-amendment validation.

   ```bash
   git -C ~/workspace/agent-tools worktree remove /tmp/opencode/skill-base-<name>
   ```

## Syncing Back to Canonical

1. Locate the project copy and read `upstream`. Diff the project copy against the **base recorded in `upstream`**, not current canonical, to isolate local amendments. Do not classify upstream drift as a local amendment.
2. Classify every hunk:
   - **Generic** — the rule holds for any project → move to the canonical copy.
   - **Project-specific** — names a project file, function, path, token, example, or convention → stays in the project. Genericize the *lesson* into the canonical copy (keep the rule, drop the names) and keep the names in the project copy. If no generic lesson remains, sync nothing.
   - **Project-only artifact** — a section, script, or whole skill that only makes sense in that project → do not sync it. A whole skill that only makes sense there is project-owned, not a variant.
3. Apply to the canonical copy: minimal diff, generic wording, no project names, paths, tokens, or examples. Use placeholders such as `<project>`, `<pkg>`, and `<REPO>_GH_TOKEN`.
4. Bump the canonical version per the table above and add or rewrite the changelog entry.
5. Re-vendor the canonical copy into the project and re-apply the remaining local amendments. If none remain, remove `variant`/`upstream`/`local_changes` and leave the copy byte-identical; otherwise reset the suffix to `+<project-slug>.1`, set `upstream` to the new canonical version, and refresh `local_changes`.
6. Update the project's changelog and the `AGENTS.md` pointer if the rule moved.
7. Update README and cross-references if the canonical change affects them.

## Renaming and Forking

- A renamed project copy: rename the folder (the skill ID) and the frontmatter `name` together, keep the canonical name in `upstream`, note the rename in `local_changes`, and bump the suffix. Update the project's `AGENTS.md`, commands, and other skill references.
- A rename in the canonical repo is a MAJOR bump. Update the README Contents table and vendoring commands, search the repo for the old name (`rg '<old-name>'`), and name the old skill in the changelog entry. Project variants update `upstream` to the new canonical name when they next sync.
- A fork that outgrew the canonical skill gets its own name, its own directory, and its own canonical entry in `~/workspace/agent-tools/skills/`. Start at `1.0.0`, keep the original author and `license`, and say `Fork of <original>@<version>` in the changelog entry. Add the README row and vendoring command. The original stays as it is.
- A fork is not a variant: a fork carries no `variant`/`upstream` markers and has its own history.

## Creating a Skill

1. Directory `skills/<name>/` with `SKILL.md`; the directory name is the ID (lowercase kebab-case), the frontmatter `name` matches it, and the description leads with the trigger keywords.
2. `metadata.version: "1.0.0"`, `metadata.author` set; add `license`/`compatibility` when they apply.
3. Add a row to the `README.md` Contents table and a vendoring command. Document any companion or overlay pairing.
4. Changelog entry under `[Unreleased]` `### Added`, per the `changelog-style-guide` skill.
5. If the skill is adapted from another skill, keep the original author and `license` and say so in the changelog entry; if it is a fork with a new name, follow [Renaming and Forking](#renaming-and-forking).
6. Exercise every command and path in the skill once before shipping.

## Validation

### Canonical change

1. Frontmatter has `name` (aligned with the folder) and `description`; `metadata` values are strings; `version` is quoted.
2. The version is bumped by the highest classification in the change set and not reused.
3. The copy carries no `variant`, `upstream`, or `local_changes`.
4. A changelog entry exists under `[Unreleased]`; if the previous version is still unreleased, the entry was rewritten rather than duplicated.
5. The canonical copy is free of project-specific names, paths, tokens, examples, and skill names.
6. A new, renamed, or forked skill has a README Contents row and vendoring command. For a rename, `rg '<old-name>'` finds no stale references.
7. If the repo ships a doc check, run it. If the documented command is missing, fix the reference or skip; a broken doc-check reference is a repo bug, not a skill failure.
8. The skill ID is unique across the repo and the directory name and frontmatter `name` agree.

### Project amendment

1. The diff is against the base recorded in `upstream`, not current canonical, and contains only the intended local hunks.
2. `variant` matches the project slug; `upstream` is the actual base; `local_changes` lists every current amendment; the suffix is bumped correctly.
3. The version base equals the actual base, not the latest canonical version.
4. The project's changelog is updated; a project-wide rule has an `AGENTS.md` pointer.
5. No project specifics were copied into the canonical copy.
6. The edited copy is the project copy, not a global copy; no duplicate skill ID shadows it.
7. If re-vendored, the base is updated, the suffix reset to `.1`, local amendments re-applied, and `upstream` current. If no amendments remain, the variant markers are gone.
8. If the skill was renamed, the folder, frontmatter `name`, and project references agree.

## Red Flags — Stop And Reconsider

- You are putting project-specific content into the canonical copy.
- You are editing a global copy or a checkout of the upstream repo other than `~/workspace/agent-tools`.
- You set `upstream` to the latest canonical version without porting those changes in.
- You diffed a variant against current canonical and treated upstream drift as a local amendment.
- You copied canonical over a variant without saving the local diff first.
- A project copy has untracked local edits but no `variant` marker.
- A project copy merely lags upstream and you marked it as a variant.
- The version changed but no changelog entry was written.
- A project path, function name, token, example, or skill name reached the canonical copy.
- You bumped PATCH for a rule change, MINOR for a rule that contradicts an existing one, or failed to reset the lower components.
- A version number was reused, or a skill's directory name and frontmatter `name` disagree.
- You added, renamed, or forked a skill without updating the README and cross-references.
- You removed the original author or `license`.
