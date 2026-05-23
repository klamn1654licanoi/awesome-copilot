"""Tests for scripts/validate_contributors.py"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_contributors import (
    validate_contributor,
    validate_all,
    load_contributorsrc,
    REQUIRED_FIELDS,
)


VALID_CONTRIBUTOR = {
    "login": "octocat",
    "name": "The Octocat",
    "avatar_url": "https://avatars.githubusercontent.com/octocat",
    "profile": "https://github.com/octocat",
    "contributions": ["code", "doc"],
}


def test_valid_contributor_has_no_errors():
    errors = validate_contributor(VALID_CONTRIBUTOR, 0)
    assert errors == []


def test_missing_required_field():
    contributor = {k: v for k, v in VALID_CONTRIBUTOR.items() if k != "name"}
    errors = validate_contributor(contributor, 0)
    assert any("name" in e for e in errors)


def test_empty_contributions_raises_error():
    contributor = {**VALID_CONTRIBUTOR, "contributions": []}
    errors = validate_contributor(contributor, 0)
    assert any("contributions" in e for e in errors)


def test_invalid_contribution_type():
    contributor = {**VALID_CONTRIBUTOR, "contributions": ["code", "unicorn"]}
    errors = validate_contributor(contributor, 0)
    assert any("unicorn" in e for e in errors)


def test_invalid_profile_url():
    contributor = {**VALID_CONTRIBUTOR, "profile": "not-a-url"}
    errors = validate_contributor(contributor, 0)
    assert any("profile" in e for e in errors)


def test_duplicate_logins_detected():
    data = {
        "contributors": [
            VALID_CONTRIBUTOR,
            {**VALID_CONTRIBUTOR, "name": "Octocat Clone"},
        ]
    }
    errors = validate_all(data)
    assert any("Duplicate" in e and "octocat" in e for e in errors)


def test_validate_all_passes_with_valid_data():
    data = {"contributors": [VALID_CONTRIBUTOR]}
    errors = validate_all(data)
    assert errors == []


def test_load_contributorsrc(tmp_path):
    sample = {"contributors": [VALID_CONTRIBUTOR]}
    rc_file = tmp_path / ".all-contributorsrc"
    rc_file.write_text(json.dumps(sample), encoding="utf-8")
    result = load_contributorsrc(rc_file)
    assert result == sample


def test_all_required_fields_defined():
    assert "login" in REQUIRED_FIELDS
    assert "contributions" in REQUIRED_FIELDS
