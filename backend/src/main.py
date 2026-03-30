import logging
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
from src.routers import esop
from src.routers import fundraising
from src.routers import share_issuance
from src.routers import stakeholders
from src.routers import investor_portal
from src.routers import cap_table_onboarding
from src.routers import valuations
from src.routers import ca_portal
from src.routers import copilot
from src.routers import marketplace
from src.routers import compliance_documents
from src.routers.company_members import router as company_members_router, invite_router, my_companies_router
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
    """Background thread that runs escalation and compliance reminder checks every 15 minutes."""
    from src.database import SessionLocal
    from src.services.escalation_service import escalation_service
    from src.services.compliance_engine import compliance_engine

    while not stop_event.is_set():
        try:
            db = SessionLocal()
            escalation_service.run_escalation_check(db)
            compliance_engine.check_and_send_reminders(db)
            db.close()
        except Exception:
            logger.exception("Escalation/compliance check failed")
        stop_event.wait(900)  # 15 minutes


def _seed_demo_data():
    """In development, bootstrap demo users, a demo company, memberships, and
    Scale subscriptions so the full dashboard is accessible out of the box.

    Runs only when ENVIRONMENT=development.  Fully idempotent — safe to call
    on every startup.  Uses raw SQL to avoid ORM column-mismatch issues with
    un-migrated SQLite schemas.
    """
    if settings.environment != "development":
        return

    from src.database import engine
    from src.utils.security import get_password_hash
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import text

    DEMO_USERS = [
        {"email": "paul@anvils.in", "name": "Paul", "role": "SUPER_ADMIN"},
        {"email": "janeevan@anvils.in", "name": "Janeevan", "role": "SUPER_ADMIN"},
        {"email": "abey@anvils.in", "name": "Abey", "role": "SUPER_ADMIN"},
        {"email": "ca@anvils.in", "name": "CA Demo", "role": "CA_LEAD"},
    ]
    DEMO_PASSWORD_HASH = get_password_hash("Anvils123")

    now = datetime.now(timezone.utc).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()

    with engine.connect() as conn:
        try:
            # ----------------------------------------------------------
            # Step 1: Create demo users if they don't exist
            # ----------------------------------------------------------
            user_ids = {}
            for u in DEMO_USERS:
                row = conn.execute(
                    text("SELECT id FROM users WHERE email = :e"),
                    {"e": u["email"]},
                ).fetchone()
                if row:
                    user_ids[u["email"]] = row[0]
                else:
                    conn.execute(
                        text(
                            "INSERT INTO users (email, full_name, hashed_password, role, is_active, created_at, updated_at) "
                            "VALUES (:email, :name, :pw, :role, 1, :now, :now)"
                        ),
                        {"email": u["email"], "name": u["name"], "pw": DEMO_PASSWORD_HASH, "role": u["role"], "now": now},
                    )
                    new_row = conn.execute(
                        text("SELECT id FROM users WHERE email = :e"),
                        {"e": u["email"]},
                    ).fetchone()
                    user_ids[u["email"]] = new_row[0]
                    logger.info("Created demo user %s", u["email"])

            # ----------------------------------------------------------
            # Step 2: Ensure at least one company exists
            # ----------------------------------------------------------
            all_companies = conn.execute(
                text("SELECT id, user_id FROM companies")
            ).fetchall()

            if not all_companies:
                # Create a demo company owned by the first demo user
                first_uid = user_ids[DEMO_USERS[0]["email"]]
                conn.execute(
                    text(
                        "INSERT INTO companies "
                        "(user_id, entity_type, proposed_names, state, "
                        "authorized_capital, num_directors, status, priority, "
                        "created_at, updated_at) "
                        "VALUES (:uid, 'private_limited', :names, 'Karnataka', "
                        "1000000, 2, 'INCORPORATED', 'NORMAL', :now, :now)"
                    ),
                    {
                        "uid": first_uid,
                        "names": '["Anvils Demo Private Limited"]',
                        "now": now,
                    },
                )
                # Update approved name
                demo_cid = conn.execute(
                    text("SELECT id FROM companies WHERE user_id = :uid ORDER BY id DESC LIMIT 1"),
                    {"uid": first_uid},
                ).fetchone()[0]
                conn.execute(
                    text("UPDATE companies SET approved_name = 'Anvils Demo Private Limited' WHERE id = :cid"),
                    {"cid": demo_cid},
                )
                logger.info("Created demo company (id=%d)", demo_cid)
                all_companies = conn.execute(
                    text("SELECT id, user_id FROM companies")
                ).fetchall()

            # ----------------------------------------------------------
            # Step 3: Add demo users as members of all companies
            # ----------------------------------------------------------
            for email, uid in user_ids.items():
                existing_memberships = set(
                    r[0]
                    for r in conn.execute(
                        text("SELECT company_id FROM company_members WHERE user_id = :uid"),
                        {"uid": uid},
                    ).fetchall()
                )

                for company_id, owner_id in all_companies:
                    if owner_id == uid:
                        continue
                    if company_id in existing_memberships:
                        continue
                    conn.execute(
                        text(
                            "INSERT INTO company_members "
                            "(company_id, user_id, invite_email, invite_name, role, "
                            "invite_status, invited_by, created_at, accepted_at) "
                            "VALUES (:cid, :uid, :email, 'Demo', 'admin', "
                            "'accepted', :owner, :now, :now)"
                        ),
                        {"cid": company_id, "uid": uid, "email": email, "owner": owner_id, "now": now},
                    )
                    logger.info("Added %s as member of company %d", email, company_id)

            # ----------------------------------------------------------
            # Step 4: Ensure every company has a Scale subscription
            # ----------------------------------------------------------
            for company_id, owner_id in all_companies:
                existing = conn.execute(
                    text(
                        "SELECT id, plan_key FROM subscriptions "
                        "WHERE company_id = :cid AND status = 'active'"
                    ),
                    {"cid": company_id},
                ).fetchone()

                if existing:
                    if existing[1] == "scale":
                        continue
                    conn.execute(
                        text(
                            "UPDATE subscriptions SET plan_key = 'scale', "
                            "plan_name = 'Anvils Scale', amount = 99999 "
                            "WHERE id = :sid"
                        ),
                        {"sid": existing[0]},
                    )
                    logger.info("Upgraded company %d to Scale", company_id)
                else:
                    conn.execute(
                        text(
                            "INSERT INTO subscriptions "
                            "(company_id, user_id, plan_key, plan_name, \"interval\", "
                            "amount, status, current_period_start, current_period_end, "
                            "created_at, updated_at) "
                            "VALUES (:cid, :uid, 'scale', 'Anvils Scale', 'annual', "
                            "99999, 'active', :now, :end, :now, :now)"
                        ),
                        {"cid": company_id, "uid": owner_id, "now": now, "end": end},
                    )
                    logger.info("Seeded Scale subscription for company %d", company_id)

            conn.commit()
            logger.info("Demo data seed complete")
        except Exception:
            conn.rollback()
            logger.exception("Failed to seed demo data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    init_db()
    _seed_demo_data()
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
    import traceback, sys
    tb = traceback.format_exc()
    print(f"UNHANDLED EXCEPTION on {request.method} {request.url.path}:\n{tb}", file=sys.stderr, flush=True)
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
app.include_router(esop.router, prefix=settings.api_v1_prefix)
app.include_router(fundraising.router, prefix=settings.api_v1_prefix)
app.include_router(share_issuance.router, prefix=settings.api_v1_prefix)
app.include_router(stakeholders.router, prefix=settings.api_v1_prefix)
app.include_router(investor_portal.router, prefix=settings.api_v1_prefix)
app.include_router(cap_table_onboarding.router, prefix=settings.api_v1_prefix)
app.include_router(valuations.router, prefix=settings.api_v1_prefix)
app.include_router(ca_portal.router, prefix=settings.api_v1_prefix)
app.include_router(copilot.router, prefix=settings.api_v1_prefix)
app.include_router(marketplace.router, prefix=settings.api_v1_prefix)
app.include_router(compliance_documents.router, prefix=settings.api_v1_prefix)
app.include_router(company_members_router, prefix=settings.api_v1_prefix)
app.include_router(invite_router, prefix=settings.api_v1_prefix)
app.include_router(my_companies_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
    }
