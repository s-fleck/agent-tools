---
name: semver
description: >
  Use when choosing the next version for a release — maps release contents to
  MAJOR/MINOR/PATCH per Semantic Versioning, including breaking changes,
  deprecations, fixes, internal-only work, pre-1.0 projects, and pre-releases.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

# Semantic Versioning

Versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):
`MAJOR.MINOR.PATCH`. This skill decides **which** component a release bumps.
The project's changelog skill decides **when** a release happens and how the
entry is written.

## When To Use

- Choosing the next version for a release.
- Classifying a change as breaking, additive, or a fix.
- Reviewing a changelog or release plan for a wrong bump.

## The Public API

The public API is what users depend on: exported functions and classes, CLI
flags and output, configuration keys, file formats, and documented behavior.
Internal helpers, private functions, and test code are not public API.

## A Release Takes The Highest Bump Its Changes Require

Classify every change in the release, then apply the highest result:

| Change | Bump |
|---|---|
| **Breaking:** existing user code, configuration, or workflow stops working without an edit | **MAJOR** |
| New backwards-compatible functionality (`Added`); public API deprecation (`Deprecated`); backwards-compatible behavior change (`Changed`) | **MINOR** |
| Backwards-compatible bug fix (`Fixed`); internal-only or docs-only change | **PATCH** |

- `Removed` — **MAJOR** when it removes public API (even deprecated API);
  **PATCH** when it removes internal-only code.
- `Security` — **PATCH** for a backwards-compatible vulnerability fix;
  **MAJOR** if the fix breaks compatibility. A new security capability belongs
  under `Added` and bumps **MINOR**.
- **Highest wins**: MAJOR > MINOR > PATCH. One breaking change makes the whole
  release MAJOR, even when everything else is a fix.
- Internal-only and docs-only changes are not a SemVer category. When the
  project releases for them, PATCH is the smallest honest bump.
- Nothing shipped, nothing to bump. Do not invent a release for an edit the
  project does not release.

## Pre-1.0

For `0.y.z`, SemVer declares the public API unstable and permits anything to
change. The usual convention is to treat the **minor** slot as the breaking
slot:

- `0.12.0` + new feature → `0.13.0`
- `0.12.0` + breaking change → `0.13.0`
- `0.12.0` + fix → `0.12.1`

If the project documents a different pre-1.0 convention, follow that instead.

## Pre-Releases And Build Metadata

- Pre-release: `1.0.0-rc.1`, `2.0.0-beta.2` — sorts before the final release.
- Build metadata: `1.0.0+build.1` — ignored when comparing versions; use it for
  local counters, never to mark a different release.

## Before You Bump

1. Every change in the release is classified.
2. The bump is the highest classification.
3. The version in the manifest, the tag, and the changelog heading agree.
