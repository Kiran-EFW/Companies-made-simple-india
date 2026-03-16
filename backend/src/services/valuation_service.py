"""Valuation Service — NAV and simplified DCF calculations for ESOP FMV.

Rule 11UA of the Income Tax Act requires FMV determination for share
allotment at premium. This service provides NAV (Net Asset Value) and
simplified DCF (Discounted Cash Flow) methods.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.valuation import Valuation, ValuationMethod, ValuationStatus
from src.models.shareholder import Shareholder

logger = logging.getLogger(__name__)


class ValuationService:
    """Calculate and persist company valuations."""

    def calculate_nav(
        self,
        db: Session,
        company_id: int,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate FMV using Net Asset Value method.

        FMV = (Total Assets - Total Liabilities) / Total Shares

        Args:
            data: {total_assets, total_liabilities, total_shares (optional)}
        """
        total_assets = data.get("total_assets", 0)
        total_liabilities = data.get("total_liabilities", 0)
        total_shares = data.get("total_shares")

        if not total_shares:
            shareholders = (
                db.query(Shareholder)
                .filter(Shareholder.company_id == company_id)
                .all()
            )
            total_shares = sum(s.shares for s in shareholders) if shareholders else 0

        if total_shares <= 0:
            return {"error": "Total shares must be greater than zero"}

        net_assets = total_assets - total_liabilities
        fmv_per_share = net_assets / total_shares

        return {
            "method": "nav",
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_assets": net_assets,
            "total_shares": total_shares,
            "fair_market_value": round(fmv_per_share, 2),
            "total_enterprise_value": round(net_assets, 2),
        }

    def calculate_dcf(
        self,
        db: Session,
        company_id: int,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate FMV using simplified DCF method.

        Projects revenue for 5 years, applies a profit margin, discounts
        to present value, and divides by total shares.

        Args:
            data: {current_revenue, growth_rate, profit_margin, discount_rate,
                   projection_years (default 5), total_shares (optional)}
        """
        current_revenue = data.get("current_revenue", 0)
        growth_rate = data.get("growth_rate", 20) / 100
        profit_margin = data.get("profit_margin", 15) / 100
        discount_rate = data.get("discount_rate", 15) / 100
        years = data.get("projection_years", 5)
        total_shares = data.get("total_shares")

        if not total_shares:
            shareholders = (
                db.query(Shareholder)
                .filter(Shareholder.company_id == company_id)
                .all()
            )
            total_shares = sum(s.shares for s in shareholders) if shareholders else 0

        if total_shares <= 0:
            return {"error": "Total shares must be greater than zero"}
        if current_revenue <= 0:
            return {"error": "Current revenue must be greater than zero"}

        # Project cash flows
        projections = []
        total_pv = 0.0
        revenue = current_revenue

        for year in range(1, years + 1):
            revenue = revenue * (1 + growth_rate)
            cash_flow = revenue * profit_margin
            discount_factor = 1 / ((1 + discount_rate) ** year)
            pv = cash_flow * discount_factor
            total_pv += pv
            projections.append({
                "year": year,
                "revenue": round(revenue, 2),
                "cash_flow": round(cash_flow, 2),
                "discount_factor": round(discount_factor, 4),
                "present_value": round(pv, 2),
            })

        # Terminal value (Gordon Growth Model)
        terminal_growth = 0.03  # 3% long-term growth
        last_cf = projections[-1]["cash_flow"]
        terminal_value = last_cf * (1 + terminal_growth) / (discount_rate - terminal_growth)
        terminal_pv = terminal_value / ((1 + discount_rate) ** years)
        enterprise_value = total_pv + terminal_pv

        fmv_per_share = enterprise_value / total_shares

        return {
            "method": "dcf",
            "current_revenue": current_revenue,
            "growth_rate": data.get("growth_rate", 20),
            "profit_margin": data.get("profit_margin", 15),
            "discount_rate": data.get("discount_rate", 15),
            "projection_years": years,
            "total_shares": total_shares,
            "projections": projections,
            "terminal_value": round(terminal_value, 2),
            "terminal_pv": round(terminal_pv, 2),
            "total_dcf_value": round(total_pv, 2),
            "total_enterprise_value": round(enterprise_value, 2),
            "fair_market_value": round(fmv_per_share, 2),
        }

    def create_valuation(
        self,
        db: Session,
        company_id: int,
        user_id: int,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Persist a valuation record."""
        method = ValuationMethod(data.get("method", "nav"))

        # Calculate based on method
        if method == ValuationMethod.NAV:
            result = self.calculate_nav(db, company_id, data)
        else:
            result = self.calculate_dcf(db, company_id, data)

        if "error" in result:
            return result

        status = ValuationStatus(data.get("status", "draft"))

        valuation = Valuation(
            company_id=company_id,
            method=method,
            fair_market_value=result["fair_market_value"],
            total_enterprise_value=result["total_enterprise_value"],
            report_data=result,
            status=status,
            prepared_by=user_id,
            notes=data.get("notes"),
        )
        db.add(valuation)
        db.commit()
        db.refresh(valuation)

        return self._serialize(valuation)

    def get_latest_valuation(
        self, db: Session, company_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent finalized valuation for a company."""
        valuation = (
            db.query(Valuation)
            .filter(
                Valuation.company_id == company_id,
                Valuation.status == ValuationStatus.FINALIZED,
            )
            .order_by(Valuation.created_at.desc())
            .first()
        )
        if not valuation:
            return None
        return self._serialize(valuation)

    def list_valuations(
        self, db: Session, company_id: int
    ) -> List[Dict[str, Any]]:
        """List all valuations for a company."""
        valuations = (
            db.query(Valuation)
            .filter(Valuation.company_id == company_id)
            .order_by(Valuation.created_at.desc())
            .all()
        )
        return [self._serialize(v) for v in valuations]

    def get_valuation(
        self, db: Session, valuation_id: int, company_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a single valuation."""
        valuation = (
            db.query(Valuation)
            .filter(Valuation.id == valuation_id, Valuation.company_id == company_id)
            .first()
        )
        if not valuation:
            return None
        return self._serialize(valuation)

    def _serialize(self, v: Valuation) -> Dict[str, Any]:
        return {
            "id": v.id,
            "company_id": v.company_id,
            "method": v.method.value if v.method else None,
            "valuation_date": v.valuation_date.isoformat() if v.valuation_date else None,
            "fair_market_value": v.fair_market_value,
            "total_enterprise_value": v.total_enterprise_value,
            "report_data": v.report_data,
            "status": v.status.value if v.status else None,
            "prepared_by": v.prepared_by,
            "notes": v.notes,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }


# Singleton
valuation_service = ValuationService()
