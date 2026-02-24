import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config.settings import get_settings
from app.core.errors import add_error_handlers
from app.middleware.logging import LoggingMiddleware
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"] ,
        allow_headers=["*"],
    )

    add_error_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    logging.getLogger(__name__).info("App initialized")
    return app


app = create_app()
