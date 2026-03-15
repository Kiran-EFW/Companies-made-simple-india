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
                        learn_more=(
                            "This must be the exact registered name of your company as it "
                            "appears on your Certificate of Incorporation and MCA records. "
                            "Using an incorrect or abbreviated name can make the notice legally "
                            "invalid. If your company has changed its name, use the current "
                            "registered name as approved by the ROC."
                        ),
                    ),
                    _clause(
                        "agm_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                        learn_more=(
                            "The CIN is a unique 21-character alphanumeric identifier assigned "
                            "by the Ministry of Corporate Affairs (MCA) when your company is "
                            "incorporated. You can find it on your Certificate of Incorporation "
                            "or by searching on the MCA portal. Including the CIN on all official "
                            "documents is mandatory under Section 12(3)(c) of the Companies Act 2013."
                        ),
                        india_note=(
                            "Section 12(3)(c) requires CIN on all official documents, "
                            "letterheads, and notices of the company."
                        ),
                    ),
                    _clause(
                        "agm_registered_office",
                        "Registered Office",
                        "textarea",
                        "Registered office address",
                        learn_more=(
                            "This must be the full address of your registered office as filed "
                            "with the ROC, including city, state, and PIN code. Under Section 12 "
                            "of the Companies Act 2013, all communications and notices are deemed "
                            "served at this address. If you have recently changed your registered "
                            "office, ensure Form INC-22 has been filed before using the new address."
                        ),
                    ),
                    _clause(
                        "agm_meeting_date",
                        "Meeting Date",
                        "date",
                        "Date of the AGM",
                        learn_more=(
                            "Under Section 96 of the Companies Act 2013, the AGM must be held "
                            "within 6 months from the close of the financial year (i.e., by "
                            "September 30 for a March 31 FY). The first AGM must be held within "
                            "9 months of the FY close. The gap between two consecutive AGMs must "
                            "not exceed 15 months. Missing this deadline requires an ROC extension "
                            "application and may attract penalties."
                        ),
                        india_note=(
                            "Section 96 mandates AGM within 6 months of FY close. "
                            "Extension can be sought from ROC under Section 96(1) for "
                            "up to 3 months (not for first AGM)."
                        ),
                    ),
                    _clause(
                        "agm_meeting_time",
                        "Meeting Time",
                        "text",
                        "Time of AGM",
                        default="11:00 AM",
                        learn_more=(
                            "Choose a time that is convenient for all shareholders, especially if "
                            "you have NRI or foreign shareholders in different time zones. Most AGMs "
                            "in India are held between 10 AM and 2 PM on weekdays. Under Section 96(2), "
                            "the meeting must be held during business hours (9 AM to 6 PM) on a day "
                            "that is not a National Holiday, unless the articles provide otherwise."
                        ),
                    ),
                    _clause(
                        "agm_venue",
                        "Venue",
                        "text",
                        'Venue/address OR "via video conferencing"',
                        learn_more=(
                            "The AGM venue must be within the city, town, or village where the "
                            "registered office is situated, as per Section 96(2) of the Companies "
                            "Act 2013. If you are holding a virtual or hybrid meeting, you can enter "
                            "the VC/OAVM platform details here. Ensure the venue is accessible and "
                            "has adequate capacity for all members who may attend in person."
                        ),
                    ),
                    _clause(
                        "agm_is_virtual",
                        "Virtual / Hybrid Meeting",
                        "toggle",
                        "Whether meeting is virtual/hybrid",
                        default=False,
                        learn_more=(
                            "A virtual or hybrid AGM allows shareholders to attend and vote "
                            "via video conferencing (VC) or other audio-visual means (OAVM). "
                            "This is especially useful if your shareholders are spread across "
                            "different cities or countries. The company must ensure the VC/OAVM "
                            "platform supports recording, attendance tracking, and e-voting. "
                            "Members joining via VC/OAVM are counted for quorum purposes."
                        ),
                        pros=[
                            "Greater shareholder participation, especially for NRI and remote shareholders",
                            "Lower logistical costs (no venue booking, travel, or refreshments)",
                            "Meeting can be easily recorded for compliance documentation",
                        ],
                        cons=[
                            "Technical issues (connectivity, audio) can disrupt proceedings",
                            "Some shareholders may not be comfortable with technology",
                            "Additional compliance requirements for VC/OAVM platform setup",
                        ],
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
                        learn_more=(
                            "This is the financial year for which the accounts and reports are "
                            "being presented at the AGM. In India, the standard financial year runs "
                            "from April 1 to March 31 (e.g., 2024-25 means April 2024 to March 2025). "
                            "Under Section 2(41) of the Companies Act 2013, all companies must follow "
                            "this uniform financial year unless they have received special approval "
                            "from the NCLT for a different period."
                        ),
                    ),
                    _clause(
                        "agm_notice_date",
                        "Notice Date",
                        "date",
                        "Date notice is being sent",
                        learn_more=(
                            "The AGM notice must be sent at least 21 clear days before the "
                            "meeting date, as required by Section 101 of the Companies Act 2013. "
                            "'Clear days' means the day of sending the notice and the day of the "
                            "meeting are both excluded from the count. For example, if the AGM is "
                            "on September 30, the notice must be sent by September 8 at the latest. "
                            "Shorter notice is allowed only with consent of 95% of members."
                        ),
                        india_note=(
                            "Section 101 requires 21 clear days notice. Shorter notice "
                            "allowed with consent of 95% of members entitled to vote."
                        ),
                    ),
                    _clause(
                        "agm_book_closure_start",
                        "Book Closure Start",
                        "date",
                        "Start of book closure period",
                        learn_more=(
                            "Book closure is the period during which the company closes its "
                            "register of members and share transfer books. Under Section 91 of "
                            "the Companies Act 2013, this closure can last between 7 and 45 days "
                            "in a year. During this period, no share transfers are processed, which "
                            "helps the company determine the exact list of shareholders entitled to "
                            "attend the AGM, receive dividends, or exercise voting rights. The book "
                            "closure dates must be announced at least 7 days in advance via newspaper "
                            "advertisement or electronic means."
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
                        learn_more=(
                            "This is the last day of the book closure period. The total book "
                            "closure period (from start to end, both inclusive) cannot exceed 45 "
                            "days in a single year under Section 91. Typically, companies keep the "
                            "book closure period short (7-10 days) ending on or just before the AGM "
                            "date. Any share transfers lodged after the start date will only be "
                            "processed after the book closure ends."
                        ),
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
                            "Ordinary business items are the standard agenda items that are "
                            "transacted at every AGM as defined under Section 102(2) of the "
                            "Companies Act 2013. These include adopting financial statements, "
                            "declaring dividends, appointing auditors, and dealing with director "
                            "retirements by rotation. Unlike special business, ordinary business "
                            "does not require a separate explanatory statement. Most startups and "
                            "private companies select at least the first three items."
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
                        learn_more=(
                            "Special business refers to any agenda item at the AGM that is not "
                            "ordinary business. Common examples include increasing authorized "
                            "capital, issuing ESOPs, related-party transactions, changing the "
                            "registered office to another state, or amending the Articles of "
                            "Association. Each special business item must be accompanied by an "
                            "explanatory statement under Section 102 that discloses all material "
                            "facts and the interest of directors or key managerial personnel."
                        ),
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
                        learn_more=(
                            "The explanatory statement is a mandatory annexure to the AGM notice "
                            "for all special business items, as required by Section 102 of the "
                            "Companies Act 2013. It must set out all material facts concerning each "
                            "item of special business, including the nature of concern or interest "
                            "of every director, manager, or key managerial personnel. Failure to "
                            "include an adequate explanatory statement can render the resolution "
                            "void. Write it in clear, simple language so shareholders can make an "
                            "informed voting decision."
                        ),
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
                        learn_more=(
                            "This is the dividend amount per equity share recommended by the "
                            "Board of Directors. Under Section 123 of the Companies Act 2013, "
                            "dividends can only be declared out of profits (current year or "
                            "accumulated reserves). The Board recommends the dividend, but "
                            "shareholders at the AGM approve it -- they can reduce it but cannot "
                            "increase it beyond the Board's recommendation. Dividend Distribution "
                            "Tax (DDT) was abolished in 2020; dividends are now taxable in the "
                            "hands of shareholders, and the company must deduct TDS under Section "
                            "194 of the Income Tax Act."
                        ),
                        india_note=(
                            "Section 123 governs dividend declaration. Dividends are "
                            "taxable in shareholders' hands post-2020. TDS at 10% "
                            "applies if dividend exceeds INR 5,000 per shareholder."
                        ),
                    ),
                    _clause(
                        "agm_auditor_name",
                        "Auditor Name",
                        "text",
                        "Name of auditor/audit firm",
                        depends_on="agm_ordinary_business_items contains Appointment of Auditors",
                        required=False,
                        learn_more=(
                            "Enter the name of the Chartered Accountant or CA firm being appointed "
                            "as Statutory Auditor. Under Section 139 of the Companies Act 2013, "
                            "auditors are appointed for a term of 5 consecutive years at the AGM. "
                            "The auditor must be an ICAI-registered CA or firm and must provide a "
                            "written consent and eligibility certificate (Form ADT-1) before "
                            "appointment. Ensure the auditor has no disqualifications under "
                            "Section 141."
                        ),
                    ),
                    _clause(
                        "agm_auditor_firm_reg",
                        "Auditor Firm Registration",
                        "text",
                        "ICAI Registration Number of auditor",
                        required=False,
                        learn_more=(
                            "This is the unique registration number assigned by the Institute "
                            "of Chartered Accountants of India (ICAI) to the auditor or audit "
                            "firm. It is typically in the format of a 6-digit number followed by "
                            "a region code (e.g., 012345N). You can verify the registration on "
                            "the ICAI website. Including this number ensures authenticity and "
                            "helps shareholders verify the auditor's credentials."
                        ),
                    ),
                    _clause(
                        "agm_retiring_director_name",
                        "Retiring Director Name",
                        "text",
                        "Name of retiring director",
                        depends_on="agm_ordinary_business_items contains Retirement of Directors by Rotation",
                        required=False,
                        learn_more=(
                            "Under Section 152(6) of the Companies Act 2013, at least two-thirds "
                            "of the total number of directors must be liable to retire by rotation. "
                            "One-third of such rotational directors must retire at each AGM, starting "
                            "with those who have been in office the longest since their last "
                            "appointment. The retiring director is eligible for re-appointment unless "
                            "the company decides otherwise. Independent directors are not subject to "
                            "retirement by rotation."
                        ),
                        india_note=(
                            "Section 152(6) governs retirement by rotation. Managing "
                            "Director, Whole-time Director, and Independent Directors are "
                            "excluded from rotation requirements."
                        ),
                    ),
                    _clause(
                        "agm_proxy_notice",
                        "Include Proxy Form Notice",
                        "toggle",
                        "Include proxy form notice",
                        default=True,
                        learn_more=(
                            "A proxy form allows shareholders who cannot attend the AGM in person "
                            "to appoint another person to attend and vote on their behalf. Under "
                            "Section 105 of the Companies Act 2013, every member entitled to attend "
                            "and vote has the right to appoint a proxy. The proxy instrument must be "
                            "deposited at the registered office at least 48 hours before the meeting. "
                            "It is standard practice to always include the proxy notice -- disabling "
                            "this is not recommended as it may deny shareholders their statutory right."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Not including a proxy notice may violate Section 105 of the "
                                "Companies Act 2013, which gives every member the right to "
                                "appoint a proxy. This is strongly discouraged."
                            ),
                        },
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
                        learn_more=(
                            "E-voting allows shareholders to cast their votes electronically "
                            "before or during the meeting, rather than only in person. Under "
                            "Section 108 of the Companies Act 2013 read with Rule 20 of the "
                            "Companies (Management and Administration) Rules 2014, listed "
                            "companies and companies with 1,000 or more members must mandatorily "
                            "provide e-voting. Even if not mandatory for your company, offering "
                            "e-voting improves shareholder participation and is considered good "
                            "governance practice."
                        ),
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
                        learn_more=(
                            "Enter the exact registered name of your company as it appears on "
                            "your Certificate of Incorporation and MCA records. This name will "
                            "appear on the official EGM notice sent to all shareholders. Using an "
                            "incorrect or informal name can make the notice legally challengeable."
                        ),
                    ),
                    _clause(
                        "egm_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                        learn_more=(
                            "The Corporate Identification Number is a 21-character unique code "
                            "assigned by MCA at the time of incorporation. It encodes your company "
                            "type, state of registration, and year of incorporation. Including CIN "
                            "on all official notices and correspondence is mandatory under Section "
                            "12(3)(c) of the Companies Act 2013."
                        ),
                    ),
                    _clause(
                        "egm_registered_office",
                        "Registered Office",
                        "textarea",
                        "Registered office address",
                        learn_more=(
                            "Provide the complete registered office address as filed with the "
                            "ROC. This address appears on the EGM notice header and is the "
                            "address where proxy forms and other documents must be deposited. "
                            "Under Section 12, the registered office is the official address for "
                            "all communications to the company."
                        ),
                    ),
                    _clause(
                        "egm_meeting_date",
                        "Meeting Date",
                        "date",
                        "Date of the EGM",
                        learn_more=(
                            "Unlike AGMs, there is no fixed deadline for holding an EGM -- it "
                            "can be called at any time during the year when urgent business needs "
                            "to be transacted. However, if the EGM is called on requisition of "
                            "members under Section 100, the Board must call the meeting within "
                            "21 days of receiving the requisition, and the meeting must be held "
                            "within 45 days from the date of the requisition. Ensure at least 21 "
                            "clear days' notice is given to all members before the meeting date."
                        ),
                        india_note=(
                            "Section 100 timelines: Board must call EGM within 21 days "
                            "of requisition; meeting must be held within 45 days."
                        ),
                    ),
                    _clause(
                        "egm_meeting_time",
                        "Meeting Time",
                        "text",
                        "Time of EGM",
                        default="11:00 AM",
                        learn_more=(
                            "EGMs are typically held during business hours between 9 AM and 6 PM "
                            "on a working day, similar to AGMs. Choose a time that allows maximum "
                            "shareholder participation. If you have shareholders in different time "
                            "zones, consider a mid-day slot. Unlike AGMs, there is no specific "
                            "statutory restriction on EGM timing, but holding it during business "
                            "hours is best practice."
                        ),
                    ),
                    _clause(
                        "egm_venue",
                        "Venue",
                        "text",
                        "Venue/address of the meeting",
                        learn_more=(
                            "The EGM venue must be at the registered office or within the same "
                            "city, town, or village as the registered office, per Section 96(2) "
                            "read with Section 100. If holding a virtual meeting, enter the "
                            "VC/OAVM platform details. Make sure the venue can accommodate "
                            "all members who may wish to attend in person."
                        ),
                    ),
                    _clause(
                        "egm_is_virtual",
                        "Virtual / Hybrid Meeting",
                        "toggle",
                        "Whether meeting is virtual/hybrid",
                        default=False,
                        learn_more=(
                            "A virtual EGM allows shareholders to attend and participate via "
                            "video conferencing or other audio-visual means. This is particularly "
                            "useful for urgent EGMs where gathering all members physically may "
                            "cause delays. The company must ensure the platform supports secure "
                            "voting, attendance tracking, and recording. Members participating "
                            "via VC/OAVM are counted for quorum purposes."
                        ),
                        pros=[
                            "Faster to organize for urgent matters without venue logistics",
                            "Higher participation rate, especially for geographically dispersed shareholders",
                            "Easy recording and documentation for compliance purposes",
                        ],
                        cons=[
                            "Technical failures may disrupt voting on critical resolutions",
                            "Shareholders unfamiliar with technology may feel excluded",
                            "Requires a compliant VC/OAVM platform with e-voting capability",
                        ],
                        india_note=(
                            "MCA allows virtual EGMs per Circular 14/2020 and "
                            "Companies (Meetings of Board and its Powers) Fourth "
                            "Amendment Rules 2020."
                        ),
                    ),
                    _clause(
                        "egm_notice_date",
                        "Notice Date",
                        "date",
                        "Date notice is being sent",
                        learn_more=(
                            "The EGM notice must be sent at least 21 clear days before the "
                            "meeting date, as per Section 101 of the Companies Act 2013. "
                            "'Clear days' excludes both the day of dispatch and the day of "
                            "the meeting from the count. Shorter notice is allowed only with "
                            "consent of members holding 95% or more of the paid-up capital "
                            "that carries voting rights."
                        ),
                        india_note=(
                            "Section 101 requires 21 clear days notice. Shorter notice "
                            "permitted with 95% member consent."
                        ),
                    ),
                    _clause(
                        "egm_requisition_based",
                        "Requisition Based",
                        "toggle",
                        "Whether EGM is called on requisition of members",
                        default=False,
                        learn_more=(
                            "A requisition-based EGM is one called at the demand of shareholders, "
                            "not by the Board's own initiative. Under Section 100 of the Companies "
                            "Act 2013, members holding at least 10% of the paid-up share capital "
                            "with voting rights can requisition the Board to call an EGM. The "
                            "requisition must state the matters to be considered. If the Board "
                            "fails to call the meeting within 21 days, the requisitioning members "
                            "can call it themselves within 3 months from the date of the requisition."
                        ),
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
                        learn_more=(
                            "This is the date on which the requisitioning members formally "
                            "submitted their requisition to the Board. This date is critical "
                            "because it triggers statutory timelines: the Board must call the "
                            "EGM within 21 days, and the meeting itself must be held within 45 "
                            "days from this date. If these deadlines are missed, the requisitioning "
                            "members gain the right to call the EGM themselves."
                        ),
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
                        learn_more=(
                            "This indicates who has convened the EGM. In most cases, the Board "
                            "of Directors calls the meeting. However, if the Board fails to act "
                            "within 21 days of receiving a valid requisition, the requisitioning "
                            "members can call the EGM themselves under Section 100(4). In rare "
                            "cases, the National Company Law Tribunal (NCLT) may order an EGM to "
                            "be called under Section 98, typically in situations of deadlock or "
                            "oppression/mismanagement disputes."
                        ),
                        warning_condition={
                            "value": "NCLT Order",
                            "message": (
                                "An NCLT-ordered EGM is typically a result of disputes "
                                "or deadlock situations. Ensure you have the certified copy "
                                "of the NCLT order and comply with all conditions specified "
                                "in the order, including quorum and chairperson requirements."
                            ),
                        },
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
                            "An Ordinary Resolution requires a simple majority -- more than 50% "
                            "of votes cast by members present in person or by proxy. A Special "
                            "Resolution requires at least 75% of votes cast in favour. The type "
                            "of resolution needed depends on the subject matter: routine matters "
                            "like appointing a director usually need an ordinary resolution, while "
                            "significant changes like altering the Articles of Association, changing "
                            "the registered office to another state, or removing an auditor before "
                            "term expiry must be passed by special resolution. Choosing the wrong "
                            "resolution type can make the resolution invalid."
                        ),
                        warning_condition={
                            "value": "Ordinary Resolution",
                            "message": (
                                "Double-check that your resolution subject does not legally "
                                "require a Special Resolution. Matters like alteration of AOA, "
                                "change of name, reduction of capital, or removal of auditor "
                                "mandatorily require a Special Resolution under the Companies "
                                "Act 2013. Passing these as Ordinary Resolutions will be invalid."
                            ),
                        },
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
                        learn_more=(
                            "This is the short, descriptive title of the resolution that will "
                            "appear as the heading in the EGM notice. It should clearly convey "
                            "the subject matter, such as 'Increase in Authorized Share Capital' "
                            "or 'Approval of Related Party Transaction'. A clear title helps "
                            "shareholders quickly understand what they are voting on."
                        ),
                    ),
                    _clause(
                        "egm_resolution_description",
                        "Resolution Description",
                        "textarea",
                        "Full text of the proposed resolution",
                        learn_more=(
                            "This is the complete legal text of the resolution, typically starting "
                            "with 'RESOLVED THAT...' followed by the specific action being approved. "
                            "Be precise and comprehensive -- the resolution text is what gets recorded "
                            "in the company's minutes book and filed with the ROC. Include specific "
                            "details like amounts, names, dates, and conditions. If any director or "
                            "KMP is authorized to take further action, include a 'RESOLVED FURTHER "
                            "THAT...' clause authorizing them."
                        ),
                    ),
                    _clause(
                        "egm_explanatory_statement",
                        "Explanatory Statement",
                        "textarea",
                        "Explanatory statement per Section 102",
                        learn_more=(
                            "Under Section 102 of the Companies Act 2013, every EGM notice must "
                            "be accompanied by an explanatory statement setting out all material "
                            "facts concerning each item of business. This must include the nature "
                            "of concern or interest (financial or otherwise) of every director, "
                            "manager, or key managerial personnel in the resolution. The statement "
                            "helps shareholders make informed decisions. Inadequate disclosure can "
                            "render the resolution voidable at the instance of any aggrieved member."
                        ),
                        india_note=(
                            "Section 102 mandates explanatory statement for all "
                            "special business. Non-compliance may render the "
                            "resolution voidable."
                        ),
                    ),
                    _clause(
                        "egm_additional_resolutions",
                        "Additional Resolutions",
                        "textarea",
                        "Additional resolutions (one per paragraph)",
                        default="",
                        required=False,
                        learn_more=(
                            "If you have more than one resolution to pass at this EGM, enter "
                            "each additional resolution as a separate paragraph. Each resolution "
                            "should be a complete, self-contained statement starting with 'RESOLVED "
                            "THAT...'. Remember that each resolution item also needs its own "
                            "explanatory statement under Section 102 if it constitutes special "
                            "business. Shareholders vote on each resolution separately."
                        ),
                    ),
                    _clause(
                        "egm_proxy_notice",
                        "Include Proxy Form Notice",
                        "toggle",
                        "Include proxy form notice",
                        default=True,
                        learn_more=(
                            "A proxy notice informs shareholders that they can appoint someone "
                            "to attend and vote on their behalf if they cannot attend the EGM "
                            "in person. Under Section 105 of the Companies Act 2013, every member "
                            "has the right to appoint a proxy, and the proxy instrument must be "
                            "deposited at the registered office at least 48 hours before the "
                            "meeting. It is strongly recommended to always include this notice."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Excluding the proxy notice may violate shareholders' "
                                "statutory right to appoint a proxy under Section 105 of "
                                "the Companies Act 2013. This is not recommended."
                            ),
                        },
                        india_note=(
                            "Section 105 gives every member the right to appoint a proxy. "
                            "Proxy form must be deposited 48 hours before the meeting."
                        ),
                    ),
                    _clause(
                        "egm_ebook_notice",
                        "Include E-Voting Notice",
                        "toggle",
                        "Include e-voting notice",
                        default=False,
                        learn_more=(
                            "E-voting enables shareholders to cast their votes electronically "
                            "before or during the EGM. Under Section 108, this is mandatory for "
                            "listed companies and companies with 1,000 or more members. For smaller "
                            "private companies, e-voting is optional but improves participation. "
                            "If enabled, you must engage an e-voting platform provider and appoint "
                            "a scrutinizer to oversee the process."
                        ),
                        india_note=(
                            "Section 108 read with Rule 20 mandates e-voting for listed "
                            "companies and companies with 1000+ members."
                        ),
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
                        learn_more=(
                            "Enter the full registered name of your company as it appears on "
                            "MCA records. This name will appear on the circular resolution "
                            "document and must match the name on your Certificate of "
                            "Incorporation. Circular resolutions are official company records "
                            "that may be scrutinized during audits or due diligence."
                        ),
                    ),
                    _clause(
                        "cr_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                        learn_more=(
                            "Your 21-character Corporate Identification Number as assigned by "
                            "MCA. This is a mandatory identifier on all official company documents "
                            "under Section 12(3)(c) of the Companies Act 2013. You can find it on "
                            "your Certificate of Incorporation or by searching the MCA21 portal."
                        ),
                    ),
                    _clause(
                        "cr_resolution_date",
                        "Resolution Date",
                        "date",
                        "Date of the resolution",
                        learn_more=(
                            "This is the date when the resolution is circulated to directors "
                            "or members for their approval. For board resolutions by circulation "
                            "under Section 175, the resolution is deemed passed on the date the "
                            "last director signs their assent (provided a majority has approved). "
                            "For shareholder resolutions by postal ballot under Section 110, the "
                            "date of the scrutinizer's report is considered the date of passing."
                        ),
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
                        learn_more=(
                            "A Board Resolution by Circulation (Section 175) allows the Board "
                            "to pass a resolution without holding a physical meeting -- the "
                            "resolution is sent to all directors and is deemed passed when a "
                            "majority of directors who are entitled to vote approve it. A "
                            "Shareholder Resolution by Circulation (Section 110) is also called "
                            "a postal ballot, where members vote by post or electronic means "
                            "without attending a meeting. Note: certain matters like approval of "
                            "annual accounts or appointment of auditors cannot be done by "
                            "circulation and require a physical/virtual meeting."
                        ),
                        pros=[
                            "Faster decision-making without scheduling a physical meeting",
                            "Convenient when directors or members are in different locations",
                            "Documented paper trail of each participant's individual assent/dissent",
                        ],
                        cons=[
                            "No opportunity for live discussion or debate on the resolution",
                            "Certain important matters cannot legally be passed by circulation",
                            "If any director requires the matter to be discussed at a meeting, the circulation process must stop (Section 175(3))",
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
                        learn_more=(
                            "Assign a unique reference number to this resolution for tracking "
                            "and record-keeping purposes. A common format is 'BR/YYYY-YY/NNN' "
                            "for board resolutions or 'SR/YYYY-YY/NNN' for shareholder "
                            "resolutions, where YYYY-YY is the financial year and NNN is a "
                            "sequential number. This number will be referenced in the minutes "
                            "book, ROC filings, and any related documentation."
                        ),
                    ),
                    _clause(
                        "cr_circulated_by",
                        "Circulated By",
                        "text",
                        "Name of person circulating the resolution (typically Company Secretary or Director)",
                        learn_more=(
                            "This is the name of the person responsible for circulating the "
                            "resolution to all directors or members. Typically, this is the "
                            "Company Secretary (if appointed) or a Director authorized by the "
                            "Board. For startups without a Company Secretary, any Director can "
                            "circulate the resolution. This person is also responsible for "
                            "collecting responses and recording the outcome in the minutes book."
                        ),
                    ),
                    _clause(
                        "cr_last_response_date",
                        "Last Response Date",
                        "date",
                        "Deadline for directors/members to respond",
                        learn_more=(
                            "This is the deadline by which all directors or members must submit "
                            "their assent or dissent to the resolution. For board resolutions by "
                            "circulation, the Companies Act does not prescribe a specific timeline, "
                            "but you should give directors a reasonable period (typically 7-15 days). "
                            "For shareholder resolutions by postal ballot, the voting period must be "
                            "at least 30 days from the date of dispatch, as per Rule 22 of the "
                            "Companies (Management and Administration) Rules 2014."
                        ),
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
                        learn_more=(
                            "The preamble provides the background and context for the resolution "
                            "using 'WHEREAS' clauses. Each WHEREAS clause states a relevant fact "
                            "or circumstance that leads to the resolution. For example: 'WHEREAS "
                            "the Company requires additional working capital for expansion...' "
                            "A well-drafted preamble helps directors or members understand why "
                            "the resolution is necessary and provides a documented rationale for "
                            "future reference during audits or regulatory reviews."
                        ),
                    ),
                    _clause(
                        "cr_resolution_text",
                        "Resolution Text",
                        "textarea",
                        "Full text of the resolution (RESOLVED THAT...)",
                        learn_more=(
                            "This is the operative part of the resolution, starting with "
                            "'RESOLVED THAT...' followed by the specific decision or authorization "
                            "being approved. Be precise about what is being approved, including "
                            "amounts, names, terms, and conditions. If you need to authorize "
                            "someone to execute the decision, add a 'RESOLVED FURTHER THAT...' "
                            "clause. This text is entered verbatim into the statutory records and "
                            "may be filed with the ROC, so ensure accuracy and completeness."
                        ),
                    ),
                    _clause(
                        "cr_supporting_documents",
                        "Supporting Documents",
                        "textarea",
                        "List of documents attached for reference",
                        default="",
                        required=False,
                        learn_more=(
                            "List all documents that are being shared along with the resolution "
                            "to help directors or members make an informed decision. Common "
                            "supporting documents include draft agreements, financial statements, "
                            "valuation reports, legal opinions, or regulatory approvals. Enter "
                            "each document name on a separate line. Providing comprehensive "
                            "supporting materials demonstrates good governance and reduces the "
                            "risk of challenges to the resolution."
                        ),
                    ),
                    _clause(
                        "cr_requires_special_resolution",
                        "Requires Special Resolution",
                        "toggle",
                        "Whether this requires special resolution (75% majority)",
                        default=False,
                        depends_on="cr_resolution_type == Shareholder Resolution by Circulation",
                        required=False,
                        learn_more=(
                            "A special resolution requires at least 75% of votes cast to be in "
                            "favour, compared to just over 50% for an ordinary resolution. Certain "
                            "matters under the Companies Act 2013 mandatorily require a special "
                            "resolution, including alteration of the Articles of Association, "
                            "change of company name, reduction of share capital, buy-back of "
                            "shares, and winding up. If your resolution topic falls into one of "
                            "these categories, you must enable this toggle -- otherwise the "
                            "resolution will be legally invalid even if passed."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Verify that the subject matter of your resolution does not "
                                "legally require a Special Resolution. Passing a matter that "
                                "requires 75% majority as an Ordinary Resolution will render "
                                "it void and unenforceable."
                            ),
                        },
                        india_note=(
                            "Section 114(2) defines special resolution requirements. "
                            "Review Section 114 to check if your resolution topic "
                            "mandatorily requires special resolution."
                        ),
                    ),
                    _clause(
                        "cr_scrutinizer_name",
                        "Scrutinizer Name",
                        "text",
                        "Name of scrutinizer",
                        depends_on="cr_resolution_type == Shareholder Resolution by Circulation",
                        required=False,
                        learn_more=(
                            "A scrutinizer is an independent person appointed to oversee the "
                            "postal ballot or e-voting process and ensure fairness. Under Rule "
                            "22(5) of the Companies (Management and Administration) Rules 2014, "
                            "the company must appoint a scrutinizer who is typically a Practicing "
                            "Company Secretary (PCS), Chartered Accountant, or Cost Accountant. "
                            "The scrutinizer counts the votes, verifies their validity, and "
                            "submits a report to the Chairman within 48 hours of the conclusion "
                            "of voting."
                        ),
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
                        learn_more=(
                            "Enter the professional qualification of the scrutinizer, such as "
                            "'Practicing Company Secretary', 'Chartered Accountant', or 'Cost "
                            "Accountant'. The scrutinizer must be an independent professional "
                            "who is not an employee or officer of the company. Their qualification "
                            "is mentioned in the postal ballot notice to establish credibility and "
                            "comply with Rule 22(5) requirements."
                        ),
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
                        learn_more=(
                            "Enter your company's exact registered name as it appears in MCA "
                            "records. This compliance checklist will be generated as an internal "
                            "review document for your company, and may be shared with auditors, "
                            "legal advisors, or investors during due diligence. Using the correct "
                            "registered name ensures the document is properly associated with "
                            "your company's compliance records."
                        ),
                    ),
                    _clause(
                        "acc_cin",
                        "CIN",
                        "text",
                        "Corporate Identification Number",
                        learn_more=(
                            "Your 21-character Corporate Identification Number uniquely "
                            "identifies your company in MCA records. It encodes your company "
                            "type (Private/Public/OPC/Section 8), state of registration, year "
                            "of incorporation, and a unique serial number. This number links "
                            "your compliance checklist to your specific entity in regulatory "
                            "systems."
                        ),
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
                        learn_more=(
                            "Your entity type determines which compliance requirements apply "
                            "to your company. Private Limited companies file AOC-4 and MGT-7 "
                            "with the ROC, while LLPs file Form 8 and Form 11 instead. Public "
                            "Limited companies have additional requirements like mandatory "
                            "e-voting, LODR compliance (if listed), and stricter board "
                            "composition rules. One Person Companies (OPCs) have relaxed "
                            "requirements like no need for AGM. Section 8 companies (non-profits) "
                            "have unique compliance around utilization of profits."
                        ),
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
                        learn_more=(
                            "Enter the financial year for which you are reviewing compliance "
                            "status (e.g., 2024-25 for April 2024 to March 2025). The compliance "
                            "checklist evaluates all statutory obligations that fell due during "
                            "this period. In India, the financial year is uniformly April 1 to "
                            "March 31 under Section 2(41) of the Companies Act 2013, unless "
                            "NCLT has granted a special exemption."
                        ),
                    ),
                    _clause(
                        "acc_date_of_incorporation",
                        "Date of Incorporation",
                        "date",
                        "Date when the company was incorporated",
                        learn_more=(
                            "This is the date on your Certificate of Incorporation issued by "
                            "the ROC. It is important because several compliance deadlines are "
                            "calculated from this date, such as the first board meeting (within "
                            "30 days), first auditor appointment (within 30 days), commencement "
                            "of business filing (within 180 days), and the first AGM timeline. "
                            "For newly incorporated companies, review all first-year compliance "
                            "deadlines carefully."
                        ),
                    ),
                    _clause(
                        "acc_authorized_capital",
                        "Authorized Capital",
                        "number",
                        "Authorized share capital (INR)",
                        learn_more=(
                            "Authorized capital is the maximum amount of share capital your "
                            "company is permitted to issue, as stated in your Memorandum of "
                            "Association. This determines the stamp duty and ROC fees you paid "
                            "at incorporation. If you plan to issue more shares (e.g., for a "
                            "funding round), you may need to increase your authorized capital "
                            "first by passing a special resolution and filing Form SH-7 with "
                            "the ROC, along with additional stamp duty."
                        ),
                        india_note=(
                            "Authorized capital increase requires special resolution, "
                            "Form SH-7 filing, and additional stamp duty (varies by state)."
                        ),
                    ),
                    _clause(
                        "acc_paid_up_capital",
                        "Paid-up Capital",
                        "number",
                        "Paid-up share capital (INR)",
                        learn_more=(
                            "Paid-up capital is the actual amount of money shareholders have "
                            "paid to the company for their shares. This is always less than or "
                            "equal to the authorized capital. Paid-up capital affects several "
                            "compliance thresholds: companies with paid-up capital of INR 50 lakhs "
                            "or more must appoint a whole-time Company Secretary (Section 203), "
                            "and the threshold for CARO applicability is also linked to paid-up "
                            "capital. Include the total paid-up capital as of the financial year end."
                        ),
                    ),
                    _clause(
                        "acc_num_employees",
                        "Number of Employees",
                        "number",
                        "Total number of employees",
                        default=0,
                        learn_more=(
                            "Enter the total number of employees (including contract workers) "
                            "as of the financial year end. This number triggers multiple compliance "
                            "requirements: 10+ employees means you must have a POSH policy and "
                            "Internal Complaints Committee; 20+ employees triggers mandatory PF "
                            "registration; 10+ employees with salary up to INR 21,000/month "
                            "triggers ESI registration. Companies with 1,000+ members must "
                            "provide e-voting at general meetings."
                        ),
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
                        learn_more=(
                            "Enter your company's total annual turnover (gross revenue) for the "
                            "financial year in INR. Turnover is a key threshold for multiple "
                            "compliance obligations: GST registration is mandatory if turnover "
                            "exceeds INR 40 lakhs (INR 20 lakhs for service providers); tax audit "
                            "under Section 44AB of the Income Tax Act is required if turnover "
                            "exceeds INR 1 crore (INR 10 crore if 95%+ transactions are digital); "
                            "and CARO reporting applicability is also linked to turnover. "
                            "Accurate turnover reporting helps determine the correct compliance "
                            "checklist for your company."
                        ),
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
                        learn_more=(
                            "DPIIT (Department for Promotion of Industry and Internal Trade) "
                            "Startup Recognition provides several compliance benefits. Recognized "
                            "startups can self-certify compliance under 6 labour laws and 3 "
                            "environmental laws for 3 years, qualify for tax exemption under "
                            "Section 80-IAC of the Income Tax Act (100% tax holiday for 3 out "
                            "of 10 years), and are exempt from angel tax under Section 56(2)(viib). "
                            "If your startup is DPIIT-recognized, some compliance items in this "
                            "checklist may be simplified."
                        ),
                        india_note=(
                            "DPIIT recognition provides self-certification for labour "
                            "and environment laws, tax holidays under Section 80-IAC, "
                            "and angel tax exemption under Section 56(2)(viib)."
                        ),
                    ),
                    _clause(
                        "acc_has_foreign_investment",
                        "Has Foreign Investment",
                        "toggle",
                        "Whether the company has any foreign investment",
                        default=False,
                        learn_more=(
                            "Enable this if your company has received any investment from "
                            "foreign nationals, NRIs, foreign companies, or foreign funds. "
                            "This includes FDI (Foreign Direct Investment), FVCI investments, "
                            "or any equity held by non-resident Indians. Having foreign "
                            "investment triggers additional compliance requirements under "
                            "FEMA (Foreign Exchange Management Act), including FC-GPR filing "
                            "within 30 days of allotment, annual FLA return to RBI by July 15, "
                            "and sectoral cap compliance. Non-compliance with FEMA can result "
                            "in penalties up to 3 times the amount involved."
                        ),
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
                        learn_more=(
                            "Under Section 173 of the Companies Act 2013, every company must "
                            "hold a minimum of 4 board meetings per year, with at least one "
                            "meeting in each calendar quarter. The maximum gap between two "
                            "consecutive board meetings cannot exceed 120 days. For newly "
                            "incorporated companies, the first board meeting must be held within "
                            "30 days of incorporation. OPCs and small companies can hold just 2 "
                            "board meetings per year with a minimum gap of 90 days."
                        ),
                        warning_condition={
                            "value": 0,
                            "message": (
                                "Zero board meetings is a serious compliance failure. "
                                "Section 173 mandates a minimum of 4 board meetings per "
                                "year. The company and every officer in default can face "
                                "fines of INR 1,00,000 and INR 25,000 respectively."
                            ),
                        },
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
                        learn_more=(
                            "Every company (except OPCs) must hold an Annual General Meeting "
                            "each year. The first AGM must be held within 9 months of the close "
                            "of the first financial year. Subsequent AGMs must be held within 6 "
                            "months of the FY close (i.e., by September 30 for a March 31 FY), "
                            "and the gap between two AGMs cannot exceed 15 months. Missing the "
                            "AGM is a serious compliance failure that attracts penalties and may "
                            "trigger regulatory action by the ROC."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Not holding an AGM is a serious non-compliance under "
                                "Section 96. The company faces a fine of INR 1,00,000 and "
                                "every officer in default faces INR 5,000 for each day of "
                                "default. Apply to ROC for an extension immediately."
                            ),
                        },
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
                        learn_more=(
                            "Enter the date on which the AGM was actually held. This date is "
                            "important because it triggers the deadlines for filing ROC forms: "
                            "AOC-4 (financial statements) must be filed within 30 days of the "
                            "AGM, and MGT-7 (annual return) must be filed within 60 days of the "
                            "AGM. Late filing attracts a penalty of INR 100 per day of delay."
                        ),
                    ),
                    _clause(
                        "acc_statutory_audit_completed",
                        "Statutory Audit Completed",
                        "toggle",
                        "Whether statutory audit is complete",
                        default=True,
                        learn_more=(
                            "The statutory audit is the annual audit of your company's financial "
                            "statements conducted by the appointed statutory auditor, as required "
                            "under Section 143 of the Companies Act 2013. The audit must be "
                            "completed before the AGM because the audited financial statements are "
                            "presented for adoption at the AGM. If the audit is not completed, you "
                            "cannot hold the AGM, which creates a cascading compliance failure. "
                            "Ensure your books of accounts are ready and provided to the auditor "
                            "well in advance."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Incomplete statutory audit will delay your AGM and all "
                                "subsequent ROC filings (AOC-4, MGT-7). This can trigger "
                                "a chain of compliance defaults. Prioritize completing the "
                                "audit immediately."
                            ),
                        },
                    ),
                    _clause(
                        "acc_auditor_appointed",
                        "Auditor Appointed",
                        "toggle",
                        "Whether auditor has been appointed",
                        default=True,
                        learn_more=(
                            "Under Section 139 of the Companies Act 2013, every company must "
                            "have a statutory auditor. The first auditor must be appointed by "
                            "the Board within 30 days of incorporation (they serve until the "
                            "first AGM). Subsequent auditors are appointed at the AGM for a "
                            "5-year term. If no auditor is appointed, the Central Government "
                            "can appoint one, and the company faces a fine of up to INR 1,00,000. "
                            "File Form ADT-1 within 15 days of appointment."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Operating without an appointed auditor is a serious "
                                "compliance breach under Section 139. The Central Government "
                                "may appoint an auditor at the company's cost, and fines of "
                                "up to INR 1,00,000 apply."
                            ),
                        },
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
                        learn_more=(
                            "Every company must file an Income Tax Return (ITR) even if it has "
                            "no income or is in a loss position. Companies file ITR-6 (non-Section "
                            "8) or ITR-7 (Section 8). The due date is October 31 if tax audit is "
                            "required, or July 31 otherwise. Late filing under Section 234F "
                            "attracts a fee of INR 5,000 (INR 1,000 if turnover is below INR 5 "
                            "crore), plus interest on any outstanding tax under Sections 234A, "
                            "234B, and 234C. Filing ITR is also a prerequisite for carrying "
                            "forward losses."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Not filing ITR attracts a late fee under Section 234F, "
                                "interest under Sections 234A/B/C, and you lose the ability "
                                "to carry forward business losses. File immediately to "
                                "minimize penalties."
                            ),
                        },
                        india_note=(
                            "ITR-6 for companies (ITR-7 for Section 8). Due by October 31 "
                            "if tax audit required, July 31 otherwise. Late fee under "
                            "Section 234F of Income Tax Act."
                        ),
                    ),
                    _clause(
                        "acc_gst_compliant",
                        "GST Compliant",
                        "toggle",
                        "All GST returns filed (GSTR-1, 3B, 9, 9C if applicable)",
                        default=True,
                        learn_more=(
                            "GST compliance involves filing multiple returns throughout the year. "
                            "GSTR-1 (outward supplies) is due by the 11th of the following month; "
                            "GSTR-3B (summary return with tax payment) is due by the 20th. Annual "
                            "returns GSTR-9 are due by December 31 of the next financial year, and "
                            "GSTR-9C (reconciliation statement) is required if turnover exceeds "
                            "INR 5 crore. Late filing attracts a fee of INR 50/day (INR 20/day "
                            "for nil returns), capped at INR 10,000 per return."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "GST non-compliance can result in late fees, interest at "
                                "18% per annum on outstanding tax, and even cancellation of "
                                "your GST registration after sustained non-filing."
                            ),
                        },
                        india_note=(
                            "GSTR-1 by 11th monthly, GSTR-3B by 20th monthly. "
                            "GSTR-9 annual return by Dec 31. GSTR-9C if turnover > 5 Cr."
                        ),
                    ),
                    _clause(
                        "acc_tds_compliant",
                        "TDS Compliant",
                        "toggle",
                        "All TDS returns filed (quarterly)",
                        default=True,
                        learn_more=(
                            "Tax Deducted at Source (TDS) must be deducted when making payments "
                            "like salary, rent, professional fees, or contractor payments, and "
                            "deposited to the government by the 7th of the following month. "
                            "Quarterly TDS returns (Form 24Q for salary, 26Q for non-salary) "
                            "must be filed within 31 days of the quarter end. Late filing attracts "
                            "a fee of INR 200/day under Section 234E and a penalty of INR 10,000 "
                            "to INR 1,00,000 under Section 271H. TDS certificates (Form 16/16A) "
                            "must also be issued to deductees."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "TDS non-compliance attracts daily late fees (INR 200/day "
                                "under Section 234E), interest at 1-1.5% per month, and "
                                "potential prosecution. File pending returns immediately."
                            ),
                        },
                        india_note=(
                            "TDS deposit by 7th of following month. Quarterly returns "
                            "within 31 days of quarter end. Late fee INR 200/day u/s 234E."
                        ),
                    ),
                    _clause(
                        "acc_roc_filings_done",
                        "ROC Filings Done",
                        "toggle",
                        "AOC-4/MGT-7 filed",
                        default=False,
                        learn_more=(
                            "ROC (Registrar of Companies) filings are the most critical annual "
                            "filings for a company. AOC-4 contains the financial statements "
                            "(balance sheet, P&L, cash flow) and must be filed within 30 days "
                            "of the AGM under Section 137. MGT-7 is the annual return containing "
                            "shareholder details, director details, and other company information, "
                            "due within 60 days of the AGM under Section 92. Late filing attracts "
                            "a fee of INR 100 per day of delay with no cap, which can add up "
                            "quickly. Persistent default can lead to strike-off proceedings."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Pending ROC filings attract INR 100/day late fee with "
                                "no cap. Persistent default (2+ years) can lead to the "
                                "ROC initiating strike-off proceedings under Section 248 "
                                "and disqualification of directors under Section 164(2)."
                            ),
                        },
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
                        learn_more=(
                            "DIR-3 KYC is an annual KYC (Know Your Customer) filing that every "
                            "person holding a Director Identification Number (DIN) must complete "
                            "by September 30 each year. It requires updating personal details "
                            "like address, contact number, and email on the MCA portal. If a "
                            "director misses the deadline, their DIN is deactivated, which "
                            "prevents them from signing any MCA forms or filings until the KYC "
                            "is completed with a late fee of INR 5,000."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Incomplete DIR-3 KYC will deactivate the DINs of your "
                                "directors, blocking all MCA filings until resolved. A "
                                "late fee of INR 5,000 per director applies."
                            ),
                        },
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
                        learn_more=(
                            "Under Section 405 of the Companies Act 2013 read with the MSME "
                            "Development Act 2006, companies that owe payments to Micro and "
                            "Small Enterprise vendors for more than 45 days must file MSME "
                            "Form 1 with the MCA on a half-yearly basis (by October 31 for "
                            "April-September, and April 30 for October-March). The form "
                            "discloses the amount outstanding, name of vendors, and delay "
                            "period. Non-filing can attract fines up to INR 25,00,000 on "
                            "the company and INR 5,00,000 on officers in default."
                        ),
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
                        learn_more=(
                            "The Prevention of Sexual Harassment (POSH) Act 2013 mandates that "
                            "every employer with 10 or more employees must have a written POSH "
                            "policy, display it prominently in the workplace, and conduct regular "
                            "awareness workshops. The policy must outline the complaint process, "
                            "the role of the Internal Complaints Committee (ICC), and the "
                            "consequences of harassment. Even startups in early stages should "
                            "implement this policy once they cross the 10-employee threshold, "
                            "including contract workers and interns."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "If you have 10 or more employees, not having a POSH policy "
                                "is a legal violation. Penalties include fines up to INR 50,000 "
                                "and cancellation of business registration on repeat offence."
                            ),
                        },
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
                        learn_more=(
                            "Under Section 4 of the POSH Act 2013, every employer with 10 or "
                            "more employees must constitute an Internal Complaints Committee "
                            "(ICC). The ICC must have a presiding officer who is a senior woman "
                            "employee, at least 2 employee members committed to the cause of "
                            "women, and 1 external member from an NGO or association. The ICC "
                            "receives and investigates complaints of sexual harassment at the "
                            "workplace. Not constituting an ICC attracts a fine up to INR 50,000."
                        ),
                        india_note=(
                            "Section 4 of POSH Act 2013 mandates ICC for employers "
                            "with 10+ employees. Must include external member."
                        ),
                    ),
                    _clause(
                        "acc_annual_posh_report",
                        "Annual POSH Report Filed",
                        "toggle",
                        "Annual report filed with District Officer",
                        default=False,
                        depends_on="acc_posh_policy_in_place",
                        learn_more=(
                            "Under Section 21 of the POSH Act 2013, the ICC must prepare an "
                            "annual report and submit it to the employer and the District Officer. "
                            "The report must include the number of complaints received, disposed "
                            "of, and pending, as well as the nature of actions taken. This report "
                            "is due by January 31 of the following year. Even if no complaints "
                            "were received, a nil report must be filed to demonstrate compliance."
                        ),
                        india_note=(
                            "Annual report due by January 31 to District Officer. "
                            "Nil report required even if no complaints received."
                        ),
                    ),
                    _clause(
                        "acc_esi_pf_compliant",
                        "ESI/PF Compliant",
                        "toggle",
                        "ESI/PF filings up to date",
                        default=True,
                        learn_more=(
                            "Provident Fund (PF) under the EPF & MP Act 1952 is mandatory for "
                            "establishments with 20 or more employees. Both employer and employee "
                            "contribute 12% of basic salary each. ESI (Employee State Insurance) "
                            "is mandatory for establishments with 10+ employees where employees "
                            "earn up to INR 21,000/month. Monthly PF filings are due by the 15th "
                            "of the following month, and ESI contributions are due by the 15th. "
                            "Non-compliance can result in damages up to 100% of arrears and even "
                            "imprisonment up to 3 years for persistent default."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "ESI/PF non-compliance is taken very seriously. Penalties "
                                "include damages up to 100% of arrears and imprisonment "
                                "up to 3 years. The EPFO can also attach the company's "
                                "bank accounts and property."
                            ),
                        },
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
                        learn_more=(
                            "Professional Tax is a state-level tax levied on employers and "
                            "employees engaged in any profession, trade, or employment. The "
                            "employer must register, deduct professional tax from employee "
                            "salaries, and remit it to the state government. Rates and due dates "
                            "vary by state -- for example, Karnataka charges INR 200/month for "
                            "salaries above INR 15,000, while Maharashtra has a slab-based "
                            "structure. The maximum professional tax is capped at INR 2,500 per "
                            "annum per Article 276 of the Constitution."
                        ),
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
                        learn_more=(
                            "The Shops and Establishments Act is a state-level law that regulates "
                            "working conditions including working hours, holidays, leave, and "
                            "employment terms. Every business operating from a premises must "
                            "register under this Act with the local municipal authority within "
                            "30 days of commencement. Registration typically requires annual "
                            "renewal (varies by state). Some states like Karnataka now offer "
                            "lifetime registration. Non-renewal can result in fines and even "
                            "closure orders in some states."
                        ),
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
                        learn_more=(
                            "Trademark registrations in India are valid for 10 years from the "
                            "date of application and must be renewed before expiry. Under the "
                            "Trade Marks Act 1999, renewal can be filed up to 6 months before "
                            "expiry or within 6 months after expiry (with a surcharge). If not "
                            "renewed, the mark is removed from the register and you lose legal "
                            "protection against infringement. If you have multiple trademarks, "
                            "check the renewal dates for each one individually."
                        ),
                        india_note=(
                            "Trademark valid for 10 years. Renewal fee is INR 9,000 "
                            "(online). Late renewal surcharge applies for 6 months "
                            "after expiry under Trade Marks Act 1999."
                        ),
                    ),
                    _clause(
                        "acc_data_protection_compliant",
                        "Data Protection Compliant",
                        "toggle",
                        "DPDP Act compliance",
                        default=False,
                        learn_more=(
                            "The Digital Personal Data Protection (DPDP) Act 2023 applies to "
                            "any company that processes personal data of individuals in India. "
                            "Key obligations include obtaining clear consent before processing "
                            "data, maintaining records of data processing activities, providing "
                            "a mechanism for data principals to exercise their rights (access, "
                            "correction, deletion), and notifying the Data Protection Board "
                            "within 72 hours of a data breach. Penalties can be severe -- up to "
                            "INR 250 crore per instance for significant data fiduciaries. Even "
                            "small startups should implement basic data protection practices."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Non-compliance with the DPDP Act 2023 can result in "
                                "penalties up to INR 250 crore. Start with basic measures: "
                                "privacy policy, consent mechanisms, and breach notification "
                                "procedures."
                            ),
                        },
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
                        learn_more=(
                            "The Foreign Liabilities and Assets (FLA) return is an annual filing "
                            "with the Reserve Bank of India (RBI) required for all Indian companies "
                            "that have received foreign direct investment or made overseas "
                            "investments. It must be submitted by July 15 each year through the "
                            "RBI's FLAIR portal. The return captures details of foreign liabilities "
                            "(equity, debt from non-residents) and foreign assets (overseas "
                            "subsidiaries, branches). Non-filing can trigger FEMA penalty "
                            "proceedings, which can be up to 3 times the amount involved."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "Missing the FLA return deadline (July 15) can trigger "
                                "FEMA penalty proceedings. The RBI may also flag your "
                                "company for non-compliance, affecting future foreign "
                                "investment transactions."
                            ),
                        },
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
                        learn_more=(
                            "FC-GPR (Foreign Currency - Gross Provisional Return) must be filed "
                            "with the RBI within 30 days of allotting shares to a foreign investor. "
                            "This is filed through the Single Master Form (SMF) on the RBI's FIRMS "
                            "portal. The form captures details of the foreign investment including "
                            "the investor's identity, amount, valuation, and sector. Late filing "
                            "requires a compounding application to RBI, which involves additional "
                            "fees and delays. If no new foreign investment was received during the "
                            "year, this filing is not required."
                        ),
                        warning_condition={
                            "value": False,
                            "message": (
                                "If foreign investment was received during the year and "
                                "FC-GPR was not filed within 30 days of allotment, you "
                                "will need to apply for compounding with the RBI, which "
                                "involves additional fees and regulatory scrutiny."
                            ),
                        },
                        india_note=(
                            "FC-GPR must be filed within 30 days of share allotment "
                            "to foreign investors via RBI FIRMS portal. Late filing "
                            "requires compounding application."
                        ),
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
