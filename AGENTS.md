# AGENTS.md — standing rules for agent-tools

This repository is the canonical source of OpenCode skills, commands, and
subagents. `README.md` owns layout and vendoring; `skills/skill-update/SKILL.md`
owns the skill-change procedure. This file adds the landing and release contract.

## Definition of done

A change is done only when all of these hold:

1. `scripts/check.sh origin/master` passes locally before pushing.
2. Every changed skill has a strict semver bump and a matching `[Unreleased]`
   changelog entry. A new skill enters at `1.0.0`; the bump check accepts a
   skill absent at the base only at that version.
3. The pull request is opened against `master` and the `Validate Skills` check
   (required status check) is green.
4. The pull request is squash-merged (linear history; no merge commits).
5. The merge commit is on `origin/master`; the pull request is merged; no
   branch or worktree with the change is left behind.
6. For releases: `/release` cuts the version, tags the merge commit, and pushes
   the tag. The hand-off names the version, merge commit SHA, pull request URL,
   and tag URL.

A local pass is not a CI pass. The required `Validate Skills` check on the PR
is the gate.

## Landing — `/land`

Use the `/land` command for all canonical changes. It handles:
branch → commit → push → PR → squash merge → sync.

**Procedure:**

1. **Stage explicitly** — `git add <paths>` only the files you changed
   (`SKILL.md`, `CHANGELOG.md`, `README.md`, etc.).
2. **Run local gate** — `scripts/check.sh origin/master` (validates layout,
   frontmatter, version bump, changelog entry).
3. **Run `/land`** — it will:
   - Create a branch (`<type>/<issue>-<slug>` or derived from diff)
   - Commit with conventional message (`<scope>: <what>`)
   - Push and open a PR against `master`
   - Squash-merge via GitHub API (requires `github-issue` skill for token)
   - Sync local `master` with `git pull --ff-only`
4. **Wait for CI** — the `Validate Skills` required check on the PR must be
   green before merge. `/land` does not wait; the branch protection enforces it.
5. **Verify** — after merge, `git fetch origin && git merge --ff-only origin/master`
   to fast-forward the shared checkout.

**Failure paths:**

- Local gate fails → fix before running `/land`.
- PR checks fail → fix in a new commit on the same branch, re-run local gate,
  push again (force-with-lease). The PR updates automatically.
- Merge refused (permission) → `/land` leaves PR open; merge manually in browser.
- Shared checkout not clean → `git fetch origin && git merge --ff-only origin/master`
  before starting.

**Branch protection** (configured in GitHub, not in commands):

- `master` is protected: require `Validate Skills` status check, require PR,
  require linear history (squash merge), no direct pushes.

## Release — `/release`

Use the `/release` command to cut a release. It handles:
analyze changelog → semver bump → update version files → `/land` → tag → publish.

**Procedure:**

1. **Ensure `[Unreleased]` has entries** — every landed change since last tag
   should have added a changelog entry under `[Unreleased]`.
2. **Run `/release`** — it will:
   - Read `[Unreleased]` from `CHANGELOG.md`
   - Invoke `semver` skill to determine next version
   - Promote `[Unreleased]` → `[<version>] - <YYYY-MM-DD>`
   - Update version in `README.md` (and any other files in `release.version_files`)
   - Stage version files and run `/land` (title: `chore: release v<version>`)
   - After merge, create annotated tag `v<version>` at merge commit, push tag
   - (No publish step for this repo — tag push = release)
3. **Verify** — tag appears on GitHub, `CHANGELOG.md` on `master` shows the
   released version.

**Arguments:**

- `/release --yes` — skip confirmation
- `/release --dry-run` — show what would happen
- `/release --skip-publish` — tag but don't publish (default for this repo)
- `/release 1.2.0` — explicit version override

**Project config (in this repo's AGENTS.md):**

```yaml
release:
  version_files:
    - README.md
    - CHANGELOG.md
  tag_prefix: "v"
  # No publish command — tag push is the release
```

## Changing CI

- Treat `.github/workflows/skills.yml` as production code. When the gate
  changes, update this file and `skills/skill-update/SKILL.md` in the same
  change.
- Keep `scripts/check.sh` and CI in sync. A new CI step needs a local
  equivalent.
- Branch protection on `master` requires the `Validate Skills` job name and a
  green check. Keep the job name stable, or update the protection rule in the
  same change.
- Test workflow edits with a pull request or `workflow_dispatch` before
  relying on them.

## Vendoring this repo's commands

Projects that vendor from this repo should copy:

```bash
P=/path/to/project
mkdir -p "$P/.opencode/skills" "$P/.opencode/commands"
cp -r skills/semver "$P/.opencode/skills/"
cp -r skills/github-issue "$P/.opencode/skills/"
cp commands/land.md "$P/.opencode/commands/"
cp commands/release.md "$P/.opencode/commands/"
# Plus any other skills they need
```

Then add to their `AGENTS.md`:
```yaml
release:
  version_files: [CHANGELOG.md, Cargo.toml]  # or DESCRIPTION, package.json, etc.
  publish: "cargo publish"  # or npm publish, devtools::release(), etc.
```

## Reporting a failure

Include the pull request URL, commit SHA, run URL, job/step, exact failing
line, content vs infrastructure classification, and next action. Never paste
tokens.