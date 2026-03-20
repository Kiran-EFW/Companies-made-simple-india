from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from src.database import get_db
from src.models.user import User
from src.models.meeting import Meeting
from src.models.company import Company
from src.schemas.meeting import (
    MEETING_TYPES,
    MEETING_STATUSES,
    MeetingCreate,
    MeetingUpdate,
    AttendanceUpdate,
    AgendaUpdate,
    ResolutionsUpdate,
    MinutesSignRequest,
    MeetingOut,
    MeetingListItem,
)
from src.utils.security import get_current_user

router = APIRouter(
    prefix="/companies/{company_id}/meetings",
    tags=["meetings"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _serialize_meeting(m: Meeting) -> dict:
    """Convert a Meeting ORM instance to a dict with ISO datetime strings."""
    return {
        "id": m.id,
        "company_id": m.company_id,
        "user_id": m.user_id,
        "meeting_type": m.meeting_type,
        "title": m.title,
        "meeting_number": m.meeting_number,
        "meeting_date": m.meeting_date.isoformat() if m.meeting_date else "",
        "venue": m.venue,
        "is_virtual": m.is_virtual or False,
        "virtual_link": m.virtual_link,
        "notice_date": m.notice_date.isoformat() if m.notice_date else None,
        "notice_html": m.notice_html,
        "agenda_items": m.agenda_items or [],
        "minutes_html": m.minutes_html,
        "minutes_signed": m.minutes_signed or False,
        "minutes_signed_date": m.minutes_signed_date.isoformat() if m.minutes_signed_date else None,
        "minutes_signed_by": m.minutes_signed_by,
        "attendees": m.attendees or [],
        "quorum_present": m.quorum_present if m.quorum_present is not None else True,
        "resolutions": m.resolutions or [],
        "status": m.status or "scheduled",
        "created_at": m.created_at.isoformat() if m.created_at else "",
        "updated_at": m.updated_at.isoformat() if m.updated_at else "",
    }


def _serialize_meeting_list(m: Meeting) -> dict:
    return {
        "id": m.id,
        "meeting_type": m.meeting_type,
        "title": m.title,
        "meeting_number": m.meeting_number,
        "meeting_date": m.meeting_date.isoformat() if m.meeting_date else "",
        "venue": m.venue,
        "is_virtual": m.is_virtual or False,
        "status": m.status or "scheduled",
        "minutes_signed": m.minutes_signed or False,
        "created_at": m.created_at.isoformat() if m.created_at else "",
    }


def _get_meeting(db: Session, company_id: int, meeting_id: int) -> Meeting:
    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == meeting_id, Meeting.company_id == company_id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


def _next_meeting_number(db: Session, company_id: int, meeting_type: str) -> int:
    max_num = (
        db.query(Meeting.meeting_number)
        .filter(
            Meeting.company_id == company_id,
            Meeting.meeting_type == meeting_type,
        )
        .order_by(Meeting.meeting_number.desc())
        .first()
    )
    return (max_num[0] + 1) if max_num and max_num[0] else 1


def _get_company_info(db: Session, company_id: int) -> dict:
    """Get company name and CIN for document headers."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if company:
        return {
            "name": company.approved_name or f"Company #{company_id}",
            "cin": company.cin or "CIN Pending",
        }
    return {"name": f"Company #{company_id}", "cin": "CIN Pending"}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_meeting(
    company_id: int,
    body: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create/schedule a meeting."""
    if body.meeting_type not in MEETING_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid meeting type. Valid types: {MEETING_TYPES}",
        )

    try:
        meeting_date = datetime.fromisoformat(body.meeting_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting_date format. Use ISO format.")

    meeting_number = _next_meeting_number(db, company_id, body.meeting_type)

    # Serialize attendees and agenda_items from Pydantic models to dicts
    attendees_data = [a.model_dump() for a in body.attendees] if body.attendees else []
    agenda_data = [a.model_dump() for a in body.agenda_items] if body.agenda_items else []

    meeting = Meeting(
        company_id=company_id,
        user_id=current_user.id,
        meeting_type=body.meeting_type,
        title=body.title,
        meeting_number=meeting_number,
        meeting_date=meeting_date,
        venue=body.venue,
        is_virtual=body.is_virtual,
        virtual_link=body.virtual_link,
        attendees=attendees_data,
        agenda_items=agenda_data,
        status="scheduled",
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return _serialize_meeting(meeting)


@router.get("/upcoming")
def list_upcoming_meetings(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List upcoming meetings (meeting_date >= now)."""
    now = datetime.now(timezone.utc)
    meetings = (
        db.query(Meeting)
        .filter(
            Meeting.company_id == company_id,
            Meeting.meeting_date >= now,
        )
        .order_by(Meeting.meeting_date.asc())
        .all()
    )
    return [_serialize_meeting_list(m) for m in meetings]


@router.get("/minutes-pending")
def list_minutes_pending(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List meetings where minutes not yet signed (compliance alert)."""
    now = datetime.now(timezone.utc)
    meetings = (
        db.query(Meeting)
        .filter(
            Meeting.company_id == company_id,
            Meeting.meeting_date < now,
            Meeting.minutes_signed == False,
        )
        .order_by(Meeting.meeting_date.desc())
        .all()
    )

    results = []
    for m in meetings:
        item = _serialize_meeting_list(m)
        # Calculate days since meeting for compliance warning
        if m.meeting_date:
            days_since = (now - m.meeting_date).days
            item["days_since_meeting"] = days_since
            item["overdue"] = days_since > 30  # Section 118: must sign within 30 days
        results.append(item)

    return results


@router.get("/")
def list_meetings(
    company_id: int,
    meeting_type: Optional[str] = Query(None),
    meeting_status: Optional[str] = Query(None, alias="status"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List meetings with optional filters."""
    query = db.query(Meeting).filter(Meeting.company_id == company_id)

    if meeting_type:
        query = query.filter(Meeting.meeting_type == meeting_type)
    if meeting_status:
        query = query.filter(Meeting.status == meeting_status)
    if date_from:
        try:
            query = query.filter(Meeting.meeting_date >= datetime.fromisoformat(date_from))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format.")
    if date_to:
        try:
            query = query.filter(Meeting.meeting_date <= datetime.fromisoformat(date_to))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format.")

    meetings = query.order_by(Meeting.meeting_date.desc()).all()
    return [_serialize_meeting_list(m) for m in meetings]


@router.get("/{meeting_id}")
def get_meeting(
    company_id: int,
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get meeting details."""
    meeting = _get_meeting(db, company_id, meeting_id)
    return _serialize_meeting(meeting)


@router.put("/{meeting_id}")
def update_meeting(
    company_id: int,
    meeting_id: int,
    body: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update meeting details."""
    meeting = _get_meeting(db, company_id, meeting_id)

    if body.title is not None:
        meeting.title = body.title
    if body.meeting_date is not None:
        try:
            meeting.meeting_date = datetime.fromisoformat(body.meeting_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid meeting_date format.")
    if body.venue is not None:
        meeting.venue = body.venue
    if body.is_virtual is not None:
        meeting.is_virtual = body.is_virtual
    if body.virtual_link is not None:
        meeting.virtual_link = body.virtual_link
    if body.status is not None:
        if body.status not in MEETING_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {MEETING_STATUSES}")
        meeting.status = body.status

    db.commit()
    db.refresh(meeting)
    return _serialize_meeting(meeting)


@router.post("/{meeting_id}/notice")
def generate_notice(
    company_id: int,
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate meeting notice HTML (21 days clear notice for AGM/EGM per Section 101)."""
    meeting = _get_meeting(db, company_id, meeting_id)
    company_info = _get_company_info(db, company_id)

    # Determine notice period
    notice_days = 21 if meeting.meeting_type in ("AGM", "EGM") else 7
    notice_date = datetime.now(timezone.utc)

    # Format attendees for notice
    attendees = meeting.attendees or []
    attendee_lines = ""
    for a in attendees:
        name = a.get("name", "")
        din = a.get("din", "")
        designation = a.get("designation", "")
        attendee_lines += f"<li>{name}"
        if din:
            attendee_lines += f" (DIN: {din})"
        if designation:
            attendee_lines += f" - {designation}"
        attendee_lines += "</li>"

    # Format agenda items
    agenda = meeting.agenda_items or []
    agenda_lines = ""
    for item in agenda:
        num = item.get("item_number", "")
        title = item.get("title", "")
        desc = item.get("description", "")
        agenda_lines += f"<li><strong>Item {num}: {title}</strong>"
        if desc:
            agenda_lines += f"<br><span style='color:#555;'>{desc}</span>"
        agenda_lines += "</li>"

    venue_text = meeting.venue or "To be confirmed"
    if meeting.is_virtual and meeting.virtual_link:
        venue_text += f"<br>Virtual Link: {meeting.virtual_link}"

    meeting_date_str = meeting.meeting_date.strftime("%d %B %Y at %I:%M %p") if meeting.meeting_date else ""

    notice_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Notice - {meeting.title}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 20px; }}
        .company-name {{ font-size: 20pt; font-weight: bold; }}
        .cin {{ font-size: 10pt; color: #666; }}
        .notice-title {{ text-align: center; font-size: 16pt; font-weight: bold; margin: 20px 0; text-decoration: underline; }}
        .section {{ margin: 15px 0; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #ccc; padding-top: 15px; font-size: 9pt; color: #666; }}
        ol {{ line-height: 2; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company-name">{company_info['name']}</div>
        <div class="cin">CIN: {company_info['cin']}</div>
    </div>

    <div class="notice-title">NOTICE</div>
    <div class="notice-title" style="font-size:13pt;">{meeting.meeting_type.replace('_', ' ')} - {meeting.title}</div>

    <div class="section">
        <p>Notice is hereby given that the <strong>{meeting.title}</strong>
        (Meeting No. {meeting.meeting_number or ''}) of {company_info['name']}
        will be held on <strong>{meeting_date_str}</strong>
        at <strong>{venue_text}</strong>
        to transact the following business:</p>
    </div>

    <div class="section">
        <h3>AGENDA</h3>
        <ol>{agenda_lines if agenda_lines else '<li>To be confirmed</li>'}</ol>
    </div>

    <div class="section">
        <h3>INVITEES</h3>
        <ul>{attendee_lines if attendee_lines else '<li>To be confirmed</li>'}</ul>
    </div>

    <div class="section" style="margin-top:30px;">
        <p>By Order of the Board</p>
        <br><br>
        <p>___________________________</p>
        <p>Company Secretary / Authorised Signatory</p>
        <p>Date: {notice_date.strftime('%d %B %Y')}</p>
        <p>Place: Registered Office</p>
    </div>

    <div class="footer">
        <p><strong>Note:</strong> {'A member entitled to attend and vote is entitled to appoint a proxy to attend and vote instead of himself/herself. A proxy need not be a member of the Company. The instrument of proxy, in order to be effective, must be deposited at the Registered Office of the Company not less than 48 hours before the commencement of the meeting.' if meeting.meeting_type in ('AGM', 'EGM') else 'This notice has been issued in accordance with the Companies Act, 2013.'}</p>
        <p>Minimum notice period: {notice_days} clear days (Section 101, Companies Act, 2013)</p>
    </div>
</body>
</html>"""

    meeting.notice_html = notice_html
    meeting.notice_date = notice_date
    if meeting.status == "scheduled":
        meeting.status = "notice_sent"
    db.commit()
    db.refresh(meeting)
    return _serialize_meeting(meeting)


@router.put("/{meeting_id}/attendance")
def update_attendance(
    company_id: int,
    meeting_id: int,
    body: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update attendance for a meeting."""
    meeting = _get_meeting(db, company_id, meeting_id)
    meeting.attendees = [a.model_dump() for a in body.attendees]
    meeting.quorum_present = body.quorum_present
    db.commit()
    db.refresh(meeting)
    return _serialize_meeting(meeting)


@router.put("/{meeting_id}/agenda")
def update_agenda(
    company_id: int,
    meeting_id: int,
    body: AgendaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update agenda items for a meeting."""
    meeting = _get_meeting(db, company_id, meeting_id)
    meeting.agenda_items = [a.model_dump() for a in body.agenda_items]
    db.commit()
    db.refresh(meeting)
    return _serialize_meeting(meeting)


@router.post("/{meeting_id}/minutes")
def generate_minutes(
    company_id: int,
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate professional meeting minutes HTML from agenda + resolutions."""
    meeting = _get_meeting(db, company_id, meeting_id)
    company_info = _get_company_info(db, company_id)

    meeting_date_str = meeting.meeting_date.strftime("%d %B %Y at %I:%M %p") if meeting.meeting_date else ""
    venue_text = meeting.venue or "Virtual"
    if meeting.is_virtual and meeting.virtual_link:
        venue_text += f" (Virtual: {meeting.virtual_link})"

    # Attendance table
    attendees = meeting.attendees or []
    attendance_rows = ""
    present_count = 0
    for i, a in enumerate(attendees, 1):
        name = a.get("name", "")
        din = a.get("din", "N/A")
        designation = a.get("designation", "")
        present = a.get("present", False)
        if present:
            present_count += 1
        status_text = "Present" if present else "Absent"
        status_color = "#28a745" if present else "#dc3545"
        attendance_rows += f"""<tr>
            <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{i}</td>
            <td style='border:1px solid #ccc;padding:6px;'>{name}</td>
            <td style='border:1px solid #ccc;padding:6px;'>{din}</td>
            <td style='border:1px solid #ccc;padding:6px;'>{designation}</td>
            <td style='border:1px solid #ccc;padding:6px;text-align:center;color:{status_color};font-weight:bold;'>{status_text}</td>
        </tr>"""

    # Agenda items discussed
    agenda = meeting.agenda_items or []
    agenda_html = ""
    for item in agenda:
        num = item.get("item_number", "")
        title = item.get("title", "")
        desc = item.get("description", "")
        presenter = item.get("presenter", "")
        agenda_html += f"""<div style='margin:15px 0;padding:10px;border-left:3px solid #007bff;'>
            <h4 style='margin:0;'>Item {num}: {title}</h4>
            {f'<p style="color:#555;">Presented by: {presenter}</p>' if presenter else ''}
            {f'<p>{desc}</p>' if desc else ''}
        </div>"""

    # Resolutions
    resolutions = meeting.resolutions or []
    resolutions_html = ""
    for res in resolutions:
        res_num = res.get("resolution_number", "")
        res_type = res.get("type", "ordinary").title()
        res_title = res.get("title", "")
        res_desc = res.get("description", "")
        votes_for = res.get("votes_for", 0)
        votes_against = res.get("votes_against", 0)
        result = res.get("result", "passed").upper()
        result_color = "#28a745" if result == "PASSED" else "#dc3545"

        resolutions_html += f"""<div style='margin:15px 0;padding:15px;border:1px solid #dee2e6;border-radius:5px;'>
            <h4 style='margin:0 0 5px 0;'>Resolution {res_num} ({res_type})</h4>
            <p style='font-weight:bold;'>{res_title}</p>
            {f'<p>{res_desc}</p>' if res_desc else ''}
            <table style='width:auto;margin:10px 0;'>
                <tr><td style='padding:3px 15px 3px 0;'>Votes For:</td><td style='font-weight:bold;'>{votes_for}</td></tr>
                <tr><td style='padding:3px 15px 3px 0;'>Votes Against:</td><td style='font-weight:bold;'>{votes_against}</td></tr>
                <tr><td style='padding:3px 15px 3px 0;'>Result:</td><td style='font-weight:bold;color:{result_color};'>{result}</td></tr>
            </table>
        </div>"""

    quorum_text = "A quorum was present and the meeting was duly constituted." if meeting.quorum_present else "NOTE: Quorum was NOT present."
    quorum_color = "#28a745" if meeting.quorum_present else "#dc3545"

    minutes_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Minutes - {meeting.title}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 25px; }}
        .company-name {{ font-size: 20pt; font-weight: bold; }}
        .cin {{ font-size: 10pt; color: #666; }}
        .minutes-title {{ text-align: center; font-size: 16pt; font-weight: bold; margin: 15px 0; text-decoration: underline; }}
        .section {{ margin: 20px 0; }}
        .section h3 {{ border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        .signature-block {{ margin-top: 60px; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #ccc; padding-top: 15px; font-size: 9pt; color: #666; text-align: center; }}
        @media print {{ body {{ margin: 20px; }} .no-print {{ display: none; }} }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company-name">{company_info['name']}</div>
        <div class="cin">CIN: {company_info['cin']}</div>
    </div>

    <div class="minutes-title">MINUTES OF THE {meeting.meeting_type.replace('_', ' ')}</div>
    <p style="text-align:center;">Meeting No. {meeting.meeting_number or ''}</p>

    <div class="section">
        <table style="width:auto;">
            <tr><td style="padding:5px 20px 5px 0;font-weight:bold;">Date & Time:</td><td>{meeting_date_str}</td></tr>
            <tr><td style="padding:5px 20px 5px 0;font-weight:bold;">Venue:</td><td>{venue_text}</td></tr>
            <tr><td style="padding:5px 20px 5px 0;font-weight:bold;">Meeting Type:</td><td>{meeting.meeting_type.replace('_', ' ')}</td></tr>
        </table>
    </div>

    <div class="section">
        <h3>ATTENDANCE</h3>
        <table>
            <thead>
                <tr style="background:#e9ecef;">
                    <th style='border:1px solid #ccc;padding:8px;'>S.No.</th>
                    <th style='border:1px solid #ccc;padding:8px;'>Name</th>
                    <th style='border:1px solid #ccc;padding:8px;'>DIN</th>
                    <th style='border:1px solid #ccc;padding:8px;'>Designation</th>
                    <th style='border:1px solid #ccc;padding:8px;'>Status</th>
                </tr>
            </thead>
            <tbody>{attendance_rows if attendance_rows else '<tr><td colspan="5" style="text-align:center;padding:15px;">No attendees recorded</td></tr>'}</tbody>
        </table>
        <p style="margin-top:10px;color:{quorum_color};font-weight:bold;">{quorum_text}</p>
        <p>Total Present: {present_count} / {len(attendees)}</p>
    </div>

    <div class="section">
        <h3>AGENDA ITEMS DISCUSSED</h3>
        {agenda_html if agenda_html else '<p style="color:#999;">No agenda items recorded.</p>'}
    </div>

    <div class="section">
        <h3>RESOLUTIONS</h3>
        {resolutions_html if resolutions_html else '<p style="color:#999;">No resolutions recorded.</p>'}
    </div>

    <div class="section">
        <p>There being no other business, the meeting was concluded with a vote of thanks to the Chair.</p>
    </div>

    <div class="signature-block">
        <p>Minutes recorded and confirmed:</p>
        <br><br><br>
        <p>___________________________</p>
        <p><strong>Chairman</strong></p>
        <p>Name: ___________________________</p>
        <p>Date: ___________________________</p>
    </div>

    <div class="footer">
        <p>These minutes have been prepared in accordance with Section 118 of the Companies Act, 2013.</p>
        <p>Minutes must be signed within 30 days from the date of the meeting.</p>
        <p>Generated on {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}</p>
    </div>
</body>
</html>"""

    meeting.minutes_html = minutes_html
    if meeting.status in ("scheduled", "notice_sent", "in_progress"):
        meeting.status = "minutes_draft"
    db.commit()
    db.refresh(meeting)
    return _serialize_meeting(meeting)


@router.put("/{meeting_id}/minutes/sign")
def sign_minutes(
    company_id: int,
    meeting_id: int,
    body: MinutesSignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark minutes as signed (must be within 30 days per Section 118)."""
    meeting = _get_meeting(db, company_id, meeting_id)

    if not meeting.minutes_html:
        raise HTTPException(status_code=400, detail="Minutes must be generated before signing.")

    now = datetime.now(timezone.utc)

    # Check 30-day compliance window
    if meeting.meeting_date:
        days_since = (now - meeting.meeting_date).days
        if days_since > 30:
            # Still allow signing but include a warning
            pass  # We proceed but the response will reflect the date

    meeting.minutes_signed = True
    meeting.minutes_signed_date = now
    meeting.minutes_signed_by = body.signed_by
    meeting.status = "minutes_signed"
    db.commit()
    db.refresh(meeting)

    result = _serialize_meeting(meeting)
    # Add compliance note
    if meeting.meeting_date:
        days_since = (now - meeting.meeting_date).days
        result["compliance_note"] = (
            "Minutes signed within the 30-day statutory period."
            if days_since <= 30
            else f"WARNING: Minutes signed {days_since} days after the meeting. Section 118 requires signing within 30 days."
        )
    return result


@router.put("/{meeting_id}/resolutions")
def update_resolutions(
    company_id: int,
    meeting_id: int,
    body: ResolutionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add/update resolutions passed."""
    meeting = _get_meeting(db, company_id, meeting_id)
    meeting.resolutions = [r.model_dump() for r in body.resolutions]
    db.commit()
    db.refresh(meeting)
    return _serialize_meeting(meeting)


@router.get("/{meeting_id}/export")
def export_meeting(
    company_id: int,
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export meeting package (notice + agenda + minutes) as HTML."""
    meeting = _get_meeting(db, company_id, meeting_id)
    company_info = _get_company_info(db, company_id)

    sections = []

    if meeting.notice_html:
        sections.append(f"""<div class="section-break">
            <h2 style="text-align:center;color:#007bff;">SECTION 1: MEETING NOTICE</h2>
            <hr>
            {meeting.notice_html}
        </div>""")

    if meeting.minutes_html:
        sections.append(f"""<div class="section-break">
            <h2 style="text-align:center;color:#007bff;">SECTION 2: MEETING MINUTES</h2>
            <hr>
            {meeting.minutes_html}
        </div>""")

    if not sections:
        sections.append("<p style='text-align:center;color:#999;'>No documents generated for this meeting yet.</p>")

    package_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Meeting Package - {meeting.title}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; }}
        .cover {{ text-align: center; padding: 100px 0; }}
        .cover h1 {{ font-size: 24pt; }}
        .cover h2 {{ font-size: 16pt; color: #555; }}
        .section-break {{ page-break-before: always; margin-top: 30px; }}
        @media print {{ .section-break {{ page-break-before: always; }} }}
    </style>
</head>
<body>
    <div class="cover">
        <h1>{company_info['name']}</h1>
        <p style="color:#666;">CIN: {company_info['cin']}</p>
        <h2>{meeting.meeting_type.replace('_', ' ')}</h2>
        <h2>{meeting.title}</h2>
        <p>Meeting No. {meeting.meeting_number or ''}</p>
        <p>Date: {meeting.meeting_date.strftime('%d %B %Y') if meeting.meeting_date else ''}</p>
        <p style="margin-top:50px;color:#999;">Meeting Document Package</p>
    </div>

    {''.join(sections)}
</body>
</html>"""

    return Response(
        content=package_html,
        media_type="text/html",
        headers={"Content-Disposition": f'inline; filename="meeting_package_{meeting_id}.html"'},
    )
