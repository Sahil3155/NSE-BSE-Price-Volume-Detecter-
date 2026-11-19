"""FastAPI application entrypoint for the market surveillance backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.api.routes import (
    health,
    stocks,
    market_data,
    detection,
    alerts,
    analytics,
    model_management,
)


def register_api_routers(app: FastAPI) -> None:
    """Register all API routers under the API V1 prefix."""
    prefix = settings.API_V1_PREFIX
    app.include_router(health.router, prefix=prefix)
    app.include_router(stocks.router, prefix=prefix)
    app.include_router(market_data.router, prefix=prefix)
    app.include_router(detection.router, prefix=prefix)
    app.include_router(alerts.router, prefix=prefix)
    app.include_router(analytics.router, prefix=prefix)
    app.include_router(model_management.router, prefix=prefix)


def create_application() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    logger.info(f"Initializing {settings.APP_NAME} in {settings.ENVIRONMENT} mode.")
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-powered surveillance system for detecting suspicious "
            "price and volume movements in small-cap NSE/BSE stocks."
        ),
        version="1.0.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_api_routers(app)
    return app


app = create_application()
