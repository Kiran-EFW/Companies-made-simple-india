"""FilingTask model — core work item for internal ops team."""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class FilingTaskType(str, enum.Enum):
    # Incorporation workflow
    DSC_PROCUREMENT = "dsc_procurement"
    DIN_APPLICATION = "din_application"
    DPIN_APPLICATION = "dpin_application"
    NAME_RESERVATION = "name_reservation"
    SPICE_PART_A = "spice_part_a"
    SPICE_PART_B = "spice_part_b"
    FILLIP = "fillip"
    MOA_AOA_DRAFTING = "moa_aoa_drafting"
    LLP_AGREEMENT = "llp_agreement"
    MCA_FILING = "mca_filing"
    ROC_FILING = "roc_filing"
    INC12_LICENSE = "inc12_license"
    NOMINEE_DECLARATION = "nominee_declaration"
    # Post-incorporation
    INC_20A = "inc_20a"
    GST_REGISTRATION = "gst_registration"
    PAN_TAN_APPLICATION = "pan_tan_application"
    BANK_ACCOUNT = "bank_account"
    AUDITOR_APPOINTMENT = "auditor_appointment"
    BOARD_MEETING = "board_meeting"
    # Annual compliance
    AOC_4 = "aoc_4"
    MGT_7 = "mgt_7"
    MGT_7A = "mgt_7a"
    DIR_3_KYC = "dir_3_kyc"
    FORM_11_LLP = "form_11_llp"
    FORM_8_LLP = "form_8_llp"
    # General
    DOCUMENT_REVIEW = "document_review"
    OTHER = "other"


class FilingTaskStatus(str, enum.Enum):
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CLIENT = "waiting_on_client"
    WAITING_ON_GOVERNMENT = "waiting_on_government"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class FilingTaskPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class FilingTask(Base):
    __tablename__ = "filing_tasks"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    task_type = Column(Enum(FilingTaskType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(FilingTaskPriority), default=FilingTaskPriority.NORMAL)

    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)

    # Status tracking
    status = Column(Enum(FilingTaskStatus), default=FilingTaskStatus.UNASSIGNED, index=True)
    due_date = Column(DateTime, nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    task_metadata = Column(JSON, nullable=True)  # SRN numbers, filing refs, form data

    # Escalation
    escalation_level = Column(Integer, default=0)
    escalated_at = Column(DateTime, nullable=True)
    escalated_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Sequential dependency
    parent_task_id = Column(Integer, ForeignKey("filing_tasks.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    company = relationship("Company", foreign_keys=[company_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    assigner = relationship("User", foreign_keys=[assigned_by])
    escalated_user = relationship("User", foreign_keys=[escalated_to])
    parent_task = relationship("FilingTask", remote_side="FilingTask.id", foreign_keys=[parent_task_id])
