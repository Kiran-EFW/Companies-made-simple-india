"""Contract template definitions — Tier 4 (Templates 25–28).

Templates included:
 25. AGM Notice (Annual General Meeting Notice)
 26. EGM Notice (Extraordinary General Meeting Notice)
 27. Circular / Written Resolution
 28. Annual Compliance Checklist

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
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<style>
body{{font-family:'Georgia','Times New Roman',serif;line-height:1.8;color:#1a1a1a;max-width:800px;margin:0 auto;padding:40px;}}
h1{{font-family:'Helvetica Neue',Arial,sans-serif;font-size:24px;text-align:center;border-bottom:2px solid #333;padding-bottom:15px;margin-bottom:30px;}}
h2{{font-family:'Helvetica Neue',Arial,sans-serif;font-size:16px;margin-top:30px;color:#222;text-transform:uppercase;letter-spacing:1px;}}
.clause{{margin:15px 0;padding:10px 0;border-bottom:1px solid #eee;}}
.clause-number{{font-weight:bold;margin-right:8px;}}
.parties{{background:#f8f8f8;padding:20px;border-radius:8px;margin:20px 0;}}
.signature-block{{margin-top:60px;}}
.signature-line{{margin:30px 0;}}
.signature-line .line{{border-bottom:1px solid #333;width:300px;margin-bottom:5px;}}
.meta{{text-align:center;color:#666;font-size:13px;margin-bottom:30px;}}
table{{width:100%;border-collapse:collapse;margin:20px 0;}}
th,td{{border:1px solid #ccc;padding:10px;text-align:left;}}
th{{background:#f0f0f0;font-weight:bold;}}
.status-ok{{color:#27ae60;font-weight:bold;}}
.status-fail{{color:#e74c3c;font-weight:bold;}}
.score{{font-size:20px;font-weight:bold;text-align:center;margin:20px 0;}}
@media print{{body{{padding:20px;}}@page{{margin:2cm;size:A4;}}}}
</style>
</head><body>
<h1>{title}</h1>
<p class="meta">Date: {date or "________________________"}</p>
{body}
</body></html>'''


# ---------------------------------------------------------------------------
# Shared list-to-HTML helper
# ---------------------------------------------------------------------------

def _list_html(items: Any) -> str:
    if isinstance(items, list) and items:
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    return f"<p>{items}</p>" if items else "<p>N/A</p>"


# ======================================================================
# TEMPLATE 25: AGM NOTICE (ANNUAL GENERAL MEETING NOTICE)
# ======================================================================

def agm_notice_template() -> dict:
    """Template 25 — AGM Notice (Annual General Meeting Notice)."""
    return {
        "name": "AGM Notice (Annual General Meeting Notice)",
        "description": (
            "Generate a formal notice for an Annual General Meeting under the "
            "Companies Act 2013. Covers ordinary and special business items, "
            "proxy notice, book closure, and e-voting details."
        ),
        "category": "Corporate Governance",
        "steps": [
            # Step 1: Meeting Details
            {
                "step_number": 1,
                "title": "Meeting Details",
                "description": "Provide company and meeting information for the AGM notice.",
                "clauses": [
                    _clause(
                        "agm_company_name",
                        "Company Name",
                        "text",
                        "Company name for the notice header",
                    ),
                    _clause(
                        "agm_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                    ),
                    _clause(
                        "agm_registered_office",
                        "Registered Office",
                        "textarea",
                        "Registered office address",
                    ),
                    _clause(
                        "agm_meeting_date",
                        "Meeting Date",
                        "date",
                        "Date of the AGM",
                    ),
                    _clause(
                        "agm_meeting_time",
                        "Meeting Time",
                        "text",
                        "Time of AGM",
                        default="11:00 AM",
                    ),
                    _clause(
                        "agm_venue",
                        "Venue",
                        "text",
                        'Venue/address OR "via video conferencing"',
                    ),
                    _clause(
                        "agm_is_virtual",
                        "Virtual / Hybrid Meeting",
                        "toggle",
                        "Whether meeting is virtual/hybrid",
                        default=False,
                        india_note=(
                            "MCA allows virtual AGMs per Circular 14/2020 and "
                            "Companies (Meetings of Board and its Powers) Fourth "
                            "Amendment Rules 2020."
                        ),
                    ),
                    _clause(
                        "agm_financial_year",
                        "Financial Year",
                        "text",
                        "Financial year being reported",
                        default="2024-25",
                    ),
                    _clause(
                        "agm_notice_date",
                        "Notice Date",
                        "date",
                        "Date notice is being sent",
                    ),
                    _clause(
                        "agm_book_closure_start",
                        "Book Closure Start",
                        "date",
                        "Start of book closure period",
                        learn_more=(
                            "Section 91 allows closure of register of members "
                            "for 7-45 days."
                        ),
                        india_note=(
                            "Book closure must be announced 7 days in advance."
                        ),
                    ),
                    _clause(
                        "agm_book_closure_end",
                        "Book Closure End",
                        "date",
                        "End of book closure period",
                    ),
                ],
            },
            # Step 2: Business Items
            {
                "step_number": 2,
                "title": "Business Items",
                "description": "Select ordinary and special business items for the AGM.",
                "clauses": [
                    _clause(
                        "agm_ordinary_business_items",
                        "Ordinary Business Items",
                        "multi_select",
                        "Standard ordinary business",
                        options=[
                            "Adoption of Financial Statements",
                            "Declaration of Dividend",
                            "Appointment of Auditors",
                            "Fixation of Auditor Remuneration",
                            "Retirement of Directors by Rotation",
                            "Re-appointment of Retiring Director",
                        ],
                        learn_more=(
                            "Section 102 requires explanatory statement for "
                            "special business only."
                        ),
                        common_choice_label="First 3 items",
                    ),
                    _clause(
                        "agm_special_business_items",
                        "Special Business Items",
                        "textarea",
                        "Special business items (each on a new line)",
                        default="",
                        required=False,
                        india_note=(
                            "Any business other than ordinary business at AGM "
                            "is special business per Section 102."
                        ),
                    ),
                    _clause(
                        "agm_explanatory_statement",
                        "Explanatory Statement",
                        "textarea",
                        "Explanatory statement for special business per Section 102",
                        required=False,
                        india_note=(
                            "MANDATORY for all special business items."
                        ),
                    ),
                    _clause(
                        "agm_dividend_amount",
                        "Dividend Amount",
                        "number",
                        "Dividend per share (INR)",
                        default=0,
                        depends_on="agm_ordinary_business_items contains Declaration of Dividend",
                        required=False,
                    ),
                    _clause(
                        "agm_auditor_name",
                        "Auditor Name",
                        "text",
                        "Name of auditor/audit firm",
                        depends_on="agm_ordinary_business_items contains Appointment of Auditors",
                        required=False,
                    ),
                    _clause(
                        "agm_auditor_firm_reg",
                        "Auditor Firm Registration",
                        "text",
                        "ICAI Registration Number of auditor",
                        required=False,
                    ),
                    _clause(
                        "agm_retiring_director_name",
                        "Retiring Director Name",
                        "text",
                        "Name of retiring director",
                        depends_on="agm_ordinary_business_items contains Retirement of Directors by Rotation",
                        required=False,
                    ),
                    _clause(
                        "agm_proxy_notice",
                        "Include Proxy Form Notice",
                        "toggle",
                        "Include proxy form notice",
                        default=True,
                        india_note=(
                            "Section 105 \u2014 proxy must be deposited 48 hours "
                            "before meeting. Only members of company can act as proxy."
                        ),
                        common_choice_label="Always include",
                    ),
                    _clause(
                        "agm_ebook_notice",
                        "Include E-Voting Notice",
                        "toggle",
                        "Include e-voting notice",
                        default=True,
                        india_note=(
                            "Listed companies and companies with 1000+ members "
                            "must provide e-voting per Section 108."
                        ),
                    ),
                ],
            },
        ],
    }


def render_agm_notice(tpl: dict, config: dict, parties: dict) -> str:
    """Render AGM Notice HTML."""
    company = config.get("agm_company_name", parties.get("company_name", "[Company Name]"))
    cin = config.get("agm_cin", "[CIN]")
    reg_office = config.get("agm_registered_office", "[Registered Office]")
    meeting_date = config.get("agm_meeting_date", "")
    meeting_time = config.get("agm_meeting_time", "11:00 AM")
    venue = config.get("agm_venue", "[Venue]")
    is_virtual = config.get("agm_is_virtual", False)
    financial_year = config.get("agm_financial_year", "2024-25")
    notice_date = config.get("agm_notice_date", "")
    book_closure_start = config.get("agm_book_closure_start", "")
    book_closure_end = config.get("agm_book_closure_end", "")

    ordinary_items = config.get("agm_ordinary_business_items", [])
    if isinstance(ordinary_items, str):
        ordinary_items = [i.strip() for i in ordinary_items.split(",") if i.strip()]
    special_items_raw = config.get("agm_special_business_items", "")
    explanatory = config.get("agm_explanatory_statement", "")
    dividend_amount = config.get("agm_dividend_amount", 0)
    auditor_name = config.get("agm_auditor_name", "")
    auditor_reg = config.get("agm_auditor_firm_reg", "")
    retiring_director = config.get("agm_retiring_director_name", "")
    proxy_notice = config.get("agm_proxy_notice", True)
    evoting_notice = config.get("agm_ebook_notice", True)

    sections: List[str] = []

    # Company header
    sections.append(
        f'<div class="parties" style="text-align:center;">'
        f'<p style="font-size:20px;font-weight:bold;margin:0;">{company}</p>'
        f'<p style="margin:2px 0;">CIN: {cin}</p>'
        f'<p style="margin:2px 0;">Registered Office: {reg_office}</p>'
        f'</div>'
    )

    # Meeting details paragraph
    venue_text = venue
    if is_virtual:
        venue_text = f'{venue} (via Video Conferencing / Other Audio Visual Means)'
    sections.append(
        f'<p>NOTICE is hereby given that the Annual General Meeting of the members '
        f'of <strong>{company}</strong> will be held on '
        f'<strong>{meeting_date or "________________________"}</strong> at '
        f'<strong>{meeting_time}</strong> at <strong>{venue_text}</strong> '
        f'to transact the following business for the Financial Year '
        f'<strong>{financial_year}</strong>:</p>'
    )

    # Ordinary Business
    sections.append('<h2>ORDINARY BUSINESS</h2>')
    item_num = 1
    for item in ordinary_items:
        detail = ""
        if item == "Declaration of Dividend" and dividend_amount:
            detail = (
                f' The Board recommends a dividend of INR {dividend_amount} '
                f'per equity share for the Financial Year {financial_year}.'
            )
        elif item == "Appointment of Auditors" and auditor_name:
            reg_detail = f" (ICAI Reg. No. {auditor_reg})" if auditor_reg else ""
            detail = (
                f' To appoint M/s {auditor_name}{reg_detail} as Statutory '
                f'Auditors of the Company.'
            )
        elif item == "Retirement of Directors by Rotation" and retiring_director:
            detail = (
                f' {retiring_director}, Director, retires by rotation at this '
                f'meeting and, being eligible, offers himself/herself for '
                f're-appointment.'
            )
        elif item == "Re-appointment of Retiring Director" and retiring_director:
            detail = (
                f' To re-appoint {retiring_director} as Director of the Company '
                f'who retires by rotation.'
            )
        sections.append(
            f'<p class="clause"><span class="clause-number">{item_num}.</span> '
            f'<strong>{item}</strong>{detail}</p>'
        )
        item_num += 1

    # Special Business
    special_items = [s.strip() for s in special_items_raw.split("\n") if s.strip()] if special_items_raw else []
    if special_items:
        sections.append('<h2>SPECIAL BUSINESS</h2>')
        for si in special_items:
            sections.append(
                f'<p class="clause"><span class="clause-number">{item_num}.</span> '
                f'{si}</p>'
            )
            item_num += 1
        if explanatory:
            sections.append(
                f'<h2>EXPLANATORY STATEMENT PURSUANT TO SECTION 102</h2>'
                f'<p>{explanatory}</p>'
            )

    # Notes
    sections.append('<h2>NOTES</h2>')
    note_num = 1

    if proxy_notice:
        sections.append(
            f'<p class="clause"><span class="clause-number">{note_num}.</span> '
            f'A MEMBER ENTITLED TO ATTEND AND VOTE AT THE MEETING IS ENTITLED '
            f'TO APPOINT A PROXY to attend and vote on his/her behalf and the proxy '
            f'need not be a member of the Company. The instrument appointing a proxy '
            f'must be deposited at the Registered Office of the Company not less than '
            f'<strong>48 hours</strong> before the commencement of the meeting '
            f'(Section 105, Companies Act 2013).</p>'
        )
        note_num += 1

    if book_closure_start and book_closure_end:
        sections.append(
            f'<p class="clause"><span class="clause-number">{note_num}.</span> '
            f'The Register of Members and the Share Transfer Books of the Company '
            f'will remain closed from <strong>{book_closure_start}</strong> to '
            f'<strong>{book_closure_end}</strong> (both days inclusive) for the '
            f'purpose of the Annual General Meeting (Section 91, Companies Act 2013).</p>'
        )
        note_num += 1

    if evoting_notice:
        sections.append(
            f'<p class="clause"><span class="clause-number">{note_num}.</span> '
            f'The Company is providing facility for voting by electronic means '
            f'(e-voting) in compliance with Section 108 of the Companies Act 2013 '
            f'read with Rule 20 of the Companies (Management and Administration) '
            f'Rules 2014. Members may cast their votes electronically during the '
            f'e-voting period. Detailed instructions for e-voting shall be sent '
            f'separately.</p>'
        )
        note_num += 1

    if is_virtual:
        sections.append(
            f'<p class="clause"><span class="clause-number">{note_num}.</span> '
            f'In compliance with MCA Circular 14/2020 and Companies (Meetings of '
            f'Board and its Powers) Fourth Amendment Rules 2020, this meeting is '
            f'being conducted through Video Conferencing / Other Audio Visual Means. '
            f'Members joining through VC/OAVM shall be counted for quorum purposes.</p>'
        )
        note_num += 1

    sections.append(
        f'<p class="clause"><span class="clause-number">{note_num}.</span> '
        f'Members are requested to notify any change of address immediately to the '
        f'Company or its Registrar and Share Transfer Agent.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block">'
        '<p style="text-align:right;"><strong>By Order of the Board</strong></p>'
        '<p style="text-align:right;">For and on behalf of</p>'
        f'<p style="text-align:right;"><strong>{company}</strong></p>'
        '<div class="signature-line" style="text-align:right;">'
        '<div class="line" style="margin-left:auto;"></div>'
        '<p>Company Secretary / Director</p>'
        '</div>'
        f'<p style="text-align:right;">Place: ________________________</p>'
        f'<p style="text-align:right;">Date: {notice_date or "________________________"}</p>'
        '</div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Notice of Annual General Meeting \u2014 {company}",
        body,
        notice_date,
    )


# ======================================================================
# TEMPLATE 26: EGM NOTICE (EXTRAORDINARY GENERAL MEETING NOTICE)
# ======================================================================

def egm_notice_template() -> dict:
    """Template 26 — EGM Notice (Extraordinary General Meeting Notice)."""
    return {
        "name": "EGM Notice (Extraordinary General Meeting Notice)",
        "description": (
            "Generate a formal notice for an Extraordinary General Meeting under "
            "the Companies Act 2013. Covers special resolutions, requisition-based "
            "EGMs, and voting requirements."
        ),
        "category": "Corporate Governance",
        "steps": [
            # Step 1: Meeting Details
            {
                "step_number": 1,
                "title": "Meeting Details",
                "description": "Provide company and meeting information for the EGM notice.",
                "clauses": [
                    _clause(
                        "egm_company_name",
                        "Company Name",
                        "text",
                        "Registered name of the company",
                    ),
                    _clause(
                        "egm_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                    ),
                    _clause(
                        "egm_registered_office",
                        "Registered Office",
                        "textarea",
                        "Registered office address",
                    ),
                    _clause(
                        "egm_meeting_date",
                        "Meeting Date",
                        "date",
                        "Date of the EGM",
                    ),
                    _clause(
                        "egm_meeting_time",
                        "Meeting Time",
                        "text",
                        "Time of EGM",
                        default="11:00 AM",
                    ),
                    _clause(
                        "egm_venue",
                        "Venue",
                        "text",
                        "Venue/address of the meeting",
                    ),
                    _clause(
                        "egm_is_virtual",
                        "Virtual / Hybrid Meeting",
                        "toggle",
                        "Whether meeting is virtual/hybrid",
                        default=False,
                    ),
                    _clause(
                        "egm_notice_date",
                        "Notice Date",
                        "date",
                        "Date notice is being sent",
                    ),
                    _clause(
                        "egm_requisition_based",
                        "Requisition Based",
                        "toggle",
                        "Whether EGM is called on requisition of members",
                        default=False,
                        india_note=(
                            "Section 100 \u2014 members holding 10%+ paid-up capital "
                            "can requisition EGM. Board must call within 21 days "
                            "of requisition date."
                        ),
                    ),
                    _clause(
                        "egm_requisition_date",
                        "Requisition Date",
                        "date",
                        "Date of member requisition",
                        depends_on="egm_requisition_based",
                        required=False,
                    ),
                    _clause(
                        "egm_called_by",
                        "Called By",
                        "dropdown",
                        "Who is calling the EGM",
                        options=[
                            "Board of Directors",
                            "Requisitioning Members",
                            "NCLT Order",
                        ],
                        india_note=(
                            "If board fails to call EGM within 21 days of "
                            "requisition, requisitioning members can call it "
                            "themselves per Section 100(4)."
                        ),
                    ),
                ],
            },
            # Step 2: Special Business
            {
                "step_number": 2,
                "title": "Special Business",
                "description": "Define the resolutions to be proposed at the EGM.",
                "clauses": [
                    _clause(
                        "egm_resolution_type",
                        "Resolution Type",
                        "dropdown",
                        "Type of resolution to be passed",
                        options=[
                            "Ordinary Resolution",
                            "Special Resolution",
                        ],
                        learn_more=(
                            "Ordinary requires simple majority (>50%), Special "
                            "requires 75% majority."
                        ),
                        india_note=(
                            "Section 114 defines special resolution. Certain "
                            "matters MUST be passed by special resolution (e.g., "
                            "alteration of AOA, change of registered office to "
                            "another state, removal of auditor)."
                        ),
                    ),
                    _clause(
                        "egm_resolution_title",
                        "Resolution Title",
                        "text",
                        "Title/subject of the resolution",
                    ),
                    _clause(
                        "egm_resolution_description",
                        "Resolution Description",
                        "textarea",
                        "Full text of the proposed resolution",
                    ),
                    _clause(
                        "egm_explanatory_statement",
                        "Explanatory Statement",
                        "textarea",
                        "Explanatory statement per Section 102",
                    ),
                    _clause(
                        "egm_additional_resolutions",
                        "Additional Resolutions",
                        "textarea",
                        "Additional resolutions (one per paragraph)",
                        default="",
                        required=False,
                    ),
                    _clause(
                        "egm_proxy_notice",
                        "Include Proxy Form Notice",
                        "toggle",
                        "Include proxy form notice",
                        default=True,
                    ),
                    _clause(
                        "egm_ebook_notice",
                        "Include E-Voting Notice",
                        "toggle",
                        "Include e-voting notice",
                        default=False,
                    ),
                ],
            },
        ],
    }


def render_egm_notice(tpl: dict, config: dict, parties: dict) -> str:
    """Render EGM Notice HTML."""
    company = config.get("egm_company_name", parties.get("company_name", "[Company Name]"))
    cin = config.get("egm_cin", "[CIN]")
    reg_office = config.get("egm_registered_office", "[Registered Office]")
    meeting_date = config.get("egm_meeting_date", "")
    meeting_time = config.get("egm_meeting_time", "11:00 AM")
    venue = config.get("egm_venue", "[Venue]")
    is_virtual = config.get("egm_is_virtual", False)
    notice_date = config.get("egm_notice_date", "")
    requisition_based = config.get("egm_requisition_based", False)
    requisition_date = config.get("egm_requisition_date", "")
    called_by = config.get("egm_called_by", "Board of Directors")

    resolution_type = config.get("egm_resolution_type", "Ordinary Resolution")
    resolution_title = config.get("egm_resolution_title", "[Resolution Title]")
    resolution_desc = config.get("egm_resolution_description", "[Resolution Description]")
    explanatory = config.get("egm_explanatory_statement", "")
    additional_raw = config.get("egm_additional_resolutions", "")
    proxy_notice = config.get("egm_proxy_notice", True)
    evoting_notice = config.get("egm_ebook_notice", False)

    sections: List[str] = []

    # Company header
    sections.append(
        f'<div class="parties" style="text-align:center;">'
        f'<p style="font-size:20px;font-weight:bold;margin:0;">{company}</p>'
        f'<p style="margin:2px 0;">CIN: {cin}</p>'
        f'<p style="margin:2px 0;">Registered Office: {reg_office}</p>'
        f'</div>'
    )

    # Requisition details
    if requisition_based:
        sections.append(
            f'<p><em>This Extraordinary General Meeting has been called pursuant '
            f'to a requisition received from members under Section 100 of the '
            f'Companies Act 2013, dated '
            f'{requisition_date or "________________________"}. '
            f'The meeting is convened by: <strong>{called_by}</strong>.</em></p>'
        )

    # Meeting details
    venue_text = venue
    if is_virtual:
        venue_text = f'{venue} (via Video Conferencing / Other Audio Visual Means)'
    sections.append(
        f'<p>NOTICE is hereby given that an Extraordinary General Meeting of the '
        f'members of <strong>{company}</strong> will be held on '
        f'<strong>{meeting_date or "________________________"}</strong> at '
        f'<strong>{meeting_time}</strong> at <strong>{venue_text}</strong> '
        f'to transact the following business:</p>'
    )

    # Special Business
    sections.append('<h2>SPECIAL BUSINESS</h2>')
    item_num = 1

    # Primary resolution
    sections.append(
        f'<p class="clause"><span class="clause-number">{item_num}.</span> '
        f'To consider and, if thought fit, to pass the following resolution as '
        f'an <strong>{resolution_type}</strong>:</p>'
        f'<p class="clause" style="padding-left:30px;">'
        f'<strong>{resolution_title}</strong></p>'
        f'<p class="clause" style="padding-left:30px;">{resolution_desc}</p>'
    )
    item_num += 1

    # Additional resolutions
    additional_items = [
        a.strip() for a in additional_raw.split("\n\n") if a.strip()
    ] if additional_raw else []
    for addl in additional_items:
        sections.append(
            f'<p class="clause"><span class="clause-number">{item_num}.</span> '
            f'{addl}</p>'
        )
        item_num += 1

    # Explanatory statement
    if explanatory:
        sections.append(
            f'<h2>EXPLANATORY STATEMENT PURSUANT TO SECTION 102</h2>'
            f'<p>{explanatory}</p>'
        )

    # Notes
    sections.append('<h2>NOTES</h2>')
    note_num = 1

    if proxy_notice:
        sections.append(
            f'<p class="clause"><span class="clause-number">{note_num}.</span> '
            f'A MEMBER ENTITLED TO ATTEND AND VOTE AT THE MEETING IS ENTITLED '
            f'TO APPOINT A PROXY to attend and vote on his/her behalf and the proxy '
            f'need not be a member of the Company. The instrument appointing a proxy '
            f'must be deposited at the Registered Office of the Company not less than '
            f'<strong>48 hours</strong> before the commencement of the meeting '
            f'(Section 105, Companies Act 2013).</p>'
        )
        note_num += 1

    if evoting_notice:
        sections.append(
            f'<p class="clause"><span class="clause-number">{note_num}.</span> '
            f'The Company is providing facility for voting by electronic means '
            f'(e-voting) in compliance with Section 108 of the Companies Act 2013 '
            f'read with Rule 20 of the Companies (Management and Administration) '
            f'Rules 2014.</p>'
        )
        note_num += 1

    if is_virtual:
        sections.append(
            f'<p class="clause"><span class="clause-number">{note_num}.</span> '
            f'This meeting is being conducted through Video Conferencing / Other '
            f'Audio Visual Means in compliance with applicable MCA Circulars. '
            f'Members joining through VC/OAVM shall be counted for quorum purposes.</p>'
        )
        note_num += 1

    sections.append(
        f'<p class="clause"><span class="clause-number">{note_num}.</span> '
        f'The {resolution_type} requires '
        f'{"a simple majority (more than 50%)" if resolution_type == "Ordinary Resolution" else "a special majority (not less than 75%)"} '
        f'of votes cast by members present in person or by proxy.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block">'
        '<p style="text-align:right;"><strong>By Order of the Board</strong></p>'
        '<p style="text-align:right;">For and on behalf of</p>'
        f'<p style="text-align:right;"><strong>{company}</strong></p>'
        '<div class="signature-line" style="text-align:right;">'
        '<div class="line" style="margin-left:auto;"></div>'
        '<p>Company Secretary / Director</p>'
        '</div>'
        f'<p style="text-align:right;">Place: ________________________</p>'
        f'<p style="text-align:right;">Date: {notice_date or "________________________"}</p>'
        '</div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Notice of Extraordinary General Meeting \u2014 {company}",
        body,
        notice_date,
    )


# ======================================================================
# TEMPLATE 27: CIRCULAR / WRITTEN RESOLUTION
# ======================================================================

def circular_resolution_template() -> dict:
    """Template 27 — Circular / Written Resolution."""
    return {
        "name": "Circular / Written Resolution",
        "description": (
            "Generate a circular resolution for board or shareholders. Board "
            "resolutions by circulation under Section 175, or shareholder "
            "resolutions by postal ballot/electronic voting under Section 110."
        ),
        "category": "Corporate Governance",
        "steps": [
            # Step 1: Resolution Details
            {
                "step_number": 1,
                "title": "Resolution Details",
                "description": "Provide resolution metadata and circulation details.",
                "clauses": [
                    _clause(
                        "cr_company_name",
                        "Company Name",
                        "text",
                        "Registered name of the company",
                    ),
                    _clause(
                        "cr_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                    ),
                    _clause(
                        "cr_resolution_date",
                        "Resolution Date",
                        "date",
                        "Date of the resolution",
                    ),
                    _clause(
                        "cr_resolution_type",
                        "Resolution Type",
                        "dropdown",
                        "Type of circular resolution",
                        options=[
                            "Board Resolution by Circulation",
                            "Shareholder Resolution by Circulation",
                        ],
                        india_note=(
                            "Section 175 allows board resolutions by circulation. "
                            "Section 110 allows shareholder resolutions by postal "
                            "ballot/electronic voting."
                        ),
                    ),
                    _clause(
                        "cr_resolution_number",
                        "Resolution Number",
                        "text",
                        "Resolution reference number",
                    ),
                    _clause(
                        "cr_circulated_by",
                        "Circulated By",
                        "text",
                        "Name of person circulating the resolution (typically Company Secretary or Director)",
                    ),
                    _clause(
                        "cr_last_response_date",
                        "Last Response Date",
                        "date",
                        "Deadline for directors/members to respond",
                        india_note=(
                            "For board resolutions, no specific timeline in the "
                            "Act but should give reasonable time. For postal "
                            "ballot, 30 days from dispatch per Rule 22 of "
                            "Companies (Management and Administration) Rules."
                        ),
                    ),
                ],
            },
            # Step 2: Resolution Content
            {
                "step_number": 2,
                "title": "Resolution Content",
                "description": "Draft the resolution text and supporting details.",
                "clauses": [
                    _clause(
                        "cr_preamble",
                        "Preamble",
                        "textarea",
                        "Background/context for the resolution (WHEREAS clauses)",
                    ),
                    _clause(
                        "cr_resolution_text",
                        "Resolution Text",
                        "textarea",
                        "Full text of the resolution (RESOLVED THAT...)",
                    ),
                    _clause(
                        "cr_supporting_documents",
                        "Supporting Documents",
                        "textarea",
                        "List of documents attached for reference",
                        default="",
                        required=False,
                    ),
                    _clause(
                        "cr_requires_special_resolution",
                        "Requires Special Resolution",
                        "toggle",
                        "Whether this requires special resolution (75% majority)",
                        default=False,
                        depends_on="cr_resolution_type == Shareholder Resolution by Circulation",
                        required=False,
                    ),
                    _clause(
                        "cr_scrutinizer_name",
                        "Scrutinizer Name",
                        "text",
                        "Name of scrutinizer",
                        depends_on="cr_resolution_type == Shareholder Resolution by Circulation",
                        required=False,
                        india_note=(
                            "Company must appoint a scrutinizer (CS in practice) "
                            "per Rule 22(5)."
                        ),
                    ),
                    _clause(
                        "cr_scrutinizer_qualification",
                        "Scrutinizer Qualification",
                        "text",
                        'Qualification (e.g., "Practicing Company Secretary")',
                        depends_on="cr_resolution_type == Shareholder Resolution by Circulation",
                        required=False,
                    ),
                ],
            },
        ],
    }


def render_circular_resolution(tpl: dict, config: dict, parties: dict) -> str:
    """Render Circular / Written Resolution HTML."""
    company = config.get("cr_company_name", parties.get("company_name", "[Company Name]"))
    cin = config.get("cr_cin", "[CIN]")
    resolution_date = config.get("cr_resolution_date", "")
    resolution_type = config.get(
        "cr_resolution_type", "Board Resolution by Circulation"
    )
    resolution_number = config.get("cr_resolution_number", "[Ref No.]")
    circulated_by = config.get("cr_circulated_by", "[Name]")
    last_response_date = config.get("cr_last_response_date", "")

    preamble = config.get("cr_preamble", "")
    resolution_text = config.get("cr_resolution_text", "[Resolution Text]")
    supporting_docs = config.get("cr_supporting_documents", "")
    requires_special = config.get("cr_requires_special_resolution", False)
    scrutinizer_name = config.get("cr_scrutinizer_name", "")
    scrutinizer_qual = config.get("cr_scrutinizer_qualification", "")

    is_board = "Board" in resolution_type

    sections: List[str] = []

    # Company header
    sections.append(
        f'<div class="parties" style="text-align:center;">'
        f'<p style="font-size:20px;font-weight:bold;margin:0;">{company}</p>'
        f'<p style="margin:2px 0;">CIN: {cin}</p>'
        f'</div>'
    )

    # Title
    if is_board:
        title_text = "RESOLUTION BY CIRCULATION"
        section_ref = "Section 175 of the Companies Act 2013"
    else:
        title_text = "POSTAL BALLOT NOTICE"
        section_ref = "Section 110 of the Companies Act 2013"

    sections.append(
        f'<p style="text-align:center;"><strong>Resolution No. {resolution_number}'
        f'</strong></p>'
        f'<p>Pursuant to {section_ref}, the following resolution is being '
        f'circulated to all {"Directors" if is_board else "Members"} of the Company '
        f'for their consideration and approval.</p>'
        f'<p><strong>Date of Circulation:</strong> '
        f'{resolution_date or "________________________"}</p>'
        f'<p><strong>Last Date for Response:</strong> '
        f'{last_response_date or "________________________"}</p>'
        f'<p><strong>Circulated by:</strong> {circulated_by}</p>'
    )

    # Preamble / WHEREAS clauses
    if preamble:
        sections.append('<h2>PREAMBLE</h2>')
        for line in preamble.split("\n"):
            line = line.strip()
            if line:
                sections.append(f'<p class="clause">{line}</p>')

    # Resolution text
    sections.append(f'<h2>RESOLUTION</h2>')
    resolution_label = "Special Resolution" if requires_special else "Ordinary Resolution"
    if not is_board:
        sections.append(
            f'<p><em>To be passed as {resolution_label}</em></p>'
        )
    for line in resolution_text.split("\n"):
        line = line.strip()
        if line:
            sections.append(f'<p class="clause"><strong>{line}</strong></p>')

    # Supporting documents
    if supporting_docs:
        sections.append('<h2>SUPPORTING DOCUMENTS</h2>')
        for doc in supporting_docs.split("\n"):
            doc = doc.strip()
            if doc:
                sections.append(f'<p class="clause">\u2022 {doc}</p>')

    # Approval / Response form
    if is_board:
        sections.append('<h2>APPROVAL FORM</h2>')
        sections.append(
            '<p>I, the undersigned Director of the Company, hereby record my '
            'assent/dissent to the above resolution circulated pursuant to '
            'Section 175 of the Companies Act 2013:</p>'
            '<table>'
            '<tr><th>Name of Director</th><td>________________________</td></tr>'
            '<tr><th>DIN</th><td>________________________</td></tr>'
            '<tr><th>Assent / Dissent</th><td>________________________</td></tr>'
            '<tr><th>Date</th><td>________________________</td></tr>'
            '<tr><th>Signature</th><td>________________________</td></tr>'
            '</table>'
        )
    else:
        # Postal ballot / shareholder form
        sections.append('<h2>POSTAL BALLOT FORM</h2>')
        sections.append(
            '<p>Members are requested to carefully read the instructions printed '
            'overleaf before exercising their vote.</p>'
            '<table>'
            '<tr><th>Name of Member</th><td>________________________</td></tr>'
            '<tr><th>Folio No. / DP ID & Client ID</th><td>________________________</td></tr>'
            '<tr><th>No. of Shares Held</th><td>________________________</td></tr>'
            '<tr><th>I/We assent to the resolution (FOR)</th><td>________________________</td></tr>'
            '<tr><th>I/We dissent to the resolution (AGAINST)</th><td>________________________</td></tr>'
            '<tr><th>Date</th><td>________________________</td></tr>'
            '<tr><th>Signature</th><td>________________________</td></tr>'
            '</table>'
        )
        if scrutinizer_name:
            sections.append(
                f'<p><strong>Scrutinizer:</strong> {scrutinizer_name}'
                f'{(", " + scrutinizer_qual) if scrutinizer_qual else ""}'
                f' (appointed under Rule 22(5) of Companies (Management and '
                f'Administration) Rules 2014)</p>'
            )

    # Signature block
    sections.append(
        '<div class="signature-block">'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{circulated_by}</strong></p>'
        f'<p>{"Company Secretary / Director" if is_board else "Company Secretary"}</p>'
        f'<p>For and on behalf of {company}</p>'
        f'<p>Date: {resolution_date or "________________________"}</p>'
        '</div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"{title_text} \u2014 {company}",
        body,
        resolution_date,
    )


# ======================================================================
# TEMPLATE 28: ANNUAL COMPLIANCE CHECKLIST
# ======================================================================

def annual_compliance_checklist_template() -> dict:
    """Template 28 — Annual Compliance Checklist."""
    return {
        "name": "Annual Compliance Checklist",
        "description": (
            "Generate a comprehensive annual compliance checklist for Indian "
            "companies. Covers MCA/ROC filings, tax compliance, labour laws, "
            "FEMA, and other statutory requirements based on entity type."
        ),
        "category": "Compliance",
        "steps": [
            # Step 1: Company Details
            {
                "step_number": 1,
                "title": "Company Details",
                "description": "Provide basic company information for the compliance report.",
                "clauses": [
                    _clause(
                        "acc_company_name",
                        "Company Name",
                        "text",
                        "Registered name of the company",
                    ),
                    _clause(
                        "acc_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                    ),
                    _clause(
                        "acc_entity_type",
                        "Entity Type",
                        "dropdown",
                        "Type of entity",
                        options=[
                            "Private Limited",
                            "Public Limited",
                            "One Person Company",
                            "LLP",
                            "Section 8",
                        ],
                        india_note=(
                            "Compliance requirements differ by entity type. "
                            "LLPs have different filings than companies."
                        ),
                    ),
                    _clause(
                        "acc_financial_year",
                        "Financial Year",
                        "text",
                        "Financial year under review",
                        default="2024-25",
                    ),
                    _clause(
                        "acc_date_of_incorporation",
                        "Date of Incorporation",
                        "date",
                        "Date when the company was incorporated",
                    ),
                    _clause(
                        "acc_authorized_capital",
                        "Authorized Capital",
                        "number",
                        "Authorized share capital (INR)",
                    ),
                    _clause(
                        "acc_paid_up_capital",
                        "Paid-up Capital",
                        "number",
                        "Paid-up share capital (INR)",
                    ),
                    _clause(
                        "acc_num_employees",
                        "Number of Employees",
                        "number",
                        "Total number of employees",
                        default=0,
                        india_note=(
                            "Companies with 1000+ employees must provide e-voting. "
                            "Companies with 10+ employees must have POSH policy."
                        ),
                    ),
                    _clause(
                        "acc_turnover",
                        "Turnover",
                        "number",
                        "Annual turnover (INR)",
                        default=0,
                        india_note=(
                            "Determines GST filing frequency and audit requirements. "
                            "Companies with turnover > 40L need GST registration. "
                            "Turnover > 1Cr needs tax audit."
                        ),
                    ),
                    _clause(
                        "acc_is_dpiit_registered",
                        "DPIIT Startup Recognition",
                        "toggle",
                        "Whether the company has DPIIT Startup recognition",
                        default=False,
                    ),
                    _clause(
                        "acc_has_foreign_investment",
                        "Has Foreign Investment",
                        "toggle",
                        "Whether the company has any foreign investment",
                        default=False,
                        india_note=(
                            "FEMA compliance required. Annual return on foreign "
                            "liabilities and assets (FLA return) to RBI."
                        ),
                    ),
                ],
            },
            # Step 2: Statutory Obligations
            {
                "step_number": 2,
                "title": "Statutory Obligations",
                "description": "Mark compliance status for core statutory requirements.",
                "clauses": [
                    _clause(
                        "acc_board_meetings_held",
                        "Board Meetings Held",
                        "number",
                        "Board meetings held during the year",
                        default=4,
                        india_note=(
                            "Minimum 4 per year (one per quarter), max gap 120 "
                            "days between meetings per Section 173. First board "
                            "meeting within 30 days of incorporation."
                        ),
                    ),
                    _clause(
                        "acc_agm_held",
                        "AGM Held",
                        "toggle",
                        "Whether AGM was held",
                        default=True,
                        india_note=(
                            "First AGM within 9 months of FY close. Subsequent "
                            "AGMs within 6 months of FY close, max gap 15 months. "
                            "Section 96."
                        ),
                    ),
                    _clause(
                        "acc_agm_date",
                        "AGM Date",
                        "date",
                        "Date of AGM",
                        depends_on="acc_agm_held",
                        required=False,
                    ),
                    _clause(
                        "acc_statutory_audit_completed",
                        "Statutory Audit Completed",
                        "toggle",
                        "Whether statutory audit is complete",
                        default=True,
                    ),
                    _clause(
                        "acc_auditor_appointed",
                        "Auditor Appointed",
                        "toggle",
                        "Whether auditor has been appointed",
                        default=True,
                        india_note=(
                            "First auditor within 30 days of incorporation "
                            "(Section 139). Subsequent at AGM for 5-year term. "
                            "Annual DIR-3 KYC mandatory."
                        ),
                    ),
                    _clause(
                        "acc_itr_filed",
                        "ITR Filed",
                        "toggle",
                        "Income tax return filed",
                        default=False,
                    ),
                    _clause(
                        "acc_gst_compliant",
                        "GST Compliant",
                        "toggle",
                        "All GST returns filed (GSTR-1, 3B, 9, 9C if applicable)",
                        default=True,
                    ),
                    _clause(
                        "acc_tds_compliant",
                        "TDS Compliant",
                        "toggle",
                        "All TDS returns filed (quarterly)",
                        default=True,
                    ),
                    _clause(
                        "acc_roc_filings_done",
                        "ROC Filings Done",
                        "toggle",
                        "AOC-4/MGT-7 filed",
                        default=False,
                        india_note=(
                            "AOC-4 within 30 days of AGM. MGT-7 within 60 days "
                            "of AGM. Late filing fee: INR 100/day."
                        ),
                    ),
                    _clause(
                        "acc_dir3_kyc_done",
                        "DIR-3 KYC Done",
                        "toggle",
                        "All directors completed DIR-3 KYC",
                        default=True,
                        india_note=(
                            "Due by September 30 each year. Late fee INR 5000."
                        ),
                    ),
                    _clause(
                        "acc_msme_form_filed",
                        "MSME Form Filed",
                        "toggle",
                        "MSME Form 1 filed if payments pending to MSMEs >45 days",
                        default=False,
                        india_note=(
                            "Half-yearly filing mandatory if any outstanding "
                            "payments to MSME vendors."
                        ),
                    ),
                ],
            },
            # Step 3: Additional Compliance
            {
                "step_number": 3,
                "title": "Additional Compliance",
                "description": "Mark compliance status for additional statutory requirements.",
                "clauses": [
                    _clause(
                        "acc_posh_policy_in_place",
                        "POSH Policy in Place",
                        "toggle",
                        "Prevention of Sexual Harassment policy in place",
                        default=False,
                        india_note=(
                            "Mandatory for organizations with 10+ employees "
                            "under POSH Act 2013."
                        ),
                    ),
                    _clause(
                        "acc_icc_constituted",
                        "ICC Constituted",
                        "toggle",
                        "Internal Complaints Committee constituted",
                        default=False,
                        depends_on="acc_num_employees >= 10",
                    ),
                    _clause(
                        "acc_annual_posh_report",
                        "Annual POSH Report Filed",
                        "toggle",
                        "Annual report filed with District Officer",
                        default=False,
                        depends_on="acc_posh_policy_in_place",
                    ),
                    _clause(
                        "acc_esi_pf_compliant",
                        "ESI/PF Compliant",
                        "toggle",
                        "ESI/PF filings up to date",
                        default=True,
                        india_note=(
                            "PF mandatory for establishments with 20+ employees. "
                            "ESI mandatory for establishments with 10+ employees "
                            "with salary up to INR 21,000/month."
                        ),
                    ),
                    _clause(
                        "acc_professional_tax_paid",
                        "Professional Tax Paid",
                        "toggle",
                        "Professional tax registration and payments",
                        default=True,
                        india_note=(
                            "Varies by state. Mandatory in Karnataka, Maharashtra, "
                            "Tamil Nadu, West Bengal, etc."
                        ),
                    ),
                    _clause(
                        "acc_shops_establishment_renewal",
                        "Shops & Establishment Renewal",
                        "toggle",
                        "Shops & Establishment Act registration renewed",
                        default=False,
                        india_note=(
                            "Varies by state, usually annual renewal."
                        ),
                    ),
                    _clause(
                        "acc_trademark_renewals_done",
                        "Trademark Renewals Done",
                        "toggle",
                        "Any trademark renewals due/completed",
                        default=False,
                    ),
                    _clause(
                        "acc_data_protection_compliant",
                        "Data Protection Compliant",
                        "toggle",
                        "DPDP Act compliance",
                        default=False,
                        india_note=(
                            "Digital Personal Data Protection Act 2023 \u2014 consent "
                            "management, data processing records, breach notification "
                            "within 72 hours."
                        ),
                    ),
                    _clause(
                        "acc_fla_return_filed",
                        "FLA Return Filed",
                        "toggle",
                        "FLA return filed with RBI",
                        default=False,
                        depends_on="acc_has_foreign_investment",
                        india_note=(
                            "Due by July 15 each year for companies with "
                            "foreign investment."
                        ),
                    ),
                    _clause(
                        "acc_fc_gpr_filed",
                        "FC-GPR Filed",
                        "toggle",
                        "FC-GPR filed for any foreign investment received during the year",
                        default=False,
                        depends_on="acc_has_foreign_investment",
                    ),
                ],
            },
        ],
    }


def render_annual_compliance_checklist(tpl: dict, config: dict, parties: dict) -> str:
    """Render Annual Compliance Checklist HTML."""
    company = config.get("acc_company_name", parties.get("company_name", "[Company Name]"))
    cin = config.get("acc_cin", "[CIN]")
    entity_type = config.get("acc_entity_type", "Private Limited")
    financial_year = config.get("acc_financial_year", "2024-25")
    date_of_inc = config.get("acc_date_of_incorporation", "")
    auth_capital = config.get("acc_authorized_capital", 0)
    paid_up_capital = config.get("acc_paid_up_capital", 0)
    num_employees = config.get("acc_num_employees", 0)
    turnover = config.get("acc_turnover", 0)
    is_dpiit = config.get("acc_is_dpiit_registered", False)
    has_foreign = config.get("acc_has_foreign_investment", False)

    board_meetings = config.get("acc_board_meetings_held", 4)
    agm_held = config.get("acc_agm_held", True)
    agm_date = config.get("acc_agm_date", "")
    audit_completed = config.get("acc_statutory_audit_completed", True)
    auditor_appointed = config.get("acc_auditor_appointed", True)
    itr_filed = config.get("acc_itr_filed", False)
    gst_compliant = config.get("acc_gst_compliant", True)
    tds_compliant = config.get("acc_tds_compliant", True)
    roc_done = config.get("acc_roc_filings_done", False)
    dir3_done = config.get("acc_dir3_kyc_done", True)
    msme_filed = config.get("acc_msme_form_filed", False)

    posh_policy = config.get("acc_posh_policy_in_place", False)
    icc_constituted = config.get("acc_icc_constituted", False)
    posh_report = config.get("acc_annual_posh_report", False)
    esi_pf = config.get("acc_esi_pf_compliant", True)
    prof_tax = config.get("acc_professional_tax_paid", True)
    shops_renewal = config.get("acc_shops_establishment_renewal", False)
    trademark = config.get("acc_trademark_renewals_done", False)
    data_protection = config.get("acc_data_protection_compliant", False)
    fla_return = config.get("acc_fla_return_filed", False)
    fc_gpr = config.get("acc_fc_gpr_filed", False)

    # Build compliance items list for scoring
    compliance_items: List[Dict[str, Any]] = []

    def _add(
        name: str,
        status: bool,
        section: str,
        penalty: str = "",
        applicable: bool = True,
    ) -> None:
        compliance_items.append({
            "name": name,
            "status": status,
            "section": section,
            "penalty": penalty,
            "applicable": applicable,
        })

    # Statutory obligations
    board_ok = int(board_meetings) >= 4
    _add(
        "Board Meetings (min. 4/year)",
        board_ok,
        "Section 173",
        "INR 1,00,000 fine on company; INR 25,000 on every officer in default",
    )
    _add(
        "Annual General Meeting held",
        bool(agm_held),
        "Section 96",
        "INR 1,00,000 on company; INR 5,000 on every officer in default",
        applicable=entity_type != "LLP",
    )
    _add(
        "Statutory Audit completed",
        bool(audit_completed),
        "Section 139/143",
        "Qualification in audit report; regulatory scrutiny",
    )
    _add(
        "Auditor appointed",
        bool(auditor_appointed),
        "Section 139",
        "Central Government may appoint auditor; INR 1,00,000 fine",
        applicable=entity_type != "LLP",
    )
    _add(
        "Income Tax Return filed",
        bool(itr_filed),
        "Section 139 of IT Act",
        "Late fee u/s 234F: INR 5,000 (if turnover < 5Cr: INR 1,000); interest u/s 234A",
    )
    _add(
        "GST Returns filed",
        bool(gst_compliant),
        "CGST Act",
        "Late fee INR 50/day (INR 20/day for Nil returns); max INR 10,000/return",
    )
    _add(
        "TDS Returns filed (quarterly)",
        bool(tds_compliant),
        "Section 200(3) of IT Act",
        "Late filing fee INR 200/day u/s 234E; penalty u/s 271H up to INR 1,00,000",
    )
    _add(
        "ROC Filings (AOC-4/MGT-7)",
        bool(roc_done),
        "Section 137/92",
        "Late filing fee: INR 100/day of delay",
        applicable=entity_type != "LLP",
    )
    _add(
        "DIR-3 KYC for all directors",
        bool(dir3_done),
        "Rule 12A, Companies (Appointment and Qualification of Directors) Rules",
        "Late fee: INR 5,000 per director",
        applicable=entity_type != "LLP",
    )
    _add(
        "MSME Form 1 filed",
        bool(msme_filed),
        "Section 405, Companies Act 2013",
        "Fine up to INR 25,00,000; officer in default up to INR 5,00,000",
    )

    # Additional compliance
    _add(
        "POSH Policy in place",
        bool(posh_policy),
        "POSH Act 2013",
        "Fine up to INR 50,000; cancellation of registration on repeat offence",
        applicable=int(num_employees) >= 10,
    )
    _add(
        "Internal Complaints Committee constituted",
        bool(icc_constituted),
        "Section 4, POSH Act 2013",
        "Fine up to INR 50,000",
        applicable=int(num_employees) >= 10,
    )
    _add(
        "Annual POSH Report filed",
        bool(posh_report),
        "Section 21, POSH Act 2013",
        "No specific penalty but non-compliance noted by authorities",
        applicable=bool(posh_policy),
    )
    _add(
        "ESI/PF filings up to date",
        bool(esi_pf),
        "EPF & MP Act 1952 / ESI Act 1948",
        "Damages up to 100% of arrears; imprisonment up to 3 years",
    )
    _add(
        "Professional Tax paid",
        bool(prof_tax),
        "State Professional Tax Acts",
        "Penalty varies by state; typically INR 5/day to 10% of due amount",
    )
    _add(
        "Shops & Establishment renewal",
        bool(shops_renewal),
        "State Shops & Establishment Acts",
        "Fine varies by state; typically INR 1,000 to INR 25,000",
    )
    _add(
        "Trademark renewals done",
        bool(trademark),
        "Trade Marks Act 1999",
        "Mark may be removed from register; loss of IP protection",
    )
    _add(
        "Data Protection (DPDP Act) compliance",
        bool(data_protection),
        "DPDP Act 2023",
        "Penalty up to INR 250 Crore per instance for significant data fiduciary",
    )
    _add(
        "FLA Return filed with RBI",
        bool(fla_return),
        "FEMA / RBI Master Direction",
        "FEMA penalty proceedings; compounding fee",
        applicable=bool(has_foreign),
    )
    _add(
        "FC-GPR filed for foreign investment",
        bool(fc_gpr),
        "FEMA / RBI NDI Rules",
        "FEMA penalty proceedings; late compounding fee",
        applicable=bool(has_foreign),
    )

    # Calculate score
    applicable_items = [i for i in compliance_items if i["applicable"]]
    compliant_count = sum(1 for i in applicable_items if i["status"])
    total_applicable = len(applicable_items)
    score_pct = (
        round(compliant_count * 100 / total_applicable)
        if total_applicable > 0
        else 0
    )

    sections: List[str] = []

    # Company details header
    sections.append(
        f'<div class="parties">'
        f'<p style="font-size:18px;font-weight:bold;text-align:center;">'
        f'{company}</p>'
        f'<table>'
        f'<tr><th>CIN</th><td>{cin}</td></tr>'
        f'<tr><th>Entity Type</th><td>{entity_type}</td></tr>'
        f'<tr><th>Financial Year</th><td>{financial_year}</td></tr>'
        f'<tr><th>Date of Incorporation</th>'
        f'<td>{date_of_inc or "N/A"}</td></tr>'
        f'<tr><th>Authorized Capital</th>'
        f'<td>INR {auth_capital:,.0f}</td></tr>'
        f'<tr><th>Paid-up Capital</th>'
        f'<td>INR {paid_up_capital:,.0f}</td></tr>'
        f'<tr><th>Number of Employees</th><td>{num_employees}</td></tr>'
        f'<tr><th>Turnover</th><td>INR {turnover:,.0f}</td></tr>'
        f'<tr><th>DPIIT Startup Recognition</th>'
        f'<td>{"Yes" if is_dpiit else "No"}</td></tr>'
        f'<tr><th>Foreign Investment</th>'
        f'<td>{"Yes" if has_foreign else "No"}</td></tr>'
        f'</table></div>'
    )

    # Overall compliance score
    if score_pct >= 80:
        score_color = "#27ae60"
    elif score_pct >= 50:
        score_color = "#f39c12"
    else:
        score_color = "#e74c3c"
    sections.append(
        f'<div class="score" style="color:{score_color};">'
        f'Compliance Score: {compliant_count}/{total_applicable} '
        f'({score_pct}%)</div>'
    )

    # Compliance status table
    sections.append(
        '<h2>COMPLIANCE STATUS</h2>'
        '<table>'
        '<tr><th>Requirement</th><th>Status</th>'
        '<th>Section Reference</th><th>Penalty for Non-Compliance</th></tr>'
    )
    for item in compliance_items:
        if not item["applicable"]:
            status_html = '<span style="color:#999;">N/A</span>'
        elif item["status"]:
            status_html = '<span class="status-ok">&#10003; Compliant</span>'
        else:
            status_html = '<span class="status-fail">&#10007; Non-Compliant</span>'
        sections.append(
            f'<tr>'
            f'<td>{item["name"]}</td>'
            f'<td>{status_html}</td>'
            f'<td>{item["section"]}</td>'
            f'<td>{item["penalty"]}</td>'
            f'</tr>'
        )
    sections.append('</table>')

    # Action items for non-compliant areas
    non_compliant = [
        i for i in compliance_items if i["applicable"] and not i["status"]
    ]
    if non_compliant:
        sections.append('<h2>ACTION ITEMS</h2>')
        sections.append(
            '<p>The following items require immediate attention:</p><ol>'
        )
        for item in non_compliant:
            sections.append(
                f'<li><strong>{item["name"]}</strong> '
                f'(Ref: {item["section"]})'
                f'{(" &mdash; Penalty: " + item["penalty"]) if item["penalty"] else ""}'
                f'</li>'
            )
        sections.append('</ol>')
    else:
        sections.append(
            '<h2>ACTION ITEMS</h2>'
            '<p style="color:#27ae60;"><strong>All applicable compliance '
            'requirements are met. No action items.</strong></p>'
        )

    # Footer
    from datetime import date as dt_date
    today = dt_date.today().strftime("%d %B %Y")
    sections.append(
        f'<div class="signature-block">'
        f'<p><em>This compliance checklist has been prepared for internal review '
        f'purposes. It does not constitute legal advice. Please consult your '
        f'Company Secretary or legal advisor for specific compliance guidance.'
        f'</em></p>'
        f'<p><strong>Prepared on:</strong> {today}</p>'
        f'<p><strong>For {company}</strong></p>'
        f'<div class="signature-line"><div class="line"></div>'
        f'<p>Authorized Signatory</p></div>'
        f'</div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Annual Compliance Checklist \u2014 {company} (FY {financial_year})",
        body,
    )


# ---------------------------------------------------------------------------
# Registry — makes it easy for the main service to import all templates/renderers
# ---------------------------------------------------------------------------

TIER4_TEMPLATES: Dict[str, dict] = {
    "agm_notice": agm_notice_template(),
    "egm_notice": egm_notice_template(),
    "circular_resolution": circular_resolution_template(),
    "annual_compliance_checklist": annual_compliance_checklist_template(),
}

TIER4_RENDERERS: Dict[str, Any] = {
    "agm_notice": render_agm_notice,
    "egm_notice": render_egm_notice,
    "circular_resolution": render_circular_resolution,
    "annual_compliance_checklist": render_annual_compliance_checklist,
}
