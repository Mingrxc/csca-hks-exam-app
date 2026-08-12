"""JWT 认证中间件"""

from fastapi import Request, HTTPException
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "csca-hks-dev-secret")
ALGORITHM = "HS256"


def create_token(openid: str) -> str:
    """生成 JWT"""
    payload = {"sub": openid}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    """解析 JWT，返回 openid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")


async def get_current_user(request: Request):
    """从请求头中提取用户"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证令牌")
    return decode_token(auth[7:])
