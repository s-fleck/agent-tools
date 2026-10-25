# Skill and Command Style Guide

Stable form rules for skills and commands in the agent-tools canonical repo. The parent `SKILL.md` is the update procedure; read this guide before changing layout, frontmatter, versioning, or command authoring.

## Platform Layout

OpenCode's discovery is broader than this repo's canonical layout. The canonical repo uses only the directory form; a project may use any form OpenCode accepts.

### Skills

```text
<source>/
├── review.md                    # flat skill, ID review (source root only)
└── git-release/
    └── SKILL.md                 # directory skill, ID git-release
```

`<source>` is one of `.opencode/skills`, `.claude/skills`, `.agents/skills`, or `~/.config/opencode/skills`.

- **Directory form is recommended.** `SKILL.md` and its supporting files share a private base directory; paths inside the skill are relative to that directory. Only directory skills get the supporting-file sample.
- A flat `<name>.md` is valid only at the source root and gets no neighboring-file sample. Use it only when the skill has no supporting files.
- Grouping directories are allowed: `<source>/teams/release/SKILL.md` has ID `release`, not `teams/release`. A directory containing `SKILL.md` is one skill; OpenCode does not search inside it for more skills.
- `SKILL.md` is case-sensitive. Hidden files/directories and `node_modules` are skipped; search stops six directories below the source root.
- Supporting files are **not** loaded with the body. OpenCode adds `SKILL.md` without frontmatter and a sample of up to ten supporting paths; the skill must tell the agent which files to read.

### Command Layout

```text
<source>/commands/
├── review.md                    # /review
└── team/review.md               # /team/review
```

- A command is one `.md` file; there is no `SKILL.md`-style directory form and no supporting-file mechanism. If a command needs reusable material, load a skill.
- Nested paths become slash-separated names: `.opencode/commands/team/review.md` is `/team/review`.
- Project commands live in `.opencode/commands/`, global commands in `~/.config/opencode/commands/`. Only `.md` is discovered. The legacy singular `command/` is still discovered; use `commands/` for new files.

### Discovery and precedence

| Scope | Skills | Commands |
|---|---|---|
| Global | `~/.config/opencode/skills` | `~/.config/opencode/commands` |
| Global compatibility | `~/.claude/skills`, `~/.agents/skills` | — |
| Project | `.opencode/skills` | `.opencode/commands` |
| Project compatibility | `.claude/skills`, `.agents/skills` | — |

- Project skill sources are searched from the current directory up to the project root, at every level.
- A `skills` array in any `opencode.json`/`opencode.jsonc` adds sources: relative paths resolve from the active working directory, `~/` from home, absolute paths as written, and HTTP(S) URLs as catalogs. Arrays are combined.
- Later sources win by ID. For skills, low to high: built-in, `.claude`, `.agents`, `~/.config/opencode`, project `.opencode`, explicit `skills` config. For commands, later definitions replace earlier ones; project over global, nearer over ancestor, custom over built-in.
- Duplicate IDs are not merged; a later source replaces an earlier one. Check the winner before editing (`opencode debug skill` shows the path for skills), and edit the file OpenCode actually loads.
- The skill ID is path-derived and case-sensitive; `name` is a display label. The repo convention keeps them equal, but OpenCode does not require it. For a portable skill use lowercase kebab-case, 1–64 characters: `^[a-z0-9]+(-[a-z0-9]+)*$`.
- `description` is required to advertise a skill. `metadata.opencode/autoinvoke: false` (or `disable-model-invocation: true`) hides it from the model list but keeps it loadable by ID; `opencode/autoinvoke` wins if both are set. `license` and `compatibility` are accepted but not interpreted.
- Agent `skill` permissions can `allow`, `ask`, or `deny` by ID; rules run in order and the last match wins. A denied skill is hidden and cannot be loaded.
- Loading a skill adds its Markdown body, not its supporting files. The model sees only ID, name, and description until then.

