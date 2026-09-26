from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core import exceptions as exc

# The one place domain errors become HTTP statuses (API.md "Errors").
_STATUS_BY_ERROR: dict[type[exc.DomainError], int] = {
    exc.EmailAlreadyRegisteredError: 409,
    exc.MobileAlreadyRegisteredError: 409,
    exc.BarangayNotFoundError: 422,
    exc.InvalidCredentialsError: 401,
    exc.AuthenticationRequiredError: 401,
    exc.InvalidVerificationTokenError: 400,
    exc.EmailNotVerifiedError: 403,
}


def _error_body(code: str, message: str, details: object = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def _domain_error_response(_: Request, error: exc.DomainError) -> JSONResponse:
    status = _STATUS_BY_ERROR.get(type(error), 400)
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return JSONResponse(_error_body(error.code, error.message), status, headers=headers)


def _validation_error_response(_: Request, error: RequestValidationError) -> JSONResponse:
    # Only loc/msg/type: pydantic's "input" would echo submitted passwords back to the client.
    fields = [
        {
            "field": ".".join(str(part) for part in e["loc"][1:]),
            "message": e["msg"],
            "type": e["type"],
        }
        for e in error.errors()
    ]
    body = _error_body("VALIDATION_ERROR", "The request is invalid.", {"fields": fields})
    return JSONResponse(body, 422)


def _http_error_response(_: Request, error: StarletteHTTPException) -> JSONResponse:
    code = "NOT_FOUND" if error.status_code == 404 else "HTTP_ERROR"
    return JSONResponse(_error_body(code, str(error.detail)), error.status_code)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(exc.DomainError, _domain_error_response)
    app.add_exception_handler(RequestValidationError, _validation_error_response)
    app.add_exception_handler(StarletteHTTPException, _http_error_response)
