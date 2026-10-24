---
description: Triage a GitHub issue into a reviewed OpenSpec change; `auto` also implements it
agent: build
---

Drive GitHub issue `$ARGUMENTS` from triage to a reviewed OpenSpec change ready for `/opsx-apply`. Flow: fetch issue → rename session → resolve open rulings → create change → independent spec review → auto-fix → escalate real decisions. You do NOT implement or commit — unless Auto mode is requested. The session title gets a trailing ` ✓` once the change is finished (see **Session title on completion**).

**Auto mode:** `/issue-to-spec auto` selects the best issue that needs no human input, runs the same flow unattended, then implements it via the `openspec-apply-change` skill. Details at the bottom of this file.

**Input:** the issue number (e.g. `42`), an issue URL, or `auto` (see Auto mode). If `$ARGUMENTS` is empty, fetch the open issues (`GET /issues?state=open&per_page=50`, see below) and make ONE question-tool call: one option per issue, label `#<n> — <short title>`, description = labels + one-line gist. Ignore entries with a `pull_request` field (PRs), and mark `product`-labeled issues in the description as "routes to the project roadmap" instead of offering them as work. Continue with the chosen number as `<N>`.

## GitHub access

Load the `github-issue` skill — it carries the REST helper (`github-rest.py`, called directly with `python3`, token rules included). If `$ARGUMENTS` is a URL, extract the issue number from it.

## Project conventions

Everything project-specific comes from the project's AGENTS.md and skills: issue skeleton, labels, ruling (⚖) handling, binding docs, checks to run, changelog skill (R packages: `r-news-styleguide`; other projects: `changelog-style-guide`), versioning (`semver`). Companions expected in `.opencode/`: `github-issue` and `issue-comment` skills, `spec-reviewer` subagent.

## Session title on completion

The title set in step 1 (or auto-mode selection) marks the work as *in progress*. When the change is **finished**, rename the session again with the *same* title plus a trailing ` ✓` (e.g. `#42 scanner: widen host matching ✓`).

Rename with the OpenCode API — `opencode api` reuses the TUI's service discovery and auth, and `$OPENCODE_SESSION_ID` identifies the current session:

```sh
opencode api session.update --param sessionID="$OPENCODE_SESSION_ID" -d '{"title":"#42 scanner: widen host matching"}'
```

Escape `"` and `\` inside the title as JSON requires.

The two finish points:
- **Auto mode** — right after the implementation and the post-solve comment (Auto mode, step 5). The change is implemented and reported; the session's work is done.
- **Manual mode** — at the post-archive boundary, in the archive session. The change is only specced at hand-off, so never mark it done then. Reconstruct the title exactly as step 1 would (`#<N> <issue title trimmed to ~60 chars>`, with `<N>` and the issue title resolved from the change's `Change: <id>` link) and append ` ✓`.

Never append ` ✓` to a change that is only specced, blocked, or paused. If the rename call fails, note it once and continue.

## 1. Check out the issue

Fetch issue + comments; read title, labels, body (sections per the project's conventions — typically Problem / Fix / Rulings / Done when / Out of scope), and comments.

Then rename the session so it reflects the work for the rest of the run: run the rename command above with `#<N> <issue title trimmed to ~60 chars>` (e.g. `#42 scanner: widen host matching`). Do this before triage; if the rename call fails, note it once and continue. This title marks the work as *in progress* — the ✓ is added only when the change is finished (see **Session title on completion**).

Guardrails:
- Label `product` → stop and tell the user it routes to the project roadmap, not an OpenSpec change.
- Body already contains `Change: <id>`: if `openspec/changes/<id>/` exists, continue it instead of creating a new change (skip step 3 creation, still review). If it exists only under `openspec/changes/archive/`, the issue is effectively solved — report that and stop; closure comes from the archiving commit's `Fixes #<N>`, don't re-spec.
- Label `draft`: the body is a human-written stub — vague by design. Batch clarifying questions to the user first (step-2 style), then rewrite the whole issue to house style via the `github-issue` skill — title, body (skeleton filled, claims verified), and labels (apply the authoritative priority tier) — and remove the `draft` label before continuing. Human-written body/comments on a `draft` issue may be rewritten without asking (per the `github-issue` skill).
- One issue = one shippable unit (AGENTS.md). If the issue spans several independent subsystems, say so before speccing and propose a split.
- Verify the issue's refs and load-bearing claims against the current codebase: refs must resolve; claims must be verified empirically where cheap (run the function or query, grep for an alleged absence). Fix stale refs/claims in the body (PATCH rule in the `github-issue` skill) and stamp the body with a one-line verification note (date + model; the stamp doubles as the issue's signature). A false load-bearing claim → stop and report before speccing; never spec from an unverified claim.

