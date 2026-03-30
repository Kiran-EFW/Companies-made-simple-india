import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _ensure_pg_columns():
    """Idempotently add any columns that the ORM models expect but that
    may be missing from the PostgreSQL schema.  Runs raw DDL so it works
    regardless of whether alembic migrations succeeded.

    Each statement runs individually so one failure doesn't block others.
    """
    from sqlalchemy import text

    # Individual ALTER TABLE statements — one per column for resilience.
    # Format: (table, column, type_sql)
    COLUMNS = [
        # users
        ("users", "reset_token", "VARCHAR"),
        ("users", "reset_token_expiry", "TIMESTAMP"),
        ("users", "department", "staffdepartment"),
        ("users", "seniority", "staffseniority"),
        ("users", "reports_to", "INTEGER REFERENCES users(id)"),
        # companies
        ("companies", "segment", "customersegment"),
        ("companies", "plan_tier", "plantier"),
        ("companies", "employee_count", "INTEGER"),
        ("companies", "incorporation_date", "TIMESTAMP"),
        ("companies", "pricing_snapshot", "JSONB"),
        ("companies", "assigned_to", "INTEGER REFERENCES users(id)"),
        ("companies", "cin", "VARCHAR"),
        ("companies", "pan", "VARCHAR"),
        ("companies", "tan", "VARCHAR"),
        ("companies", "data", "JSONB DEFAULT '{}'::jsonb"),
        # shareholders
        ("shareholders", "stakeholder_profile_id", "INTEGER REFERENCES stakeholder_profiles(id)"),
        # subscriptions
        ("subscriptions", "pending_plan_key", "VARCHAR"),
        ("subscriptions", "pending_plan_name", "VARCHAR"),
        ("subscriptions", "pending_amount", "INTEGER"),
    ]

    with engine.connect() as conn:
        # Step 1: Ensure enum types exist
        enum_types = {
            "customersegment": "'micro_business','sme','startup','non_profit','nidhi','producer','enterprise'",
            "plantier": "'launch','grow','scale'",
            "staffdepartment": "'cs','ca','filing','support','admin'",
            "staffseniority": "'junior','mid','senior','lead','head'",
        }
        for ename, evalues in enum_types.items():
            try:
                conn.execute(text(
                    f"DO $$ BEGIN "
                    f"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{ename}') THEN "
                    f"CREATE TYPE {ename} AS ENUM ({evalues}); "
                    f"END IF; END $$;"
                ))
            except Exception as exc:
                logger.warning("ensure_pg enum %s: %s", ename, exc)

        # Step 2: Add enum values to entitytype
        for val in ("nidhi", "producer_company"):
            try:
                conn.execute(text(
                    f"ALTER TYPE entitytype ADD VALUE IF NOT EXISTS '{val}'"
                ))
            except Exception as exc:
                logger.warning("ensure_pg entitytype+%s: %s", val, exc)

        # Step 3: Add missing columns (one at a time)
        for table, col, col_type in COLUMNS:
            try:
                exists = conn.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name = :t AND column_name = :c"
                ), {"t": table, "c": col}).fetchone()
                if not exists:
                    conn.execute(text(
                        f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"
                    ))
                    logger.info("ensure_pg: added %s.%s", table, col)
            except Exception as exc:
                logger.warning("ensure_pg %s.%s: %s", table, col, exc)

        # Step 4: Fix plan_tier type if it was created as VARCHAR
        try:
            row = conn.execute(text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name = 'companies' AND column_name = 'plan_tier'"
            )).fetchone()
            if row and row[0] == "character varying":
                conn.execute(text(
                    "ALTER TABLE companies ALTER COLUMN plan_tier "
                    "TYPE plantier USING plan_tier::plantier"
                ))
                logger.info("ensure_pg: converted plan_tier to enum")
        except Exception as exc:
            logger.warning("ensure_pg plan_tier fix: %s", exc)

        conn.commit()
    logger.info("ensure_pg: completed")


def init_db():
    """Create / migrate all tables. Called on app startup.

    - **SQLite** (development): uses ``create_all`` for simplicity.
    - **PostgreSQL** (production): runs Alembic migrations so that new
      columns and schema changes are applied automatically on deploy.
      If the database was originally bootstrapped by ``create_all``
      (no ``alembic_version`` table), we stamp it at the last known
      state before running ``upgrade head``.
    """
    # Import all models so metadata is fully populated
    from src.models import user, company, director, document, payment, pricing, task  # noqa
    from src.models import notification, admin_log, internal_note  # noqa
    from src.models import compliance_task  # noqa
    from src.models import shareholder  # noqa
    from src.models import filing_task, verification_queue, escalation_rule  # noqa
    from src.models import legal_template  # noqa
    from src.models import statutory_register, meeting, data_room  # noqa
    from src.models import esign  # noqa
    from src.models import message  # noqa
    from src.models import service_catalog  # noqa
    from src.models import accounting_connection  # noqa
    from src.models import esop  # noqa
    from src.models import funding_round  # noqa
    from src.models import stakeholder  # noqa
    from src.models import conversion_event  # noqa
    from src.models import valuation  # noqa
    from src.models import ca_assignment  # noqa
    from src.models import investor_interest  # noqa
    from src.models import company_member  # noqa
    from src.models import deal_share  # noqa
    from src.models import marketplace  # noqa

    if "sqlite" in settings.database_url:
        # Dev / SQLite — create_all is fine
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as exc:
            logger.warning("create_all error (continuing): %s", exc)
    else:
        # Production / PostgreSQL — run Alembic migrations
        try:
            import os
            from alembic.config import Config
            from alembic import command
            from sqlalchemy import inspect, text

            # Resolve alembic.ini relative to the backend root (/app)
            backend_root = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "..")
            )
            alembic_ini = os.path.join(backend_root, "alembic.ini")
            alembic_cfg = Config(alembic_ini)
            alembic_cfg.set_main_option(
                "script_location", os.path.join(backend_root, "alembic")
            )
            alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

            # If the DB was bootstrapped by create_all and has no
            # alembic_version table, stamp it at 005_segments (the last
            # migration that existed before we added missing-column fixes).
            inspector = inspect(engine)
            if "alembic_version" not in inspector.get_table_names():
                command.stamp(alembic_cfg, "005_segments")
                logger.info("Stamped alembic at 005_segments (existing DB)")

            command.upgrade(alembic_cfg, "head")
            logger.info("Alembic migrations applied successfully")
        except Exception as exc:
            logger.exception("Alembic migration error (continuing): %s", exc)

        # Belt-and-suspenders: ensure critical columns exist via raw SQL.
        # This handles cases where alembic migrations fail silently.
        _ensure_pg_columns()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
