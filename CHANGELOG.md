# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Skill changes are the unit of release here: every skill carries its own
`metadata.version`, and every version bump gets an entry below with the skill
name as the area prefix.

## [Unreleased]

### Added

- **issue-to-spec:** Auto mode accepts an explicit issue (`/issue-to-spec auto 42`) and still implements after review
- **issue-to-spec:** Rename the session with the OpenCode API (`opencode api session.update`) instead of a plugin tool; the title marks work in progress and gains a trailing ` ✓` on completion
- **semver:** Add skill mapping release contents to MAJOR/MINOR/PATCH per Semantic Versioning (1.0.0)

### Changed

- **github-issue:** Move the REST helper to `scripts/github-rest.py` and update every invocation path; the skill root now follows the canonical layout (`SKILL.md` plus `references/`, `scripts/`, and `assets/`) (8.0.0)
- **github-issue:** Define label resolution in `references/labels.md`: skill defaults, project AGENTS.md overrides, write/read deny rules, repository label descriptions, and ask-before-use for incomplete metadata; add read-only triage signals for the standard GitHub labels (`wontfix`/`invalid`/`duplicate`/`question`, `stale`, project blockers, ready gates, and classification hints); the style guide keeps the form contract (7.0.0)
- **issue-to-spec:** Resolve label roles through the `github-issue` labels reference instead of hardcoding `product`/`idea`, `draft`, `needs-ruling`, and the priority tiers
- **issue-to-spec:** Honor issue disposition and workflow metadata: skip or warn on declined labels, `not_planned` closures, assignees, parent/sub-issue trackers, open blockers, open/draft linked PRs, missing ready gates, milestone/board gates, and unchecked template gates
- **issue-to-spec:** Trust only maintainer comments for rulings, paginate comments, reconcile stale `needs-ruling`/`draft` labels, rank project priority tiers, handle multiple/dangling `Change:` links, and refresh the verification stamp in place; locked issues skip the post-solve comment
- **github-issue:** Merge the `issue-comment` skill into `github-issue`: filing, maintaining, and commenting are one lifecycle; the title, body, label, comment, and signature rules move to `references/style-guide.md`, while the REST helper stays in the skill directory (5.0.0)
- **issue-to-spec:** Parse the leading `auto` as an exact token instead of a substring, reject malformed, PR-URL, and foreign-repo targets before fetching, stop when a numeric target resolves to a PR, and ask before proceeding on closed issues
- **issue-to-spec:** Treat auto-selection eligibility as selection-only: explicit `auto <N>` targets still hit the per-issue guardrails (draft/`needs-ruling` ask, active changes ask before implementation, product/archived/multi-subsystem stop)
- **github-issue:** Add the whole-surface footprint check for a term and require naming/vocabulary rulings to check the project's binding vocabulary (4.1.0)
- **spec-reviewer:** Add settled-spec interaction and binding-vocabulary criteria, and require evidence checks for reported claims (unversioned subagent)
- **agent-tools:** README: add `semver` as a required companion to both changelog skills, with the vendoring note; genericize the variant example (`acme`)
- **agent-tools:** README: warn that a global skill copy can shadow the vendored one (opencode registers skills by name, and the loader resolves duplicates concurrently)
- **changelog-style-guide:** Add a release-cutting step that delegates the version decision to the `semver` skill (1.1.0)
- **doc-rewrite:** Drop the R-specific doc-check example; defer to the project's documented command (1.0.1)
- **github-issue:** Rename the REST helper to `github-rest.py` and state plainly that it is a skill script, not the `gh` CLI; rewrite it as a typed, importable CLI with `--help`, lazy token paths, `pathlib`, `HelperError` exit handling and pinned API headers (3.0.0)
- **github-issue:** Require every title to be `<scope>: <what>` — a lowercase project scope, a colon, one space, then a lowercase imperative; `area:` is no longer a prefix, and an em dash, ` - ` or a second colon is never the separator (2.0.0)
- **github-issue:** Replace the R file-path and fire-specific token examples with neutral placeholders (1.0.1)
- **github-issue:** Align the title rule with practice (declarative statements allowed, scope mandatory for agent-authored issues, `Ruling:` is not a scope), make the label set extensible from AGENTS.md and the repository, require a duplicate search, the `verified YYYY-MM-DD (model: <model_id>)` stamp and a named regression test for bugs; the helper gains `--paginate` (GET, same-host `Link` only), method-aware retries (POST is not retried after a 5xx or network error) and transient 403 rate limits (4.0.0)
- **issue-to-spec:** Sync the generic guardrails from the fire variant — `openspec validate` before hand-off, changelog delegation per project type (`r-news-styleguide` for R, `changelog-style-guide` otherwise), version bumps delegate to the `semver` skill, `draft`-issue rewrite and auto-mode exclusion, load-bearing claim verification, failing-test-first for bugs; GitHub access defers to the `github-issue` skill; the doc-check example is language-neutral
- **issue-to-spec:** Treat the project's product-direction label (`idea` as well as `product`) as roadmap work in the picker and auto mode, not as an implementable issue; paginate the open-issue fetch
- **agent-tools:** README: align skill discovery with the V2 docs — use the `skills` config array, describe ID-based source precedence instead of a loader race, and note that command files reload automatically
- **r-data-table:** Rename `data-table` to `r-data-table` so R-specific skills carry the `r-` prefix (2.0.0)
- **r-news-styleguide:** Delegate the version bump to the `semver` skill; `NEWS.md` now owns the R-specific timing, promotion, and `DESCRIPTION` sync only (2.0.0)
- **r-package-style-guide:** Point at the renamed `r-data-table` skill (3.0.1)
- **skill-update:** Rework the variant lifecycle: distinguish stale copies from variants, record the actual vendoring base in `upstream`, reset semver components correctly, split canonical and project validation, add pull-upstream and drift-check procedures, and require README/cross-reference updates on create, rename, and fork; keep the fixed canonical checkout, `semver` delegation, and language-neutral rule (3.0.0)
- **skill-update:** Add the parallel-landing procedure (per-session worktree, fetch/rebase/re-bump, changelog reconciliation, duplicate-lesson check), record the exact `upstream_commit` in variant metadata, and ship a skill metadata checker plus CI (4.0.0)
- **skill-update:** Fix the checker script: skip Layout-table placeholders in the README Contents scan, fix the `git status --porcelain` path parsing, annotate the generic `CompletedProcess` type, and reformat to lint cleanly under a 100-char limit (4.0.2)
- **skill-update:** Document OpenCode's actual skill and command layout and split the stable form rules into `references/style-guide.md`, keeping `SKILL.md` as the update and landing procedure; move the validator into `scripts/`; commands are single `.md` files, not skill directories (4.1.0)
- **skill-update:** Enforce the canonical skill directory layout in the checker: lowercase kebab-case IDs, `skills/<name>/SKILL.md` only, no flat/grouped/nested skills, a skill root limited to `SKILL.md`, `references/`, `scripts/`, and `assets/`, and variant folder/name agreement (4.2.0)

### Removed

- **issue-comment:** Remove the standalone skill; its post-solve comment template and signature policy moved to `github-issue` (merged into `github-issue` 5.0.0)

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
