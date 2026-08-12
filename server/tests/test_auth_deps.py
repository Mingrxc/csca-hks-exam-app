import pytest
from fastapi import HTTPException

from src.common import deps


def test_missing_authorization_uses_explicit_dev_openid_when_enabled(monkeypatch):
    monkeypatch.setattr(deps.settings, "AUTH_ALLOW_DEV_OPENID", True)
    monkeypatch.setattr(deps.settings, "DEV_OPENID", "test-dev-openid")

    assert deps.get_current_openid(None) == "test-dev-openid"


def test_missing_authorization_fails_when_dev_openid_disabled(monkeypatch):
    monkeypatch.setattr(deps.settings, "AUTH_ALLOW_DEV_OPENID", False)

    with pytest.raises(HTTPException) as exc_info:
        deps.get_current_openid(None)

    assert exc_info.value.status_code == 401
