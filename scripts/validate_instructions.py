#!/usr/bin/env python3
"""Validate .github/copilot-instructions.md and agent instruction files."""

import re
import sys
from pathlib import Path
from typing import Optional

REQUIRED_SECTIONS = [
    "## Overview",
    "## Guidelines",
]

MAX_LINE_LENGTH = 120
MIN_FILE_LENGTH = 10  # lines
MAX_FILE_LENGTH = 500  # lines


def load_instruction_file(path: Path) -> list[str]:
    """Load an instruction markdown file and return its lines."""
    if not path.exists():
        raise FileNotFoundError(f"Instruction file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return f.readlines()


def validate_instruction_file(path: Path) -> list[str]:
    """Validate a single instruction file. Returns list of error messages."""
    errors: list[str] = []

    try:
        lines = load_instruction_file(path)
    except FileNotFoundError as e:
        return [str(e)]

    if len(lines) < MIN_FILE_LENGTH:
        errors.append(f"{path}: file too short ({len(lines)} lines, min {MIN_FILE_LENGTH})")

    if len(lines) > MAX_FILE_LENGTH:
        errors.append(f"{path}: file too long ({len(lines)} lines, max {MAX_FILE_LENGTH})")

    content = "".join(lines)

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"{path}: missing required section '{section}'")

    for i, line in enumerate(lines, start=1):
        stripped = line.rstrip("\n")
        if len(stripped) > MAX_LINE_LENGTH:
            errors.append(
                f"{path}:{i}: line exceeds {MAX_LINE_LENGTH} characters ({len(stripped)})"
            )

    if not content.endswith("\n"):
        errors.append(f"{path}: file must end with a newline")

    return errors


def find_instruction_files(root: Path) -> list[Path]:
    """Find all instruction markdown files in the project."""
    files = []
    main_instructions = root / ".github" / "copilot-instructions.md"
    if main_instructions.exists():
        files.append(main_instructions)
    agents_dir = root / ".github" / "agents"
    if agents_dir.exists():
        files.extend(sorted(agents_dir.glob("*.md")))
    return files


def validate_all(root: Optional[Path] = None) -> dict[str, list[str]]:
    """Validate all instruction files. Returns dict of path -> errors."""
    if root is None:
        root = Path(".")
    results: dict[str, list[str]] = {}
    for path in find_instruction_files(root):
        errors = validate_instruction_file(path)
        results[str(path)] = errors
    return results


def main() -> int:
    root = Path(".")
    results = validate_all(root)
    total_errors = 0
    for path, errors in results.items():
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
            total_errors += 1
    if total_errors == 0:
        print(f"All {len(results)} instruction file(s) passed validation.")
        return 0
    print(f"\n{total_errors} error(s) found in {len(results)} file(s).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
