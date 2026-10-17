# agent-tools — archival source of agent tooling

Canonical copies of opencode tooling (skills, commands, subagents, checks) that projects **copy from** when needed. It is deliberately not a live tool directory:

- Do **not** add this repo to `skills.paths`, `~/.agents/skills/`, or any other auto-discovery location — agents should only see the tools a project actually vendored.
- Selection is per project; not everything fits everywhere. Example: R package repos take `r-news-styleguide`, other projects take `changelog-style-guide`.
- Vendored copies stay byte-identical to this repo; project differences live in the project's `AGENTS.md`.

## Layout → destination

| Path | Vendored to |
|------|-------------|
| `skills/<name>/` | `<project>/.opencode/skills/<name>/` |
| `commands/*.md` | `<project>/.opencode/commands/` |
| `agents/*.md` | `<project>/.opencode/agent/` |
| `scripts/check-docs.R` | `<project>/tools/check-docs.R` (or any scripts dir) |

## Contents

- `skills/r-package-*`, `skills/r-roxygen`, `skills/r-news-styleguide` — R package development, style, testing, docs, release notes.
- `skills/changelog-style-guide` — changelog convention for non-R projects.
- `skills/github-issue` — composing/filing issues plus the self-contained GitHub REST helper.
- `skills/issue-comment` — post-solve issue comments.
- `skills/doc-rewrite` — scoped review/rewrite procedure for one named document.
- `commands/issue-to-spec` — GitHub issue → reviewed OpenSpec change; `/issue-to-spec auto` picks and implements one. Companions: `agents/spec-reviewer`, `skills/github-issue`, `skills/issue-comment`, the project's changelog skill. Prerequisite: OpenSpec (CLI + its `openspec-*` skills).
- `agents/spec-reviewer` — read-only OpenSpec change reviewer.
- `scripts/check-docs.R` — markdown cross-reference checker (links, anchors, `file:line`, `§`, `Status:` headers): `Rscript tools/check-docs.R` from the repo root; CI-ready (exit 1 on errors). Base R only.

## Conventions

- GitHub token: `<REPO>_GH_TOKEN` — repo name uppercased, `-`/`.` → `_` — in `~/.Renviron` (e.g. `FIRE_GH_TOKEN` for `s-fleck/fire`); fallback `GH_TOKEN` / `GITHUB_TOKEN`. Never commit or log it.
- Vendored copies stay byte-identical to this repo; project differences belong in the project's `AGENTS.md`.

## Vendoring

```bash
P=/path/to/project
mkdir -p "$P/.opencode/skills" "$P/.opencode/agent" "$P/.opencode/commands" "$P/tools"
cp -r skills/github-issue skills/issue-comment "$P/.opencode/skills/"
cp -r skills/r-news-styleguide "$P/.opencode/skills/"   # pick per project, e.g. R packages
cp agents/spec-reviewer.md "$P/.opencode/agent/"
cp commands/issue-to-spec.md "$P/.opencode/commands/"
cp scripts/check-docs.R "$P/tools/"
```
