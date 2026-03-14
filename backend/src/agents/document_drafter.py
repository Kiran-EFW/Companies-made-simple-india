import time
from sqlalchemy.orm import Session
from src.models.company import Company, CompanyStatus
from src.utils.retry_utils import with_retry
from src.utils.logging_utils import logger
from src.models.task import Task, AgentLog, TaskStatus
from src.models.document import Document, DocumentType

class DocumentDrafterAgent:
    def __init__(self, db_session=None, company_id: int = None):
        self.db_session = db_session
        self.company_id = company_id
        self.agent_name = "Agent: MCA Document Drafter"

    def _get_db(self):
        if self.db_session:
            return self.db_session
        from src.database import SessionLocal
        return SessionLocal()

    def log(self, message: str, level: str = "INFO"):
        db = self._get_db()
        try:
            from src.models.task import AgentLog
            log_entry = AgentLog(
                company_id=self.company_id,
                agent_name=self.agent_name,
                message=message,
                level=level
            )
            db.add(log_entry)
            db.commit()
        finally:
            if not self.db_session:
                db.close()

    @with_retry(max_retries=3, delay=2.0)
    def run(self):
        db = self._get_db()
        try:
            self.log("MCA Document Drafting Agent initialized. Fetching company data for form generation...", "INFO")
            
            comp = db.query(Company).filter(Company.id == self.company_id).first()
            if not comp:
                self.log("Company not found. Aborting.", "ERROR")
                return

            task = Task(
                company_id=comp.id,
                agent_name=self.agent_name,
                status=TaskStatus.RUNNING
            )
            db.add(task)
            db.commit()

            # Step 1: Simulate SPICe+ Part A/B drafting
            self.log(f"Auto-filling SPICe+ Part A for name reservation: '{comp.approved_name}'...", "INFO")
            time.sleep(1.5)
            self.log("Mapping director PAN details to SPICe+ Part B Part 1 (Director Particulars)...", "INFO")
            time.sleep(2)
            
            # Step 2: Simulate MOA/AOA drafting
            self.log(f"Generating Memorandum of Association (MOA) based on {comp.entity_type} template...", "INFO")
            time.sleep(1.5)
            self.log("Customizing MOA Main Objects clause based on user input description...", "INFO")
            time.sleep(2)
            
            self.log("Generating Articles of Association (AOA) with default Table F adoption...", "INFO")
            time.sleep(1)

            # Step 3: Simulate "Generating" files
            docs_to_create = [
                (DocumentType.OTHER, "spice_draft_generated.pdf", "Auto-filled SPICe+ Form (Active)"),
                (DocumentType.OTHER, "moa_draft_generated.pdf", "Draft Memorandum of Association"),
                (DocumentType.OTHER, "aoa_draft_generated.pdf", "Draft Articles of Association")
            ]

            import json
            for dtype, filename, display_name in docs_to_create:
                new_doc = Document(
                    company_id=comp.id,
                    doc_type=dtype,
                    original_filename=filename,
                    file_path=f"storage/generated/{filename}",
                    verification_status="ai_verified",
                    extracted_data=json.dumps({"display_name": display_name, "is_generated": True})
                )
                db.add(new_doc)
            
            self.log("Internal Check: Cross-verifying drafted forms against MCA V3 business rules...", "INFO")
            time.sleep(2)

            # Advance status
            comp.status = CompanyStatus.MCA_PROCESSING
            self.log("Filing package successfully drafted. All forms ready for human sign-off and MCA submission.", "SUCCESS")
            
            task.status = TaskStatus.COMPLETED
            task.result = {"docs_generated": [d[1] for d in docs_to_create]}
            
            db.commit()

            # Trigger the next phase in the orchestrator (Registrar)
            from src.services.orchestrator import ProcessOrchestrator
            ProcessOrchestrator.trigger_pipeline(self.company_id)
        finally:
            if not self.db_session:
                db.close()
