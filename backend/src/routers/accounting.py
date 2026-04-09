"""
Accounting Integration Router — connect Zoho Books / Tally to a company,
manage OAuth flow, and sync data.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.utils.security import get_current_user
from src.models.user import User
from src.models.company import Company
from src.models.accounting_connection import (
    AccountingConnection, AccountingPlatform, ConnectionStatus,
)
from src.services.zoho_books_service import zoho_books_service
from src.utils.company_access import get_user_company

router = APIRouter(prefix="/accounting", tags=["Accounting"])


# ── Schemas ─────────────────────────────────────────────────────────────

from pydantic import BaseModel
from typing import List


class AccountingConnectionOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    company_id: int
    platform: str
    status: str
    zoho_org_name: Optional[str] = None
    tally_host: Optional[str] = None
    tally_port: Optional[int] = None
    tally_company_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    created_at: datetime


class ZohoConnectRequest(BaseModel):
    company_id: int
    code: str  # OAuth authorization code


class TallyConnectRequest(BaseModel):
    company_id: int
    host: str = "localhost"
    port: int = 9000
    company_name: str


class SyncSummaryOut(BaseModel):
    total_invoices: int = 0
    total_bills: int = 0
    fy_period: str = ""
    last_synced: Optional[str] = None
    status: str = "unknown"
    error: Optional[str] = None


# ── Get Auth URL ────────────────────────────────────────────────────────

@router.get("/zoho/auth-url")
def get_zoho_auth_url(
    company_id: int = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Get the Zoho OAuth2 authorization URL for connecting."""
    url = zoho_books_service.get_auth_url(state=str(company_id))
    return {"auth_url": url, "company_id": company_id}


# ── Connect Zoho Books ─────────────────────────────────────────────────

