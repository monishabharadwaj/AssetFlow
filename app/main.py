import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import get_db
from app.core.health_checks import readiness_report
from app.exceptions.handlers import register_exception_handlers
from app.middleware.request_logging import RequestLoggingMiddleware
from app.services.scheduler_service import lifespan_scheduler

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with lifespan_scheduler(app):
        yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=app_lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/ready")
def readiness_check(db: Session = Depends(get_db)) -> JSONResponse:
    report = readiness_report(db)
    status_code = 200 if report["status"] == "ready" else 503
    return JSONResponse(status_code=status_code, content=report)
