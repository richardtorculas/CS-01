from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict = {}


class ErrorResponse(BaseModel):
    """Documents the single error shape from API.md in the OpenAPI spec."""

    error: ErrorBody
