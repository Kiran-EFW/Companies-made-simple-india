import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.main import app
from fastapi.testclient import TestClient
from src.utils.security import get_password_hash, create_access_token
from src.models.user import User, UserRole
from src.models.company import Company, EntityType, CompanyStatus, PlanTier
from src.models.legal_template import LegalDocument
from src.models.compliance_task import ComplianceTask, ComplianceTaskType, ComplianceTaskStatus
from src.models.shareholder import Shareholder, ShareType
from src.models.meeting import Meeting
from src.models.data_room import DataRoomFolder, DataRoomFile, DataRoomShareLink
from src.models.esign import SignatureRequest, Signatory, SignatureAuditLog
from datetime import datetime, timedelta, timezone

# Use in-memory SQLite for tests (avoids stale file issues between runs)
TEST_DB_URL = "sqlite:///./test.db"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """TestClient with overridden DB dependency."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
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
