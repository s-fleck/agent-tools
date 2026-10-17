---
description: Triage a GitHub issue into a reviewed OpenSpec change; `auto` also implements it
agent: build
---

Drive GitHub issue `$ARGUMENTS` from triage to a reviewed OpenSpec change ready for `/opsx-apply`. Flow: fetch issue → resolve open rulings → create change → independent spec review → auto-fix → escalate real decisions. You do NOT implement or commit — unless Auto mode is requested.

**Auto mode:** `/issue-to-spec auto` selects the best issue that needs no human input, runs the same flow unattended, then implements it via the `openspec-apply-change` skill. Details at the bottom of this file.

**Input:** the issue number (e.g. `42`), an issue URL, or `auto` (see Auto mode). If `$ARGUMENTS` is empty, fetch the open issues (`GET /issues?state=open&per_page=50`, see below) and make ONE question-tool call: one option per issue, label `#<n> — <short title>`, description = labels + one-line gist. Ignore entries with a `pull_request` field (PRs), and mark `product`-labeled issues in the description as "routes to the project roadmap" instead of offering them as work. Continue with the chosen number as `<N>`.

## GitHub access

Load the `github-issue` skill — it carries the self-contained helper (derives `owner/repo` from `git remote get-url origin`; resolves the token per the project convention: default `<REPO>_GH_TOKEN` — repo name uppercased, `-`/`.` → `_` — in `~/.Renviron`, e.g. `FIRE_GH_TOKEN`; falls back to `GH_TOKEN`/`GITHUB_TOKEN`; never print or log it). Typical calls:

- `python3 - GET /issues/<N>` · `python3 - GET /issues/<N>/comments` · `python3 - GET "/issues?state=open&per_page=50"`
- `python3 - PATCH /issues/<N> /tmp/opencode/issue-<N>-body.md` — full body update (rulings, `Change:` link)
- `python3 - POST /issues/<N>/comments /tmp/opencode/issue-<N>-comment.md`
- `python3 - DELETE /issues/<N>/labels/needs-ruling`

If `$ARGUMENTS` is a URL, extract the issue number from it.

## Project conventions

Everything project-specific comes from the project's AGENTS.md and skills: issue skeleton, labels, ruling (⚖) handling, binding docs, checks to run, changelog skill (R packages: `r-news-styleguide`). Companions expected in `.opencode/`: `github-issue` and `issue-comment` skills, `spec-reviewer` subagent.

## 1. Check out the issue

Fetch issue + comments; read title, labels, body (sections per the project's conventions — typically Problem / Fix / Rulings / Done when / Out of scope), and comments.

Guardrails:
- Label `product` → stop and tell the user it routes to the project roadmap, not an OpenSpec change.
- Body already contains `Change: <id>`: if `openspec/changes/<id>/` exists, continue it instead of creating a new change (skip step 3 creation, still review). If it exists only under `openspec/changes/archive/`, the issue is effectively solved — report that and stop; closure comes from the archiving commit's `Fixes #<N>`, don't re-spec.
- One issue = one shippable unit (AGENTS.md). If the issue spans several independent subsystems, say so before speccing and propose a split.
- Verify `file:line` / doc references in the issue still resolve.

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

Make sure `tasks.md` ends with: (a) update the changelog per the project's changelog skill (R packages: `r-news-styleguide`; omit if the project has none), (b) post the post-solve comment per the `issue-comment` skill.

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
3. Run the project's doc checker if one exists (e.g. `Rscript tools/check-docs.R`): fix in-scope findings, surface the rest.
4. Run `openspec status --change <id>`.
5. Summarize: change name/location, review status, fixes applied, rulings recorded, doc-sync result, doc-checker result, leftover advisory items.
6. Manual mode: close with "Ready for `/opsx-apply`." Auto mode: continue to Auto mode below.

## Auto mode (`$ARGUMENTS` contains `auto`)

No issue number needed, and the run does not stop before implementation. Questions still pause the run when a human decision is genuinely required.

**Selection** — fetch `GET /issues?state=open&per_page=50` and pick the best eligible issue:
- Exclude: PR entries, `product` issues, `needs-ruling` issues, issues with unresolved ⚖ items or explicit open questions in body/comments, issues spanning several independent subsystems, issues too vague to spec without guessing.
- Prefer explicit acceptance criteria ("Done when"), then priority labels per the project conventions (e.g. `P1` > `P2` > `P3` > unlabeled), then lowest issue number.
- Skip issues that already carry a `Change: <id>` link: an active `openspec/changes/<id>/` may be mid-flight in another session, and an archived one is effectively solved. Both stay available via the explicit `/issue-to-spec <N>` path.
- Announce the pick and a one-line reason. If nothing is eligible, stop and report why.

**Execution deltas** for steps 1–7:
- Step 2 normally finds nothing for an eligible issue — if something slipped through, ask instead of guessing.
- Steps 6 and 7-docs: batch-ask any human decisions, including needed binding-doc edits (AGENTS.md: doc edits are always explicit).
- Step 7 summary happens, then continue below instead of handing off.

**Implement:**
1. Load the `openspec-apply-change` skill and follow it for the change.
2. Update the changelog per the project's changelog skill if one exists (R packages: `r-news-styleguide` — extend the existing development-version entry for this feature if there is one, else add one; then run the skill's validation). Skip only if the change has no user-visible effect — say so in the report.
3. Run the repo checks required by the skill and AGENTS.md (tests/lint).
4. If implementation settled any ⚖ decisions, record them in the issue's Rulings section (body PATCH) first. Then post the post-solve comment per the `issue-comment` skill (`POST /issues/<N>/comments`).
5. Report: tasks completed, checks run + outcomes, files touched, changelog entry, comment URL.
6. Stop: no archive, no commit. Suggest `/opsx-archive` (and a closing commit with `Fixes #<N>`) once the user has verified.
7. Task unclear, blocker, or failing check you can't fix → pause and report, same as manual mode.

**Hard rules**
- Manual mode: no implementation code. Auto mode: implement only via the `openspec-apply-change` skill, only after the reviewed spec exists. Never commit in either mode.
- Never echo the GitHub token.
- One batched question call per escalation round; ask only what genuinely needs a human.
- Follow the project's AGENTS.md (docs map, issue mechanics, package conventions) at all times.
