import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database import Base, get_db
from src.main import app
from fastapi.testclient import TestClient
from src.utils.security import get_password_hash, create_access_token
# Import all models via __init__ so Base.metadata has every table
# (ordering matters for foreign-key resolution, and __init__ handles it)
import src.models  # noqa: F401
from src.models.user import User, UserRole
from src.models.company import Company, EntityType, CompanyStatus, PlanTier
from src.models.legal_template import LegalDocument
from src.models.compliance_task import ComplianceTask, ComplianceTaskType, ComplianceTaskStatus
from src.models.shareholder import Shareholder, ShareType
from src.models.meeting import Meeting
from src.models.data_room import DataRoomFolder, DataRoomFile, DataRoomShareLink
from src.models.esign import SignatureRequest, Signatory, SignatureAuditLog
from src.models.service_catalog import Subscription, SubscriptionStatus, SubscriptionInterval
from datetime import datetime, timedelta, timezone

# Use in-memory SQLite for tests.  StaticPool ensures every connection
# shares the same underlying database so the app sees test data.
TEST_DB_URL = "sqlite://"


@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Enable SQLite foreign-key enforcement
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _clear_rate_limiter():
    """Walk app.middleware_stack to find the RateLimitMiddleware and clear its
    in-memory request log so tests are not throttled by prior test calls."""
    stack = getattr(app, "middleware_stack", None)
    if stack is None:
        return
    obj = stack
    while obj is not None:
        if hasattr(obj, "requests") and type(obj).__name__ == "RateLimitMiddleware":
            obj.requests.clear()
            return
        obj = getattr(obj, "app", None)


@pytest.fixture
def client(db_session):
    """TestClient with overridden DB dependency and cleared rate limiter."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        _clear_rate_limiter()
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user and return it."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        phone="+919876543210",
        hashed_password=get_password_hash("testpassword123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Return Authorization headers for the test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_company(db_session, test_user):
    """Create a test company owned by the test user."""
    company = Company(
        user_id=test_user.id,
        entity_type=EntityType.PRIVATE_LIMITED,
        plan_tier=PlanTier.LAUNCH,
        proposed_names=["Test Company Pvt Ltd"],
        approved_name="Test Company Pvt Ltd",
        state="Karnataka",
        authorized_capital=100000,
        num_directors=2,
        status=CompanyStatus.INCORPORATED,
        cin="U12345KA2025PTC000001",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for admin-only endpoints."""
    user = User(
        email="admin@example.com",
        full_name="Admin User",
        phone="+919876543211",
        hashed_password=get_password_hash("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user):
    """Return Authorization headers for the admin user."""
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_legal_document(db_session, test_user):
    """Create a finalized legal document for e-sign tests."""
    doc = LegalDocument(
        user_id=test_user.id,
        template_type="nda",
        title="Test NDA",
        status="finalized",
        generated_html="<html><body><h1>Test NDA</h1><p>Content here</p></body></html>",
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc


@pytest.fixture
def test_compliance_task(db_session, test_company):
    """Create a compliance task for update tests."""
    task = ComplianceTask(
        company_id=test_company.id,
        task_type=ComplianceTaskType.AOC_4,
        title="File AOC-4 Annual Accounts",
        description="Annual financial statement filing",
        due_date=datetime.now(timezone.utc) + timedelta(days=30),
        status=ComplianceTaskStatus.UPCOMING,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def test_overdue_task(db_session, test_company):
    """Create an overdue compliance task."""
    task = ComplianceTask(
        company_id=test_company.id,
        task_type=ComplianceTaskType.MGT_7,
        title="File MGT-7 Annual Return",
        description="Annual return filing",
        due_date=datetime.now(timezone.utc) - timedelta(days=10),
        status=ComplianceTaskStatus.OVERDUE,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def test_shareholder(db_session, test_company):
    """Create a test shareholder."""
    sh = Shareholder(
        company_id=test_company.id,
        name="Founder A",
        email="founder@example.com",
        shares=5000,
        share_type=ShareType.EQUITY,
        face_value=10.0,
        paid_up_value=10.0,
        is_promoter=True,
    )
    db_session.add(sh)
    db_session.commit()
    db_session.refresh(sh)
    return sh


@pytest.fixture
def second_shareholder(db_session, test_company):
    """Create a second shareholder for transfer tests."""
    sh = Shareholder(
        company_id=test_company.id,
        name="Founder B",
        email="founderb@example.com",
        shares=5000,
        share_type=ShareType.EQUITY,
        face_value=10.0,
        paid_up_value=10.0,
        is_promoter=True,
    )
    db_session.add(sh)
    db_session.commit()
    db_session.refresh(sh)
    return sh


@pytest.fixture
def test_folder(db_session, test_company):
    """Create a test data room folder."""
    folder = DataRoomFolder(
        company_id=test_company.id,
        name="Test Folder",
        folder_type="CUSTOM",
        sort_order=1,
    )
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)
    return folder


@pytest.fixture
def scale_subscription(db_session, test_company, test_user):
    """Create an active 'scale' subscription so tier-gated endpoints pass."""
    sub = Subscription(
        company_id=test_company.id,
        user_id=test_user.id,
        plan_key="scale",
        plan_name="Scale",
        interval=SubscriptionInterval.ANNUAL,
        amount=99900,
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub
