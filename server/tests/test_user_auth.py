import httpx
import pytest
from fastapi import HTTPException

from src.common.auth import create_token, decode_token
from src.modules.user import service


@pytest.mark.asyncio
async def test_exchange_wx_code_uses_explicit_dev_user_without_credentials(monkeypatch):
    monkeypatch.setattr(service.settings, "WX_APPID", "")
    monkeypatch.setattr(service.settings, "WX_SECRET", "")
    monkeypatch.setattr(service.settings, "AUTH_ALLOW_DEV_OPENID", True)
    monkeypatch.setattr(service.settings, "DEV_OPENID", "local-user")

    assert await service.exchange_wx_code("temporary-code") == "local-user"


@pytest.mark.asyncio
async def test_exchange_wx_code_requires_configuration_in_production(monkeypatch):
    monkeypatch.setattr(service.settings, "WX_APPID", "")
    monkeypatch.setattr(service.settings, "WX_SECRET", "")
    monkeypatch.setattr(service.settings, "AUTH_ALLOW_DEV_OPENID", False)

    with pytest.raises(service.AppException) as exc_info:
        await service.exchange_wx_code("temporary-code")

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_exchange_wx_code_returns_openid_from_wechat(monkeypatch):
    monkeypatch.setattr(service.settings, "WX_APPID", "test-appid")
    monkeypatch.setattr(service.settings, "WX_SECRET", "test-secret")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["appid"] == "test-appid"
        assert request.url.params["js_code"] == "valid-code"
        return httpx.Response(200, json={"openid": "wx-openid", "session_key": "hidden"})

    openid = await service.exchange_wx_code(
        "valid-code",
        transport=httpx.MockTransport(handler),
    )

    assert openid == "wx-openid"


@pytest.mark.asyncio
async def test_exchange_wx_code_rejects_wechat_error(monkeypatch):
    monkeypatch.setattr(service.settings, "WX_APPID", "test-appid")
    monkeypatch.setattr(service.settings, "WX_SECRET", "test-secret")
    monkeypatch.setattr(service.settings, "AUTH_ALLOW_DEV_OPENID", False)
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"errcode": 40029, "errmsg": "invalid code"})
    )

    with pytest.raises(service.AppException) as exc_info:
        await service.exchange_wx_code("expired-code", transport=transport)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_exchange_wx_code_falls_back_after_wechat_error_in_dev(monkeypatch):
    monkeypatch.setattr(service.settings, "WX_APPID", "test-appid")
    monkeypatch.setattr(service.settings, "WX_SECRET", "test-secret")
    monkeypatch.setattr(service.settings, "AUTH_ALLOW_DEV_OPENID", True)
    monkeypatch.setattr(service.settings, "DEV_OPENID", "local-user")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"errcode": 40029, "errmsg": "invalid code"})
    )

    assert await service.exchange_wx_code("tourist-code", transport=transport) == "local-user"


def test_jwt_uses_configured_secret_and_contains_subject(monkeypatch):
    monkeypatch.setattr(service.settings, "JWT_SECRET_KEY", "test-secret-at-least-32-characters")
    monkeypatch.setattr(service.settings, "JWT_EXPIRE_HOURS", 1)

    token = create_token("jwt-user")

    assert decode_token(token) == "jwt-user"


def test_jwt_rejects_token_after_secret_changes(monkeypatch):
    monkeypatch.setattr(service.settings, "JWT_SECRET_KEY", "first-secret-at-least-32-characters")
    token = create_token("jwt-user")
    monkeypatch.setattr(service.settings, "JWT_SECRET_KEY", "second-secret-at-least-32-characters")

    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == 401
