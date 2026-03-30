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
    regardless of whether alembic migrations succeeded."""
    from sqlalchemy import text

    DDL = [
        # --- enum types ---
        """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'customersegment') THEN
                CREATE TYPE customersegment AS ENUM (
                    'micro_business','sme','startup','non_profit',
                    'nidhi','producer','enterprise'
                );
            END IF;
        END $$;
        """,
        """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plantier') THEN
                CREATE TYPE plantier AS ENUM ('launch','grow','scale');
            END IF;
        END $$;
        """,
        # --- enum values ---
        "ALTER TYPE entitytype ADD VALUE IF NOT EXISTS 'nidhi'",
        "ALTER TYPE entitytype ADD VALUE IF NOT EXISTS 'producer_company'",
        # --- columns ---
        """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='reset_token') THEN
                ALTER TABLE users ADD COLUMN reset_token VARCHAR;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='reset_token_expiry') THEN
                ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='companies' AND column_name='segment') THEN
                ALTER TABLE companies ADD COLUMN segment customersegment;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='companies' AND column_name='plan_tier') THEN
                ALTER TABLE companies ADD COLUMN plan_tier plantier;
            ELSE
                -- Fix: migration 006 may have created this as VARCHAR
                IF (SELECT data_type FROM information_schema.columns WHERE table_name='companies' AND column_name='plan_tier') = 'character varying' THEN
                    ALTER TABLE companies ALTER COLUMN plan_tier TYPE plantier USING plan_tier::plantier;
                END IF;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='shareholders' AND column_name='stakeholder_profile_id') THEN
                ALTER TABLE shareholders ADD COLUMN stakeholder_profile_id INTEGER REFERENCES stakeholder_profiles(id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscriptions' AND column_name='pending_plan_key') THEN
                ALTER TABLE subscriptions ADD COLUMN pending_plan_key VARCHAR;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscriptions' AND column_name='pending_plan_name') THEN
                ALTER TABLE subscriptions ADD COLUMN pending_plan_name VARCHAR;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscriptions' AND column_name='pending_amount') THEN
                ALTER TABLE subscriptions ADD COLUMN pending_amount INTEGER;
            END IF;
        END $$;
        """,
    ]

    with engine.connect() as conn:
        for i, stmt in enumerate(DDL):
            try:
                conn.execute(text(stmt))
                print(f"[ensure_pg] DDL {i+1}/{len(DDL)} OK", flush=True)
            except Exception as exc:
                print(f"[ensure_pg] DDL {i+1}/{len(DDL)} SKIPPED: {exc}", flush=True)
        conn.commit()
    print("[ensure_pg] _ensure_pg_columns completed", flush=True)


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