## 2. Resolve open questions first

Look for undecided rulings: `needs-ruling` label, ⚖ items with no decision, explicit open questions in body/comments. If none → continue to step 3.

If any exist, batch ALL of them into ONE question-tool call, with a recommendation/options per question. Do not guess decisions.

After the user answers:
1. Record each decision by editing the Rulings section (preserve the rest of the body verbatim) and PATCH the issue.
2. Remove the `needs-ruling` label once every ruling is decided (skip if not present):
   `DELETE /issues/<N>/labels/needs-ruling`

## 3. Create the OpenSpec change

Load the `openspec-propose` skill and follow it; input = issue content (title, requirements, rulings, link). Change name: use the issue key if the title has one (e.g. `scanner-widening-2`), else a 2–4 word kebab-case name.

Then add the `Change: <id>` line to the issue body (PATCH as above).

Make sure `tasks.md` ends with: (a) update the changelog per the project's changelog skill (R packages: `r-news-styleguide`; other projects: `changelog-style-guide`; omit if the project has none) and choose the bump with `semver`, (b) post the post-solve comment per the `issue-comment` skill.

For bug issues, `tasks.md` must also *start* with reproducing the issue's claim as a failing test — that test is the authoritative claim check and must pass after implementation (per the project's definition of done).

Docs↔specs sync: if the spec settles anything that affects the project's binding docs (per AGENTS.md), flag it for the user during hand-off (step 7). Doc edits are always explicitly confirmed, never silent.

## 4. Independent spec review

Delegate to the `spec-reviewer` subagent via the Task tool — fresh context, read-only, cannot edit. Prompt: "Review OpenSpec change `<id>` in `openspec/changes/<id>/`. Follow your agent instructions. Return only the review report." If the subagent isn't installed, use a general read-only subagent and give it the criteria inline: completeness, consistency, clarity, scope, YAGNI; report issues + advisory recommendations only. Wait for the report.

## 5. Auto-fix what needs no human

Apply every *Issues Found* item that is resolvable from the issue text, binding docs, and repo conventions without changing scope, behavior, cost, or user-facing requirements. Edit the artifacts directly; note each fix. Advisory recommendations: apply only if clearly non-controversial, otherwise carry them to the final summary.

## 6. Escalate what needs a human

For remaining findings that require a real decision (scope, behavior, tradeoffs, unresolvable ambiguity), batch them into ONE question-tool call with your recommendation per item. Apply the answers to the artifacts. If the answers change requirements, re-check spec deltas and tasks for consistency.

## 7. Re-review and hand off

1. Run the `spec-reviewer` subagent once more on the updated change. Apply new fixable issues; do not loop more than twice — surface leftovers to the user.
2. Docs sync per AGENTS.md: review the settled spec against the project's binding docs; propose any doc update and get explicit confirmation before editing. If a doc changes, bump its `Status:` version + date and verify cross-references.
3. Run the project's doc checker if one exists (see AGENTS.md/README for the command): fix in-scope findings, surface the rest.
4. Run `openspec validate --changes` and `openspec status --change <id>`; fix any validation failure before hand-off. Spec-hygiene detail — the validator checks only the **first source line** of a requirement body for `SHALL`/`MUST` — lives in the spec-hygiene guardrail of the openspec skills.
5. Summarize: change name/location, review status, fixes applied, rulings recorded, doc-sync result, doc-checker result, leftover advisory items.
6. Manual mode: close with "Ready for `/opsx-apply`." Auto mode: continue to Auto mode below. Manual mode does **not** mark the session done — the change is only specced at hand-off (see **Session title on completion**).

