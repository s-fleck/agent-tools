# agent-tools — archival source of agent tooling

**Version:** 0.2.1 — see [CHANGELOG.md](CHANGELOG.md) for the release history. Releases are tagged `v<version>`.

Canonical copies of opencode tooling (skills, commands, subagents, checks) that projects **copy from** when needed. It is deliberately not a live tool directory:

- Do **not** add this repo to `skills.paths`, `~/.agents/skills/`, or any other auto-discovery location — agents should only see the tools a project actually vendored.
- Selection is per project; not everything fits everywhere. Example: R package repos take `r-news-styleguide`, other projects take `changelog-style-guide`.
- Vendored copies start byte-identical to this repo. A copy that later takes project-specific amendments is marked as a **variant** in its metadata — see [Skill versioning](#skill-versioning).

## Layout → destination

| Path | Vendored to |
|------|-------------|
| `skills/<name>/` | `<project>/.opencode/skills/<name>/` |
| `commands/*.md` | `<project>/.opencode/commands/` |
| `agents/*.md` | `<project>/.opencode/agent/` |
| `scripts/check-docs.R` | `<project>/tools/check-docs.R` (or any scripts dir) |

## Contents

| Path | What it gives you | Vendor it when |
|------|-------------------|----------------|
| `skills/r-package-development` | R package workflow: devtools, testthat, roxygen2 | any R package |
| `skills/r-package-style-guide` | code style rules for R packages | any R package |
| `skills/r-package-style-guide-rlang` | rlang error rules — **overlay**, needs the base skill alongside it | the package depends on rlang |
| `skills/r-package-testing` | testthat 3 patterns, fixtures, mocking, snapshots | any R package with tests |
| `skills/r-roxygen` | roxygen2 documentation conventions | any R package |
| `skills/r-news-styleguide` | `NEWS.md` conventions, version-bump rules | any R package |
| `skills/data-table` | `data.table` semantics and footguns | the package uses `data.table` |
| `skills/changelog-style-guide` | Keep a Changelog for non-R projects | a non-R project |
| `skills/github-issue` | issue composition plus the self-contained GitHub REST helper (`gh.py`, vendored with the skill directory) | the project files issues on GitHub |
| `skills/issue-comment` | post-solve issue comments | ditto |
| `skills/doc-rewrite` | scoped review/rewrite procedure for one named document | the project has binding docs |
| `skills/skill-update` | amending, versioning, renaming, and syncing back skills; the metadata contract for variants | the project amends its own copies |
| `commands/issue-to-spec` | GitHub issue → reviewed OpenSpec change; `/issue-to-spec auto` picks and implements one | the project uses OpenSpec — needs the CLI and its `openspec-*` skills |
| `agents/spec-reviewer` | read-only OpenSpec change reviewer | ditto |
| `scripts/check-docs.R` | markdown cross-reference checker (links, anchors, `file:line`, `§`, `Status:` headers): `Rscript tools/check-docs.R` from the repo root; CI-ready (exit 1 on errors). Base R only. | the project has markdown docs |

## Skill versioning

Every skill carries `metadata.version` (semver, `MAJOR.MINOR.PATCH`) and `metadata.author`. Rules, in short — the `skill-update` skill is the procedure:

- **Every change to a skill bumps its version.** PATCH for wording and fixes, MINOR for new guidance, MAJOR for a changed or removed rule, a changed frontmatter contract, or a rename.
- **A fork keeps the original author's credit.** `metadata.author` is a comma-separated list, original author first: `author: "Garrick Aden-Buie (@gadenbuie), Stefan Fleck"`. Amendments add to the list, they never replace it. Carry the upstream `license:` line into the fork.
- **Every version bump gets a `CHANGELOG.md` entry** under `[Unreleased]`, area prefix = skill name. The repo follows its own `changelog-style-guide`.
- **A project copy with local amendments is a variant** and says so:

  ```yaml
  metadata:
    author: Stefan Fleck
    version: 3.0.0+fire.1      # upstream version + local amendment counter
    variant: fire             # the project that owns the amendments
    upstream: r-package-style-guide@3.0.0
    local_changes: "Problem: repro stamp and symbol refs"
  ```

  The `+<project>.<n>` suffix is semver build metadata — the base tracks upstream, the counter tracks local amendments. Re-vendoring resets the counter.
- **An overlay is vendored next to its base skill.** `r-package-style-guide-rlang` overrides one section of `r-package-style-guide`; copying both leaves the base's metadata untouched. A project that amends the overlay itself records it as a variant of the overlay skill, not of the base.
- **Project-specific rules live in the project copy**; the canonical copy stays generic. Genericize the lesson when syncing back — keep the rule, drop the project's names, paths, and tokens.
- **Rename the folder and the frontmatter `name` together** when a project copy is renamed; the canonical name stays in `upstream`. A rename in this repo is a MAJOR bump.

## Conventions

- GitHub token: `<REPO>_GH_TOKEN` — repo name uppercased, `-`/`.` → `_` — in `~/.Renviron` (e.g. `FIRE_GH_TOKEN` for `s-fleck/fire`); fallback `GH_TOKEN` / `GITHUB_TOKEN`. Never commit or log it.
- Vendored copies start byte-identical to this repo; project differences belong in the project's `AGENTS.md` and, once they touch a skill, in that copy's variant metadata.

## Vendoring

Copy the whole skill directory — skills ship with `references/`, scripts, and helpers next to `SKILL.md`.

```bash
P=/path/to/project
mkdir -p "$P/.opencode/skills" "$P/.opencode/agent" "$P/.opencode/commands" "$P/tools"
cp -r skills/github-issue skills/issue-comment "$P/.opencode/skills/"
cp -r skills/r-news-styleguide "$P/.opencode/skills/"   # pick per project, e.g. R packages
cp -r skills/skill-update "$P/.opencode/skills/"          # whenever the project amends its copies
cp agents/spec-reviewer.md "$P/.opencode/agent/"
cp commands/issue-to-spec.md "$P/.opencode/commands/"
cp scripts/check-docs.R "$P/tools/"
```

**Overlays ship with their base.** `r-package-style-guide-rlang` only means something next to `r-package-style-guide` — copy both, and only when the package depends on rlang:

```bash
cp -r skills/r-package-style-guide skills/r-package-style-guide-rlang "$P/.opencode/skills/"
```

**Then restart opencode.** Skills, agents, and commands are read at startup; a running session keeps the set it started with. After the restart, verify what was picked up:

```bash
cd "$P" && opencode debug skill   # lists every skill opencode found
```

A copy stays byte-identical until the project amends it. The first amendment
turns it into a variant: bump the version suffix, set `variant`, `upstream`,
and `local_changes` in the copy's frontmatter, and note the rule in the
project's `AGENTS.md`. See `skills/skill-update`.
