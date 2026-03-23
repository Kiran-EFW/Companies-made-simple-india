"""
Cap Table Service — manages shareholding, share transfers, allotments,
and dilution previews.

Generates form data for SH-4 (share transfer) and PAS-3 (allotment return).
"""

import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.shareholder import Shareholder, ShareTransaction, ShareType, TransactionType
from src.models.company import Company, EntityType

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
# Pydantic schemas for round / exit simulation
# ---------------------------------------------------------------------------

class InvestorInput(BaseModel):
    name: str
    amount: float


class SimulateRoundRequest(BaseModel):
    pre_money_valuation: float
    investment_amount: float
    esop_pool_pct: float = 0.0
    investors: List[InvestorInput] = []
    round_name: str = "Seed Round"


class SimulateExitRequest(BaseModel):
    exit_valuation: float
    liquidation_preference: float = 1.0
    participating_preferred: bool = False


class SaveScenarioRequest(BaseModel):
    scenario_name: str
    scenario_type: str  # "round" or "exit"
    scenario_data: Dict[str, Any]


# ---------------------------------------------------------------------------
# Cap Table Service
# ---------------------------------------------------------------------------

class CapTableService:
    """Service for managing company cap tables."""

    def get_cap_table(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Get current cap table for a company."""
        # Fetch company to determine entity type
        company = db.query(Company).filter(Company.id == company_id).first()
        entity_type = company.entity_type if company else None

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

        # ESOP pool summary (lazy import to avoid circular deps)
        esop_pool = None
        try:
            from src.services.esop_service import esop_service
            esop_pool = esop_service.get_esop_pool_summary(db, company_id)
        except Exception:
            pass

        return {
            "company_id": company_id,
            "total_shares": total_shares,
            "total_shareholders": len(shareholders),
            "shareholders": shareholder_data,
            "esop_pool": esop_pool,
            "entity_context": self._get_entity_context(entity_type),
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
        # OPC guard: One Person Company can only have 1 shareholder
        company = db.query(Company).filter(Company.id == company_id).first()
        if company and company.entity_type == EntityType.OPC:
            existing_count = db.query(Shareholder).filter(
                Shareholder.company_id == company_id,
                Shareholder.shares > 0,
            ).count()
            if existing_count >= 1:
                return {"error": "OPC (One Person Company) can only have one shareholder. Transfer existing shares first or convert to Private Limited."}

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

        # Sync to Register of Members
        self._sync_register_entry(db, company_id, "MEMBERS", {
            "shareholder_name": entry.name,
            "shares": entry.shares,
            "share_type": share_type.value,
            "face_value": entry.face_value,
            "date_of_allotment": (allotment_date or datetime.now(timezone.utc)).isoformat(),
            "email": entry.email,
            "pan_number": entry.pan_number,
            "is_promoter": entry.is_promoter,
            "action": "initial_allotment",
        }, notes=f"New shareholder: {entry.name} — {entry.shares} shares")

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
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
        company = db.query(Company).filter(Company.id == company_id).first()
        entity_note = None

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

        # OPC note
        if company and company.entity_type == EntityType.OPC:
            entity_note = "Note: Share transfer in OPC may require filing Form INC-4 with ROC for change in member details."

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

        # Sync to Register of Share Transfers
        self._sync_register_entry(db, company_id, "SHARE_TRANSFERS", {
            "transferor": from_holder.name,
            "transferee": to_holder.name,
            "shares_transferred": shares,
            "price_per_share": price_per_share,
            "total_consideration": total_amount,
            "share_type": from_holder.share_type.value if from_holder.share_type else "equity",
            "transfer_date": datetime.now(timezone.utc).isoformat(),
            "form_reference": "SH-4",
        }, notes=f"Transfer: {from_holder.name} \u2192 {to_holder.name} \u2014 {shares} shares")

        # Also update Register of Members
        self._sync_register_entry(db, company_id, "MEMBERS", {
            "shareholder_name": from_holder.name,
            "shares_after": from_holder.shares,
            "action": "transfer_out",
            "counterparty": to_holder.name,
            "shares_transferred": shares,
            "transfer_date": datetime.now(timezone.utc).isoformat(),
        }, notes=f"Transfer out: {shares} shares to {to_holder.name}")

        self._sync_register_entry(db, company_id, "MEMBERS", {
            "shareholder_name": to_holder.name,
            "shares_after": to_holder.shares,
            "action": "transfer_in",
            "counterparty": from_holder.name,
            "shares_received": shares,
            "transfer_date": datetime.now(timezone.utc).isoformat(),
        }, notes=f"Transfer in: {shares} shares from {from_holder.name}")

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        # Generate SH-4 form data
        sh4_data = self._generate_sh4(from_holder, to_holder, shares, price_per_share, total_amount)

        result = {
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
        if entity_note:
            result["entity_note"] = entity_note
        return result

    def record_allotment(
        self,
        db: Session,
        company_id: int,
        entries: List[AllotmentEntry],
    ) -> Dict[str, Any]:
        """Record new share allotment and generate PAS-3 form data."""
        # OPC guard: block adding new shareholders
        company = db.query(Company).filter(Company.id == company_id).first()
        if company and company.entity_type == EntityType.OPC:
            existing_shareholders = db.query(Shareholder).filter(
                Shareholder.company_id == company_id,
                Shareholder.shares > 0,
            ).all()
            existing_ids = {s.id for s in existing_shareholders}
            for entry in entries:
                if entry.shareholder_id is None and len(existing_shareholders) >= 1:
                    return {"error": "OPC can only have one shareholder. Cannot allot shares to a new shareholder."}
                if entry.shareholder_id and entry.shareholder_id not in existing_ids and len(existing_shareholders) >= 1:
                    return {"error": "OPC can only have one shareholder. Cannot allot shares to a new shareholder."}

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

        # Sync to Register of Members for each allottee
        for result_entry in allotment_results:
            if "error" not in result_entry:
                self._sync_register_entry(db, company_id, "MEMBERS", {
                    "shareholder_name": result_entry.get("name", ""),
                    "shares_allotted": result_entry.get("shares_allotted", 0),
                    "total_shares_after": result_entry.get("total_shares", 0),
                    "action": "allotment",
                    "allotment_date": datetime.now(timezone.utc).isoformat(),
                    "form_reference": "PAS-3",
                }, notes=f"Allotment: {result_entry.get('name', '')} — {result_entry.get('shares_allotted', 0)} shares")

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

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
    # Round simulation & exit scenarios
    # ------------------------------------------------------------------

    def simulate_round(
        self,
        db: Session,
        company_id: int,
        pre_money_valuation: float,
        investment_amount: float,
        esop_pool_pct: float = 0.0,
        investors: Optional[List[Dict[str, Any]]] = None,
        round_name: str = "Seed Round",
    ) -> Dict[str, Any]:
        """
        Simulate a funding round showing dilution, ESOP pool expansion,
        and post-money cap table without persisting anything.
        """
        if investors is None:
            investors = []

        # 1. Fetch current shareholders
        shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )
        current_total_shares = sum(s.shares for s in shareholders)

        if current_total_shares == 0:
            return {"error": "No existing shareholders found for this company"}

        # 2. Price per share from pre-money valuation
        price_per_share = pre_money_valuation / current_total_shares

        # 3. ESOP pool expansion (pre-round)
        esop_shares = 0
        if esop_pool_pct > 0:
            esop_shares = int(
                current_total_shares * esop_pool_pct / (100 - esop_pool_pct)
            )
        total_after_esop = current_total_shares + esop_shares

        # 4. Before-round snapshot
        before_round = []
        for s in shareholders:
            pct = round(s.shares / current_total_shares * 100, 2)
            before_round.append({
                "name": s.name,
                "shares": s.shares,
                "percentage": pct,
            })

        # 5. Investor shares
        investor_details = []
        total_investor_shares = 0
        for inv in investors:
            inv_shares = int(inv["amount"] / price_per_share)
            total_investor_shares += inv_shares
            investor_details.append({
                "name": inv["name"],
                "investment": inv["amount"],
                "shares": inv_shares,
                "percentage": 0.0,  # filled below
            })

        # 6. Post-money totals
        post_total_shares = total_after_esop + total_investor_shares
        post_money_valuation = pre_money_valuation + investment_amount

        # 7. After-round table
        after_round = []
        for s in shareholders:
            pre_pct = round(s.shares / current_total_shares * 100, 2)
            post_pct = round(s.shares / post_total_shares * 100, 2) if post_total_shares > 0 else 0.0
            dilution_pct = round(pre_pct - post_pct, 2)
            after_round.append({
                "name": s.name,
                "shares": s.shares,
                "percentage": post_pct,
                "dilution_pct": dilution_pct,
            })

        # ESOP row
        if esop_shares > 0:
            esop_post_pct = round(esop_shares / post_total_shares * 100, 2) if post_total_shares > 0 else 0.0
            after_round.append({
                "name": "ESOP Pool",
                "shares": esop_shares,
                "percentage": esop_post_pct,
                "dilution_pct": 0.0,
            })

        # Investor rows
        for inv_detail in investor_details:
            inv_pct = round(inv_detail["shares"] / post_total_shares * 100, 2) if post_total_shares > 0 else 0.0
            inv_detail["percentage"] = inv_pct
            after_round.append({
                "name": inv_detail["name"],
                "shares": inv_detail["shares"],
                "percentage": inv_pct,
                "dilution_pct": 0.0,
            })

        # ESOP pool summary
        esop_pool_info = {
            "shares": esop_shares,
            "percentage_post": round(esop_shares / post_total_shares * 100, 2) if post_total_shares > 0 and esop_shares > 0 else 0.0,
        }

        return {
            "round_name": round_name,
            "pre_money_valuation": pre_money_valuation,
            "post_money_valuation": post_money_valuation,
            "investment_amount": investment_amount,
            "price_per_share": round(price_per_share, 4),
            "esop_pool": esop_pool_info,
            "before_round": before_round,
            "after_round": after_round,
            "investors": investor_details,
            "summary": {
                "total_shares_before": current_total_shares,
                "total_shares_after": post_total_shares,
                "new_shares_issued": esop_shares + total_investor_shares,
            },
        }

    def simulate_exit(
        self,
        db: Session,
        company_id: int,
        exit_valuation: float,
        liquidation_preference: float = 1.0,
        participating_preferred: bool = False,
    ) -> Dict[str, Any]:
        """
        Simulate an exit / liquidity event and compute per-shareholder payouts.
        """
        shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )
        total_shares = sum(s.shares for s in shareholders)

        if total_shares == 0:
            return {"error": "No existing shareholders found for this company"}

        value_per_share = exit_valuation / total_shares

        payouts = []
        total_distributed = 0.0
        for s in shareholders:
            payout_amount = round(s.shares * value_per_share, 2)
            cost_basis = s.face_value * s.shares
            roi_multiple = round(payout_amount / cost_basis, 2) if cost_basis > 0 else 0.0
            pct = round(s.shares / total_shares * 100, 2)

            payouts.append({
                "name": s.name,
                "shares": s.shares,
                "percentage": pct,
                "payout_amount": payout_amount,
                "roi_multiple": roi_multiple,
                "is_promoter": s.is_promoter,
            })
            total_distributed += payout_amount

        return {
            "exit_valuation": exit_valuation,
            "value_per_share": round(value_per_share, 4),
            "payouts": payouts,
            "summary": {
                "total_distributed": round(total_distributed, 2),
                "remaining": round(exit_valuation - total_distributed, 2),
            },
        }

    def save_scenario(
        self,
        scenario_name: str,
        scenario_type: str,
        scenario_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Wrap scenario data with a generated UUID and timestamp.
        Pure in-memory — nothing persisted to the database.
        """
        return {
            "id": str(uuid.uuid4()),
            "scenario_name": scenario_name,
            "scenario_type": scenario_type,
            "scenario_data": scenario_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Exit waterfall & share certificates
    # ------------------------------------------------------------------

    def simulate_exit_waterfall(
        self,
        db: Session,
        company_id: int,
        exit_valuation: float,
        liquidation_preferences: Optional[List[Dict[str, Any]]] = None,
        participating_preferred: bool = False,
    ) -> Dict[str, Any]:
        """
        Full waterfall analysis: pay liquidation preferences first,
        then distribute remaining pro-rata among common holders (and
        optionally participating preferred).

        liquidation_preferences format:
        [{"shareholder_id": 5, "multiple": 1.5, "invested_amount": 5000000}, ...]
        """
        shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )
        total_shares = sum(s.shares for s in shareholders)

        if total_shares == 0:
            return {"error": "No existing shareholders found for this company"}

        if liquidation_preferences is None:
            liquidation_preferences = []

        # Build lookup of liq pref shareholders
        lp_lookup: Dict[int, Dict[str, Any]] = {}
        for lp in liquidation_preferences:
            lp_lookup[lp["shareholder_id"]] = {
                "multiple": lp.get("multiple", 1.0),
                "invested_amount": lp.get("invested_amount", 0),
            }

        waterfall_steps = []
        remaining = exit_valuation

        # Step 1: Pay liquidation preferences
        lp_payouts: Dict[int, float] = {}
        total_lp_payout = 0.0
        for lp in liquidation_preferences:
            sh_id = lp["shareholder_id"]
            pref_amount = round(lp.get("invested_amount", 0) * lp.get("multiple", 1.0), 2)
            actual_payout = min(pref_amount, remaining)
            lp_payouts[sh_id] = actual_payout
            remaining -= actual_payout
            total_lp_payout += actual_payout

        if total_lp_payout > 0:
            waterfall_steps.append({
                "step": "Liquidation Preferences",
                "amount": total_lp_payout,
                "remaining_after": round(remaining, 2),
                "details": [
                    {
                        "shareholder_id": sh_id,
                        "name": next(
                            (s.name for s in shareholders if s.id == sh_id), "Unknown"
                        ),
                        "payout": payout,
                    }
                    for sh_id, payout in lp_payouts.items()
                ],
            })

        # Step 2: Pro-rata distribution of remaining
        # If participating preferred, all holders share remaining
        # If non-participating, lp holders already got their pref — they don't
        #   participate further unless their pro-rata would exceed pref
        payouts: Dict[int, float] = {}
        pro_rata_details = []

        if participating_preferred:
            # All shareholders share remaining pro-rata
            for s in shareholders:
                pct = s.shares / total_shares if total_shares > 0 else 0
                share_of_remaining = round(remaining * pct, 2)
                payouts[s.id] = lp_payouts.get(s.id, 0) + share_of_remaining
                pro_rata_details.append({
                    "shareholder_id": s.id,
                    "name": s.name,
                    "payout": share_of_remaining,
                })
        else:
            # Non-participating: lp holders take GREATER of (pref, pro-rata)
            for s in shareholders:
                pct = s.shares / total_shares if total_shares > 0 else 0
                full_pro_rata = round(exit_valuation * pct, 2)
                lp_amount = lp_payouts.get(s.id, 0)
                if s.id in lp_lookup:
                    # Investor takes greater of pref or pro-rata
                    payouts[s.id] = max(lp_amount, full_pro_rata)
                else:
                    # Common holder gets pro-rata of remaining
                    share_of_remaining = round(remaining * pct, 2)
                    payouts[s.id] = share_of_remaining
                pro_rata_details.append({
                    "shareholder_id": s.id,
                    "name": s.name,
                    "payout": payouts[s.id] - lp_payouts.get(s.id, 0),
                })

        waterfall_steps.append({
            "step": "Pro-Rata Distribution" + (" (Participating)" if participating_preferred else ""),
            "amount": round(remaining, 2),
            "remaining_after": 0,
            "details": pro_rata_details,
        })

        # Build final shareholder payouts
        final_payouts = []
        total_distributed = 0.0
        for s in shareholders:
            payout_amount = round(payouts.get(s.id, 0), 2)
            cost_basis = s.face_value * s.shares
            roi_multiple = round(payout_amount / cost_basis, 2) if cost_basis > 0 else 0.0
            pct = round(s.shares / total_shares * 100, 2)

            final_payouts.append({
                "shareholder_id": s.id,
                "name": s.name,
                "shares": s.shares,
                "percentage": pct,
                "lp_payout": lp_payouts.get(s.id, 0),
                "pro_rata_payout": round(payout_amount - lp_payouts.get(s.id, 0), 2),
                "total_payout": payout_amount,
                "roi_multiple": roi_multiple,
                "is_promoter": s.is_promoter,
            })
            total_distributed += payout_amount

        return {
            "exit_valuation": exit_valuation,
            "participating_preferred": participating_preferred,
            "waterfall_steps": waterfall_steps,
            "payouts": final_payouts,
            "summary": {
                "total_distributed": round(total_distributed, 2),
                "remaining": round(exit_valuation - total_distributed, 2),
                "total_lp_amount": total_lp_payout,
            },
        }

    def generate_share_certificate(
        self,
        db: Session,
        company_id: int,
        shareholder_id: int,
    ) -> Dict[str, Any]:
        """Generate HTML share certificate for a shareholder."""
        shareholder = (
            db.query(Shareholder)
            .filter(
                Shareholder.id == shareholder_id,
                Shareholder.company_id == company_id,
            )
            .first()
        )
        if not shareholder:
            return {"error": "Shareholder not found"}

        # Fetch company name
        try:
            company = db.query(Company).filter(Company.id == company_id).first()
            company_name = company.company_name if company else f"Company #{company_id}"
            cin = getattr(company, "cin", "") or ""
        except Exception:
            company_name = f"Company #{company_id}"
            cin = ""

        cert_number = f"SC-{company_id:04d}-{shareholder_id:06d}"
        allotment_date = (
            shareholder.date_of_allotment.strftime("%d %B %Y")
            if shareholder.date_of_allotment
            else "N/A"
        )
        share_type = shareholder.share_type.value if shareholder.share_type else "equity"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Share Certificate {cert_number}</title>
<style>
  @page {{ size: landscape; margin: 20mm; }}
  body {{ font-family: 'Georgia', serif; margin: 0; padding: 40px; background: #fff; color: #1a1a1a; }}
  .certificate {{ border: 3px double #333; padding: 40px 60px; max-width: 900px; margin: auto; position: relative; }}
  .certificate::before {{ content: ''; position: absolute; inset: 8px; border: 1px solid #999; pointer-events: none; }}
  .header {{ text-align: center; margin-bottom: 30px; }}
  .company-name {{ font-size: 28px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; }}
  .cin {{ font-size: 11px; color: #666; margin-top: 4px; }}
  .cert-title {{ font-size: 18px; text-transform: uppercase; letter-spacing: 3px; margin: 20px 0; color: #555; }}
  .cert-number {{ font-size: 13px; color: #888; }}
  .body {{ text-align: center; margin: 30px 0; line-height: 1.8; font-size: 15px; }}
  .highlight {{ font-size: 20px; font-weight: bold; }}
  .details-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 40px; margin: 30px auto; max-width: 600px; text-align: left; font-size: 14px; }}
  .details-grid dt {{ color: #666; }}
  .details-grid dd {{ font-weight: 600; margin: 0 0 10px 0; }}
  .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #888; }}
  .signatures {{ display: flex; justify-content: space-between; margin-top: 50px; }}
  .sig-block {{ text-align: center; width: 200px; }}
  .sig-line {{ border-top: 1px solid #333; margin-top: 60px; padding-top: 5px; font-size: 12px; }}
</style></head>
<body>
<div class="certificate">
  <div class="header">
    <div class="company-name">{company_name}</div>
    {f'<div class="cin">CIN: {cin}</div>' if cin else ''}
    <div class="cert-title">Share Certificate</div>
    <div class="cert-number">Certificate No. {cert_number}</div>
  </div>
  <div class="body">
    <p>This is to certify that</p>
    <p class="highlight">{shareholder.name}</p>
    <p>is the registered holder of</p>
    <p class="highlight">{shareholder.shares:,} {share_type.title()} Shares</p>
    <p>of <strong>{company_name}</strong></p>
  </div>
  <dl class="details-grid">
    <dt>Face Value per Share</dt><dd>Rs {shareholder.face_value}</dd>
    <dt>Paid-up Value per Share</dt><dd>Rs {shareholder.paid_up_value}</dd>
    <dt>Date of Allotment</dt><dd>{allotment_date}</dd>
    <dt>Share Type</dt><dd>{share_type.title()}</dd>
    {f'<dt>PAN</dt><dd>{shareholder.pan_number}</dd>' if shareholder.pan_number else ''}
    {f'<dt>Email</dt><dd>{shareholder.email}</dd>' if shareholder.email else ''}
  </dl>
  <div class="signatures">
    <div class="sig-block"><div class="sig-line">Director</div></div>
    <div class="sig-block"><div class="sig-line">Company Secretary</div></div>
  </div>
  <div class="footer">
    Generated on {datetime.now(timezone.utc).strftime('%d %B %Y')} | Companies Act, 2013 — Rule 5(2)
  </div>
</div>
</body></html>"""

        return {
            "certificate_number": cert_number,
            "shareholder_id": shareholder_id,
            "shareholder_name": shareholder.name,
            "shares": shareholder.shares,
            "share_type": share_type,
            "company_name": company_name,
            "html": html,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_entity_context(self, entity_type) -> Dict[str, Any]:
        """Return entity-type specific labels and restrictions for the frontend."""
        if entity_type is None:
            return {"labels": {"shareholder": "Shareholder", "shares": "Shares", "share_capital": "Share Capital"}, "restrictions": {}}

        # Default labels for Companies Act entities
        labels = {
            "shareholder": "Shareholder",
            "shares": "Shares",
            "share_capital": "Share Capital",
            "allotment": "Share Allotment",
            "transfer": "Share Transfer",
            "face_value": "Face Value",
        }
        restrictions = {}

        if entity_type == EntityType.LLP:
            labels = {
                "shareholder": "Partner",
                "shares": "Capital Contribution",
                "share_capital": "Total Capital",
                "allotment": "Capital Contribution",
                "transfer": "Capital Transfer",
                "face_value": "Contribution Amount",
            }
            restrictions["no_share_certificates"] = True
            restrictions["no_esop"] = True
        elif entity_type == EntityType.OPC:
            labels["shareholder"] = "Member"
            restrictions["max_shareholders"] = 1
            restrictions["no_share_transfer_without_inc4"] = True
        elif entity_type == EntityType.SOLE_PROPRIETORSHIP:
            labels = {
                "shareholder": "Proprietor",
                "shares": "Capital",
                "share_capital": "Proprietor Capital",
                "allotment": "Capital Infusion",
                "transfer": "Not Applicable",
                "face_value": "Capital Amount",
            }
            restrictions["max_shareholders"] = 1
            restrictions["no_share_certificates"] = True
            restrictions["no_share_transfer"] = True
            restrictions["no_esop"] = True
        elif entity_type == EntityType.PARTNERSHIP:
            labels = {
                "shareholder": "Partner",
                "shares": "Capital Contribution",
                "share_capital": "Partner Capital",
                "allotment": "Capital Contribution",
                "transfer": "Partnership Interest Transfer",
                "face_value": "Contribution Amount",
            }
            restrictions["no_share_certificates"] = True
            restrictions["no_esop"] = True
        elif entity_type == EntityType.SECTION_8:
            restrictions["no_dividend"] = True
            restrictions["profit_applied_to_objects"] = True
            restrictions["transfer_requires_nclat"] = True
        elif entity_type == EntityType.PUBLIC_LIMITED:
            restrictions["min_shareholders"] = 7
            restrictions["min_directors"] = 3

        return {"labels": labels, "restrictions": restrictions, "entity_type": entity_type.value if entity_type else None}

    def _sync_register_entry(
        self,
        db: Session,
        company_id: int,
        register_type: str,
        entry_data: Dict[str, Any],
        notes: str = "",
    ) -> None:
        """Auto-create a statutory register entry for cap table changes."""
        from src.models.statutory_register import StatutoryRegister, RegisterEntry

        # Ensure the register exists
        register = (
            db.query(StatutoryRegister)
            .filter(
                StatutoryRegister.company_id == company_id,
                StatutoryRegister.register_type == register_type,
            )
            .first()
        )
        if not register:
            register = StatutoryRegister(
                company_id=company_id,
                register_type=register_type,
            )
            db.add(register)
            db.flush()

        # Get next entry number
        max_entry = (
            db.query(RegisterEntry.entry_number)
            .filter(RegisterEntry.register_id == register.id)
            .order_by(RegisterEntry.entry_number.desc())
            .first()
        )
        next_num = (max_entry[0] + 1) if max_entry else 1

        entry = RegisterEntry(
            register_id=register.id,
            company_id=company_id,
            entry_number=next_num,
            entry_date=datetime.now(timezone.utc),
            data=entry_data,
            notes=notes,
            created_by=0,  # System-generated (no user context in service)
        )
        db.add(entry)

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
