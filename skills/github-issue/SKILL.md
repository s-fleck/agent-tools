---
name: github-issue
description: Use when filing, drafting, or reformatting a GitHub issue — turning notes or discussion into an issue, filing follow-up work from a solved issue, or checking an issue body against house style. Also carries the self-contained GitHub REST helper (`github-rest.py`, a skill script — not the `gh` CLI) used by the issue-to-spec command.
metadata:
  author: Stefan Fleck
  version: "3.0.0"
---

Compose issues for the project's issue registry. AGENTS.md rules apply (registry policy wins); this skill is the how-to.

## Body

1. Use the project's section skeleton (default: `**Problem**` / `**Fix**` / `**Rulings**` / `**Done when**` / `**Out of scope**`).
2. Delete sections that stay empty before filing. Keep the body under ~40 lines.
3. Fill the sections:
   - **Problem** — what is wrong or missing, and why it matters. `file:line` plus the enclosing symbol for code (lines rot; symbols are greppable — e.g. `path/to/file` line 138, symbol `parse_amount`); doc name + `§` for binding docs. Verify behavioral claims against the current codebase before filing — repro or inspection, stated in one line with the model (e.g. `repro 2026-10-20 (model: <name>)`); that stamp doubles as the issue's signature — no end-of-body signature line; verify old refs still resolve before trusting them. State the measured numbers, not the expected direction: a mechanism can move a figure up or down, so a claim like "the figures dip" needs its sign checked against the real data.
   - **Fix** — concrete task list (`- [ ]`); name the required spec delta inline (project notation, e.g. `Δspec: <capability>`).
   - **Rulings** — ⚖ only decisions that need the owner: options + one recommendation. Resolved by editing this section; `needs-ruling` label while undecided.
   - **Done when** — machine-checkable acceptance: tests that must exist/pass, commands to run, doc bumps.
   - **Out of scope** — only when a reader (human or agent) might plausibly wander there.
4. Title: `<scope>: <what>` — a scope, a colon, one space, then the what.
   - `<scope>` names where the work lands: the project's own module, layer, surface, document or skill. One lowercase word, hyphenated if compound (`cash-ledger`); no underscore, no code formatting. Reuse a scope the open issues already use; a new one takes the project's own word for that area (the code layout or the binding vocabulary), not an invented synonym. Cross-cutting work gets its own short scope (`chore`, `hygiene`, `tooling`); the generic word `area` is never the scope.
   - The what starts lower case unless its first word is a proper noun or acronym, is imperative, front-loads the verb, and ends without a period.
   - The scope is separated by exactly `: `. An em dash, ` - ` or a second colon never replaces it, and the scope is never wrapped in backticks: `area:run — add the preflight check` is wrong; `run: add the preflight check` is right. A detail that would otherwise add a second colon goes in parentheses: `run: implement landing (push, PR, required checks, merge)`.
   - Omit the scope only when the issue genuinely has no single home; say why in the body.
5. Labels (this is the authoritative set — don't invent others): `P1` highest priority · `P2` medium · `P3` low — pure priority tiers, not failure modes (that context lives in the title/body); `needs-ruling` decision pending; `product` routed to ROADMAP, not a code change; `draft` human-written stub — when work starts, clarify with the user, rewrite title/body/labels to house style, remove the label (human-written text on it may be rewritten without asking).
6. No token values; no personal data beyond what the fix needs.

When composing in chat, output the issue markdown only — no commentary around it.

## GitHub access: the `github-rest.py` script, not the `gh` CLI

`github-rest.py` (next to this file) is the project's only GitHub client. There is no `gh` CLI dependency: no `gh` binary is installed for this workflow and none is needed. The helper is a standard-library Python script, not executable and not on `PATH` — always call it by path with `python3`; `--help` lists the methods and the payload rules. The paths below show a vendored copy; from the canonical repo use `skills/github-issue/github-rest.py`.

It derives `owner/repo` from `git remote get-url origin` and resolves the token from `AGENT_GH_TOKEN`, then `$XDG_CONFIG_HOME/issue-pipeline/github-token` (one line, chmod 600), then a per-repository `<REPO>_GH_TOKEN`, then `GH_TOKEN` and `GITHUB_TOKEN`; the token is never printed or logged. Call it directly — no heredoc:

```bash
python3 .opencode/skills/github-issue/github-rest.py GET /issues/42
python3 .opencode/skills/github-issue/github-rest.py GET "/issues?state=open&per_page=50"
python3 .opencode/skills/github-issue/github-rest.py POST /issues /tmp/opencode/issue.json                      # create: {"title", "body", "labels"}
python3 .opencode/skills/github-issue/github-rest.py PATCH /issues/42 /tmp/opencode/issue-42-body.md            # rulings, `Change:` link
python3 .opencode/skills/github-issue/github-rest.py POST /issues/42/comments /tmp/opencode/issue-42-comment.md
python3 .opencode/skills/github-issue/github-rest.py DELETE /issues/42/labels/needs-ruling
```

- A file argument ending in `.json` is sent as the raw payload (e.g. creating an issue); anything else (`.md`) is wrapped as `{"body": <text>}` (comments, body updates).
- `PATCH /issues/<N>` replaces the whole body: re-fetch immediately before editing and keep everything unrelated verbatim — never PATCH from a cached body.
- Token hygiene: the operator token file is `$XDG_CONFIG_HOME/issue-pipeline/github-token` (one line, file 600, directory 700); a project may also provide `<REPO>_GH_TOKEN` in its environment — never write the token value into the repo, workspace files, or logs.

## Lifecycle

- One issue = one shippable unit of work: an agent session or a focused pass can finish it; if not, split it. Issues carry context, not designs — when work on a cluster starts, create its OpenSpec change, link it in the body (`Change: <id>`), and let the design live in the change.
- Rulings (⚖) are decided by editing the issue's Rulings section; follow-up work becomes new issues.
- Verify old refs still resolve when touching an existing issue.
- Post-solve summary comments follow the `issue-comment` skill.
- Signature/traceability for substantive agent-authored GitHub content (comments with findings, review results, plans, or reports) is specified once in the `issue-comment` skill — routine posts stay unsigned, issues are signed by the Problem verification stamp, archiving commits keep the `model: …; version: …` trailer.
- Close with `Fixes #<N>` in the archiving/closing commit.
