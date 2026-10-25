# AGENTS.md — standing rules for agent-tools

This repository is the canonical source of OpenCode skills, commands, and
subagents. `README.md` owns layout and vendoring; `skills/skill-update/SKILL.md`
owns the skill-change procedure. This file adds the landing and CI contract.

## Definition of done

A change is done only when all of these hold:

1. `scripts/check.sh origin/master` passes.
2. Every changed skill has a strict semver bump and a matching `[Unreleased]`
   changelog entry. A new skill enters at `1.0.0`; the bump check accepts a
   skill absent at the base only at that version.
3. The `Validate Skills` run for the pull request head is green.
4. The pull request is squash-merged and the post-merge `Validate Skills` run
   for the landed commit on `master` is green.
5. The merge commit is on `origin/master`; the pull request is merged; no
   branch or worktree with the change is left behind.
6. The hand-off names the merge commit SHA, the pull request URL, and the green
   run URL.

A local pass is not a CI pass. A green pull request check is not a landing
until the post-merge run for the merge commit is green.

## Pre-PR gate

Run in the per-session worktree, after the final rebase:

```bash
scripts/check.sh origin/master
```

It validates the canonical repo and runs the version-bump check for every
changed skill. Never open or update a pull request with a red tree. Do not run
the checks in the shared checkout; edit and validate in the worktree.

## Pull request and post-merge CI loop

Workflow: `.github/workflows/skills.yml`, job `Validate Skills`.

1. Push the per-session branch and open a pull request against `master`.
   Never push to `master` directly.
2. Record the pull request head: `SHA=$(git rev-parse HEAD)`.
3. Wait for the `Validate Skills` run for `$SHA` to complete. Use the Actions
   UI, `gh pr checks` if available, or the repository REST helper. Do not infer
   status from an earlier run or from the push output.
4. Green: merge the pull request with a squash merge (linear history; no merge
   commits). Do not merge while the check is pending or red.
5. After merge, fetch and record the merge commit
   (`MERGE_SHA=$(git rev-parse origin/master)`), then wait for the `push` run
   for `$MERGE_SHA`. Green: fast-forward the shared checkout, delete the
   branch (local and remote, unless GitHub already deleted it), and remove the
   worktree.
6. Red on the pull request: fix it in a new commit on the same branch, re-run
   `scripts/check.sh origin/master`, and push again. Red after merge: stop the
   line and fix forward in a new pull request.
7. Bound the loop at three attempts. Then stop, leave the worktree and branch
   in place, and report the pull request URL, SHA, run URL, failed step, exact
   error, and what you tried.

Never push or force-push `master`. Update your own pull request branch after a
rebase with `--force-with-lease`; never use a merge commit to catch up. Never
merge or delete a worktree while a run for the pull request head or the landed
SHA is pending or red. Never weaken CI to get green: no removed steps, no
dropped `--strict`, no `continue-on-error`, no skipped skill.

## Landing

- Canonical changes use a per-session worktree from `origin/master`, stage
  explicit paths, rebase, re-validate, push the branch, open a pull request,
  and squash-merge only after the required `Validate Skills` check is green
  (`skill-update` procedure).
- `master` is protected: direct pushes, force pushes, and deletion are
  disabled; the `Validate Skills` check is required and the branch must be up
  to date before merging.
- The shared checkout `~/workspace/agent-tools` is a fetch anchor. Never push
  from it. After a merge, update it with
  `git fetch origin && git merge --ff-only origin/master`.
- One logical change per commit; do not mix unrelated skill bumps.
- A red `master` is a stop-the-line event: fix or report it before adding new
  work.

## Changing CI

- Treat `.github/workflows/skills.yml` as production code. When the gate
  changes, update this file and `skills/skill-update/SKILL.md` in the same
  change.
- Keep `scripts/check.sh` and CI in sync. A new CI step needs a local
  equivalent.
- Branch protection on `master` requires the `Validate Skills` job name and a
  green post-merge run. Keep the job name stable, or update the protection
  rule in the same change.
- Test workflow edits with a pull request or `workflow_dispatch` before
  relying on them.

## Reporting a failure

Include the pull request URL, commit SHA, run URL, job/step, exact failing
line, content vs infrastructure classification, and next action. Never paste
tokens.
