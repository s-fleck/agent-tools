---
name: doc-rewrite
description: Use when reviewing, tightening, or rewriting a named document or section — specs, ADRs, READMEs, guides, architecture docs. Scoped procedure: verify claims against code, repair references, minimal edits. Not for OpenSpec change artifacts.
metadata:
  author: Stefan Fleck
  version: "1.0.0"
---

# Scoped documentation review

Review one document (or one named section) per invocation. "Review all docs" in a single pass produces shallow bulk rewrites; doc rot is fixed where it is found, or filed as issues.

## 0. Preflight

- Run the project's doc checker if one exists (e.g. `Rscript tools/check-docs.R`); its findings seed the inventory.
- Fix the scope from the request or the issue; if none is given, list the docs and ask which one. Read the document fully, plus the code and paths it references.
- OpenSpec change artifacts (`openspec/changes/**`) are reviewed by the `spec-reviewer` subagent — not here.

## 1. Classify claims

- **Normative** — contracts others rely on: the binding docs named in AGENTS.md, interfaces, schemas, settled decisions. May be clarified or corrected, never silently changed: editing a normative claim is a decision that needs explicit confirmation.
- **Informative** — explanations, examples, how-tos. Fix freely.

## 2. Verify

- Accuracy: every factual claim, path, command, and example still matches the code. Check that `file:line` and document references resolve; run example commands when cheap.
- Terminology: identifiers and vocabulary match the project's binding vocabulary — not synonyms.
- Duplication: text copied from a single source of truth becomes a reference, not a copy.
- Structure: headings and anchors other docs link to are preserved unless the links move too.

## 3. Report findings before editing

Per finding: category (wrong / stale / duplicated / unclear / missing), severity, evidence, minimal fix. Out-of-scope findings become issue-ready items (see the `github-issue` skill) instead of silent fixes.

## 4. Apply minimal edits

- Minimal diffs: no wholesale rewrites, no reflowing untouched paragraphs, no wording preferences unless they cause ambiguity.
- Preserve normative meaning exactly unless the change was explicitly confirmed.
- If the document has a `Status:` line and settled content changed, bump version + date per the project convention.

## 5. Verify after

- Re-run the checker; confirm the findings are gone and no new ones appeared.
- Grep for the document's name elsewhere to catch incoming references that need updating.
