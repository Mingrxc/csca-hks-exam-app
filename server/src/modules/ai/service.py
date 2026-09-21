"""AI 问答业务逻辑."""

from __future__ import annotations

from textwrap import dedent

import httpx

from src.common.exceptions import AppException
from src.config.settings import settings
from src.modules.ai.schemas import AIChatRequest


def build_system_prompt(payload: AIChatRequest) -> str:
    base = dedent(
        """
        你是 DYH 留学备考 AI 助手，主要服务准备 CSCA 和 HSK 的留学生。
        你的回答要：
        1. 优先使用简洁、准确、可执行的中文。
        2. 题目讲解要先给结论，再给依据，再给记忆技巧。
        3. 留学咨询要区分已确认信息和不确定信息，不要编造政策、院校或签证结论。
        4. 如果用户给出题目、选项、知识点或错题上下文，要围绕这些内容直接给建议。
        5. 可以适度鼓励，但不要空话太多。
        """
    ).strip()
    extras = []
    if payload.exam_type:
        extras.append(f"当前考试类型：{payload.exam_type}")
    if payload.topic:
        extras.append(f"当前主题：{payload.topic}")
    if payload.question:
        extras.append(f"题目上下文：{payload.question}")
    if payload.context:
        extras.append(f"补充上下文：{payload.context}")
    if extras:
        base = base + "\n\n" + "\n".join(extras)
    return base


async def chat_with_qwen(payload: AIChatRequest) -> dict:
    if not settings.QWEN_API_KEY:
        return {
            "reply": "AI 服务暂未配置密钥。你可以先把题目、选项和你的困惑发给我，我会按接入后的格式继续整理。",  # pragma: no cover
            "model": settings.QWEN_MODEL,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    messages = [{"role": "system", "content": build_system_prompt(payload)}]
    messages.extend(
        {"role": message.role, "content": message.content}
        for message in payload.messages[-12:]
    )

    try:
        async with httpx.AsyncClient(timeout=settings.QWEN_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{settings.QWEN_BASE_URL.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.QWEN_MODEL,
                    "messages": messages,
                    "temperature": settings.QWEN_TEMPERATURE,
                    "max_tokens": settings.QWEN_MAX_TOKENS,
                },
            )
    except httpx.TimeoutException as exc:
        raise AppException(50451, "AI 回复超时，请稍后重试", status_code=504) from exc
    except httpx.RequestError as exc:
        raise AppException(50255, "AI 服务暂时不可用，请稍后重试", status_code=502) from exc

    try:
        payload_data = response.json()
    except ValueError as exc:
        raise AppException(50251, "AI 服务返回了无法解析的结果", status_code=502) from exc

    if response.status_code >= 400:
        message = (
            payload_data.get("error", {}).get("message")
            or payload_data.get("message")
            or "AI 服务请求失败"
        )
        raise AppException(50252, message, status_code=response.status_code)

    choices = payload_data.get("choices") or []
    if not choices:
        raise AppException(50253, "AI 服务未返回可用回复", status_code=502)
    reply = choices[0].get("message", {}).get("content", "").strip()
    if not reply:
        raise AppException(50254, "AI 服务返回了空回复", status_code=502)

    usage = payload_data.get("usage") or {}
    return {
        "reply": reply,
        "model": payload_data.get("model") or settings.QWEN_MODEL,
        "usage": {
            "prompt_tokens": int(usage.get("prompt_tokens") or 0),
            "completion_tokens": int(usage.get("completion_tokens") or 0),
            "total_tokens": int(usage.get("total_tokens") or 0),
        },
    }
