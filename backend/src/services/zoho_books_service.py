"""
Zoho Books Integration Service — handles OAuth2, data sync, and API calls.

Zoho Books API: https://www.zoho.com/books/api/v3/
Auth: OAuth 2.0 with refresh token flow.
"""

import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ZohoBooksService:
    """Service for interacting with Zoho Books API."""

    AUTH_BASE = "https://accounts.zoho.in/oauth/v2"  # .in for India DC
    API_BASE = "https://www.zohoapis.in/books/v3"

    def __init__(self):
        self.client_id = getattr(settings, "zoho_client_id", "")
        self.client_secret = getattr(settings, "zoho_client_secret", "")
        self.redirect_uri = getattr(settings, "zoho_redirect_uri", "http://localhost:3000/settings/accounting/callback")

    # ── OAuth2 Flow ─────────────────────────────────────────────────────

    def get_auth_url(self, state: str = "") -> str:
        """Generate the Zoho OAuth2 authorization URL."""
        scopes = [
            "ZohoBooks.fullaccess.all",
        ]
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": ",".join(scopes),
            "redirect_uri": self.redirect_uri,
            "access_type": "offline",  # get refresh token
            "prompt": "consent",
        }
        if state:
            params["state"] = state
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_BASE}/auth?{qs}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access + refresh tokens."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.AUTH_BASE}/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": code,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),
                "expires_in": data.get("expires_in", 3600),
                "token_type": data.get("token_type", "Bearer"),
            }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.AUTH_BASE}/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "access_token": data["access_token"],
                "expires_in": data.get("expires_in", 3600),
            }

    # ── API Calls ───────────────────────────────────────────────────────

    async def _api_call(
        self,
        method: str,
        path: str,
        access_token: str,
        org_id: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated API call to Zoho Books."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        url = f"{self.API_BASE}{path}"
        query_params = {"organization_id": org_id}
        if params:
            query_params.update(params)

        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method, url,
                headers=headers,
                params=query_params,
                json=json_data,
                timeout=30.0,
            )
            resp.raise_for_status()
            return resp.json()

    # ── Organization ────────────────────────────────────────────────────

    async def get_organizations(self, access_token: str) -> List[Dict[str, Any]]:
        """Get all organizations linked to this Zoho account."""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.API_BASE}/organizations",
                headers=headers,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("organizations", [])

    # ── Chart of Accounts ───────────────────────────────────────────────

    async def get_chart_of_accounts(
        self, access_token: str, org_id: str
    ) -> List[Dict[str, Any]]:
        """Fetch the chart of accounts."""
        data = await self._api_call("GET", "/chartofaccounts", access_token, org_id)
        return data.get("chartofaccounts", [])

    # ── Invoices ────────────────────────────────────────────────────────

    async def get_invoices(
        self, access_token: str, org_id: str, page: int = 1
    ) -> Dict[str, Any]:
        """List invoices (sales register for GSTR-1)."""
        data = await self._api_call(
            "GET", "/invoices", access_token, org_id,
            params={"page": page, "per_page": 200, "sort_column": "date", "sort_order": "D"},
        )
        return {
            "invoices": data.get("invoices", []),
            "page_context": data.get("page_context", {}),
        }

    # ── Bills ───────────────────────────────────────────────────────────

    async def get_bills(
        self, access_token: str, org_id: str, page: int = 1
    ) -> Dict[str, Any]:
        """List bills (purchase register for GSTR-2)."""
        data = await self._api_call(
            "GET", "/bills", access_token, org_id,
            params={"page": page, "per_page": 200},
        )
        return {
            "bills": data.get("bills", []),
            "page_context": data.get("page_context", {}),
        }

    # ── Bank Transactions ───────────────────────────────────────────────

    async def get_bank_transactions(
        self, access_token: str, org_id: str, account_id: str, page: int = 1
    ) -> Dict[str, Any]:
        """Get bank transactions for a specific account."""
        data = await self._api_call(
            "GET", "/banktransactions", access_token, org_id,
            params={"account_id": account_id, "page": page, "per_page": 200},
        )
        return {
            "banktransactions": data.get("banktransactions", []),
            "page_context": data.get("page_context", {}),
        }

    # ── Journal Entries ─────────────────────────────────────────────────

    async def get_journals(
        self, access_token: str, org_id: str, page: int = 1
    ) -> Dict[str, Any]:
        """List journal entries."""
        data = await self._api_call(
            "GET", "/journals", access_token, org_id,
            params={"page": page, "per_page": 200},
        )
        return {
            "journals": data.get("journals", []),
            "page_context": data.get("page_context", {}),
        }

    # ── Financial Reports ───────────────────────────────────────────────

    async def get_trial_balance(
        self, access_token: str, org_id: str,
        from_date: Optional[str] = None, to_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get trial balance report."""
        params: Dict[str, Any] = {}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return await self._api_call(
            "GET", "/reports/trialbalance", access_token, org_id, params=params,
        )

    async def get_profit_and_loss(
        self, access_token: str, org_id: str,
        from_date: Optional[str] = None, to_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get profit and loss report."""
        params: Dict[str, Any] = {}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return await self._api_call(
            "GET", "/reports/profitandloss", access_token, org_id, params=params,
        )

    async def get_balance_sheet(
        self, access_token: str, org_id: str,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get balance sheet report."""
        params: Dict[str, Any] = {}
        if date:
            params["date"] = date
        return await self._api_call(
            "GET", "/reports/balancesheet", access_token, org_id, params=params,
        )

    # ── GST Data ────────────────────────────────────────────────────────

    async def get_gst_summary(
        self, access_token: str, org_id: str,
        from_date: str, to_date: str,
    ) -> Dict[str, Any]:
        """Get GST summary data for return filing."""
        return await self._api_call(
            "GET", "/reports/taxsummary", access_token, org_id,
            params={"from_date": from_date, "to_date": to_date},
        )

    # ── Contacts ────────────────────────────────────────────────────────

    async def get_contacts(
        self, access_token: str, org_id: str, page: int = 1
    ) -> Dict[str, Any]:
        """List contacts (customers + vendors)."""
        data = await self._api_call(
            "GET", "/contacts", access_token, org_id,
            params={"page": page, "per_page": 200},
        )
        return {
            "contacts": data.get("contacts", []),
            "page_context": data.get("page_context", {}),
        }

    # ── Sync Summary ────────────────────────────────────────────────────

    async def get_sync_summary(
        self, access_token: str, org_id: str,
    ) -> Dict[str, Any]:
        """Get a summary of the accounting data for dashboard display."""
        try:
            now = datetime.now(timezone.utc)
            fy_start = f"{now.year if now.month >= 4 else now.year - 1}-04-01"
            fy_end = f"{now.year + 1 if now.month >= 4 else now.year}-03-31"

            invoices = await self.get_invoices(access_token, org_id)
            bills = await self.get_bills(access_token, org_id)

            return {
                "total_invoices": invoices.get("page_context", {}).get("total", 0),
                "total_bills": bills.get("page_context", {}).get("total", 0),
                "fy_period": f"{fy_start} to {fy_end}",
                "last_synced": now.isoformat(),
                "status": "success",
            }
        except Exception as e:
            logger.error("Failed to get sync summary: %s", str(e))
            return {"status": "error", "error": str(e)}


# Singleton
zoho_books_service = ZohoBooksService()
