import asyncio
import threading
from sqlalchemy.orm import Session
from src.models.company import Company, CompanyStatus


class ProcessOrchestrator:
    """
    Background orchestrator that listens to state changes and triggers the appropriate AI agents.
    Now supports entity-specific incorporation workflows via IncorporationService.
    """

    @staticmethod
    def _run_agents_pipeline(company_id: int):
        from src.database import SessionLocal
        db = SessionLocal()
        try:
            comp = db.query(Company).filter(Company.id == company_id).first()
            if not comp:
                return

            if comp.status == CompanyStatus.DOCUMENTS_UPLOADED:
                from src.agents.name_validator import NameValidatorAgent
                agent = NameValidatorAgent(db_session=db, company_id=comp.id)
                agent.run()
                db.refresh(comp)
                ProcessOrchestrator._check_for_drafting_readiness(db, comp)

            elif comp.status == CompanyStatus.DOCUMENTS_VERIFIED or comp.status == CompanyStatus.NAME_RESERVED:
                ProcessOrchestrator._check_for_drafting_readiness(db, comp)

            elif comp.status == CompanyStatus.DSC_IN_PROGRESS:
                # Trigger DSC procurement via the incorporation workflow
                ProcessOrchestrator._run_incorporation_workflow(db, comp)

            elif comp.status == CompanyStatus.MCA_PROCESSING:
                from src.agents.registrar import RegistrarAgent
                agent = RegistrarAgent(db_session=db, company_id=comp.id)
                agent.run()
                db.refresh(comp)

        except Exception as e:
            print(f"Orchestrator pipeline failed for company {company_id}: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def _run_incorporation_workflow(db: Session, comp: Company):
        """
        Route to entity-specific workflow using the IncorporationService.
        Runs async code in a new event loop (we are in a background thread).
        """
        from src.services.incorporation_service import incorporation_service

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                incorporation_service.start_workflow(db, comp.id)
            )
            if not result.get("success"):
                print(
                    f"Incorporation workflow failed for company {comp.id}: "
                    f"{result.get('error', 'unknown error')}"
                )
        except Exception as e:
            print(f"Incorporation workflow exception for company {comp.id}: {str(e)}")
        finally:
            loop.close()

    @staticmethod
    def trigger_pipeline(company_id: int):
        """
        Kicks off the orchestrator in a background thread so the HTTP request can return immediately.
        """
        thread = threading.Thread(target=ProcessOrchestrator._run_agents_pipeline, args=(company_id,))
        thread.start()

    @staticmethod
    def trigger_incorporation_workflow(company_id: int):
        """
        Trigger the entity-specific incorporation workflow in a background thread.
        """
        def _run(cid: int):
            from src.database import SessionLocal
            db = SessionLocal()
            try:
                comp = db.query(Company).filter(Company.id == cid).first()
                if comp:
                    ProcessOrchestrator._run_incorporation_workflow(db, comp)
            except Exception as e:
                print(f"Incorporation workflow trigger failed for company {cid}: {str(e)}")
            finally:
                db.close()

        thread = threading.Thread(target=_run, args=(company_id,))
        thread.start()

    @staticmethod
    def trigger_document_parsing(document_id: int):
        """
        Trigger the AI Document Parser for a specific document.
        """
        from src.agents.document_parser import DocumentParserAgent
        agent = DocumentParserAgent(document_id=document_id)
        thread = threading.Thread(target=agent.run)
        thread.start()

    @staticmethod
    def _check_for_drafting_readiness(db: Session, comp: Company):
        """
        Logic to check if we can move the company to FILING_DRAFTED.
        Requires:
        1. Name is reserved (approved_name exists)
        2. All required documents are team_verified
        """
        # 1. Check Name
        if not comp.approved_name:
            return

        # 2. Check Documents (Simplify: Check if company status is DOCUMENTS_VERIFIED
        # or if we have at least one team_verified document in this MVP)
        from src.models.document import Document
        verified_docs = db.query(Document).filter(
            Document.company_id == comp.id,
            Document.verification_status == "team_verified"
        ).count()

        if verified_docs > 0:
            # We are ready — route through entity-specific workflow
            entity_type = comp.entity_type.value if hasattr(comp.entity_type, "value") else str(comp.entity_type)

            # For entity types that have full incorporation workflows, use them
            if entity_type in ("private_limited", "opc", "llp", "section_8", "sole_proprietorship"):
                print(f"Company {comp.id} is ready. Triggering {entity_type} incorporation workflow.")
                ProcessOrchestrator._run_incorporation_workflow(db, comp)
            else:
                # Fallback to legacy drafting agent for other entity types
                comp.status = CompanyStatus.FILING_DRAFTED
                db.commit()
                print(f"Company {comp.id} is now READY_FOR_DRAFTING. Triggering Drafting Agent.")

                from src.agents.document_drafter import DocumentDrafterAgent
                drafter = DocumentDrafterAgent(company_id=comp.id)
                thread = threading.Thread(target=drafter.run)
                thread.start()
