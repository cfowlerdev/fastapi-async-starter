import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings, fastapi_config

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # Startup
    logger.info("*** Server starting UP ***")
    yield

    # Shutdown
    logger.info("*** Server shutting DOWN ***")


app = FastAPI(**fastapi_config, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

