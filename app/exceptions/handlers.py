from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.exceptions.errors import BusinessRuleError, ConflictError, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(BusinessRuleError)
    async def business_rule_handler(_request: Request, exc: BusinessRuleError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_request: Request, exc: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "A database constraint was violated"},
        )
