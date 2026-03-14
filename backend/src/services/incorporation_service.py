"""
Incorporation Workflow Service — entity-specific workflow orchestration.

Each entity type has a distinct sequence of steps for incorporation.
This service manages the ordered execution of those steps, tracks progress,
and coordinates between the various sub-services (DSC, MCA forms, legal docs, etc.).
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.models.company import Company, CompanyStatus, EntityType
from src.models.director import Director
from src.models.task import AgentLog
from src.services.dsc_service import dsc_service, DSCRequest
from src.services.mca_form_service import mca_form_service
from src.services.legal_document_service import legal_document_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Workflow Step Definitions
# ---------------------------------------------------------------------------

WORKFLOW_STEPS: Dict[str, List[Dict[str, Any]]] = {
    "private_limited": [
        {"key": "dsc", "name": "DSC Procurement", "description": "Obtain Digital Signature Certificates for all directors"},
        {"key": "din", "name": "DIN Application", "description": "Apply for Director Identification Number via DIR-3"},
        {"key": "run", "name": "Name Reservation (RUN)", "description": "Reserve company name through RUN (INC-1) form"},
        {"key": "spice_part_a", "name": "SPICe+ Part A", "description": "File SPICe+ Part A for name approval"},
        {"key": "spice_part_b", "name": "SPICe+ Part B", "description": "File SPICe+ Part B with incorporation details"},
        {"key": "moa_aoa", "name": "MOA & AOA Drafting", "description": "Draft Memorandum and Articles of Association"},
        {"key": "filing", "name": "MCA Filing", "description": "Submit complete filing package to MCA"},
    ],
    "opc": [
        {"key": "nominee", "name": "Nominee Declaration", "description": "File INC-3 nominee declaration form"},
        {"key": "dsc", "name": "DSC Procurement", "description": "Obtain Digital Signature Certificate for sole member"},
        {"key": "din", "name": "DIN Application", "description": "Apply for Director Identification Number via DIR-3"},
        {"key": "run", "name": "Name Reservation (RUN)", "description": "Reserve company name through RUN (INC-1) form"},
        {"key": "spice_plus", "name": "SPICe+ Filing", "description": "File SPICe+ with INC-3 attachment"},
        {"key": "moa_aoa", "name": "MOA & AOA Drafting", "description": "Draft Memorandum and Articles of Association (OPC format)"},
        {"key": "filing", "name": "MCA Filing", "description": "Submit complete filing package to MCA"},
    ],
    "llp": [
        {"key": "dsc", "name": "DSC Procurement", "description": "Obtain Digital Signature Certificates for designated partners"},
        {"key": "dpin", "name": "DPIN Application", "description": "Apply for Designated Partner Identification Number"},
        {"key": "run_llp", "name": "Name Reservation (RUN-LLP)", "description": "Reserve LLP name through RUN-LLP form"},
        {"key": "fillip", "name": "FiLLiP Filing", "description": "File FiLLiP form for LLP incorporation"},
        {"key": "llp_agreement", "name": "LLP Agreement", "description": "Draft and execute LLP Agreement"},
        {"key": "filing", "name": "ROC Filing", "description": "File Form 3 (LLP Agreement) with ROC within 30 days"},
    ],
    "section_8": [
        {"key": "inc12", "name": "INC-12 License Application", "description": "Apply for Section 8 license from Regional Director"},
        {"key": "license_wait", "name": "License Approval Wait", "description": "Await Regional Director license approval (2-3 months)"},
        {"key": "dsc", "name": "DSC Procurement", "description": "Obtain Digital Signature Certificates for directors"},
        {"key": "din", "name": "DIN Application", "description": "Apply for Director Identification Number via DIR-3"},
        {"key": "spice_plus", "name": "SPICe+ Filing", "description": "File SPICe+ with license number"},
        {"key": "filing", "name": "MCA Filing", "description": "Submit complete filing package to MCA"},
    ],
    "sole_proprietorship": [
        {"key": "gst", "name": "GST Registration", "description": "Apply for GST registration (REG-01) as primary step"},
        {"key": "udyam", "name": "MSME/Udyam Registration", "description": "Obtain Udyam Registration for MSME benefits"},
        {"key": "shop_act", "name": "Shop & Establishment Act", "description": "State-wise Shop & Establishment Act license guidance"},
    ],
}


def _get_step_status(step_index: int, current_index: int) -> str:
    """Return the status of a step relative to the current progress."""
    if step_index < current_index:
        return "completed"
    elif step_index == current_index:
        return "current"
    else:
        return "upcoming"


class IncorporationService:
    """
    Entity-specific workflow orchestration for incorporation.

    Each entity type has a specific ordered workflow. This service manages
    execution, progress tracking, and coordination between sub-services.
    """

    def _log(self, db: Session, company_id: int, message: str, level: str = "INFO") -> None:
        try:
            entry = AgentLog(
                company_id=company_id,
                agent_name="Service: Incorporation Workflow",
                message=message,
                level=level,
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()

    # ------------------------------------------------------------------
    # Workflow Routing
    # ------------------------------------------------------------------

    async def start_workflow(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Route to the entity-specific workflow based on company.entity_type."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        entity_type = company.entity_type.value if hasattr(company.entity_type, "value") else str(company.entity_type)

        workflow_map = {
            "private_limited": self.start_pvt_ltd_workflow,
            "opc": self.start_opc_workflow,
            "llp": self.start_llp_workflow,
            "section_8": self.start_section8_workflow,
            "sole_proprietorship": self.start_sole_prop_workflow,
        }

        handler = workflow_map.get(entity_type)
        if not handler:
            return {
                "success": False,
                "error": f"No workflow defined for entity type: {entity_type}",
            }

        self._log(
            db, company_id,
            f"Starting {entity_type} incorporation workflow for company {company_id}.",
        )

        return await handler(db, company_id)

    # ------------------------------------------------------------------
    # Private Limited Workflow
    # ------------------------------------------------------------------

    async def start_pvt_ltd_workflow(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Private Limited Company workflow:
        DSC -> DIN -> RUN -> SPICe+ Part A -> Part B -> MOA/AOA -> Filing
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(Director.company_id == company_id).all()
        results: Dict[str, Any] = {"steps_completed": []}

        # Step 1: DSC Procurement
        self._log(db, company_id, "Step 1/7: Initiating DSC procurement for all directors...")
        for director in directors:
            dsc_req = DSCRequest(
                director_id=director.id,
                full_name=director.full_name,
                email=director.email or "",
                phone=director.phone or "",
                pan_number=director.pan_number or "",
                dsc_class=3,
                validity_years=2,
            )
            dsc_result = await dsc_service.initiate_dsc_procurement(db, director.id, dsc_req)
            if not dsc_result.get("success"):
                self._log(db, company_id, f"DSC procurement failed for {director.full_name}: {dsc_result.get('error')}", "ERROR")
                return {"success": False, "error": f"DSC procurement failed for {director.full_name}", "details": dsc_result}
        results["steps_completed"].append("dsc")
        company.status = CompanyStatus.DSC_OBTAINED
        db.commit()

        # Step 2: DIN Application
        self._log(db, company_id, "Step 2/7: Processing DIN applications for directors...")
        for director in directors:
            if not director.din:
                director.din = f"DIN-{director.id:08d}"  # Simulated DIN
                self._log(db, company_id, f"DIN assigned to {director.full_name}: {director.din}")
        db.commit()
        results["steps_completed"].append("din")

        # Step 3: Name Reservation (RUN)
        self._log(db, company_id, "Step 3/7: Generating RUN form for name reservation...")
        proposed_names = company.proposed_names or []
        if proposed_names:
            run_data = mca_form_service.generate_run(
                proposed_names=proposed_names,
                entity_type="private_limited",
                state=company.state,
            )
            results["run_form"] = run_data
        results["steps_completed"].append("run")

        # Step 4: SPICe+ Part A
        self._log(db, company_id, "Step 4/7: Generating SPICe+ Part A for name approval...")
        director_dicts = self._directors_to_dicts(directors)
        spice_data = mca_form_service.generate_spice_plus(
            company_name=company.approved_name or proposed_names[0] if proposed_names else "",
            entity_type="private_limited",
            state=company.state,
            authorized_capital=company.authorized_capital,
            directors=director_dicts,
        )
        results["spice_form"] = spice_data
        results["steps_completed"].append("spice_part_a")

        # Step 5: SPICe+ Part B
        self._log(db, company_id, "Step 5/7: SPICe+ Part B — incorporation details populated...")
        results["steps_completed"].append("spice_part_b")

        # Step 6: MOA & AOA
        self._log(db, company_id, "Step 6/7: Drafting MOA and AOA...")
        doc_set = await legal_document_service.generate_full_document_set(
            company_name=company.approved_name or "(Proposed Company)",
            entity_type="private_limited",
            state=company.state,
            authorized_capital=company.authorized_capital,
            directors=director_dicts,
        )
        results["legal_documents"] = doc_set
        results["steps_completed"].append("moa_aoa")

        # Step 7: Filing
        self._log(db, company_id, "Step 7/7: Filing package prepared for MCA submission.")
        company.status = CompanyStatus.FILING_DRAFTED
        db.commit()
        results["steps_completed"].append("filing")

        self._log(db, company_id, "Private Limited incorporation workflow completed successfully.", "SUCCESS")
        return {"success": True, "entity_type": "private_limited", "results": results}

    # ------------------------------------------------------------------
    # OPC Workflow
    # ------------------------------------------------------------------

    async def start_opc_workflow(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        OPC workflow:
        Nominee Declaration -> DSC -> DIN -> RUN -> SPICe+ -> MOA/AOA -> Filing
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(Director.company_id == company_id).all()
        results: Dict[str, Any] = {"steps_completed": []}

        # Step 1: Nominee Declaration (INC-3)
        self._log(db, company_id, "Step 1/7: Generating OPC nominee declaration (INC-3)...")
        from src.services.opc_service import opc_service
        nominee_result = await opc_service.generate_nominee_declaration(db, company_id)
        if nominee_result.get("success"):
            results["nominee_declaration"] = nominee_result.get("form_data")
        else:
            self._log(db, company_id, f"Nominee declaration failed: {nominee_result.get('error')}", "ERROR")
        results["steps_completed"].append("nominee")

        # Step 2: DSC
        self._log(db, company_id, "Step 2/7: Initiating DSC procurement for sole member...")
        sole_member = next((d for d in directors if not d.is_nominee), None)
        if sole_member:
            dsc_req = DSCRequest(
                director_id=sole_member.id,
                full_name=sole_member.full_name,
                email=sole_member.email or "",
                phone=sole_member.phone or "",
                pan_number=sole_member.pan_number or "",
                dsc_class=3,
                validity_years=2,
            )
            await dsc_service.initiate_dsc_procurement(db, sole_member.id, dsc_req)
        company.status = CompanyStatus.DSC_OBTAINED
        db.commit()
        results["steps_completed"].append("dsc")

        # Step 3: DIN
        self._log(db, company_id, "Step 3/7: Processing DIN application for sole member...")
        if sole_member and not sole_member.din:
            sole_member.din = f"DIN-{sole_member.id:08d}"
            db.commit()
        results["steps_completed"].append("din")

        # Step 4: RUN
        self._log(db, company_id, "Step 4/7: Generating RUN form for name reservation...")
        proposed_names = company.proposed_names or []
        if proposed_names:
            run_data = mca_form_service.generate_run(
                proposed_names=proposed_names,
                entity_type="opc",
                state=company.state,
            )
            results["run_form"] = run_data
        results["steps_completed"].append("run")

        # Step 5: SPICe+
        self._log(db, company_id, "Step 5/7: Generating SPICe+ form (with INC-3 attachment)...")
        director_dicts = self._directors_to_dicts(directors)
        spice_data = mca_form_service.generate_spice_plus(
            company_name=company.approved_name or proposed_names[0] if proposed_names else "",
            entity_type="opc",
            state=company.state,
            authorized_capital=company.authorized_capital,
            directors=director_dicts,
        )
        results["spice_form"] = spice_data
        results["steps_completed"].append("spice_plus")

        # Step 6: MOA & AOA
        self._log(db, company_id, "Step 6/7: Drafting MOA and AOA (OPC format)...")
        doc_set = await legal_document_service.generate_full_document_set(
            company_name=company.approved_name or "(Proposed OPC)",
            entity_type="opc",
            state=company.state,
            authorized_capital=company.authorized_capital,
            directors=director_dicts,
        )
        results["legal_documents"] = doc_set
        results["steps_completed"].append("moa_aoa")

        # Step 7: Filing
        self._log(db, company_id, "Step 7/7: OPC filing package prepared for MCA submission.")
        company.status = CompanyStatus.FILING_DRAFTED
        db.commit()
        results["steps_completed"].append("filing")

        self._log(db, company_id, "OPC incorporation workflow completed successfully.", "SUCCESS")
        return {"success": True, "entity_type": "opc", "results": results}

    # ------------------------------------------------------------------
    # LLP Workflow
    # ------------------------------------------------------------------

    async def start_llp_workflow(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        LLP workflow:
        DSC -> DPIN -> RUN-LLP -> FiLLiP -> LLP Agreement -> Filing
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(Director.company_id == company_id).all()
        results: Dict[str, Any] = {"steps_completed": []}

        # Step 1: DSC
        self._log(db, company_id, "Step 1/6: Initiating DSC procurement for designated partners...")
        for director in directors:
            dsc_req = DSCRequest(
                director_id=director.id,
                full_name=director.full_name,
                email=director.email or "",
                phone=director.phone or "",
                pan_number=director.pan_number or "",
                dsc_class=3,
                validity_years=2,
            )
            await dsc_service.initiate_dsc_procurement(db, director.id, dsc_req)
        company.status = CompanyStatus.DSC_OBTAINED
        db.commit()
        results["steps_completed"].append("dsc")

        # Step 2: DPIN
        self._log(db, company_id, "Step 2/6: Processing DPIN applications for designated partners...")
        from src.services.llp_service import llp_service
        for director in directors:
            if not director.dpin:
                dpin_result = await llp_service.generate_dpin_application(db, director.id)
                if dpin_result.get("success"):
                    director.dpin = f"DPIN-{director.id:08d}"  # Simulated
                    self._log(db, company_id, f"DPIN assigned to {director.full_name}: {director.dpin}")
        db.commit()
        results["steps_completed"].append("dpin")

        # Step 3: RUN-LLP
        self._log(db, company_id, "Step 3/6: Generating RUN-LLP form for name reservation...")
        proposed_names = company.proposed_names or []
        if proposed_names:
            run_data = mca_form_service.generate_run(
                proposed_names=proposed_names,
                entity_type="llp",
                state=company.state,
            )
            results["run_form"] = run_data
        results["steps_completed"].append("run_llp")

        # Step 4: FiLLiP
        self._log(db, company_id, "Step 4/6: Generating FiLLiP form for LLP incorporation...")
        fillip_result = await llp_service.generate_fillip_form(db, company_id)
        if fillip_result.get("success"):
            results["fillip_form"] = fillip_result.get("form_data")
        results["steps_completed"].append("fillip")

        # Step 5: LLP Agreement
        self._log(db, company_id, "Step 5/6: Drafting LLP Agreement...")
        agreement_result = await llp_service.generate_llp_agreement(db, company_id)
        if agreement_result.get("success"):
            results["llp_agreement"] = agreement_result.get("agreement")
        results["steps_completed"].append("llp_agreement")

        # Step 6: Filing
        self._log(db, company_id, "Step 6/6: LLP filing package prepared. Generating Form 3 for ROC filing...")
        form3_result = await llp_service.generate_form3(db, company_id)
        if form3_result.get("success"):
            results["form3"] = form3_result.get("form_data")
        company.status = CompanyStatus.FILING_DRAFTED
        db.commit()
        results["steps_completed"].append("filing")

        self._log(db, company_id, "LLP incorporation workflow completed successfully.", "SUCCESS")
        return {"success": True, "entity_type": "llp", "results": results}

    # ------------------------------------------------------------------
    # Section 8 Workflow
    # ------------------------------------------------------------------

    async def start_section8_workflow(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Section 8 workflow:
        INC-12 License -> Wait -> DSC -> DIN -> SPICe+ -> Filing
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(Director.company_id == company_id).all()
        results: Dict[str, Any] = {"steps_completed": []}

        # Step 1: INC-12 License Application
        self._log(db, company_id, "Step 1/6: Generating INC-12 license application for Section 8 company...")
        from src.services.section8_service import section8_service
        inc12_result = await section8_service.generate_inc12_application(db, company_id)
        if inc12_result.get("success"):
            results["inc12_form"] = inc12_result.get("form_data")

        # Generate supporting documents
        projection_result = await section8_service.generate_income_projection(db, company_id)
        if projection_result.get("success"):
            results["income_projection"] = projection_result.get("projection")

        declaration_result = await section8_service.generate_director_declaration(db, company_id)
        if declaration_result.get("success"):
            results["director_declarations"] = declaration_result.get("declarations")

        results["steps_completed"].append("inc12")

        # Step 2: License Wait (simulated as immediate in dev)
        self._log(db, company_id, "Step 2/6: Section 8 license application submitted. Awaiting Regional Director approval...")
        self._log(db, company_id, "[DEV] License approval simulated as immediate.", "SUCCESS")
        # In dev mode, update company data to reflect license approval
        data = company.data or {}
        data["section8_license"] = {
            "status": "approved",
            "license_number": f"S8-LIC-{company_id:06d}",
            "license_date": datetime.now(timezone.utc).date().isoformat(),
        }
        company.data = data
        db.commit()
        results["steps_completed"].append("license_wait")

        # Step 3: DSC
        self._log(db, company_id, "Step 3/6: Initiating DSC procurement for directors...")
        for director in directors:
            dsc_req = DSCRequest(
                director_id=director.id,
                full_name=director.full_name,
                email=director.email or "",
                phone=director.phone or "",
                pan_number=director.pan_number or "",
                dsc_class=3,
                validity_years=2,
            )
            await dsc_service.initiate_dsc_procurement(db, director.id, dsc_req)
        company.status = CompanyStatus.DSC_OBTAINED
        db.commit()
        results["steps_completed"].append("dsc")

        # Step 4: DIN
        self._log(db, company_id, "Step 4/6: Processing DIN applications for directors...")
        for director in directors:
            if not director.din:
                director.din = f"DIN-{director.id:08d}"
                self._log(db, company_id, f"DIN assigned to {director.full_name}: {director.din}")
        db.commit()
        results["steps_completed"].append("din")

        # Step 5: SPICe+
        self._log(db, company_id, "Step 5/6: Generating SPICe+ form (with Section 8 license number)...")
        director_dicts = self._directors_to_dicts(directors)
        spice_data = mca_form_service.generate_spice_plus(
            company_name=company.approved_name or "(Proposed Section 8 Company)",
            entity_type="section_8",
            state=company.state,
            authorized_capital=company.authorized_capital,
            directors=director_dicts,
        )
        results["spice_form"] = spice_data
        results["steps_completed"].append("spice_plus")

        # Step 6: Filing
        self._log(db, company_id, "Step 6/6: Section 8 filing package prepared for MCA submission.")
        company.status = CompanyStatus.FILING_DRAFTED
        db.commit()
        results["steps_completed"].append("filing")

        self._log(db, company_id, "Section 8 incorporation workflow completed successfully.", "SUCCESS")
        return {"success": True, "entity_type": "section_8", "results": results}

    # ------------------------------------------------------------------
    # Sole Proprietorship Workflow
    # ------------------------------------------------------------------

    async def start_sole_prop_workflow(
        self, db: Session, company_id: int
    ) -> Dict[str, Any]:
        """
        Sole Proprietorship workflow:
        GST Registration -> MSME/Udyam -> Shop Act Guidance
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        directors = db.query(Director).filter(Director.company_id == company_id).all()
        owner = directors[0] if directors else None
        results: Dict[str, Any] = {"steps_completed": []}

        from src.services.sole_prop_service import sole_prop_service

        # Step 1: GST Registration
        self._log(db, company_id, "Step 1/3: Generating GST registration (REG-01) form data...")
        owner_details = {
            "full_name": owner.full_name if owner else "",
            "pan_number": owner.pan_number if owner else "",
            "aadhaar_number": owner.aadhaar_number if owner else "",
            "email": owner.email if owner else "",
            "phone": owner.phone if owner else "",
            "state": company.state,
            "business_address": owner.address if owner else "",
        }
        gst_data = sole_prop_service.generate_gst_registration_data(owner_details)
        results["gst_registration"] = gst_data
        results["steps_completed"].append("gst")

        # Step 2: Udyam Registration
        self._log(db, company_id, "Step 2/3: Generating MSME/Udyam registration data...")
        business_details = {
            "business_name": company.approved_name or "(Business Name)",
            "type": "Service",
            "activity": "",
            "investment": 0,
            "turnover": 0,
            "address": owner.address if owner else "",
            "district": "",
            "pincode": "",
        }
        udyam_data = sole_prop_service.generate_udyam_registration(owner_details, business_details)
        results["udyam_registration"] = udyam_data
        results["steps_completed"].append("udyam")

        # Step 3: Shop Act Guidance
        self._log(db, company_id, f"Step 3/3: Providing Shop & Establishment Act guidance for {company.state}...")
        shop_act = sole_prop_service.get_shop_act_guidance(company.state)
        results["shop_act_guidance"] = shop_act
        results["steps_completed"].append("shop_act")

        # Mark as drafted (sole prop doesn't go through MCA filing)
        company.status = CompanyStatus.FILING_DRAFTED
        db.commit()

        self._log(db, company_id, "Sole Proprietorship registration workflow completed successfully.", "SUCCESS")
        return {"success": True, "entity_type": "sole_proprietorship", "results": results}

    # ------------------------------------------------------------------
    # Step Information
    # ------------------------------------------------------------------

    def get_workflow_steps(self, entity_type: str) -> List[Dict[str, Any]]:
        """Return the ordered list of steps for an entity type."""
        et = entity_type.value if hasattr(entity_type, "value") else str(entity_type)
        steps = WORKFLOW_STEPS.get(et, [])
        return [
            {
                "index": i,
                "key": step["key"],
                "name": step["name"],
                "description": step["description"],
            }
            for i, step in enumerate(steps)
        ]

    def get_current_step(self, company: Company) -> Dict[str, Any]:
        """
        Determine the current step based on the company's status.

        Maps CompanyStatus to the corresponding workflow step index.
        """
        entity_type = company.entity_type.value if hasattr(company.entity_type, "value") else str(company.entity_type)
        steps = WORKFLOW_STEPS.get(entity_type, [])

        if not steps:
            return {
                "entity_type": entity_type,
                "steps": [],
                "current_step_index": -1,
                "message": "No workflow defined for this entity type.",
            }

        # Map status to approximate step index
        status_val = company.status.value if hasattr(company.status, "value") else str(company.status)
        status_to_step: Dict[str, int] = {
            "draft": 0,
            "entity_selected": 0,
            "payment_pending": 0,
            "payment_completed": 0,
            "documents_pending": 0,
            "documents_uploaded": 0,
            "documents_verified": 0,
            "name_pending": 0,
            "name_reserved": 1,
            "name_rejected": 0,
            "dsc_in_progress": 0,
            "dsc_obtained": 1,
            "filing_drafted": len(steps) - 1,
            "filing_under_review": len(steps) - 1,
            "filing_submitted": len(steps),
            "mca_processing": len(steps),
            "mca_query": len(steps) - 1,
            "incorporated": len(steps),
            "bank_account_pending": len(steps),
            "bank_account_opened": len(steps),
            "inc20a_pending": len(steps),
            "fully_setup": len(steps),
        }

        current_index = status_to_step.get(status_val, 0)

        enriched_steps = []
        for i, step in enumerate(steps):
            enriched_steps.append({
                "index": i,
                "key": step["key"],
                "name": step["name"],
                "description": step["description"],
                "status": _get_step_status(i, current_index),
            })

        total_steps = len(steps)
        completed_steps = min(current_index, total_steps)

        return {
            "entity_type": entity_type,
            "company_status": status_val,
            "steps": enriched_steps,
            "current_step_index": current_index,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_pct": round((completed_steps / total_steps) * 100) if total_steps > 0 else 0,
        }

    # ------------------------------------------------------------------
    # Next Step Trigger
    # ------------------------------------------------------------------

    async def trigger_next_step(self, db: Session, company_id: int) -> Dict[str, Any]:
        """
        Trigger the next step in the workflow.

        This is used by the frontend "Next Step" button to advance the workflow.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        current = self.get_current_step(company)
        current_index = current.get("current_step_index", 0)
        steps = current.get("steps", [])

        if current_index >= len(steps):
            return {
                "success": True,
                "message": "All workflow steps are completed.",
                "current_step": current,
            }

        # If the workflow hasn't started at all, start the full workflow
        if current_index == 0:
            return await self.start_workflow(db, company_id)

        # Otherwise, return the current step info for manual action
        current_step = steps[current_index] if current_index < len(steps) else None

        return {
            "success": True,
            "message": f"Current step: {current_step['name']}" if current_step else "Workflow in progress",
            "current_step": current_step,
            "workflow_progress": current,
        }

    # ------------------------------------------------------------------
    # Form Collection
    # ------------------------------------------------------------------

    async def get_all_forms(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Retrieve all generated form data for a company."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"success": False, "error": "Company not found"}

        entity_type = company.entity_type.value if hasattr(company.entity_type, "value") else str(company.entity_type)
        directors = db.query(Director).filter(Director.company_id == company_id).all()
        director_dicts = self._directors_to_dicts(directors)

        forms: Dict[str, Any] = {
            "company_id": company_id,
            "entity_type": entity_type,
            "company_name": company.approved_name or "(Proposed Company)",
            "forms": {},
        }

        # RUN form (all entity types except sole prop)
        if entity_type != "sole_proprietorship":
            proposed_names = company.proposed_names or []
            if proposed_names:
                forms["forms"]["run"] = mca_form_service.generate_run(
                    proposed_names=proposed_names,
                    entity_type=entity_type,
                    state=company.state,
                )

        # SPICe+ form (companies, not LLP or sole prop)
        if entity_type in ("private_limited", "opc", "section_8", "public_limited"):
            forms["forms"]["spice_plus"] = mca_form_service.generate_spice_plus(
                company_name=company.approved_name or "(Proposed Company)",
                entity_type=entity_type,
                state=company.state,
                authorized_capital=company.authorized_capital,
                directors=director_dicts,
            )

            # INC-9
            forms["forms"]["inc_9"] = mca_form_service.generate_inc_9(
                company_name=company.approved_name or "(Proposed Company)",
                directors=director_dicts,
            )

            # DIR-2
            forms["forms"]["dir_2"] = mca_form_service.generate_dir_2(
                company_name=company.approved_name or "(Proposed Company)",
                directors=director_dicts,
            )

        # FiLLiP (LLP only)
        if entity_type == "llp":
            forms["forms"]["fillip"] = mca_form_service.generate_fillip(
                llp_name=company.approved_name or "(Proposed LLP)",
                state=company.state,
                partners=director_dicts,
                capital_contribution=company.authorized_capital or 0,
            )

        return {"success": True, "data": forms}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _directors_to_dicts(directors: List[Director]) -> List[Dict[str, Any]]:
        """Convert Director ORM objects to plain dicts for service calls."""
        return [
            {
                "full_name": d.full_name,
                "din": d.din or "",
                "pan_number": d.pan_number or "",
                "email": d.email or "",
                "phone": d.phone or "",
                "address": d.address or "",
                "date_of_birth": d.date_of_birth or "",
                "has_dsc": d.has_dsc,
                "is_nominee": d.is_nominee,
                "is_designated_partner": d.is_designated_partner,
                "dpin": d.dpin or "",
            }
            for d in directors
        ]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
incorporation_service = IncorporationService()
