---
name: skill-update
description: >
  Use when changing an OpenCode skill or command — creating a skill or slash
  command, amending a project copy with project-specific rules, marking a copy
  as a variant, pulling upstream changes into a variant, bumping a skill's
  version, renaming or forking a skill, writing its changelog entry, syncing a
  project's amendments back into the canonical repo, or updating a command's
  template and frontmatter. Also covers parallel-safe canonical landings.
metadata:
  author: Stefan Fleck
  version: "5.0.1"
---

# Skill Update

When a project vendors a skill this repo owns, the skill exists in two places: the **canonical copy** in the skill repo (upstream: <https://github.com/s-fleck/agent-tools>) and the **project copy** the project vendored from it. This skill is the procedure for changing one without losing the difference between the two.

Below, `<name>` is the canonical skill ID and `<project-name>` is the project copy's directory name; they differ only after a rename. `<project-skill-dir>` is the project's skills source that contains the copy.

## Before You Edit

Read `references/style-guide.md` before changing a skill or command. It contains the stable form rules: platform layout and discovery, canonical anatomy, frontmatter and variant metadata, attribution, versioning, changelog, and command authoring. It is not auto-loaded; read it explicitly.

The procedure below is the state machine: which copy you are changing, how to preserve local amendments, and how to land the result. The style guide is the form contract.

Non-negotiables:

- Skills are directories (`skills/<name>/SKILL.md` canonically); commands are single files (`commands/<name>.md`). A skill root holds `SKILL.md` plus optional `references/`, `scripts/`, and `assets/` only.
- Every changed skill bumps `metadata.version` and gets a `CHANGELOG.md` entry.
- Canonical copies stay generic; project names, paths, tokens, and examples stay in the project copy.
- A variant carries `variant`, `upstream`, `upstream_commit`, and `local_changes`; the exact contract is in the style guide.

## Scope

This procedure covers skills and commands with a canonical copy in `agent-tools`. The variant and metadata contract applies to skills; commands use the simpler file-based lifecycle in the style guide's **Command Authoring** section. It does not cover:

- **Third-party skills** — leave their metadata alone; fork under a new name if the project needs changes.
- **Project-owned skills** — no canonical upstream and no variant markers; version them in the project, and use the fork/creation flow if one graduates to canonical.

Initial vendoring is a straight copy: the whole directory for a skill, the single `.md` file for a command. Verify the copy is byte-identical and add no markers. See the repository README for the vendoring commands.

## When To Use

- Creating a skill and adding it to the canonical repo.
- Creating or changing an OpenCode slash command, or vendoring one into a project.
- Amending a project copy of a skill with a project-specific rule, example, or path.
- Pulling upstream changes into a variant.
- Syncing a project's amendments back into the canonical copy.
- Renaming or forking a skill.
- Bumping a skill's version and recording it in the changelog.
- Landing a canonical change while other writers are active (parallel updates).
- A push was rejected and you need to rebase and re-validate.
- A `Skill Validation` run for a landed change is red and you need to fix
  forward.

## The Two Copies

| Role | Lives in | Metadata |
|------|----------|----------|
| Canonical | `~/workspace/agent-tools/skills/<name>/` | `author` + `version`; no variant markers |
| Project copy | `<project-skill-dir>/<project-name>/` | `author` + `version`, plus `variant`/`upstream`/`upstream_commit`/`local_changes` once amended |

A project copy may also be a flat `<project-skill-dir>/<project-name>.md`. It has no private directory for supporting files and no neighboring-file sample; prefer the directory form when the skill ships `references/`, scripts, or assets. The variant checker expects the directory form; validate a flat variant's frontmatter and diff manually.

The style guide lists the discovery sources and precedence. Before editing, confirm which copy OpenCode actually loads; a duplicate ID in another source can shadow the copy you meant to edit. Never edit a global copy (`~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`) thinking it is the project copy.

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

A non-empty diff means the copy is stale or drifted. For a variant, diff against the base recorded in `upstream_commit` (or `upstream` for legacy variants); every hunk must be explained by `local_changes`, and an unexplained hunk is drift. A diff against current canonical also shows upstream drift, which is not a local amendment.

### Locating the Project Copy

Find the directory by its skill ID (the directory name, not the frontmatter display name):

```bash
find <project>/.opencode/skills <project>/.claude/skills <project>/.agents/skills \
  -name SKILL.md 2>/dev/null | grep '/<project-name>/'
```

A flat skill is `<project-skill-dir>/<project-name>.md`; the `find` above only matches the directory form. Check the source root for a flat file before concluding the copy is missing.

If more than one source contains the ID, stop and resolve the duplicate before editing; OpenCode loads one by precedence.

## Parallel Updates — Landing Procedure

The canonical repo runs `Skill Validation` on every push and pull request and
accepts direct pushes to `master`. A push is not landed until the run for the
pushed SHA is green. Multiple writers may edit skills concurrently. To land a
change without conflicts or lost updates:

1. **Fetch and isolate.** `git -C ~/workspace/agent-tools fetch origin`. Create a per-session worktree from `origin/master` — never edit the shared checkout directly:
   ```bash
   WT=$(mktemp -d /tmp/opencode/agent-tools-<skill>.XXXXXX)
   git -C ~/workspace/agent-tools worktree add \
     -b skill-update/<skill>-<stamp> "$WT" origin/master
   ```
   All edits, staging, and commits happen in `$WT`. The shared checkout `~/workspace/agent-tools` is a read-only fetch anchor.

2. **Stage explicitly.** Never `git add -A` or `git commit -a`. Stage only the files you changed:
   ```bash
   git -C "$WT" add skills/<name>/SKILL.md CHANGELOG.md README.md
   ```

3. **Commit with the tentative version.** After editing, run `scripts/check.sh origin/master` to verify the canonical checks, the tentative version bump, and the changelog entry. Commit:
   ```bash
   git -C "$WT" commit -m "<skill>: <imperative summary> (<version>)"
   ```

4. **Rebase and re-validate.** Before pushing, fetch again, rebase onto the latest `origin/master`, then recompute the version and changelog entry against the new base:
   ```bash
   git -C "$WT" fetch origin
   git -C "$WT" rebase origin/master
   ```
   - If the rebase applies cleanly, read the skill's version from `origin/master:skills/<name>/SKILL.md`. Your version must be a **strict semver increase** over that base and must match the residual diff after rebase.
   - If the base changed, re-bump from the new base (reset lower components), update the changelog entry, and amend the commit (`git commit --amend`).
   - If the other writer's change is the same lesson, your residual diff may be zero: drop the commit (`git reset HEAD~1`).
   - If it is a refinement, reclassify and bump from their version.
   - Search `origin/master` for the generic lesson again (see **Syncing Back to Canonical**, step 2). If they already landed it, sync nothing.
   - Run `scripts/check.sh origin/master` again after the rebase. It must pass before you push.

5. **Changelog reconciliation.** After rebase, re-read the **entire** `[Unreleased]` section. Insert or rewrite your entry in sorted position (area name alphabetically). Never drop or rewrite another writer's distinct entry. If the conflict is ambiguous, stop and ask rather than guessing.

6. **Push with retry.** Push the branch to `master`:
   ```bash
   git -C "$WT" push origin HEAD:master
   ```
   - On rejection (non-fast-forward), repeat from step 4 (fetch, rebase, re-check, push).
   - Bound retries at three attempts with a short randomized wait (`sleep $((RANDOM % 5 + 1))`), then stop and leave the branch for a human.
   - Never force-push. Never merge `origin/master` into the branch; rebase keeps history linear.
   - Record the pushed object name: `SHA=$(git -C "$WT" rev-parse HEAD)`.

7. **Verify CI.** Wait for the `Skill Validation` run for `$SHA` to finish.
   - Green: continue to cleanup.
   - Red: read the failing step's log, fix the cause in a new commit, run `scripts/check.sh origin/master` again, and push again.
   - Bound the CI-fix loop at three attempts. If it is still red, leave the worktree and report the run URL and failed step.
   - Do not report the change as landed while the run is pending or red.

8. **Cleanup.** Only after the commit is on `origin/master` **and** the run for `$SHA` is green, remove the worktree:
   ```bash
   git -C ~/workspace/agent-tools worktree remove "$WT"
   ```
   If the push failed or CI is red, leave the worktree and report its path and the run URL.

**Version allocation is at landing, not edit time.** An unpublished version never reached `origin/master` and may be discarded during rebase. A pushed version is never reused.

## The Canonical Repo

The upstream location is fixed — do not parameterize it or guess another path:

- **Repository:** <https://github.com/s-fleck/agent-tools>
- **Local checkout:** `~/workspace/agent-tools`; the canonical copy of `<name>` is `~/workspace/agent-tools/skills/<name>/`.

Both paths are hard-coded on purpose. If the checkout is missing, clone it:

```bash
git clone https://github.com/s-fleck/agent-tools ~/workspace/agent-tools
```

If it is missing and cannot be cloned, stop and ask — do not substitute another checkout or a stale copy of the repo.

**The shared checkout is a fetch anchor, not an edit surface.** When working on a canonical change, create a per-session worktree from `origin/master` (see **Parallel Updates — Landing Procedure**). When working in a project, edit the project copy and sync the generic lesson back separately.

The current canonical state is always `origin/master` after `git fetch`. Do not read skill files from the shared working tree while another session may be mid-edit. Use `git show origin/master:skills/<name>/SKILL.md` or a detached worktree for snapshots.

## Amending a Project Copy

1. Locate the project copy (see [Locating the Project Copy](#locating-the-project-copy)); do not edit a global copy.
2. Determine the variant's base from `upstream` (for a first amendment, the copy's current version, which equals the canonical version it was vendored from). Diff the project copy against **that base**, not current canonical, to isolate local amendments. If the copy is stale and you also want the upstream changes, pull them first.
3. Make the smallest edit that states the project's rule. Keep the generic part generic — a project rule belongs in the project copy, not in every copy of the skill.
4. Add or bump the suffix: the first amendment is `+<project-slug>.1`, later amendments increment it. Keep `upstream` at the actual base; if you also pulled current canonical in, set `upstream` to that version and reset the suffix to `+<project-slug>.1`. **Record `upstream_commit`**: find the canonical commit that introduced the base version (see [Pulling Upstream Into a Variant](#pulling-upstream-into-a-variant), step 2, but use the name from `upstream`), and set `upstream_commit` to that hash.
5. Refresh `local_changes` cumulatively.
6. If the amendment is a project-wide rule, add a one-line pointer to it in the project's `AGENTS.md` — the skill holds the detail, AGENTS.md points at the skill.
7. Record the amendment in the project's changelog.
8. Do not copy project specifics back into the canonical copy from inside the project.

## Pulling Upstream Into a Variant

1. Read `upstream` and `upstream_commit` to get the base version, canonical name, and exact base commit. If the base is already current (i.e., `upstream_commit` is an ancestor of `origin/master` and no new commits touch `skills/<name>/`), there is nothing to pull.
2. If `upstream_commit` is present, use it directly. Otherwise, locate the base commit using the name from `upstream` (this handles renames correctly because `upstream` carries the canonical name at vendoring time):
   ```bash
   git -C ~/workspace/agent-tools log --oneline --reverse \
     -S 'version: "<base-version>"' -- "skills/<upstream-name>/SKILL.md"
   ```
   The first commit that introduced the version is the base. If the file does not quote its version, search for the bare version string. If no commit matches (shallow clone or rewritten history), fetch the full history or stop and ask. If multiple commits match (e.g., after a rename), pick the one whose tree has the correct skill path and version; if ambiguous, stop and ask. Once identified, record the hash in `upstream_commit`.
3. Check out the base snapshot and diff the variant against it to capture the local amendments:
   ```bash
   BASE_WT=$(mktemp -d /tmp/opencode/skill-base-<name>.XXXXXX)
   git -C ~/workspace/agent-tools worktree add --detach "$BASE_WT" <upstream_commit>
   diff -ru "$BASE_WT/skills/<upstream-name>" <project-skill-dir>/<project-name>
   ```
   Differences are expected; `diff` exits 1 when files differ. Save the local-only hunks. This is the diff you must preserve.
4. Diff the base snapshot against current canonical to see what upstream changed:
   ```bash
   diff -ru "$BASE_WT/skills/<upstream-name>" ~/workspace/agent-tools/skills/<name>
   ```
5. Re-vendor current canonical into a scratch copy, then **re-apply local amendments via a three-way merge** (preferred) or by hand-reapplying hunks:
   ```bash
   # Three-way merge for SKILL.md (and other files if needed)
   git -C ~/workspace/agent-tools show origin/master:skills/<name>/SKILL.md > /tmp/current.md
   git -C ~/workspace/agent-tools show <upstream_commit>:skills/<upstream-name>/SKILL.md > /tmp/base.md
   cp <project-skill-dir>/<project-name>/SKILL.md /tmp/variant.md
   git merge-file /tmp/variant.md /tmp/base.md /tmp/current.md
   # Resolve conflicts in favor of the project's intent. The merged result is the new variant.
   ```
   For non-Markdown files, hand-apply the local hunks. Replace the project copy only after the result is reviewed.
6. Set `version` to `<new-base>+<project-slug>.1`, set `upstream` to `<canonical-name>@<new-base>`, set `upstream_commit` to the commit at `origin/master` that introduced `<new-base>` (find via `git log -1 --oneline --reverse -S 'version: "<new-base>"' -- skills/<name>/SKILL.md`), and refresh `local_changes`. If every local amendment was promoted upstream, do not re-apply it; remove the variant markers instead.
7. Remove the base worktree, update the project changelog, and run the project-amendment validation:
   ```bash
   git -C ~/workspace/agent-tools worktree remove "$BASE_WT"
   ```

## Syncing Back to Canonical

1. Locate the project copy and read `upstream` and `upstream_commit`. Diff the project copy against the **base recorded in `upstream_commit`**, not current canonical, to isolate local amendments. Do not classify upstream drift as a local amendment.
2. **Before applying, search canonical for the lesson.** `rg` the rule's key terms in `origin/master`'s copy and read the surrounding section. If the rule is already there, refine or merge it; do not add a parallel statement. If canonical already contains the lesson: sync nothing, re-vendor the project copy from the commit that contains it, drop that local amendment, and do not bump canonical.
3. Classify every hunk:
   - **Generic** — the rule holds for any project → move to the canonical copy.
   - **Project-specific** — names a project file, function, path, token, example, or convention → stays in the project. Genericize the *lesson* into the canonical copy (keep the rule, drop the names) and keep the names in the project copy. If no generic lesson remains, sync nothing.
   - **Project-only artifact** — a section, script, or whole skill that only makes sense in that project → do not sync it. A whole skill that only makes sense there is project-owned, not a variant.
4. Apply to the canonical copy: minimal diff, generic wording, no project names, paths, tokens, or examples. Use placeholders such as `<project>`, `<pkg>`, and `<REPO>_GH_TOKEN`.
5. **Land the canonical change using the [Parallel Updates — Landing Procedure](#parallel-updates--landing-procedure).** The version is allocated at landing (after rebase). Bump per the versioning table in `references/style-guide.md` and add or rewrite the changelog entry. If the previous version is still under `[Unreleased]`, rewrite that entry; never duplicate it.
6. After the canonical change lands on `origin/master`, re-vendor the canonical copy into the project and re-apply the remaining local amendments. If none remain, remove `variant`/`upstream`/`upstream_commit`/`local_changes` and leave the copy byte-identical; otherwise reset the suffix to `+<project-slug>.1`, set `upstream` to the new canonical version, set `upstream_commit` to the landed commit, and refresh `local_changes`.
7. Update the project's changelog and the `AGENTS.md` pointer if the rule moved.
8. Update README and cross-references if the canonical change affects them.

## Renaming and Forking

- A renamed project copy: rename the folder (the skill ID) and the frontmatter `name` together, keep the canonical name in `upstream`, note the rename in `local_changes`, and bump the suffix. Update the project's `AGENTS.md`, commands, and other skill references.
- A rename in the canonical repo is a MAJOR bump. Update the README Contents table and vendoring commands, search the repo for the old name (`rg '<old-name>'`), and name the old skill in the changelog entry. Project variants update `upstream` to the new canonical name when they next sync; `upstream_commit` stays valid.
- A fork that outgrew the canonical skill gets its own name, its own directory, and its own canonical entry in `~/workspace/agent-tools/skills/`. Start at `1.0.0`, keep the original author and `license`, and say `Fork of <original>@<version>` in the changelog entry. Add the README row and vendoring command. The original stays as it is.
- A fork is not a variant: a fork carries no `variant`/`upstream` markers and has its own history.

## Creating a Skill

1. Directory `skills/<name>/` with `SKILL.md`; the directory name is the ID (lowercase kebab-case), the frontmatter `name` matches it, and the description leads with the trigger keywords.
2. `metadata.version: "1.0.0"`, `metadata.author` set; add `license`/`compatibility` when they apply.
3. Add a row to the `README.md` Contents table and a vendoring command. Document any companion or overlay pairing.
4. Changelog entry under `[Unreleased]` `### Added`, per the `changelog-style-guide` skill.
5. If the skill is adapted from another skill, keep the original author and `license` and say so in the changelog entry; if it is a fork with a new name, follow [Renaming and Forking](#renaming-and-forking).
6. Exercise every command and path in the skill once before shipping.
7. Land the change using the [Parallel Updates — Landing Procedure](#parallel-updates--landing-procedure).

## Validation

A `check_skill.py` script ships with this skill (see `skills/skill-update/scripts/check_skill.py`). In the canonical repo, `scripts/check.sh` wraps the canonical check and the per-skill bump check; run it before committing and again after a rebase.

### Canonical change

1. Frontmatter matches `references/style-guide.md`: `name` aligned with the folder and `description` present; `metadata` values are strings; `version` is quoted.
2. The version bump follows the style guide's versioning table, uses the highest classification in the change set, and is not reused. A skill absent at the base is new and enters at `1.0.0`; an existing skill must be a strict increase.
3. The copy carries no `variant`, `upstream`, `upstream_commit`, or `local_changes`.
4. A changelog entry exists under `[Unreleased]`; if the previous version is still unreleased, the entry was rewritten rather than duplicated.
5. The canonical copy is free of project-specific names, paths, tokens, examples, and skill names.
6. A new, renamed, or forked skill has a README Contents row and vendoring command. For a rename, `rg '<old-name>'` finds no stale references.
7. If the repo ships a doc check, run it. If the documented command is missing, fix the reference or skip; a broken doc-check reference is a repo bug, not a skill failure.
8. The skill ID is unique across the repo, is lowercase kebab-case, and the directory name and frontmatter `name` agree. The skill root holds only `SKILL.md`, `references/`, `scripts/`, and `assets/`.
9. Run `scripts/check.sh origin/master` — it validates the skill layout and IDs, frontmatter, versions, changelog coverage, duplicate entries, README cross-references, and duplicate skill/version pairs, then checks every changed skill for a strict bump against `origin/master`.

### Project amendment

1. The diff is against the base recorded in `upstream_commit` (or `upstream` for legacy variants), not current canonical, and contains only the intended local hunks.
2. `variant` matches the project slug; `upstream` is the actual base; `upstream_commit` is a valid 40-hex commit reachable from `origin/master` and its tree's version equals the `upstream` version; `local_changes` lists every current amendment; the suffix is bumped correctly.
3. The version base equals the actual base, not the latest canonical version.
4. The project's changelog is updated; a project-wide rule has an `AGENTS.md` pointer.
5. No project specifics were copied into the canonical copy.
6. The edited copy is the project copy, not a global copy; no duplicate skill ID shadows it.
7. If re-vendored, the base is updated, the suffix reset to `.1`, local amendments re-applied, `upstream` and `upstream_commit` current. If no amendments remain, the variant markers are gone.
8. If the skill was renamed, the folder, frontmatter `name`, and project references agree.
9. Run `python3 skills/skill-update/scripts/check_skill.py --variant <dir> --canonical <repo>` — it validates the directory layout and folder/name agreement, metadata contract, hash reachability, version consistency, and drift.

### Command change

1. The file is `commands/<name>.md` in the canonical repo (or `.opencode/commands/<name>.md` in a project), not a directory; nested paths produce the intended `/group/name`.
2. The body is the template; there is no `template:` key in Markdown frontmatter. `$ARGUMENTS`/`$n` placeholders and the no-placeholder fallback behave as intended.
3. Shell blocks only contain trusted commands; no untrusted argument is interpolated into a shell block.
4. `agent`, `model`, and `subagent` values are valid; the command runs in the intended session or child session.
5. A vendored command is byte-identical to the canonical file; project-specific changes are project-owned and recorded in the project's changelog.

### Landing validation

Before pushing a canonical change:

- Run `scripts/check.sh origin/master` — it runs the canonical check and the bump check for every changed skill. The underlying command is `python3 skills/skill-update/scripts/check_skill.py --check-bump <skill> --base origin/master`; it verifies a strict version increase over the base or `1.0.0` for a new skill, a matching changelog entry, and a clean tree.

After pushing:

- Wait for the `Skill Validation` run for the pushed SHA. Report the run URL only when it is green; a pending or red run means the change is not landed.

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
- You edited the shared checkout `~/workspace/agent-tools` directly instead of using a per-session worktree.
- You used `git add -A` or `git commit -a` instead of staging explicit paths.
- You force-pushed or merged `origin/master` into your branch instead of rebasing.
- You reported a change as landed before the `Skill Validation` run for the pushed SHA was green.
- You removed the worktree while the run for the pushed SHA was pending or red.
- You weakened or skipped a CI check to make a red run green.
- You force-pushed `master` to recover from a CI failure.
- You kept a pre-rebase version number or changelog entry after the base moved.
- You resolved a changelog conflict by dropping another writer's distinct entry.
- You recorded a local (unpushed) canonical commit in `upstream_commit`.
- You omitted `upstream_commit` on a new variant or re-vendor.
- You used the fixed path `/tmp/opencode/skill-base-<name>` instead of `mktemp` for the base worktree.
- You created a command as a directory, or expected it to support `references/` or scripts.
- You put `template:` in Markdown command frontmatter, or placed untrusted arguments in a `!` block.
- You added skill variant markers to a command.