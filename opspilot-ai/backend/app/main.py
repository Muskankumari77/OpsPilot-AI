"""
OpsPilot AI — FastAPI application entrypoint.

Phase 1 scope: app wiring, CORS, error handling, logging, and a health
endpoint backed by a real (SQLite) database connection. Domain routers are
added phase by phase in app/api/v1/router.py.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import OpsPilotError, opspilot_exception_handler
from app.core.logging import get_logger, setup_logging
from app.db import base  # noqa: F401  (ensures models are registered on Base.metadata)
from app.db.session import Base, engine

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables that don't exist yet. In later phases this is superseded
    # by Alembic migrations for anything beyond local dev.
    Base.metadata.create_all(bind=engine)
    logger.info("%s starting up in '%s' mode", settings.APP_NAME, settings.APP_ENV)
    yield
    logger.info("%s shutting down", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered business operations and decision intelligence platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(OpsPilotError, opspilot_exception_handler)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {"message": f"{settings.APP_NAME} API — see /docs for the interactive API reference."}
