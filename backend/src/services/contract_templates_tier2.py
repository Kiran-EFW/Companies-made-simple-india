"""Contract template definitions — Tier 2 (Templates 9–14).

Templates included:
  9. Board Resolution (Multi-Type)
 10. Privacy Policy (DPDP Act 2023)
 11. Terms of Service
 12. Offer Letter
 13. IP Assignment Agreement
 14. Share Transfer Agreement

Each template is exposed as a standalone function returning a dict, plus a
matching render function that produces HTML.  These can be imported and
registered into the main ContractTemplateService.
"""

from typing import Any, Optional, Dict, List


# ---------------------------------------------------------------------------
# Clause helper — builds a single clause definition dict
# ---------------------------------------------------------------------------

def _clause(
    clause_id: str,
    label: str,
    input_type: str,
    explanation: str,
    *,
    options: Optional[List[str]] = None,
    default: Any = None,
    learn_more: Optional[str] = None,
    pros: Optional[List[str]] = None,
    cons: Optional[List[str]] = None,
    india_note: Optional[str] = None,
    warning: Optional[str] = None,
    warning_condition: Optional[Dict[str, Any]] = None,
    common_choice_label: Optional[str] = None,
    depends_on: Optional[str] = None,
    preview_template: Optional[str] = None,
    required: bool = True,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> dict:
    c: Dict[str, Any] = {
        "id": clause_id,
        "label": label,
        "input_type": input_type,
        "explanation": explanation,
        "required": required,
    }
    if options is not None:
        c["options"] = options
    if default is not None:
        c["default"] = default
    if learn_more:
        c["learn_more"] = learn_more
    if pros:
        c["pros"] = pros
    if cons:
        c["cons"] = cons
    if india_note:
        c["india_note"] = india_note
    if warning:
        c["warning"] = warning
    if warning_condition:
        c["warning_condition"] = warning_condition
    if common_choice_label:
        c["common_choice_label"] = common_choice_label
    if depends_on:
        c["depends_on"] = depends_on
    if preview_template:
        c["preview_template"] = preview_template
    if min_value is not None:
        c["min_value"] = min_value
    if max_value is not None:
        c["max_value"] = max_value
    return c


# ---------------------------------------------------------------------------
# Base HTML wrapper
# ---------------------------------------------------------------------------

def _base_html_wrap(title: str, body: str, date: str = "") -> str:
    from src.services.document_html_utils import base_html_wrap
    return base_html_wrap(title, body, date)


# ======================================================================
# TEMPLATE 9: BOARD RESOLUTION (MULTI-TYPE)
# ======================================================================

def board_resolution_template() -> dict:
    """Template 9 — Board Resolution for common corporate actions."""
    return {
        "name": "Board Resolution (Multi-Type)",
        "description": (
            "Generate board resolutions for common corporate actions \u2014 director "
            "appointments, bank account opening, share allotment, auditor appointment, "
            "registered office change, and more."
        ),
        "category": "Corporate Governance",
        "steps": [
            # Step 1: Resolution Type & Details
            {
                "step_number": 1,
                "title": "Resolution Type & Details",
                "description": "Select the type of board resolution and provide meeting details.",
                "clauses": [
                    _clause(
                        "br_resolution_type",
                        "Resolution Type",
                        "dropdown",
                        "Type of board resolution to generate",
                        options=[
                            "Director Appointment",
                            "Director Resignation Acceptance",
                            "Bank Account Opening",
                            "Share Allotment",
                            "Auditor Appointment",
                            "Registered Office Change",
                            "ESOP Pool Creation",
                            "Authorized Capital Increase",
                            "Loan/Borrowing Approval",
                            "Related Party Transaction",
                        ],
                        learn_more=(
                            "Board resolutions record decisions made at board meetings. Under "
                            "Companies Act 2013, certain decisions must be made by the board and "
                            "recorded in minutes. Some require ordinary resolution (simple "
                            "majority), while others need special resolution (75% majority)."
                        ),
                        india_note=(
                            "Under Section 179 of Companies Act 2013, the Board has power to "
                            "exercise all powers on behalf of the company. Section 118 requires "
                            "minutes of board meetings to be maintained. Minutes must be prepared "
                            "within 30 days of the meeting."
                        ),
                    ),
                    _clause(
                        "br_company_name",
                        "Company Name",
                        "text",
                        "Registered name of the company",
                        learn_more=(
                            "Use the exact registered name as it appears on your Certificate of "
                            "Incorporation from the MCA. Any variation could make the resolution "
                            "legally invalid. The name must match MCA records including the suffix "
                            "(Private Limited, LLP, etc.)."
                        ),
                    ),
                    _clause(
                        "br_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number (CIN)",
                        required=False,
                        learn_more=(
                            "The CIN is a 21-character alphanumeric code assigned by the Ministry "
                            "of Corporate Affairs (MCA) to every registered company. You can find it "
                            "on your Certificate of Incorporation or by searching the MCA portal. "
                            "Including the CIN adds authenticity and helps identify the company uniquely."
                        ),
                    ),
                    _clause(
                        "br_meeting_date",
                        "Meeting Date",
                        "date",
                        "Date of the board meeting",
                        learn_more=(
                            "This is the actual date the board meeting was held. Under Section 173 "
                            "of the Companies Act 2013, at least 7 days notice must be given before "
                            "a board meeting. The first board meeting must be held within 30 days of "
                            "incorporation, and subsequent meetings at least once every 120 days."
                        ),
                    ),
                    _clause(
                        "br_meeting_place",
                        "Meeting Place",
                        "text",
                        "Place where the meeting was held",
                        learn_more=(
                            "Enter the city and address where the board meeting was physically held. "
                            "Board meetings can be held at any place in India, but it is common "
                            "practice to hold them at the registered office. Video conferencing is "
                            "allowed under Section 173(2), but certain matters like approval of "
                            "financial statements cannot be conducted via video conference."
                        ),
                    ),
                    _clause(
                        "br_directors_present",
                        "Directors Present",
                        "textarea",
                        "Names and DINs of directors present (one per line)",
                        learn_more=(
                            "List each director who attended the meeting along with their DIN "
                            "(Director Identification Number). Quorum is required for a valid board "
                            "meeting \u2014 typically one-third of total directors or two directors, "
                            "whichever is higher (Section 174). If quorum is not met, the resolution "
                            "is invalid and cannot be enforced."
                        ),
                    ),
                    _clause(
                        "br_meeting_serial",
                        "Meeting Serial Number",
                        "number",
                        "Serial number of this board meeting (e.g., 1, 2, 3)",
                        required=False,
                        min_value=1,
                        learn_more=(
                            "Board meetings are sequentially numbered from incorporation. "
                            "The first board meeting must be held within 30 days of incorporation "
                            "(Section 173(1)). This serial number helps maintain proper minutes "
                            "records as required under Secretarial Standard SS-1 issued by ICSI."
                        ),
                    ),
                    _clause(
                        "br_chairperson_name",
                        "Chairperson",
                        "text",
                        "Name of the director presiding as Chairperson of this meeting",
                        required=False,
                        learn_more=(
                            "Under Section 175 of the Companies Act, 2013, if the Articles "
                            "provide for a Chairman, they shall preside. Otherwise, directors "
                            "present may elect one of themselves as Chairman. The Chairman signs "
                            "the minutes and has a casting vote in case of a tie."
                        ),
                    ),
                    _clause(
                        "br_company_secretary",
                        "Company Secretary",
                        "text",
                        "Name of the Company Secretary (if appointed)",
                        required=False,
                        learn_more=(
                            "Under Section 203, every listed company and every company with "
                            "paid-up share capital of Rs 10 crore or more must appoint a "
                            "whole-time Company Secretary. The CS attests the minutes and "
                            "ensures compliance with Secretarial Standards."
                        ),
                    ),
                    _clause(
                        "br_registered_office",
                        "Registered Office Address",
                        "textarea",
                        "Registered office address of the company (for document header)",
                        required=False,
                        learn_more=(
                            "Section 12(3)(c) requires every company to print its registered "
                            "office address on all business letters and letter papers. Including "
                            "this in board resolution minutes is standard practice per SS-1."
                        ),
                    ),
                    _clause(
                        "br_directors_leave",
                        "Directors Absent (Leave of Absence)",
                        "textarea",
                        "Names of directors absent from the meeting (one per line)",
                        required=False,
                        learn_more=(
                            "Under Section 167(1)(b), if a director is absent from all board "
                            "meetings for twelve months, the office is automatically vacated. "
                            "Granting leave of absence in the minutes protects directors from "
                            "this provision. This is standard practice per SS-1."
                        ),
                    ),
                ],
            },
            # Step 2: Resolution-Specific Details
            {
                "step_number": 2,
                "title": "Resolution-Specific Details",
                "description": "Provide details specific to the selected resolution type.",
                "clauses": [
                    _clause(
                        "br_person_name",
                        "Person Name",
                        "text",
                        "Name of the person involved (director being appointed, auditor, etc.)",
                        required=False,
                        learn_more=(
                            "Enter the full legal name of the person this resolution concerns. For "
                            "director appointments, this must match the name on their DIN application. "
                            "For auditor appointments, use the full name of the individual or firm. "
                            "Accuracy here is critical as the name will appear in MCA filings."
                        ),
                    ),
                    _clause(
                        "br_person_din",
                        "DIN",
                        "text",
                        "DIN (Director Identification Number) if applicable",
                        required=False,
                        learn_more=(
                            "A DIN is an 8-digit unique identification number assigned to every "
                            "director by the MCA. A person must obtain a DIN before being appointed "
                            "as a director. You can apply for a DIN using Form DIR-3 on the MCA "
                            "portal, and it typically takes 3-5 business days to be approved."
                        ),
                        india_note=(
                            "Every director must have a DIN obtained from MCA before "
                            "appointment. Apply using DIR-3 form."
                        ),
                    ),
                    _clause(
                        "br_amount",
                        "Amount",
                        "number",
                        "Amount involved (authorized capital, loan amount, etc.) in INR",
                        required=False,
                        learn_more=(
                            "Enter the monetary value relevant to your resolution type. For share "
                            "allotment, this is the total consideration. For authorized capital "
                            "increase, it is the new proposed capital. For loan approvals, enter the "
                            "borrowing limit. This amount will appear in the resolution text and any "
                            "related MCA filings, so ensure it is accurate."
                        ),
                    ),
                    _clause(
                        "br_bank_name",
                        "Bank Name",
                        "text",
                        "Bank name (for bank account resolution)",
                        required=False,
                        learn_more=(
                            "Enter the full official name of the bank where you are opening the "
                            "company's current account. Most startups open accounts with scheduled "
                            "commercial banks. The bank will require a certified copy of this board "
                            "resolution as part of the account opening documentation."
                        ),
                    ),
                    _clause(
                        "br_address",
                        "Address",
                        "textarea",
                        "Address details (for registered office change)",
                        required=False,
                        learn_more=(
                            "Provide the complete new registered office address including building "
                            "name, street, city, state, and PIN code. Changing the registered office "
                            "within the same city requires a board resolution and Form INC-22 filing. "
                            "A change across states requires shareholder approval by special resolution "
                            "and Central Government confirmation."
                        ),
                        india_note=(
                            "Under Section 12 of the Companies Act 2013, a company must have a "
                            "registered office within 30 days of incorporation. Any change must be "
                            "notified to the ROC via Form INC-22 within 30 days."
                        ),
                    ),
                    _clause(
                        "br_additional_details",
                        "Additional Details",
                        "textarea",
                        "Additional details specific to the resolution",
                        required=False,
                        learn_more=(
                            "Use this field to add any specifics not covered by the other fields. "
                            "For example, for a related party transaction, describe the nature and "
                            "terms of the transaction. For ESOP creation, mention the vesting schedule. "
                            "Being detailed here helps create a complete and defensible corporate record."
                        ),
                    ),
                    _clause(
                        "br_director_designation",
                        "Director Designation",
                        "dropdown",
                        "Type/designation of director being appointed",
                        options=[
                            "Additional Director",
                            "Non-Executive Director",
                            "Independent Director",
                            "Whole-Time Director",
                            "Managing Director",
                        ],
                        required=False,
                        depends_on="br_resolution_type",
                        learn_more=(
                            "The Companies Act, 2013 recognizes different categories. Additional "
                            "Directors (§ 161) hold office until the next AGM. Independent Directors "
                            "(§ 149) serve a fixed term and are not liable to retire by rotation. "
                            "Managing/Whole-Time Directors require approvals under §§ 196\u2013197."
                        ),
                    ),
                    _clause(
                        "br_num_shares",
                        "Number of Shares",
                        "number",
                        "Number of equity shares to be allotted",
                        required=False,
                        depends_on="br_resolution_type",
                        min_value=1,
                    ),
                    _clause(
                        "br_face_value",
                        "Face Value per Share (INR)",
                        "number",
                        "Nominal/face value per equity share in INR",
                        required=False,
                        depends_on="br_resolution_type",
                        default=10,
                        min_value=1,
                    ),
                    _clause(
                        "br_premium",
                        "Premium per Share (INR)",
                        "number",
                        "Share premium per equity share, if any",
                        required=False,
                        depends_on="br_resolution_type",
                        default=0,
                        min_value=0,
                    ),
                    _clause(
                        "br_auditor_frn",
                        "Auditor Firm Registration No.",
                        "text",
                        "ICAI Firm Registration Number (FRN) of the statutory auditor",
                        required=False,
                        depends_on="br_resolution_type",
                    ),
                    _clause(
                        "br_account_operation",
                        "Account Operation Mandate",
                        "dropdown",
                        "How the bank account will be operated",
                        options=["Singly", "Jointly", "Either or Survivor"],
                        required=False,
                        depends_on="br_resolution_type",
                        default="Singly",
                    ),
                ],
            },
            # Step 3: Authorization & Compliance
            {
                "step_number": 3,
                "title": "Authorization & Compliance",
                "description": "Specify who is authorized to act and filing requirements.",
                "clauses": [
                    _clause(
                        "br_authorized_signatory",
                        "Authorized Signatory",
                        "text",
                        "Name of person authorized to execute related documents",
                        learn_more=(
                            "This is the person the board authorizes to sign documents, file forms "
                            "with MCA, and execute any actions needed to implement the resolution. "
                            "Typically this is a director or the company secretary. Banks, government "
                            "agencies, and other third parties will rely on this authorization, so "
                            "choose someone who is readily available to sign documents."
                        ),
                    ),
                    _clause(
                        "br_filing_required",
                        "MCA Filing Required",
                        "toggle",
                        "Whether this resolution requires MCA filing",
                        learn_more=(
                            "Many board resolutions must be filed with MCA within specified "
                            "deadlines. Director appointment: DIR-12 within 30 days. Share "
                            "allotment: PAS-3 within 30 days. Registered office change: "
                            "INC-22 within 30 days."
                        ),
                        india_note=(
                            "Late filing attracts penalties under Companies Act 2013. The "
                            "penalty is \u20b9100 per day of delay for each form."
                        ),
                    ),
                ],
            },
        ],
    }


def _ordinal(n: int) -> str:
    """Return ordinal string (1 -> '1st', 2 -> '2nd', etc.)."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _indian_amount(n) -> str:
    """Format number in Indian numbering system (e.g., 10,00,000)."""
    try:
        n = int(n)
    except (ValueError, TypeError):
        return "0"
    if n < 0:
        return "-" + _indian_amount(-n)
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    parts: List[str] = []
    while rest:
        parts.append(rest[-2:] if len(rest) >= 2 else rest)
        rest = rest[:-2]
    parts.reverse()
    return ",".join(parts) + "," + last3


# MCA filing requirements per resolution type: (e-Form, Section, Deadline)
_BR_FILING_MAP = {
    "Director Appointment": ("DIR-12", "170(2)", "30 days"),
    "Director Resignation Acceptance": ("DIR-12", "168(1)", "30 days"),
    "Share Allotment": ("PAS-3", "39(4)", "30 days"),
    "Auditor Appointment": ("ADT-1", "139(1)", "15 days"),
    "Registered Office Change": ("INC-22", "12(4)", "30 days"),
    "Authorized Capital Increase": ("SH-7", "64(1)", "30 days"),
    "ESOP Pool Creation": ("PAS-3 / SH-7", "62(1)(b)", "30 days"),
    "Loan/Borrowing Approval": ("MGT-14", "179(3)(d)", "30 days"),
    "Related Party Transaction": ("MGT-14", "188 / 117", "30 days"),
}


def render_board_resolution(tpl: dict, config: dict, parties: dict) -> str:
    """Render Board Resolution HTML per Companies Act 2013 & Secretarial Standard SS-1."""
    company = config.get("br_company_name", "[Company Name]")
    cin = config.get("br_cin", "")
    res_type = config.get("br_resolution_type", "[Resolution Type]")
    meeting_date = config.get("br_meeting_date", "")
    meeting_place = config.get("br_meeting_place", "[Meeting Place]")
    directors = config.get("br_directors_present", "")
    person_name = config.get("br_person_name", "")
    person_din = config.get("br_person_din", "")
    amount = config.get("br_amount", 0)
    bank_name = config.get("br_bank_name", "")
    address = config.get("br_address", "")
    additional = config.get("br_additional_details", "")
    signatory = config.get("br_authorized_signatory", "[Authorized Signatory]")
    filing = config.get("br_filing_required", False)
    # New fields
    serial = config.get("br_meeting_serial", "")
    chairperson = config.get("br_chairperson_name", "")
    cs_name = config.get("br_company_secretary", "")
    reg_office = config.get("br_registered_office", "")
    directors_leave = config.get("br_directors_leave", "")
    designation = config.get("br_director_designation", "Additional Director")
    num_shares = config.get("br_num_shares", 0)
    face_value = config.get("br_face_value", 10)
    premium_val = config.get("br_premium", 0)
    auditor_frn = config.get("br_auditor_frn", "")
    account_op = config.get("br_account_operation", "Singly")

    # Safe integer parsing
    try:
        amount = int(amount) if amount else 0
    except (ValueError, TypeError):
        amount = 0
    try:
        num_shares = int(num_shares) if num_shares else 0
    except (ValueError, TypeError):
        num_shares = 0
    try:
        face_value = int(face_value) if face_value else 10
    except (ValueError, TypeError):
        face_value = 10
    try:
        premium_val = int(premium_val) if premium_val else 0
    except (ValueError, TypeError):
        premium_val = 0

    sections: List[str] = []

    # ----------------------------------------------------------------
    # Company letterhead
    # ----------------------------------------------------------------
    serial_num = ""
    if serial and str(serial).isdigit():
        serial_num = _ordinal(int(serial)).upper()
    else:
        serial_num = f"{serial or '____'}TH"

    sections.append(
        '<div style="text-align:center; border-bottom:2px solid #333; '
        'padding-bottom:12px; margin-bottom:20px;">'
        f'<p style="font-size:18px; font-weight:bold; text-transform:uppercase; '
        f'margin:0; letter-spacing:1px;">{company}</p>'
        + (f'<p style="font-size:11px; margin:2px 0;">CIN: {cin}</p>' if cin else '')
        + (f'<p style="font-size:11px; margin:2px 0;">Registered Office: {reg_office}</p>'
           if reg_office else '')
        + '</div>'
    )

    # ----------------------------------------------------------------
    # Meeting title per Secretarial Standard SS-1
    # ----------------------------------------------------------------
    sections.append(
        '<div style="text-align:center; margin-bottom:20px;">'
        '<p style="font-size:13px; font-weight:bold; text-transform:uppercase; '
        'text-decoration:underline; margin:0;">'
        f'MINUTES OF THE {serial_num} MEETING OF THE BOARD OF DIRECTORS</p>'
        '<p style="font-size:13px; font-weight:bold; text-transform:uppercase; '
        f'margin:4px 0;">OF {company.upper()}</p>'
        f'<p style="font-size:12px; margin:8px 0;">Held on '
        f'<strong>{meeting_date or "________________"}</strong> at '
        f'<strong>{meeting_place}</strong></p>'
        '</div>'
    )

    # ----------------------------------------------------------------
    # Directors Present (tabular)
    # ----------------------------------------------------------------
    director_lines = [
        d.strip() for d in directors.split("\n") if d.strip()
    ] if directors else []

    sections.append(
        '<h2 style="font-size:12px; text-transform:uppercase; margin-top:20px;">'
        'Directors Present:</h2>'
    )
    if director_lines:
        sections.append(
            '<table style="width:100%; border-collapse:collapse; margin-bottom:10px;">'
            '<tr style="border-bottom:1px solid #ccc;">'
            '<th style="text-align:left; padding:4px; width:40px;">Sr.</th>'
            '<th style="text-align:left; padding:4px;">Name &amp; DIN</th></tr>'
        )
        for i, d in enumerate(director_lines, 1):
            sections.append(
                f'<tr style="border-bottom:1px solid #eee;">'
                f'<td style="padding:4px;">{i}.</td>'
                f'<td style="padding:4px;">{d}</td></tr>'
            )
        sections.append('</table>')
    else:
        sections.append(
            '<p>1. ________________________</p>'
            '<p>2. ________________________</p>'
        )

    # ----------------------------------------------------------------
    # Leave of Absence
    # ----------------------------------------------------------------
    leave_lines = [
        d.strip() for d in directors_leave.split("\n") if d.strip()
    ] if directors_leave else []
    sections.append(
        '<h2 style="font-size:12px; text-transform:uppercase; margin-top:15px;">'
        'Leave of Absence:</h2>'
    )
    if leave_lines:
        sections.append(
            '<p class="clause">The Board granted leave of absence to the following '
            'Director(s) who could not attend the meeting:</p>'
            '<ol>' + ''.join(f'<li>{d}</li>' for d in leave_lines) + '</ol>'
        )
    else:
        sections.append(
            '<p class="clause">None. All Directors were present.</p>'
        )

    # ----------------------------------------------------------------
    # In Attendance
    # ----------------------------------------------------------------
    if cs_name:
        sections.append(
            '<h2 style="font-size:12px; text-transform:uppercase; margin-top:15px;">'
            'In Attendance:</h2>'
            f'<p class="clause">{cs_name}, Company Secretary</p>'
        )

    # ----------------------------------------------------------------
    # Chairperson & Quorum — Section 174, SS-1
    # ----------------------------------------------------------------
    chair_text = chairperson or (
        director_lines[0].split("(")[0].strip() if director_lines else "[Chairperson]"
    )
    sections.append(
        '<hr style="border:none; border-top:1px solid #999; margin:20px 0;">'
        f'<p class="clause"><strong>{chair_text}</strong>, Chairperson of the meeting, '
        'welcomed the Directors and took the Chair. The Chairperson noted that the '
        'requisite quorum was present in terms of Section 174 of the Companies Act, 2013 '
        'read with Secretarial Standard on Meetings of the Board of Directors (SS-1) '
        'issued by the Institute of Company Secretaries of India, and called the meeting '
        'to order.</p>'
    )

    # ----------------------------------------------------------------
    # Notice compliance — Section 173(3)
    # ----------------------------------------------------------------
    sections.append(
        '<p class="clause">The Chairperson informed the Board that due notice of the '
        'meeting had been given to all the Directors of the Company in accordance with '
        'Section 173(3) of the Companies Act, 2013 and Secretarial Standard SS-1, and '
        'the same was taken as read.</p>'
    )

    # ----------------------------------------------------------------
    # Resolution Item
    # ----------------------------------------------------------------
    sections.append(
        '<hr style="border:none; border-top:1px solid #999; margin:20px 0;">'
        f'<h2 style="font-size:13px; text-transform:uppercase;">'
        f'Item No. 1: {res_type}</h2>'
    )

    # Shorthand variables for resolution text
    _person = f'<strong>{person_name or "[Name]"}</strong>'
    _din = f' (DIN: {person_din})' if person_din else ''
    _amt = _indian_amount(amount)

    # ================================================================
    # Resolution bodies — WHEREAS recitals + RESOLVED clauses per type
    # ================================================================

    if res_type == "Director Appointment":
        retire_text = (
            'not liable to retire by rotation'
            if designation == 'Independent Director'
            else 'liable to retire by rotation'
        )
        sections.append(
            f'<p class="clause"><strong>WHEREAS</strong> the Board has received the '
            f'consent of {_person}{_din} to act as a Director of the Company in Form '
            f'DIR-2 pursuant to Rule 8 of the Companies (Appointment and Qualification '
            f'of Directors) Rules, 2014;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> the Board has verified that '
            f'{_person} is not disqualified from being appointed as a Director under '
            f'Section 164 of the Companies Act, 2013 and has furnished a declaration to '
            f'that effect;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> {_person} has given a '
            f'declaration pursuant to Rule 14 of the Companies (Appointment and '
            f'Qualification of Directors) Rules, 2014 confirming that '
            f'{person_name or "[Name]"} is not debarred from holding the office of '
            f'director by virtue of any order of NCLT or under the Companies Act, '
            f'2013;</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            f'provisions of Sections 152, 160, and 161 and other applicable provisions, '
            f'if any, of the Companies Act, 2013 read with the Companies (Appointment '
            f'and Qualification of Directors) Rules, 2014 (including any statutory '
            f'modification(s) or re-enactment(s) thereof for the time being in force) '
            f'and subject to the provisions of the Articles of Association of the '
            f'Company, {_person}{_din} be and is hereby appointed as '
            f'<strong>{designation}</strong> of the Company, {retire_text}, with effect '
            f'from {meeting_date or "[Date]"}.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> the Board '
            f'hereby notes that {_person} has confirmed that {person_name or "[Name]"} '
            f'is not disqualified from being appointed as a Director in terms of '
            f'Section 164(2) of the Companies Act, 2013 and has given consent to act as '
            f'a Director in Form DIR-2.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to file e-Form '
            f'DIR-12 with the Registrar of Companies within thirty (30) days of such '
            f'appointment in terms of Section 170(2) of the Companies Act, 2013, and to '
            f'do all such acts, deeds, matters, and things as may be necessary, proper, '
            f'or desirable to give effect to this resolution.\u201d</p>'
        )

    elif res_type == "Director Resignation Acceptance":
        sections.append(
            f'<p class="clause"><strong>WHEREAS</strong> the Board has received a letter '
            f'of resignation dated {meeting_date or "[Date]"} from {_person}{_din} from '
            f'the office of Director of the Company;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> the Board has noted that as '
            f'per Section 168(1) of the Companies Act, 2013, a director may resign from '
            f'the office by giving a notice in writing to the Company, and the '
            f'resignation shall take effect from the date on which the notice is received '
            f'by the Board or the date, if any, specified in the notice, whichever is '
            f'later;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> {_person} has confirmed '
            f'that there are no pending matters or obligations requiring attention;</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> the resignation of '
            f'{_person}{_din} from the office of Director of the Company be and is '
            f'hereby noted and accepted with effect from '
            f'{meeting_date or "[Date]"}, and the Board places on record its '
            f'appreciation for the valuable services rendered by '
            f'{person_name or "[Name]"} during the tenure as Director of the '
            f'Company.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to file e-Form '
            f'DIR-12 with the Registrar of Companies within thirty (30) days of such '
            f'cessation, and to intimate any other regulatory authorities as may be '
            f'necessary.\u201d</p>'
        )

    elif res_type == "Bank Account Opening":
        sections.append(
            f'<p class="clause"><strong>WHEREAS</strong> the Company requires a current '
            f'account for its day-to-day business operations and management of '
            f'funds;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> the Board has considered '
            f'and found it expedient to open a current account with '
            f'<strong>{bank_name or "[Bank Name]"}</strong>;</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to '
            f'Section 179 and other applicable provisions of the Companies Act, 2013, '
            f'a current account be and is hereby authorized to be opened in the name '
            f'and style of the Company, i.e., <strong>{company}</strong>, with '
            f'<strong>{bank_name or "[Bank Name]"}</strong>, and the following '
            f'person(s) be and are hereby authorized as the authorized signatory(ies) '
            f'for operating the said account '
            f'<strong>{account_op.lower()}</strong>:</p>'
            f'<ol><li><strong>{signatory}</strong></li></ol>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> the '
            f'authorized signatory(ies) be and are hereby empowered, '
            f'{account_op.lower()}, to:</p>'
            f'<ol type="a">'
            f'<li>sign, execute, and deliver cheques, demand drafts, pay orders, and '
            f'other negotiable instruments;</li>'
            f'<li>authorize and execute fund transfers through NEFT, RTGS, IMPS, or any '
            f'other electronic mode of transfer;</li>'
            f'<li>operate the account through internet banking, mobile banking, or any '
            f'other digital banking facility offered by the Bank;</li>'
            f'<li>authorize standing instructions, auto-debit mandates, and recurring '
            f'payments;</li>'
            f'<li>sign any documents, forms, agreements, declarations, or undertakings '
            f'as may be required by the Bank for opening and operating the said '
            f'account.</li>'
            f'</ol>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> a certified '
            f'true copy of this resolution, duly signed by a Director of the Company, be '
            f'furnished to <strong>{bank_name or "[Bank Name]"}</strong> as evidence and '
            f'proof of the authority herein conferred.\u201d</p>'
        )

    elif res_type == "Share Allotment":
        total = num_shares * (face_value + premium_val) if num_shares else amount
        if num_shares:
            share_desc = (
                f'{_indian_amount(num_shares)} equity shares of INR '
                f'{_indian_amount(face_value)} each'
                + (f' at a premium of INR {_indian_amount(premium_val)} per share'
                   if premium_val else '')
            )
        else:
            share_desc = f'equity shares for a total consideration of INR {_amt}'

        sections.append(
            f'<p class="clause"><strong>WHEREAS</strong> the Board has considered the '
            f'proposal for allotment of equity shares of the Company in accordance with '
            f'the provisions of Section 62 of the Companies Act, 2013 read with the '
            f'Companies (Share Capital and Debentures) Rules, 2014;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> the Board has noted that '
            f'the consideration for the proposed allotment has been received / will be '
            f'received prior to allotment;</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            f'provisions of Section 62 and other applicable provisions, if any, of the '
            f'Companies Act, 2013 read with the Companies (Share Capital and Debentures) '
            f'Rules, 2014 (including any statutory modification(s) or re-enactment(s) '
            f'thereof for the time being in force) and subject to the provisions of the '
            f'Memorandum and Articles of Association of the Company, the Board hereby '
            f'approves the allotment of {share_desc}, aggregating to a total '
            f'consideration of INR {_indian_amount(total or amount)}, to {_person}, on '
            f'such terms and conditions as set out herein.\u201d</p>'
        )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> the equity '
            'shares so allotted shall rank pari passu in all respects with the existing '
            'equity shares of the Company.\u201d</p>'
        )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> share '
            'certificates be issued to the allottee(s) within two (2) months from the '
            'date of allotment in accordance with Section 56(4) of the Companies Act, '
            '2013.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to file the '
            f'return of allotment in e-Form PAS-3 with the Registrar of Companies '
            f'within thirty (30) days of such allotment in terms of Section 39(4) of '
            f'the Companies Act, 2013, and to execute all documents and do all acts '
            f'necessary to give effect to this resolution.\u201d</p>'
        )

    elif res_type == "Auditor Appointment":
        frn_text = f' (FRN: {auditor_frn})' if auditor_frn else ''
        sections.append(
            f'<p class="clause"><strong>WHEREAS</strong> pursuant to Section 139(1) of '
            f'the Companies Act, 2013, the Company is required to appoint a Statutory '
            f'Auditor;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> {_person}{frn_text}, '
            f'Chartered Accountants, have conveyed their written consent and confirmed '
            f'their eligibility for appointment as Statutory Auditor under Section 141 '
            f'of the Companies Act, 2013;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> {_person} have confirmed '
            f'that their appointment, if made, would be within the limits prescribed '
            f'under Section 141(3)(g) of the Companies Act, 2013;</p>'
        )
        rem_text = (
            f' at a remuneration of INR {_amt} (Rupees {_amt} only)'
            if amount else ''
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            f'provisions of Section 139 and other applicable provisions, if any, of the '
            f'Companies Act, 2013 read with the Companies (Audit and Auditors) Rules, '
            f'2014 (including any statutory modification(s) or re-enactment(s) thereof '
            f'for the time being in force), and based on the recommendation of the Audit '
            f'Committee (where applicable), {_person}{frn_text}, Chartered Accountants, '
            f'be and are hereby appointed as the Statutory Auditor of the Company'
            f'{rem_text}, plus applicable taxes and reimbursement of out-of-pocket '
            f'expenses, to hold office from the conclusion of this meeting until the '
            f'conclusion of the Annual General Meeting to be held for the financial year '
            f'ending on March 31, [____], subject to ratification of the appointment by '
            f'the members at every subsequent Annual General Meeting, if '
            f'applicable.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to file the '
            f'notice of appointment in e-Form ADT-1 with the Registrar of Companies '
            f'within fifteen (15) days of such appointment in terms of Section 139(1) '
            f'of the Companies Act, 2013.\u201d</p>'
        )

    elif res_type == "Registered Office Change":
        sections.append(
            '<p class="clause"><strong>WHEREAS</strong> the Board has considered and '
            'found it necessary and expedient in the interest of the Company to shift '
            'the registered office of the Company;</p>'

            '<p class="clause"><strong>AND WHEREAS</strong> the Board has noted that '
            'the change of registered office within the local limits of the same '
            'city/town/village does not require approval of the members;</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            f'provisions of Section 12 and other applicable provisions, if any, of the '
            f'Companies Act, 2013 read with the Companies (Incorporation) Rules, 2014 '
            f'(including any statutory modification(s) or re-enactment(s) thereof for '
            f'the time being in force), the registered office of the Company be and is '
            f'hereby shifted to:</p>'
            f'<p class="clause" style="padding-left:40px; font-weight:bold;">'
            f'{address or "[New Registered Office Address with PIN Code]"}</p>'
            f'<p class="clause">with effect from '
            f'{meeting_date or "[Date]"}.\u201d</p>'
        )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> all '
            'statutory records, registers, and documents of the Company be kept at the '
            'new registered office address with effect from the said date.\u201d</p>'
        )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> the name '
            'board displaying the name and registered office address of the Company be '
            'affixed at the new registered office in accordance with Section 12(3)(a) '
            'of the Companies Act, 2013, and the letterhead, stationery, and website of '
            'the Company be updated accordingly.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to file e-Form '
            f'INC-22 with the Registrar of Companies within thirty (30) days of such '
            f'change, along with the proof of the new registered office address, and to '
            f'do all such acts and things as may be necessary.\u201d</p>'
        )

    elif res_type == "ESOP Pool Creation":
        sections.append(
            '<p class="clause"><strong>WHEREAS</strong> the Board recognizes the need '
            'to attract, retain, and motivate key employees by offering them an '
            'opportunity to participate in the growth of the Company through equity '
            'ownership;</p>'

            '<p class="clause"><strong>AND WHEREAS</strong> the Board has considered '
            'the creation of an Employee Stock Option Plan (\u201cESOP\u201d) in '
            'accordance with the provisions of Section 62(1)(b) of the Companies Act, '
            '2013 read with Rule 12 of the Companies (Share Capital and Debentures) '
            'Rules, 2014;</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            f'provisions of Section 62(1)(b) of the Companies Act, 2013 read with '
            f'Rule 12 of the Companies (Share Capital and Debentures) Rules, 2014 '
            f'(including any statutory modification(s) or re-enactment(s) thereof for '
            f'the time being in force), the Board hereby recommends to the shareholders '
            f'for their approval by way of Special Resolution, the creation of an '
            f'Employee Stock Option Plan with a pool of INR {_amt} (Rupees {_amt} '
            f'only), the key terms of which are as follows:</p>'
            f'<ol type="a">'
            f'<li>Total number of options: as may be decided by the Board from time to '
            f'time;</li>'
            f'<li>Exercise price: as may be determined by the Board;</li>'
            f'<li>Vesting period: minimum one (1) year from the date of grant in '
            f'accordance with Rule 12(1);</li>'
            f'<li>Exercise period: as determined by the Board;</li>'
            f'<li>Eligible employees: present and future permanent employees of the '
            f'Company (excluding Independent Directors and promoters holding more than '
            f'10% of outstanding equity).</li>'
            f'</ol>'
        )
        if additional:
            sections.append(
                f'<p class="clause"><em>Additional terms noted by the Board:</em> '
                f'{additional}</p>'
            )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> the ESOP '
            'shall be subject to the approval of the shareholders of the Company by way '
            'of Special Resolution at the next General Meeting in terms of '
            'Section 62(1)(b).\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to finalize and '
            f'circulate the detailed ESOP scheme, convene a General Meeting for '
            f'obtaining shareholder approval, and file the necessary e-forms with the '
            f'Registrar of Companies.\u201d</p>'
        )

    elif res_type == "Authorized Capital Increase":
        sections.append(
            '<p class="clause"><strong>WHEREAS</strong> the present authorized share '
            'capital of the Company is insufficient to meet the proposed allotment / '
            'business requirements;</p>'

            '<p class="clause"><strong>AND WHEREAS</strong> the Board has considered '
            'and found it necessary to increase the authorized share capital of the '
            'Company pursuant to Section 61 of the Companies Act, 2013;</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            f'provisions of Section 61 and other applicable provisions, if any, of the '
            f'Companies Act, 2013 read with the Companies (Share Capital and Debentures) '
            f'Rules, 2014 (including any statutory modification(s) or re-enactment(s) '
            f'thereof for the time being in force) and subject to the approval of the '
            f'members by way of Ordinary Resolution, the authorized share capital of '
            f'the Company be and is hereby proposed to be increased from INR '
            f'[Existing Authorized Capital] to INR {_amt} (Rupees {_amt} only) by the '
            f'creation of additional equity shares of INR '
            f'{_indian_amount(face_value)} each, ranking pari passu with the existing '
            f'equity shares of the Company.\u201d</p>'
        )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> the '
            'Memorandum of Association of the Company be altered accordingly by '
            'substituting the existing Clause V (Capital Clause) with the revised '
            'capital clause reflecting the increased authorized share '
            'capital.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to convene an '
            f'Extraordinary General Meeting / pass the Ordinary Resolution by way of '
            f'postal ballot, and upon passing of the resolution, to file e-Form SH-7 '
            f'with the Registrar of Companies within thirty (30) days in terms of '
            f'Section 64(1) of the Companies Act, 2013.\u201d</p>'
        )

    elif res_type == "Loan/Borrowing Approval":
        lender = f'from <strong>{bank_name}</strong> ' if bank_name else ''
        sections.append(
            '<p class="clause"><strong>WHEREAS</strong> the Company requires funds for '
            'its business operations / capital expenditure / working capital '
            'requirements;</p>'

            f'<p class="clause"><strong>AND WHEREAS</strong> the Board has considered '
            f'and found it expedient to borrow funds {lender}on such terms and '
            f'conditions as may be mutually agreed;</p>'

            '<p class="clause"><strong>AND WHEREAS</strong> the aggregate borrowings '
            'of the Company together with this proposed borrowing [do / do not] exceed '
            'the aggregate of the paid-up share capital, free reserves and securities '
            'premium account of the Company, and accordingly [a Board Resolution is '
            'sufficient / a Special Resolution under Section 180(1)(c) will be '
            'required];</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            f'provisions of Section 179(3)(d) and Section 186 and other applicable '
            f'provisions, if any, of the Companies Act, 2013 (including any statutory '
            f'modification(s) or re-enactment(s) thereof for the time being in force), '
            f'the Board hereby approves borrowing of a sum not exceeding INR {_amt} '
            f'(Rupees {_amt} only) {lender}on such terms and conditions as may be '
            f'agreed upon, including but not limited to interest rate, repayment '
            f'schedule, and security/collateral.\u201d</p>'
        )
        if additional:
            sections.append(
                f'<p class="clause"><em>Key terms noted:</em> {additional}</p>'
            )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to negotiate, '
            f'finalize, and execute all loan agreements, security documents, '
            f'guarantees, and other documents as may be required, and to do all such '
            f'acts, deeds, and things as may be necessary to give effect to this '
            f'resolution, including filing of e-Form MGT-14 (if applicable) with the '
            f'Registrar of Companies within thirty (30) days.\u201d</p>'
        )

    elif res_type == "Related Party Transaction":
        sections.append(
            f'<p class="clause"><strong>WHEREAS</strong> the Board has received a '
            f'proposal for entering into a transaction with {_person}, a related party '
            f'within the meaning of Section 2(76) of the Companies Act, 2013;</p>'

            '<p class="clause"><strong>AND WHEREAS</strong> the interested Director(s), '
            'having a concern or interest in the proposed transaction, have disclosed '
            'their interest pursuant to Section 184 of the Companies Act, 2013 and have '
            'not participated in the discussion and voting on this item;</p>'

            '<p class="clause"><strong>AND WHEREAS</strong> the Board, having '
            'considered the terms and conditions of the proposed transaction, is '
            'satisfied that the same is on an arm\'s length basis and in the ordinary '
            'course of business;</p>'
        )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED THAT</strong> pursuant to the '
            'provisions of Section 188 and other applicable provisions, if any, of the '
            'Companies Act, 2013 read with Rule 15 of the Companies (Meetings of Board '
            'and its Powers) Rules, 2014 (including any statutory modification(s) or '
            're-enactment(s) thereof for the time being in force), and subject to such '
            'other approvals as may be required, the consent of the Board be and is '
            'hereby accorded for entering into the following related party '
            'transaction:</p>'
            '<table style="width:100%; border-collapse:collapse; margin:10px 0;">'
            '<tr style="border:1px solid #999;">'
            '<td style="padding:6px; border:1px solid #999; width:40%;">'
            '<strong>Related Party</strong></td>'
            f'<td style="padding:6px; border:1px solid #999;">'
            f'{person_name or "[Name]"}</td></tr>'
            '<tr style="border:1px solid #999;">'
            '<td style="padding:6px; border:1px solid #999;">'
            '<strong>Nature of Transaction</strong></td>'
            f'<td style="padding:6px; border:1px solid #999;">'
            f'{additional or "[Describe nature and terms]"}</td></tr>'
            '<tr style="border:1px solid #999;">'
            '<td style="padding:6px; border:1px solid #999;">'
            '<strong>Maximum Value (INR)</strong></td>'
            f'<td style="padding:6px; border:1px solid #999;">{_amt}</td></tr>'
            '</table>'
        )
        sections.append(
            '<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> the '
            'transaction be entered in the Register of Contracts maintained under '
            'Section 189 of the Companies Act, 2013.\u201d</p>'
        )
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED FURTHER THAT</strong> '
            f'<strong>{signatory}</strong> be and is hereby authorized to execute all '
            f'necessary agreements and documents, and to file e-Form MGT-14 with the '
            f'Registrar of Companies within thirty (30) days in terms of Section 117 '
            f'of the Companies Act, 2013 (if applicable), and to do all such acts and '
            f'things as may be necessary.\u201d</p>'
        )

    else:
        sections.append(
            f'<p class="clause"><strong>\u201cRESOLVED THAT</strong> '
            f'{additional or "[Resolution details to be specified]"}.\u201d</p>'
        )

    # ----------------------------------------------------------------
    # Additional details (if not consumed by type-specific rendering)
    # ----------------------------------------------------------------
    if additional and res_type not in (
        "Related Party Transaction", "ESOP Pool Creation",
        "Loan/Borrowing Approval",
    ):
        sections.append(
            f'<p class="clause"><em>Additional details noted by the Board:</em> '
            f'{additional}</p>'
        )

    # ----------------------------------------------------------------
    # Filing compliance note with specific form, section, deadline
    # ----------------------------------------------------------------
    filing_info = _BR_FILING_MAP.get(res_type)
    if filing or filing_info:
        if filing_info:
            form_name, section_ref, deadline = filing_info
            sections.append(
                '<div style="background:#f8f9fa; border-left:4px solid #0d6efd; '
                'padding:12px; margin:15px 0;">'
                '<p style="margin:0; font-weight:bold;">Compliance Note:</p>'
                f'<p style="margin:4px 0;">MCA e-Form: '
                f'<strong>{form_name}</strong></p>'
                f'<p style="margin:4px 0;">Statutory Reference: Section {section_ref}, '
                f'Companies Act, 2013</p>'
                f'<p style="margin:4px 0;">Filing Deadline: Within '
                f'<strong>{deadline}</strong> from the date of this resolution</p>'
                '<p style="margin:4px 0; font-size:11px; color:#666;">Late filing '
                'attracts additional fees under Section 403 of the Companies Act, 2013 '
                '(Rs 100 per day of delay).</p>'
                '</div>'
            )
        else:
            sections.append(
                '<p class="clause"><em>Note: This resolution requires filing with the '
                'Ministry of Corporate Affairs (MCA) within the prescribed time '
                'limit.</em></p>'
            )

    # ----------------------------------------------------------------
    # Closure
    # ----------------------------------------------------------------
    sections.append(
        '<hr style="border:none; border-top:1px solid #999; margin:20px 0;">'
        '<p class="clause">There being no other business, the Chairperson thanked the '
        'Directors for their participation and the meeting was concluded with a vote '
        'of thanks to the Chair.</p>'
        '<p class="clause"><strong>Time of conclusion:</strong> ____________</p>'
    )

    # ----------------------------------------------------------------
    # Signature blocks — one per director present
    # ----------------------------------------------------------------
    sections.append('<div style="margin-top:40px;">')
    if director_lines:
        sig_grid = (
            '<div style="display:flex; flex-wrap:wrap; gap:30px; margin-top:20px;">'
        )
        for d in director_lines:
            name_part = d.split("(")[0].strip() if "(" in d else d
            din_part = ""
            if "(" in d and ")" in d:
                din_part = d[d.index("("):d.index(")") + 1]
            sig_grid += (
                '<div style="min-width:200px; margin-bottom:30px;">'
                '<div style="border-bottom:1px solid #333; width:200px; '
                'margin-bottom:5px;">&nbsp;</div>'
                f'<p style="margin:2px 0; font-weight:bold;">{name_part}</p>'
                f'<p style="margin:2px 0; font-size:11px;">Director {din_part}</p>'
                '</div>'
            )
        sig_grid += '</div>'
        sections.append(sig_grid)
    else:
        sections.append(
            '<div style="display:flex; gap:40px; margin-top:20px;">'
            '<div style="min-width:200px;">'
            '<div style="border-bottom:1px solid #333; width:200px; '
            'margin-bottom:5px;">&nbsp;</div>'
            '<p style="margin:2px 0; font-weight:bold;">[Chairperson]</p></div>'
            '<div style="min-width:200px;">'
            '<div style="border-bottom:1px solid #333; width:200px; '
            'margin-bottom:5px;">&nbsp;</div>'
            '<p style="margin:2px 0; font-weight:bold;">[Director]</p></div>'
            '</div>'
        )

    # Company Secretary attestation
    if cs_name:
        sections.append(
            '<div style="margin-top:30px;">'
            '<div style="border-bottom:1px solid #333; width:200px; '
            'margin-bottom:5px;">&nbsp;</div>'
            f'<p style="margin:2px 0; font-weight:bold;">{cs_name}</p>'
            '<p style="margin:2px 0; font-size:11px;">Company Secretary</p>'
            '<p style="margin:2px 0; font-size:10px; color:#666;">'
            '(Certified that the above is a true and correct record of the '
            'proceedings of the meeting in compliance with Secretarial Standard '
            'SS-1)</p>'
            '</div>'
        )

    sections.append('</div>')

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Board Resolution \u2014 {res_type}", body, meeting_date
    )


# ======================================================================
# TEMPLATE 10: PRIVACY POLICY (DPDP ACT 2023)
# ======================================================================

def privacy_policy_template() -> dict:
    """Template 10 — Privacy Policy compliant with DPDP Act 2023 & DPDP Rules 2025."""
    return {
        "name": "Privacy Policy (DPDP Act 2023 & Rules 2025)",
        "description": (
            "Privacy policy compliant with India's Digital Personal Data Protection "
            "Act 2023 (DPDP Act), DPDP Rules 2025 (notified 14 November 2025), and "
            "IT Act 2000. Essential for any business collecting user data in India."
        ),
        "category": "Compliance",
        "steps": [
            # Step 1: Business Information
            {
                "step_number": 1,
                "title": "Business Information",
                "description": "Basic details about your company and online presence.",
                "clauses": [
                    _clause(
                        "pp_company_name",
                        "Company Name",
                        "text",
                        "Name of the company/data fiduciary",
                        learn_more=(
                            "Under the DPDP Act 2023, your company is the 'Data Fiduciary' \u2014 "
                            "the entity that determines the purpose and means of processing personal "
                            "data. Use your exact registered company name as it will appear at the top "
                            "of your privacy policy and in any regulatory correspondence with the Data "
                            "Protection Board of India."
                        ),
                    ),
                    _clause(
                        "pp_website_url",
                        "Website URL",
                        "text",
                        "Website URL",
                        learn_more=(
                            "Enter the primary URL where your privacy policy will be published. "
                            "Under the DPDP Act 2023, the privacy policy must be easily accessible "
                            "to users before they provide their data. If you operate multiple websites "
                            "or apps, use the main domain and consider linking the policy from all "
                            "your digital properties."
                        ),
                    ),
                    _clause(
                        "pp_contact_email",
                        "Contact Email",
                        "text",
                        "Contact email for privacy queries",
                        learn_more=(
                            "This email will be published in your privacy policy as the primary "
                            "contact for data-related queries, consent withdrawal requests, and "
                            "grievances. Use a dedicated email like privacy@yourcompany.com rather "
                            "than a personal email, so the address remains valid even if team members "
                            "change. This email must be monitored regularly to meet response deadlines."
                        ),
                    ),
                    _clause(
                        "pp_business_type",
                        "Business Type",
                        "dropdown",
                        "Type of business",
                        options=[
                            "SaaS/Technology",
                            "E-commerce",
                            "Fintech",
                            "Healthcare",
                            "Education",
                            "General Services",
                            "Marketplace",
                        ],
                        learn_more=(
                            "Your business type determines what additional sector-specific "
                            "regulations apply beyond the DPDP Act. For example, Fintech companies "
                            "must also comply with RBI data localization guidelines, Healthcare "
                            "companies handle sensitive health data with stricter obligations, and "
                            "E-commerce platforms are subject to Consumer Protection (E-Commerce) "
                            "Rules 2020. Select the option that best describes your primary business."
                        ),
                    ),
                ],
            },
            # Step 2: Data Collection
            {
                "step_number": 2,
                "title": "Data Collection",
                "description": "What personal data you collect and why.",
                "clauses": [
                    _clause(
                        "pp_personal_data_collected",
                        "Personal Data Collected",
                        "multi_select",
                        "Types of personal data collected",
                        options=[
                            "Name",
                            "Email address",
                            "Phone number",
                            "Physical address",
                            "Date of birth",
                            "Government IDs (Aadhaar, PAN)",
                            "Financial information",
                            "Location data",
                            "Device information",
                            "Usage analytics",
                            "Cookies & tracking data",
                            "Biometric data",
                            "Health data",
                        ],
                        learn_more=(
                            "Select every type of personal data your product collects, even if "
                            "collected indirectly through analytics or third-party SDKs. Under the "
                            "DPDP Act, you must disclose all categories of data you process. "
                            "Collecting more data than disclosed in your policy can lead to penalties "
                            "of up to \u20b9250 crore. When in doubt, include the category \u2014 it is "
                            "better to over-disclose than under-disclose."
                        ),
                        india_note=(
                            "Under DPDP Act 2023, 'personal data' means any data about an "
                            "individual who is identifiable by or in relation to such data. "
                            "'Sensitive personal data' gets additional protections."
                        ),
                    ),
                    _clause(
                        "pp_collection_methods",
                        "Collection Methods",
                        "multi_select",
                        "How data is collected",
                        options=[
                            "Direct from user (forms, registration)",
                            "Automatically (cookies, analytics)",
                            "Third-party sources",
                            "Public sources",
                        ],
                        learn_more=(
                            "Be transparent about all the ways you gather user data. Direct "
                            "collection includes signup forms and profile pages. Automatic collection "
                            "covers cookies, server logs, and analytics SDKs like Google Analytics or "
                            "Mixpanel. Third-party sources include social login providers or data "
                            "enrichment services. The DPDP Act requires you to inform users of each "
                            "collection method before or at the time of data collection."
                        ),
                    ),
                    _clause(
                        "pp_purpose_of_collection",
                        "Purpose of Collection",
                        "multi_select",
                        "Purposes for collecting data",
                        options=[
                            "Account creation & management",
                            "Service delivery",
                            "Payment processing",
                            "Communication & marketing",
                            "Analytics & improvement",
                            "Legal compliance",
                            "Fraud prevention",
                            "Personalization",
                        ],
                        learn_more=(
                            "Select every purpose for which you use personal data. Under the DPDP "
                            "Act, purpose limitation is a fundamental principle \u2014 you cannot use "
                            "data for a purpose you did not disclose. If you later want to use data "
                            "for a new purpose (e.g., adding marketing emails), you must obtain fresh "
                            "consent. Only select purposes you genuinely need to avoid over-collection."
                        ),
                        india_note=(
                            "Under DPDP Act 2023, personal data can only be processed for "
                            "the purpose for which consent was given. Purpose limitation is "
                            "a key principle."
                        ),
                    ),
                ],
            },
            # Step 3: Data Processing & Sharing
            {
                "step_number": 3,
                "title": "Data Processing & Sharing",
                "description": "Where data is stored, how long it is retained, and who it is shared with.",
                "clauses": [
                    _clause(
                        "pp_data_storage_location",
                        "Data Storage Location",
                        "dropdown",
                        "Where data is stored",
                        options=[
                            "India only",
                            "India + international (with safeguards)",
                            "Cloud (provider choice)",
                        ],
                        learn_more=(
                            "This determines where your users' personal data is physically stored. "
                            "If you use AWS, GCP, or Azure, check which region your servers are in. "
                            "Storing data in India only provides maximum regulatory safety but may "
                            "limit your cloud provider options. International storage is allowed under "
                            "DPDP Act unless the destination country is specifically restricted by "
                            "the Central Government."
                        ),
                        pros=["India only: Maximum compliance, no cross-border risk",
                              "International: Better performance for global users, more provider options",
                              "Cloud provider choice: Flexibility and cost optimization"],
                        cons=["India only: Higher costs, fewer provider options",
                              "International: Risk if government restricts a country later",
                              "Cloud provider choice: Less control over where data physically resides"],
                        india_note=(
                            "DPDP Act 2023 allows data transfer outside India to all "
                            "countries EXCEPT those specifically restricted by the Central "
                            "Government. No adequacy assessment needed (unlike GDPR). "
                            "However, certain categories of data notified by government "
                            "may have localization requirements."
                        ),
                    ),
                    _clause(
                        "pp_data_retention",
                        "Data Retention Period",
                        "dropdown",
                        "How long data is retained",
                        options=[
                            "Until account deletion",
                            "2 years after last activity",
                            "As required by law",
                            "Custom period",
                        ],
                        learn_more=(
                            "Data retention defines how long you keep user data after collection. "
                            "Under the DPDP Act, you must erase personal data when it is no longer "
                            "needed for the stated purpose or when the user withdraws consent. "
                            "Keeping data indefinitely increases your compliance risk and breach "
                            "liability. Choose the shortest retention period that works for your "
                            "business needs."
                        ),
                        pros=["Until account deletion: Simple, user-controlled",
                              "2 years after last activity: Balanced approach, auto-cleanup",
                              "As required by law: Flexible, covers regulatory needs"],
                        cons=["Until account deletion: Data may linger if users abandon accounts",
                              "2 years: May lose useful data for analytics",
                              "As required by law: Vague, harder to enforce consistently"],
                    ),
                    _clause(
                        "pp_third_party_sharing",
                        "Third-Party Sharing",
                        "multi_select",
                        "Categories of third parties data may be shared with",
                        options=[
                            "Payment processors",
                            "Cloud/hosting providers",
                            "Analytics services",
                            "Marketing partners",
                            "Government/regulatory bodies (when required)",
                            "Business partners",
                        ],
                        learn_more=(
                            "List every category of third party you share user data with, even "
                            "if the sharing is automated through integrations. Under the DPDP Act, "
                            "third parties processing data on your behalf are 'Data Processors' and "
                            "you remain responsible for how they handle the data. You must have "
                            "contractual safeguards with each processor. Failing to disclose sharing "
                            "relationships can result in significant penalties."
                        ),
                    ),
                    _clause(
                        "pp_cookies_used",
                        "Cookies Used",
                        "toggle",
                        "Whether the website/app uses cookies",
                        learn_more=(
                            "Cookies are small text files stored on users' browsers that track "
                            "behavior, remember preferences, and enable analytics. Even if you do not "
                            "set cookies directly, third-party services like Google Analytics, "
                            "Facebook Pixel, or Intercom may set cookies on your behalf. Check your "
                            "website with a cookie scanner tool to find out. If you use any tracking "
                            "scripts, enable this option."
                        ),
                    ),
                ],
            },
            # Step 4: User Rights & Contact
            {
                "step_number": 4,
                "title": "User Rights & Contact",
                "description": "Rights available to users and how they can reach you.",
                "clauses": [
                    _clause(
                        "pp_user_rights",
                        "User Rights",
                        "multi_select",
                        "Rights available to data principals (users)",
                        options=[
                            "Access their data",
                            "Correct inaccurate data",
                            "Delete their data (erasure)",
                            "Withdraw consent",
                            "Data portability",
                            "Nominate another person",
                            "Lodge grievance",
                        ],
                        learn_more=(
                            "These are the rights you grant your users over their personal data. "
                            "The DPDP Act 2023 mandates certain rights (access, correction, erasure, "
                            "consent withdrawal, grievance redressal, and nomination), so it is "
                            "recommended to include all of them. Selecting all rights ensures "
                            "compliance and builds user trust. You must also build internal processes "
                            "to actually fulfill these rights when users request them."
                        ),
                        india_note=(
                            "Under DPDP Act 2023, Data Principals have: Right to access "
                            "information about processing, right to correction and erasure, "
                            "right to grievance redressal, right to nominate. The Data "
                            "Fiduciary must respond within prescribed time. Children's data "
                            "(under 18) requires verifiable parental consent."
                        ),
                        common_choice_label="Include all rights",
                    ),
                    _clause(
                        "pp_grievance_officer",
                        "Grievance Officer",
                        "text",
                        "Name/designation of the Grievance Officer",
                        learn_more=(
                            "The Grievance Officer is the person users contact when they have "
                            "concerns about how their data is handled. This is a mandatory "
                            "appointment under the DPDP Act. For early-stage startups, a founder or "
                            "senior team member typically takes this role. The Grievance Officer must "
                            "acknowledge complaints within 48 hours and resolve them within the "
                            "prescribed timeline."
                        ),
                        india_note=(
                            "Under DPDP Act 2023, every Data Fiduciary must appoint a "
                            "Data Protection Officer or designate a person to handle data "
                            "principal grievances."
                        ),
                    ),
                    _clause(
                        "pp_consent_mechanism",
                        "Consent Mechanism",
                        "dropdown",
                        "How user consent is obtained",
                        options=[
                            "Opt-in checkbox",
                            "Click-wrap agreement",
                            "Browse-wrap",
                            "Explicit consent form",
                        ],
                        learn_more=(
                            "This determines how users give permission for you to process their "
                            "data. Opt-in checkbox requires users to actively check a box, which is "
                            "the safest legally. Click-wrap means users click 'I Agree' to proceed. "
                            "Browse-wrap (using the site implies consent) is the weakest and may not "
                            "satisfy DPDP Act requirements. Explicit consent forms are best for "
                            "sensitive data like health or financial information."
                        ),
                        pros=["Opt-in checkbox: Strongest legal protection, DPDP compliant",
                              "Click-wrap: Good balance of compliance and user experience",
                              "Explicit consent form: Best for sensitive data categories"],
                        cons=["Opt-in checkbox: Higher friction, some users may not check the box",
                              "Click-wrap: May not hold up for sensitive data processing",
                              "Browse-wrap: Weakest legally, likely non-compliant with DPDP Act"],
                        warning_condition={
                            "value": "Browse-wrap",
                            "message": (
                                "Browse-wrap consent (where using the site implies agreement) is "
                                "unlikely to satisfy the DPDP Act requirement for 'clear affirmative "
                                "action'. This approach has been challenged in Indian courts and may "
                                "expose you to penalties."
                            ),
                        },
                        india_note=(
                            "DPDP Act 2023 requires consent to be free, specific, informed, "
                            "unconditional, and unambiguous. Pre-ticked boxes or bundled "
                            "consent is not valid. Consent must be given by clear "
                            "affirmative action."
                        ),
                        common_choice_label="Most compliant: Opt-in checkbox",
                    ),
                    _clause(
                        "pp_children_data",
                        "Children's Data",
                        "toggle",
                        "Whether the platform collects data from children (under 18)",
                        learn_more=(
                            "Enable this if your platform may be used by anyone under 18 years "
                            "of age. The DPDP Act has strict requirements for children's data: you "
                            "must obtain verifiable parental consent, you cannot track or "
                            "behaviorally monitor children, and targeted advertising to children is "
                            "completely prohibited. If your platform is not designed for children but "
                            "they could still use it, it is safer to enable this option."
                        ),
                        warning_condition={
                            "value": True,
                            "message": (
                                "Collecting children's data triggers strict compliance requirements "
                                "under DPDP Act 2023 including verifiable parental consent mechanisms. "
                                "Ensure you have processes in place to verify parental identity and "
                                "consent before going live."
                            ),
                        },
                        india_note=(
                            "DPDP Act 2023 requires verifiable parental consent before "
                            "processing children's data. Tracking, behavioral monitoring, "
                            "and targeted advertising directed at children is prohibited."
                        ),
                    ),
                ],
            },
            # Step 5: DPDP Act Advanced Compliance
            {
                "step_number": 5,
                "title": "DPDP Act Advanced Compliance",
                "description": "Additional compliance settings required under the DPDP Act 2023.",
                "clauses": [
                    _clause(
                        "pp_cross_border_transfers",
                        "Cross-Border Data Transfers",
                        "toggle",
                        "Whether data is transferred outside India",
                        learn_more=(
                            "Enable this if you use any cloud services, SaaS tools, or third-party "
                            "processors that store or process data outside India. This includes "
                            "services like AWS (US regions), Google Workspace, Stripe, Mailchimp, "
                            "etc. Under the DPDP Act 2023, cross-border transfers are allowed "
                            "to all countries EXCEPT those specifically restricted by the Central "
                            "Government via notification. Your privacy policy must disclose these "
                            "transfers and name the destination countries."
                        ),
                        india_note=(
                            "DPDP Act 2023, Section 16: Transfer of personal data outside "
                            "India is permitted unless the Central Government restricts "
                            "transfer to a specific country. Unlike GDPR, no adequacy "
                            "assessment is required, but you must disclose the transfer."
                        ),
                    ),
                    _clause(
                        "pp_transfer_countries",
                        "Transfer Destination Countries",
                        "multi_select",
                        "Countries where data may be transferred",
                        options=[
                            "United States",
                            "European Union",
                            "Singapore",
                            "United Kingdom",
                            "Australia",
                            "Japan",
                        ],
                        learn_more=(
                            "Select all countries where your data may be stored or processed. "
                            "Check your cloud hosting regions, third-party tool data centers, and "
                            "any offshore team locations. Under the DPDP Act, the Central Government "
                            "may restrict transfers to specific countries at any time, so keeping "
                            "this list accurate helps you respond quickly to regulatory changes."
                        ),
                    ),
                    _clause(
                        "pp_breach_notification",
                        "Data Breach Notification Process",
                        "dropdown",
                        "How data breach notifications are handled",
                        options=[
                            "Notify Data Protection Board + affected users within 72 hours",
                            "Notify Data Protection Board + affected users as soon as practicable",
                            "Notify per DPDP Rules 2025 prescribed timelines",
                        ],
                        learn_more=(
                            "Under the DPDP Act 2023 and DPDP Rules 2025 (notified 14 Nov 2025), "
                            "Data Fiduciaries must report personal data breaches to the Data "
                            "Protection Board of India and to each affected Data Principal in the "
                            "prescribed manner. The detailed timelines for breach notification are "
                            "part of the phased rollout under the DPDP Rules (operational rules "
                            "expected within 18 months of notification). Industry best practice is "
                            "to notify within 72 hours (aligned with GDPR standards). Failure to "
                            "report a breach can attract penalties of up to Rs. 200 crore."
                        ),
                        india_note=(
                            "DPDP Act 2023, Section 8(6): In the event of a personal data "
                            "breach, the Data Fiduciary shall notify the Data Protection "
                            "Board and each affected Data Principal in the prescribed manner. "
                            "DPDP Rules 2025 provide the detailed procedural framework."
                        ),
                    ),
                    _clause(
                        "pp_significant_data_fiduciary",
                        "Significant Data Fiduciary",
                        "toggle",
                        "Whether your company may be classified as a Significant Data Fiduciary",
                        learn_more=(
                            "The Central Government may designate certain Data Fiduciaries as "
                            "'Significant Data Fiduciaries' based on volume/sensitivity of data "
                            "processed, risk to data principals, impact on sovereignty/public order, "
                            "etc. Significant Data Fiduciaries must: (1) appoint a Data Protection "
                            "Officer (DPO) based in India, (2) appoint an independent data auditor, "
                            "(3) conduct Data Protection Impact Assessments (DPIA), and (4) perform "
                            "periodic audits. Most early-stage startups are NOT Significant Data "
                            "Fiduciaries, but large platforms handling millions of users' data may be. "
                            "The DPDP Rules 2025 (notified Nov 2025) provide the detailed framework "
                            "for SDF obligations, with operational rules expected within 18 months."
                        ),
                        india_note=(
                            "DPDP Act 2023, Section 10: The Central Government may notify "
                            "any Data Fiduciary as a Significant Data Fiduciary. Additional "
                            "obligations include appointing a DPO in India, conducting DPIAs, "
                            "and periodic data audits by independent auditors. DPDP Rules 2025 "
                            "provide the implementation framework."
                        ),
                    ),
                ],
            },
        ],
    }


def render_privacy_policy(tpl: dict, config: dict, parties: dict) -> str:
    """Render Privacy Policy HTML."""
    company = config.get("pp_company_name", "[Company Name]")
    website = config.get("pp_website_url", "[Website URL]")
    email = config.get("pp_contact_email", "[Contact Email]")
    biz_type = config.get("pp_business_type", "General Services")

    data_collected = config.get("pp_personal_data_collected", [])
    collection_methods = config.get("pp_collection_methods", [])
    purposes = config.get("pp_purpose_of_collection", [])
    storage = config.get("pp_data_storage_location", "India only")
    retention = config.get("pp_data_retention", "As required by law")
    third_parties = config.get("pp_third_party_sharing", [])
    cookies = config.get("pp_cookies_used", False)
    user_rights = config.get("pp_user_rights", [])
    grievance_officer = config.get("pp_grievance_officer", "[Grievance Officer]")
    consent = config.get("pp_consent_mechanism", "Opt-in checkbox")
    children = config.get("pp_children_data", False)
    cross_border = config.get("pp_cross_border_transfers", False)
    transfer_countries = config.get("pp_transfer_countries", [])
    breach_notification = config.get(
        "pp_breach_notification",
        "Notify Data Protection Board + affected users as soon as practicable",
    )
    is_sdf = config.get("pp_significant_data_fiduciary", False)

    def _list_html(items: Any) -> str:
        if isinstance(items, list) and items:
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
        return f"<p>{items}</p>" if items else "<p>N/A</p>"

    sections: List[str] = []
    cn = 0

    # Section 1 — Introduction
    cn += 1
    sections.append(
        f'<h2>{cn}. Introduction</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Privacy Policy explains how <strong>{company}</strong> '
        f'("we", "us", "our"), operating {website}, collects, uses, stores, and '
        f'protects your personal data in accordance with the Digital Personal Data '
        f'Protection Act, 2023 ("DPDP Act"), the Digital Personal Data Protection '
        f'Rules, 2025 ("DPDP Rules", notified 14 November 2025), and the '
        f'Information Technology Act, 2000.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'For the purposes of the DPDP Act, we are the "Data Fiduciary" and you '
        f'are the "Data Principal".</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Business type: {biz_type}.</p>'
    )

    # Section 2 — Data We Collect
    cn += 1
    sections.append(
        f'<h2>{cn}. Personal Data We Collect</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'We collect the following categories of personal data:</p>'
        f'{_list_html(data_collected)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'We collect data through the following methods:</p>'
        f'{_list_html(collection_methods)}'
    )

    # Section 3 — Purpose
    cn += 1
    sections.append(
        f'<h2>{cn}. Purpose of Data Collection</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'We process your personal data for the following purposes:</p>'
        f'{_list_html(purposes)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'We will not process your personal data for any purpose beyond what is '
        f'specified above without obtaining fresh consent.</p>'
    )

    # Section 4 — Consent
    cn += 1
    sections.append(
        f'<h2>{cn}. Consent</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'We obtain your consent through: <strong>{consent}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Your consent is free, specific, informed, and unambiguous as required '
        f'under the DPDP Act 2023. You may withdraw your consent at any time by '
        f'contacting us at {email}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Withdrawal of consent shall not affect the lawfulness of processing '
        f'carried out before such withdrawal.</p>'
    )

    # Section 5 — Data Storage & Retention
    cn += 1
    sections.append(
        f'<h2>{cn}. Data Storage & Retention</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Data storage location: <strong>{storage}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Data retention period: <strong>{retention}</strong>. We will erase '
        f'personal data when it is no longer necessary for the stated purpose or '
        f'when you withdraw consent, unless retention is required by law.</p>'
    )

    # Section 6 — Sharing
    cn += 1
    sections.append(
        f'<h2>{cn}. Data Sharing with Third Parties</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'We may share your data with the following categories of third parties:</p>'
        f'{_list_html(third_parties)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'All third-party processors are bound by contractual obligations to '
        f'maintain confidentiality and process data only for the specified purposes.</p>'
    )

    # Section 7 — Cookies
    if cookies:
        cn += 1
        sections.append(
            f'<h2>{cn}. Cookies & Tracking Technologies</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'We use cookies and similar tracking technologies to enhance your '
            f'experience, analyze usage patterns, and deliver personalized content.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'You can manage cookie preferences through your browser settings. '
            f'Disabling cookies may affect the functionality of certain features.</p>'
        )

    # Section 8 — Your Rights
    cn += 1
    sections.append(
        f'<h2>{cn}. Your Rights as Data Principal</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Under the DPDP Act 2023, you have the following rights:</p>'
        f'{_list_html(user_rights)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'To exercise any of your rights, please contact us at {email}. '
        f'We will respond to your request within the time prescribed under the '
        f'DPDP Act.</p>'
    )

    # Section 9 — Legitimate Uses Without Consent
    cn += 1
    sections.append(
        f'<h2>{cn}. Processing Without Consent (Legitimate Uses)</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Under Section 7 of the DPDP Act 2023, we may process your personal data '
        f'without explicit consent for certain legitimate uses, including:</p>'
        f'<ul>'
        f'<li>Where you have voluntarily provided data and have not indicated that '
        f'you do not consent to its use;</li>'
        f'<li>For compliance with any law, court order, or government directive;</li>'
        f'<li>For responding to a medical emergency involving a threat to your life '
        f'or health;</li>'
        f'<li>For employment-related purposes (existing employees only);</li>'
        f'<li>For purposes related to public interest such as mergers, insolvency, '
        f'or fraud prevention as specified by the Central Government.</li>'
        f'</ul>'
    )

    # Section 10 — Cross-Border Data Transfers
    if cross_border:
        cn += 1
        countries_text = ", ".join(transfer_countries) if transfer_countries else "various jurisdictions"
        sections.append(
            f'<h2>{cn}. Cross-Border Data Transfers</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Your personal data may be transferred to and processed in the following '
            f'countries/regions: <strong>{countries_text}</strong>.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Under Section 16 of the DPDP Act 2023, transfer of personal data outside '
            f'India is permitted to all countries except those specifically restricted '
            f'by the Central Government through notification. As of the date of this '
            f'policy, no such restriction applies to the countries listed above.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'We ensure that adequate contractual safeguards are in place with all '
            f'international data processors to protect your personal data to a standard '
            f'no less than what is required under Indian law.</p>'
        )

    # Section 11 — Data Breach Notification
    cn += 1
    sections.append(
        f'<h2>{cn}. Data Breach Notification</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'In the event of a personal data breach, we will notify the Data Protection '
        f'Board of India and each affected Data Principal in the prescribed manner, '
        f'in accordance with Section 8(6) of the DPDP Act 2023 and the DPDP Rules 2025.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Our breach notification process: <strong>{breach_notification}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The notification will include: (a) the nature of the breach, (b) the '
        f'categories of personal data affected, (c) the measures taken or proposed '
        f'to address the breach, and (d) the contact details of our Grievance Officer '
        f'for further information.</p>'
    )

    # Section 12 — Children's data
    if children:
        cn += 1
        sections.append(
            f'<h2>{cn}. Children\'s Data</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'We may process personal data of children (persons under 18 years of '
            f'age) only after obtaining verifiable consent from a parent or lawful '
            f'guardian, as required under Section 9 of the DPDP Act 2023.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'We do not engage in tracking, behavioral monitoring, or targeted '
            f'advertising directed at children, as prohibited under the DPDP Act 2023.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'If we become aware that we have collected personal data from a child '
            f'without verifiable parental consent, we will take steps to delete such '
            f'data promptly.</p>'
        )

    # Section 13 — Significant Data Fiduciary (if applicable)
    if is_sdf:
        cn += 1
        sections.append(
            f'<h2>{cn}. Significant Data Fiduciary Obligations</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'As a Significant Data Fiduciary under Section 10 of the DPDP Act 2023, '
            f'we have implemented the following additional measures:</p>'
            f'<ul>'
            f'<li>Appointed a <strong>Data Protection Officer (DPO)</strong> based in '
            f'India who serves as the point of contact for data protection matters;</li>'
            f'<li>Appointed an <strong>independent data auditor</strong> to conduct '
            f'periodic compliance audits;</li>'
            f'<li>Conduct <strong>Data Protection Impact Assessments (DPIA)</strong> '
            f'before undertaking any processing that involves significant risk to data '
            f'principals;</li>'
            f'<li>Undergo <strong>periodic data audits</strong> as prescribed by the '
            f'Central Government.</li>'
            f'</ul>'
        )

    # Section 14 — Your Duties as Data Principal
    cn += 1
    sections.append(
        f'<h2>{cn}. Your Duties as Data Principal</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Under Section 15 of the DPDP Act 2023, as a Data Principal you have '
        f'certain duties, including:</p>'
        f'<ul>'
        f'<li>To comply with all applicable laws while exercising your rights;</li>'
        f'<li>Not to register a false or frivolous complaint with the Data Protection '
        f'Board;</li>'
        f'<li>Not to furnish any false particulars, suppress material information, or '
        f'impersonate another person when providing personal data;</li>'
        f'<li>To provide only authentic and verifiable information when exercising '
        f'your right to correction or erasure.</li>'
        f'</ul>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Breach of these duties may attract a penalty of up to Rs. 10,000 as '
        f'prescribed under the DPDP Act 2023.</p>'
    )

    # Section 15 — Grievance Officer
    cn += 1
    sections.append(
        f'<h2>{cn}. Grievance Officer</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'In accordance with the DPDP Act 2023, we have designated the following '
        f'person as our Grievance Officer:</p>'
        f'<p class="clause"><strong>{grievance_officer}</strong><br>'
        f'Email: {email}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'You may contact the Grievance Officer for any concerns related to the '
        f'processing of your personal data. We will acknowledge your grievance '
        f'within 48 hours and resolve it within the prescribed time limit.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'If you are not satisfied with our response, you may file a complaint '
        f'with the Data Protection Board of India established under the DPDP Act 2023.</p>'
    )

    # Section 16 — Governing Law & Jurisdiction
    cn += 1
    sections.append(
        f'<h2>{cn}. Governing Law & Dispute Resolution</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Privacy Policy shall be governed by and construed in accordance with '
        f'the laws of India, including the Digital Personal Data Protection Act, 2023, '
        f'the Digital Personal Data Protection Rules, 2025, the Information Technology '
        f'Act, 2000, and rules framed thereunder.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Any disputes arising under this policy shall be subject to the exclusive '
        f'jurisdiction of the Data Protection Board of India for matters under the '
        f'DPDP Act, and the courts of competent jurisdiction in India for all other '
        f'matters.</p>'
    )

    # Section 17 — Updates
    cn += 1
    sections.append(
        f'<h2>{cn}. Changes to This Policy</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'We may update this Privacy Policy from time to time. Any material changes '
        f'will be notified to you via email or a prominent notice on our website.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Continued use of our services after changes constitutes acceptance of the '
        f'updated policy.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This policy was last updated on: {config.get("effective_date", "[Date]")}.</p>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Privacy Policy \u2014 {company}", body
    )


# ======================================================================
# TEMPLATE 11: TERMS OF SERVICE
# ======================================================================

def terms_of_service_template() -> dict:
    """Template 11 — Terms of Service."""
    return {
        "name": "Terms of Service",
        "description": (
            "Terms and conditions governing the use of your website, app, or platform. "
            "Covers user obligations, intellectual property, limitations of liability, "
            "and dispute resolution."
        ),
        "category": "Compliance",
        "steps": [
            # Step 1: Platform Details
            {
                "step_number": 1,
                "title": "Platform Details",
                "description": "Basic information about your company and platform.",
                "clauses": [
                    _clause(
                        "tos_company_name",
                        "Company Name",
                        "text",
                        "Legal name of the company",
                        learn_more=(
                            "Use your exact legal registered company name as it appears on your "
                            "Certificate of Incorporation. This name will appear throughout the Terms "
                            "of Service and is the entity that users enter into a legal relationship "
                            "with. If you operate through a subsidiary or parent company, use the "
                            "entity that actually operates the platform."
                        ),
                    ),
                    _clause(
                        "tos_platform_name",
                        "Platform Name",
                        "text",
                        "Name of the website/app/platform",
                        learn_more=(
                            "This is the consumer-facing name of your product or service, which may "
                            "differ from your legal company name. For example, your company might be "
                            "'XYZ Technologies Pvt Ltd' but your platform is called 'QuickPay'. The "
                            "terms of service will reference this name so users know exactly which "
                            "service is covered."
                        ),
                    ),
                    _clause(
                        "tos_platform_type",
                        "Platform Type",
                        "dropdown",
                        "Type of platform",
                        options=[
                            "Website",
                            "Mobile App",
                            "SaaS Platform",
                            "Marketplace",
                            "API Service",
                        ],
                        learn_more=(
                            "The platform type affects which legal provisions are included and how "
                            "terms are structured. A Marketplace has additional obligations under the "
                            "Consumer Protection (E-Commerce) Rules 2020, including seller "
                            "verification and grievance handling. SaaS platforms need service level "
                            "commitments. API services need usage limits and rate-limiting terms. "
                            "Choose the type that best describes how users interact with your product."
                        ),
                    ),
                    _clause(
                        "tos_effective_date",
                        "Effective Date",
                        "date",
                        "Date from which these terms are effective",
                        learn_more=(
                            "This is the date from which your Terms of Service become legally "
                            "binding on users. Set this to the date you plan to publish the terms on "
                            "your platform. If you are updating existing terms, set a future date and "
                            "give users adequate notice (usually 30 days) before the new terms take "
                            "effect. Always display the effective date prominently on your ToS page."
                        ),
                    ),
                ],
            },
            # Step 2: User Terms
            {
                "step_number": 2,
                "title": "User Terms",
                "description": "Eligibility, account requirements, and user obligations.",
                "clauses": [
                    _clause(
                        "tos_eligibility",
                        "Eligibility",
                        "dropdown",
                        "Who can use the platform",
                        options=[
                            "18+ years only",
                            "13+ years (with parental consent for minors)",
                            "Business users only",
                            "No age restriction",
                        ],
                        learn_more=(
                            "This sets who is legally allowed to use your platform. Under the Indian "
                            "Contract Act 1872, a person must be 18 or older to enter a contract, so "
                            "'18+ years only' is the safest default. If you choose to allow minors "
                            "(13+), you must implement verifiable parental consent under the DPDP Act "
                            "and your terms may not be enforceable against them. 'Business users only' "
                            "is suitable for B2B SaaS products."
                        ),
                        warning_condition={
                            "value": "No age restriction",
                            "message": (
                                "Having no age restriction means minors can use your platform, "
                                "which triggers DPDP Act requirements for verifiable parental "
                                "consent and prohibits tracking or targeted advertising to children. "
                                "Your terms may also be unenforceable against minors under the "
                                "Indian Contract Act 1872."
                            ),
                        },
                        india_note=(
                            "Under Indian Contract Act 1872, persons below 18 cannot enter "
                            "contracts. Under DPDP Act, processing children's data requires "
                            "verifiable parental consent."
                        ),
                    ),
                    _clause(
                        "tos_account_requirements",
                        "Account Requirements",
                        "multi_select",
                        "What's needed to create an account",
                        options=[
                            "Email verification",
                            "Phone verification",
                            "KYC/identity verification",
                            "Business registration proof",
                        ],
                        learn_more=(
                            "Select the verification steps users must complete to create an account. "
                            "Email and phone verification are basic fraud prevention measures. KYC "
                            "(Know Your Customer) is mandatory for fintech, lending, and certain "
                            "regulated services under RBI guidelines. Business registration proof is "
                            "relevant for B2B platforms. More verification steps reduce fraud but "
                            "increase signup friction."
                        ),
                    ),
                    _clause(
                        "tos_prohibited_activities",
                        "Prohibited Activities",
                        "multi_select",
                        "Activities prohibited on the platform",
                        options=[
                            "Illegal activities",
                            "Harassment or abuse",
                            "Spam or unsolicited marketing",
                            "Intellectual property infringement",
                            "Reverse engineering",
                            "Data scraping",
                            "Impersonation",
                            "Distribution of malware",
                        ],
                        learn_more=(
                            "This defines what users are not allowed to do on your platform. Having "
                            "a clear list of prohibited activities gives you legal grounds to suspend "
                            "or terminate accounts and limits your liability for user misconduct. "
                            "Select all items that apply. Under the IT Act 2000 (Sections 79 and "
                            "79A), intermediaries must exercise due diligence, including having clear "
                            "usage policies. A comprehensive prohibited activities list strengthens "
                            "your 'safe harbour' protection as an intermediary."
                        ),
                    ),
                    _clause(
                        "tos_user_content",
                        "User Content Ownership",
                        "dropdown",
                        "Who owns content users create/upload",
                        options=[
                            "Users cannot post content",
                            "Users retain ownership, grant license",
                            "All user content becomes company property",
                        ],
                        learn_more=(
                            "This determines who owns content that users create or upload on your "
                            "platform (posts, photos, reviews, etc.). 'Users retain ownership, grant "
                            "license' is the industry standard \u2014 users keep their IP but give you "
                            "permission to display and use the content on your platform. 'All content "
                            "becomes company property' is aggressive and may deter users. If your "
                            "platform does not have user-generated content, select the first option."
                        ),
                        pros=["Users retain, grant license: User-friendly, industry standard, attracts creators",
                              "All content becomes company property: Maximum company control over content",
                              "Users cannot post content: Simplest, no content moderation needed"],
                        cons=["Users retain, grant license: Users can request content removal",
                              "All content becomes company property: May scare away users, harder to enforce",
                              "Users cannot post content: Limits platform engagement and community building"],
                        warning_condition={
                            "value": "All user content becomes company property",
                            "message": (
                                "Claiming ownership of all user content is unusual and may deter "
                                "users from joining your platform. Under Indian Copyright Act 1957, "
                                "the original creator typically holds copyright. This clause may be "
                                "challenged if it is considered unfair under the Consumer Protection "
                                "Act 2019."
                            ),
                        },
                        common_choice_label="Standard: Users retain, grant license",
                    ),
                ],
            },
            # Step 3: Legal Protections
            {
                "step_number": 3,
                "title": "Legal Protections",
                "description": "Liability limitations, disclaimers, and IP ownership.",
                "clauses": [
                    _clause(
                        "tos_liability_limitation",
                        "Liability Limitation",
                        "dropdown",
                        "Cap on company's liability",
                        options=[
                            "Liability limited to fees paid in last 12 months",
                            "Liability limited to \u20b910,000",
                            "No limitation (not recommended)",
                            "Maximum of fees paid or \u20b91,00,000",
                        ],
                        learn_more=(
                            "Limitation of liability clauses cap the maximum damages you "
                            "could owe users. This protects the company from "
                            "disproportionate claims. Indian courts generally uphold "
                            "reasonable liability caps in B2B agreements. Tying the cap to "
                            "fees paid in the last 12 months is the most balanced approach "
                            "\u2014 it is proportional and widely accepted."
                        ),
                        pros=["Limited to fees paid: Proportional and widely accepted",
                              "Fixed cap of \u20b910,000: Simple and predictable exposure",
                              "Maximum of fees or \u20b91,00,000: Provides a reasonable floor"],
                        cons=["Limited to fees paid: Low cap for free-tier users means effectively zero",
                              "Fixed cap: May seem unreasonably low for enterprise users",
                              "No limitation: Exposes company to unlimited financial risk"],
                        warning_condition={
                            "value": "No limitation (not recommended)",
                            "message": (
                                "Having no liability cap exposes your company to potentially "
                                "unlimited damages claims. Even a single lawsuit could threaten your "
                                "company's survival. This is strongly discouraged for any startup."
                            ),
                        },
                        india_note=(
                            "Under Indian Consumer Protection Act 2019, liability "
                            "limitation clauses may be overridden for consumer disputes. "
                            "However, they remain valid for B2B relationships."
                        ),
                        common_choice_label="Standard: Limited to fees paid in 12 months",
                    ),
                    _clause(
                        "tos_warranty_disclaimer",
                        "Warranty Disclaimer",
                        "toggle",
                        "Whether to include 'as-is' warranty disclaimer",
                        learn_more=(
                            "An 'as-is' warranty disclaimer means you do not guarantee the platform "
                            "will be error-free, always available, or fit for any particular purpose. "
                            "This is standard practice and protects you from claims if the platform "
                            "has bugs or downtime. Without this disclaimer, users could potentially "
                            "claim damages for any service interruption. Note that warranty "
                            "disclaimers may be limited by the Consumer Protection Act 2019 for "
                            "consumer-facing products."
                        ),
                        common_choice_label="Recommended: Yes",
                    ),
                    _clause(
                        "tos_indemnification",
                        "User Indemnification",
                        "toggle",
                        "Whether users indemnify the company against third-party claims",
                        learn_more=(
                            "Indemnification means users agree to cover your legal costs and damages "
                            "if a third party sues you because of something the user did on your "
                            "platform. For example, if a user uploads copyrighted content and the "
                            "copyright holder sues you, the user would be responsible for your legal "
                            "expenses. This is a standard protection clause included in most Terms of "
                            "Service worldwide."
                        ),
                        common_choice_label="Standard: Yes",
                    ),
                    _clause(
                        "tos_ip_ownership",
                        "IP Ownership",
                        "dropdown",
                        "Who owns the platform's intellectual property",
                        options=[
                            "All platform IP belongs to company",
                            "Open source components acknowledged",
                            "Mixed ownership",
                        ],
                        learn_more=(
                            "This clause clarifies that your platform's code, design, branding, "
                            "and other intellectual property belong to the company. This prevents "
                            "users from claiming ownership over any part of the platform. If your "
                            "product uses open-source software, select 'Open source components "
                            "acknowledged' to comply with open-source license requirements. Mixed "
                            "ownership is rare and typically used for collaborative platforms."
                        ),
                        common_choice_label="Standard: All IP belongs to company",
                    ),
                ],
            },
            # Step 4: Dispute Resolution & Miscellaneous
            {
                "step_number": 4,
                "title": "Dispute Resolution & Miscellaneous",
                "description": "Governing law, dispute resolution, modification, and termination.",
                "clauses": [
                    _clause(
                        "tos_governing_law",
                        "Governing Law",
                        "dropdown",
                        "Which state's laws govern",
                        options=[
                            "Maharashtra",
                            "Karnataka",
                            "Delhi",
                            "Tamil Nadu",
                            "Telangana",
                        ],
                        learn_more=(
                            "Governing law determines which state's courts have jurisdiction and "
                            "which state-specific laws apply in case of a dispute. Typically, you "
                            "should choose the state where your company is registered or has its "
                            "primary office. This gives you the home-court advantage of litigating "
                            "disputes in a familiar jurisdiction. Note that for consumer disputes, "
                            "consumers can file complaints wherever they reside regardless of this "
                            "clause."
                        ),
                        india_note=(
                            "While parties can choose governing law, consumer disputes under "
                            "Consumer Protection Act 2019 can be filed where the consumer "
                            "resides. State-specific stamp duty and registration laws may also "
                            "apply."
                        ),
                    ),
                    _clause(
                        "tos_dispute_resolution",
                        "Dispute Resolution",
                        "dropdown",
                        "How disputes are resolved",
                        options=[
                            "Courts only",
                            "Arbitration",
                            "Mediation then Arbitration",
                            "Consumer forum + Arbitration for B2B",
                        ],
                        learn_more=(
                            "This determines how disagreements between you and your users are "
                            "resolved. Arbitration is private, faster, and usually cheaper than "
                            "court, but the award is binding. 'Mediation then Arbitration' adds a "
                            "negotiation step before formal arbitration, saving costs if parties can "
                            "agree. For consumer-facing platforms, Indian law gives consumers the "
                            "right to approach consumer forums regardless of any arbitration clause, "
                            "so 'Consumer forum + Arbitration for B2B' is the most legally sound "
                            "option."
                        ),
                        pros=["Arbitration: Faster, private, binding decisions",
                              "Mediation then Arbitration: Cost-saving first step, preserves relationship",
                              "Consumer forum + Arbitration for B2B: Most legally compliant for mixed user base"],
                        cons=["Courts only: Slow and expensive, public proceedings",
                              "Arbitration: Arbitrator fees can be high, limited appeal options",
                              "Mediation then Arbitration: Adds time if mediation fails"],
                        india_note=(
                            "For consumer-facing platforms, users cannot be denied access "
                            "to consumer forums/courts regardless of arbitration clause. "
                            "Consumer Protection Act 2019 overrides arbitration for "
                            "consumer disputes."
                        ),
                        common_choice_label="Standard: Arbitration for B2B, consumer forum preserved",
                    ),
                    _clause(
                        "tos_modification_notice",
                        "Modification Notice",
                        "dropdown",
                        "How users are notified of changes to terms",
                        options=[
                            "Email notification 30 days before",
                            "Posted on website 15 days before",
                            "Immediate effect with notification",
                            "Requires active consent",
                        ],
                        learn_more=(
                            "This defines how you must inform users when you change the Terms of "
                            "Service. Giving users adequate notice (ideally 30 days) is both good "
                            "practice and may be legally required. 'Email notification 30 days "
                            "before' is the most user-friendly and defensible option. 'Immediate "
                            "effect with notification' is convenient for the company but may be "
                            "challenged if changes are material. 'Requires active consent' is the "
                            "most protective for users but adds operational complexity."
                        ),
                        warning_condition={
                            "value": "Immediate effect with notification",
                            "message": (
                                "Making changes effective immediately without a notice period may "
                                "be considered unfair, especially for paid services. Courts may view "
                                "this as a unilateral contract modification without reasonable "
                                "opportunity for users to review and decide."
                            ),
                        },
                        common_choice_label="Best practice: Email 30 days before",
                    ),
                    _clause(
                        "tos_termination",
                        "Termination",
                        "dropdown",
                        "How the agreement can be terminated",
                        options=[
                            "Either party with 30 days notice",
                            "Company can terminate immediately for violation",
                            "Both",
                        ],
                        learn_more=(
                            "Termination defines how either party can end the relationship. 'Both' "
                            "is the most balanced option: users can leave with notice, and you can "
                            "terminate accounts immediately if users violate the terms. This protects "
                            "your platform from abusive users while being fair to legitimate ones. "
                            "Key provisions like IP ownership, confidentiality, and indemnification "
                            "typically survive termination."
                        ),
                    ),
                ],
            },
        ],
    }


def render_terms_of_service(tpl: dict, config: dict, parties: dict) -> str:
    """Render Terms of Service HTML."""
    company = config.get("tos_company_name", "[Company Name]")
    platform = config.get("tos_platform_name", "[Platform Name]")
    platform_type = config.get("tos_platform_type", "Website")
    effective_date = config.get("tos_effective_date", "")

    eligibility = config.get("tos_eligibility", "18+ years only")
    account_reqs = config.get("tos_account_requirements", [])
    prohibited = config.get("tos_prohibited_activities", [])
    user_content = config.get("tos_user_content", "Users retain ownership, grant license")

    liability = config.get("tos_liability_limitation", "Liability limited to fees paid in last 12 months")
    warranty = config.get("tos_warranty_disclaimer", True)
    indemnification = config.get("tos_indemnification", True)
    ip_ownership = config.get("tos_ip_ownership", "All platform IP belongs to company")

    governing = config.get("tos_governing_law", "Maharashtra")
    dispute = config.get("tos_dispute_resolution", "Arbitration")
    modification = config.get("tos_modification_notice", "Email notification 30 days before")
    termination = config.get("tos_termination", "Both")

    def _list_html(items: Any) -> str:
        if isinstance(items, list) and items:
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
        return f"<p>{items}</p>" if items else "<p>N/A</p>"

    sections: List[str] = []
    cn = 0

    # Section 1 — Acceptance
    cn += 1
    sections.append(
        f'<h2>{cn}. Acceptance of Terms</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'These Terms of Service ("Terms") govern your use of '
        f'<strong>{platform}</strong> ({platform_type}), operated by '
        f'<strong>{company}</strong> ("Company", "we", "us").</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'By accessing or using the platform, you agree to be bound by these Terms. '
        f'If you do not agree, you must not use the platform.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'These Terms are effective as of '
        f'{effective_date or "________________________"}.</p>'
    )

    # Section 2 — Eligibility
    cn += 1
    sections.append(
        f'<h2>{cn}. Eligibility</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Eligibility requirement: <strong>{eligibility}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'By using the platform, you represent and warrant that you meet the '
        f'eligibility requirements stated above.</p>'
    )

    # Section 3 — Account
    cn += 1
    sections.append(
        f'<h2>{cn}. Account Registration</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'To access certain features, you may need to create an account. '
        f'The following may be required:</p>'
        f'{_list_html(account_reqs)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'You are responsible for maintaining the confidentiality of your account '
        f'credentials and for all activities that occur under your account.</p>'
    )

    # Section 4 — Prohibited activities
    cn += 1
    sections.append(
        f'<h2>{cn}. Prohibited Activities</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'You agree not to engage in any of the following activities while using '
        f'the platform:</p>'
        f'{_list_html(prohibited)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Violation of these restrictions may result in immediate termination of '
        f'your account and may subject you to legal liability.</p>'
    )

    # Section 5 — User content
    cn += 1
    sections.append(
        f'<h2>{cn}. User Content</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'User content policy: <strong>{user_content}</strong>.</p>'
    )
    if user_content == "Users retain ownership, grant license":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'By posting content on the platform, you grant the Company a worldwide, '
            f'non-exclusive, royalty-free, sublicensable license to use, reproduce, '
            f'modify, distribute, and display such content solely in connection with '
            f'operating and providing the platform.</p>'
        )

    # Section 6 — IP
    cn += 1
    sections.append(
        f'<h2>{cn}. Intellectual Property</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'IP ownership: <strong>{ip_ownership}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Company name, logo, and all related trademarks, trade names, and '
        f'service marks are the property of the Company. Nothing in these Terms '
        f'grants you any right to use them without prior written consent.</p>'
    )

    # Section 7 — Disclaimer & Liability
    cn += 1
    sections.append(
        f'<h2>{cn}. Disclaimer & Limitation of Liability</h2>'
    )
    if warranty:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'THE PLATFORM IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES '
            f'OF ANY KIND, WHETHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO '
            f'IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, '
            f'AND NON-INFRINGEMENT.</p>'
        )
    sections.append(
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Liability limitation: <strong>{liability}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'IN NO EVENT SHALL THE COMPANY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, '
        f'SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES.</p>'
    )

    # Section 8 — Indemnification
    if indemnification:
        cn += 1
        sections.append(
            f'<h2>{cn}. Indemnification</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'You agree to indemnify, defend, and hold harmless the Company, its '
            f'directors, officers, employees, and agents from and against any and all '
            f'claims, damages, losses, liabilities, costs, and expenses (including '
            f'reasonable legal fees) arising out of or relating to your use of the '
            f'platform or violation of these Terms.</p>'
        )

    # Section 9 — Governing law & Disputes
    cn += 1
    sections.append(
        f'<h2>{cn}. Governing Law & Dispute Resolution</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'These Terms shall be governed by and construed in accordance with the '
        f'laws of <strong>{governing}</strong>, India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Dispute resolution: <strong>{dispute}</strong>.</p>'
    )
    if "Consumer forum" in dispute:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Nothing in these Terms shall restrict the right of any consumer to '
            f'approach consumer forums/courts under the Consumer Protection Act, 2019.</p>'
        )

    # Section 10 — Modifications
    cn += 1
    sections.append(
        f'<h2>{cn}. Modifications to Terms</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'We reserve the right to modify these Terms at any time. '
        f'Notification method: <strong>{modification}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Your continued use of the platform after any changes constitutes '
        f'acceptance of the modified Terms.</p>'
    )

    # Section 11 — Termination
    cn += 1
    sections.append(
        f'<h2>{cn}. Termination</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Termination provision: <strong>{termination}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Upon termination, your right to use the platform will immediately cease. '
        f'Provisions relating to IP, confidentiality, indemnification, limitation '
        f'of liability, and dispute resolution shall survive termination.</p>'
    )

    # Section 12 — Contact
    cn += 1
    sections.append(
        f'<h2>{cn}. Contact Information</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'For any questions about these Terms, please contact '
        f'<strong>{company}</strong>.</p>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Terms of Service \u2014 {platform}", body, effective_date
    )


# ======================================================================
# TEMPLATE 12: OFFER LETTER
# ======================================================================

def offer_letter_template() -> dict:
    """Template 12 — Offer Letter."""
    return {
        "name": "Offer Letter",
        "description": (
            "Formal offer of employment letter to extend to candidates. Covers "
            "position, compensation, start date, and key terms before the detailed "
            "employment agreement."
        ),
        "category": "Team",
        "steps": [
            # Step 1: Position & Compensation
            {
                "step_number": 1,
                "title": "Position & Compensation",
                "description": "Job details and compensation for the candidate.",
                "clauses": [
                    _clause(
                        "ol_candidate_name",
                        "Candidate Name",
                        "text",
                        "Full name of the candidate",
                        learn_more=(
                            "Enter the candidate's full legal name as it appears on their "
                            "government-issued identity documents. This name will appear on the offer "
                            "letter and must match the name used for PF registration, Form 16, and "
                            "other employment records. Using a nickname or shortened name can create "
                            "compliance issues later."
                        ),
                    ),
                    _clause(
                        "ol_designation",
                        "Designation",
                        "text",
                        "Job title/designation",
                        learn_more=(
                            "The designation is the official job title that will appear on the "
                            "employee's records, experience letter, and LinkedIn profile. Be thoughtful "
                            "about titles \u2014 overly senior titles for early employees can create "
                            "hierarchy problems as the company grows. Common startup titles include "
                            "Software Engineer, Product Manager, Head of Growth, etc."
                        ),
                    ),
                    _clause(
                        "ol_department",
                        "Department",
                        "text",
                        "Department",
                        learn_more=(
                            "Enter the department or team the candidate will join (e.g., Engineering, "
                            "Product, Marketing, Operations, Finance). Even if your startup does not "
                            "have formal departments yet, assigning one helps with organizational "
                            "clarity and is required for payroll and HR records."
                        ),
                    ),
                    _clause(
                        "ol_reporting_to",
                        "Reporting To",
                        "text",
                        "Reporting manager name and title",
                        learn_more=(
                            "Specify the name and designation of the person this employee will "
                            "report to (e.g., 'Priya Sharma, CTO'). Clear reporting lines set "
                            "expectations from day one and prevent ambiguity. In early-stage startups, "
                            "most employees report directly to a founder."
                        ),
                    ),
                    _clause(
                        "ol_start_date",
                        "Start Date",
                        "date",
                        "Proposed date of joining",
                        learn_more=(
                            "This is the date the candidate is expected to begin working. Allow "
                            "enough time for the candidate to serve their notice period at their "
                            "current employer (typically 30-90 days in India). If the candidate does "
                            "not join by this date without prior communication, the offer may be "
                            "considered lapsed depending on your offer validity terms."
                        ),
                    ),
                    _clause(
                        "ol_ctc",
                        "Annual CTC",
                        "number",
                        "Annual CTC (Cost to Company) in INR",
                        learn_more=(
                            "CTC (Cost to Company) is the total annual cost your company bears "
                            "for this employee. It includes basic salary, HRA, special allowances, "
                            "employer PF contribution (12% of basic), gratuity provision (4.81% of "
                            "basic), and any insurance premiums. The employee's take-home salary will "
                            "be lower than CTC after deducting employee PF, professional tax, and "
                            "income tax (TDS). A detailed CTC breakup is typically shared separately."
                        ),
                        india_note=(
                            "CTC includes all employer costs: basic salary, HRA, "
                            "allowances, employer PF contribution, gratuity provision, "
                            "insurance, etc."
                        ),
                    ),
                    _clause(
                        "ol_location",
                        "Work Location",
                        "text",
                        "Work location",
                        learn_more=(
                            "Specify the primary work location (city and office address). If the "
                            "role is remote, state 'Remote' or 'Work from Home'. For hybrid roles, "
                            "mention the office location and the expected in-office frequency. The "
                            "work location affects professional tax applicability, which varies by "
                            "state (e.g., Maharashtra charges up to \u20b92,500/year, Karnataka up to "
                            "\u20b92,400/year)."
                        ),
                    ),
                    _clause(
                        "ol_employment_type",
                        "Employment Type",
                        "dropdown",
                        "Type of employment",
                        options=[
                            "Full-time permanent",
                            "Full-time contractual",
                            "Part-time",
                            "Intern converting to full-time",
                        ],
                        learn_more=(
                            "The employment type determines benefits, notice periods, and legal "
                            "obligations. Full-time permanent employees get PF, gratuity (after 5 "
                            "years), and full labor law protections. Full-time contractual employees "
                            "work for a fixed term and the contract ends on a specified date. "
                            "Part-time arrangements need clear working hour definitions. Intern "
                            "conversions should specify the internship end date and full-time start "
                            "date."
                        ),
                        pros=["Full-time permanent: Attracts top talent, full commitment",
                              "Full-time contractual: Flexibility to end without notice period complications",
                              "Intern converting: Trial period before full commitment"],
                        cons=["Full-time permanent: Harder to terminate, full statutory benefits required",
                              "Full-time contractual: May not attract serious candidates",
                              "Part-time: Limited commitment, may work for competitors"],
                    ),
                ],
            },
            # Step 2: Conditions & Acceptance
            {
                "step_number": 2,
                "title": "Conditions & Acceptance",
                "description": "Offer conditions and documents required from the candidate.",
                "clauses": [
                    _clause(
                        "ol_offer_validity",
                        "Offer Validity",
                        "dropdown",
                        "How long the offer remains valid",
                        options=["7 days", "14 days", "30 days"],
                        learn_more=(
                            "Offer validity is the deadline by which the candidate must accept or "
                            "decline the offer. 14 days is standard and gives the candidate enough "
                            "time to consider while keeping your hiring pipeline moving. 7 days "
                            "creates urgency but may pressure candidates. 30 days is generous but "
                            "could delay your hiring if the candidate declines late. After the "
                            "validity period, the offer automatically lapses."
                        ),
                        common_choice_label="Standard: 14 days",
                    ),
                    _clause(
                        "ol_probation",
                        "Probation Period",
                        "dropdown",
                        "Probation period",
                        options=["No probation", "3 months", "6 months"],
                        learn_more=(
                            "The probation period is a trial phase during which either party can "
                            "end the employment with a shorter notice period (typically 15 days "
                            "instead of 30-90 days). This gives the company a chance to evaluate "
                            "the employee's fit before confirming them. During probation, the "
                            "employee may have fewer benefits. 6 months is standard in India, "
                            "giving enough time for a fair evaluation."
                        ),
                        pros=["No probation: Attracts confident candidates, shows trust",
                              "3 months: Quick evaluation, shorter uncertainty for employee",
                              "6 months: Thorough evaluation, industry standard in India"],
                        cons=["No probation: Harder to let go of poor performers quickly",
                              "3 months: May not be enough time to fully evaluate",
                              "6 months: Longer uncertainty may deter some candidates"],
                        common_choice_label="Standard: 6 months",
                    ),
                    _clause(
                        "ol_background_check",
                        "Background Check",
                        "toggle",
                        "Whether the offer is contingent on background verification",
                        learn_more=(
                            "A background check verifies the candidate's educational qualifications, "
                            "previous employment history, criminal record, and identity. Making the "
                            "offer contingent on a clean background check protects your company from "
                            "fraud. If discrepancies are found after joining, the company can revoke "
                            "the offer or terminate employment. Most background checks in India are "
                            "done through third-party agencies and take 7-14 days."
                        ),
                        common_choice_label="Standard: Yes",
                    ),
                    _clause(
                        "ol_documents_required",
                        "Documents Required",
                        "multi_select",
                        "Documents candidate must submit",
                        options=[
                            "Identity proof (Aadhaar/Passport)",
                            "PAN card",
                            "Educational certificates",
                            "Previous employment proof",
                            "Bank account details",
                            "Medical fitness certificate",
                            "Relieving letter from previous employer",
                            "Photos",
                        ],
                        learn_more=(
                            "These are the documents the candidate must submit on or before their "
                            "joining date. PAN card and Aadhaar are mandatory for payroll setup \u2014 "
                            "PAN for TDS deduction and Aadhaar for EPFO registration. A relieving "
                            "letter from the previous employer confirms the candidate has been "
                            "formally released and is not dual-employed. Bank account details are "
                            "needed for salary credit. Select all documents relevant to the role."
                        ),
                        india_note=(
                            "Under Payment of Wages Act, employers must collect PAN for "
                            "TDS deduction. Aadhaar is required for PF registration "
                            "(EPFO mandates UAN-Aadhaar linkage)."
                        ),
                    ),
                ],
            },
        ],
    }


def render_offer_letter(tpl: dict, config: dict, parties: dict) -> str:
    """Render Offer Letter HTML."""
    candidate = config.get("ol_candidate_name", "[Candidate Name]")
    designation = config.get("ol_designation", "[Designation]")
    department = config.get("ol_department", "[Department]")
    reporting = config.get("ol_reporting_to", "[Reporting Manager]")
    start_date = config.get("ol_start_date", "")
    ctc = config.get("ol_ctc", 0)
    location = config.get("ol_location", "[Location]")
    emp_type = config.get("ol_employment_type", "Full-time permanent")

    validity = config.get("ol_offer_validity", "14 days")
    probation = config.get("ol_probation", "6 months")
    bg_check = config.get("ol_background_check", True)
    docs = config.get("ol_documents_required", [])

    company = parties.get("company_name", "[Company Name]")

    def _list_html(items: Any) -> str:
        if isinstance(items, list) and items:
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
        return f"<p>{items}</p>" if items else "<p>N/A</p>"

    sections: List[str] = []

    # Header / Address
    sections.append(
        f'<p class="clause"><strong>To:</strong> {candidate}</p>'
        f'<p class="clause"><strong>From:</strong> {company}</p>'
        f'<p class="clause"><strong>Subject:</strong> Offer of Employment \u2014 '
        f'{designation}</p>'
    )

    sections.append(
        f'<p class="clause">Dear <strong>{candidate}</strong>,</p>'
        f'<p class="clause">We are pleased to extend this offer of employment to you '
        f'for the position detailed below. We were impressed with your qualifications '
        f'and believe you will be a valuable addition to our team.</p>'
    )

    # Position details
    sections.append(
        f'<h2>1. Position Details</h2>'
        f'<p class="clause"><span class="clause-number">1.1</span> '
        f'<strong>Designation:</strong> {designation}</p>'
        f'<p class="clause"><span class="clause-number">1.2</span> '
        f'<strong>Department:</strong> {department}</p>'
        f'<p class="clause"><span class="clause-number">1.3</span> '
        f'<strong>Reporting To:</strong> {reporting}</p>'
        f'<p class="clause"><span class="clause-number">1.4</span> '
        f'<strong>Employment Type:</strong> {emp_type}</p>'
        f'<p class="clause"><span class="clause-number">1.5</span> '
        f'<strong>Work Location:</strong> {location}</p>'
        f'<p class="clause"><span class="clause-number">1.6</span> '
        f'<strong>Proposed Date of Joining:</strong> '
        f'{start_date or "________________________"}</p>'
    )

    # Compensation
    sections.append(
        f'<h2>2. Compensation</h2>'
        f'<p class="clause"><span class="clause-number">2.1</span> '
        f'Your annual Cost to Company (CTC) will be '
        f'<strong>INR {ctc:,}</strong> (Indian Rupees '
        f'{_number_to_words_inr(ctc)} only).</p>'
        f'<p class="clause"><span class="clause-number">2.2</span> '
        f'The CTC is inclusive of all allowances, employer contributions to '
        f'Provident Fund, gratuity provisions, and applicable insurance. '
        f'A detailed compensation breakup will be provided upon joining.</p>'
        f'<p class="clause"><span class="clause-number">2.3</span> '
        f'All payments are subject to applicable tax deductions at source (TDS) '
        f'as per the Income Tax Act, 1961.</p>'
    )

    # Terms
    sections.append(
        f'<h2>3. Terms & Conditions</h2>'
        f'<p class="clause"><span class="clause-number">3.1</span> '
        f'<strong>Probation Period:</strong> {probation}. During probation, either '
        f'party may terminate employment with 15 days written notice or salary in lieu.</p>'
    )
    if bg_check:
        sections.append(
            f'<p class="clause"><span class="clause-number">3.2</span> '
            f'This offer is contingent upon successful completion of background '
            f'verification. If any discrepancy is found during or after the '
            f'verification process, the Company reserves the right to revoke this '
            f'offer or terminate employment.</p>'
        )
    sections.append(
        f'<p class="clause"><span class="clause-number">3.3</span> '
        f'Upon joining, you will be required to sign a detailed Employment Agreement '
        f'covering confidentiality, intellectual property, non-compete, and other '
        f'standard terms.</p>'
    )

    # Documents required
    if docs:
        sections.append(
            f'<h2>4. Documents Required</h2>'
            f'<p class="clause"><span class="clause-number">4.1</span> '
            f'Please submit the following documents on or before your date of '
            f'joining:</p>'
            f'{_list_html(docs)}'
        )

    # Acceptance
    sections.append(
        f'<h2>5. Acceptance</h2>'
        f'<p class="clause"><span class="clause-number">5.1</span> '
        f'This offer is valid for <strong>{validity}</strong> from the date of '
        f'this letter. Please sign and return a copy of this letter to confirm '
        f'your acceptance.</p>'
        f'<p class="clause"><span class="clause-number">5.2</span> '
        f'If we do not receive your acceptance within the specified period, this '
        f'offer will stand automatically withdrawn.</p>'
    )

    # Closing
    sections.append(
        f'<p class="clause">We look forward to welcoming you to the team!</p>'
        f'<p class="clause">Warm regards,</p>'
    )

    # Signature
    sections.append(
        '<div class="signature-block">'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>For {company}</strong></p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    # Acceptance block
    sections.append(
        '<h2>Acceptance by Candidate</h2>'
        f'<p class="clause">I, <strong>{candidate}</strong>, accept this offer of '
        f'employment on the terms and conditions stated herein.</p>'
        '<div class="signature-block">'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{candidate}</strong></p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Offer Letter \u2014 {candidate}", body
    )


def _number_to_words_inr(n: int) -> str:
    """Convert a number to Indian English words (simplified for common ranges)."""
    if n == 0:
        return "zero"
    if n < 0:
        return "minus " + _number_to_words_inr(-n)

    parts: List[str] = []

    crore = n // 10000000
    n %= 10000000
    lakh = n // 100000
    n %= 100000
    thousand = n // 1000
    n %= 1000
    hundred = n // 100
    remainder = n % 100

    ones = [
        "", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
    ]
    tens = [
        "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety",
    ]

    def _two_digits(num: int) -> str:
        if num < 20:
            return ones[num]
        t, o = divmod(num, 10)
        return (tens[t] + (" " + ones[o] if o else "")).strip()

    def _three_digits(num: int) -> str:
        h, r = divmod(num, 100)
        parts_inner = []
        if h:
            parts_inner.append(ones[h] + " hundred")
        if r:
            parts_inner.append(_two_digits(r))
        return " and ".join(parts_inner)

    if crore:
        parts.append(_two_digits(crore) + " crore")
    if lakh:
        parts.append(_two_digits(lakh) + " lakh")
    if thousand:
        parts.append(_two_digits(thousand) + " thousand")
    if hundred:
        parts.append(ones[hundred] + " hundred")
    if remainder:
        parts.append(_two_digits(remainder))

    return " ".join(parts)


# ======================================================================
# TEMPLATE 13: IP ASSIGNMENT AGREEMENT
# ======================================================================

def ip_assignment_template() -> dict:
    """Template 13 — IP Assignment Agreement."""
    return {
        "name": "IP Assignment Agreement",
        "description": (
            "Transfers ownership of intellectual property (code, designs, inventions, "
            "content) from creators to the company. Critical for securing IP rights "
            "from founders, contractors, and consultants."
        ),
        "category": "Intellectual Property",
        "steps": [
            # Step 1: Parties & IP Description
            {
                "step_number": 1,
                "title": "Parties & IP Description",
                "description": "Who is assigning IP and what IP is being assigned.",
                "clauses": [
                    _clause(
                        "ipa_assignor_name",
                        "Assignor Name",
                        "text",
                        "Name of the person/entity assigning IP",
                        learn_more=(
                            "This is the person or entity transferring their intellectual property "
                            "rights to the company. For founders, this is critical before fundraising "
                            "\u2014 investors will verify that all IP has been properly assigned to the "
                            "company. Use the full legal name matching their government ID or business "
                            "registration."
                        ),
                    ),
                    _clause(
                        "ipa_assignor_type",
                        "Assignor Type",
                        "dropdown",
                        "Relationship of assignor to the company",
                        options=[
                            "Founder",
                            "Employee",
                            "Contractor",
                            "Consultant",
                            "Third party",
                        ],
                        learn_more=(
                            "The assignor's relationship to the company affects the legal basis for "
                            "the IP assignment. Founder IP assignments are essential before "
                            "fundraising \u2014 VCs will insist on this. Employee-created IP typically "
                            "belongs to the employer under Section 17 of the Copyright Act, but an "
                            "explicit assignment is still recommended. For contractors and consultants, "
                            "IP does NOT automatically belong to the company \u2014 an assignment "
                            "agreement is legally required to transfer ownership."
                        ),
                    ),
                    _clause(
                        "ipa_company_name",
                        "Company Name",
                        "text",
                        "Name of the company receiving IP",
                        learn_more=(
                            "This is the company that will own the IP after the assignment. Use the "
                            "exact registered company name. If you have multiple entities (e.g., an "
                            "Indian subsidiary and a holding company), ensure the IP is assigned to "
                            "the correct entity \u2014 typically the operating entity that actually "
                            "uses the IP for its business."
                        ),
                    ),
                    _clause(
                        "ipa_ip_description",
                        "IP Description",
                        "textarea",
                        "Detailed description of the IP being assigned (software code, designs, inventions, trademarks, trade secrets, etc.)",
                        learn_more=(
                            "Be as specific and detailed as possible when describing the IP being "
                            "assigned. Instead of 'software code', say 'source code for the XYZ "
                            "mobile application built using React Native, including all associated "
                            "libraries, configurations, and deployment scripts'. Vague descriptions "
                            "can lead to disputes about what was actually assigned. Include version "
                            "numbers, repository URLs, or design file names where applicable."
                        ),
                    ),
                    _clause(
                        "ipa_ip_type",
                        "IP Type",
                        "multi_select",
                        "Types of IP being assigned",
                        options=[
                            "Software/source code",
                            "Designs and artwork",
                            "Inventions and patents",
                            "Trademarks and brand assets",
                            "Trade secrets and know-how",
                            "Content and documentation",
                            "Domain names",
                            "Databases",
                        ],
                        learn_more=(
                            "Select all categories of intellectual property being transferred. Each "
                            "type of IP is governed by different laws in India: software and content "
                            "by the Copyright Act 1957, inventions by the Patents Act 1970, "
                            "trademarks by the Trade Marks Act 1999, and designs by the Designs Act "
                            "2000. Selecting the right categories ensures the assignment covers all "
                            "relevant rights and can be registered with the appropriate authorities."
                        ),
                    ),
                ],
            },
            # Step 2: Assignment Terms
            {
                "step_number": 2,
                "title": "Assignment Terms",
                "description": "Scope, consideration, and warranties for the IP assignment.",
                "clauses": [
                    _clause(
                        "ipa_scope",
                        "Assignment Scope",
                        "dropdown",
                        "Scope of IP being assigned",
                        options=[
                            "All IP created during engagement",
                            "Specific IP only (as described)",
                            "All IP related to company's business",
                        ],
                        learn_more=(
                            "The scope defines how broadly the IP assignment reaches. 'All IP "
                            "created during engagement' is the broadest and most protective for the "
                            "company \u2014 anything the assignor creates while working for or with the "
                            "company belongs to the company. 'Specific IP only' is narrower and "
                            "limited to what you described above. 'All IP related to company's "
                            "business' is a middle ground that only captures work relevant to your "
                            "industry. For founders and employees, the broadest scope is recommended."
                        ),
                        pros=["All IP during engagement: Maximum protection, no gaps",
                              "Specific IP only: Clear boundaries, easier to negotiate",
                              "Related to business: Balanced, assignor keeps unrelated work"],
                        cons=["All IP during engagement: May discourage side projects, harder to negotiate",
                              "Specific IP only: Risk of missing future IP not described",
                              "Related to business: Disputes over what is 'related' to the business"],
                        india_note=(
                            "Under Indian Copyright Act 1957 (Section 18), copyright can "
                            "be assigned wholly or partially. The assignment must be in "
                            "writing signed by the assignor. For patents, assignment must "
                            "be registered with the Patent Office under Section 68 of "
                            "Patents Act 1970."
                        ),
                        common_choice_label="Most protective: All IP created during engagement",
                    ),
                    _clause(
                        "ipa_consideration",
                        "Consideration",
                        "dropdown",
                        "Compensation for the IP assignment",
                        options=[
                            "Included in employment/consulting fees",
                            "Separate consideration of \u20b91",
                            "Specific amount",
                            "Equity",
                        ],
                        learn_more=(
                            "For the assignment to be legally valid, there must be "
                            "'consideration' (something of value given in return). This "
                            "can be as nominal as \u20b91, or included in existing "
                            "compensation. For employees and consultants, the most common "
                            "approach is to include it in their existing fees/salary. For "
                            "founders, \u20b91 consideration or equity is standard. Ensure the "
                            "consideration is documented \u2014 without it, the assignment may "
                            "be challenged as a gift and could be revocable."
                        ),
                        india_note=(
                            "Indian Contract Act requires consideration for a valid "
                            "contract. \u20b91 as consideration is legally accepted and "
                            "commonly used in IP assignments."
                        ),
                        common_choice_label="Most common: Included in existing fees",
                    ),
                    _clause(
                        "ipa_moral_rights",
                        "Moral Rights",
                        "dropdown",
                        "Whether the creator retains moral rights (right to be credited, etc.)",
                        options=[
                            "Waived to extent permitted by law",
                            "Retained by assignor",
                            "Partially waived",
                        ],
                        learn_more=(
                            "Moral rights are personal rights of the creator that exist separately "
                            "from economic rights. They include the right to be credited as the "
                            "author (right of paternity) and the right to prevent distortion of the "
                            "work. In India, moral rights under Section 57 of the Copyright Act "
                            "cannot be fully waived \u2014 the author always retains the right to claim "
                            "authorship. 'Waived to extent permitted by law' is the standard choice, "
                            "meaning the assignor agrees not to assert moral rights against the "
                            "company while retaining the rights the law does not allow them to give up."
                        ),
                        india_note=(
                            "Under Section 57 of Indian Copyright Act, moral rights "
                            "(right of paternity and right against distortion) cannot be "
                            "fully waived in India. The author always retains the right to "
                            "claim authorship. However, right against distortion can be "
                            "waived for specific purposes."
                        ),
                        common_choice_label="Standard: Waived to extent permitted",
                    ),
                    _clause(
                        "ipa_warranties",
                        "Warranties",
                        "multi_select",
                        "Warranties provided by the assignor",
                        options=[
                            "IP is original work of assignor",
                            "No third-party claims or encumbrances",
                            "No infringement of third-party rights",
                            "Assignor has authority to assign",
                            "No open-source contamination (for code)",
                        ],
                        learn_more=(
                            "Warranties are legally binding promises from the assignor about the "
                            "quality and ownership of the IP. Selecting 'IP is original work' "
                            "confirms the assignor actually created it. 'No third-party claims' "
                            "means nobody else has rights to this IP. 'No open-source contamination' "
                            "is critical for software \u2014 it confirms the code does not include "
                            "copyleft-licensed components (like GPL) that could force you to "
                            "open-source your entire product. Select all that apply for maximum "
                            "protection."
                        ),
                    ),
                ],
            },
            # Step 3: Additional Terms
            {
                "step_number": 3,
                "title": "Additional Terms",
                "description": "Future assistance obligations and governing law.",
                "clauses": [
                    _clause(
                        "ipa_future_assistance",
                        "Future Assistance",
                        "toggle",
                        "Whether assignor will assist with patent filings, trademark registrations, etc.",
                        learn_more=(
                            "This clause obligates the assignor to help the company with future IP "
                            "filings, such as signing patent applications or trademark registration "
                            "documents. This is especially important because IP registrations often "
                            "happen months or years after the initial assignment. Without this clause, "
                            "if the assignor becomes unavailable or uncooperative, you may be unable "
                            "to complete critical filings. The agreement also includes a power of "
                            "attorney so the company can sign on the assignor's behalf if needed."
                        ),
                        common_choice_label="Recommended: Yes",
                    ),
                    _clause(
                        "ipa_governing_law",
                        "Governing Law",
                        "dropdown",
                        "Governing law",
                        options=[
                            "Maharashtra",
                            "Karnataka",
                            "Delhi",
                            "Tamil Nadu",
                            "Telangana",
                        ],
                        learn_more=(
                            "Choose the state whose courts will have jurisdiction over disputes "
                            "arising from this agreement. This is typically the state where the "
                            "company is incorporated or has its principal office. IP disputes are "
                            "handled by District Courts or High Courts in India. Delhi and Mumbai "
                            "High Courts are generally considered to have the most experience with "
                            "IP litigation."
                        ),
                    ),
                ],
            },
        ],
    }


def render_ip_assignment(tpl: dict, config: dict, parties: dict) -> str:
    """Render IP Assignment Agreement HTML."""
    assignor = config.get("ipa_assignor_name", "[Assignor Name]")
    assignor_type = config.get("ipa_assignor_type", "Contractor")
    company = config.get("ipa_company_name", "[Company Name]")
    ip_desc = config.get("ipa_ip_description", "[IP Description]")
    ip_types = config.get("ipa_ip_type", [])
    scope = config.get("ipa_scope", "All IP created during engagement")
    consideration = config.get("ipa_consideration", "Included in employment/consulting fees")
    moral = config.get("ipa_moral_rights", "Waived to extent permitted by law")
    warranties = config.get("ipa_warranties", [])
    assistance = config.get("ipa_future_assistance", True)
    governing = config.get("ipa_governing_law", "Maharashtra")

    def _list_html(items: Any) -> str:
        if isinstance(items, list) and items:
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
        return f"<p>{items}</p>" if items else "<p>N/A</p>"

    sections: List[str] = []
    cn = 0

    # Section 1 — Parties
    cn += 1
    sections.append(
        f'<h2>{cn}. Parties</h2>'
        f'<div class="parties">'
        f'<p><strong>Assignor:</strong> {assignor} ({assignor_type})</p>'
        f'<p><strong>Assignee (Company):</strong> {company}</p>'
        f'</div>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This IP Assignment Agreement ("Agreement") is entered into between '
        f'<strong>{assignor}</strong> ("Assignor") and <strong>{company}</strong> '
        f'("Assignee" or "Company").</p>'
    )

    # Section 2 — IP Description
    cn += 1
    ip_types_str = ", ".join(ip_types) if isinstance(ip_types, list) else str(ip_types)
    sections.append(
        f'<h2>{cn}. Intellectual Property Description</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Assignor hereby assigns the following intellectual property '
        f'("Assigned IP") to the Assignee:</p>'
        f'<p class="clause"><em>{ip_desc}</em></p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Types of IP covered: {ip_types_str}.</p>'
    )

    # Section 3 — Assignment
    cn += 1
    sections.append(
        f'<h2>{cn}. Assignment of Rights</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Scope of assignment: <strong>{scope}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Assignor hereby irrevocably assigns, transfers, and conveys to the '
        f'Assignee all right, title, and interest in and to the Assigned IP, '
        f'including all copyrights, patent rights, trademark rights, trade secret '
        f'rights, and all other intellectual property rights therein, throughout '
        f'the world, for the full term of such rights.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The assignment includes the right to sue for past, present, and future '
        f'infringement of the Assigned IP.</p>'
    )

    # Section 4 — Consideration
    cn += 1
    sections.append(
        f'<h2>{cn}. Consideration</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'In consideration for the assignment, the Assignor shall receive: '
        f'<strong>{consideration}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Assignor acknowledges that the consideration is adequate and '
        f'sufficient for the assignment of rights herein.</p>'
    )

    # Section 5 — Moral Rights
    cn += 1
    sections.append(
        f'<h2>{cn}. Moral Rights</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Moral rights: <strong>{moral}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'To the extent moral rights cannot be waived under applicable law '
        f'(including Section 57 of the Indian Copyright Act, 1957), the Assignor '
        f'agrees not to assert such rights against the Assignee or its licensees.</p>'
    )

    # Section 6 — Warranties
    cn += 1
    sections.append(
        f'<h2>{cn}. Representations & Warranties</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Assignor represents and warrants that:</p>'
        f'{_list_html(warranties)}'
    )

    # Section 7 — Future Assistance
    if assistance:
        cn += 1
        sections.append(
            f'<h2>{cn}. Future Assistance</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Assignor agrees to provide all reasonable assistance to the '
            f'Assignee, at the Assignee\'s expense, in connection with securing, '
            f'maintaining, or enforcing the Assigned IP, including but not limited '
            f'to executing patent applications, trademark registrations, and any '
            f'other filings or documents.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Assignor hereby irrevocably appoints the Assignee as its '
            f'attorney-in-fact to execute any documents necessary to effectuate '
            f'the assignment, in the event the Assignor is unavailable or '
            f'unwilling to do so.</p>'
        )

    # Section 8 — General
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be governed by and construed in accordance with '
        f'the laws of <strong>{governing}</strong>, India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'This Agreement constitutes the entire agreement between the parties '
        f'with respect to the subject matter hereof and supersedes all prior '
        f'agreements and understandings.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This Agreement shall be binding upon and inure to the benefit of the '
        f'parties and their respective successors and assigns.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Assignor:</strong> {assignor}</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Assignee:</strong> {company}</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"IP Assignment Agreement \u2014 {assignor} to {company}", body
    )


# ======================================================================
# TEMPLATE 14: SHARE TRANSFER AGREEMENT
# ======================================================================

def share_transfer_template() -> dict:
    """Template 14 — Share Transfer Agreement."""
    return {
        "name": "Share Transfer Agreement",
        "description": (
            "Agreement for transferring shares between parties \u2014 whether founder "
            "exits, secondary sales, or investor transfers. Handles valuation, "
            "transfer restrictions, and regulatory compliance."
        ),
        "category": "Equity",
        "steps": [
            # Step 1: Transfer Details
            {
                "step_number": 1,
                "title": "Transfer Details",
                "description": "Details of the shares being transferred and the parties involved.",
                "clauses": [
                    _clause(
                        "sta_transferor_name",
                        "Transferor Name",
                        "text",
                        "Name of the person/entity selling shares",
                        learn_more=(
                            "The transferor is the current shareholder who is selling or "
                            "transferring their shares. Enter the full legal name as it appears "
                            "on the company's register of members and share certificates. If the "
                            "transferor is an entity (like an investment fund), use the full "
                            "registered name of that entity."
                        ),
                    ),
                    _clause(
                        "sta_transferee_name",
                        "Transferee Name",
                        "text",
                        "Name of the person/entity buying shares",
                        learn_more=(
                            "The transferee is the person or entity acquiring the shares. Enter "
                            "their full legal name. If the transferee is a foreign national or "
                            "foreign entity, additional FEMA (Foreign Exchange Management Act) "
                            "compliance may be required, including RBI reporting within 60 days "
                            "of the transfer."
                        ),
                    ),
                    _clause(
                        "sta_company_name",
                        "Company Name",
                        "text",
                        "Name of the company whose shares are being transferred",
                        learn_more=(
                            "Enter the exact registered name of the company whose shares are being "
                            "transferred. The company itself is not a party to this transaction "
                            "but must register the transfer in its books. The company's Articles of "
                            "Association may contain transfer restrictions that must be complied with "
                            "before the transfer can be registered."
                        ),
                    ),
                    _clause(
                        "sta_num_shares",
                        "Number of Shares",
                        "number",
                        "Number of shares being transferred",
                        learn_more=(
                            "Enter the exact number of shares being transferred. Verify this "
                            "against the company's register of members and the transferor's share "
                            "certificate. You cannot transfer more shares than the transferor holds. "
                            "Partial transfers are allowed \u2014 the transferor can sell some shares "
                            "and retain the rest."
                        ),
                    ),
                    _clause(
                        "sta_share_class",
                        "Share Class",
                        "dropdown",
                        "Class of shares being transferred",
                        options=[
                            "Equity shares",
                            "Preference shares",
                            "Compulsorily Convertible Preference Shares",
                        ],
                        learn_more=(
                            "Different classes of shares have different rights and transfer "
                            "implications. Equity shares are the most common and carry voting rights. "
                            "Preference shares have priority in dividend payments and liquidation but "
                            "usually limited voting rights. Compulsorily Convertible Preference "
                            "Shares (CCPS) are commonly used by investors \u2014 they convert to equity "
                            "shares on a specified date or event. The transfer restrictions and "
                            "pricing rules may differ by share class."
                        ),
                    ),
                    _clause(
                        "sta_price_per_share",
                        "Price Per Share",
                        "number",
                        "Price per share in INR",
                        learn_more=(
                            "The price per share should be agreed upon by both parties and should "
                            "reflect fair market value. For income tax purposes, if shares are "
                            "transferred below fair market value, the difference may be taxed as "
                            "income in the hands of the transferee under Section 56(2)(x) of the "
                            "Income Tax Act. A registered valuer's report is recommended to "
                            "establish fair value and avoid tax disputes."
                        ),
                        warning_condition={
                            "value": 0,
                            "message": (
                                "Transferring shares at zero or nominal value may trigger income "
                                "tax implications under Section 56(2)(x) of the Income Tax Act. "
                                "The difference between fair market value and the transfer price "
                                "can be treated as taxable income. Consult a CA before proceeding."
                            ),
                        },
                        india_note=(
                            "For Private Limited companies, share transfer price must "
                            "comply with Section 56 of Companies Act 2013. Stamp duty is "
                            "payable on share transfers \u2014 0.25% of consideration or "
                            "market value, whichever is higher. Transfer must be "
                            "registered within 60 days."
                        ),
                    ),
                ],
            },
            # Step 2: Transfer Conditions
            {
                "step_number": 2,
                "title": "Transfer Conditions",
                "description": "Conditions, approvals, and representations for the transfer.",
                "clauses": [
                    _clause(
                        "sta_transfer_reason",
                        "Transfer Reason",
                        "dropdown",
                        "Reason for the share transfer",
                        options=[
                            "Secondary sale",
                            "Founder exit",
                            "Investor exit",
                            "ESOP exercise and sell",
                            "Gift/inheritance",
                            "Inter-group transfer",
                        ],
                        learn_more=(
                            "The reason for transfer affects tax treatment and compliance "
                            "requirements. Secondary sales between existing shareholders are "
                            "straightforward. Founder exits may trigger tag-along or drag-along "
                            "rights in the Shareholders' Agreement. ESOP exercise and sell requires "
                            "two tax events \u2014 perquisite tax on exercise and capital gains on sale. "
                            "Gift/inheritance transfers have different stamp duty and tax rules "
                            "compared to sales."
                        ),
                        warning_condition={
                            "value": "Founder exit",
                            "message": (
                                "A founder exit may trigger drag-along, tag-along, or other "
                                "provisions in your Shareholders' Agreement. Review the SHA "
                                "carefully and ensure all co-founders and investors are informed "
                                "and have provided necessary consents."
                            ),
                        },
                    ),
                    _clause(
                        "sta_board_approval",
                        "Board Approval",
                        "toggle",
                        "Whether board approval has been obtained",
                        learn_more=(
                            "For Private Limited companies in India, share transfers must be "
                            "approved by the board of directors. This is a legal requirement, not "
                            "optional. The board has the right to refuse to register a transfer if "
                            "the Articles of Association give them that power. Obtain board approval "
                            "via a board resolution before executing the share transfer agreement. "
                            "Without board approval, the company can legally refuse to register the "
                            "transfer."
                        ),
                        india_note=(
                            "For Private Limited companies, Articles of Association "
                            "typically require board approval for share transfers. This "
                            "is a mandatory restriction under Section 2(68) of Companies "
                            "Act 2013."
                        ),
                        common_choice_label="Required: Yes",
                    ),
                    _clause(
                        "sta_rofr_compliance",
                        "ROFR Compliance",
                        "toggle",
                        "Whether Right of First Refusal (if any) has been complied with",
                        learn_more=(
                            "If the Shareholders' Agreement has ROFR (Right of First Refusal) "
                            "provisions, existing shareholders must be given the opportunity to buy "
                            "the shares at the proposed price before they can be sold to an outside "
                            "party. ROFR is designed to prevent unwanted third parties from becoming "
                            "shareholders. The process typically involves sending a written notice to "
                            "all existing shareholders with the offer details and giving them 15-30 "
                            "days to respond. Skipping ROFR compliance can make the transfer voidable."
                        ),
                        common_choice_label="If applicable: Yes",
                    ),
                    _clause(
                        "sta_representations",
                        "Representations",
                        "multi_select",
                        "Representations made by the transferor",
                        options=[
                            "Shares are free from encumbrances",
                            "No pending litigation related to shares",
                            "All taxes paid",
                            "Transferor has full authority",
                            "No restriction on transfer violated",
                        ],
                        learn_more=(
                            "Representations are legally binding statements of fact made by the "
                            "transferor. 'Free from encumbrances' means the shares are not pledged "
                            "or used as collateral for any loan. 'No pending litigation' confirms "
                            "there are no ongoing lawsuits that could affect ownership. 'All taxes "
                            "paid' means no outstanding tax liabilities related to the shares. "
                            "Selecting all representations gives the transferee maximum protection "
                            "and legal recourse if any statement turns out to be false."
                        ),
                    ),
                    _clause(
                        "sta_payment_terms",
                        "Payment Terms",
                        "dropdown",
                        "When the purchase price is paid",
                        options=[
                            "Full payment on execution",
                            "Payment within 7 days",
                            "Payment within 30 days",
                            "Installments",
                        ],
                        learn_more=(
                            "Payment terms define when the buyer pays for the shares. 'Full payment "
                            "on execution' is the safest for the seller \u2014 shares are transferred "
                            "only after full payment is received. Deferred payment options (7 or 30 "
                            "days) carry the risk that the buyer may default after the agreement is "
                            "signed. Installment payments are rare in share transfers and add "
                            "complexity around when ownership actually transfers. Ensure the payment "
                            "method is documented (bank transfer, cheque, etc.)."
                        ),
                        pros=["Full payment on execution: Zero risk for seller, clean transfer",
                              "Payment within 7 days: Slight flexibility for buyer to arrange funds",
                              "Payment within 30 days: More time for larger transactions"],
                        cons=["Full payment on execution: Buyer must have funds ready immediately",
                              "Deferred payment: Risk of buyer default after agreement signing",
                              "Installments: Complex ownership transfer, escrow may be needed"],
                        common_choice_label="Standard: Full payment on execution",
                    ),
                ],
            },
            # Step 3: Stamp Duty & Filing
            {
                "step_number": 3,
                "title": "Stamp Duty & Filing",
                "description": "Stamp duty responsibility and governing law.",
                "clauses": [
                    _clause(
                        "sta_stamp_duty",
                        "Stamp Duty",
                        "toggle",
                        "Whether stamp duty will be paid by transferee",
                        learn_more=(
                            "Stamp duty is a government tax on the share transfer transaction. "
                            "In India, it is 0.25% of the consideration amount or fair market value, "
                            "whichever is higher. By convention, the buyer (transferee) pays the "
                            "stamp duty. Stamp duty must be paid before or at the time of execution "
                            "of the share transfer instrument. Unstamped or insufficiently stamped "
                            "documents are not admissible as evidence in court."
                        ),
                        india_note=(
                            "Share transfer stamp duty is 0.25% of the consideration "
                            "amount under Indian Stamp Act. This is typically paid by "
                            "the transferee/buyer. Share transfer forms (SH-4) must be "
                            "filed with the company."
                        ),
                        common_choice_label="Standard: Paid by transferee",
                    ),
                    _clause(
                        "sta_governing_law",
                        "Governing Law",
                        "dropdown",
                        "Governing law",
                        options=[
                            "Maharashtra",
                            "Karnataka",
                            "Delhi",
                            "Tamil Nadu",
                            "Telangana",
                        ],
                        learn_more=(
                            "Choose the state whose laws and courts will govern this share transfer "
                            "agreement. This should typically match the state where the company is "
                            "registered. Disputes will be resolved through arbitration in this state "
                            "under the Arbitration and Conciliation Act, 1996. Stamp duty rates are "
                            "generally uniform for share transfers across states (0.25%), but it is "
                            "good practice to align governing law with the company's registered state."
                        ),
                    ),
                ],
            },
        ],
    }


def render_share_transfer(tpl: dict, config: dict, parties: dict) -> str:
    """Render Share Transfer Agreement HTML."""
    transferor = config.get("sta_transferor_name", "[Transferor Name]")
    transferee = config.get("sta_transferee_name", "[Transferee Name]")
    company = config.get("sta_company_name", "[Company Name]")
    num_shares = config.get("sta_num_shares", 0)
    share_class = config.get("sta_share_class", "Equity shares")
    price_per_share = config.get("sta_price_per_share", 0)

    reason = config.get("sta_transfer_reason", "Secondary sale")
    board_approval = config.get("sta_board_approval", True)
    rofr = config.get("sta_rofr_compliance", True)
    representations = config.get("sta_representations", [])
    payment = config.get("sta_payment_terms", "Full payment on execution")

    stamp_duty = config.get("sta_stamp_duty", True)
    governing = config.get("sta_governing_law", "Maharashtra")

    total_consideration = num_shares * price_per_share if isinstance(num_shares, (int, float)) and isinstance(price_per_share, (int, float)) else 0
    stamp_amount = int(total_consideration * 0.0025)

    def _list_html(items: Any) -> str:
        if isinstance(items, list) and items:
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
        return f"<p>{items}</p>" if items else "<p>N/A</p>"

    sections: List[str] = []
    cn = 0

    # Section 1 — Parties
    cn += 1
    sections.append(
        f'<h2>{cn}. Parties</h2>'
        f'<div class="parties">'
        f'<p><strong>Transferor (Seller):</strong> {transferor}</p>'
        f'<p><strong>Transferee (Buyer):</strong> {transferee}</p>'
        f'<p><strong>Company:</strong> {company}</p>'
        f'</div>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Share Transfer Agreement ("Agreement") is entered into between '
        f'<strong>{transferor}</strong> ("Transferor") and '
        f'<strong>{transferee}</strong> ("Transferee") for the transfer of shares '
        f'in <strong>{company}</strong> ("Company").</p>'
    )

    # Section 2 — Transfer Details
    cn += 1
    sections.append(
        f'<h2>{cn}. Share Transfer Details</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Transferor agrees to sell, assign, and transfer, and the Transferee '
        f'agrees to purchase and acquire:</p>'
        f'<p class="clause"><strong>Number of shares:</strong> {num_shares:,}</p>'
        f'<p class="clause"><strong>Class of shares:</strong> {share_class}</p>'
        f'<p class="clause"><strong>Price per share:</strong> INR {price_per_share:,}</p>'
        f'<p class="clause"><strong>Total consideration:</strong> INR {total_consideration:,}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Reason for transfer: <strong>{reason}</strong>.</p>'
    )

    # Section 3 — Conditions Precedent
    cn += 1
    conditions: List[str] = []
    if board_approval:
        conditions.append("Board approval for the share transfer has been obtained")
    if rofr:
        conditions.append(
            "Right of First Refusal (ROFR) provisions, if any, under the "
            "Shareholders' Agreement have been duly complied with"
        )
    conditions.append(
        "No event has occurred that would make the transfer unlawful or in "
        "violation of any applicable agreement"
    )
    sections.append(
        f'<h2>{cn}. Conditions Precedent</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The transfer is subject to the following conditions being satisfied:</p>'
        f'<ol>{"".join("<li>" + c + "</li>" for c in conditions)}</ol>'
    )

    # Section 4 — Consideration & Payment
    cn += 1
    sections.append(
        f'<h2>{cn}. Consideration & Payment</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The total consideration for the transfer of {num_shares:,} {share_class} '
        f'shall be INR {total_consideration:,} (Indian Rupees '
        f'{_number_to_words_inr(int(total_consideration))} only).</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Payment terms: <strong>{payment}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Payment shall be made by electronic bank transfer to the account '
        f'designated by the Transferor.</p>'
    )

    # Section 5 — Representations & Warranties
    cn += 1
    sections.append(
        f'<h2>{cn}. Representations & Warranties</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Transferor represents and warrants that:</p>'
        f'{_list_html(representations)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Transferee represents that it has the financial capacity and legal '
        f'authority to complete the purchase.</p>'
    )

    # Section 6 — Stamp Duty & Registration
    cn += 1
    stamp_bearer = "Transferee" if stamp_duty else "Transferor"
    sections.append(
        f'<h2>{cn}. Stamp Duty & Registration</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Stamp duty on this transfer (estimated at 0.25% = INR {stamp_amount:,}) '
        f'shall be borne by the <strong>{stamp_bearer}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The parties shall execute Form SH-4 (Share Transfer Form) and deliver '
        f'the same along with the relevant share certificates to the Company for '
        f'registration of the transfer within 60 days as required under the '
        f'Companies Act, 2013.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The Company shall register the transfer and issue new share certificates '
        f'in the name of the Transferee within 30 days of receipt of the transfer '
        f'documents, subject to compliance with the Articles of Association.</p>'
    )

    # Section 7 — Covenants
    cn += 1
    sections.append(
        f'<h2>{cn}. Post-Transfer Covenants</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Transferor shall not, after the completion date, hold out as a '
        f'shareholder of the Company in respect of the transferred shares.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Transferee shall be bound by the existing Shareholders\' Agreement '
        f'and Articles of Association of the Company from the date of registration '
        f'of the transfer.</p>'
    )

    # Section 8 — General
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be governed by and construed in accordance with '
        f'the laws of <strong>{governing}</strong>, India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Any dispute arising out of or in connection with this Agreement shall '
        f'be resolved by arbitration under the Arbitration and Conciliation Act, '
        f'1996, with the seat of arbitration being in {governing}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This Agreement constitutes the entire agreement between the parties and '
        f'supersedes all prior negotiations, representations, and agreements.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'This Agreement may be executed in counterparts, each of which shall be '
        f'deemed an original.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Transferor:</strong> {transferor}</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Transferee:</strong> {transferee}</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Share Transfer Agreement \u2014 {company}", body
    )


# ---------------------------------------------------------------------------
# Registry — makes it easy for the main service to import all templates/renderers
# ---------------------------------------------------------------------------

TIER2_TEMPLATES: Dict[str, dict] = {
    "board_resolution": board_resolution_template(),
    "privacy_policy": privacy_policy_template(),
    "terms_of_service": terms_of_service_template(),
    "offer_letter": offer_letter_template(),
    "ip_assignment": ip_assignment_template(),
    "share_transfer": share_transfer_template(),
}

TIER2_RENDERERS: Dict[str, Any] = {
    "board_resolution": render_board_resolution,
    "privacy_policy": render_privacy_policy,
    "terms_of_service": render_terms_of_service,
    "offer_letter": render_offer_letter,
    "ip_assignment": render_ip_assignment,
    "share_transfer": render_share_transfer,
}
