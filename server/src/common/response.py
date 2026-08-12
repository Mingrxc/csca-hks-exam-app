"""统一响应格式"""

from typing import Any, Optional


def success(data: Any = None, message: str = "成功") -> dict:
    return {"code": 0, "message": message, "data": data}


def fail(code: int = -1, message: str = "失败", data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}
