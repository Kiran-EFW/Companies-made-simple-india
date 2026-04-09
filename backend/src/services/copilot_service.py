"""
Copilot Service — context-aware AI assistant for founders.

Aggregates live company data from compliance tasks, cap table, funding rounds,
ESOP plans, and directors to build enriched system prompts for the LLM.
Separate from the support chatbot — this is a platform-native AI copilot.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.company import Company, CompanyStatus, EntityType
from src.models.compliance_task import ComplianceTask, ComplianceTaskStatus
from src.models.shareholder import Shareholder
from src.models.funding_round import FundingRound, FundingRoundStatus, RoundInvestor
from src.models.esop import ESOPPlan, ESOPGrant, ESOPPlanStatus, ESOPGrantStatus
from src.models.director import Director, DSCStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Display maps (reused from chatbot router pattern)
# ---------------------------------------------------------------------------

ENTITY_DISPLAY = {
    EntityType.PRIVATE_LIMITED: "Private Limited Company",
    EntityType.OPC: "One Person Company (OPC)",
    EntityType.LLP: "Limited Liability Partnership (LLP)",
    EntityType.SECTION_8: "Section 8 Company (Non-Profit)",
    EntityType.SOLE_PROPRIETORSHIP: "Sole Proprietorship",
    EntityType.PARTNERSHIP: "Partnership Firm",
    EntityType.PUBLIC_LIMITED: "Public Limited Company",
}

STATUS_DISPLAY = {
    CompanyStatus.DRAFT: "Draft",
    CompanyStatus.ENTITY_SELECTED: "Entity Selected",
    CompanyStatus.PAYMENT_PENDING: "Payment Pending",
    CompanyStatus.PAYMENT_COMPLETED: "Payment Completed",
    CompanyStatus.DOCUMENTS_PENDING: "Documents Pending",
    CompanyStatus.DOCUMENTS_UPLOADED: "Documents Uploaded",
    CompanyStatus.DOCUMENTS_VERIFIED: "Documents Verified",
    CompanyStatus.NAME_PENDING: "Name Reservation Pending",
    CompanyStatus.NAME_RESERVED: "Name Reserved / Approved",
    CompanyStatus.NAME_REJECTED: "Name Rejected",
    CompanyStatus.DSC_IN_PROGRESS: "DSC In Progress",
    CompanyStatus.DSC_OBTAINED: "DSC Obtained",
    CompanyStatus.FILING_DRAFTED: "Filing Drafted",
    CompanyStatus.FILING_UNDER_REVIEW: "Filing Under Review",
    CompanyStatus.FILING_SUBMITTED: "Filing Submitted to MCA",
    CompanyStatus.MCA_PROCESSING: "MCA Processing",
    CompanyStatus.MCA_QUERY: "MCA Query Raised",
    CompanyStatus.INCORPORATED: "Incorporated",
    CompanyStatus.BANK_ACCOUNT_PENDING: "Bank Account Opening Pending",
    CompanyStatus.BANK_ACCOUNT_OPENED: "Bank Account Opened",
    CompanyStatus.INC20A_PENDING: "INC-20A Filing Pending",
    CompanyStatus.FULLY_SETUP: "Fully Set Up",
}

PAGE_DISPLAY = {
    "/dashboard": "Dashboard Overview",
    "/dashboard/cap-table": "Cap Table",
    "/dashboard/esop": "ESOP Management",
    "/dashboard/stakeholders": "Stakeholders",
    "/dashboard/fundraising": "Fundraising",
    "/dashboard/valuations": "Valuations",
    "/dashboard/compliance": "Compliance Calendar",
    "/dashboard/meetings": "Board Meetings",
    "/dashboard/registers": "Statutory Registers",
    "/dashboard/documents": "Legal Documents",
    "/dashboard/signatures": "E-Signatures",
    "/dashboard/data-room": "Data Room",
    "/dashboard/gst": "GST",
    "/dashboard/tax": "Tax Dashboard",
    "/dashboard/accounting": "Accounting",
    "/dashboard/services": "Services Marketplace",
    "/dashboard/team": "Team Management",
    "/dashboard/settings": "Settings",
}


class CopilotService:
    """Context-aware AI copilot for platform founders."""

    # ------------------------------------------------------------------
    # Context aggregation
    # ------------------------------------------------------------------

    def get_company_context(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Aggregate all company data for copilot context."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {}

        compliance = self._get_compliance_summary(db, company_id)
        fundraising = self._get_fundraising_summary(db, company_id)
        directors = self._get_directors_summary(db, company_id)

        return {
            "company": self._get_company_summary(company),
            "compliance": compliance,
            "cap_table": self._get_cap_table_summary(db, company_id),
            "fundraising": fundraising,
            "esop": self._get_esop_summary(db, company_id),
            "directors": directors,
            "pending_actions": self._get_pending_actions(
                company, compliance, fundraising, directors
            ),
        }

    def _get_company_summary(self, company: Company) -> Dict[str, Any]:
        entity = ENTITY_DISPLAY.get(company.entity_type, str(company.entity_type))
        status = STATUS_DISPLAY.get(company.status, str(company.status))
        name = company.approved_name or (
            ", ".join(company.proposed_names) if company.proposed_names else "Not yet proposed"
        )
        return {
            "name": name,
            "entity_type": entity,
            "status": status,
            "status_raw": company.status.value if company.status else None,
            "state": company.state,
            "cin": company.cin,
            "pan": company.pan,
            "tan": company.tan,
            "authorized_capital": company.authorized_capital,
            "created_at": company.created_at.isoformat() if company.created_at else None,
        }

    def _get_compliance_summary(self, db: Session, company_id: int) -> Dict[str, Any]:
        pending_statuses = [
            ComplianceTaskStatus.UPCOMING,
            ComplianceTaskStatus.DUE_SOON,
            ComplianceTaskStatus.OVERDUE,
            ComplianceTaskStatus.IN_PROGRESS,
        ]

        # Full counts (not capped by limit)
        overdue_count = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.status == ComplianceTaskStatus.OVERDUE,
            )
            .count()
        )
        due_soon_count = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.status == ComplianceTaskStatus.DUE_SOON,
            )
            .count()
        )
        total_pending = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.status.in_(pending_statuses),
            )
            .count()
        )

        tasks = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.status.in_(pending_statuses),
            )
            .order_by(ComplianceTask.due_date.asc())
            .limit(10)
            .all()
        )

        upcoming = []
        for t in tasks[:5]:
            days_left = None
            if t.due_date:
                delta = t.due_date.replace(tzinfo=None) - datetime.now(timezone.utc).replace(tzinfo=None)
                days_left = delta.days

            upcoming.append({
                "title": t.title,
                "task_type": t.task_type.value if t.task_type else None,
                "due_date": t.due_date.strftime("%d %b %Y") if t.due_date else None,
                "days_left": days_left,
                "status": t.status.value if t.status else None,
            })

        return {
            "overdue_count": overdue_count,
            "due_soon_count": due_soon_count,
            "total_pending": total_pending,
            "upcoming_deadlines": upcoming,
        }

    def _get_cap_table_summary(self, db: Session, company_id: int) -> Dict[str, Any]:
        shareholders = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )

        if not shareholders:
            return {
                "shareholder_count": 0,
                "total_shares": 0,
                "promoter_count": 0,
                "promoter_percentage": 0.0,
                "shareholders": [],
            }

        total_shares = sum(s.shares for s in shareholders)
        promoters = [s for s in shareholders if s.is_promoter]
        promoter_shares = sum(s.shares for s in promoters)
        promoter_pct = (promoter_shares / total_shares * 100) if total_shares > 0 else 0.0

        top_shareholders = sorted(shareholders, key=lambda s: s.shares, reverse=True)[:5]

        return {
            "shareholder_count": len(shareholders),
            "total_shares": total_shares,
            "promoter_count": len(promoters),
            "promoter_percentage": round(promoter_pct, 2),
            "shareholders": [
                {
                    "name": s.name,
                    "shares": s.shares,
                    "percentage": round(s.percentage, 2),
                    "is_promoter": s.is_promoter,
                }
                for s in top_shareholders
            ],
        }

    def _get_fundraising_summary(self, db: Session, company_id: int) -> Dict[str, Any]:
        rounds = (
            db.query(FundingRound)
            .filter(FundingRound.company_id == company_id)
            .order_by(FundingRound.created_at.desc())
            .all()
        )

        if not rounds:
            return {"total_rounds": 0, "active_rounds": [], "total_raised": 0.0}

        active_rounds = []
        total_raised = 0.0

        for r in rounds:
            total_raised += r.amount_raised or 0.0

            if r.status not in (FundingRoundStatus.CLOSED, FundingRoundStatus.CANCELLED):
                investors = (
                    db.query(RoundInvestor)
                    .filter(RoundInvestor.funding_round_id == r.id)
                    .all()
                )
                pending_funds = sum(1 for i in investors if i.committed and not i.funds_received)
                pending_docs = sum(1 for i in investors if not i.documents_signed)

                active_rounds.append({
                    "round_name": r.round_name,
                    "instrument_type": r.instrument_type.value if r.instrument_type else None,
                    "target_amount": r.target_amount,
                    "amount_raised": r.amount_raised,
                    "status": r.status.value if r.status else None,
                    "investor_count": len(investors),
                    "pending_funds": pending_funds,
                    "pending_docs": pending_docs,
                    "has_term_sheet": r.term_sheet_document_id is not None,
                    "has_sha": r.sha_document_id is not None,
                    "has_ssa": r.ssa_document_id is not None,
                    "allotment_completed": r.allotment_completed,
                })

        return {
            "total_rounds": len(rounds),
            "active_rounds": active_rounds,
            "total_raised": total_raised,
        }

    def _get_esop_summary(self, db: Session, company_id: int) -> Dict[str, Any]:
        plans = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.company_id == company_id)
            .all()
        )

        if not plans:
            return {
                "has_esop": False,
                "total_pool_size": 0,
                "total_allocated": 0,
                "total_available": 0,
                "plans": [],
            }

        total_pool = sum(p.pool_size for p in plans)
        total_allocated = sum(p.pool_shares_allocated for p in plans)

        grants = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.company_id == company_id)
            .all()
        )
        active_grants = sum(
            1 for g in grants
            if g.status in (ESOPGrantStatus.ACTIVE, ESOPGrantStatus.ACCEPTED, ESOPGrantStatus.PARTIALLY_EXERCISED)
        )
        pending_grants = sum(
            1 for g in grants
            if g.status in (ESOPGrantStatus.DRAFT, ESOPGrantStatus.OFFERED)
        )

        return {
            "has_esop": True,
            "total_pool_size": total_pool,
            "total_allocated": total_allocated,
            "total_available": total_pool - total_allocated,
            "utilization_pct": round(total_allocated / total_pool * 100, 1) if total_pool > 0 else 0.0,
            "active_grants": active_grants,
            "pending_grants": pending_grants,
            "total_grants": len(grants),
            "plans": [
                {
                    "name": p.plan_name,
                    "pool_size": p.pool_size,
                    "allocated": p.pool_shares_allocated,
                    "status": p.status.value if p.status else None,
                }
                for p in plans
            ],
        }

    def _get_directors_summary(self, db: Session, company_id: int) -> Dict[str, Any]:
        directors = (
            db.query(Director)
            .filter(Director.company_id == company_id)
            .all()
        )

        if not directors:
            return {"count": 0, "directors": [], "issues": []}

        issues = []
        for d in directors:
            if not d.din:
                issues.append(f"{d.full_name} does not have a DIN")
            if d.dsc_status == DSCStatus.EXPIRED:
                issues.append(f"{d.full_name}'s DSC has expired")
            elif d.dsc_status != DSCStatus.OBTAINED and d.dsc_status != DSCStatus.PROCESSING:
                issues.append(f"{d.full_name} does not have a valid DSC")

        return {
            "count": len(directors),
            "directors": [
                {
                    "name": d.full_name,
                    "din": d.din,
                    "dsc_status": d.dsc_status.value if d.dsc_status else None,
                }
                for d in directors
            ],
            "issues": issues,
        }

    def _get_pending_actions(
        self,
        company: Company,
        compliance: Dict[str, Any],
        fundraising: Dict[str, Any],
        directors: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Build pending actions from pre-computed context (no extra DB queries)."""
        actions: List[Dict[str, Any]] = []

        # Status-based actions
        status = company.status
        if status == CompanyStatus.PAYMENT_COMPLETED:
            actions.append({
                "action": "Upload required documents (identity proofs, address proofs, office address proof)",
                "category": "incorporation",
                "url": "/dashboard",
            })
        elif status == CompanyStatus.DOCUMENTS_VERIFIED:
            actions.append({
                "action": "Reserve your company name via RUN / SPICe+ Part A",
                "category": "incorporation",
                "url": "/dashboard",
            })
        elif status == CompanyStatus.NAME_REJECTED:
            actions.append({
                "action": "Propose new company names and resubmit",
                "category": "incorporation",
                "url": "/dashboard",
            })
        elif status == CompanyStatus.NAME_RESERVED:
            actions.append({
                "action": "Obtain DSC for all directors, then file SPICe+ Part B",
                "category": "incorporation",
                "url": "/dashboard",
            })
        elif status == CompanyStatus.MCA_QUERY:
            actions.append({
                "action": "Respond to query raised by the Registrar of Companies",
                "category": "incorporation",
                "url": "/dashboard",
            })
        elif status == CompanyStatus.INCORPORATED:
            actions.append({
                "action": "File INC-20A, hold first board meeting, appoint auditor, open bank account",
                "category": "post_incorporation",
                "url": "/dashboard/compliance",
            })
        elif status == CompanyStatus.INC20A_PENDING:
            actions.append({
                "action": "File INC-20A declaration for commencement of business",
                "category": "post_incorporation",
                "url": "/dashboard/compliance",
            })

        # Data-driven actions (using pre-computed context)
        if compliance["overdue_count"] > 0:
            actions.append({
                "action": f"{compliance['overdue_count']} overdue compliance task(s) need attention",
                "category": "compliance",
                "url": "/dashboard/compliance",
            })

        for r in fundraising.get("active_rounds", []):
            if r["pending_funds"] > 0:
                actions.append({
                    "action": f"{r['round_name']}: {r['pending_funds']} investor(s) have not transferred funds",
                    "category": "fundraising",
                    "url": "/dashboard/fundraising",
                })
            if not r["has_term_sheet"] and r["status"] == "draft":
                actions.append({
                    "action": f"{r['round_name']}: Generate a term sheet to share with investors",
                    "category": "fundraising",
                    "url": "/dashboard/fundraising",
                })

        if directors["issues"]:
            actions.append({
                "action": f"Director issue(s): {directors['issues'][0]}",
                "category": "directors",
                "url": "/dashboard/stakeholders",
            })

        return actions

    # ------------------------------------------------------------------
    # Suggestion engine (deterministic, no LLM)
    # ------------------------------------------------------------------

    def get_suggestions(
        self, db: Session, company_id: int, current_page: str
    ) -> List[Dict[str, Any]]:
        """Generate page-aware proactive suggestions."""
        suggestions: List[Dict[str, Any]] = []
        suggestion_id = 0

        def add(title: str, description: str, url: str, priority: str, category: str):
            nonlocal suggestion_id
            suggestion_id += 1
            suggestions.append({
                "id": f"s{suggestion_id}",
                "title": title,
                "description": description,
                "action_url": url,
                "priority": priority,
                "category": category,
            })

        # Always check compliance (cross-cutting concern)
        compliance = self._get_compliance_summary(db, company_id)

        if compliance["overdue_count"] > 0:
            add(
                f"{compliance['overdue_count']} overdue compliance task(s)",
                "These tasks are past their due date and may attract penalties.",
                "/dashboard/compliance",
                "high",
                "compliance",
            )

        for deadline in compliance.get("upcoming_deadlines", []):
            if deadline.get("days_left") is not None and 0 < deadline["days_left"] <= 7:
                add(
                    f"{deadline['title']} due in {deadline['days_left']} days",
                    f"Due on {deadline['due_date']}. Start preparation now.",
                    "/dashboard/compliance",
                    "high",
                    "compliance",
                )

        # Page-specific suggestions
        if current_page.startswith("/dashboard/cap-table"):
            self._suggest_cap_table(db, company_id, add)
        elif current_page.startswith("/dashboard/compliance"):
            self._suggest_compliance(db, company_id, compliance, add)
        elif current_page.startswith("/dashboard/fundraising"):
            self._suggest_fundraising(db, company_id, add)
        elif current_page.startswith("/dashboard/esop"):
            self._suggest_esop(db, company_id, add)
        elif current_page.startswith("/dashboard/documents") or current_page.startswith("/dashboard/signatures"):
            self._suggest_documents(db, company_id, add)
        else:
            # Default: overview suggestions
            self._suggest_overview(db, company_id, add)

        return suggestions[:6]

    def _suggest_cap_table(self, db, company_id, add):
        esop = self._get_esop_summary(db, company_id)
        if not esop["has_esop"]:
            add(
                "Consider setting up an ESOP pool",
                "Most funded startups reserve 10-15% of equity for employee stock options.",
                "/dashboard/esop",
                "medium",
                "esop",
            )
        elif esop["utilization_pct"] > 80:
            add(
                f"ESOP pool is {esop['utilization_pct']}% utilized",
                f"Only {esop['total_available']} options remaining. Consider expanding the pool.",
                "/dashboard/esop",
                "medium",
                "esop",
            )

        cap = self._get_cap_table_summary(db, company_id)
        if cap["shareholder_count"] == 0:
            add(
                "Set up your cap table",
                "Add shareholders and their holdings to track equity ownership.",
                "/dashboard/cap-table",
                "medium",
                "cap_table",
            )

    def _suggest_compliance(self, db, company_id, compliance, add):
        for deadline in compliance.get("upcoming_deadlines", []):
            if deadline.get("days_left") is not None and 7 < deadline["days_left"] <= 30:
                add(
                    f"{deadline['title']} — due {deadline['due_date']}",
                    f"{deadline['days_left']} days remaining. Plan your filing.",
                    "/dashboard/compliance",
                    "medium",
                    "compliance",
                )

    def _suggest_fundraising(self, db, company_id, add):
        fundraising = self._get_fundraising_summary(db, company_id)
        for r in fundraising.get("active_rounds", []):
            if not r["has_term_sheet"]:
                add(
                    f"Generate term sheet for {r['round_name']}",
                    "Create a term sheet to formalize investment terms with investors.",
                    "/dashboard/documents",
                    "medium",
                    "fundraising",
                )
            if r["pending_docs"] > 0:
                add(
                    f"{r['pending_docs']} investor(s) haven't signed documents",
                    f"Follow up on pending signatures for {r['round_name']}.",
                    "/dashboard/signatures",
                    "medium",
                    "fundraising",
                )
            if r["status"] == "closing" and not r["allotment_completed"]:
                add(
                    f"Complete share allotment for {r['round_name']}",
                    "Round is in closing — allot shares and file PAS-3 with MCA.",
                    "/dashboard/fundraising",
                    "high",
                    "fundraising",
                )

        if fundraising["total_rounds"] == 0:
            add(
                "Ready to raise funding?",
                "Create a funding round to track investors, generate term sheets, and manage the closing process.",
                "/dashboard/fundraising",
                "low",
                "fundraising",
            )

    def _suggest_esop(self, db, company_id, add):
        esop = self._get_esop_summary(db, company_id)
        if not esop["has_esop"]:
            add(
                "Create your first ESOP plan",
                "Set up an employee stock option plan to attract and retain talent.",
                "/dashboard/esop",
                "medium",
                "esop",
            )
        else:
            if esop["pending_grants"] > 0:
                add(
                    f"{esop['pending_grants']} pending grant(s) awaiting action",
                    "Review and send grant letters to employees.",
                    "/dashboard/esop",
                    "medium",
                    "esop",
                )

    def _suggest_documents(self, db, company_id, add):
        fundraising = self._get_fundraising_summary(db, company_id)
        for r in fundraising.get("active_rounds", []):
            if not r["has_sha"] and r["status"] in ("documentation", "closing"):
                add(
                    f"Draft SHA for {r['round_name']}",
                    "A Shareholders' Agreement is needed before closing the round.",
                    "/dashboard/documents",
                    "high",
                    "fundraising",
                )
            if not r["has_ssa"] and r["status"] in ("documentation", "closing"):
                add(
                    f"Draft SSA for {r['round_name']}",
                    "A Share Subscription Agreement is needed before allotting shares.",
                    "/dashboard/documents",
                    "high",
                    "fundraising",
                )

    def _suggest_overview(self, db, company_id, add):
        """General suggestions for the dashboard overview page."""
        fundraising = self._get_fundraising_summary(db, company_id)
        for r in fundraising.get("active_rounds", []):
            if r["pending_funds"] > 0:
                add(
                    f"{r['round_name']}: {r['pending_funds']} investor(s) pending fund transfer",
                    "Follow up to keep the round on track.",
                    "/dashboard/fundraising",
                    "medium",
                    "fundraising",
                )

        esop = self._get_esop_summary(db, company_id)
        if esop["has_esop"] and esop["pending_grants"] > 0:
            add(
                f"{esop['pending_grants']} ESOP grant(s) need attention",
                "Review pending grants and send offer letters.",
                "/dashboard/esop",
                "medium",
                "esop",
            )

        directors = self._get_directors_summary(db, company_id)
        if directors["issues"]:
            add(
                "Director compliance issue",
                directors["issues"][0],
                "/dashboard/stakeholders",
                "medium",
                "general",
            )

    # ------------------------------------------------------------------
    # System prompt builder
    # ------------------------------------------------------------------

    def build_system_prompt(
        self, company_context: Dict[str, Any], current_page: str
    ) -> str:
        parts = [
            self._role_definition(),
            self._format_company_context(company_context),
            self._format_page_context(current_page),
            self._behavioral_guidelines(),
        ]
        return "\n\n".join(parts)

    def _role_definition(self) -> str:
        return (
            "You are the Anvils Copilot, a constructive AI guide for Indian company founders "
            "on the Anvils equity, governance, and compliance platform.\n\n"
            "YOUR ROLE:\n"
            "- You are a guide and educator, NOT a document drafter. You explain legal concepts, "
            "compliance requirements, regulatory procedures, and platform features so founders "
            "can make informed decisions and take action themselves.\n"
            "- You give constructive, actionable feedback on the founder's current company status. "
            "Point out what they're doing well, what needs attention, and what risks they face.\n"
            "- You explain the 'why' behind every obligation — why a filing matters, what the "
            "penalty is, what the business impact of missing it would be.\n"
            "- You help founders understand their cap table, equity dilution, ESOP implications, "
            "and fundraising instruments — but you do NOT generate legal documents. All document "
            "drafting, signing, and filing is done by the founder through the platform.\n"
            "- You guide founders on how to use the Anvils platform — which page to go to, "
            "what actions to take, and in what order.\n\n"
            "You have access to real-time data about the founder's company, provided below."
        )

    def _format_company_context(self, ctx: Dict[str, Any]) -> str:
        if not ctx:
            return "No company data available."

        sections = []

        # Company overview
        co = ctx.get("company", {})
        sections.append(
            "=== COMPANY OVERVIEW ===\n"
            f"Company: {co.get('name', 'N/A')}\n"
            f"Entity Type: {co.get('entity_type', 'N/A')}\n"
            f"Status: {co.get('status', 'N/A')}\n"
            f"State: {co.get('state', 'N/A')}\n"
            f"CIN: {co.get('cin') or 'Not yet assigned'}\n"
            f"Authorized Capital: Rs {(co.get('authorized_capital') or 0):,}"
        )

        # Compliance
        comp = ctx.get("compliance", {})
        deadlines_text = ""
        for i, d in enumerate(comp.get("upcoming_deadlines", []), 1):
            days = d.get("days_left")
            days_str = f" ({days} days left)" if days is not None else ""
            deadlines_text += f"\n  {i}. {d['title']} — Due: {d.get('due_date', 'TBD')} — Status: {d.get('status', 'unknown')}{days_str}"

        sections.append(
            "=== COMPLIANCE STATUS ===\n"
            f"Overdue tasks: {comp.get('overdue_count', 0)}\n"
            f"Due soon (within 30 days): {comp.get('due_soon_count', 0)}\n"
            f"Total pending: {comp.get('total_pending', 0)}\n"
            f"Upcoming deadlines:{deadlines_text or ' None'}"
        )

        # Cap table
        cap = ctx.get("cap_table", {})
        sh_text = ""
        for s in cap.get("shareholders", []):
            promoter_tag = " (Promoter)" if s.get("is_promoter") else ""
            sh_text += f"\n  - {s['name']}: {s['shares']} shares ({s['percentage']}%){promoter_tag}"

        sections.append(
            "=== CAP TABLE ===\n"
            f"Total Shareholders: {cap.get('shareholder_count', 0)}\n"
            f"Total Shares: {cap.get('total_shares', 0):,}\n"
            f"Promoter Holding: {cap.get('promoter_percentage', 0)}%\n"
            f"Top Shareholders:{sh_text or ' None'}"
        )

        # Fundraising
        fr = ctx.get("fundraising", {})
        rounds_text = ""
        for r in fr.get("active_rounds", []):
            target = r.get("target_amount") or 0
            raised = r.get("amount_raised") or 0
            pct = round(raised / target * 100, 1) if target > 0 else 0
            rounds_text += (
                f"\n  - {r['round_name']} ({r.get('instrument_type', 'equity')}): "
                f"Rs {raised:,.0f} / Rs {target:,.0f} ({pct}%) — Status: {r.get('status', 'unknown')}"
            )
            if r.get("pending_funds", 0) > 0:
                rounds_text += f" | {r['pending_funds']} investor(s) awaiting fund transfer"

        sections.append(
            "=== FUNDRAISING ===\n"
            f"Total Rounds: {fr.get('total_rounds', 0)}\n"
            f"Total Raised (all rounds): Rs {fr.get('total_raised', 0):,.0f}\n"
            f"Active Rounds:{rounds_text or ' None'}"
        )

        # ESOP
        esop = ctx.get("esop", {})
        if esop.get("has_esop"):
            plans_text = ""
            for p in esop.get("plans", []):
                plans_text += f"\n  - {p['name']}: {p['allocated']}/{p['pool_size']} allocated — {p.get('status', 'unknown')}"
            sections.append(
                "=== ESOP ===\n"
                f"Pool Size: {esop.get('total_pool_size', 0):,} options\n"
                f"Allocated: {esop.get('total_allocated', 0):,} | Available: {esop.get('total_available', 0):,}\n"
                f"Utilization: {esop.get('utilization_pct', 0)}%\n"
                f"Active Grants: {esop.get('active_grants', 0)} | Pending: {esop.get('pending_grants', 0)}\n"
                f"Plans:{plans_text}"
            )
        else:
            sections.append("=== ESOP ===\nNo ESOP plan set up.")

        # Directors
        dirs = ctx.get("directors", {})
        dir_text = ""
        for d in dirs.get("directors", []):
            dir_text += f"\n  - {d['name']} (DIN: {d.get('din') or 'None'}, DSC: {d.get('dsc_status', 'unknown')})"
        issues_text = ""
        for issue in dirs.get("issues", []):
            issues_text += f"\n  - {issue}"

        sections.append(
            "=== DIRECTORS ===\n"
            f"Count: {dirs.get('count', 0)}\n"
            f"Directors:{dir_text or ' None'}"
            + (f"\nIssues:{issues_text}" if issues_text else "")
        )

        # Pending actions
        actions = ctx.get("pending_actions", [])
        if actions:
            actions_text = ""
            for i, a in enumerate(actions, 1):
                actions_text += f"\n  {i}. {a['action']}"
            sections.append(f"=== PENDING ACTIONS ==={actions_text}")

        return "\n\n".join(sections)

    def _format_page_context(self, current_page: str) -> str:
        page_name = PAGE_DISPLAY.get(current_page, current_page)
        return (
            f"=== CURRENT PAGE ===\n"
            f"The user is currently viewing: {page_name} ({current_page})\n"
            f"Focus your responses on topics relevant to this page unless asked otherwise."
        )

    def _behavioral_guidelines(self) -> str:
        return (
            "=== GUIDELINES ===\n"
            "- Give constructive feedback: acknowledge what the founder has done well, then "
            "clearly explain what needs attention and why.\n"
            "- Be a guide, not a drafter: explain what a document is, why it's needed, and "
            "where to create it on the platform — but never generate document content yourself. "
            "Say things like 'Go to Legal Documents to draft your term sheet' rather than writing one.\n"
            "- Explain legal concepts in plain language: break down regulatory jargon (MCA, ROC, "
            "SPICe+, PAS-3, etc.) so first-time founders can understand.\n"
            "- Reference specific numbers, dates, and names from the company context above.\n"
            "- When suggesting actions, mention the exact platform page (e.g., 'Go to Compliance Calendar').\n"
            "- Always explain the consequence of inaction — penalties, deadlines, business impact.\n"
            "- Do not invent data not present in the context. If asked about something outside "
            "the context, say you don't have that information.\n"
            "- For specific legal or tax advice, recommend consulting a CA or legal professional.\n"
            "- Format responses with bullet points and bold text for readability.\n"
            "- Use Indian regulatory terminology naturally but always explain it on first mention.\n\n"
            "=== MANDATORY DISCLAIMER ===\n"
            "- ALWAYS end every response with this disclaimer:\n"
            "'*This is general guidance only — not legal or tax advice. Verify deadlines on the "
            "MCA/GST portal and consult a qualified CA or CS before acting.*'\n"
            "- NEVER state that a company name is 'reserved' or 'approved' — only MCA can confirm.\n"
            "- When quoting penalty amounts or deadlines, add 'as per current rules' since these "
            "may be updated by government notifications.\n"
            "- Do NOT recommend specific tax-saving strategies or interpret court judgments.\n"
            "- If the user asks about a legal dispute, litigation, or NCLT proceedings, advise "
            "them to consult a practicing advocate — do not attempt to guide on litigation."
        )

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    async def chat(
        self,
        db: Session,
        company_id: int,
        message: str,
        current_page: str,
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """Send a copilot chat message with full company context."""
        from src.services.llm_service import llm_service

        context = self.get_company_context(db, company_id)
        system_prompt = self.build_system_prompt(context, current_page)

        messages = (conversation_history[-20:] if conversation_history else [])
        messages.append({"role": "user", "content": message})
        return await llm_service.chat_with_history(
            system_prompt=system_prompt,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )


# Singleton
copilot_service = CopilotService()
