"""
Cap Table Service — manages shareholding, share transfers, allotments,
and dilution previews.

Generates form data for SH-4 (share transfer) and PAS-3 (allotment return).
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.shareholder import Shareholder, ShareTransaction, ShareType, TransactionType

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas for service inputs
# ---------------------------------------------------------------------------

class ShareholderEntry(BaseModel):
    name: str
    shares: int
    share_type: str = "equity"  # equity, preference
    face_value: float = 10.0
    paid_up_value: float = 10.0
    percentage: float = 0.0
    date_of_allotment: Optional[str] = None
    email: Optional[str] = None
    pan_number: Optional[str] = None
    is_promoter: bool = False


class TransferRequest(BaseModel):
    from_shareholder_id: int
    to_shareholder_id: int
    shares: int
    price_per_share: float = 10.0


class AllotmentEntry(BaseModel):
    shareholder_id: Optional[int] = None  # None for new shareholders
    name: Optional[str] = None  # Required if shareholder_id is None
    shares: int
    share_type: str = "equity"
    face_value: float = 10.0
    paid_up_value: float = 10.0
    price_per_share: float = 10.0
    email: Optional[str] = None
    pan_number: Optional[str] = None
    is_promoter: bool = False


# ---------------------------------------------------------------------------
# Cap Table Service
# ---------------------------------------------------------------------------

class CapTableService:
    """Service for managing company cap tables."""

    def get_cap_table(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Get current cap table for a company."""
        shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )

        total_shares = sum(s.shares for s in shareholders)

        shareholder_data = []
        for s in shareholders:
            pct = round((s.shares / total_shares * 100), 2) if total_shares > 0 else 0.0
            shareholder_data.append({
                "id": s.id,
                "name": s.name,
                "email": s.email,
                "pan_number": s.pan_number,
                "shares": s.shares,
                "share_type": s.share_type.value if s.share_type else "equity",
                "face_value": s.face_value,
                "paid_up_value": s.paid_up_value,
                "percentage": pct,
                "date_of_allotment": s.date_of_allotment.isoformat() if s.date_of_allotment else None,
                "is_promoter": s.is_promoter,
            })

        return {
            "company_id": company_id,
            "total_shares": total_shares,
            "total_shareholders": len(shareholders),
            "shareholders": shareholder_data,
            "summary": {
                "equity_shares": sum(
                    s.shares for s in shareholders
                    if s.share_type == ShareType.EQUITY
                ),
                "preference_shares": sum(
                    s.shares for s in shareholders
                    if s.share_type == ShareType.PREFERENCE
                ),
                "promoter_shares": sum(
                    s.shares for s in shareholders if s.is_promoter
                ),
                "promoter_percentage": round(
                    sum(s.shares for s in shareholders if s.is_promoter)
                    / total_shares * 100, 2
                ) if total_shares > 0 else 0.0,
            },
        }

    def add_shareholder(
        self, db: Session, company_id: int, entry: ShareholderEntry
    ) -> Dict[str, Any]:
        """Add a new shareholder to the cap table."""
        # Parse date if provided
        allotment_date = None
        if entry.date_of_allotment:
            try:
                allotment_date = datetime.strptime(
                    entry.date_of_allotment, "%Y-%m-%d"
                ).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                allotment_date = datetime.now(timezone.utc)

        # Determine share type enum
        share_type = ShareType.PREFERENCE if entry.share_type == "preference" else ShareType.EQUITY

        shareholder = Shareholder(
            company_id=company_id,
            name=entry.name,
            email=entry.email,
            pan_number=entry.pan_number,
            shares=entry.shares,
            share_type=share_type,
            face_value=entry.face_value,
            paid_up_value=entry.paid_up_value,
            percentage=entry.percentage,
            date_of_allotment=allotment_date or datetime.now(timezone.utc),
            is_promoter=entry.is_promoter,
        )
        db.add(shareholder)

        # Record allotment transaction
        transaction = ShareTransaction(
            company_id=company_id,
            transaction_type=TransactionType.ALLOTMENT,
            from_shareholder_id=None,
            to_shareholder_id=None,  # Will update after flush
            shares=entry.shares,
            price_per_share=entry.face_value,
            total_amount=entry.shares * entry.face_value,
            form_reference="PAS-3",
            transaction_date=allotment_date or datetime.now(timezone.utc),
        )
        db.add(transaction)
        db.flush()

        # Update transaction with shareholder ID
        transaction.to_shareholder_id = shareholder.id

        # Recalculate percentages for all shareholders
        self._recalculate_percentages(db, company_id)
        db.commit()
        db.refresh(shareholder)

        return {
            "message": "Shareholder added successfully",
            "shareholder": {
                "id": shareholder.id,
                "name": shareholder.name,
                "shares": shareholder.shares,
                "percentage": shareholder.percentage,
            },
        }

    def record_transfer(
        self,
        db: Session,
        company_id: int,
        from_holder_id: int,
        to_holder_id: int,
        shares: int,
        price_per_share: float = 10.0,
    ) -> Dict[str, Any]:
        """Record share transfer and generate SH-4 form data."""
        from_holder = (
            db.query(Shareholder)
            .filter(
                Shareholder.id == from_holder_id,
                Shareholder.company_id == company_id,
            )
            .first()
        )
        to_holder = (
            db.query(Shareholder)
            .filter(
                Shareholder.id == to_holder_id,
                Shareholder.company_id == company_id,
            )
            .first()
        )

        if not from_holder:
            return {"error": "Transferor shareholder not found"}
        if not to_holder:
            return {"error": "Transferee shareholder not found"}
        if from_holder.shares < shares:
            return {
                "error": (
                    f"Insufficient shares. {from_holder.name} has {from_holder.shares} shares, "
                    f"transfer requested: {shares}"
                )
            }

        # Execute transfer
        from_holder.shares -= shares
        to_holder.shares += shares
        total_amount = shares * price_per_share

        # Record transaction
        transaction = ShareTransaction(
            company_id=company_id,
            transaction_type=TransactionType.TRANSFER,
            from_shareholder_id=from_holder_id,
            to_shareholder_id=to_holder_id,
            shares=shares,
            price_per_share=price_per_share,
            total_amount=total_amount,
            form_reference="SH-4",
            transaction_date=datetime.now(timezone.utc),
        )
        db.add(transaction)

        # Recalculate percentages
        self._recalculate_percentages(db, company_id)
        db.commit()

        # Generate SH-4 form data
        sh4_data = self._generate_sh4(from_holder, to_holder, shares, price_per_share, total_amount)

        return {
            "message": "Share transfer recorded successfully",
            "transfer": {
                "from": {"id": from_holder.id, "name": from_holder.name, "remaining_shares": from_holder.shares},
                "to": {"id": to_holder.id, "name": to_holder.name, "total_shares": to_holder.shares},
                "shares_transferred": shares,
                "price_per_share": price_per_share,
                "total_amount": total_amount,
            },
            "form_data": sh4_data,
        }

    def record_allotment(
        self,
        db: Session,
        company_id: int,
        entries: List[AllotmentEntry],
    ) -> Dict[str, Any]:
        """Record new share allotment and generate PAS-3 form data."""
        allotment_results = []

        for entry in entries:
            if entry.shareholder_id:
                # Existing shareholder — add shares
                shareholder = (
                    db.query(Shareholder)
                    .filter(
                        Shareholder.id == entry.shareholder_id,
                        Shareholder.company_id == company_id,
                    )
                    .first()
                )
                if not shareholder:
                    allotment_results.append({
                        "error": f"Shareholder ID {entry.shareholder_id} not found"
                    })
                    continue

                shareholder.shares += entry.shares
            else:
                # New shareholder
                share_type = ShareType.PREFERENCE if entry.share_type == "preference" else ShareType.EQUITY
                shareholder = Shareholder(
                    company_id=company_id,
                    name=entry.name or "Unknown",
                    email=entry.email,
                    pan_number=entry.pan_number,
                    shares=entry.shares,
                    share_type=share_type,
                    face_value=entry.face_value,
                    paid_up_value=entry.paid_up_value,
                    percentage=0.0,
                    date_of_allotment=datetime.now(timezone.utc),
                    is_promoter=entry.is_promoter,
                )
                db.add(shareholder)
                db.flush()

            # Record transaction
            transaction = ShareTransaction(
                company_id=company_id,
                transaction_type=TransactionType.ALLOTMENT,
                from_shareholder_id=None,
                to_shareholder_id=shareholder.id,
                shares=entry.shares,
                price_per_share=entry.price_per_share,
                total_amount=entry.shares * entry.price_per_share,
                form_reference="PAS-3",
                transaction_date=datetime.now(timezone.utc),
            )
            db.add(transaction)

            allotment_results.append({
                "shareholder_id": shareholder.id,
                "name": shareholder.name,
                "shares_allotted": entry.shares,
                "total_shares": shareholder.shares,
            })

        # Recalculate percentages
        self._recalculate_percentages(db, company_id)
        db.commit()

        # Generate PAS-3 form data
        pas3_data = self._generate_pas3(company_id, allotment_results)

        return {
            "message": "Share allotment recorded successfully",
            "allotments": allotment_results,
            "form_data": pas3_data,
        }

    def get_dilution_preview(
        self,
        db: Session,
        company_id: int,
        new_shares: int,
        investor_name: str = "New Investor",
        price_per_share: float = 10.0,
    ) -> Dict[str, Any]:
        """Preview dilution from new investment."""
        shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )

        current_total = sum(s.shares for s in shareholders)
        post_total = current_total + new_shares
        investment_amount = new_shares * price_per_share

        # Pre-money valuation = price_per_share * current_total
        pre_money_valuation = price_per_share * current_total
        post_money_valuation = price_per_share * post_total

        current_holdings = []
        for s in shareholders:
            pre_pct = round((s.shares / current_total * 100), 2) if current_total > 0 else 0.0
            post_pct = round((s.shares / post_total * 100), 2) if post_total > 0 else 0.0
            dilution = round(pre_pct - post_pct, 2)
            current_holdings.append({
                "id": s.id,
                "name": s.name,
                "shares": s.shares,
                "pre_percentage": pre_pct,
                "post_percentage": post_pct,
                "dilution": dilution,
                "is_promoter": s.is_promoter,
            })

        investor_pct = round((new_shares / post_total * 100), 2) if post_total > 0 else 0.0

        return {
            "company_id": company_id,
            "current_total_shares": current_total,
            "new_shares": new_shares,
            "post_total_shares": post_total,
            "investor": {
                "name": investor_name,
                "shares": new_shares,
                "percentage": investor_pct,
                "investment_amount": investment_amount,
            },
            "valuation": {
                "price_per_share": price_per_share,
                "pre_money_valuation": pre_money_valuation,
                "post_money_valuation": post_money_valuation,
            },
            "existing_shareholders": current_holdings,
        }

    def export_cap_table(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Export cap table as structured data."""
        cap_table = self.get_cap_table(db, company_id)

        # Add transaction history
        transactions = (
            db.query(ShareTransaction)
            .filter(ShareTransaction.company_id == company_id)
            .order_by(ShareTransaction.transaction_date.desc())
            .all()
        )

        transaction_data = []
        for t in transactions:
            transaction_data.append({
                "id": t.id,
                "type": t.transaction_type.value if t.transaction_type else "unknown",
                "from_shareholder_id": t.from_shareholder_id,
                "to_shareholder_id": t.to_shareholder_id,
                "shares": t.shares,
                "price_per_share": t.price_per_share,
                "total_amount": t.total_amount,
                "form_reference": t.form_reference,
                "date": t.transaction_date.isoformat() if t.transaction_date else None,
            })

        cap_table["transactions"] = transaction_data
        cap_table["export_date"] = datetime.now(timezone.utc).isoformat()

        return cap_table

    def get_transactions(self, db: Session, company_id: int) -> List[Dict[str, Any]]:
        """Get transaction history for a company."""
        transactions = (
            db.query(ShareTransaction)
            .filter(ShareTransaction.company_id == company_id)
            .order_by(ShareTransaction.transaction_date.desc())
            .all()
        )

        result = []
        for t in transactions:
            from_name = None
            to_name = None
            if t.from_shareholder_id:
                from_sh = db.query(Shareholder).filter(Shareholder.id == t.from_shareholder_id).first()
                from_name = from_sh.name if from_sh else None
            if t.to_shareholder_id:
                to_sh = db.query(Shareholder).filter(Shareholder.id == t.to_shareholder_id).first()
                to_name = to_sh.name if to_sh else None

            result.append({
                "id": t.id,
                "type": t.transaction_type.value if t.transaction_type else "unknown",
                "from_shareholder": from_name,
                "to_shareholder": to_name,
                "shares": t.shares,
                "price_per_share": t.price_per_share,
                "total_amount": t.total_amount,
                "form_reference": t.form_reference,
                "date": t.transaction_date.isoformat() if t.transaction_date else None,
            })

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _recalculate_percentages(self, db: Session, company_id: int) -> None:
        """Recalculate percentage holdings for all shareholders."""
        shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )
        total_shares = sum(s.shares for s in shareholders)

        for s in shareholders:
            if total_shares > 0:
                s.percentage = round((s.shares / total_shares * 100), 2)
            else:
                s.percentage = 0.0

            # Remove shareholders with 0 shares (optional cleanup)
            # We keep them in the database for audit trail

    def _generate_sh4(
        self,
        from_holder: Shareholder,
        to_holder: Shareholder,
        shares: int,
        price_per_share: float,
        total_amount: float,
    ) -> Dict[str, Any]:
        """Generate SH-4 (Share Transfer Form) data."""
        return {
            "form_name": "SH-4",
            "title": "Securities Transfer Form",
            "fields": {
                "transferor": {
                    "name": from_holder.name,
                    "pan": from_holder.pan_number or "",
                    "shares_before": from_holder.shares + shares,  # Before transfer
                    "shares_transferred": shares,
                    "shares_after": from_holder.shares,
                },
                "transferee": {
                    "name": to_holder.name,
                    "pan": to_holder.pan_number or "",
                    "shares_before": to_holder.shares - shares,  # Before transfer
                    "shares_received": shares,
                    "shares_after": to_holder.shares,
                },
                "share_details": {
                    "share_type": "Equity",
                    "face_value": from_holder.face_value,
                    "number_of_shares": shares,
                    "consideration": total_amount,
                    "price_per_share": price_per_share,
                },
            },
            "stamp_duty": {
                "note": "Stamp duty on share transfer is 0.015% of consideration or Rs 200, whichever is higher.",
                "estimated_duty": max(200, int(total_amount * 0.00015)),
            },
        }

    def _generate_pas3(
        self,
        company_id: int,
        allotment_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate PAS-3 (Return of Allotment) form data."""
        total_shares_allotted = sum(
            a.get("shares_allotted", 0) for a in allotment_results if "error" not in a
        )

        return {
            "form_name": "PAS-3",
            "title": "Return of Allotment",
            "fields": {
                "company_id": company_id,
                "total_shares_allotted": total_shares_allotted,
                "allottees": [
                    {
                        "name": a.get("name", ""),
                        "shares": a.get("shares_allotted", 0),
                    }
                    for a in allotment_results
                    if "error" not in a
                ],
            },
            "filing_deadline": "Within 15 days of allotment",
            "fee": 200,
            "note": (
                "PAS-3 must be filed with the Registrar of Companies within "
                "15 days of the allotment of shares."
            ),
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
cap_table_service = CapTableService()
