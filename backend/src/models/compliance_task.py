"""Compliance task model for tracking post-incorporation and recurring compliance obligations."""

import enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class ComplianceTaskType(str, enum.Enum):
    # Post-incorporation (one-time)
    INC_20A = "inc_20a"
    BANK_ACCOUNT = "bank_account"
    FIRST_BOARD_MEETING = "first_board_meeting"
    AUDITOR_APPOINTMENT = "auditor_appointment"
    GST_REGISTRATION = "gst_registration"
    DPIIT_REGISTRATION = "dpiit_registration"
    PF_REGISTRATION = "pf_registration"
    ESI_REGISTRATION = "esi_registration"
    LLP_AGREEMENT = "llp_agreement"
    SHARE_ALLOTMENT = "share_allotment"

    # Annual — ROC filings
    AOC_4 = "aoc_4"
    MGT_7 = "mgt_7"
    MGT_7A = "mgt_7a"
    DIR_3_KYC = "dir_3_kyc"
    ADT_1_RENEWAL = "adt_1_renewal"
    FORM_11 = "form_11"
    FORM_8 = "form_8"

    # Board / AGM
    BOARD_MEETING_Q1 = "board_meeting_q1"
    BOARD_MEETING_Q2 = "board_meeting_q2"
    BOARD_MEETING_Q3 = "board_meeting_q3"
    BOARD_MEETING_Q4 = "board_meeting_q4"
    AGM = "agm"

    # GST
    GSTR_1 = "gstr_1"
    GSTR_3B = "gstr_3b"
    GSTR_9 = "gstr_9"

    # TDS
    TDS_RETURN_Q1 = "tds_return_q1"
    TDS_RETURN_Q2 = "tds_return_q2"
    TDS_RETURN_Q3 = "tds_return_q3"
    TDS_RETURN_Q4 = "tds_return_q4"
    FORM_16 = "form_16"

    # Income Tax
    ITR_FILING = "itr_filing"
    ADVANCE_TAX_Q1 = "advance_tax_q1"
    ADVANCE_TAX_Q2 = "advance_tax_q2"
    ADVANCE_TAX_Q3 = "advance_tax_q3"
    ADVANCE_TAX_Q4 = "advance_tax_q4"


class ComplianceTaskStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    DUE_SOON = "due_soon"       # Within 30 days
    OVERDUE = "overdue"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NOT_APPLICABLE = "not_applicable"


class ComplianceTask(Base):
    __tablename__ = "compliance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    task_type = Column(Enum(ComplianceTaskType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    status = Column(Enum(ComplianceTaskStatus), default=ComplianceTaskStatus.UPCOMING)
    form_data = Column(JSON, nullable=True)
    filing_reference = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    company = relationship("Company", backref="compliance_tasks")
