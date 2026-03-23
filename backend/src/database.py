from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Create all tables. Called on app startup."""
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
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
