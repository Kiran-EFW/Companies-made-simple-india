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
            backend_root = os.path.join(os.path.dirname(__file__), "..")
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


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
