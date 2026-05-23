"""Tests for scripts/validate_instructions.py"""

import textwrap
from pathlib import Path

import pytest

from scripts.validate_instructions import (
    validate_instruction_file,
    find_instruction_files,
    validate_all,
    REQUIRED_SECTIONS,
    MAX_LINE_LENGTH,
)


def write_file(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


VALID_CONTENT = textwrap.dedent("""\
    # Copilot Instructions

    ## Overview

    This file describes how Copilot should behave.

    ## Guidelines

    - Be helpful
    - Be concise
    - Follow project conventions
""")


def test_valid_file_has_no_errors(tmp_path):
    p = write_file(tmp_path, "copilot-instructions.md", VALID_CONTENT)
    errors = validate_instruction_file(p)
    assert errors == []


def test_missing_overview_section(tmp_path):
    content = VALID_CONTENT.replace("## Overview", "## Summary")
    p = write_file(tmp_path, "instructions.md", content)
    errors = validate_instruction_file(p)
    assert any("Overview" in e for e in errors)


def test_missing_guidelines_section(tmp_path):
    content = VALID_CONTENT.replace("## Guidelines", "## Rules")
    p = write_file(tmp_path, "instructions.md", content)
    errors = validate_instruction_file(p)
    assert any("Guidelines" in e for e in errors)


def test_file_too_short(tmp_path):
    content = "# Title\n\nShort file.\n"
    p = write_file(tmp_path, "instructions.md", content)
    errors = validate_instruction_file(p)
    assert any("too short" in e for e in errors)


def test_line_too_long(tmp_path):
    long_line = "x" * (MAX_LINE_LENGTH + 1)
    content = VALID_CONTENT + long_line + "\n"
    p = write_file(tmp_path, "instructions.md", content)
    errors = validate_instruction_file(p)
    assert any("exceeds" in e for e in errors)


def test_missing_trailing_newline(tmp_path):
    content = VALID_CONTENT.rstrip("\n")
    p = write_file(tmp_path, "instructions.md", content)
    errors = validate_instruction_file(p)
    assert any("newline" in e for e in errors)


def test_file_not_found(tmp_path):
    p = tmp_path / "nonexistent.md"
    errors = validate_instruction_file(p)
    assert any("not found" in e for e in errors)


def test_find_instruction_files(tmp_path):
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    agents_dir = github_dir / "agents"
    agents_dir.mkdir()
    (github_dir / "copilot-instructions.md").write_text(VALID_CONTENT)
    (agents_dir / "my-agent.md").write_text(VALID_CONTENT)
    files = find_instruction_files(tmp_path)
    paths = [str(f) for f in files]
    assert any("copilot-instructions.md" in p for p in paths)
    assert any("my-agent.md" in p for p in paths)


def test_validate_all_returns_dict(tmp_path):
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "copilot-instructions.md").write_text(VALID_CONTENT)
    results = validate_all(tmp_path)
    assert isinstance(results, dict)
    assert all(isinstance(v, list) for v in results.values())
