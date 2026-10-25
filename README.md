# agent-tools — archival source of agent tooling

**Version:** 0.2.1 — see [CHANGELOG.md](CHANGELOG.md) for the release history. Releases are tagged `v<version>`.

Canonical copies of opencode tooling (skills, commands, subagents, checks) that projects **copy from** when needed. It is deliberately not a live tool directory:

- Do **not** add this repo to the `skills` config array, `~/.agents/skills/`, or any other auto-discovery location — agents should only see the tools a project actually vendored.
- Selection is per project; not everything fits everywhere. Example: R package repos take `r-news-styleguide` + `semver`, other projects take `changelog-style-guide` + `semver`.
- Vendored copies start byte-identical to this repo. A copy that later takes project-specific amendments is marked as a **variant** in its metadata — see [Skill versioning](#skill-versioning).

## Layout → destination

| Path | Vendored to |
|------|-------------|
| `skills/<name>/` | `<project>/.opencode/skills/<name>/` |
| `commands/*.md` | `<project>/.opencode/commands/` |
| `agents/*.md` | `<project>/.opencode/agent/` |

## Contents

| Path | What it gives you | Vendor it when |
|------|-------------------|----------------|
| `skills/r-package-development` | R package workflow: devtools, testthat, roxygen2 | any R package |
| `skills/r-package-style-guide` | code style rules for R packages | any R package |
| `skills/r-package-style-guide-rlang` | rlang error rules — **overlay**, needs the base skill alongside it | the package depends on rlang |
| `skills/r-package-testing` | testthat 3 patterns, fixtures, mocking, snapshots | any R package with tests |
| `skills/r-roxygen` | roxygen2 documentation conventions | any R package |
| `skills/r-news-styleguide` | `NEWS.md` conventions and the completion-time promotion rule | any R package |
| `skills/r-data-table` | `data.table` semantics and footguns | the package uses `data.table` |
| `skills/changelog-style-guide` | Keep a Changelog for non-R projects | a non-R project |
| `skills/semver` | SemVer version bumps for releases — **companion**, vendor with either changelog skill | any project that releases |
| `skills/github-issue` | issue composition plus the self-contained GitHub REST helper (`github-rest.py`, vendored with the skill directory) | the project files issues on GitHub |
| `skills/issue-comment` | post-solve issue comments | ditto |
| `skills/doc-rewrite` | scoped review/rewrite procedure for one named document | the project has binding docs |
| `skills/skill-update` | OpenCode skill/command style guide, layout and discovery; amending, versioning, renaming, syncing back skills; pulling upstream into a variant; parallel-safe canonical landings; the metadata contract for variants | the project amends its own copies or ships slash commands |
| `commands/issue-to-spec` | GitHub issue → reviewed OpenSpec change; `/issue-to-spec auto [<issue>]` picks or takes an issue and implements it | the project uses OpenSpec — needs the CLI and its `openspec-*` skills |
| `agents/spec-reviewer` | read-only OpenSpec change reviewer | ditto |

## Skill versioning

Every skill carries `metadata.version` (semver, `MAJOR.MINOR.PATCH`) and `metadata.author`. Rules, in short — the `skill-update` skill is the procedure:

- **Every change to a skill bumps its version.** PATCH for wording and fixes, MINOR for new guidance, MAJOR for a changed or removed rule, a changed frontmatter contract, or a rename. `semver` covers project/package release versions; skill versions follow this table via `skill-update`.
- **A fork keeps the original author's credit.** `metadata.author` is a comma-separated list, original author first: `author: "Garrick Aden-Buie (@gadenbuie), Stefan Fleck"`. Amendments add to the list, they never replace it. Carry the upstream `license:` line into the fork.
- **Every version bump gets a `CHANGELOG.md` entry** under `[Unreleased]`, area prefix = skill name. The repo follows its own `changelog-style-guide`.
- **A project copy with local amendments is a variant** and says so:

  ```yaml
  metadata:
    author: Stefan Fleck
    version: "4.0.0+acme.1"      # upstream version + local amendment counter
    variant: acme               # the project that owns the amendments
    upstream: r-package-style-guide@4.0.0
    upstream_commit: 4f3a2c1d9e8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f
    local_changes: "Package name <project> instead of <pkg>; release timing defers to the project release skill"
  ```

  The `+<project>.<n>` suffix is semver build metadata — the base tracks upstream, the counter tracks local amendments. Re-vendoring resets the counter. `upstream_commit` records the exact canonical commit the copy was vendored from; it is required for new variants and on re-vendor.
- **An overlay is vendored next to its base skill.** `r-package-style-guide-rlang` overrides one section of `r-package-style-guide`; copying both leaves the base's metadata untouched. A project that amends the overlay itself records it as a variant of the overlay skill, not of the base.
- **Project-specific rules live in the project copy**; the canonical copy stays generic. Genericize the lesson when syncing back — keep the rule, drop the project's names, paths, and tokens.
- **Rename the folder and the frontmatter `name` together** when a project copy is renamed; the canonical name stays in `upstream`. A rename in this repo is a MAJOR bump.
- **Canonical changes land through a fetch/rebase loop.** See `skill-update` for the parallel-safe landing procedure (per-session worktree, rebase, re-validate, push with retry). Versions are allocated when the change reaches `origin/master`, not at edit time.

## Conventions

- GitHub token: `<REPO>_GH_TOKEN` — repo name uppercased, `-`/`.` → `_` — in `~/.Renviron` (e.g. `FIRE_GH_TOKEN` for `s-fleck/fire`); fallback `GH_TOKEN` / `GITHUB_TOKEN`. Never commit or log it.
- Vendored copies start byte-identical to this repo; project differences belong in the project's `AGENTS.md` and, once they touch a skill, in that copy's variant metadata.

## Vendoring

Copy the whole skill directory — skills ship with `references/`, scripts, and helpers next to `SKILL.md`. Do not copy `SKILL.md` alone.

Commands are single `.md` files: copy the file, not a directory. A command has no supporting-file mechanism; put reusable material in a skill and load it from the command.

```bash
P=/path/to/project
mkdir -p "$P/.opencode/skills" "$P/.opencode/agent" "$P/.opencode/commands" "$P/tools"
cp -r skills/github-issue skills/issue-comment "$P/.opencode/skills/"
cp -r skills/r-news-styleguide "$P/.opencode/skills/"   # pick per project, e.g. R packages
cp -r skills/semver "$P/.opencode/skills/"                # with either changelog skill
cp -r skills/skill-update "$P/.opencode/skills/"          # whenever the project amends its copies
cp agents/spec-reviewer.md "$P/.opencode/agent/"
cp commands/issue-to-spec.md "$P/.opencode/commands/"
```

**Overlays ship with their base.** `r-package-style-guide-rlang` only means something next to `r-package-style-guide` — copy both, and only when the package depends on rlang:

```bash
cp -r skills/r-package-style-guide skills/r-package-style-guide-rlang "$P/.opencode/skills/"
```

**Changelog skills ship with `semver`.** Both `r-news-styleguide` and
`changelog-style-guide` delegate the version bump to `semver` — copy it
alongside either one.

**Then restart opencode if you changed skills or agents.** Skills and agents are read at startup; a running session keeps the set it started with. Command files reload automatically. After the restart, verify what was picked up:

```bash
cd "$P" && opencode debug skill   # lists every skill opencode found, with its path
```

**Watch for name collisions.** opencode registers skills by ID, and later
sources replace earlier ones. A duplicate in a global source or another project
directory can still be the copy you edit by mistake. Prefer `.opencode/skills/`
for vendored copies; it outranks the global and compatibility sources. Explicit
`skills` config entries rank above it, so do not duplicate an ID there.
`opencode debug skill` shows which path won. To run without the global set
entirely: `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`.

A copy stays byte-identical until the project amends it. The first amendment
turns it into a variant: bump the version suffix, set `variant`, `upstream`,
`upstream_commit`, and `local_changes` in the copy's frontmatter, and note the rule in the
project's `AGENTS.md`. See `skills/skill-update`.