"""SLA (Service Level Agreement) tracking service.

Defines target durations for each status transition and provides
methods to detect breaches and compute aggregate compliance metrics.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.company import Company, CompanyStatus
from src.models.admin_log import AdminLog

logger = logging.getLogger(__name__)


# ── SLA Targets ──────────────────────────────────────────────────────────────
# Maps status transitions to their maximum allowed duration.

SLA_TARGETS: Dict[str, timedelta] = {
    "documents_uploaded_to_documents_verified": timedelta(hours=24),
    "documents_verified_to_name_reserved": timedelta(hours=48),
    "name_reserved_to_filing_drafted": timedelta(hours=72),
    "filing_drafted_to_filing_under_review": timedelta(hours=24),
    "filing_under_review_to_filing_submitted": timedelta(hours=48),
    "filing_submitted_to_mca_processing": timedelta(hours=24),
    "mca_processing_to_incorporated": timedelta(hours=168),  # 7 days (external)
    "incorporated_to_bank_account_pending": timedelta(hours=24),
    "payment_completed_to_documents_pending": timedelta(hours=4),
}

# Ordered pipeline stages for SLA tracking
_PIPELINE_ORDER = [
    CompanyStatus.DRAFT,
    CompanyStatus.ENTITY_SELECTED,
    CompanyStatus.PAYMENT_PENDING,
    CompanyStatus.PAYMENT_COMPLETED,
    CompanyStatus.DOCUMENTS_PENDING,
    CompanyStatus.DOCUMENTS_UPLOADED,
    CompanyStatus.DOCUMENTS_VERIFIED,
    CompanyStatus.NAME_PENDING,
    CompanyStatus.NAME_RESERVED,
    CompanyStatus.DSC_IN_PROGRESS,
    CompanyStatus.DSC_OBTAINED,
    CompanyStatus.FILING_DRAFTED,
    CompanyStatus.FILING_UNDER_REVIEW,
    CompanyStatus.FILING_SUBMITTED,
    CompanyStatus.MCA_PROCESSING,
    CompanyStatus.INCORPORATED,
    CompanyStatus.BANK_ACCOUNT_PENDING,
    CompanyStatus.BANK_ACCOUNT_OPENED,
    CompanyStatus.INC20A_PENDING,
    CompanyStatus.FULLY_SETUP,
]


class SLAService:
    """SLA breach detection and metrics computation."""

    def check_sla_breach(
        self, db: Session, company: Company
    ) -> Optional[Dict[str, Any]]:
        """Check if a company has any SLA breach based on its current stage.

        Compares time spent in the current status against the SLA target
        for the transition *into* that status.

        Returns:
            dict with breach info if breached, else None.
        """
        if not company.updated_at:
            return None

        current_status = company.status
        if not current_status:
            return None

        # Find the previous status in the pipeline to build the transition key
        try:
            idx = _PIPELINE_ORDER.index(current_status)
        except ValueError:
            return None

        if idx == 0:
            return None

        prev_status = _PIPELINE_ORDER[idx - 1]
        transition_key = f"{prev_status.value}_to_{current_status.value}"

        target = SLA_TARGETS.get(transition_key)
        if not target:
            return None

        now = datetime.now(timezone.utc)
        # updated_at reflects when the status was last set
        time_in_status = now - company.updated_at.replace(tzinfo=timezone.utc)

        if time_in_status > target:
            return {
                "company_id": company.id,
                "company_status": current_status.value,
                "breach_stage": transition_key,
                "expected_hours": target.total_seconds() / 3600,
                "actual_hours": round(time_in_status.total_seconds() / 3600, 2),
                "breached_at": (company.updated_at + target).isoformat(),
            }

        return None

    def get_sla_breaches(self, db: Session) -> List[Dict[str, Any]]:
        """Return all companies currently in SLA breach.

        Queries active companies (not DRAFT, FULLY_SETUP, or terminal states)
        and checks each for breach.
        """
        # Only check companies in active pipeline stages
        active_statuses = [
            s for s in CompanyStatus
            if s not in (
                CompanyStatus.DRAFT,
                CompanyStatus.FULLY_SETUP,
                CompanyStatus.NAME_REJECTED,
                CompanyStatus.MCA_QUERY,
            )
        ]

        companies = (
            db.query(Company)
            .filter(Company.status.in_(active_statuses))
            .all()
        )

        breaches = []
        for company in companies:
            breach = self.check_sla_breach(db, company)
            if breach:
                breaches.append(breach)

        return breaches

    def get_sla_metrics(self, db: Session) -> Dict[str, Any]:
        """Compute aggregate SLA compliance statistics.

        Returns:
            dict with total_companies, on_time_percentage, avg_processing_hours,
            breaches_count, and per-stage breakdown.
        """
        all_companies = db.query(Company).all()
        total = len(all_companies)

        if total == 0:
            return {
                "total_companies": 0,
                "on_time_percentage": 100.0,
                "avg_processing_hours": 0.0,
                "breaches_count": 0,
                "stage_metrics": [],
            }

        breaches = self.get_sla_breaches(db)
        breaches_count = len(breaches)
        on_time = total - breaches_count
        on_time_pct = round((on_time / total) * 100, 2) if total > 0 else 100.0

        # Average processing time: created_at to updated_at for completed companies
        completed = [
            c for c in all_companies
            if c.status in (CompanyStatus.INCORPORATED, CompanyStatus.FULLY_SETUP)
        ]
        if completed:
            total_hours = sum(
                (c.updated_at - c.created_at).total_seconds() / 3600
                for c in completed
                if c.updated_at and c.created_at
            )
            avg_hours = round(total_hours / len(completed), 2)
        else:
            avg_hours = 0.0

        # Per-stage counts
        stage_counts: Dict[str, int] = {}
        for c in all_companies:
            status_val = c.status.value if c.status else "unknown"
            stage_counts[status_val] = stage_counts.get(status_val, 0) + 1

        stage_metrics = [
            {"stage": stage, "count": count}
            for stage, count in sorted(stage_counts.items())
        ]

        return {
            "total_companies": total,
            "on_time_percentage": on_time_pct,
            "avg_processing_hours": avg_hours,
            "breaches_count": breaches_count,
            "stage_metrics": stage_metrics,
        }


# Module-level singleton
sla_service = SLAService()