@router.post("/zoho/connect", response_model=AccountingConnectionOut)
async def connect_zoho_books(
    payload: ZohoConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exchange OAuth code and connect Zoho Books to a company."""
    # Verify company ownership
    company = get_user_company(payload.company_id, db, current_user)

    # Check for existing connection
    existing = db.query(AccountingConnection).filter(
        AccountingConnection.company_id == payload.company_id,
    ).first()
    if existing and existing.status == ConnectionStatus.CONNECTED:
        raise HTTPException(status_code=400, detail="Company already has an active accounting connection")

    # Exchange code for tokens
    try:
        tokens = await zoho_books_service.exchange_code(payload.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect Zoho Books: {str(e)}")

    # Get organizations to find the right one
    try:
        orgs = await zoho_books_service.get_organizations(tokens["access_token"])
    except Exception:
        orgs = []

    org_id = orgs[0]["organization_id"] if orgs else ""
    org_name = orgs[0]["name"] if orgs else "Unknown"

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600))

    if existing:
        existing.platform = AccountingPlatform.ZOHO_BOOKS
        existing.status = ConnectionStatus.CONNECTED
        existing.zoho_org_id = org_id
        existing.zoho_org_name = org_name
        existing.zoho_access_token = tokens["access_token"]
        existing.zoho_refresh_token = tokens.get("refresh_token", existing.zoho_refresh_token)
        existing.zoho_token_expires_at = expires_at
        existing.updated_at = datetime.now(timezone.utc)
        conn = existing
    else:
        conn = AccountingConnection(
            company_id=payload.company_id,
            user_id=current_user.id,
            platform=AccountingPlatform.ZOHO_BOOKS,
            status=ConnectionStatus.CONNECTED,
            zoho_org_id=org_id,
            zoho_org_name=org_name,
            zoho_access_token=tokens["access_token"],
            zoho_refresh_token=tokens.get("refresh_token"),
            zoho_token_expires_at=expires_at,
        )
        db.add(conn)

    db.commit()
    db.refresh(conn)
    return conn


# ── Connect Tally Prime ────────────────────────────────────────────────

@router.post("/tally/connect", response_model=AccountingConnectionOut)
def connect_tally(
    payload: TallyConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Connect Tally Prime to a company."""
    company = get_user_company(payload.company_id, db, current_user)

    existing = db.query(AccountingConnection).filter(
        AccountingConnection.company_id == payload.company_id,
    ).first()
    if existing and existing.status == ConnectionStatus.CONNECTED:
        raise HTTPException(status_code=400, detail="Company already has an active accounting connection")

    if existing:
        existing.platform = AccountingPlatform.TALLY_PRIME
        existing.status = ConnectionStatus.CONNECTED
        existing.tally_host = payload.host
        existing.tally_port = payload.port
        existing.tally_company_name = payload.company_name
        existing.updated_at = datetime.now(timezone.utc)
        conn = existing
    else:
        conn = AccountingConnection(
            company_id=payload.company_id,
            user_id=current_user.id,
            platform=AccountingPlatform.TALLY_PRIME,
            status=ConnectionStatus.CONNECTED,
            tally_host=payload.host,
            tally_port=payload.port,
            tally_company_name=payload.company_name,
        )
        db.add(conn)

    db.commit()
    db.refresh(conn)
    return conn


# ── Get Connection Status ──────────────────────────────────────────────

@router.get("/connection/{company_id}", response_model=AccountingConnectionOut)
def get_connection(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the accounting connection for a company."""
    get_user_company(company_id, db, current_user)
    conn = db.query(AccountingConnection).filter(
        AccountingConnection.company_id == company_id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="No accounting connection found")
    return conn


# ── List Connections ───────────────────────────────────────────────────

@router.get("/connections", response_model=list[AccountingConnectionOut])
def list_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all accounting connections for the current user's companies."""
    connections = db.query(AccountingConnection).filter(
        AccountingConnection.user_id == current_user.id,
    ).all()
    return connections


# ── Disconnect ─────────────────────────────────────────────────────────

@router.post("/disconnect/{company_id}")
def disconnect_accounting(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Disconnect accounting platform from a company."""
    get_user_company(company_id, db, current_user)
    conn = db.query(AccountingConnection).filter(
        AccountingConnection.company_id == company_id,
        AccountingConnection.user_id == current_user.id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="No connection found")

    conn.status = ConnectionStatus.DISCONNECTED
    conn.zoho_access_token = None
    conn.zoho_refresh_token = None
    conn.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Accounting platform disconnected"}


# ── Sync Data ──────────────────────────────────────────────────────────

@router.post("/sync/{company_id}", response_model=SyncSummaryOut)
async def sync_accounting_data(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger a data sync from the connected accounting platform."""
    get_user_company(company_id, db, current_user)
    conn = db.query(AccountingConnection).filter(
        AccountingConnection.company_id == company_id,
        AccountingConnection.user_id == current_user.id,
        AccountingConnection.status == ConnectionStatus.CONNECTED,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="No active accounting connection")

    if conn.platform == AccountingPlatform.ZOHO_BOOKS:
        # Refresh token if expired
        if conn.zoho_token_expires_at and conn.zoho_token_expires_at < datetime.now(timezone.utc):
            try:
                tokens = await zoho_books_service.refresh_access_token(conn.zoho_refresh_token)
                conn.zoho_access_token = tokens["access_token"]
                conn.zoho_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens["expires_in"])
            except Exception as e:
                conn.status = ConnectionStatus.ERROR
                conn.last_sync_status = "error"
                conn.last_sync_error = f"Token refresh failed: {str(e)}"
                db.commit()
                raise HTTPException(status_code=400, detail="Failed to refresh Zoho token. Please reconnect.")

        summary = await zoho_books_service.get_sync_summary(
            conn.zoho_access_token, conn.zoho_org_id,
        )

        conn.last_sync_at = datetime.now(timezone.utc)
        conn.last_sync_status = summary.get("status", "error")
        conn.last_sync_error = summary.get("error")
        db.commit()

        return SyncSummaryOut(**summary)

    elif conn.platform == AccountingPlatform.TALLY_PRIME:
        # Tally sync is done via XML HTTP — placeholder for now
        conn.last_sync_at = datetime.now(timezone.utc)
        conn.last_sync_status = "success"
        db.commit()
        return SyncSummaryOut(
            status="success",
            last_synced=datetime.now(timezone.utc).isoformat(),
        )

    raise HTTPException(status_code=400, detail="Unsupported platform")
