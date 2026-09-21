from fastapi import HTTPException, Query
from fastapi.testclient import TestClient

from src.app import create_app
from src.common.exceptions import AppException
from src.common.response import ApiResponse, success


def build_contract_client(*, raise_server_exceptions: bool = True) -> TestClient:
    app = create_app()

    @app.get("/__test/success")
    def success_route() -> ApiResponse[dict[str, str]]:
        return success({"value": "ok"})

    @app.get("/__test/app-error")
    def app_error_route():
        raise AppException(40901, "conflict", status_code=409)

    @app.get("/__test/http-error")
    def http_error_route():
        raise HTTPException(status_code=401, detail="unauthorized")

    @app.get("/__test/validation")
    def validation_route(limit: int = Query(..., ge=1)):
        return success({"limit": limit})

    @app.get("/__test/unhandled")
    def unhandled_route():
        raise RuntimeError("sensitive internal detail")

    return TestClient(app, raise_server_exceptions=raise_server_exceptions)


def test_success_envelope_and_request_id_are_consistent():
    with build_contract_client() as client:
        response = client.get("/__test/success", headers={"X-Request-ID": "test-request-1"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-1"
    assert response.json() == {
        "code": 0,
        "message": "成功",
        "data": {"value": "ok"},
        "request_id": "test-request-1",
    }


def test_application_and_http_errors_use_the_same_envelope():
    with build_contract_client() as client:
        app_error = client.get("/__test/app-error")
        http_error = client.get("/__test/http-error")

    assert app_error.status_code == 409
    assert app_error.json()["code"] == 40901
    assert app_error.json()["message"] == "conflict"
    assert app_error.json()["request_id"]
    assert http_error.status_code == 401
    assert http_error.json()["code"] == 40100
    assert http_error.json()["message"] == "unauthorized"
    assert http_error.json()["request_id"]


def test_validation_errors_are_normalized_without_echoing_input():
    with build_contract_client() as client:
        response = client.get("/__test/validation", params={"limit": 0})

    payload = response.json()
    assert response.status_code == 422
    assert payload["code"] == 42200
    assert payload["message"] == "请求参数校验失败"
    assert payload["data"]["errors"][0]["field"] == "query.limit"
    assert "input" not in payload["data"]["errors"][0]


def test_unhandled_errors_hide_internal_details():
    with build_contract_client(raise_server_exceptions=False) as client:
        response = client.get("/__test/unhandled")

    payload = response.json()
    assert response.status_code == 500
    assert payload["code"] == 50000
    assert payload["message"] == "服务器内部错误"
    assert "sensitive" not in response.text
    assert payload["request_id"]


def test_openapi_exposes_the_shared_success_envelope():
    with build_contract_client() as client:
        schema = client.get("/openapi.json").json()

    response_schema = schema["paths"]["/__test/success"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert "$ref" in response_schema
