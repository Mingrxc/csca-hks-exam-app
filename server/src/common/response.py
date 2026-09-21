"""Shared API response envelope."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from src.common.request_context import get_request_id


ResponseData = TypeVar("ResponseData")


class ApiResponse(BaseModel, Generic[ResponseData]):
    code: int = 0
    message: str = "成功"
    data: ResponseData
    request_id: str = ""


def success(data: Any = None, message: str = "成功") -> dict[str, Any]:
    return {
        "code": 0,
        "message": message,
        "data": data,
        "request_id": get_request_id(),
    }


def error(code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": get_request_id(),
    }
