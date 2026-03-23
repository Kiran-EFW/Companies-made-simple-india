from pydantic import BaseModel
from typing import Any, Dict, List, Optional


MEETING_TYPES = [
    "BOARD_MEETING",
    "AGM",
    "EGM",
    "COMMITTEE_MEETING",
    "AUDIT_COMMITTEE",
    "NOMINATION_COMMITTEE",
    "CSR_COMMITTEE",
]

MEETING_STATUSES = [
    "scheduled",
    "notice_sent",
    "in_progress",
    "minutes_draft",
    "minutes_signed",
    "completed",
]


class AgendaItem(BaseModel):
    item_number: int
    title: str
    description: Optional[str] = None
    presenter: Optional[str] = None


class Attendee(BaseModel):
    name: str
    din: Optional[str] = None
    designation: Optional[str] = None
    present: bool = False


class Resolution(BaseModel):
    resolution_number: Optional[str] = None
    type: Optional[str] = None  # ordinary, special
    title: str
    description: Optional[str] = None
    votes_for: Optional[int] = None
    votes_against: Optional[int] = None
    result: Optional[str] = None  # passed, rejected


class MeetingCreate(BaseModel):
    meeting_type: str
    title: str
    meeting_date: str  # ISO datetime string
    venue: Optional[str] = None
    is_virtual: bool = False
    virtual_link: Optional[str] = None
    attendees: List[Attendee] = []
    agenda_items: List[AgendaItem] = []


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    meeting_date: Optional[str] = None
    venue: Optional[str] = None
    is_virtual: Optional[bool] = None
    virtual_link: Optional[str] = None
    status: Optional[str] = None


class AttendanceUpdate(BaseModel):
    attendees: List[Attendee]
    quorum_present: bool = True


class AgendaUpdate(BaseModel):
    agenda_items: List[AgendaItem]


class ResolutionsUpdate(BaseModel):
    resolutions: List[Resolution]


class MinutesSignRequest(BaseModel):
    signed_by: str  # Chairman name


class MeetingOut(BaseModel):
    id: int
    company_id: int
    user_id: int
    meeting_type: str
    title: str
    meeting_number: Optional[int] = None
    meeting_date: str
    venue: Optional[str] = None
    is_virtual: bool
    virtual_link: Optional[str] = None
    notice_date: Optional[str] = None
    notice_html: Optional[str] = None
    notice_document_id: Optional[int] = None
    agenda_items: List[Dict[str, Any]] = []
    minutes_html: Optional[str] = None
    minutes_signed: bool
    minutes_signed_date: Optional[str] = None
    minutes_signed_by: Optional[str] = None
    minutes_signature_request_id: Optional[int] = None
    attendees: List[Dict[str, Any]] = []
    quorum_present: bool
    resolutions: List[Dict[str, Any]] = []
    resolution_votes: Optional[Dict[str, Any]] = None
    filing_status: Optional[Dict[str, Any]] = None
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class MeetingListItem(BaseModel):
    id: int
    meeting_type: str
    title: str
    meeting_number: Optional[int] = None
    meeting_date: str
    venue: Optional[str] = None
    is_virtual: bool
    status: str
    minutes_signed: bool
    created_at: str

    class Config:
        from_attributes = True


class ResolutionVotesUpdate(BaseModel):
    votes: Dict[str, Any]  # {resolution_id: {attendee_name: "for"|"against"|"abstain"}}


class MinutesSigningRequest(BaseModel):
    chairman_name: str
    chairman_email: str


class FilingStatusUpdate(BaseModel):
    filing_type: str  # e.g., "mgt14", "aoc4"
    status: str  # "pending"|"filed"|"acknowledged"
    filed_date: Optional[str] = None
    reference_number: Optional[str] = None
