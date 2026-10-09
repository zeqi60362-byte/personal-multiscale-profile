#!/usr/bin/env python3
"""Minimal dependency-free structural validation for this Codex skill."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MAX_SKILL_NAME_LENGTH = 64
ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}


def parse_simple_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    if not text.startswith("---\n"):
        return None, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format"

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None, f"Unsupported frontmatter line: {line!r}"
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in frontmatter:
            return None, f"Duplicate frontmatter key: {key}"
        frontmatter[key] = value
    return frontmatter, text[match.end() :]


def has_unfinished_todo(body: str) -> bool:
    fence_marker: str | None = None
    fence_length = 0
    for line in body.splitlines():
        fence = re.match(
            r"^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$",
            line,
        )
        if fence:
            marker = fence.group(1)
            if fence_marker is None:
                fence_marker = marker[0]
                fence_length = len(marker)
            elif (
                marker[0] == fence_marker
                and len(marker) >= fence_length
                and not fence.group(2).strip()
            ):
                fence_marker = None
                fence_length = 0
            continue
        if fence_marker is None and re.fullmatch(
            r"[ ]{0,3}\[TODO:[^\n]*\][ \t]*",
            line,
        ):
            return True
    return False


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md not found"]

    frontmatter, body_or_error = parse_simple_frontmatter(
        skill_md.read_text(encoding="utf-8")
    )
    if frontmatter is None:
        return [body_or_error]

    unexpected = set(frontmatter) - ALLOWED_PROPERTIES
    if unexpected:
        errors.append(
            "Unexpected frontmatter keys: "
            + ", ".join(sorted(unexpected))
            + ". Allowed: "
            + ", ".join(sorted(ALLOWED_PROPERTIES))
        )

    name = frontmatter.get("name", "").strip()
    if not name:
        errors.append("Missing name in frontmatter")
    else:
        if not re.fullmatch(r"[a-z0-9-]+", name):
            errors.append("Name must use lowercase letters, digits, and hyphens")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append("Name cannot start/end with hyphen or contain consecutive hyphens")
        if len(name) > MAX_SKILL_NAME_LENGTH:
            errors.append(f"Name exceeds {MAX_SKILL_NAME_LENGTH} characters")

    description = frontmatter.get("description", "").strip()
    if not description:
        errors.append("Missing description in frontmatter")
    else:
        if description.startswith("[TODO:"):
            errors.append("Description contains an unfinished TODO placeholder")
        if "<" in description or ">" in description:
            errors.append("Description cannot contain angle brackets")
        if len(description) > 1024:
            errors.append("Description exceeds 1024 characters")

    if has_unfinished_todo(body_or_error):
        errors.append("Skill instructions contain an unfinished TODO placeholder")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skill directory to validate",
    )
    args = parser.parse_args()

    errors = validate_skill(args.skill_dir.resolve())
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Skill structure is valid: {args.skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
