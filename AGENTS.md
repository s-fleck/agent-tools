# AGENTS.md — standing rules for agent-tools

This repository is the canonical source of OpenCode skills, commands, and
subagents. `README.md` owns layout and vendoring; `skills/skill-update/SKILL.md`
owns the skill-change procedure. This file adds the landing and CI contract.

## Definition of done

A change is done only when all of these hold:

1. `scripts/check.sh origin/master` passes.
2. Every changed skill has a strict semver bump and a matching `[Unreleased]`
   changelog entry.
3. The `Validate Skills` run for the landed commit is green.
4. The commit is on `origin/master`; no branch or worktree with the change is
   left behind.
5. The hand-off names the commit SHA and the green run URL.

A push is not a landing. A local pass is not a CI pass.

## Pre-push gate

Run in the per-session worktree, after the final rebase:

```bash
scripts/check.sh origin/master
```

It validates the canonical repo and runs the version-bump check for every
changed skill. Never push a red tree. Do not run the checks in the shared
checkout; edit and validate in the worktree.

## Post-push CI loop

Workflow: `.github/workflows/skills.yml`, job `Validate Skills`.

1. Record the pushed commit: `SHA=$(git rev-parse HEAD)`.
2. Wait for the run for `$SHA` to complete. Use the Actions UI, `gh run watch`
   if available, or the repository REST helper. Do not infer status from an
   earlier run or from the push output.
3. Green: report the run URL, then clean up the worktree.
4. Red: read the failing step and the exact error line.
   - Content failure: fix it in a new commit on the same branch, re-run
     `scripts/check.sh origin/master`, and push again.
   - Infrastructure failure: retry once (`gh run rerun <id> --failed`, or
     re-push). If it persists, report it.
5. Bound the loop at three attempts. Then stop, leave the worktree and branch
   in place, and report the SHA, run URL, failed step, exact error, and what
   you tried.

Never force-push `master`. Never merge or delete a worktree while the run for
the landed SHA is pending or red. Never weaken CI to get green: no removed
steps, no dropped `--strict`, no `continue-on-error`, no skipped skill.

## Landing

- Canonical changes use a per-session worktree from `origin/master`, stage
  explicit paths, rebase, re-validate, then push (`skill-update` procedure).
- One logical change per commit; do not mix unrelated skill bumps.
- With branch protection enabled, land through a PR and merge only after the
  required `Validate Skills` check is green.
- Direct pushes to `master` are allowed only with the post-push loop above.
- A red `master` is a stop-the-line event: fix or report it before adding new
  work.

## Changing CI

- Treat `.github/workflows/skills.yml` as production code. When the gate
  changes, update this file and `skills/skill-update/SKILL.md` in the same
  change.
- Keep `scripts/check.sh` and CI in sync. A new CI step needs a local
  equivalent.
- Test workflow edits with a PR or `workflow_dispatch` before relying on them.

## Reporting a failure

Include the run URL, commit SHA, job/step, exact failing line, content vs
infrastructure classification, and next action. Never paste tokens.
