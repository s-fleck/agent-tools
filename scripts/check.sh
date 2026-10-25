#!/usr/bin/env bash
# Local and CI gate for canonical skill changes.
#
# Usage: scripts/check.sh [base-revision]
#
# The default base is origin/master, which is correct inside a per-session
# worktree. CI passes the event base (the PR base or the pushed-from commit).
set -euo pipefail

base="${1:-origin/master}"
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if ! git rev-parse --verify --quiet "$base^{commit}" >/dev/null; then
  echo "ERROR: base revision '$base' not found." >&2
  exit 2
fi

echo "==> Validating canonical repo against $base"
python3 skills/skill-update/scripts/check_skill.py --repo . --strict

mapfile -t changed < <(
  {
    git diff --name-only "$base" -- 'skills/*'
    git ls-files --others --exclude-standard -- 'skills/*'
  } | sed -E 's|^skills/([^/]+)/.*$|\1|' | sort -u
)

if [ "${#changed[@]}" -eq 0 ]; then
  echo "==> No skill changes against $base"
  exit 0
fi

for skill in "${changed[@]}"; do
  if [ ! -d "skills/$skill" ]; then
    echo "ERROR: skill '$skill' was deleted; handle removal explicitly." >&2
    exit 1
  fi
  echo "==> Checking version bump for $skill"
  python3 skills/skill-update/scripts/check_skill.py \
    --check-bump "$skill" --base "$base"
done
