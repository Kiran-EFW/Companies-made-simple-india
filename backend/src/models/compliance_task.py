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

    # GST — Monthly / Quarterly returns
    GSTR_1 = "gstr_1"
    GSTR_3B = "gstr_3b"
    GSTR_9 = "gstr_9"

    # GST — Individual month returns (monthly filers)
    GSTR_1_M01 = "gstr_1_m01"   # April
    GSTR_1_M02 = "gstr_1_m02"   # May
    GSTR_1_M03 = "gstr_1_m03"   # June
    GSTR_1_M04 = "gstr_1_m04"   # July
    GSTR_1_M05 = "gstr_1_m05"   # August
    GSTR_1_M06 = "gstr_1_m06"   # September
    GSTR_1_M07 = "gstr_1_m07"   # October
    GSTR_1_M08 = "gstr_1_m08"   # November
    GSTR_1_M09 = "gstr_1_m09"   # December
    GSTR_1_M10 = "gstr_1_m10"   # January
    GSTR_1_M11 = "gstr_1_m11"   # February
    GSTR_1_M12 = "gstr_1_m12"   # March

    GSTR_3B_M01 = "gstr_3b_m01"
    GSTR_3B_M02 = "gstr_3b_m02"
    GSTR_3B_M03 = "gstr_3b_m03"
    GSTR_3B_M04 = "gstr_3b_m04"
    GSTR_3B_M05 = "gstr_3b_m05"
    GSTR_3B_M06 = "gstr_3b_m06"
    GSTR_3B_M07 = "gstr_3b_m07"
    GSTR_3B_M08 = "gstr_3b_m08"
    GSTR_3B_M09 = "gstr_3b_m09"
    GSTR_3B_M10 = "gstr_3b_m10"
    GSTR_3B_M11 = "gstr_3b_m11"
    GSTR_3B_M12 = "gstr_3b_m12"

    # GST — Quarterly filers (QRMP scheme, turnover ≤ Rs 5 crore)
    GSTR_1_Q1 = "gstr_1_q1"    # Apr-Jun
    GSTR_1_Q2 = "gstr_1_q2"    # Jul-Sep
    GSTR_1_Q3 = "gstr_1_q3"    # Oct-Dec
    GSTR_1_Q4 = "gstr_1_q4"    # Jan-Mar
    GSTR_3B_Q1 = "gstr_3b_q1"
    GSTR_3B_Q2 = "gstr_3b_q2"
    GSTR_3B_Q3 = "gstr_3b_q3"
    GSTR_3B_Q4 = "gstr_3b_q4"

    # GST — Composition scheme
    CMP_08_Q1 = "cmp_08_q1"
    CMP_08_Q2 = "cmp_08_q2"
    CMP_08_Q3 = "cmp_08_q3"
    CMP_08_Q4 = "cmp_08_q4"
    GSTR_4_ANNUAL = "gstr_4_annual"

    # GST — Annual / Reconciliation
    GSTR_9C = "gstr_9c"

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

    # MSME — Semi-annual
    MSME_1_H1 = "msme_1_h1"  # Oct (for Apr-Sep delayed payments)
    MSME_1_H2 = "msme_1_h2"  # Apr (for Oct-Mar delayed payments)

    # FEMA / RBI — FDI tracking
    FC_GPR = "fc_gpr"          # Within 30 days of allotment to non-resident
    FLA_RETURN = "fla_return"  # Annual — July 15

    # Post-incorporation — share certificates
    SHARE_CERTIFICATE_ISSUE = "share_certificate_issue"

    # Annual — DPT-3 (deposit return)
    DPT_3 = "dpt_3"

    # Event-based — ROC filings
    BEN_2 = "ben_2"      # Beneficial ownership (§ 90)
    MGT_14 = "mgt_14"    # Filing of resolutions (§ 117)

    # Board meetings — Half-yearly (OPC / Section 8 / Small Company)
    BOARD_MEETING_H1 = "board_meeting_h1"
    BOARD_MEETING_H2 = "board_meeting_h2"

    # GST Annual
    GSTR_9_ANNUAL = "gstr_9_annual"

    # Labor & Payroll — Monthly
    EPFO_MONTHLY = "epfo_monthly"
    ESIC_MONTHLY = "esic_monthly"

    # State-specific — Professional Tax & LWF
    PT_MONTHLY = "pt_monthly"
    PT_ANNUAL = "pt_annual"
    LWF_H1 = "lwf_h1"  # Half-yearly
    LWF_H2 = "lwf_h2"


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
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

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
