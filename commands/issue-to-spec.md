---
description: Triage a GitHub issue into a reviewed OpenSpec change; auto mode also implements it, with or without an issue number
agent: build
---

## Arguments

Usage: `/issue-to-spec [auto] [<issue>]`

OpenCode supplies the invocation: first position = $1; remaining positions = $2.

| First position | Remaining | Mode | Target |
|---|---|---|---|
| empty | empty | manual | interactive picker |
| `<issue>` | empty | manual | first position |
| `auto` | empty | auto | auto-select |
| `auto` | `<issue>` | auto | remaining |
| anything else | anything | — | usage error, stop |

`<issue>` is the issue number (`42`), a `#`-prefixed number (`#42`), or a URL to an issue in this repository.

Rules:
- `auto` is matched as a whole token, case-insensitively, and only in the first position. Never use substring matching: an issue URL that contains `auto` is still a URL.
- At most one target. Anything not in the table — `42 auto`, `auto 42 extra`, `auto auto`, an unknown word, a PR URL, or a URL from another repository — prints the usage block and stops before any GitHub fetch. Do not guess a target. For `42 auto`, suggest `/issue-to-spec auto 42`.
- Normalize `42` and `#42` to `<N>`. For a URL, require the same repository as the project and extract the issue number only after that check; reject `/pull/` URLs. A numeric target that resolves to a PR also stops.
- With an explicit target, skip issue selection entirely (both the picker and Auto mode's Selection; do not fetch the open-issue list). An explicit target still goes through the step-1/step-2 guardrails.

**Interactive picker (manual mode, no target):** fetch the open issues (`--paginate GET "/issues?state=open&per_page=100"`, see below) and make ONE question-tool call: one option per issue, label `#<n> — <short title>`, description = labels + one-line gist. Ignore entries with a `pull_request` field (PRs). Do not offer an issue carrying a disposition label (`wontfix`/`invalid`/`duplicate`/`question`), a project blocked/hold label, a non-empty `assignees` list, or an open sub-issue tracker; if that empties the picker, report the excluded issues and why. Mark product-direction issues (resolved from the `github-issue` labels reference; default `product`, or a project equivalent such as `idea`) in the description as "routes to the project roadmap" instead of offering them as work. A `stale` label or a missing ready-gate is noted in the description, not a reason to hide the issue. Continue with the chosen number as `<N>`.

`auto` is the **execution mode** ("spec, review, then implement"). The target is separate: supply one and auto skips selection; omit it and auto selects. Bare `auto` never opens the picker.

Drive the resolved issue from triage to a reviewed OpenSpec change ready for `/opsx-apply`. Flow: fetch issue → rename session → resolve open rulings → create change → independent spec review → auto-fix → escalate real decisions. You do NOT implement or commit — unless Auto mode is requested. The session title gets a trailing ` ✓` once the change is finished (see **Session title on completion**).

Auto mode runs the same flow, then implements via the `openspec-apply-change` skill; details at the bottom.

## GitHub access

Load the `github-issue` skill — it carries the REST helper (`github-rest.py`, called directly with `python3`, token rules included), the house style for issue bodies and comments, and the labels reference (`references/labels.md`), which resolves the label roles and read-only triage signals used below. If the target is a URL, its repository must match the project's; extract the issue number only after that check.

## Project conventions

Everything project-specific comes from the project's AGENTS.md and skills: issue skeleton, ruling (⚖) handling, binding docs, checks to run, changelog skill (R packages: `r-news-styleguide`; other projects: `changelog-style-guide`), versioning (`semver`). Milestone and project-board status are project-specific too: when AGENTS.md makes either a gate, read it through the project's documented path and treat `In progress`/`Done` like an assignee or terminal signal. Companions expected in `.opencode/`: the `github-issue` skill and the `spec-reviewer` subagent.

**Label roles.** Resolve the project's labels from the `github-issue` labels reference (`references/labels.md`) before triage. This command uses four write roles: *priority* (default `P1`–`P3`), *needs-ruling* (default `needs-ruling`), *product-direction* (default `product`, sometimes `idea`), and *draft* (default `draft`). It also reads the reference's read-only triage signals: *disposition* (defaults `wontfix`, `invalid`, `duplicate`, `question`), *stale*, project-defined *blocked*/*hold* labels, an optional *ready-gate*, and *classification* hints (`bug`, `enhancement`, `documentation`). The resolved names win over the defaults named below. Never apply, change, or remove a read-only signal; a write deny in AGENTS.md does not hide a human-applied one.

## Session title on completion

The title set in step 1 (or by Auto mode's target resolution) marks the work as *in progress*. When the change is **finished**, rename the session again with the *same* title plus a trailing ` ✓` (e.g. `#42 scanner: widen host matching ✓`).

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

Resolve the label roles and triage signals from the `github-issue` labels reference (see **Label roles**), then fetch the issue and all comments (`--paginate GET "/issues/<N>/comments?per_page=100"`); read title, labels, body (sections per the project's conventions — typically Problem / Fix / Rulings / Done when / Out of scope), and comments. When reading comments, ignore `user.type == "Bot"` (including `[bot]` logins) for rulings and open questions, and treat only comments with `author_association` `OWNER`, `MEMBER`, or `COLLABORATOR` as able to settle a ruling or create a blocking open question; report a drive-by question instead of treating it as a decision.

Then rename the session so it reflects the work for the rest of the run: run the rename command above with `#<N> <issue title trimmed to ~60 chars>` (e.g. `#42 scanner: widen host matching`). Do this before triage; if the rename call fails, note it once and continue. This title marks the work as *in progress* — the ✓ is added only when the change is finished (see **Session title on completion**).

Guardrails:
- The fetched object has a `pull_request` field → stop; this command works on issues only.
- The product-direction label (default `product`, project equivalent e.g. `idea`) → stop and tell the user it routes to the project roadmap, not an OpenSpec change.
- A disposition label (`wontfix`, `invalid`, `duplicate`, `question`): report it. `duplicate` names the canonical issue (from the body, comments, or `state_reason`), is never specced, and should be offered as the target instead; `question` routes to an answer and is never specced unless the user confirms a mislabel; `wontfix`/`invalid` ask before continuing, and only an explicit override proceeds. A `stale` label is noted, not a blocker.
- The issue is `closed` and no active or archived change is known (check the `Change:` link and the reverse search below): read `state_reason`. `not_planned` or `duplicate` → stop with the reason; to proceed, the issue must be reopened. `completed` with a merged closing PR or closing commit → report it as solved and stop. Otherwise report the closure and ask before proceeding. (The picker and Auto mode's Selection only offer open issues.)
- `assignees` is non-empty → report who is assigned and ask before continuing; Auto Selection excludes assigned issues.
- `sub_issues_summary.total > 0` with open children, or a body that is clearly a child-issue checklist → this is a tracker, not one shippable unit. Stop and ask which child to spec; if every child is completed, report the issue as ready to close instead. A `parent_issue_url` alone is fine.
- An open blocker — an explicit `Blocked by #<n>` line in the body, an issue dependency, or a resolved blocked/hold label — stops and asks; do not spec blocked work. A closed blocker is fine, but mention it.
- If the project defines a ready-gate label and the issue lacks it → ask before continuing; Auto Selection excludes the issue.
- A milestone or project-board status that AGENTS.md makes a gate: `In progress` asks like an assignee; `Done` reports the issue as effectively solved and stops. Read it through the project's documented path (REST does not expose project fields).
- Scan the issue timeline (`--paginate GET "/issues/<N>/timeline?per_page=100"`) for cross-referenced PRs:
  - an open or draft PR that references `#<N>` → ask before continuing (Auto Selection excludes it);
  - a merged PR that closes the issue (`Fixes #<N>`) → report the issue as solved and stop;
  - a merged or closed PR that only references `#<N>` → mention the prior work and ask.
- Body already contains `Change: <id>`:
  - exactly one id under `openspec/changes/<id>/` → continue it instead of creating a new change (skip step 3 creation, still review);
  - exactly one id only under `openspec/changes/archive/` → the issue is effectively solved — report it and stop; closure comes from the archiving commit's `Fixes #<N>`, don't re-spec;
  - several different ids → ask which is authoritative; never guess or create a second change;
  - the id exists in neither place → treat the link as dangling, search active/archived `proposal.md` files for `#<N>`, and ask before creating a new change.
- No `Change:` line, but an active/archived change names `#<N>` in its `proposal.md`: treat it as the issue's change (active → continue it, archived → report solved and stop) and add or repair the `Change:` line.
- The draft label (default `draft`): the body is a human-written stub — vague by design. Batch clarifying questions to the user first (step-2 style), then rewrite the whole issue to house style via the `github-issue` skill — title, body (skeleton filled, claims verified), and labels (apply the resolved priority tier) — and remove the draft label before continuing. Human-written body/comments on a draft issue may be rewritten without asking (per the `github-issue` skill).
- One issue = one shippable unit (AGENTS.md). If the issue spans several independent subsystems, say so before speccing and propose a split.
- The body's template or preflight checklist has unchecked items that the project treats as prerequisites → ask; do not spec until they are satisfied.
- Classify a bug from the GitHub issue type (`Bug`) first, then the read-only `bug` label, then the body; if the type and label disagree, prefer the type and note the conflict. Bug classification controls step 3's failing-test-first rule; it never blocks triage.
- `locked` is true → the post-solve comment cannot be posted. Note it; Auto mode skips the comment, reports the skip, and continues.
- Verify the issue's refs and load-bearing claims against the current codebase: refs must resolve; claims must be verified empirically where cheap (run the function or query, grep for an alleged absence). Fix stale refs/claims in the body (PATCH rule in the `github-issue` skill) and stamp the body with the verification line `verified YYYY-MM-DD (model: <model_id>)` (per the `github-issue` skill; the stamp is the issue's signature). If a stamp already exists, replace it in place; never append a second. A false load-bearing claim → stop and report before speccing; never spec from an unverified claim.

## 2. Resolve open questions first

Look for undecided rulings: the needs-ruling label (default `needs-ruling`), ⚖ items with no decision, and explicit open questions in the body or in maintainer comments. A maintainer comment (author association `OWNER`, `MEMBER`, or `COLLABORATOR`) that already settles an ⚖ item or an explicit open question is a decision, not an open question: record it in the Rulings section, remove the label when everything is decided, and do not re-ask. Ignore bot comments when judging whether a ruling is settled; report a drive-by (non-maintainer) question without treating it as a blocking decision.

If the needs-ruling label is present but no ⚖ item or maintainer question remains, treat it as stale: remove it, note it, and continue. Do not open an empty question round.

If any undecided items exist, batch ALL of them into ONE question-tool call, with a recommendation/options per question. Do not guess decisions.

After the user answers:
1. Re-fetch the issue immediately before editing, then record each decision by editing the Rulings section (preserve the rest of the body verbatim) and PATCH the issue.
2. Remove the needs-ruling label once every ruling is decided (skip if not present):
   `DELETE /issues/<N>/labels/<resolved needs-ruling label>` (default: `DELETE /issues/<N>/labels/needs-ruling`)

## 3. Create the OpenSpec change

Load the `openspec-propose` skill and follow it; input = issue content (title, requirements, rulings, link). Change name: use the issue key if the title has one (e.g. `scanner-widening-2`), else a 2–4 word kebab-case name.

Before creating, check the reverse link from step 1: if an active/archived change already names `#<N>`, continue it or stop instead of creating a second. Then add the `Change: <id>` line to the issue body. Re-fetch the issue immediately before the PATCH and merge the line into the current body — never PATCH a cached copy. If the PATCH fails after creation, report it; the next run's reverse search finds the change.

Make sure `tasks.md` ends with: (a) update the changelog per the project's changelog skill (R packages: `r-news-styleguide`; other projects: `changelog-style-guide`; omit if the project has none) and choose the bump with `semver`, (b) post the post-solve comment per the `github-issue` skill.

For bug issues (classified in step 1), `tasks.md` must also *start* with reproducing the issue's claim as a failing test — that test is the authoritative claim check and must pass after implementation (per the project's definition of done).

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

## Auto mode (spec + implement)

Auto mode runs the same steps 1–7, then implements. The target is optional:
- **No target** — run **Selection** below to pick the issue.
- **Explicit target** — skip Selection and start at step 1 with `<N>`; after fetching the issue, announce `Auto mode → #<N> <title> (explicit target)`.

Questions still pause the run when a human decision is genuinely required.

### Selection (only when no target)

Resolve the label roles and read-only triage signals (see **Label roles**), fetch `--paginate GET "/issues?state=open&per_page=100"`, and pick the best eligible issue:
- Exclude: PR entries; issues carrying the product-direction, needs-ruling, draft, or any disposition label (`wontfix`/`invalid`/`duplicate`/`question`); project blocked/hold labels; issues with a non-empty `assignees` list; a parent with open sub-issues (tracker); an open blocker; an open/draft linked PR or a merged PR that closes the issue (report the latter as solved); a merged or closed PR that only references the issue is reported, not treated as a solve; a missing ready-gate when the project defines one; an in-progress or done milestone/board state when AGENTS.md makes it a gate; issues with unresolved ⚖ items or maintainer open questions in body/comments; issues spanning several independent subsystems; issues too vague to spec without guessing.
- The list payload has no comments. Apply the cheap filters first, then fetch each shortlisted candidate's issue and all comments and verify the comment/PR/blocker filters before announcing. If a candidate fails, continue down the list. Do not silently skip the comment filter.
- Prefer explicit acceptance criteria ("Done when"), then the priority tier using the project's order from the labels reference (if several priority labels are present, use the highest and note the conflict; an unknown tier ranks lowest), then lowest issue number.
- Skip issues that already carry a `Change: <id>` link, or whose `#<N>` appears in an active/archived `proposal.md`: an active change may be mid-flight in another session, and an archived one is effectively solved. Both can be addressed explicitly with `/issue-to-spec auto <N>`: active changes are reviewed and ask before implementation; archived ones stop with the report.
- After choosing, re-fetch the issue; if it no longer meets these filters or has closed, drop it and continue down the list. Announce the pick and a one-line reason, then rename the session (see **Session title on completion**) with `#<N> <issue title trimmed to ~60 chars>`; the ` ✓` comes later, when the change is finished. If nothing is eligible, stop and report why; never fall back to the interactive picker.

These filters choose an issue for an unattended run. They do **not** validate an explicit target: `auto <N>` skips Selection and relies on the step-1/step-2 guardrails instead. A product-direction issue still stops; a disposition label stops (`wontfix`/`invalid` ask, `duplicate`/`question` stop); an assigned, blocked, tracker, or open-PR issue asks or stops per step 1; a draft or needs-ruling issue asks; a multi-subsystem or vague issue stops; an active change is reviewed and then asks before implementation; an archived change stops.

### Execution deltas for steps 1–7

- Step 1's claim verification is blocking in Auto mode — the run implements without a hand-off review, so a false load-bearing claim stops it.
- Step 1's triage signals apply in Auto mode too: terminal signals stop; ownership/readiness signals ask. Bare auto excludes them during Selection, so an ask here means the issue changed after selection.
- Re-fetch the issue before creating the change and before the post-solve comment; if it closed or gained a terminal signal in the meantime, stop.
- Step 2 may find rulings on an explicit target — batch-ask instead of guessing.
- Step 1's `Change: <id>` guardrail: for an active change, review it as usual, then **ask** whether to implement it here before continuing (it may be mid-flight in another session). For an archived change, stop as usual.
- A draft or needs-ruling target is allowed under explicit `auto <N>`: the user is present, so run the interactive rewrite and ruling steps. Bare auto still excludes both during Selection.
- Steps 6 and 7-docs: batch-ask any human decisions, including needed binding-doc edits (AGENTS.md: doc edits are always explicit).
- Step 7 summary happens, then continue below instead of handing off.

### Implement

1. Load the `openspec-apply-change` skill and follow it for the change.
2. Update the changelog per the project's changelog skill if one exists — R packages: `r-news-styleguide`; other projects: `changelog-style-guide`; omit if the project has none. The skill decides what gets an entry; never skip an entry the skill requires. Choose the version bump with the `semver` skill — a release takes the highest bump its entries require (breaking → major; `Added`/`Deprecated`/backwards-compatible `Changed` → minor; `Fixed`/internal-only/docs-only → patch). In R packages, rule 14 bumps on completion; elsewhere the bump is applied when `[Unreleased]` is cut. Run the skill's validation; release promotion happens at the post-archive boundary, not here.
3. Run the checks required by the skill and the project's AGENTS.md (tests/lint), plus any check the change's tasks require.
4. If implementation settled any ⚖ decisions, record them in the issue's Rulings section (body PATCH) first. Then post the post-solve comment per the `github-issue` skill (`POST /issues/<N>/comments`). If the issue is locked, skip the comment, note it in the report, and do not fail the run.
5. Mark the session done: rename it with the same title plus a trailing ` ✓` (e.g. `#42 scanner: widen host matching ✓`) — the change is implemented and reported (see **Session title on completion**).
6. Report: tasks completed, checks run + outcomes, files touched, changelog entry, comment URL.
7. Stop: no archive, no commit. Suggest `/opsx-archive` (and a closing commit with `Fixes #<N>`) once the user has verified.
8. Task unclear, blocker, or failing check you can't fix → pause and report, same as manual mode; do not mark the session done.

### Hard rules
- Manual mode: no implementation code. Auto mode: implement only via the `openspec-apply-change` skill, only after the reviewed spec exists. Never commit in either mode.
- Never write a read-only triage label (`wontfix`, `invalid`, `duplicate`, `question`, `stale`, project blockers/ready gates, classification hints) unless the user explicitly asks for that specific change; never spec a `duplicate` or a `question`.
- Never PATCH from a cached issue body; re-fetch immediately before every body edit.
- Never echo the GitHub token.
- One batched question call per escalation round; ask only what genuinely needs a human.
- Follow the project's AGENTS.md (docs map, issue mechanics, package conventions) at all times.
