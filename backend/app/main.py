"""FastAPI application factory with middleware, routers, and lifespan."""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from collections import defaultdict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_database_connection

# In-memory sliding window rate limiter (per IP, 60 req/min)
# For multi-process deployments replace with Redis INCR + EXPIRE
_rate_buckets: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 60
RATE_LIMIT_WINDOW = 60.0  # seconds

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    logger.info(f"Starting PlotIQ backend v{settings.app_version} [{settings.app_env}]")

    # Check DB connectivity at startup
    db_status = await check_database_connection()
    for dep, status_val in db_status.items():
        if status_val not in ("ok",):
            logger.error(f"Startup check FAILED: {dep} = {status_val}")
        else:
            logger.info(f"Startup check OK: {dep}")

    # Load or train price model
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        from ai.price_model.train import load_or_train
        await asyncio.to_thread(load_or_train)
    except Exception as exc:
        logger.warning(f"Price model startup load skipped: {exc}")

    yield

    logger.info("Shutting down PlotIQ backend")


def create_app() -> FastAPI:
    app = FastAPI(
        title="PlotIQ API",
        description="AI-powered land discovery and verification platform",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Per-IP rate limiting middleware (60 req/min)
    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = _rate_buckets[client_ip]
        # Drop timestamps outside the window
        _rate_buckets[client_ip] = [t for t in window if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_buckets[client_ip]) >= RATE_LIMIT_MAX:
            retry_after = int(RATE_LIMIT_WINDOW - (now - _rate_buckets[client_ip][0]))
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(max(retry_after, 1))},
                content={"error": {"code": "RATE_LIMIT_EXCEEDED", "message": f"Max {RATE_LIMIT_MAX} requests per minute"}},
            )
        _rate_buckets[client_ip].append(now)
        return await call_next(request)

    # Structured request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            '{"method": "%s", "path": "%s", "status": %d, "response_time_ms": %s}',
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                    "details": [],
                }
            },
        )

    # Health endpoint
    @app.get("/health", tags=["system"])
    async def health_check():
        db_status = await check_database_connection()
        
        # Check Redis
        redis_status = "ok"
        try:
            import redis as redis_sync
            r = redis_sync.from_url(settings.redis_url, socket_connect_timeout=2)
            r.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            redis_status = "unavailable"

        all_deps = {**db_status, "redis": redis_status}
        overall_ok = all(v == "ok" for v in all_deps.values())
        
        return JSONResponse(
            status_code=200 if overall_ok else 503,
            content={
                "status": "ok" if overall_ok else "degraded",
                "version": settings.app_version,
                "dependencies": all_deps,
            },
        )

    # Register routers
    from app.api import search, listings, documents, admin, webhooks

    app.include_router(search.router, prefix="/api/v1", tags=["search"])
    app.include_router(listings.router, prefix="/api/v1", tags=["listings"])
    app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
    app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
    app.include_router(webhooks.router, prefix="/api/v1", tags=["webhooks"])

    return app


app = create_app()
