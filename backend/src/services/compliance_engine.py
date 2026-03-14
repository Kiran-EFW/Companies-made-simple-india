"""Compliance Autopilot Engine — generates compliance calendars and tracks deadlines.

Master compliance rules database for all Indian entity types with automatic
deadline calculation, penalty estimation, and compliance health scoring.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.models.company import Company, EntityType
from src.models.compliance_task import ComplianceTask, ComplianceTaskType, ComplianceTaskStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Master Compliance Rules
# ---------------------------------------------------------------------------

COMPLIANCE_RULES: Dict[str, List[Dict[str, Any]]] = {
    "private_limited": [
        {
            "type": "aoc_4",
            "title": "AOC-4 (Financial Statements)",
            "frequency": "annual",
            "due_rule": "within_30_days_of_agm",
            "description": "File financial statements with ROC including Balance Sheet, P&L, and notes.",
            "penalty_per_day": 100,
            "max_penalty": None,
        },
        {
            "type": "mgt_7",
            "title": "MGT-7 (Annual Return)",
            "frequency": "annual",
            "due_rule": "within_60_days_of_agm",
            "description": "File annual return with ROC containing company details, shareholding, and directors.",
            "penalty_per_day": 100,
            "max_penalty": None,
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC (Director KYC)",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": "Every director must file annual KYC with MCA by September 30.",
            "penalty_per_day": 0,
            "penalty_late_fee": 5000,
        },
        {
            "type": "adt_1_renewal",
            "title": "ADT-1 (Auditor Reappointment)",
            "frequency": "annual",
            "due_rule": "within_15_days_of_agm",
            "description": "File notice of auditor appointment/reappointment after AGM.",
            "penalty_per_day": 100,
            "max_penalty": None,
        },
        {
            "type": "board_meeting_q1",
            "title": "Board Meeting — Q1 (Apr-Jun)",
            "frequency": "quarterly",
            "due_rule": "june_30",
            "description": "Mandatory quarterly board meeting. Maximum 120 days gap between meetings.",
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
        },
        {
            "type": "board_meeting_q2",
            "title": "Board Meeting — Q2 (Jul-Sep)",
            "frequency": "quarterly",
            "due_rule": "september_30",
            "description": "Mandatory quarterly board meeting.",
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
        },
        {
            "type": "board_meeting_q3",
            "title": "Board Meeting — Q3 (Oct-Dec)",
            "frequency": "quarterly",
            "due_rule": "december_31",
            "description": "Mandatory quarterly board meeting.",
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
        },
        {
            "type": "board_meeting_q4",
            "title": "Board Meeting — Q4 (Jan-Mar)",
            "frequency": "quarterly",
            "due_rule": "march_31",
            "description": "Mandatory quarterly board meeting.",
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
        },
        {
            "type": "agm",
            "title": "Annual General Meeting",
            "frequency": "annual",
            "due_rule": "within_6_months_of_fy_end",
            "description": "Hold AGM within 6 months of financial year end (by September 30).",
            "penalty_per_day": 0,
            "penalty_fixed": 100000,
        },
        {
            "type": "itr_filing",
            "title": "Income Tax Return",
            "frequency": "annual",
            "due_rule": "october_31",
            "description": "File ITR by October 31 (if audit applicable) or July 31 (otherwise).",
            "penalty_per_day": 0,
            "penalty_late_fee": 10000,
        },
        {
            "type": "advance_tax_q1",
            "title": "Advance Tax — Q1 (15% of estimated tax)",
            "frequency": "quarterly",
            "due_rule": "june_15",
            "description": "Pay 15% of estimated annual tax liability as advance tax.",
            "penalty_per_day": 0,
            "penalty_interest": "1% per month under 234C",
        },
        {
            "type": "advance_tax_q2",
            "title": "Advance Tax — Q2 (45% cumulative)",
            "frequency": "quarterly",
            "due_rule": "september_15",
            "description": "Pay advance tax to bring cumulative payment to 45% of estimated liability.",
        },
        {
            "type": "advance_tax_q3",
            "title": "Advance Tax — Q3 (75% cumulative)",
            "frequency": "quarterly",
            "due_rule": "december_15",
            "description": "Pay advance tax to bring cumulative payment to 75% of estimated liability.",
        },
        {
            "type": "advance_tax_q4",
            "title": "Advance Tax — Q4 (100% cumulative)",
            "frequency": "quarterly",
            "due_rule": "march_15",
            "description": "Pay remaining advance tax to reach 100% of estimated liability.",
        },
        {
            "type": "tds_return_q1",
            "title": "TDS Return — Q1 (Apr-Jun)",
            "frequency": "quarterly",
            "due_rule": "july_31",
            "description": "File quarterly TDS return (24Q/26Q/27Q) for Q1.",
            "penalty_per_day": 200,
            "max_penalty": None,
        },
        {
            "type": "tds_return_q2",
            "title": "TDS Return — Q2 (Jul-Sep)",
            "frequency": "quarterly",
            "due_rule": "october_31",
            "description": "File quarterly TDS return for Q2.",
            "penalty_per_day": 200,
            "max_penalty": None,
        },
        {
            "type": "tds_return_q3",
            "title": "TDS Return — Q3 (Oct-Dec)",
            "frequency": "quarterly",
            "due_rule": "january_31",
            "description": "File quarterly TDS return for Q3.",
            "penalty_per_day": 200,
            "max_penalty": None,
        },
        {
            "type": "tds_return_q4",
            "title": "TDS Return — Q4 (Jan-Mar)",
            "frequency": "quarterly",
            "due_rule": "may_31",
            "description": "File quarterly TDS return for Q4.",
            "penalty_per_day": 200,
            "max_penalty": None,
        },
        {
            "type": "form_16",
            "title": "Form 16 / 16A Issuance",
            "frequency": "annual",
            "due_rule": "june_15",
            "description": "Issue Form 16 to employees and Form 16A to vendors by June 15.",
        },
    ],

    "opc": [
        {
            "type": "aoc_4",
            "title": "AOC-4 (Financial Statements)",
            "frequency": "annual",
            "due_rule": "within_180_days_of_fy_end",
            "description": "OPC must file AOC-4 within 180 days of FY end (no AGM required).",
            "penalty_per_day": 100,
        },
        {
            "type": "mgt_7",
            "title": "MGT-7A (Annual Return — Small Company)",
            "frequency": "annual",
            "due_rule": "within_60_days_of_fy_end_plus_180",
            "description": "OPC files simplified MGT-7A.",
            "penalty_per_day": 100,
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC (Director KYC)",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": "Director must file annual KYC.",
            "penalty_late_fee": 5000,
        },
        {
            "type": "itr_filing",
            "title": "Income Tax Return",
            "frequency": "annual",
            "due_rule": "october_31",
            "description": "File ITR by October 31 (audit applicable) or July 31.",
        },
    ],

    "llp": [
        {
            "type": "form_11",
            "title": "Form 11 (LLP Annual Return)",
            "frequency": "annual",
            "due_rule": "may_30",
            "description": "File LLP Annual Return within 60 days of FY end.",
            "penalty_per_day": 100,
        },
        {
            "type": "form_8",
            "title": "Form 8 (Statement of Account & Solvency)",
            "frequency": "annual",
            "due_rule": "october_30",
            "description": "File statement of accounts within 30 days from 6 months of FY end.",
            "penalty_per_day": 100,
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC (Partner KYC)",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": "Designated partners must file annual KYC.",
            "penalty_late_fee": 5000,
        },
        {
            "type": "itr_filing",
            "title": "Income Tax Return (ITR-5)",
            "frequency": "annual",
            "due_rule": "october_31",
            "description": "LLP must file ITR-5 by October 31 (if audit applicable) or July 31.",
        },
    ],

    "section_8": [
        {
            "type": "aoc_4",
            "title": "AOC-4 (Financial Statements)",
            "frequency": "annual",
            "due_rule": "within_30_days_of_agm",
            "description": "File financial statements with ROC.",
            "penalty_per_day": 100,
        },
        {
            "type": "mgt_7",
            "title": "MGT-7 (Annual Return)",
            "frequency": "annual",
            "due_rule": "within_60_days_of_agm",
            "description": "File annual return.",
            "penalty_per_day": 100,
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": "Director annual KYC.",
            "penalty_late_fee": 5000,
        },
        {
            "type": "agm",
            "title": "Annual General Meeting",
            "frequency": "annual",
            "due_rule": "within_6_months_of_fy_end",
            "description": "Hold AGM within 6 months of FY end.",
        },
        {
            "type": "board_meeting_q1",
            "title": "Board Meeting — Q1",
            "frequency": "quarterly",
            "due_rule": "june_30",
            "description": "Quarterly board meeting.",
        },
        {
            "type": "board_meeting_q2",
            "title": "Board Meeting — Q2",
            "frequency": "quarterly",
            "due_rule": "september_30",
            "description": "Quarterly board meeting.",
        },
        {
            "type": "board_meeting_q3",
            "title": "Board Meeting — Q3",
            "frequency": "quarterly",
            "due_rule": "december_31",
            "description": "Quarterly board meeting.",
        },
        {
            "type": "board_meeting_q4",
            "title": "Board Meeting — Q4",
            "frequency": "quarterly",
            "due_rule": "march_31",
            "description": "Quarterly board meeting.",
        },
    ],

    "public_limited": [],  # extends private_limited — handled in code

    "sole_proprietorship": [
        {
            "type": "itr_filing",
            "title": "Income Tax Return (ITR-3/4)",
            "frequency": "annual",
            "due_rule": "july_31",
            "description": "File ITR by July 31.",
        },
    ],

    "partnership": [
        {
            "type": "itr_filing",
            "title": "Income Tax Return (ITR-5)",
            "frequency": "annual",
            "due_rule": "july_31",
            "description": "File ITR-5 by July 31.",
        },
    ],
}


# ---------------------------------------------------------------------------
# Penalty Rates
# ---------------------------------------------------------------------------

PENALTY_RATES: Dict[str, Dict[str, Any]] = {
    "aoc_4": {
        "description": "Late filing of AOC-4",
        "per_day": 100,
        "max": None,
        "additional": "Company and every officer in default liable.",
    },
    "mgt_7": {
        "description": "Late filing of MGT-7",
        "per_day": 100,
        "max": None,
        "additional": "Company and every officer in default liable.",
    },
    "dir_3_kyc": {
        "description": "Late DIR-3 KYC",
        "per_day": 0,
        "fixed": 5000,
        "additional": "DIN will be deactivated until KYC is filed.",
    },
    "board_meeting_q1": {
        "description": "Failure to hold Board Meeting",
        "per_day": 0,
        "fixed": 25000,
        "additional": "Each director: Rs 5,000 per meeting missed.",
    },
    "board_meeting_q2": {"per_day": 0, "fixed": 25000},
    "board_meeting_q3": {"per_day": 0, "fixed": 25000},
    "board_meeting_q4": {"per_day": 0, "fixed": 25000},
    "agm": {
        "description": "Failure to hold AGM",
        "per_day": 0,
        "fixed": 100000,
        "additional": "Additional Rs 5,000/day if continued default.",
    },
    "tds_return_q1": {
        "description": "Late TDS Return filing",
        "per_day": 200,
        "max": None,
        "additional": "Plus interest @ 1.5% per month on unpaid TDS.",
    },
    "tds_return_q2": {"per_day": 200, "max": None},
    "tds_return_q3": {"per_day": 200, "max": None},
    "tds_return_q4": {"per_day": 200, "max": None},
    "itr_filing": {
        "description": "Late ITR filing",
        "per_day": 0,
        "fixed": 10000,
        "additional": "Rs 5,000 if filed after Dec 31. Interest @ 1% per month under 234A.",
    },
    "form_11": {"per_day": 100, "max": None},
    "form_8": {"per_day": 100, "max": None},
}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class ComplianceEngine:
    """Core compliance calendar engine with deadline calculation and scoring."""

    # ── Calendar Generation ──────────────────────────────────────────────

    def generate_calendar(
        self,
        company: Company,
        financial_year: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Generate all compliance deadlines for a company for a given FY.

        Args:
            company: Company model instance.
            financial_year: FY start year (e.g. 2025 for FY 2025-26). Defaults to current FY.
        """
        entity = company.entity_type
        if isinstance(entity, EntityType):
            entity = entity.value

        if financial_year is None:
            today = date.today()
            financial_year = today.year if today.month >= 4 else today.year - 1

        fy_start = date(financial_year, 4, 1)
        fy_end = date(financial_year + 1, 3, 31)

        # Get rules — public_limited uses private_limited rules
        rules = COMPLIANCE_RULES.get(entity, [])
        if entity == "public_limited" and not rules:
            rules = COMPLIANCE_RULES.get("private_limited", [])

        calendar: List[Dict[str, Any]] = []
        for rule in rules:
            due = self.calculate_deadline(rule, company, fy_start, fy_end)
            days_until = (due - date.today()).days if due else None

            status = "upcoming"
            if days_until is not None:
                if days_until < 0:
                    status = "overdue"
                elif days_until <= 30:
                    status = "due_soon"

            calendar.append({
                "type": rule["type"],
                "title": rule["title"],
                "description": rule.get("description", ""),
                "frequency": rule["frequency"],
                "due_date": due.isoformat() if due else None,
                "days_remaining": max(days_until, 0) if days_until is not None else None,
                "status": status,
                "financial_year": f"{financial_year}-{financial_year + 1}",
            })

        # Sort by due_date
        calendar.sort(key=lambda x: x["due_date"] or "9999-12-31")
        return calendar

    # ── Deadline Calculation ─────────────────────────────────────────────

    def calculate_deadline(
        self,
        rule: Dict[str, Any],
        company: Company,
        fy_start: date,
        fy_end: date,
    ) -> Optional[date]:
        """Calculate actual due date from a compliance rule."""
        due_rule = rule.get("due_rule", "")

        # Fixed-date rules
        fixed_dates = {
            "april_30": date(fy_start.year, 4, 30),
            "may_30": date(fy_start.year, 5, 30),
            "may_31": date(fy_start.year, 5, 31),
            "june_15": date(fy_start.year, 6, 15),
            "june_30": date(fy_start.year, 6, 30),
            "july_31": date(fy_start.year, 7, 31),
            "september_15": date(fy_start.year, 9, 15),
            "september_30": date(fy_start.year, 9, 30),
            "october_30": date(fy_start.year, 10, 30),
            "october_31": date(fy_start.year, 10, 31),
            "december_15": date(fy_start.year, 12, 15),
            "december_31": date(fy_start.year, 12, 31),
            "january_31": date(fy_end.year, 1, 31),
            "march_15": date(fy_end.year, 3, 15),
            "march_31": date(fy_end.year, 3, 31),
        }

        if due_rule in fixed_dates:
            return fixed_dates[due_rule]

        # AGM-relative rules
        # AGM due date is September 30 (6 months from FY end March 31)
        agm_deadline = date(fy_start.year, 9, 30)

        if due_rule == "within_6_months_of_fy_end":
            return agm_deadline
        if due_rule == "at_agm":
            return agm_deadline
        if due_rule == "within_15_days_of_agm":
            return agm_deadline + timedelta(days=15)
        if due_rule == "within_30_days_of_agm":
            return agm_deadline + timedelta(days=30)
        if due_rule == "within_60_days_of_agm":
            return agm_deadline + timedelta(days=60)

        # OPC-specific
        if due_rule == "within_180_days_of_fy_end":
            return fy_end + timedelta(days=180)
        if due_rule == "within_60_days_of_fy_end_plus_180":
            return fy_end + timedelta(days=240)

        # Board meeting max gap
        if due_rule == "gap_max_120_days":
            return fy_start + timedelta(days=120)

        logger.warning("Unknown due_rule: %s", due_rule)
        return None

    # ── Task CRUD ────────────────────────────────────────────────────────

    def create_compliance_tasks(
        self,
        db: Session,
        company_id: int,
    ) -> List[ComplianceTask]:
        """Create ComplianceTask records for the next 12 months."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return []

        calendar = self.generate_calendar(company)
        created: List[ComplianceTask] = []

        for entry in calendar:
            # Check if task already exists for this type and approximate period
            task_type_str = entry["type"]
            try:
                task_type = ComplianceTaskType(task_type_str)
            except ValueError:
                logger.warning("Unknown ComplianceTaskType: %s — skipping", task_type_str)
                continue

            existing = (
                db.query(ComplianceTask)
                .filter(
                    ComplianceTask.company_id == company_id,
                    ComplianceTask.task_type == task_type,
                    ComplianceTask.due_date is not None,
                )
                .first()
            )
            if existing:
                continue

            due_date = None
            if entry["due_date"]:
                due_date = datetime.fromisoformat(entry["due_date"])
                due_date = due_date.replace(tzinfo=timezone.utc)

            status = ComplianceTaskStatus.UPCOMING
            if entry["status"] == "overdue":
                status = ComplianceTaskStatus.OVERDUE
            elif entry["status"] == "due_soon":
                status = ComplianceTaskStatus.DUE_SOON

            task = ComplianceTask(
                company_id=company_id,
                task_type=task_type,
                title=entry["title"],
                description=entry.get("description", ""),
                due_date=due_date,
                status=status,
            )
            db.add(task)
            created.append(task)

        db.commit()
        for t in created:
            db.refresh(t)
        return created

    # ── Queries ──────────────────────────────────────────────────────────

    def check_overdue_tasks(self, db: Session) -> List[ComplianceTask]:
        """Find all overdue compliance tasks across all companies."""
        now = datetime.now(timezone.utc)
        tasks = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.due_date < now,
                ComplianceTask.status.notin_([
                    ComplianceTaskStatus.COMPLETED,
                    ComplianceTaskStatus.NOT_APPLICABLE,
                ]),
            )
            .all()
        )
        # Update status to OVERDUE
        for t in tasks:
            if t.status != ComplianceTaskStatus.OVERDUE:
                t.status = ComplianceTaskStatus.OVERDUE
        db.commit()
        return tasks

    def get_upcoming_deadlines(
        self,
        db: Session,
        company_id: int,
        days: int = 30,
    ) -> List[ComplianceTask]:
        """Get deadlines coming up in next N days."""
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)
        return (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.due_date >= now,
                ComplianceTask.due_date <= future,
                ComplianceTask.status.notin_([
                    ComplianceTaskStatus.COMPLETED,
                    ComplianceTaskStatus.NOT_APPLICABLE,
                ]),
            )
            .order_by(ComplianceTask.due_date)
            .all()
        )

    # ── Penalty Calculator ───────────────────────────────────────────────

    def calculate_penalty(
        self,
        task_type: str,
        days_overdue: int,
    ) -> Dict[str, Any]:
        """Calculate MCA/IT penalty for late filing."""
        rates = PENALTY_RATES.get(task_type, {})
        if not rates:
            return {
                "task_type": task_type,
                "days_overdue": days_overdue,
                "estimated_penalty": 0,
                "note": "No penalty information available for this task type.",
            }

        per_day = rates.get("per_day", 0)
        fixed = rates.get("fixed", 0)
        max_penalty = rates.get("max", None)

        penalty = fixed + (per_day * max(days_overdue, 0))
        if max_penalty is not None and penalty > max_penalty:
            penalty = max_penalty

        return {
            "task_type": task_type,
            "days_overdue": days_overdue,
            "per_day_rate": per_day,
            "fixed_penalty": fixed,
            "estimated_penalty": penalty,
            "description": rates.get("description", ""),
            "additional_notes": rates.get("additional", ""),
        }

    # ── Compliance Score ─────────────────────────────────────────────────

    def get_compliance_score(
        self,
        db: Session,
        company_id: int,
    ) -> Dict[str, Any]:
        """Calculate compliance health score (0-100)."""
        all_tasks = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.status != ComplianceTaskStatus.NOT_APPLICABLE,
            )
            .all()
        )

        if not all_tasks:
            return {
                "score": 100,
                "grade": "A+",
                "total_tasks": 0,
                "completed": 0,
                "overdue": 0,
                "due_soon": 0,
                "upcoming": 0,
                "message": "No compliance tasks found. Generate tasks to start tracking.",
            }

        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.COMPLETED)
        overdue = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.OVERDUE)
        due_soon = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.DUE_SOON)
        in_progress = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.IN_PROGRESS)
        upcoming = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.UPCOMING)

        # Scoring algorithm:
        # Start from 100.
        # -15 points per overdue task
        # -5 points per due_soon task not in_progress
        # +0 for upcoming (neutral)
        # Completed tasks don't reduce score
        score = 100
        score -= overdue * 15
        score -= max(0, due_soon - in_progress) * 5
        score = max(0, min(100, score))

        # Grade
        if score >= 90:
            grade = "A+"
        elif score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B+"
        elif score >= 60:
            grade = "B"
        elif score >= 50:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"

        # Estimated total penalty exposure
        total_penalty = 0
        now = datetime.now(timezone.utc)
        for t in all_tasks:
            if t.status == ComplianceTaskStatus.OVERDUE and t.due_date:
                days_over = (now - t.due_date).days
                penalty_info = self.calculate_penalty(t.task_type.value, days_over)
                total_penalty += penalty_info.get("estimated_penalty", 0)

        return {
            "score": score,
            "grade": grade,
            "total_tasks": total,
            "completed": completed,
            "overdue": overdue,
            "due_soon": due_soon,
            "in_progress": in_progress,
            "upcoming": upcoming,
            "estimated_penalty_exposure": total_penalty,
            "message": (
                "Excellent compliance record!" if score >= 90
                else "Good standing — address due items." if score >= 70
                else "Action required — overdue filings detected." if score >= 50
                else "Critical — immediate action needed to avoid penalties."
            ),
        }


# Module-level singleton
compliance_engine = ComplianceEngine()
