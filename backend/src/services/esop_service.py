"""
ESOP Service — manages ESOP plans, grants, vesting calculations,
option exercise, and grant letter generation.

Integrates with:
- cap_table_service for share allotment on exercise
- esign_service for grant letter signing
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from src.models.esop import (
    ESOPPlan, ESOPGrant, ESOPPlanStatus, ESOPGrantStatus, VestingType,
)

logger = logging.getLogger(__name__)


class ESOPService:
    """Service for ESOP plan and grant management."""

    # ------------------------------------------------------------------
    # Plan CRUD
    # ------------------------------------------------------------------

    def create_plan(
        self, db: Session, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new ESOP plan."""
        from src.models.company import Company, EntityType

        # Entity type guard — block entity types that don't support ESOPs
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}

        blocked_types = {
            EntityType.SOLE_PROPRIETORSHIP,
            EntityType.PARTNERSHIP,
            EntityType.LLP,
            EntityType.SECTION_8,
        }
        if company.entity_type in blocked_types:
            return {
                "error": f"ESOP plans are not available for {company.entity_type.value} entities"
            }

        effective_date = None
        if data.get("effective_date"):
            effective_date = datetime.strptime(
                data["effective_date"], "%Y-%m-%d"
            ).replace(tzinfo=timezone.utc)

        expiry_date = None
        if data.get("expiry_date"):
            expiry_date = datetime.strptime(
                data["expiry_date"], "%Y-%m-%d"
            ).replace(tzinfo=timezone.utc)

        board_resolution_date = None
        if data.get("board_resolution_date"):
            board_resolution_date = datetime.strptime(
                data["board_resolution_date"], "%Y-%m-%d"
            ).replace(tzinfo=timezone.utc)

        vesting_type = VestingType.MONTHLY
        if data.get("default_vesting_type") == "quarterly":
            vesting_type = VestingType.QUARTERLY
        elif data.get("default_vesting_type") == "annually":
            vesting_type = VestingType.ANNUALLY

        plan = ESOPPlan(
            company_id=company_id,
            plan_name=data["plan_name"],
            pool_size=data["pool_size"],
            default_vesting_months=data.get("default_vesting_months", 48),
            default_cliff_months=data.get("default_cliff_months", 12),
            default_vesting_type=vesting_type,
            exercise_price=data.get("exercise_price", 10.0),
            exercise_price_basis=data.get("exercise_price_basis", "face_value"),
            effective_date=effective_date,
            expiry_date=expiry_date,
            board_resolution_date=board_resolution_date,
            dpiit_recognized=data.get("dpiit_recognized", False),
            dpiit_recognition_number=data.get("dpiit_recognition_number"),
        )
        db.add(plan)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(plan)

        return self._serialize_plan(db, plan)

    def get_plan(
        self, db: Session, plan_id: int, company_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get plan details with computed stats."""
        plan = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.id == plan_id, ESOPPlan.company_id == company_id)
            .first()
        )
        if not plan:
            return None
        return self._serialize_plan(db, plan)

    def list_plans(
        self, db: Session, company_id: int
    ) -> List[Dict[str, Any]]:
        """List all ESOP plans for a company."""
        plans = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.company_id == company_id)
            .order_by(ESOPPlan.created_at.desc())
            .all()
        )
        return [self._serialize_plan(db, p) for p in plans]

    def update_plan(
        self, db: Session, plan_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update plan details."""
        plan = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.id == plan_id, ESOPPlan.company_id == company_id)
            .first()
        )
        if not plan:
            return {"error": "Plan not found"}

        if data.get("pool_size") is not None:
            if data["pool_size"] < plan.pool_shares_allocated:
                return {
                    "error": (
                        f"Cannot reduce pool size below allocated amount "
                        f"({plan.pool_shares_allocated} options already granted)"
                    )
                }
            plan.pool_size = data["pool_size"]

        if data.get("plan_name") is not None:
            plan.plan_name = data["plan_name"]
        if data.get("default_vesting_months") is not None:
            plan.default_vesting_months = data["default_vesting_months"]
        if data.get("default_cliff_months") is not None:
            plan.default_cliff_months = data["default_cliff_months"]
        if data.get("default_vesting_type") is not None:
            plan.default_vesting_type = VestingType(data["default_vesting_type"])
        if data.get("exercise_price") is not None:
            plan.exercise_price = data["exercise_price"]
        if data.get("status") is not None:
            plan.status = ESOPPlanStatus(data["status"])
        if data.get("dpiit_recognized") is not None:
            plan.dpiit_recognized = data["dpiit_recognized"]
        if data.get("dpiit_recognition_number") is not None:
            plan.dpiit_recognition_number = data["dpiit_recognition_number"]

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(plan)

        return self._serialize_plan(db, plan)

    def activate_plan(
        self, db: Session, plan_id: int, company_id: int
    ) -> Dict[str, Any]:
        """Move plan to active status."""
        plan = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.id == plan_id, ESOPPlan.company_id == company_id)
            .first()
        )
        if not plan:
            return {"error": "Plan not found"}

        if plan.status not in (
            ESOPPlanStatus.DRAFT,
            ESOPPlanStatus.BOARD_APPROVED,
            ESOPPlanStatus.SHAREHOLDER_APPROVED,
        ):
            return {"error": f"Cannot activate plan in '{plan.status.value}' status"}

        # Validate required documents are linked before activation
        if not plan.board_resolution_document_id:
            return {"error": "Board resolution document must be linked before activating the plan"}
        if not plan.shareholder_resolution_document_id:
            return {"error": "Shareholder resolution document must be linked before activating the plan"}

        # Warn (log only) if special resolution hasn't been passed
        approval_state = plan.approval_state or {}
        if not approval_state.get("special_resolution_passed"):
            logger.warning(
                "Plan %s activated without special_resolution_passed in approval_state",
                plan_id,
            )

        plan.status = ESOPPlanStatus.ACTIVE
        if not plan.effective_date:
            plan.effective_date = datetime.now(timezone.utc)
        if not plan.board_resolution_date:
            plan.board_resolution_date = datetime.now(timezone.utc)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(plan)

        return self._serialize_plan(db, plan)

    # ------------------------------------------------------------------
    # Grant CRUD
    # ------------------------------------------------------------------

    def create_grant(
        self, db: Session, plan_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Issue a new grant under a plan."""
        plan = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.id == plan_id, ESOPPlan.company_id == company_id)
            .first()
        )
        if not plan:
            return {"error": "Plan not found"}

        if plan.status != ESOPPlanStatus.ACTIVE:
            return {"error": "Plan must be active to issue grants"}

        num_options = data["number_of_options"]
        available = plan.pool_size - plan.pool_shares_allocated
        if num_options > available:
            return {
                "error": (
                    f"Insufficient pool. Available: {available}, "
                    f"requested: {num_options}"
                )
            }

        grant_date = datetime.strptime(
            data["grant_date"], "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc)

        vesting_start_str = data.get("vesting_start_date") or data["grant_date"]
        vesting_start = datetime.strptime(
            vesting_start_str, "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc)

        vesting_type_str = data.get("vesting_type") or plan.default_vesting_type.value
        vesting_type = VestingType(vesting_type_str)

        grant = ESOPGrant(
            plan_id=plan_id,
            company_id=company_id,
            grantee_name=data["grantee_name"],
            grantee_email=data["grantee_email"],
            grantee_employee_id=data.get("grantee_employee_id"),
            grantee_designation=data.get("grantee_designation"),
            grant_date=grant_date,
            number_of_options=num_options,
            exercise_price=data.get("exercise_price") or plan.exercise_price,
            vesting_months=data.get("vesting_months") or plan.default_vesting_months,
            cliff_months=data.get("cliff_months") or plan.default_cliff_months,
            vesting_type=vesting_type,
            vesting_start_date=vesting_start,
            status=ESOPGrantStatus.DRAFT,
        )
        db.add(grant)

        # Increment pool allocation
        plan.pool_shares_allocated += num_options

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(grant)

        return self._serialize_grant(grant)

    def get_grant(
        self, db: Session, grant_id: int, company_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get grant details with computed vesting status."""
        grant = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.id == grant_id, ESOPGrant.company_id == company_id)
            .first()
        )
        if not grant:
            return None
        return self._serialize_grant(grant)

    def list_grants(
        self, db: Session, plan_id: int, company_id: int
    ) -> List[Dict[str, Any]]:
        """List all grants under a plan."""
        grants = (
            db.query(ESOPGrant)
            .filter(
                ESOPGrant.plan_id == plan_id,
                ESOPGrant.company_id == company_id,
            )
            .order_by(ESOPGrant.grant_date.desc())
            .all()
        )
        return [self._serialize_grant(g) for g in grants]

    def get_grants_by_company(
        self, db: Session, company_id: int
    ) -> List[Dict[str, Any]]:
        """List all grants across all plans for a company."""
        grants = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.company_id == company_id)
            .order_by(ESOPGrant.grant_date.desc())
            .all()
        )
        return [self._serialize_grant(g) for g in grants]

    # ------------------------------------------------------------------
    # Vesting Calculation
    # ------------------------------------------------------------------

    def calculate_vesting_schedule(
        self,
        vesting_start_date: datetime,
        number_of_options: int,
        vesting_months: int,
        cliff_months: int,
        vesting_type: str,
    ) -> List[Dict[str, Any]]:
        """
        Compute the full vesting schedule.

        Logic:
        - Nothing vests before cliff
        - At cliff: vest (cliff_months / vesting_months) * number_of_options
        - After cliff: vest remaining periodically
        - Final period gets remainder to ensure total = number_of_options
        """
        schedule = []

        if vesting_months <= 0 or number_of_options <= 0:
            return schedule

        # Determine period interval
        if vesting_type == "quarterly":
            period_months = 3
        elif vesting_type == "annually":
            period_months = 12
        else:
            period_months = 1  # monthly

        # Options that vest at cliff
        cliff_options = int((cliff_months / vesting_months) * number_of_options)

        # Remaining options after cliff
        remaining_after_cliff = number_of_options - cliff_options

        # Number of periods after cliff
        months_after_cliff = vesting_months - cliff_months
        if months_after_cliff <= 0:
            # Everything vests at cliff
            cliff_date = vesting_start_date + relativedelta(months=cliff_months)
            schedule.append({
                "date": cliff_date.strftime("%Y-%m-%d"),
                "options_vesting": number_of_options,
                "cumulative_vested": number_of_options,
                "percentage_vested": 100.0,
            })
            return schedule

        num_periods_after_cliff = max(1, months_after_cliff // period_months)
        options_per_period = remaining_after_cliff // num_periods_after_cliff if num_periods_after_cliff > 0 else 0

        cumulative = 0

        # Cliff vesting event
        cliff_date = vesting_start_date + relativedelta(months=cliff_months)
        cumulative += cliff_options
        schedule.append({
            "date": cliff_date.strftime("%Y-%m-%d"),
            "options_vesting": cliff_options,
            "cumulative_vested": cumulative,
            "percentage_vested": round(cumulative / number_of_options * 100, 2),
        })

        # Post-cliff periodic vesting
        for i in range(1, num_periods_after_cliff + 1):
            vesting_date = cliff_date + relativedelta(months=i * period_months)

            if i == num_periods_after_cliff:
                # Last period gets remainder
                options_this_period = number_of_options - cumulative
            else:
                options_this_period = options_per_period

            if options_this_period <= 0:
                continue

            cumulative += options_this_period
            schedule.append({
                "date": vesting_date.strftime("%Y-%m-%d"),
                "options_vesting": options_this_period,
                "cumulative_vested": cumulative,
                "percentage_vested": round(cumulative / number_of_options * 100, 2),
            })

        return schedule

    def get_vested_options(
        self, grant: ESOPGrant, as_of_date: Optional[datetime] = None
    ) -> int:
        """Compute how many options are vested as of a given date."""
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)

        schedule = self.calculate_vesting_schedule(
            vesting_start_date=grant.vesting_start_date,
            number_of_options=grant.number_of_options,
            vesting_months=grant.vesting_months,
            cliff_months=grant.cliff_months,
            vesting_type=grant.vesting_type.value if grant.vesting_type else "monthly",
        )

        vested = 0
        for entry in schedule:
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            if entry_date <= as_of_date:
                vested = entry["cumulative_vested"]
            else:
                break

        return vested

    # ------------------------------------------------------------------
    # Exercise Options
    # ------------------------------------------------------------------

    def exercise_options(
        self,
        db: Session,
        grant_id: int,
        company_id: int,
        num_options: int,
    ) -> Dict[str, Any]:
        """
        Exercise vested options.
        Creates share allotment via cap_table_service.
        """
        from src.services.cap_table_service import cap_table_service, AllotmentEntry

        grant = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.id == grant_id, ESOPGrant.company_id == company_id)
            .first()
        )
        if not grant:
            return {"error": "Grant not found"}

        vested = self.get_vested_options(grant)
        exercisable = vested - grant.options_exercised

        if num_options > exercisable:
            return {
                "error": (
                    f"Only {exercisable} options are exercisable "
                    f"(vested: {vested}, already exercised: {grant.options_exercised})"
                )
            }

        # Determine price per share: use FMV if plan basis is "fmv"
        exercise_price = grant.exercise_price
        fmv_used = None
        plan = db.query(ESOPPlan).filter(ESOPPlan.id == grant.plan_id).first()
        if plan and plan.exercise_price_basis == "fmv":
            from src.services.valuation_service import valuation_service
            latest = valuation_service.get_latest_valuation(db, company_id)
            if latest and latest.get("fair_market_value"):
                fmv_used = latest["fair_market_value"]
                exercise_price = max(exercise_price, fmv_used)

        # Create share allotment via cap table service
        entry = AllotmentEntry(
            name=grant.grantee_name,
            shares=num_options,
            share_type="equity",
            face_value=grant.exercise_price,
            paid_up_value=exercise_price,
            price_per_share=exercise_price,
            email=grant.grantee_email,
            is_promoter=False,
        )
        allotment_result = cap_table_service.record_allotment(
            db, company_id, [entry]
        )

        # Update grant
        grant.options_exercised += num_options
        if grant.options_exercised >= grant.number_of_options - grant.options_lapsed:
            grant.status = ESOPGrantStatus.FULLY_EXERCISED
        elif grant.options_exercised > 0:
            grant.status = ESOPGrantStatus.PARTIALLY_EXERCISED

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(grant)

        result = {
            "message": f"{num_options} options exercised successfully",
            "grant": self._serialize_grant(grant),
            "allotment": allotment_result,
        }
        if fmv_used is not None:
            result["fmv_per_share_used"] = fmv_used
        return result

    # ------------------------------------------------------------------
    # Grant Letter Generation
    # ------------------------------------------------------------------

    def generate_grant_letter(
        self,
        db: Session,
        grant_id: int,
        company_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Generate grant letter as a LegalDocument."""
        from src.models.legal_template import LegalDocument
        from src.models.company import Company

        grant = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.id == grant_id, ESOPGrant.company_id == company_id)
            .first()
        )
        if not grant:
            return {"error": "Grant not found"}

        plan = db.query(ESOPPlan).filter(ESOPPlan.id == grant.plan_id).first()
        company = db.query(Company).filter(Company.id == company_id).first()

        html = self._render_grant_letter_html(grant, plan, company)

        doc = LegalDocument(
            user_id=user_id,
            company_id=company_id,
            template_type="esop_grant_letter",
            title=f"ESOP Grant Letter - {grant.grantee_name}",
            generated_html=html,
            status="finalized",
        )
        db.add(doc)
        db.flush()

        grant.grant_letter_document_id = doc.id

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(doc)

        return {
            "message": "Grant letter generated successfully",
            "document_id": doc.id,
            "grant_id": grant.id,
        }

    def send_grant_letter_for_signing(
        self,
        db: Session,
        grant_id: int,
        company_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Create a SignatureRequest for the grant letter via esign_service."""
        from src.services.esign_service import esign_service
        from src.schemas.esign import SignatureRequestCreate, SignatoryCreate

        grant = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.id == grant_id, ESOPGrant.company_id == company_id)
            .first()
        )
        if not grant:
            return {"error": "Grant not found"}

        if not grant.grant_letter_document_id:
            return {"error": "Grant letter must be generated first"}

        sig_data = SignatureRequestCreate(
            legal_document_id=grant.grant_letter_document_id,
            title=f"ESOP Grant Letter - {grant.grantee_name}",
            message="Please review and sign your ESOP grant letter.",
            signing_order="sequential",
            expires_in_days=30,
            signatories=[
                SignatoryCreate(
                    name=grant.grantee_name,
                    email=grant.grantee_email,
                    designation=grant.grantee_designation or "Employee",
                    signing_order=1,
                ),
            ],
        )

        sig_request = esign_service.create_signature_request(
            db=db, user_id=user_id, data=sig_data
        )

        grant.acceptance_signature_request_id = sig_request.id
        grant.status = ESOPGrantStatus.OFFERED

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "message": "Grant letter sent for signing",
            "signature_request_id": sig_request.id,
            "grant_id": grant.id,
        }

    # ------------------------------------------------------------------
    # Pool Summary (for cap table integration)
    # ------------------------------------------------------------------

    def get_esop_pool_summary(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """Summary of ESOP pool for cap table display."""
        plans = (
            db.query(ESOPPlan)
            .filter(
                ESOPPlan.company_id == company_id,
                ESOPPlan.status.in_([
                    ESOPPlanStatus.ACTIVE,
                    ESOPPlanStatus.BOARD_APPROVED,
                    ESOPPlanStatus.SHAREHOLDER_APPROVED,
                ]),
            )
            .all()
        )

        total_pool = sum(p.pool_size for p in plans)
        total_allocated = sum(p.pool_shares_allocated for p in plans)
        total_available = total_pool - total_allocated

        # Get exercise/vesting data from grants
        grants = (
            db.query(ESOPGrant)
            .filter(
                ESOPGrant.company_id == company_id,
                ESOPGrant.status.notin_([
                    ESOPGrantStatus.CANCELLED,
                    ESOPGrantStatus.LAPSED,
                ]),
            )
            .all()
        )

        total_exercised = sum(g.options_exercised for g in grants)
        total_lapsed = sum(g.options_lapsed for g in grants)
        total_vested = sum(self.get_vested_options(g) for g in grants)
        total_unvested = total_allocated - total_vested - total_lapsed

        return {
            "total_pool": total_pool,
            "allocated": total_allocated,
            "available": total_available,
            "vested": total_vested,
            "unvested": max(0, total_unvested),
            "exercised": total_exercised,
            "lapsed": total_lapsed,
            "active_plans": len(plans),
            "active_grants": len(grants),
        }

    # ------------------------------------------------------------------
    # Approval State & Document Linking
    # ------------------------------------------------------------------

    def save_approval_state(
        self, db: Session, plan_id: int, company_id: int, state: dict
    ) -> Dict[str, Any]:
        """Persist the frontend approval-wizard state on the plan."""
        plan = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.id == plan_id, ESOPPlan.company_id == company_id)
            .first()
        )
        if not plan:
            return {"error": "Plan not found"}

        plan.approval_state = state

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(plan)

        return self._serialize_plan(db, plan)

    def link_document(
        self,
        db: Session,
        plan_id: int,
        company_id: int,
        doc_type: str,
        document_id: int,
    ) -> Dict[str, Any]:
        """Link a document (board resolution, shareholder resolution, or plan doc) to a plan."""
        plan = (
            db.query(ESOPPlan)
            .filter(ESOPPlan.id == plan_id, ESOPPlan.company_id == company_id)
            .first()
        )
        if not plan:
            return {"error": "Plan not found"}

        field_map = {
            "board_resolution": "board_resolution_document_id",
            "shareholder_resolution": "shareholder_resolution_document_id",
            "plan_document": "plan_document_id",
        }

        if doc_type not in field_map:
            return {
                "error": (
                    f"Invalid doc_type '{doc_type}'. "
                    f"Must be one of: {', '.join(field_map.keys())}"
                )
            }

        setattr(plan, field_map[doc_type], document_id)

        # Also record in approval_state
        current_state = plan.approval_state or {}
        current_state[f"{doc_type}_document_id"] = document_id
        plan.approval_state = current_state

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(plan)

        return self._serialize_plan(db, plan)

    # ------------------------------------------------------------------
    # Grant Acceptance Tracking
    # ------------------------------------------------------------------

    def check_grant_acceptance(
        self, db: Session, grant_id: int, company_id: int
    ) -> Dict[str, Any]:
        """
        Check whether the grantee has signed the grant letter.
        If all signatories have signed, update grant status to ACCEPTED.
        """
        from src.models.esign import SignatureRequest, Signatory

        grant = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.id == grant_id, ESOPGrant.company_id == company_id)
            .first()
        )
        if not grant:
            return {"error": "Grant not found"}

        if not grant.acceptance_signature_request_id:
            return {
                "grant_id": grant.id,
                "status": grant.status.value if grant.status else "draft",
                "acceptance_status": "no_signature_request",
                "accepted_at": None,
            }

        sig_request = (
            db.query(SignatureRequest)
            .filter(SignatureRequest.id == grant.acceptance_signature_request_id)
            .first()
        )
        if not sig_request:
            return {
                "grant_id": grant.id,
                "status": grant.status.value if grant.status else "draft",
                "acceptance_status": "signature_request_not_found",
                "accepted_at": None,
            }

        signatories = (
            db.query(Signatory)
            .filter(Signatory.signature_request_id == sig_request.id)
            .all()
        )

        all_signed = all(s.status == "signed" for s in signatories) and len(signatories) > 0

        if all_signed and grant.status != ESOPGrantStatus.ACCEPTED:
            grant.status = ESOPGrantStatus.ACCEPTED
            grant.accepted_at = datetime.now(timezone.utc)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise
            db.refresh(grant)

        return {
            "grant_id": grant.id,
            "status": grant.status.value if grant.status else "draft",
            "acceptance_status": "accepted" if all_signed else "pending",
            "accepted_at": grant.accepted_at.isoformat() if grant.accepted_at else None,
            "signature_request_status": sig_request.status,
            "signatories": [
                {
                    "name": s.name,
                    "email": s.email,
                    "status": s.status,
                    "signed_at": s.signed_at.isoformat() if s.signed_at else None,
                }
                for s in signatories
            ],
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _render_grant_letter_html(
        self, grant: ESOPGrant, plan: ESOPPlan, company
    ) -> str:
        """Render grant letter HTML."""
        company_name = company.approved_name or "the Company"
        grant_date_str = grant.grant_date.strftime("%d %B %Y") if grant.grant_date else "N/A"
        vesting_start_str = grant.vesting_start_date.strftime("%d %B %Y") if grant.vesting_start_date else grant_date_str

        cliff_years = grant.cliff_months / 12
        vesting_years = grant.vesting_months / 12

        return f"""
        <div style="font-family: 'Inter', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px;">
            <div style="text-align: center; margin-bottom: 40px;">
                <h1 style="font-size: 24px; margin-bottom: 8px;">EMPLOYEE STOCK OPTION GRANT LETTER</h1>
                <p style="color: #666; font-size: 14px;">Under {plan.plan_name}</p>
            </div>

            <div style="margin-bottom: 24px;">
                <p><strong>Date:</strong> {grant_date_str}</p>
                <p><strong>To:</strong> {grant.grantee_name}</p>
                {f'<p><strong>Designation:</strong> {grant.grantee_designation}</p>' if grant.grantee_designation else ''}
                {f'<p><strong>Employee ID:</strong> {grant.grantee_employee_id}</p>' if grant.grantee_employee_id else ''}
            </div>

            <div style="margin-bottom: 24px;">
                <p>Dear {grant.grantee_name},</p>
                <p>We are pleased to inform you that the Board of Directors of <strong>{company_name}</strong>
                has approved a grant of stock options to you under the <strong>{plan.plan_name}</strong>,
                subject to the terms and conditions set forth herein and in the Plan.</p>
            </div>

            <h2 style="font-size: 18px; border-bottom: 2px solid #7c3aed; padding-bottom: 8px;">Grant Details</h2>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 600; width: 40%;">Number of Options Granted</td>
                    <td style="padding: 12px;">{grant.number_of_options:,}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 600;">Exercise Price per Option</td>
                    <td style="padding: 12px;">Rs {grant.exercise_price:,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 600;">Grant Date</td>
                    <td style="padding: 12px;">{grant_date_str}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 600;">Vesting Commencement Date</td>
                    <td style="padding: 12px;">{vesting_start_str}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 600;">Vesting Period</td>
                    <td style="padding: 12px;">{vesting_years:.0f} years ({grant.vesting_months} months)</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 600;">Cliff Period</td>
                    <td style="padding: 12px;">{cliff_years:.0f} year(s) ({grant.cliff_months} months)</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 600;">Vesting Schedule</td>
                    <td style="padding: 12px;">{grant.vesting_type.value.capitalize()} after cliff</td>
                </tr>
            </table>

            <h2 style="font-size: 18px; border-bottom: 2px solid #7c3aed; padding-bottom: 8px;">Vesting Schedule</h2>
            <div style="margin-bottom: 24px;">
                <p>The options shall vest as follows:</p>
                <ul>
                    <li>No options shall vest during the first {grant.cliff_months} months (Cliff Period).</li>
                    <li>At the end of the Cliff Period, {int((grant.cliff_months / grant.vesting_months) * 100)}% of
                        the options ({int((grant.cliff_months / grant.vesting_months) * grant.number_of_options):,} options)
                        shall vest.</li>
                    <li>The remaining options shall vest {grant.vesting_type.value} over the balance of the
                        vesting period.</li>
                </ul>
            </div>

            <h2 style="font-size: 18px; border-bottom: 2px solid #7c3aed; padding-bottom: 8px;">Key Terms</h2>
            <div style="margin-bottom: 24px;">
                <ol>
                    <li><strong>Exercise:</strong> Vested options may be exercised by paying the Exercise Price
                        per option. Upon exercise, equity shares of the Company shall be allotted to you.</li>
                    <li><strong>Termination:</strong> If your employment is terminated for any reason, unvested
                        options shall lapse immediately. Vested but unexercised options must be exercised within
                        90 days of termination, failing which they shall lapse.</li>
                    <li><strong>Transfer Restrictions:</strong> Options granted under this letter are personal
                        to you and are non-transferable.</li>
                    <li><strong>Tax Obligations:</strong> You shall be responsible for all tax obligations
                        arising from the grant, vesting, and exercise of these options, including any perquisite
                        tax under Section 17(2) of the Income Tax Act, 1961.</li>
                    {f'''<li><strong>DPIIT Tax Deferral:</strong> The Company is a DPIIT-recognized startup
                        (Recognition No. {plan.dpiit_recognition_number}). Under Section 80-IAC and the
                        DPIIT notification dated 19 February 2019, the perquisite tax arising on exercise
                        of these options is deferred for a period of 5 years from the date of exercise,
                        or until the date of sale of the shares, or until the date of cessation of
                        employment — whichever is earliest.</li>''' if plan.dpiit_recognized and plan.dpiit_recognition_number else ''}
                    <li><strong>Governing Law:</strong> This grant is governed by the Companies Act, 2013
                        (Section 62(1)(b)) and the rules made thereunder.</li>
                </ol>
            </div>

            <div style="margin-bottom: 40px;">
                <p>This grant is subject to the terms and conditions of the {plan.plan_name} and applicable laws.
                In case of any conflict between this letter and the Plan, the Plan shall prevail.</p>
            </div>

            <div style="margin-top: 60px;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <p style="margin-bottom: 40px;"><strong>For {company_name}</strong></p>
                        <p>_________________________</p>
                        <p>Authorized Signatory</p>
                    </div>
                    <div>
                        <p style="margin-bottom: 40px;"><strong>Acknowledgement by Employee</strong></p>
                        <p>_________________________</p>
                        <p>{grant.grantee_name}</p>
                    </div>
                </div>
            </div>
        </div>
        """

    def _serialize_plan(
        self, db: Session, plan: ESOPPlan
    ) -> Dict[str, Any]:
        """Serialize ESOPPlan to dict with computed fields."""
        grants = (
            db.query(ESOPGrant)
            .filter(ESOPGrant.plan_id == plan.id)
            .all()
        )
        active_statuses = {
            ESOPGrantStatus.DRAFT,
            ESOPGrantStatus.OFFERED,
            ESOPGrantStatus.ACCEPTED,
            ESOPGrantStatus.ACTIVE,
            ESOPGrantStatus.PARTIALLY_EXERCISED,
        }

        return {
            "id": plan.id,
            "company_id": plan.company_id,
            "plan_name": plan.plan_name,
            "pool_size": plan.pool_size,
            "pool_shares_allocated": plan.pool_shares_allocated,
            "pool_available": plan.pool_size - plan.pool_shares_allocated,
            "default_vesting_months": plan.default_vesting_months,
            "default_cliff_months": plan.default_cliff_months,
            "default_vesting_type": plan.default_vesting_type.value if plan.default_vesting_type else "monthly",
            "exercise_price": plan.exercise_price,
            "exercise_price_basis": plan.exercise_price_basis,
            "effective_date": plan.effective_date.isoformat() if plan.effective_date else None,
            "expiry_date": plan.expiry_date.isoformat() if plan.expiry_date else None,
            "status": plan.status.value if plan.status else "draft",
            "dpiit_recognized": plan.dpiit_recognized or False,
            "dpiit_recognition_number": plan.dpiit_recognition_number,
            "tax_deferral_eligible": bool(plan.dpiit_recognized and plan.dpiit_recognition_number),
            "approval_state": plan.approval_state or {},
            "board_resolution_document_id": plan.board_resolution_document_id,
            "shareholder_resolution_document_id": plan.shareholder_resolution_document_id,
            "plan_document_id": plan.plan_document_id,
            "board_resolution_date": plan.board_resolution_date.isoformat() if plan.board_resolution_date else None,
            "shareholder_resolution_date": plan.shareholder_resolution_date.isoformat() if plan.shareholder_resolution_date else None,
            "total_grants": len(grants),
            "active_grants": sum(1 for g in grants if g.status in active_statuses),
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
        }

    def _serialize_grant(
        self,
        grant: ESOPGrant,
        as_of_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Serialize ESOPGrant to dict with computed vesting data."""
        vested = self.get_vested_options(grant, as_of_date)
        exercisable = max(0, vested - grant.options_exercised)
        unvested = max(0, grant.number_of_options - vested - grant.options_lapsed)

        schedule = self.calculate_vesting_schedule(
            vesting_start_date=grant.vesting_start_date,
            number_of_options=grant.number_of_options,
            vesting_months=grant.vesting_months,
            cliff_months=grant.cliff_months,
            vesting_type=grant.vesting_type.value if grant.vesting_type else "monthly",
        )

        return {
            "id": grant.id,
            "plan_id": grant.plan_id,
            "company_id": grant.company_id,
            "grantee_name": grant.grantee_name,
            "grantee_email": grant.grantee_email,
            "grantee_employee_id": grant.grantee_employee_id,
            "grantee_designation": grant.grantee_designation,
            "grant_date": grant.grant_date.strftime("%Y-%m-%d") if grant.grant_date else None,
            "number_of_options": grant.number_of_options,
            "exercise_price": grant.exercise_price,
            "vesting_months": grant.vesting_months,
            "cliff_months": grant.cliff_months,
            "vesting_type": grant.vesting_type.value if grant.vesting_type else "monthly",
            "vesting_start_date": grant.vesting_start_date.strftime("%Y-%m-%d") if grant.vesting_start_date else None,
            "options_vested": vested,
            "options_exercised": grant.options_exercised,
            "options_unvested": unvested,
            "options_exercisable": exercisable,
            "options_lapsed": grant.options_lapsed,
            "status": grant.status.value if grant.status else "draft",
            "grant_letter_document_id": grant.grant_letter_document_id,
            "accepted_at": grant.accepted_at.isoformat() if grant.accepted_at else None,
            "acceptance_signature_request_id": grant.acceptance_signature_request_id,
            "vesting_schedule": schedule,
            "created_at": grant.created_at.isoformat() if grant.created_at else None,
            "updated_at": grant.updated_at.isoformat() if grant.updated_at else None,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
esop_service = ESOPService()
