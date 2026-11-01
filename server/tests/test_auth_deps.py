import pytest
from fastapi import HTTPException

from src.common import deps


def test_missing_authorization_fails_even_with_dev_openid_enabled(monkeypatch):
    monkeypatch.setattr(deps.settings, "AUTH_ALLOW_DEV_OPENID", True)
    monkeypatch.setattr(deps.settings, "DEV_OPENID", "test-dev-openid")

    with pytest.raises(HTTPException) as exc_info:
        deps.get_current_openid(None)
    assert exc_info.value.status_code == 401


def test_missing_authorization_fails_when_dev_openid_disabled(monkeypatch):
    monkeypatch.setattr(deps.settings, "AUTH_ALLOW_DEV_OPENID", False)

    with pytest.raises(HTTPException) as exc_info:
        deps.get_current_openid(None)

    assert exc_info.value.status_code == 401
