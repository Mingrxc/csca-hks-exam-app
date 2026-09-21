"""Application factory."""

import logging
from time import perf_counter

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request

from src.api.v1 import api_router
from src.common.exceptions import (
    AppException,
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from src.common.request_context import (
    REQUEST_ID_HEADER,
    normalize_request_id,
    reset_request_id,
    set_request_id,
)


logger = logging.getLogger("app.requests")


def create_app() -> FastAPI:
    from src.config.settings import settings

    app = FastAPI(
        title="留学考霸 API",
        description="CSCA & HKS 备考刷题小程序后端服务",
        version="1.0.0",
    )

    cors_origins = settings.cors_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials="*" not in cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = normalize_request_id(request.headers.get(REQUEST_ID_HEADER))
        token = set_request_id(request_id)
        started_at = perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception as exc:
                response = await general_exception_handler(request, exc)
            response.headers[REQUEST_ID_HEADER] = request_id
            elapsed_ms = round((perf_counter() - started_at) * 1000, 2)
            logger.info(
                "%s %s status=%s duration_ms=%s request_id=%s",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
                request_id,
            )
            return response
        finally:
            reset_request_id(token)

    app.include_router(api_router)

    @app.get("/api/v1/health")
    def health_check():
        return {
            "status": "ok",
            "service": "csca-hks-exam-app",
            "version": app.version,
        }

    return app
