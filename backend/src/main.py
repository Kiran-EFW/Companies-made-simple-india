import logging
import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.config import get_settings
from src.database import init_db
from src.routers import health, pricing, wizard, auth, companies, documents, payments, chatbot, notifications, admin
from src.routers import post_incorporation, compliance
from src.routers import entity_comparison, cap_table
from src.routers import ops
from src.routers import legal_docs
from src.routers import statutory_registers, meetings, data_room
from src.routers import esign
from src.routers import invoices
from src.routers import founder_education
from src.routers import messages
from src.routers import services
from src.routers import accounting
from src.utils.exceptions import APIError
from src.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    PIIMaskingMiddleware,
)
from src.middleware.logging import RequestLoggingMiddleware
from src.utils.structured_logging import setup_structured_logging


logger = logging.getLogger(__name__)
settings = get_settings()


def _run_escalation_loop(stop_event: threading.Event):
    """Background thread that runs escalation checks every 15 minutes."""
    from src.database import SessionLocal
    from src.services.escalation_service import escalation_service

    while not stop_event.is_set():
        try:
            db = SessionLocal()
            escalation_service.run_escalation_check(db)
            db.close()
        except Exception:
            logger.exception("Escalation check failed")
        stop_event.wait(900)  # 15 minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    init_db()
    # Initialize structured JSON logging
    setup_structured_logging(settings.log_level if hasattr(settings, 'log_level') else "INFO")
    # Start background escalation checker
    stop_event = threading.Event()
    escalation_thread = threading.Thread(
        target=_run_escalation_loop, args=(stop_event,), daemon=True
    )
    escalation_thread.start()
    yield
    stop_event.set()


app = FastAPI(
    title="Anvils",
    description="AI-powered company incorporation and compliance platform for India",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — defaults to localhost for dev; override CORS_ORIGINS env var for production
cors_origins = (
    [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    if settings.cors_origins
    else ["http://localhost:3000", "http://127.0.0.1:3000"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Security & observability middleware (added after CORS so CORS runs first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls_per_minute=120)
app.add_middleware(PIIMaskingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    body = {"error": {"code": exc.error_code, "message": exc.detail}}
    if exc.details is not None:
        body["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        details.append({
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
        })
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": details}},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    message = str(exc) if settings.environment == "development" else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": message}},
    )


# Mount routers under /api/v1
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(companies.router, prefix=settings.api_v1_prefix)
app.include_router(payments.router, prefix=settings.api_v1_prefix)
app.include_router(documents.router, prefix=settings.api_v1_prefix)
app.include_router(pricing.router, prefix=settings.api_v1_prefix)
app.include_router(wizard.router, prefix=settings.api_v1_prefix)
app.include_router(chatbot.router, prefix=settings.api_v1_prefix)
app.include_router(notifications.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)
app.include_router(post_incorporation.router, prefix=settings.api_v1_prefix)
app.include_router(compliance.router, prefix=settings.api_v1_prefix)
app.include_router(entity_comparison.router, prefix=settings.api_v1_prefix)
app.include_router(cap_table.router, prefix=settings.api_v1_prefix)
app.include_router(ops.router, prefix=settings.api_v1_prefix)
app.include_router(legal_docs.router, prefix=settings.api_v1_prefix)
app.include_router(statutory_registers.router, prefix=settings.api_v1_prefix)
app.include_router(meetings.router, prefix=settings.api_v1_prefix)
app.include_router(data_room.router, prefix=settings.api_v1_prefix)
app.include_router(esign.router, prefix=settings.api_v1_prefix)
app.include_router(invoices.router, prefix=settings.api_v1_prefix)
app.include_router(founder_education.router, prefix=settings.api_v1_prefix)
app.include_router(messages.router, prefix=settings.api_v1_prefix)
app.include_router(services.router, prefix=settings.api_v1_prefix)
app.include_router(accounting.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
    }
