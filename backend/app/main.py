import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config.settings import get_settings
from app.core.errors import add_error_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityMiddleware
from app.core.logging import setup_logging
from app.memory.short_term.conversation import ConversationMemory


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"] ,
        allow_headers=["*"],
    )

    add_error_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup() -> None:
        try:
            import asyncio
            memory = ConversationMemory(settings)
            # Set a short timeout for MongoDB connection
            await asyncio.wait_for(memory.ensure_indexes(), timeout=5.0)
            logging.getLogger(__name__).info("MongoDB indexes created")
        except asyncio.TimeoutError:
            logging.getLogger(__name__).warning("MongoDB connection timeout. Memory features will be disabled.")
        except Exception as e:
            logging.getLogger(__name__).warning(f"MongoDB not available: {e}. Memory features will be disabled.")

    logging.getLogger(__name__).info("App initialized")
    return app


app = create_app()
