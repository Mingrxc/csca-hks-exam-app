from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import JWTError, jwt

from src.config.settings import settings


def create_token(openid: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {"sub": openid, "exp": expires_at}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        openid = payload.get("sub")
        if not openid:
            raise JWTError("missing subject")
        return openid
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
