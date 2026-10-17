---
name: github-issue
description: Use when filing, drafting, or reformatting a GitHub issue — turning notes or discussion into an issue, filing follow-up work from a solved issue, or checking an issue body against house style. Also carries the self-contained GitHub REST helper used by the issue-to-spec command.
---

Compose issues for the project's issue registry (defined in AGENTS.md — it wins over the defaults below).

## Body

1. Use the project's section skeleton (default: `**Problem**` / `**Fix**` / `**Rulings**` / `**Done when**` / `**Out of scope**`).
2. Delete sections that stay empty before filing. Keep the body under ~40 lines.
3. Fill the sections:
   - **Problem** — what is wrong or missing, and why it matters. `file:line` for code; doc name + `§` for binding docs. Verify old `file:line` refs still resolve before trusting them.
   - **Fix** — concrete task list (`- [ ]`); name the required spec delta inline (project notation, e.g. `Δspec: <capability>`).
   - **Rulings** — ⚖ only decisions that need the owner: options + one recommendation. Resolved by editing this section; `needs-ruling` label while undecided.
   - **Done when** — machine-checkable acceptance: tests that must exist/pass, commands to run, doc bumps.
   - **Out of scope** — only when a reader (human or agent) might plausibly wander there.
4. One issue = one shippable unit; split anything an agent session can't finish. Issues carry context, not designs — design belongs in the OpenSpec change. Follow-up work becomes new issues, never TODO comments.
5. Title: imperative, front-load the what; an `area:` prefix is fine when it helps scanning.
6. Labels (this is the authoritative set — don't invent others): `P1` highest priority · `P2` medium · `P3` low — pure priority tiers, not failure modes (that context lives in the title/body); `needs-ruling` decision pending; `product` routed to ROADMAP, not a code change.
7. No token values; no personal data beyond what the fix needs.

When composing in chat, output the issue markdown only — no commentary around it.

## GitHub REST helper

Self-contained — derives `owner/repo` from `git remote get-url origin`, resolves the token per the project convention (default `<REPO>_GH_TOKEN`: repo name uppercased, `-`/`.` → `_`, e.g. `FIRE_GH_TOKEN`, read from `~/.Renviron`; fallback `GH_TOKEN`/`GITHUB_TOKEN`; never printed or logged):

```bash
python3 - METHOD PATH [FILE|JSONFILE] <<'PY'
import json, os, re, subprocess, sys, urllib.request

method, path, *rest = sys.argv[1:]
slug = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True).stdout.strip()
slug = re.sub(r'\.git$', '', re.sub(r'^(git@github\.com:|https://github\.com/)', '', slug))
if '/' not in slug:
    sys.exit('cannot derive owner/repo from git remote origin')
var = re.sub(r'[-.]', '_', slug.split('/')[-1]).upper() + '_GH_TOKEN'
try:
    env = open(os.path.expanduser('~/.Renviron')).read()
except OSError:
    env = ''
m = re.search(rf'^{var}=(\S+)', env, re.M)
tok = ((m.group(1).strip('"\'') if m else '') or os.environ.get('GH_TOKEN')
       or os.environ.get('GITHUB_TOKEN'))
if not tok:
    sys.exit(f'no token: set {var} in ~/.Renviron or GH_TOKEN')
payload = None
if rest:
    text = open(rest[0]).read()
    payload = text.encode() if rest[0].endswith('.json') else json.dumps({'body': text}).encode()
req = urllib.request.Request(
    'https://api.github.com/repos/' + slug + path, data=payload,
    headers={'Authorization': 'Bearer ' + tok, 'Accept': 'application/vnd.github+json'},
    method=method)
resp = urllib.request.urlopen(req)
if method == 'DELETE':
    print('done')
else:
    data = json.load(resp)
    print(json.dumps(data, indent=2)[:6000] if method == 'GET' else data.get('html_url', 'ok'))
PY
```

- A file argument ending in `.md` is wrapped as `{"body": <text>}` (comments, body updates); ending in `.json` it is sent as the raw payload (e.g. creating an issue with `{"title", "body", "labels"}`).
- Examples:
  - `python3 - GET /issues/42` · `python3 - GET "/issues?state=open&per_page=50"`
  - `python3 - POST /issues /tmp/opencode/issue.json` (create)
  - `python3 - PATCH /issues/42 /tmp/opencode/issue-42-body.md` (rulings, `Change:` link)
  - `python3 - POST /issues/42/comments /tmp/opencode/issue-42-comment.md`
  - `python3 - DELETE /issues/42/labels/needs-ruling`

## Lifecycle

- The issue-to-spec workflow writes the `Change: <id>` link into the body and records decided rulings by editing the Rulings section.
- Post-solve summary comments follow the `issue-comment` skill.
- Close with `Fixes #<N>` in the archiving/closing commit.
