#!/usr/bin/env python3
"""
Skill metadata validator for agent-tools.

Validates canonical skills, project variants, and landing bumps.
Usage:
  check_skill.py --repo <path>                        # validate canonical repo
  check_skill.py --variant <dir> --canonical <repo>   # validate project variant
  check_skill.py --check-bump <skill> --base <rev>    # validate strict bump
"""

from __future__ import annotations

import argparse
import dataclasses
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


@dataclasses.dataclass
class Frontmatter:
    name: str = ""
    description: str = ""
    license: str = ""
    compatibility: str = ""
    metadata: dict[str, str] = dataclasses.field(default_factory=dict)
    raw_metadata_lines: list[str] = dataclasses.field(default_factory=list)


def _strip_quotes(val: str) -> str:
    """Strip surrounding quotes from a YAML scalar value."""
    if len(val) >= 2:
        if (val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'"):
            return val[1:-1]
    return val


def parse_frontmatter(path: Path) -> Frontmatter:
    """Parse YAML frontmatter from SKILL.md. Values become strings."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return Frontmatter()
    end = text.find("\n---\n", 4)
    if end == -1:
        return Frontmatter()
    fm_text = text[4:end]
    fm = Frontmatter()
    lines = fm_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped:
            i += 1
            continue
        indent = len(line) - len(stripped)
        m = re.match(r"^(\w+):\s*(.*)$", stripped)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in ("|", ">"):
            # Block scalar: skip all deeper-indented continuation lines.
            i += 1
            while i < len(lines):
                cont = lines[i]
                if not cont.lstrip():
                    i += 1
                    continue
                if (len(cont) - len(cont.lstrip())) > indent:
                    i += 1
                    continue
                break
            continue
        val = _strip_quotes(val)
        if key == "name":
            fm.name = val
        elif key == "description":
            fm.description = val
        elif key == "license":
            fm.license = val
        elif key == "compatibility":
            fm.compatibility = val
        elif key == "metadata":
            # Parse the indented metadata block.
            i += 1
            while i < len(lines):
                ml = lines[i]
                mstripped = ml.lstrip()
                if not mstripped:
                    i += 1
                    continue
                mindent = len(ml) - len(mstripped)
                if mindent <= indent:
                    break
                mm = re.match(r"^(\w+):\s*(.*)$", mstripped)
                if mm:
                    mkey = mm.group(1)
                    mval = _strip_quotes(mm.group(2).strip())
                    fm.metadata[mkey] = mval
                    fm.raw_metadata_lines.append(ml)
                i += 1
            continue
        i += 1
    return fm


def run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def git_show(path: str, rev: str, cwd: Path) -> str:
    """Return the content of a file at a revision, or '' on error."""
    res = run_git(["show", f"{rev}:{path}"], cwd=cwd)
    if res.returncode != 0:
        return ""
    return res.stdout


def git_cat_file_exists(oid: str, cwd: Path) -> bool:
    res = run_git(["cat-file", "-e", f"{oid}^{{commit}}"], cwd=cwd)
    return res.returncode == 0


def git_is_ancestor(ancestor: str, descendant: str, cwd: Path) -> bool:
    res = run_git(["merge-base", "--is-ancestor", ancestor, descendant], cwd=cwd)
    return res.returncode == 0


def get_skill_dirs(repo: Path) -> list[Path]:
    skills = repo / "skills"
    if not skills.exists():
        return []
    return [d for d in skills.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]


def _parse_version_from_text(text: str) -> str:
    """Extract the first 'version: x.y.z' value from skill text."""
    for line in text.splitlines():
        m = re.match(r'^\s*version:\s*["\']?(\d+\.\d+\.\d+)["\']?', line)
        if m:
            return m.group(1)
    return ""


def validate_canonical_repo(repo: Path, strict: bool = False) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    skills = get_skill_dirs(repo)
    if not skills:
        errors.append("No skills found in repo")
        return errors

    versions: dict[str, str] = {}
    for skill_dir in skills:
        skill_name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        fm = parse_frontmatter(skill_md)
        raw = skill_md.read_text(encoding="utf-8")

        if not fm.name:
            errors.append(f"{skill_name}: missing frontmatter 'name'")
        elif fm.name != skill_name:
            errors.append(
                f"{skill_name}: frontmatter name '{fm.name}' "
                f"!= directory name '{skill_name}'"
            )

        # Description key must exist (value may be block scalar or inline).
        if not re.search(r"^description:\s*", raw, re.MULTILINE):
            errors.append(f"{skill_name}: missing frontmatter 'description'")

        if "author" not in fm.metadata:
            errors.append(f"{skill_name}: metadata.author missing")
        elif not fm.metadata["author"]:
            errors.append(f"{skill_name}: metadata.author empty")

        version = fm.metadata.get("version", "")
        if not version:
            errors.append(f"{skill_name}: metadata.version missing")
        elif not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(
                f"{skill_name}: metadata.version '{version}' "
                "not valid semver (MAJOR.MINOR.PATCH)"
            )
        else:
            versions[skill_name] = version

        # Canonical copies must not carry variant markers.
        for bad_key in ("variant", "upstream", "upstream_commit", "local_changes"):
            if bad_key in fm.metadata:
                errors.append(
                    f"{skill_name}: canonical copy has project marker '{bad_key}'"
                )

    # Duplicate skill IDs (case-insensitive).
    names_lower = [s.name.lower() for s in skills]
    for d in sorted({n for n in names_lower if names_lower.count(n) > 1}):
        errors.append(f"Duplicate skill ID (case-insensitive): {d}")

    # README Contents cross-references.
    readme = repo / "README.md"
    if readme.exists():
        readme_text = readme.read_text(encoding="utf-8")
        rows = re.findall(r"\|\s*`skills/([^`]+)`\s*\|", readme_text)
        skill_names = {s.name for s in skills}
        for row_name in rows:
            # Skip placeholder rows from the Layout table (e.g. <name>/).
            if "<" in row_name or ">" in row_name:
                continue
            if row_name not in skill_names:
                warnings.append(f"README Contents references missing skill: {row_name}")
        for skill_dir in skills:
            if f"`skills/{skill_dir.name}`" not in readme_text:
                warnings.append(
                    f"Skill {skill_dir.name} missing from README Contents table"
                )

    # CHANGELOG coverage and duplicate-version detection in [Unreleased].
    changelog = repo / "CHANGELOG.md"
    if changelog.exists():
        cl_text = changelog.read_text(encoding="utf-8")
        current_version: str | None = None
        unreleased: list[tuple[str, str]] = []
        all_entries: list[tuple[str, str, str]] = []
        for line in cl_text.splitlines():
            m = re.match(r"^##\s+\[([^\]]+)\]\s*-", line)
            if m:
                current_version = m.group(1)
                continue
            m = re.match(r"^-\s+\*\*([^*]+):\*\s*(.*)$", line)
            if m:
                area = m.group(1).strip()
                rest = m.group(2).strip()
                vm = re.search(
                    r"\((\d+\.\d+\.\d+(?:\+[a-zA-Z0-9.-]+)?)\)\s*$", rest
                )
                entry_version = vm.group(1) if vm else ""
                section = current_version or "Unreleased"
                all_entries.append((area, entry_version, section))
                if section == "Unreleased":
                    unreleased.append((area, entry_version))

        # Each skill's current version must appear in the changelog.
        for skill_name, version in versions.items():
            found = any(
                area == skill_name and entry_version == version
                for area, entry_version, _ in all_entries
            )
            if not found:
                errors.append(
                    f"{skill_name}@{version}: no changelog entry with matching version"
                )

        # Duplicate (skill, version) pairs within [Unreleased].
        seen: set[tuple[str, str]] = set()
        for area, entry_version in unreleased:
            if area in versions and entry_version:
                key = (area, entry_version)
                if key in seen:
                    errors.append(
                        f"Duplicate changelog entry in [Unreleased] "
                        f"for {area}@{entry_version}"
                    )
                seen.add(key)

        if "## [Unreleased]" not in cl_text:
            errors.append("CHANGELOG.md missing ## [Unreleased] section")

    if warnings and strict:
        errors.extend(warnings)
    else:
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)

    return errors


def extract_tree_at_commit(
    repo: Path, commit: str, prefix: str, dest: Path
) -> bool:
    """Extract a tree from a commit into dest using git archive."""
    res = run_git(["archive", commit, prefix], cwd=repo)
    if res.returncode != 0:
        return False
    try:
        with tarfile.open(fileobj=io.BytesIO(res.stdout.encode()), mode="r") as tf:
            tf.extractall(dest)
        return True
    except (tarfile.TarError, OSError):
        return False


def diff_dirs(a: Path, b: Path) -> list[str]:
    """Return the list of files that differ between two directories."""
    diffs: list[str] = []
    for root, _, files in os.walk(a):
        for f in files:
            rel = Path(root).relative_to(a) / f
            pa = a / rel
            pb = b / rel
            if not pb.exists() or pa.read_bytes() != pb.read_bytes():
                diffs.append(str(rel))
    for root, _, files in os.walk(b):
        for f in files:
            rel = Path(root).relative_to(b) / f
            if not (a / rel).exists():
                diffs.append(str(rel))
    return diffs


def validate_variant(
    variant_dir: Path, canonical_repo: Path, require_commit: bool = False
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    fm = parse_frontmatter(variant_dir / "SKILL.md")
    skill_name = variant_dir.name

    if not fm.name:
        errors.append(f"{skill_name}: missing frontmatter name")
        return errors

    variant = fm.metadata.get("variant", "")
    if not variant:
        errors.append(f"{skill_name}: missing metadata.variant")
        return errors
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", variant):
        errors.append(
            f"{skill_name}: metadata.variant '{variant}' "
            "not a valid slug (lowercase, hyphens)"
        )

    upstream = fm.metadata.get("upstream", "")
    upstream_name = ""
    upstream_version = ""
    if not upstream:
        errors.append(f"{skill_name}: missing metadata.upstream")
    else:
        m = re.match(r"^([a-z0-9]+(?:-[a-z0-9]+)*)@(\d+\.\d+\.\d+)$", upstream)
        if not m:
            errors.append(
                f"{skill_name}: metadata.upstream '{upstream}' "
                "malformed (expected name@version)"
            )
        else:
            upstream_name, upstream_version = m.group(1), m.group(2)

    upstream_commit = fm.metadata.get("upstream_commit", "")
    if upstream_commit:
        if not re.match(r"^[0-9a-f]{40}$", upstream_commit):
            errors.append(
                f"{skill_name}: metadata.upstream_commit "
                f"'{upstream_commit}' not a valid 40-hex commit hash"
            )
        elif not git_cat_file_exists(upstream_commit, canonical_repo):
            errors.append(
                f"{skill_name}: metadata.upstream_commit "
                f"'{upstream_commit}' not found in canonical repo"
            )
        else:
            # Verify it is an ancestor of origin/master (or HEAD).
            res = run_git(["rev-parse", "--verify", "origin/master"], cwd=canonical_repo)
            if res.returncode == 0:
                head = res.stdout.strip()
                if not git_is_ancestor(upstream_commit, head, canonical_repo):
                    warnings.append(
                        f"{skill_name}: upstream_commit not ancestor of origin/master"
                    )
            # Verify the commit's version matches the upstream version.
            if upstream_version:
                base_skill = git_show(
                    f"skills/{upstream_name}/SKILL.md",
                    upstream_commit,
                    canonical_repo,
                )
                if base_skill:
                    base_version = _parse_version_from_text(base_skill)
                    if base_version and base_version != upstream_version:
                        errors.append(
                            f"{skill_name}: upstream_commit version "
                            f"{base_version} != upstream version {upstream_version}"
                        )
    elif require_commit:
        errors.append(
            f"{skill_name}: missing metadata.upstream_commit "
            "(required for new variants)"
        )

    local_changes = fm.metadata.get("local_changes", "")
    if not local_changes:
        errors.append(f"{skill_name}: missing metadata.local_changes")

    version = fm.metadata.get("version", "")
    if not version:
        errors.append(f"{skill_name}: missing metadata.version")
    elif upstream:
        expected_base = upstream.split("@")[1]
        m = re.match(
            rf"^{re.escape(expected_base)}\+{re.escape(variant)}\.(\d+)$", version
        )
        if not m:
            errors.append(
                f"{skill_name}: metadata.version '{version}' does not match "
                f"upstream base '{expected_base}' + variant suffix"
            )
        else:
            counter = int(m.group(1))
            if counter < 1:
                errors.append(
                    f"{skill_name}: metadata.version suffix counter must be >= 1"
                )

    # Drift check: if we have upstream_commit, compare variant to base tree.
    if upstream_commit and git_cat_file_exists(upstream_commit, canonical_repo):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir) / "base"
            base_dir.mkdir()
            if extract_tree_at_commit(
                canonical_repo, upstream_commit, f"skills/{upstream_name}/", base_dir
            ):
                base_skill_dir = base_dir / "skills" / upstream_name
                if not base_skill_dir.exists():
                    base_skill_dir = base_dir / upstream_name
                diffs = diff_dirs(base_skill_dir, variant_dir)
                if not diffs and local_changes:
                    warnings.append(
                        f"{skill_name}: variant has no differences from base "
                        "but local_changes is non-empty"
                    )
                elif diffs and not local_changes:
                    errors.append(
                        f"{skill_name}: variant has differences from base "
                        f"but no local_changes: {', '.join(diffs)}"
                    )
            else:
                warnings.append(
                    f"{skill_name}: could not extract base tree for drift check"
                )

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    return errors


def validate_bump(skill_name: str, base_rev: str, repo: Path) -> list[str]:
    errors: list[str] = []

    # Get current version from the base revision.
    base_skill = git_show(f"skills/{skill_name}/SKILL.md", base_rev, repo)
    if not base_skill:
        errors.append(f"Skill {skill_name} not found at {base_rev}")
        return errors
    base_version = _parse_version_from_text(base_skill)
    if not base_version:
        errors.append(
            f"Could not parse base version for {skill_name} at {base_rev}"
        )
        return errors

    # Get working-tree version.
    skill_dir = repo / "skills" / skill_name
    if not skill_dir.exists():
        errors.append(f"Skill directory {skill_name} not found in working tree")
        return errors
    fm = parse_frontmatter(skill_dir / "SKILL.md")
    work_version = fm.metadata.get("version", "")
    if not work_version:
        errors.append(f"Working tree {skill_name} has no metadata.version")
        return errors

    # Strict semver increase check.
    def parse_semver(v: str) -> tuple[int, int, int]:
        m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", v)
        if not m:
            raise ValueError(f"Invalid semver: {v}")
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    try:
        bv = parse_semver(base_version)
        wv = parse_semver(work_version)
    except ValueError as e:
        errors.append(str(e))
        return errors

    is_increase = wv > bv
    if not is_increase:
        errors.append(
            f"Version {work_version} is not a strict increase over base {base_version}"
        )

    # Check changelog entry under [Unreleased].
    changelog = repo / "CHANGELOG.md"
    if changelog.exists():
        cl_text = changelog.read_text(encoding="utf-8")
        in_unreleased = False
        found = False
        for line in cl_text.splitlines():
            if line.startswith("## [Unreleased]"):
                in_unreleased = True
                continue
            if line.startswith("## [") and in_unreleased:
                in_unreleased = False
            if in_unreleased:
                m = re.match(
                    rf"^-\s+\*\*{re.escape(skill_name)}:\*\s*"
                    r".*\((\d+\.\d+\.\d+)\)\s*$",
                    line,
                )
                if m and m.group(1) == work_version:
                    found = True
                    break
        if not found:
            errors.append(
                f"No matching changelog entry under [Unreleased] "
                f"for {skill_name}@{work_version}"
            )

    # Check for unstaged changes to unrelated files.
    res = run_git(["status", "--porcelain"], cwd=repo)
    if res.returncode == 0:
        for line in res.stdout.splitlines():
            if not line:
                continue
            path = line[3:].strip()
            allowed = (
                path.startswith(f"skills/{skill_name}/")
                or path == "CHANGELOG.md"
                or path == "README.md"
                or path == ".github/workflows/skills.yml"
            )
            if not allowed:
                errors.append(f"Unstaged changes to unrelated file: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill metadata validator")
    parser.add_argument(
        "--repo", type=Path, help="Path to canonical repo (default: .)"
    )
    parser.add_argument(
        "--variant", type=Path, help="Path to project variant skill directory"
    )
    parser.add_argument(
        "--canonical", type=Path, help="Path to canonical repo for variant validation"
    )
    parser.add_argument(
        "--check-bump", type=str, help="Skill name to check version bump"
    )
    parser.add_argument(
        "--base",
        type=str,
        default="origin/master",
        help="Base revision for bump check (default: origin/master)",
    )
    parser.add_argument(
        "--require-commit",
        action="store_true",
        help="Require upstream_commit for variants",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    args = parser.parse_args()

    repo = args.repo or Path(".").resolve()

    all_errors: list[str] = []

    if args.check_bump:
        all_errors.extend(validate_bump(args.check_bump, args.base, repo))
    elif args.variant:
        if not args.canonical:
            print("Error: --canonical required with --variant", file=sys.stderr)
            return 2
        all_errors.extend(
            validate_variant(args.variant, args.canonical, args.require_commit)
        )
    else:
        all_errors.extend(validate_canonical_repo(repo, args.strict))

    if all_errors:
        for e in all_errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
