from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from src.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    meeting_type = Column(String, nullable=False)
    # Types: BOARD_MEETING, AGM, EGM, COMMITTEE_MEETING, AUDIT_COMMITTEE,
    # NOMINATION_COMMITTEE, CSR_COMMITTEE

    title = Column(String, nullable=False)
    meeting_number = Column(Integer, nullable=True)  # Sequential per type per company
    meeting_date = Column(DateTime, nullable=False)
    venue = Column(String, nullable=True)
    is_virtual = Column(Boolean, default=False)
    virtual_link = Column(String, nullable=True)

    # Notice
    notice_date = Column(DateTime, nullable=True)
    notice_html = Column(Text, nullable=True)

    # Agenda & Minutes
    agenda_items = Column(JSON, default=list)  # [{item_number, title, description, presenter}]
    minutes_html = Column(Text, nullable=True)
    minutes_signed = Column(Boolean, default=False)
    minutes_signed_date = Column(DateTime, nullable=True)
    minutes_signed_by = Column(String, nullable=True)  # Chairman name

    # Attendance
    attendees = Column(JSON, default=list)  # [{name, din, designation, present: bool}]
    quorum_present = Column(Boolean, default=True)

    # Resolutions passed
    resolutions = Column(JSON, default=list)
    # [{resolution_number, type, title, description, votes_for, votes_against, result}]

    # Detailed per-attendee votes (persisted from frontend ResolutionWorkflow)
    resolution_votes = Column(JSON, default=dict)
    # {resolution_id: {attendee_name: "for"|"against"|"abstain"}}

    # Document & signature integration
    notice_document_id = Column(Integer, ForeignKey("legal_documents.id"), nullable=True)
    minutes_signature_request_id = Column(Integer, ForeignKey("signature_requests.id"), nullable=True)

    # Compliance filing tracking (persisted from frontend)
    filing_status = Column(JSON, default=dict)
    # {filing_type: {status: "pending"|"filed"|"acknowledged", filed_date, reference_number}}

    status = Column(String, default="scheduled")
    # scheduled, notice_sent, in_progress, minutes_draft, minutes_signed, completed

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
