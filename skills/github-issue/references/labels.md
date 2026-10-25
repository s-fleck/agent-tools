# GitHub Issue Labels

Issue labels come from a resolved set, never from memory. This reference owns the resolution order and the default label semantics. The parent `SKILL.md` tells the agent to read it before applying, changing, or checking a label; `issue-to-spec` reads it for triage. Read the project's AGENTS.md first — it wins on conflict.

## Resolution Order

Resolve the set once per repository before applying, changing, or relying on a label. Re-resolve if the project's AGENTS.md or label settings change.

1. **Defaults in this reference** — the baseline roles and names in [Default Labels](#default-labels). The set is deliberately small: priority tiers, `needs-ruling`, `product`, and `draft`; standard GitHub triage labels are not applied by the agent by default.
2. **Project AGENTS.md** — adds labels, replaces a default role (for example, product-direction is `idea` instead of `product`), refines semantics, and may forbid labels: "do not use `bug`", "never apply `wontfix`". An explicit project rule wins over a default and over a GitHub label description.
3. **Project GitHub labels** — `GET /labels` is the inventory of names that actually exist. Read the description; it can add a label, replace a default role, refine its use, or deny it when AGENTS.md does not define it.

Project sources replace a default for its role, and AGENTS.md wins over a GitHub description on the same label. Defaults apply only where no project source overrides them, so AGENTS.md needs to state only additions, replacements, and denials. A project can deny any label in AGENTS.md or in the label's GitHub description; AGENTS.md wins if the two conflict. A deny rule is binding for the agent: do not apply, remove, or rely on that label, even when another source suggests otherwise. A denied role with no project replacement is inactive; do not substitute an unmentioned label without asking. If a rule might be a deny rule, ask before using the label.

## Required Label Metadata

A label outside the defaults is usable only when its source explains:

- what it means (the purpose),
- when the agent applies it.

A label that records a state the agent later removes or replaces also needs a close-out rule: the condition under which the agent removes or replaces it. Permanent classification labels (`bug`, `area:*`, `documentation`) do not need one.

AGENTS.md and the GitHub label description are the only sources. A name alone, or a description that only repeats the name, is not enough. Existence is not permission: a label must say when the agent applies it, not merely what it means.

When a label you need lacks that metadata:

1. Ask the user what it means and when it should be applied (and, for a state label, when it is removed or replaced). Batch all unclear labels into one question call.
2. Ask whether the answer belongs in the project's AGENTS.md or in the label's GitHub description. Do not encode it silently.
3. If the user chooses AGENTS.md, add the rule there in the same pass, following the project's doc rules. If they choose the GitHub description, update it only with permission.
4. Do not apply the label until the answer is in hand. If the label is not needed for the current work, leave it alone.

Do not audit labels unrelated to the issue at hand.

## Repository Inventory

Fetch the repository's labels as part of resolving the set, and again whenever the project's label setup may have changed:

```bash
python3 .opencode/skills/github-issue/github-rest.py --paginate GET "/labels?per_page=100"
```

`github-rest.py` is in the skill directory, one level up from this reference; from the canonical repo that is `skills/github-issue/github-rest.py`. It is the project's only GitHub client; `--paginate` follows `Link rel=next` and prints one JSON array. Do not use the `gh` CLI.

- Use the exact name and casing returned by GitHub.
- Skip labels with a non-null `archived_at`; they cannot be applied to new work.
- Apply only labels that exist in the repository. A default role with no matching label is inactive; do not create the label unless the user asks.
- If AGENTS.md names a label that is absent from the repository, stop and ask whether to create it or which existing label fills the role.
- Do not invent a label, repurpose one contrary to its description, or create or delete a label without explicit permission.

## Default Labels

| Role | Default name | Use |
|---|---|---|
| priority | `P1` / `P2` / `P3` | Highest / medium / low priority. Apply at most one; priority is a tier, not a failure mode — the failure context belongs in the title and body. A project may define more tiers or different names; use its order. |
| needs-ruling | `needs-ruling` | A decision is pending. Apply when a ⚖ item is undecided; remove once every ruling is decided. |
| product-direction | `product` | Product-direction issue, not a code change; routes to the project roadmap (a project may call it `idea`). Apply to an unsettled direction, not to shippable work. Remove it once the direction is settled — folded into binding docs, spawned as issues, or rejected — per AGENTS.md. |
| draft | `draft` | Human-written stub. A human applies it; the agent does not apply it to its own issues. When work starts, clarify the open points, rewrite title/body/labels to house style, then remove it. Human-written text on a `draft` issue may be rewritten without asking. |

The standard GitHub labels (`bug`, `enhancement`, `documentation`, `question`, `invalid`, `duplicate`, `wontfix`) are not part of the agent's default set. They are triage and classification labels owned by humans unless AGENTS.md or the description explicitly assigns one to agent use.

## Apply, Change, Remove

All writes go through the same helper. A `.json` payload is sent verbatim; any other file is wrapped as `{"body": <text>}`. The payload rules and token handling are in the parent `SKILL.md`.

```bash
python3 .opencode/skills/github-issue/github-rest.py POST /issues/42/labels /tmp/opencode/labels.json
# /tmp/opencode/labels.json: {"labels": ["P2", "needs-ruling"]}
```

The `.json` suffix is required for a label payload; a `.md` file would be sent as a body update instead.

- **At issue creation:** put the resolved names in the `labels` array of the `POST /issues` payload.
- **Add labels:** `POST /issues/<N>/labels` with `{"labels": ["<name>", ...]}` adds without touching the existing set.
- **Replace the set:** `PUT /issues/<N>/labels` with `{"labels": [...]}` removes every label not in the payload. Use it only when the caller intends to replace the whole set, and re-read the issue first.
- **Remove one label:** `DELETE /issues/<N>/labels/<name>`; URL-encode names containing spaces, `/`, or `#`.
- **When maintaining an issue:** re-fetch its current labels before changing them, and touch only the labels whose role — and, for state labels, close-out rule — you resolved. Leave human triage labels alone.

If no resolved label expresses the needed state, leave the issue unlabeled and say so; never invent a label to fill the gap.
