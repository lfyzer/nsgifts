"""Tests for repository and package hygiene."""

import subprocess
from pathlib import Path, PurePosixPath

FORBIDDEN_PARTS = frozenset(
    {
        ".agents",
        ".codex",
        ".codex-plugin",
        ".superpowers",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }
)


def _tracked_paths() -> list[PurePosixPath]:
    """Return paths currently tracked by Git."""
    root = Path(__file__).parents[1]
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "ls-files",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [PurePosixPath(line) for line in result.stdout.splitlines() if line]


def test_tracked_files_do_not_contain_forbidden_paths() -> None:
    """Verify that assistant metadata and caches are not tracked."""
    offenders = [
        path
        for path in _tracked_paths()
        if FORBIDDEN_PARTS.intersection(path.parts)
    ]
    assert offenders == []


def test_real_environment_files_are_not_tracked() -> None:
    """Verify that only the safe environment template may be tracked."""
    offenders = [
        path
        for path in _tracked_paths()
        if path.name.startswith(".env") and path.name != ".env.example"
    ]
    assert offenders == []


def test_environment_template_contains_only_placeholders() -> None:
    """Verify that the environment template has no likely real secret."""
    root = Path(__file__).parents[1]
    content = (root / ".env.example").read_text(encoding="utf-8")
    assert "PASTE-YOUR-BASE64-SECRET" in content
    assert "your_password" in content


def test_pep561_marker_is_packaged() -> None:
    """Expose inline annotations to installed-package type checkers."""
    root = Path(__file__).parents[1]
    marker = root / "nsgifts_api" / "py.typed"
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert marker.is_file()
    assert 'nsgifts_api = ["py.typed"]' in pyproject