References: <https://opencode.ai/v2/docs/skills/> and <https://opencode.ai/v2/docs/commands/>.

## Canonical Skill Anatomy

The canonical repo uses the directory form only:

```text
skills/<name>/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Only those four entries may appear at the skill root: `SKILL.md` plus optional `references/`, `scripts/`, and `assets/` directories. Put helper scripts in `scripts/` (never loose at the root), reference documents in `references/`, and static or binary assets in `assets/`. IDs are lowercase kebab-case, 1–64 characters (`^[a-z0-9]+(?:-[a-z0-9]+)*$`). The checker enforces this layout; it rejects flat skills (`skills/<name>.md`), directories without `SKILL.md`, grouped or nested skills, and any other root entry.

`SKILL.md` opens with YAML frontmatter:

```yaml
---
name: code-review                    # display label; keep equal to the folder name
description: Use when ...            # required; third person, covers what it does + when to trigger
license: MIT                         # optional
compatibility: Requires <runtime> >= <version>    # optional
metadata:                            # optional; flat string → string map, no nesting
  author: Stefan Fleck
  version: "4.0.2"
---
```

- The directory name is the skill ID: case-sensitive, and the repo convention is lowercase kebab-case. The frontmatter `name` is the display label; keep it equal to the folder name.
- `description` is what an agent matches against. Without it the skill is never surfaced; keep the trigger keywords in the first sentence.
- `metadata` values are strings, not lists or maps. A new field is a new key, never a nested structure. Quote `version`.
- Supporting files are referenced relative to `SKILL.md`; use `references/<file>`, `scripts/<file>`, or `assets/<file>` and say when to read or run them. Do not rely on auto-loading.

## Metadata Contract

Canonical copy — no project markers:

```yaml
metadata:
  author: Stefan Fleck
  version: "4.0.2"
```

Project copy with local amendments — four extra keys:

```yaml
metadata:
  author: Stefan Fleck
  version: "4.0.0+acme.1"
  variant: acme
  upstream: code-review@4.0.0
  upstream_commit: 4f3a2c1d9e8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f
  local_changes: "Package name <project> instead of <pkg>; release timing defers to the project release skill"
