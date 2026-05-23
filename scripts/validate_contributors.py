#!/usr/bin/env python3
"""Validate .all-contributorsrc entries for consistency and required fields."""

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {"login", "name", "avatar_url", "profile", "contributions"}
VALID_CONTRIBUTION_TYPES = {
    "code", "doc", "design", "ideas", "bug", "review",
    "test", "infra", "translation", "maintenance", "question",
    "security", "content", "data", "example", "eventOrganizing",
    "financial", "fundingFinding", "mentoring", "plugin", "projectManagement",
    "research", "talk", "tutorial", "userTesting", "video",
}


def load_contributorsrc(path: Path) -> dict[str, Any]:
    """Load and parse the .all-contributorsrc file."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_contributor(contributor: dict[str, Any], index: int) -> list[str]:
    """Validate a single contributor entry. Returns list of error messages."""
    errors: list[str] = []
    login = contributor.get("login", f"<unknown at index {index}>")

    missing = REQUIRED_FIELDS - set(contributor.keys())
    for field in sorted(missing):
        errors.append(f"[{login}] Missing required field: '{field}'")

    contributions = contributor.get("contributions", [])
    if not isinstance(contributions, list) or len(contributions) == 0:
        errors.append(f"[{login}] 'contributions' must be a non-empty list")
    else:
        for contrib in contributions:
            if contrib not in VALID_CONTRIBUTION_TYPES:
                errors.append(f"[{login}] Unknown contribution type: '{contrib}'")

    profile = contributor.get("profile", "")
    if profile and not profile.startswith("http"):
        errors.append(f"[{login}] 'profile' should be a valid URL, got: '{profile}'")

    return errors


def validate_all(data: dict[str, Any]) -> list[str]:
    """Validate all contributors in the data."""
    all_errors: list[str] = []
    contributors = data.get("contributors", [])

    logins = [c.get("login") for c in contributors if c.get("login")]
    duplicates = {l for l in logins if logins.count(l) > 1}
    for dup in sorted(duplicates):
        all_errors.append(f"Duplicate contributor login: '{dup}'")

    for i, contributor in enumerate(contributors):
        all_errors.extend(validate_contributor(contributor, i))

    return all_errors


def main() -> int:
    rc_path = Path(".all-contributorsrc")
    if not rc_path.exists():
        print(f"ERROR: {rc_path} not found.", file=sys.stderr)
        return 1

    data = load_contributorsrc(rc_path)
    errors = validate_all(data)

    if errors:
        print(f"Found {len(errors)} validation error(s):\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    contributor_count = len(data.get("contributors", []))
    print(f"✓ Validation passed. {contributor_count} contributors are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