## Auto mode (`$ARGUMENTS` contains `auto`)

No issue number needed, and the run does not stop before implementation. Questions still pause the run when a human decision is genuinely required.

**Selection** — fetch `GET /issues?state=open&per_page=50` and pick the best eligible issue:
- Exclude: PR entries, `product` issues, `needs-ruling` issues, `draft` issues (stubs need an interactive rewrite), issues with unresolved ⚖ items or explicit open questions in body/comments, issues spanning several independent subsystems, issues too vague to spec without guessing.
- Prefer explicit acceptance criteria ("Done when"), then priority labels per the project conventions (e.g. `P1` > `P2` > `P3` > unlabeled), then lowest issue number.
- Skip issues that already carry a `Change: <id>` link: an active `openspec/changes/<id>/` may be mid-flight in another session, and an archived one is effectively solved. Both stay available via the explicit `/issue-to-spec <N>` path.
- Announce the pick and a one-line reason, then rename the session (see **Session title on completion**) with `#<N> <issue title trimmed to ~60 chars>`; the ` ✓` comes later, when the change is finished. If nothing is eligible, stop and report why.

**Execution deltas** for steps 1–7:
- Step 1's claim verification is blocking here — no human has read the issue this session; a false load-bearing claim stops the run.
- Step 2 normally finds nothing for an eligible issue — if something slipped through, ask instead of guessing.
- Steps 6 and 7-docs: batch-ask any human decisions, including needed binding-doc edits (AGENTS.md: doc edits are always explicit).
- Step 7 summary happens, then continue below instead of handing off.

**Implement:**
1. Load the `openspec-apply-change` skill and follow it for the change.
2. Update the changelog per the project's changelog skill if one exists — R packages: `r-news-styleguide`; other projects: `changelog-style-guide`; omit if the project has none. The skill decides what gets an entry; never skip an entry the skill requires. Choose the version bump with the `semver` skill — a release takes the highest bump its entries require (breaking → major; `Added`/`Deprecated`/backwards-compatible `Changed` → minor; `Fixed`/internal-only/docs-only → patch). In R packages, rule 14 bumps on completion; elsewhere the bump is applied when `[Unreleased]` is cut. Run the skill's validation; release promotion happens at the post-archive boundary, not here.
3. Run the checks required by the skill and the project's AGENTS.md (tests/lint), plus any check the change's tasks require.
4. If implementation settled any ⚖ decisions, record them in the issue's Rulings section (body PATCH) first. Then post the post-solve comment per the `issue-comment` skill (`POST /issues/<N>/comments`).
5. Mark the session done: rename it with the same title plus a trailing ` ✓` (e.g. `#42 scanner: widen host matching ✓`) — the change is implemented and reported (see **Session title on completion**).
6. Report: tasks completed, checks run + outcomes, files touched, changelog entry, comment URL.
7. Stop: no archive, no commit. Suggest `/opsx-archive` (and a closing commit with `Fixes #<N>`) once the user has verified.
8. Task unclear, blocker, or failing check you can't fix → pause and report, same as manual mode; do not mark the session done.

**Hard rules**
- Manual mode: no implementation code. Auto mode: implement only via the `openspec-apply-change` skill, only after the reviewed spec exists. Never commit in either mode.
- Never echo the GitHub token.
- One batched question call per escalation round; ask only what genuinely needs a human.
- Follow the project's AGENTS.md (docs map, issue mechanics, package conventions) at all times.
