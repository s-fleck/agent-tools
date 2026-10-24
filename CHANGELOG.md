# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Skill changes are the unit of release here: every skill carries its own
`metadata.version`, and every version bump gets an entry below with the skill
name as the area prefix.

## [Unreleased]

### Added

- **issue-to-spec:** Rename the session with the OpenCode API (`opencode api session.update`) instead of a plugin tool; the title marks work in progress and gains a trailing ` ✓` on completion
- **semver:** Add skill mapping release contents to MAJOR/MINOR/PATCH per Semantic Versioning (1.0.0)

### Changed

- **agent-tools:** README: add `semver` as a required companion to both changelog skills, with the vendoring note; genericize the variant example (`acme`)
- **agent-tools:** README: warn that a global skill copy can shadow the vendored one (opencode registers skills by name, and the loader resolves duplicates concurrently)
- **changelog-style-guide:** Add a release-cutting step that delegates the version decision to the `semver` skill (1.1.0)
- **doc-rewrite:** Drop the R-specific doc-check example; defer to the project's documented command (1.0.1)
- **github-issue:** Rename the REST helper to `github-rest.py` and state plainly that it is a skill script, not the `gh` CLI; rewrite it as a typed, importable CLI with `--help`, lazy token paths, `pathlib`, `HelperError` exit handling and pinned API headers (3.0.0)
- **github-issue:** Require every title to be `<scope>: <what>` — a lowercase project scope, a colon, one space, then a lowercase imperative; `area:` is no longer a prefix, and an em dash, ` - ` or a second colon is never the separator (2.0.0)
- **github-issue:** Replace the R file-path and fire-specific token examples with neutral placeholders (1.0.1)
- **github-issue:** Align the title rule with practice (declarative statements allowed, scope mandatory for agent-authored issues), make the label set extensible from AGENTS.md and the repository, require a duplicate search, the `verified YYYY-MM-DD (model: <model_id>)` stamp and a named regression test for bugs; the helper gains `--paginate` (GET, same-host `Link` only), method-aware retries (POST is not retried after a 5xx or network error) and transient 403 rate limits (4.0.0)
- **issue-to-spec:** Sync the generic guardrails from the fire variant — `openspec validate` before hand-off, changelog delegation per project type (`r-news-styleguide` for R, `changelog-style-guide` otherwise), version bumps delegate to the `semver` skill, `draft`-issue rewrite and auto-mode exclusion, load-bearing claim verification, failing-test-first for bugs; GitHub access defers to the `github-issue` skill; the doc-check example is language-neutral
- **issue-to-spec:** Treat the project's product-direction label (`idea` as well as `product`) as roadmap work in the picker and auto mode, not as an implementable issue
- **r-data-table:** Rename `data-table` to `r-data-table` so R-specific skills carry the `r-` prefix (2.0.0)
- **r-news-styleguide:** Delegate the version bump to the `semver` skill; `NEWS.md` now owns the R-specific timing, promotion, and `DESCRIPTION` sync only (2.0.0)
- **r-package-style-guide:** Point at the renamed `r-data-table` skill (3.0.1)
- **skill-update:** Hardcode the canonical repo (`https://github.com/s-fleck/agent-tools`) and its local checkout (`~/workspace/agent-tools`) in place of the `<skill-repo>` placeholder, reference the `semver` skill as the general versioning policy, and require non-`r-` skills to stay language-neutral (2.0.0)

## [0.2.1] - 2026-10-21

### Changed

- **agent-tools:** README: add a selection table, the overlay pairing rule, a restart note, and a verification step (opencode debug skill)
- **r-news-styleguide:** Use a neutral `<pkg>` placeholder instead of the fire example, so projects can vendor it unchanged (1.3.0)
- **skill-update:** Do not hardcode the canonical repo path, so the skill works when vendored elsewhere (1.0.1)

## [0.2.0] - 2026-10-21

### Added

- **r-package-style-guide-rlang:** Add overlay skill with the rlang error rules for packages that depend on rlang (1.0.0)

### Changed

- **r-package-style-guide:** Replace the rlang error rules with base-R ones (classed conditions via `stop()`); the rlang rules move to the `r-package-style-guide-rlang` overlay (3.0.0)

## [0.1.0] - 2026-10-21

### Added

- **data-table:** Add skill covering data.table scoping, joins, by-reference updates, and key types (1.0.0)
- **skill-update:** Add skill for amending, versioning, renaming, and syncing back skills (1.0.0)

### Changed

- **agent-tools:** Normalize skill versions to full semver and require a changelog entry per version bump
- **github-issue:** Extract the GitHub REST helper into `gh.py` and add repro-stamp, symbol-reference, and draft-label rules (1.0.0)
- **issue-comment:** Add the signature policy for agent-authored GitHub content (1.0.0)
- **r-news-styleguide:** Add the version-bump-on-completion rule and the R NEWS parser note (1.2.0)
- **r-package-development:** Add the `air format . --check` command and the formatting-baseline rule (1.3.0)
- **r-package-development:** Restore the original author's frontmatter credit alongside the amending author (1.3.0)
- **r-package-style-guide:** Add the rlang error rules, the vendored assertion toolset, and the data.table cross-reference (2.3.0)
- **r-package-testing:** Add the rule against mocking base bindings (2.2.0)
- **r-package-testing:** Credit the amending author alongside the original author in the frontmatter (2.2.0)
- **r-roxygen:** Add frontmatter and a version (1.0.0)

[Unreleased]: https://github.com/s-fleck/agent-tools/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/s-fleck/agent-tools/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/s-fleck/agent-tools/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/s-fleck/agent-tools/releases/tag/v0.1.0
