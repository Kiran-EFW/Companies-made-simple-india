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
@media print{{body{{padding:20px;}}@page{{margin:2cm;size:A4;}}}}
</style>
</head><body>
<h1>{title}</h1>
<p class="meta">Date: {date or "________________________"}</p>
{body}
</body></html>'''


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


def render_board_resolution(tpl: dict, config: dict, parties: dict) -> str:
    """Render Board Resolution HTML."""
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

    sections: List[str] = []

    # Meeting header
    sections.append(
        f'<div class="parties">'
        f'<p><strong>Company:</strong> {company}'
        f'{" (CIN: " + cin + ")" if cin else ""}</p>'
        f'<p><strong>Meeting Date:</strong> {meeting_date or "________________________"}</p>'
        f'<p><strong>Meeting Place:</strong> {meeting_place}</p>'
        f'</div>'
    )

    # Directors present
    director_lines = [d.strip() for d in directors.split("\n") if d.strip()] if directors else []
    dir_html = "<ol>" + "".join(f"<li>{d}</li>" for d in director_lines) + "</ol>" if director_lines else "<p>________________________</p>"
    sections.append(
        f'<h2>Directors Present</h2>'
        f'{dir_html}'
    )

    # Quorum
    sections.append(
        '<p class="clause">The Chairperson noted that the requisite quorum was present '
        'and called the meeting to order.</p>'
    )

    # Resolution body — varies by type
    cn = 1
    sections.append(f'<h2>Resolution {cn}: {res_type}</h2>')

    if res_type == "Director Appointment":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT pursuant to Section 152 and other applicable provisions of '
            f'the Companies Act, 2013 and the rules made thereunder, '
            f'<strong>{person_name or "[Director Name]"}</strong>'
            f'{" (DIN: " + person_din + ")" if person_din else ""} '
            f'be and is hereby appointed as a Director of the Company, liable to retire '
            f'by rotation."</p>'
        )
    elif res_type == "Director Resignation Acceptance":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT the resignation of '
            f'<strong>{person_name or "[Director Name]"}</strong>'
            f'{" (DIN: " + person_din + ")" if person_din else ""} '
            f'from the position of Director of the Company be and is hereby accepted '
            f'with effect from {meeting_date or "[Date]"}."</p>'
        )
    elif res_type == "Bank Account Opening":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT a current account be and is hereby authorized to be opened '
            f'with <strong>{bank_name or "[Bank Name]"}</strong> in the name of the Company, '
            f'and that <strong>{signatory}</strong> be and is hereby authorized as the '
            f'authorized signatory for operating the said bank account."</p>'
        )
    elif res_type == "Share Allotment":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT pursuant to Section 62 and other applicable provisions of '
            f'the Companies Act, 2013, the Board hereby approves the allotment of shares '
            f'to <strong>{person_name or "[Allottee Name]"}</strong> for a total '
            f'consideration of INR {amount:,} as detailed herein."</p>'
        )
    elif res_type == "Auditor Appointment":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT pursuant to Section 139 of the Companies Act, 2013, '
            f'<strong>{person_name or "[Auditor Name/Firm]"}</strong> be and is hereby '
            f'appointed as the Statutory Auditor of the Company for the financial year, '
            f'subject to ratification by the members at the ensuing Annual General Meeting."</p>'
        )
    elif res_type == "Registered Office Change":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT pursuant to Section 12 of the Companies Act, 2013, the '
            f'registered office of the Company be and is hereby changed to:</p>'
            f'<p class="clause"><strong>{address or "[New Address]"}</strong></p>'
            f'<p class="clause">with effect from {meeting_date or "[Date]"}."</p>'
        )
    elif res_type == "ESOP Pool Creation":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT pursuant to Section 62(1)(b) of the Companies Act, 2013 '
            f'and Rule 12 of the Companies (Share Capital and Debentures) Rules, 2014, '
            f'the Board hereby approves the creation of an Employee Stock Option Pool '
            f'of INR {amount:,}, subject to approval of the shareholders by special '
            f'resolution."</p>'
        )
    elif res_type == "Authorized Capital Increase":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT subject to the approval of the shareholders by ordinary '
            f'resolution, the authorized share capital of the Company be and is hereby '
            f'proposed to be increased to INR {amount:,} by the creation of additional '
            f'equity shares."</p>'
        )
    elif res_type == "Loan/Borrowing Approval":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT pursuant to Section 179(3)(d) of the Companies Act, 2013, '
            f'the Board hereby approves borrowing of up to INR {amount:,} '
            f'{("from " + bank_name) if bank_name else ""} '
            f'on such terms and conditions as may be agreed upon by '
            f'<strong>{signatory}</strong>."</p>'
        )
    elif res_type == "Related Party Transaction":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT pursuant to Section 188 of the Companies Act, 2013 and '
            f'Rule 15 of the Companies (Meetings of Board and its Powers) Rules, 2014, '
            f'the Board hereby approves the related party transaction with '
            f'<strong>{person_name or "[Related Party Name]"}</strong> '
            f'for an amount of INR {amount:,}, details of which are as follows:</p>'
            f'<p class="clause">{additional or "[Transaction Details]"}</p>'
        )
    else:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"RESOLVED THAT {additional or "[Resolution details to be specified]"}."</p>'
        )

    # Additional details (if not already consumed)
    if additional and res_type != "Related Party Transaction":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Additional details: {additional}</p>'
        )

    # Authorization clause
    cn += 1
    sections.append(
        f'<h2>Resolution {cn}: Authorization</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'"RESOLVED FURTHER THAT <strong>{signatory}</strong> be and is hereby authorized '
        f'to do all such acts, deeds, matters, and things as may be necessary, desirable, '
        f'or expedient to give effect to the above resolution(s), including but not limited '
        f'to signing and filing of all necessary forms and documents with the Registrar of '
        f'Companies and other authorities."</p>'
    )

    # Filing note
    if filing:
        sections.append(
            f'<p class="clause"><em>Note: This resolution requires filing with the '
            f'Ministry of Corporate Affairs (MCA) within the prescribed time limit.</em></p>'
        )

    # Closure
    sections.append(
        '<p class="clause">There being no other business, the meeting was concluded '
        'with a vote of thanks to the Chair.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>For and on behalf of the Board</h2>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{signatory}</strong></p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        '<p><strong>Chairperson</strong></p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Board Resolution \u2014 {res_type}", body, meeting_date
    )


# ======================================================================
# TEMPLATE 10: PRIVACY POLICY (DPDP ACT 2023)
# ======================================================================

def privacy_policy_template() -> dict:
    """Template 10 — Privacy Policy compliant with DPDP Act 2023."""
    return {
        "name": "Privacy Policy (DPDP Act 2023)",
        "description": (
            "Privacy policy compliant with India's Digital Personal Data Protection "
            "Act 2023 (DPDP Act) and IT Act 2000. Essential for any business collecting "
            "user data in India."
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
        f'Protection Act, 2023 ("DPDP Act") and the Information Technology Act, 2000.</p>'
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

    # Section 9 — Children's data
    if children:
        cn += 1
        sections.append(
            f'<h2>{cn}. Children\'s Data</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'We may process personal data of children (persons under 18 years of '
            f'age) only after obtaining verifiable consent from a parent or lawful '
            f'guardian.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'We do not engage in tracking, behavioral monitoring, or targeted '
            f'advertising directed at children, as prohibited under the DPDP Act 2023.</p>'
        )

    # Section 10 — Grievance Officer
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
    )

    # Section 11 — Updates
    cn += 1
    sections.append(
        f'<h2>{cn}. Changes to This Policy</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'We may update this Privacy Policy from time to time. Any material changes '
        f'will be notified to you via email or a prominent notice on our website.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Continued use of our services after changes constitutes acceptance of the '
        f'updated policy.</p>'
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
