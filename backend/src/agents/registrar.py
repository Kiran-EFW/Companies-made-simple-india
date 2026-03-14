import time
import json
from sqlalchemy.orm import Session
from src.models.company import Company, CompanyStatus
from src.utils.retry_utils import with_retry
from src.utils.logging_utils import logger
from src.models.task import Task, AgentLog, TaskStatus
from src.models.document import Document, DocumentType

class RegistrarAgent:
    """
    Simulates the Ministry of Corporate Affairs (MCA) / ROC processing 
    and issuing the Certificate of Incorporation (COI).
    """
class RegistrarAgent:
    def __init__(self, db_session=None, company_id: int = None):
        self.db_session = db_session
        self.company_id = company_id
        self.agent_name = "Agent: Registrar of Companies (ROC)"

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

    @with_retry(max_retries=3, delay=5.0)
    def run(self):
        db = self._get_db()
        try:
            self.log("ROC Filing received from Digital Drafter. Beginning final scrutiny...", "INFO")
            
            comp = db.query(Company).filter(Company.id == self.company_id).first()
            if not comp: return

            task = Task(
                company_id=comp.id,
                agent_name=self.agent_name,
                status=TaskStatus.RUNNING
            )
            db.add(task)
            db.commit()

            # Step 1: Simulate checking SPICe+ and attachments
            self.log("Verifying digital signatures (DSC) and stamp duty payment...", "INFO")
            time.sleep(2)
            
            # Step 2: Final approval
            self.log("Filing package approved. Assigning Corporate Identification Number (CIN)...", "SUCCESS")
            time.sleep(1.5)
            
            cin = f"U{10000 + comp.id}KA2024PTC{200000 + comp.id}"
            # In a real app we'd have a cin field, but we'll put it in company meta or logs for now
            self.log(f"CIN Generated: {cin}", "SUCCESS")

            # Step 3: Issue COI
            new_doc = Document(
                company_id=comp.id,
                doc_type=DocumentType.OTHER,
                original_filename="Certificate_of_Incorporation.pdf",
                file_path="storage/generated/coi_official.pdf",
                verification_status="ai_verified",
                extracted_data=json.dumps({
                    "display_name": "Official Certificate of Incorporation (COI)",
                    "is_generated": True,
                    "cin": cin
                })
            )
            db.add(new_doc)
            
            # Advance status to INCORPORATED
            comp.status = CompanyStatus.INCORPORATED
            
            self.log("Company is now officially INCORPORATED. Welcome to the ecosystem!", "SUCCESS")
            
            task.status = TaskStatus.COMPLETED
            task.result = {"cin": cin, "status": "incorporated"}
            
            db.commit()
        finally:
            if not self.db_session:
                db.close()
