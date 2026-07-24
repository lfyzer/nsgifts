"""Tests for release and user-facing documentation."""

from pathlib import Path

import tomllib

import nsgifts_api

ROOT = Path(__file__).parents[1]


def test_readme_documents_required_v2_workflows() -> None:
    """Verify that security and order workflows are documented."""
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    required = (
        "API v2",
        "NSGIFTS_API_SECRET",
        "IP whitelist",
        "OrderField",
        "totp_code",
        "APIRequestOutcomeUnknownError",
        "Migration from v1",
        "Миграция с v1",
    )
    for value in required:
        assert value in text


def test_changelog_contains_complete_release_sections() -> None:
    """Verify release notes include every agreed change category."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    for heading in (
        "Breaking",
        "Added",
        "Changed",
        "Removed",
        "Security",
        "Migration",
    ):
        assert f"### {heading}" in text


def test_version_is_consistent_across_package_and_metadata() -> None:
    """Verify a single release version is used everywhere."""
    pyproject = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert nsgifts_api.__version__ == "2.0.0"
    assert pyproject["project"]["version"] == "2.0.0"
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [2.0.0] - 2026-07-24" in changelog
