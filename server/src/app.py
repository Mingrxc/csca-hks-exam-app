"""Application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import api_router
from src.common.exceptions import AppException, app_exception_handler, general_exception_handler


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
    app.add_exception_handler(Exception, general_exception_handler)

    app.include_router(api_router)

    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "ok", "service": "csca-hks-exam-app"}

    return app
