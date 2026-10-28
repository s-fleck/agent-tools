---
description: Land staged work through a pull request — branch, commit, push, PR, squash merge, sync
agent: build
---

Land the staged work through a pull request. `$ARGUMENTS` optionally names the issue (`70` / `#70`) and a title; without it, derive both from the staged diff and the conversation.

**Preconditions — stop and report if any fails**

- `git diff --cached --name-status` is non-empty and holds only this change's files. An unrelated staged path is unstaged (`git restore --staged <paths>`) or the landing stops and asks; it never carries another session's work.
- No commit is made with `--no-verify`, and `master` is never a push target.
- The project's local checks pass in the working tree. Checks are defined in the project's `AGENTS.md` (see **Project Conventions**); if none are defined, this step is skipped. CI on the pull request is informational — never wait for it.
- **Version bump guardrail** — the staged set must include at least one file that looks like a version bump or changelog entry (e.g. `CHANGELOG.md`, `NEWS.md`, `Cargo.toml`, `package.json`, `pyproject.toml`, `DESCRIPTION`, `version.txt`, `VERSION`, `go.mod`, `pom.xml`, `build.gradle*`, `*.csproj`, `*.fsproj`). If none are found, report the staged files and ask before continuing. A project can disable this in `AGENTS.md` with `land: { require_version_bump: false }`.

**Steps** — chain the git steps in one shell call; each extra round trip is full-context resend on a rate-limited model.

1. **Branch** — `git switch -c <type>/<issue>-<slug>` (`feat`, `fix`, `docs`, `chore`; e.g. `feat/70-pr-landing`). If the branch for this work already exists, switch to it instead of opening a second one.
2. **Commit** — one focused commit on that branch. Message: `<scope>: <what>` (conventional commits; project may override via `AGENTS.md`) plus the body if the reasoning is not obvious. An archiving landing ends it with the trailer `model: <model>; version: <DESCRIPTION version>` — the `github-issue` skill reserves that trailer for archiving commits.
3. **Push** — `git push -u origin <branch>`.
4. **Pull request** — `POST /pulls` with a JSON payload (`{"title": …, "head": "<branch>", "base": "master", "body": …}`). Body: 2–4 lines — what and why, then the issue reference. It carries `Refs #<N>`; use `Fixes #<N>` only when this landing completes the issue — the archiving PR — never for a mid-flight implementation landing, which would close the issue early.
5. **Merge** — `PUT /pulls/<n>/merge` with a JSON payload `{"merge_method": "squash"}`. Do **not** call `DELETE /git/refs/heads/<branch>`: `delete_branch_on_merge` removes it, and deleting an already-removed ref fails terminally (`422`). Do not wait for the CI run.
6. **Sync** — `git switch master && git pull --ff-only`.
7. **Report** — PR URL, merge commit, and the issue reference the body carried.

**Failure paths**

- Unrelated or empty staged set → stop before committing; nothing is landed.
- A local check fails → fix it before the branch is pushed; nothing lands red.
- Merge refused (403 or a permission error) → leave the PR open and report its URL for a browser merge; never retry blindly.

**Efficiency** — bookkeeping edits (checkbox ticks, task-note records) ride with the next substantive landing or the archiving PR, never their own pull request. Batch issue-body edits into one PATCH. Script GitHub calls so only the needed fields enter context, never raw JSON.

**GitHub access** — use the `github-issue` skill's helper, which resolves the token and never prints it:

```bash
python3 .opencode/skills/github-issue/github-rest.py POST /pulls /tmp/opencode/pr.json
python3 .opencode/skills/github-issue/github-rest.py PUT /pulls/<n>/merge /tmp/opencode/merge.json
```

## Project Conventions

Everything project-specific comes from the project's `AGENTS.md` and skills:

- **Local checks** — a list of commands to run before pushing (e.g. `pre-commit run --all-files`, `cargo test`, `go test ./...`). If `AGENTS.md` does not define checks, this step is skipped.
- **Branch base** — the target branch for the PR (default `master`; `main` or `trunk` if the project uses it).
- **Commit message style** — conventional commits by default; project may specify a different format in `AGENTS.md`.
- **Changelog skill** — R packages: `r-news-styleguide`; other projects: `changelog-style-guide`; omit if the project has none.
- **Versioning** — the `semver` skill for choosing the bump.
- **Post-solve comment** — the `github-issue` skill's comment format.
- **Postmortem** — if the project keeps a `POSTMORTEMS.md` registry, the `postmortem` skill handles seeds and consolidation at the archive boundary.

Companions expected in `.opencode/`: the `github-issue` skill (for the REST helper and labels reference). If the project keeps a postmortem registry, also the `postmortem` skill.

## Argument Handling

- `$ARGUMENTS` is the complete argument string.
- If empty: derive issue number and title from the staged diff and conversation context.
- If provided: parse as `[<issue>] [<title...>]` where `<issue>` is a number (`70`), `#`-prefixed (`#70`), or a URL to an issue in this repository. The remaining words form the title.
- Normalize `<issue>` to `<N>`. For a URL, require the same repository as the project and extract the issue number only after that check; reject `/pull/` URLs.
- If an explicit issue is given but the title is omitted, derive the title from the staged diff.