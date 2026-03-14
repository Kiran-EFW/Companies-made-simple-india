"""Assignment service — auto-assign tasks, generate filing task queues from workflows."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.user import User, UserRole, StaffDepartment, StaffSeniority
from src.models.company import Company, EntityType
from src.models.filing_task import FilingTask, FilingTaskType, FilingTaskStatus, FilingTaskPriority
from src.services.incorporation_service import WORKFLOW_STEPS

logger = logging.getLogger(__name__)

# Maps filing task types to eligible departments
TASK_DEPARTMENT_MAP: Dict[str, StaffDepartment] = {
    FilingTaskType.DSC_PROCUREMENT.value: StaffDepartment.FILING,
    FilingTaskType.DIN_APPLICATION.value: StaffDepartment.FILING,
    FilingTaskType.DPIN_APPLICATION.value: StaffDepartment.FILING,
    FilingTaskType.NAME_RESERVATION.value: StaffDepartment.FILING,
    FilingTaskType.SPICE_PART_A.value: StaffDepartment.CS,
    FilingTaskType.SPICE_PART_B.value: StaffDepartment.CS,
    FilingTaskType.FILLIP.value: StaffDepartment.CS,
    FilingTaskType.MOA_AOA_DRAFTING.value: StaffDepartment.CS,
    FilingTaskType.LLP_AGREEMENT.value: StaffDepartment.CS,
    FilingTaskType.MCA_FILING.value: StaffDepartment.CS,
    FilingTaskType.ROC_FILING.value: StaffDepartment.CS,
    FilingTaskType.INC12_LICENSE.value: StaffDepartment.CS,
    FilingTaskType.NOMINEE_DECLARATION.value: StaffDepartment.CS,
    FilingTaskType.INC_20A.value: StaffDepartment.CS,
    FilingTaskType.GST_REGISTRATION.value: StaffDepartment.CA,
    FilingTaskType.PAN_TAN_APPLICATION.value: StaffDepartment.CA,
    FilingTaskType.BANK_ACCOUNT.value: StaffDepartment.FILING,
    FilingTaskType.AUDITOR_APPOINTMENT.value: StaffDepartment.CA,
    FilingTaskType.BOARD_MEETING.value: StaffDepartment.CS,
    FilingTaskType.AOC_4.value: StaffDepartment.CA,
    FilingTaskType.MGT_7.value: StaffDepartment.CS,
    FilingTaskType.MGT_7A.value: StaffDepartment.CS,
    FilingTaskType.DIR_3_KYC.value: StaffDepartment.FILING,
    FilingTaskType.FORM_11_LLP.value: StaffDepartment.CS,
    FilingTaskType.FORM_8_LLP.value: StaffDepartment.CA,
    FilingTaskType.DOCUMENT_REVIEW.value: StaffDepartment.FILING,
    FilingTaskType.OTHER.value: StaffDepartment.FILING,
}

# Maps workflow step keys to FilingTaskType
WORKFLOW_KEY_TO_TASK_TYPE: Dict[str, FilingTaskType] = {
    "dsc": FilingTaskType.DSC_PROCUREMENT,
    "din": FilingTaskType.DIN_APPLICATION,
    "dpin": FilingTaskType.DPIN_APPLICATION,
    "run": FilingTaskType.NAME_RESERVATION,
    "run_llp": FilingTaskType.NAME_RESERVATION,
    "spice_part_a": FilingTaskType.SPICE_PART_A,
    "spice_part_b": FilingTaskType.SPICE_PART_B,
    "spice_plus": FilingTaskType.SPICE_PART_B,
    "fillip": FilingTaskType.FILLIP,
    "moa_aoa": FilingTaskType.MOA_AOA_DRAFTING,
    "llp_agreement": FilingTaskType.LLP_AGREEMENT,
    "filing": FilingTaskType.MCA_FILING,
    "roc_filing": FilingTaskType.ROC_FILING,
    "inc12": FilingTaskType.INC12_LICENSE,
    "license_wait": FilingTaskType.INC12_LICENSE,
    "nominee": FilingTaskType.NOMINEE_DECLARATION,
    "prop_registration": FilingTaskType.OTHER,
    "shop_act": FilingTaskType.OTHER,
    "gst": FilingTaskType.GST_REGISTRATION,
}

# Default SLA hours per task type
DEFAULT_SLA_HOURS: Dict[str, int] = {
    FilingTaskType.DSC_PROCUREMENT.value: 48,
    FilingTaskType.DIN_APPLICATION.value: 24,
    FilingTaskType.NAME_RESERVATION.value: 24,
    FilingTaskType.SPICE_PART_A.value: 48,
    FilingTaskType.SPICE_PART_B.value: 72,
    FilingTaskType.MOA_AOA_DRAFTING.value: 48,
    FilingTaskType.MCA_FILING.value: 24,
    FilingTaskType.DOCUMENT_REVIEW.value: 12,
}


class AssignmentService:
    """Handles task assignment logic and workflow-based task generation."""

    def auto_assign(self, db: Session, task: FilingTask) -> Optional[User]:
        """Pick the best available team member for a filing task.

        Selection criteria:
        1. Must belong to the correct department for the task type
        2. Must be active
        3. Prefer lowest active task count (load balancing)
        """
        dept = TASK_DEPARTMENT_MAP.get(task.task_type.value if hasattr(task.task_type, 'value') else task.task_type)
        if not dept:
            dept = StaffDepartment.FILING

        # Find eligible staff in the right department
        eligible = (
            db.query(User)
            .filter(
                User.is_active == True,
                User.department == dept,
                User.role != UserRole.USER,
            )
            .all()
        )

        if not eligible:
            # Fall back to any admin staff
            eligible = (
                db.query(User)
                .filter(User.is_active == True, User.role != UserRole.USER)
                .all()
            )

        if not eligible:
            return None

        # Pick the one with fewest active tasks
        best = None
        lowest_count = float("inf")
        for user in eligible:
            active_count = (
                db.query(FilingTask)
                .filter(
                    FilingTask.assigned_to == user.id,
                    FilingTask.status.in_([
                        FilingTaskStatus.ASSIGNED,
                        FilingTaskStatus.IN_PROGRESS,
                    ]),
                )
                .count()
            )
            if active_count < lowest_count:
                lowest_count = active_count
                best = user

        return best

    def create_filing_tasks_for_company(
        self,
        db: Session,
        company_id: int,
        auto_assign: bool = True,
        assigned_by: Optional[int] = None,
    ) -> List[FilingTask]:
        """Generate all workflow-step filing tasks for a company based on entity type.

        Returns the list of created FilingTask objects.
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return []

        entity = company.entity_type
        if isinstance(entity, EntityType):
            entity = entity.value

        steps = WORKFLOW_STEPS.get(entity, [])
        if not steps:
            logger.warning("No workflow steps found for entity type: %s", entity)
            return []

        created_tasks = []
        prev_task = None

        for step in steps:
            task_type_enum = WORKFLOW_KEY_TO_TASK_TYPE.get(step["key"], FilingTaskType.OTHER)
            sla_hours = DEFAULT_SLA_HOURS.get(task_type_enum.value, 72)

            task = FilingTask(
                company_id=company_id,
                task_type=task_type_enum,
                title=step["name"],
                description=step.get("description", ""),
                priority=FilingTaskPriority.NORMAL,
                status=FilingTaskStatus.UNASSIGNED,
                due_date=datetime.now(timezone.utc) + timedelta(hours=sla_hours),
                parent_task_id=prev_task.id if prev_task else None,
                assigned_by=assigned_by,
            )
            db.add(task)
            db.flush()  # Get the ID for parent_task_id chain

            if auto_assign:
                assignee = self.auto_assign(db, task)
                if assignee:
                    task.assigned_to = assignee.id
                    task.assigned_at = datetime.now(timezone.utc)
                    task.status = FilingTaskStatus.ASSIGNED

            created_tasks.append(task)
            prev_task = task

        db.commit()
        return created_tasks

    def get_required_department(self, task_type: str) -> Optional[StaffDepartment]:
        """Return the department responsible for a given task type."""
        return TASK_DEPARTMENT_MAP.get(task_type)


# Module-level singleton
assignment_service = AssignmentService()