```

- `variant` — the project slug that owns the amendments. Its presence is the signal that this copy is a variant.
- `upstream` — `<canonical-skill-name>@<version>` the copy was **actually vendored from**, not the latest canonical version. If canonical has moved on, this stays at the old base until the variant is re-vendored. It carries the canonical name when the project copy was renamed.
- `upstream_commit` — the full 40-hex object name of the canonical commit the copy was actually vendored from. This commit must be reachable from `origin/master`. It is the authoritative base for three-way merges and survives renames. Record it on the first amendment and on every re-vendor. Legacy variants without this field: use the `upstream` name and version to locate the base commit; if ambiguous or renamed, stop and ask, then record the hash once resolved.
- `local_changes` — one line of plain text, semicolon-separated, one clause per current amendment. Cumulative: update it whenever an amendment is added, changed, or removed. It is a summary, not a changelog.
- `version` — the base from `upstream` plus a build suffix `+<project-slug>.<n>` counting local amendment edits. Semver ignores build metadata when comparing precedence, so the suffix is a local counter, not a precedence claim. Use a lowercase, hyphenated project slug; SemVer build metadata allows only alphanumerics and hyphens.
- If the last amendment is removed, re-vendor (or confirm the copy matches its base), then drop all four markers and set `version` to that canonical version.

## Attribution

- `metadata.author` lists the skill's authors, comma-separated, **original author first**:

  ```yaml
  metadata:
    author: "Garrick Aden-Buie (@gadenbuie), Stefan Fleck"
  ```

- A fork **keeps** the original author's credit. Amendments add the amending author to the list; they never replace the original.
- A skill that was rewritten from scratch names only its own author — say so in the changelog entry.
- Carry the upstream `license:` line into the fork (e.g. `license: MIT` for a skill from a MIT-licensed collection) and never change it. If upstream has no `license` line, do not invent one.
- Look the original author up before you credit them: the upstream file, the project's skill lock file (e.g. `.agents/skills/skills-lock.json`), and the upstream repository are the sources. A fork that ships without frontmatter has no recorded author — do not guess one.

## Versioning

Every change to a skill bumps its version. Nothing ships unbumped. This is the
`semver` skill applied to skill guidance: a skill's rules are its public API,
so changing or removing one is MAJOR.

Classify the whole change set; the highest bump wins. Do not bump once per hunk.

| Change | Bump | Example |
|--------|------|---------|
| Typo, wording, formatting, a clarification that does not change guidance | PATCH | 2.3.0 → 2.3.1 |
| New guidance, new section, new option — additive, contradicts nothing | MINOR | 2.3.0 → 2.4.0 |
| A rule changed or was removed, the frontmatter contract changed, or the skill was renamed | MAJOR | 2.3.0 → 3.0.0 |

- A MAJOR bump resets MINOR and PATCH to 0; a MINOR bump resets PATCH to 0; a PATCH bump increments PATCH. Never bump a lower component without resetting the ones below it.
- Never reuse a version number, not even after a revert.
- A project copy's local amendments bump the suffix: `2.3.0+acme.1` → `2.3.0+acme.2`. The base stays at the upstream version the copy actually came from.
- Re-vendoring resets the suffix: after pulling upstream 2.4.0 in and re-applying the local amendments, the copy is `2.4.0+acme.1`.
- A rename in the canonical repo is a MAJOR bump; the changelog entry names the old skill.
- New skills and forks start at `1.0.0`; pre-1.0 versions are not used for skills. Converting a variant into a fork is a project-copy rename plus a new canonical skill, not a MAJOR bump of the original.

## Changelog

- The canonical repo keeps one changelog at `~/workspace/agent-tools/CHANGELOG.md`, in Keep a Changelog + semver form, per the `changelog-style-guide` skill.
- Every skill version bump gets an entry under `[Unreleased]`, with the skill name as the area prefix.
- Entry shape: `- **<skill>:** <imperative summary> (<new version>)`.
- If the previous version is still under `[Unreleased]`, **rewrite that entry** instead of adding a second one for the same feature.
- A project copy's local amendments are recorded in the **project's** changelog (or `NEWS.md` for R packages), not the canonical one. The canonical changelog records only what landed upstream.

## Command Authoring

Commands are prompt templates invoked explicitly, not model-discovered skills. The trimmed Markdown body is the template; Markdown frontmatter carries metadata. `template` belongs only in JSON command definitions, never in Markdown frontmatter.

- Frontmatter: `description`, `agent`, `model` (`provider/model` or `provider/model#variant`), and `subagent` (legacy alias `subtask`; `subagent` wins).
- Commands can also be defined under `commands` in `opencode.json`/`opencode.jsonc`; a JSON entry requires `template`. Markdown and JSON share one registry, so a later definition replaces an earlier command of the same name.
- Command files reload automatically; a saved change updates the command without restarting OpenCode.
- `$ARGUMENTS` is the complete argument string exactly as entered. `$1`, `$2`, ... are positional; single or double quotes group words and are removed. The highest-numbered placeholder consumes its argument and everything after; missing positions become empty strings. With no placeholder, OpenCode appends non-empty arguments after a blank line.
- A `!` backtick block runs before submission and is replaced by its combined output; placeholders expand first. Shell blocks run outside the agent's tool permission flow, so never put untrusted arguments in them.
- A stored template does not expand `@path`; add attachments through the composer, where they are preserved.
- Commands run in the current session by default. `agent` switches the agent; `model` overrides the model. `subagent: true` runs a background child session and returns its result or failure to the parent; `false` forces the current session; omitted uses a child only when the selected agent is a subagent.
- Commands have no `variant`/`upstream`/`version` metadata contract in this repo. A project-specific command is a project-owned copy: record the change in the project's changelog and keep the generic source in `commands/`. Do not invent variant markers for it.
