# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Skill changes are the unit of release here: every skill carries its own
`metadata.version`, and every version bump gets an entry below with the skill
name as the area prefix.

## [Unreleased]

### Changed

- **agent-tools:** README: warn that a global skill copy can shadow the vendored one (opencode registers skills by name, and the loader resolves duplicates concurrently)

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
