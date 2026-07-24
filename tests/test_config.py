"""Tests for API v2 client configuration."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from nsgifts_api import ClientConfig


def _config() -> ClientConfig:
    """Build a valid explicit configuration."""
    return ClientConfig(
        user_id=1234,
        login="partner-login",
        password="plain-password-value",
        api_secret="c2VjcmV0LWtleQ==",
    )


def test_config_masks_secret_values() -> None:
    """Verify that repr does not reveal credentials."""
    rendered = repr(_config())
    assert "plain-password-value" not in rendered
    assert "c2VjcmV0LWtleQ==" not in rendered


def test_safe_dict_excludes_secret_fields() -> None:
    """Verify that safe serialization omits all credentials."""
    data = _config().to_safe_dict()
    assert data["user_id"] == 1234
    assert data["login"] == "partner-login"
    assert "password" not in data
    assert "api_secret" not in data


def test_base_url_is_normalized_without_trailing_slash() -> None:
    """Verify URL normalization used to concatenate endpoint paths."""
    config = _config()
    assert config.normalized_base_url == "https://api.ns.gifts"


def test_non_https_base_url_is_rejected() -> None:
    """Verify that production credentials cannot use clear-text HTTP."""
    with pytest.raises(ValidationError):
        ClientConfig(
            user_id=1234,
            login="partner-login",
            password="plain-password-value",
            api_secret="c2VjcmV0LWtleQ==",
            base_url="http://api.ns.gifts",
        )


def test_from_env_reads_prefixed_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify safe configuration loading from environment variables."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NSGIFTS_USER_ID", "321")
    monkeypatch.setenv("NSGIFTS_LOGIN", "environment-login")
    monkeypatch.setenv("NSGIFTS_PASSWORD", "environment-password")
    monkeypatch.setenv(
        "NSGIFTS_API_SECRET",
        "ZW52aXJvbm1lbnQtc2VjcmV0",
    )

    config = ClientConfig.from_env(env_file=None)

    assert config.user_id == 321
    assert config.login == "environment-login"
    assert config.password.get_secret_value() == ("environment-password")
