---
description: Cut a release — bump version, update changelog, land via PR, tag, and publish
agent: build
---

Cut a full release: analyze `[Unreleased]` changelog entries, choose the version bump via the `semver` skill, update version files, land through a pull request, tag the merge commit, and optionally publish to a package registry.

**Preconditions — stop and report if any fails**

- Working tree is clean except for the release changes this command will make (no unrelated unstaged changes).
- Current branch is `master` (or the project's release branch per `AGENTS.md`).
- `CHANGELOG.md` exists and has an `[Unreleased]` section with at least one entry.
- The `semver` skill is available in `.opencode/skills/`.
- The `github-issue` skill is available in `.opencode/skills/` (for `/land` and GitHub API).
- GitHub token is configured (see `github-issue` skill for token resolution).
- If publishing: the project's publish command is defined in `AGENTS.md` (e.g. `cargo publish`, `npm publish`, `devtools::release()`).

**Steps**

1. **Analyze changelog** — read `CHANGELOG.md`, extract the `[Unreleased]` section. If empty, stop: "No unreleased changes to release."
2. **Determine bump** — invoke the `semver` skill to classify the `[Unreleased]` entries and compute the next version (major/minor/patch). Present the proposed version and the entries driving it.
3. **Confirm** — ask "Release v<next> with these changes? [Y/n]" (unless `--yes` / `-y` flag given).
4. **Update version files** —
   - Promote `[Unreleased]` → `[<version>] - <YYYY-MM-DD>` in `CHANGELOG.md`.
   - Update version in project files defined in `AGENTS.md` (e.g. `DESCRIPTION` for R, `Cargo.toml`, `package.json`, `pyproject.toml`, `version.txt`). If none defined, update common files found in the repo root.
   - Update `README.md` version badge/line if present.
5. **Stage and land** — stage all version/changelog files, then invoke `/land` with a generated title (`chore: release v<version>`). `/land` handles: branch → commit → push → PR → squash merge → sync → report.
6. **Tag** — after `/land` reports the merge commit SHA, create an annotated tag: `git tag -a v<version> -m "Release v<version>" <merge-sha>` and push it: `git push origin v<version>`.
7. **Publish** — if `AGENTS.md` defines a `release.publish` command, run it. Otherwise, if a common publish command is detected (Cargo, npm, PyPI, CRAN, etc.), ask before running.
8. **Report** — version, tag URL, merge commit, publish status.

**Failure paths**

- No `[Unreleased]` entries → stop, nothing to release.
- `semver` skill returns no bump (only internal/docs changes) → ask whether to proceed as patch.
- `/land` fails (merge refused, checks fail) → tag/publish skipped; report PR URL for manual merge.
- Tag push fails (tag exists) → report and stop; do not publish.
- Publish fails → report error; tag remains pushed; manual publish needed.

**Arguments**

- `$ARGUMENTS`:
  - `--yes` / `-y` — skip the confirmation prompt.
  - `--dry-run` — show what would be done without writing files, creating PR, tagging, or publishing.
  - `--skip-publish` — tag but do not run the publish step.
  - `<version>` — explicit version (e.g. `1.2.0`, `v2.0.0`); bypasses `semver` analysis.

**Project Conventions (from AGENTS.md)**

- `release.version_files` — list of files to update with the new version (default: auto-detect common files).
- `release.changelog` — path to changelog (default: `CHANGELOG.md`).
- `release.branch` — branch to release from (default: `master`).
- `release.publish` — command to publish the release (e.g. `cargo publish`, `npm publish`, `python -m build && twine upload dist/*`, `devtools::release()`).
- `release.tag_prefix` — tag prefix (default: `v`).
- `release.sign_tags` — whether to sign tags with GPG (default: false).

**GitHub access** — uses the `github-issue` skill's helper (via `/land`) and direct `git`/`gh` for tagging.

**Example AGENTS.md snippet**

```yaml
release:
  version_files:
    - CHANGELOG.md
    - DESCRIPTION
    - README.md
  publish: "Rscript -e 'devtools::release()'"
  tag_prefix: "v"
```