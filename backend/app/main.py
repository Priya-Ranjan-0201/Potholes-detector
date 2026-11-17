"""ScamRoad FastAPI Application Entrypoint."""

import uuid
from collections.abc import Callable

from backend.app.api.health import router as health_router
from backend.app.api.v1.router import api_v1_router
from backend.app.core.config import settings
from backend.app.schemas.health import ErrorDetail, ErrorResponse
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI-Powered Road and Infrastructure Damage Detection and Severity Assessment Backend API",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # CORS Middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Correlation ID & Timing Middleware
    @app.middleware("http")
    async def correlation_id_middleware(
        request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Global Exception Handlers enforcing A6 error envelope
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        error_resp = ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred.",
                details={"exception": str(exc)} if settings.DEBUG else None,
                request_id=request_id,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.model_dump(),
        )

    # Include root /health endpoint directly (for load balancers and docker compose)
    app.include_router(health_router, prefix="", tags=["Health"])

    # Root service descriptor and user-friendly documentation redirects
    @app.get("/", tags=["Root"])
    async def root_index() -> JSONResponse:
        return JSONResponse({
            "service": "AI-Powered Road and Infrastructure Damage Detection and Severity Assessment API",
            "version": settings.VERSION,
            "status": "online",
            "docs_url": f"{settings.API_V1_STR}/docs",
            "health_url": "/api/v1/health",
            "web_app": "http://localhost:3000",
        })

    @app.get("/docs", include_in_schema=False)
    async def docs_redirect() -> RedirectResponse:
        return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

    @app.get("/redoc", include_in_schema=False)
    async def redoc_redirect() -> RedirectResponse:
        return RedirectResponse(url=f"{settings.API_V1_STR}/redoc")

    @app.get("/openapi.json", include_in_schema=False)
    async def openapi_redirect() -> RedirectResponse:
        return RedirectResponse(url=f"{settings.API_V1_STR}/openapi.json")

    # Include versioned API router under /api/v1
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    @app.on_event("startup")
    async def startup_event() -> None:
        from backend.app.api.v1.infer import self_test_obstacle_blocker
        ok = self_test_obstacle_blocker()
        print(f"[AI ENGINE] COCO scene obstacle blocker self-test: {'PASSED' if ok else 'FAILED'}", flush=True)

    return app


app = create_application()
