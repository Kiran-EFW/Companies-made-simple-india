"""Contract template definitions — Tier 3A (Templates 15–19).

Templates included:
 15. POSH Policy (Prevention of Sexual Harassment)
 16. Convertible Note / iSAFE Agreement
 17. Service Agreement / Master Service Agreement (MSA)
 18. Vendor Agreement
 19. SaaS Agreement / Software License

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
# TEMPLATE 15: POSH POLICY (Prevention of Sexual Harassment)
# ======================================================================

def posh_policy_template() -> dict:
    """Template 15 — POSH Policy compliant with the Sexual Harassment of Women
    at Workplace (Prevention, Prohibition and Redressal) Act, 2013."""
    return {
        "name": "POSH Policy (Prevention of Sexual Harassment)",
        "description": (
            "Comprehensive workplace policy against sexual harassment as mandated "
            "by the POSH Act, 2013. Covers policy scope, Internal Complaints "
            "Committee (ICC) composition, complaint procedures, inquiry process, "
            "and awareness obligations."
        ),
        "category": "Compliance",
        "steps": [
            # Step 1: Policy Overview
            {
                "step_number": 1,
                "title": "Policy Overview",
                "description": "Company details and Internal Complaints Committee composition.",
                "clauses": [
                    _clause(
                        "posh_company_name",
                        "Company Name",
                        "text",
                        "Registered name of the company",
                        learn_more=(
                            "Use the exact legal name as registered with the Ministry of Corporate Affairs (MCA). "
                            "This name will appear on all official POSH policy documents and any filings with the "
                            "District Officer. An incorrect name can create compliance issues if the policy is ever "
                            "challenged or audited."
                        ),
                    ),
                    _clause(
                        "posh_registered_address",
                        "Registered Address",
                        "textarea",
                        "Registered office address of the company",
                        learn_more=(
                            "Enter the registered office address as it appears on your Certificate of Incorporation. "
                            "Under the POSH Act, each office or branch with 10+ employees must have its own ICC. "
                            "If your company operates from multiple locations, you may need separate POSH policies "
                            "or annexures covering each workplace."
                        ),
                    ),
                    _clause(
                        "posh_employee_count",
                        "Employee Count",
                        "number",
                        "Total number of employees in the organization",
                        learn_more=(
                            "Under the POSH Act 2013, every employer with 10 or more "
                            "employees must constitute an Internal Complaints Committee (ICC). "
                            "Employers with fewer than 10 employees are covered by the Local "
                            "Complaints Committee (LCC) constituted by the District Officer."
                        ),
                        india_note=(
                            "Section 4 of the POSH Act mandates constitution of an ICC at "
                            "every workplace with 10 or more employees. Non-compliance can "
                            "attract a penalty of up to INR 50,000."
                        ),
                        min_value=1,
                        warning="ICC is mandatory for organizations with 10+ employees.",
                        warning_condition={"posh_employee_count": {"gte": 10}},
                    ),
                    _clause(
                        "posh_icc_presiding_officer",
                        "ICC Presiding Officer",
                        "text",
                        "Name of the senior woman employee who will preside over the ICC",
                        learn_more=(
                            "The Presiding Officer must be a senior-level woman employee. "
                            "If no such woman is available, the Presiding Officer shall be "
                            "nominated from another office or workplace of the same employer."
                        ),
                        india_note=(
                            "Under Section 4(2)(a) of the POSH Act, the Presiding Officer "
                            "must be a woman employed at a senior level. The term of the "
                            "ICC members shall not exceed three years."
                        ),
                    ),
                    _clause(
                        "posh_icc_members",
                        "ICC Internal Members",
                        "textarea",
                        "Names and designations of at least 2 internal ICC members (one per line)",
                        learn_more=(
                            "The ICC must have at least 2 members from amongst employees "
                            "who are committed to the cause of women or have experience in "
                            "social work or legal knowledge."
                        ),
                    ),
                    _clause(
                        "posh_icc_external_member",
                        "ICC External Member",
                        "text",
                        "Name and organization of the external member from an NGO or association",
                        learn_more=(
                            "The external member brings an independent, unbiased perspective to the ICC. "
                            "This person should be from an NGO or association committed to women's causes, "
                            "or someone with experience in sexual harassment issues. Many companies approach "
                            "local women's organizations, legal aid societies, or social work professionals. "
                            "A common mistake is appointing someone with no relevant experience just to "
                            "fulfill the requirement."
                        ),
                        india_note=(
                            "Section 4(2)(c) requires one external member from an NGO or "
                            "association committed to the cause of women, or a person familiar "
                            "with issues relating to sexual harassment."
                        ),
                    ),
                ],
            },
            # Step 2: Complaint Process
            {
                "step_number": 2,
                "title": "Complaint Process",
                "description": "Procedure for filing complaints, inquiry timelines, and interim relief.",
                "clauses": [
                    _clause(
                        "posh_complaint_timeline",
                        "Complaint Filing Timeline",
                        "dropdown",
                        "Maximum time within which a complaint must be filed after the incident",
                        options=[
                            "3 months from date of incident",
                            "6 months from date of incident",
                            "3 months (extendable by ICC for valid reasons)",
                        ],
                        default="3 months (extendable by ICC for valid reasons)",
                        learn_more=(
                            "Under Section 9 of the POSH Act, the complaint must be filed "
                            "within 3 months of the date of the incident. The ICC may extend "
                            "this period by a further 3 months if satisfied that circumstances "
                            "prevented earlier filing."
                        ),
                        india_note=(
                            "The statutory time limit under Section 9 is 3 months, extendable "
                            "by 3 months by the ICC. The complaint must be in writing; if the "
                            "complainant cannot write, the Presiding Officer shall render "
                            "reasonable assistance."
                        ),
                        common_choice_label="3 months (extendable) as per POSH Act",
                    ),
                    _clause(
                        "posh_inquiry_completion",
                        "Inquiry Completion Timeline",
                        "dropdown",
                        "Time within which the inquiry must be completed",
                        options=[
                            "90 days from date of complaint",
                            "60 days from date of complaint",
                        ],
                        default="90 days from date of complaint",
                        learn_more=(
                            "The inquiry timeline determines how quickly the ICC must investigate and reach "
                            "a conclusion. While 90 days is the statutory maximum under Section 11(4) of the "
                            "POSH Act, choosing 60 days demonstrates a stronger commitment to swift resolution. "
                            "A faster timeline benefits the complainant but requires the ICC to be well-organized "
                            "and responsive. Most startups should stick with 90 days to allow adequate time for "
                            "thorough investigation."
                        ),
                        india_note=(
                            "Section 11(4) of the POSH Act requires the inquiry to be "
                            "completed within 90 days."
                        ),
                        common_choice_label="90 days as per POSH Act",
                    ),
                    _clause(
                        "posh_conciliation_offered",
                        "Conciliation Option",
                        "toggle",
                        "Whether the company offers conciliation before formal inquiry",
                        learn_more=(
                            "Section 10 allows the ICC to attempt conciliation before "
                            "initiating an inquiry, if requested by the complainant. "
                            "No monetary settlement shall be the basis of conciliation."
                        ),
                        pros=["Can resolve matters faster", "Less adversarial process"],
                        cons=["May not be suitable for severe cases", "Monetary settlement is not permitted"],
                    ),
                    _clause(
                        "posh_interim_relief",
                        "Interim Relief Measures",
                        "multi_select",
                        "Interim relief measures available during inquiry",
                        options=[
                            "Transfer of complainant or respondent",
                            "Grant of leave to complainant (up to 3 months)",
                            "Restraining respondent from reporting on complainant",
                            "Restraining respondent from contacting complainant",
                        ],
                        learn_more=(
                            "Interim relief measures protect the complainant during the pendency of the inquiry. "
                            "These are temporary measures, not punishments. The ICC can recommend any combination "
                            "of these measures based on the circumstances. It is best practice to include all "
                            "available measures in your policy so the ICC has flexibility. The leave granted under "
                            "Section 12 is in addition to the complainant's regular leave entitlement."
                        ),
                        india_note=(
                            "Section 12 of the POSH Act empowers the ICC to recommend "
                            "interim relief including transfer, leave (up to 3 months, "
                            "in addition to regular leave), and restraining orders."
                        ),
                        common_choice_label="Include all interim measures",
                    ),
                ],
            },
            # Step 3: Penalties & Awareness
            {
                "step_number": 3,
                "title": "Penalties & Awareness",
                "description": "Penalty framework, mandatory training, and annual reporting.",
                "clauses": [
                    _clause(
                        "posh_penalty_actions",
                        "Penalty Actions",
                        "multi_select",
                        "Disciplinary actions that may be taken upon substantiated complaints",
                        options=[
                            "Written warning",
                            "Suspension",
                            "Withholding of promotion",
                            "Withholding of pay rise or increments",
                            "Termination of employment",
                            "Deduction from salary (compensation to complainant)",
                            "Counseling",
                            "Community service",
                        ],
                        learn_more=(
                            "Section 13 of the POSH Act provides that the employer shall "
                            "act upon the recommendation of the ICC within 60 days. Actions "
                            "may be taken in accordance with service rules or as prescribed."
                        ),
                        india_note=(
                            "Under Section 13(3)(ii), the ICC may also recommend deduction "
                            "of an appropriate sum from the salary of the respondent as "
                            "compensation to the aggrieved woman."
                        ),
                    ),
                    _clause(
                        "posh_training_frequency",
                        "Training Frequency",
                        "dropdown",
                        "How often POSH awareness training is conducted",
                        options=[
                            "Annually",
                            "Semi-annually",
                            "Quarterly",
                            "At onboarding + annually",
                        ],
                        default="At onboarding + annually",
                        learn_more=(
                            "Regular awareness programmes are mandated under Section 19(c) "
                            "of the POSH Act. Training should cover what constitutes sexual "
                            "harassment, complaint mechanisms, and consequences."
                        ),
                        common_choice_label="At onboarding + annually",
                    ),
                    _clause(
                        "posh_false_complaint_action",
                        "Action for False/Malicious Complaints",
                        "dropdown",
                        "Action to be taken if a complaint is found to be false or malicious",
                        options=[
                            "Disciplinary action as per service rules",
                            "Warning letter",
                            "As recommended by ICC",
                        ],
                        default="As recommended by ICC",
                        learn_more=(
                            "This clause addresses situations where the ICC finds a complaint was made with "
                            "malicious intent or is provably false. It is crucial to understand that the mere "
                            "inability to prove a complaint does NOT make it false or malicious — this is a very "
                            "important distinction under Section 14. Choosing 'As recommended by ICC' gives the "
                            "committee discretion to decide appropriate action based on severity, which is the "
                            "safest option for most companies."
                        ),
                        india_note=(
                            "Section 14 of the POSH Act provides that if the ICC concludes "
                            "that the complaint was made with malicious intent or is false, "
                            "it may recommend action against the complainant. However, the "
                            "mere inability to substantiate a complaint does not attract "
                            "action for false complaint."
                        ),
                    ),
                    _clause(
                        "posh_annual_report",
                        "Annual Report Filing",
                        "toggle",
                        "Whether the company will file the annual report with the District Officer",
                        default=True,
                        learn_more=(
                            "Annual report filing is mandatory under Section 21 of the POSH Act. The report "
                            "must contain details of complaints received, resolved, and pending. Even if your "
                            "company had zero complaints during the year, you must still file the report. "
                            "Non-filing can attract penalties and shows non-compliance during any audit or "
                            "inspection. This should always be enabled."
                        ),
                        warning_condition={"posh_annual_report": {"eq": False}},
                        warning="Annual report filing is mandatory under Section 21 of the POSH Act.",
                        india_note=(
                            "Section 21 of the POSH Act mandates that the ICC shall prepare "
                            "an annual report and submit it to the employer and District "
                            "Officer. The report must include number of complaints received, "
                            "disposed of, pending, and time taken for disposal."
                        ),
                    ),
                ],
            },
        ],
    }


def render_posh_policy(tpl: dict, config: dict, parties: dict) -> str:
    """Render POSH Policy HTML."""
    company = config.get("posh_company_name", "[Company Name]")
    address = config.get("posh_registered_address", "[Registered Address]")
    emp_count = config.get("posh_employee_count", 0)
    presiding = config.get("posh_icc_presiding_officer", "[Presiding Officer]")
    members_raw = config.get("posh_icc_members", "")
    external = config.get("posh_icc_external_member", "[External Member]")
    complaint_tl = config.get("posh_complaint_timeline", "3 months (extendable by ICC for valid reasons)")
    inquiry_tl = config.get("posh_inquiry_completion", "90 days from date of complaint")
    conciliation = config.get("posh_conciliation_offered", False)
    interim = config.get("posh_interim_relief", [])
    penalties = config.get("posh_penalty_actions", [])
    training = config.get("posh_training_frequency", "At onboarding + annually")
    false_action = config.get("posh_false_complaint_action", "As recommended by ICC")
    annual_report = config.get("posh_annual_report", True)

    members = [m.strip() for m in members_raw.split("\n") if m.strip()] if members_raw else []

    def _list_html(items: Any) -> str:
        if isinstance(items, list) and items:
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
        return f"<p>{items}</p>" if items else "<p>N/A</p>"

    sections: List[str] = []
    cn = 0

    # Section 1 — Preamble
    cn += 1
    sections.append(
        f'<h2>{cn}. Preamble</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>{company}</strong>, having its registered office at {address}, '
        f'is committed to providing a safe, respectful, and harassment-free workplace '
        f'for all employees, regardless of gender.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'This Policy is framed in compliance with the Sexual Harassment of Women at '
        f'Workplace (Prevention, Prohibition and Redressal) Act, 2013 ("POSH Act") '
        f'and the rules made thereunder.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The Company has {emp_count} employees as of the date of this policy.</p>'
    )

    # Section 2 — Scope
    cn += 1
    sections.append(
        f'<h2>{cn}. Scope & Applicability</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This policy applies to all employees (permanent, temporary, contractual, '
        f'trainees, and apprentices), as well as visitors, clients, and any person '
        f'at the workplace as defined under Section 2(o) of the POSH Act.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'"Workplace" includes the registered office, branch offices, factory premises, '
        f'any place visited by employees arising out of employment, and transportation '
        f'provided by the employer.</p>'
    )

    # Section 3 — Definition of Sexual Harassment
    cn += 1
    sections.append(
        f'<h2>{cn}. Definition of Sexual Harassment</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'As per Section 2(n) of the POSH Act, sexual harassment includes any one or '
        f'more of the following unwelcome acts or behaviour: (i) physical contact and '
        f'advances; (ii) a demand or request for sexual favours; (iii) making sexually '
        f'coloured remarks; (iv) showing pornography; (v) any other unwelcome physical, '
        f'verbal or non-verbal conduct of sexual nature.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The following circumstances, if they occur or are present in relation to any '
        f'act of sexual harassment, may also amount to sexual harassment: implied or '
        f'explicit promise of preferential treatment, implied or explicit threat of '
        f'detrimental treatment, interference with work, creating an intimidating or '
        f'hostile work environment, and humiliating treatment likely to affect health '
        f'or safety.</p>'
    )

    # Section 4 — Internal Complaints Committee
    cn += 1
    member_list = "<ol>" + "".join(f"<li>{m}</li>" for m in members) + "</ol>" if members else "<p>________________________</p>"
    sections.append(
        f'<h2>{cn}. Internal Complaints Committee (ICC)</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'In accordance with Section 4 of the POSH Act, the Company hereby constitutes '
        f'an Internal Complaints Committee with the following members:</p>'
        f'<div class="parties">'
        f'<p><strong>Presiding Officer:</strong> {presiding}</p>'
        f'<p><strong>Internal Members:</strong></p>{member_list}'
        f'<p><strong>External Member:</strong> {external}</p>'
        f'</div>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The term of the ICC members shall be three years from the date of their '
        f'nomination. At least half the members shall be women.</p>'
    )

    # Section 5 — Complaint Procedure
    cn += 1
    sections.append(
        f'<h2>{cn}. Complaint Procedure</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Any aggrieved person may file a written complaint with the ICC within '
        f'<strong>{complaint_tl}</strong> of the date of the incident.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'If the aggrieved person is unable to make a complaint in writing, the '
        f'Presiding Officer or any ICC member shall render reasonable assistance.</p>'
    )

    # Section 6 — Conciliation (conditional)
    if conciliation:
        cn += 1
        sections.append(
            f'<h2>{cn}. Conciliation</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Before initiating an inquiry, the ICC may, at the request of the complainant, '
            f'take steps to settle the matter through conciliation as per Section 10 of '
            f'the POSH Act.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'No monetary settlement shall be made as a basis of conciliation.</p>'
        )

    # Section 7 — Inquiry Process
    cn += 1
    sections.append(
        f'<h2>{cn}. Inquiry Process</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The ICC shall conduct the inquiry in accordance with the principles of natural '
        f'justice, giving both parties an opportunity to be heard.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The inquiry shall be completed within <strong>{inquiry_tl}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'During the pendency of the inquiry, the ICC may recommend the following '
        f'interim relief measures:</p>'
        f'{_list_html(interim)}'
    )

    # Section 8 — Penalties
    cn += 1
    sections.append(
        f'<h2>{cn}. Action on Substantiated Complaints</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Upon completion of the inquiry, if the allegation is proved, the ICC shall '
        f'recommend any of the following actions to the employer:</p>'
        f'{_list_html(penalties)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The employer shall act upon the ICC recommendation within 60 days of receipt.</p>'
    )

    # Section 9 — False Complaints
    cn += 1
    sections.append(
        f'<h2>{cn}. False or Malicious Complaints</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'If the ICC concludes that the allegation was made with malicious intent or '
        f'the complaint was false, it may recommend: <strong>{false_action}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The mere inability to substantiate a complaint or provide adequate proof '
        f'shall not attract action for false complaint.</p>'
    )

    # Section 10 — Training & Awareness
    cn += 1
    sections.append(
        f'<h2>{cn}. Training & Awareness</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Company shall conduct POSH awareness training with the following frequency: '
        f'<strong>{training}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Training shall cover the definition of sexual harassment, complaint mechanisms, '
        f'rights and responsibilities, and consequences of violations.</p>'
    )

    # Section 11 — Annual Report (conditional)
    if annual_report:
        cn += 1
        sections.append(
            f'<h2>{cn}. Annual Report</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The ICC shall prepare an annual report as required under Section 21 of '
            f'the POSH Act and submit it to the employer and the District Officer.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The annual report shall include the number of complaints received, disposed '
            f'of, pending, and the time taken for disposal.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The employer shall include this information in the annual report of the '
            f'Company under Section 22 of the POSH Act.</p>'
        )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Authorized by</h2>'
        '<p class="clause">This Policy has been approved and adopted by the Board of '
        'Directors / Management of the Company.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{company}</strong></p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{presiding}</strong></p>'
        '<p>Presiding Officer, Internal Complaints Committee</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"POSH Policy \u2014 {company}", body
    )


# ======================================================================
# TEMPLATE 16: CONVERTIBLE NOTE / iSAFE AGREEMENT
# ======================================================================

def convertible_note_template() -> dict:
    """Template 16 — Convertible Note / iSAFE (Indian Simple Agreement for
    Future Equity) for early-stage fundraising."""
    return {
        "name": "Convertible Note / iSAFE Agreement",
        "description": (
            "A convertible instrument for early-stage fundraising based on the iSAFE "
            "(Indian Simple Agreement for Future Equity) framework. Defines investment "
            "amount, valuation cap, discount, conversion triggers, and maturity terms "
            "compliant with Companies Act 2013."
        ),
        "category": "Fundraising",
        "steps": [
            # Step 1: Parties & Investment
            {
                "step_number": 1,
                "title": "Parties & Investment",
                "description": "Company and investor details along with investment amount.",
                "clauses": [
                    _clause(
                        "cn_company_name",
                        "Company Name",
                        "text",
                        "Registered name of the company issuing the note",
                        learn_more=(
                            "Use the exact registered name of your company as it appears on your Certificate "
                            "of Incorporation issued by the Registrar of Companies (ROC). This name will appear "
                            "on MCA filings including the PAS-3 form that must be filed within 30 days of allotment. "
                            "Any mismatch can cause filing rejections."
                        ),
                    ),
                    _clause(
                        "cn_company_cin",
                        "Company CIN",
                        "text",
                        "Corporate Identification Number of the company",
                        required=False,
                        learn_more=(
                            "The CIN is a unique 21-digit alphanumeric identifier assigned by MCA to every "
                            "company registered in India. You can find it on your Certificate of Incorporation "
                            "or by searching the MCA portal. While optional here, including it adds credibility "
                            "and makes the agreement easier to enforce. Investors typically expect to see this."
                        ),
                    ),
                    _clause(
                        "cn_company_address",
                        "Company Registered Address",
                        "textarea",
                        "Registered office address of the company",
                        learn_more=(
                            "Enter the registered office address as it appears in your MCA records. This is "
                            "the address where legal notices can be served. If your operating address differs "
                            "from your registered address, use the registered one here. Investors may conduct "
                            "due diligence to verify this address matches official records."
                        ),
                    ),
                    _clause(
                        "cn_investor_name",
                        "Investor Name",
                        "text",
                        "Full legal name of the investor (individual or entity)",
                        learn_more=(
                            "Enter the investor's full legal name exactly as it appears on their PAN card "
                            "(for individuals) or Certificate of Incorporation (for entities). This name will "
                            "be used in the company's register of members upon conversion and in RBI filings "
                            "for foreign investors. Using an incorrect name can cause delays in share allotment "
                            "and regulatory filings."
                        ),
                    ),
                    _clause(
                        "cn_investor_type",
                        "Investor Type",
                        "dropdown",
                        "Type of investor",
                        options=[
                            "Indian Resident Individual",
                            "Indian Entity (Company/LLP/Fund)",
                            "NRI",
                            "Foreign Individual",
                            "Foreign Entity / VC Fund",
                        ],
                        learn_more=(
                            "The investor type determines which regulatory framework applies. Indian residents "
                            "and entities have simpler compliance requirements. NRIs, foreign individuals, and "
                            "foreign entities trigger FEMA compliance, RBI filing requirements, and a minimum "
                            "investment threshold of INR 25 lakhs per convertible note. If you choose a foreign "
                            "investor type, budget extra time and legal fees for regulatory filings."
                        ),
                        india_note=(
                            "Foreign investors must comply with FEMA (Foreign Exchange "
                            "Management Act) regulations and RBI pricing guidelines. "
                            "Convertible notes from foreign investors require prior filing "
                            "with RBI and compliance with FDI policy. Minimum investment "
                            "of INR 25 lakhs per convertible note for foreign investors."
                        ),
                        warning="Foreign investors require FEMA compliance and RBI filings.",
                        warning_condition={"cn_investor_type": {"in": ["Foreign Individual", "Foreign Entity / VC Fund", "NRI"]}},
                    ),
                    _clause(
                        "cn_investment_amount",
                        "Investment Amount (INR)",
                        "number",
                        "Total investment amount in Indian Rupees",
                        min_value=1,
                        learn_more=(
                            "This is the total amount the investor will invest in exchange for the convertible "
                            "note. For foreign investors, the minimum is INR 25 lakhs per note as per RBI "
                            "regulations. The company must pass a special resolution under Section 42 of the "
                            "Companies Act and file Form PAS-3 with MCA within 30 days of allotment. A common "
                            "founder mistake is not accounting for the dilution this amount will cause upon conversion."
                        ),
                        india_note=(
                            "Under Companies Act 2013, Section 42 governs private placement "
                            "of securities. The company must pass a special resolution and "
                            "file PAS-3 with MCA within 30 days of allotment."
                        ),
                    ),
                    _clause(
                        "cn_execution_date",
                        "Execution Date",
                        "date",
                        "Date of execution of this agreement",
                        learn_more=(
                            "The execution date is when both parties sign the agreement. Interest (if any) "
                            "starts accruing from the date the investment amount is actually received by the "
                            "company, not necessarily the execution date. The maturity period also begins from "
                            "this date. Ensure funds are received promptly after execution to avoid mismatches."
                        ),
                    ),
                ],
            },
            # Step 2: Conversion Terms
            {
                "step_number": 2,
                "title": "Conversion Terms",
                "description": "Valuation cap, discount rate, conversion triggers, and interest.",
                "clauses": [
                    _clause(
                        "cn_valuation_cap",
                        "Valuation Cap (INR)",
                        "number",
                        "Maximum pre-money valuation at which the note converts to equity",
                        learn_more=(
                            "The valuation cap sets the maximum company valuation at which "
                            "the investor's note converts. If the company raises at a higher "
                            "valuation, the investor still converts at the cap, getting more "
                            "shares for their investment."
                        ),
                        pros=["Protects investor from dilution at high valuations"],
                        cons=["May limit founder upside if set too low"],
                        min_value=1,
                    ),
                    _clause(
                        "cn_discount_rate",
                        "Discount Rate (%)",
                        "number",
                        "Discount to the price per share in the qualifying round",
                        default=20,
                        learn_more=(
                            "The discount gives the investor a reduced price per share "
                            "compared to new investors in the qualifying round. A 20% "
                            "discount means the note holder pays 80% of the price."
                        ),
                        min_value=0,
                        max_value=50,
                        common_choice_label="20% is market standard",
                    ),
                    _clause(
                        "cn_conversion_trigger",
                        "Conversion Trigger Event",
                        "dropdown",
                        "Event that triggers automatic conversion of the note",
                        options=[
                            "Qualified Financing Round (equity raise above threshold)",
                            "Any Equity Financing Round",
                            "IPO or Change of Control",
                            "Maturity Date",
                        ],
                        default="Qualified Financing Round (equity raise above threshold)",
                        learn_more=(
                            "The conversion trigger defines when the note automatically "
                            "converts into equity. Most commonly, this is a qualified "
                            "financing round where the company raises above a minimum "
                            "threshold amount."
                        ),
                    ),
                    _clause(
                        "cn_qualifying_amount",
                        "Qualifying Round Minimum (INR)",
                        "number",
                        "Minimum amount of the equity round to trigger conversion",
                        required=False,
                        depends_on="cn_conversion_trigger",
                        learn_more=(
                            "The qualifying amount sets the minimum size of a future equity round that triggers "
                            "automatic conversion. Setting this too high may mean the note never converts and "
                            "reaches maturity instead. Setting it too low means even a small funding round triggers "
                            "conversion. Common practice is to set this at 2-3x the note amount. For example, if "
                            "the note is INR 50 lakhs, a qualifying round minimum of INR 1-1.5 Cr is typical."
                        ),
                    ),
                    _clause(
                        "cn_interest_rate",
                        "Interest Rate (% per annum)",
                        "number",
                        "Annual simple interest rate on the principal amount",
                        default=0,
                        learn_more=(
                            "Some convertible notes carry interest that accrues and converts "
                            "to equity along with the principal. iSAFEs typically carry 0% "
                            "interest."
                        ),
                        pros=["Compensates investor for time value of money"],
                        cons=["Increases effective dilution for founders"],
                        min_value=0,
                        max_value=18,
                        common_choice_label="0% for iSAFE; 6-8% for convertible notes",
                    ),
                ],
            },
            # Step 3: Other Terms
            {
                "step_number": 3,
                "title": "Other Terms",
                "description": "Maturity, information rights, and governing law.",
                "clauses": [
                    _clause(
                        "cn_maturity_months",
                        "Maturity Period (months)",
                        "number",
                        "Number of months until the note matures if no conversion event occurs",
                        default=24,
                        learn_more=(
                            "If no conversion trigger occurs before maturity, the investor "
                            "may have the right to convert at a pre-agreed valuation, or "
                            "request repayment of the principal plus accrued interest."
                        ),
                        min_value=6,
                        max_value=60,
                        common_choice_label="18-24 months is typical",
                    ),
                    _clause(
                        "cn_maturity_action",
                        "Action on Maturity",
                        "dropdown",
                        "What happens if the note reaches maturity without a conversion event",
                        options=[
                            "Convert at valuation cap",
                            "Repay principal + interest",
                            "Extend maturity by mutual agreement",
                            "Convert at fair market value (independent valuation)",
                        ],
                        default="Convert at valuation cap",
                        learn_more=(
                            "If no qualifying round happens before the note matures, this clause determines "
                            "the outcome. Converting at the valuation cap is founder-friendly as it avoids a "
                            "cash repayment obligation. Repaying principal + interest protects the investor but "
                            "can strain a startup's cash. Extending by mutual agreement is flexible but uncertain. "
                            "Fair market valuation requires an independent valuer which adds cost and may result "
                            "in a valuation neither party likes."
                        ),
                        pros=["Conversion at cap: No cash outflow for company", "FMV: Fair to both parties"],
                        cons=["Repayment: Cash burden on startup", "Extension: Uncertainty for investor"],
                        warning_condition={"cn_maturity_action": {"eq": "Repay principal + interest"}},
                        warning="Repayment obligation at maturity can strain startup cash flow.",
                    ),
                    _clause(
                        "cn_information_rights",
                        "Information Rights",
                        "toggle",
                        "Whether the investor receives periodic financial updates",
                        default=True,
                        learn_more=(
                            "Information rights typically include quarterly financial "
                            "statements, annual audited accounts, and notice of any material "
                            "events affecting the company."
                        ),
                    ),
                    _clause(
                        "cn_most_favoured_nation",
                        "Most Favoured Nation (MFN) Clause",
                        "toggle",
                        "Whether the investor gets the benefit of more favourable terms in subsequent notes",
                        learn_more=(
                            "An MFN clause ensures that if the company issues subsequent "
                            "convertible notes with better terms (higher discount, lower cap), "
                            "this investor's terms automatically adjust to match."
                        ),
                        pros=["Protects early investors"],
                        cons=["Adds complexity to cap table management"],
                    ),
                    _clause(
                        "cn_governing_law",
                        "Governing Law & Jurisdiction",
                        "dropdown",
                        "Governing law and courts with jurisdiction",
                        options=[
                            "Indian law, courts at New Delhi",
                            "Indian law, courts at Mumbai",
                            "Indian law, courts at Bengaluru",
                            "Indian law, courts at company registered office",
                        ],
                        default="Indian law, courts at company registered office",
                        learn_more=(
                            "The governing law determines which legal framework interprets the agreement, and "
                            "jurisdiction determines where disputes are heard. Choosing courts at your company's "
                            "registered office is most convenient for the company. Investors sometimes negotiate "
                            "for a neutral or more commercially active jurisdiction like Mumbai or Delhi. "
                            "Convertible notes involving foreign investors must always be governed by Indian law "
                            "per FEMA requirements."
                        ),
                    ),
                ],
            },
        ],
    }


def render_convertible_note(tpl: dict, config: dict, parties: dict) -> str:
    """Render Convertible Note / iSAFE Agreement HTML."""
    company = config.get("cn_company_name", "[Company Name]")
    cin = config.get("cn_company_cin", "")
    company_addr = config.get("cn_company_address", "[Company Address]")
    investor = config.get("cn_investor_name", "[Investor Name]")
    investor_type = config.get("cn_investor_type", "Indian Resident Individual")
    amount = config.get("cn_investment_amount", 0)
    exec_date = config.get("cn_execution_date", "")
    val_cap = config.get("cn_valuation_cap", 0)
    discount = config.get("cn_discount_rate", 20)
    trigger = config.get("cn_conversion_trigger", "Qualified Financing Round (equity raise above threshold)")
    qual_amount = config.get("cn_qualifying_amount", 0)
    interest = config.get("cn_interest_rate", 0)
    maturity = config.get("cn_maturity_months", 24)
    maturity_action = config.get("cn_maturity_action", "Convert at valuation cap")
    info_rights = config.get("cn_information_rights", True)
    mfn = config.get("cn_most_favoured_nation", False)
    gov_law = config.get("cn_governing_law", "Indian law, courts at company registered office")

    sections: List[str] = []
    cn = 0

    # Parties
    sections.append(
        f'<div class="parties">'
        f'<p>This Convertible Note Agreement ("Agreement") is entered into on '
        f'{exec_date or "________________________"} by and between:</p>'
        f'<p><strong>Company:</strong> {company}'
        f'{" (CIN: " + cin + ")" if cin else ""}, having its registered office at '
        f'{company_addr} (hereinafter the "Company")</p>'
        f'<p><strong>Investor:</strong> {investor} ({investor_type}) '
        f'(hereinafter the "Investor")</p>'
        f'</div>'
    )

    # Section 1 — Investment
    cn += 1
    sections.append(
        f'<h2>{cn}. Investment</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Investor agrees to invest a total sum of INR {amount:,} '
        f'("Investment Amount") in the Company by way of a convertible note.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Investment Amount shall be remitted to the Company\'s designated bank '
        f'account within 5 (five) business days of execution of this Agreement.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This convertible note is issued in compliance with Section 42 of the '
        f'Companies Act, 2013 (Private Placement) and applicable rules thereunder.</p>'
    )

    # Section 2 — Conversion Terms
    cn += 1
    sections.append(
        f'<h2>{cn}. Conversion Terms</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Valuation Cap:</strong> The note shall convert at a pre-money '
        f'valuation not exceeding INR {val_cap:,} ("Valuation Cap").</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Discount:</strong> The Investor shall receive a {discount}% discount '
        f'to the price per share paid by investors in the Conversion Event.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The conversion price shall be the lower of: (a) the Valuation Cap divided by '
        f'the fully diluted share capital; or (b) the price per share in the Conversion '
        f'Event less the {discount}% discount.</p>'
    )

    # Section 3 — Conversion Trigger
    cn += 1
    trigger_text = trigger
    if qual_amount and "Qualified" in trigger:
        trigger_text += f" (minimum INR {qual_amount:,})"
    sections.append(
        f'<h2>{cn}. Conversion Event</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The note shall automatically convert upon the occurrence of: '
        f'<strong>{trigger_text}</strong> ("Conversion Event").</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Upon a Conversion Event, the outstanding principal together with any accrued '
        f'interest shall convert into equity shares of the Company at the conversion '
        f'price determined under Clause 2.</p>'
    )

    # Section 4 — Interest
    cn += 1
    sections.append(
        f'<h2>{cn}. Interest</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Investment Amount shall accrue simple interest at the rate of '
        f'<strong>{interest}% per annum</strong> from the date of receipt by the Company.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Accrued interest shall not be paid in cash but shall convert into equity '
        f'shares along with the principal upon a Conversion Event.</p>'
    )

    # Section 5 — Maturity
    cn += 1
    sections.append(
        f'<h2>{cn}. Maturity</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The maturity date of this note shall be <strong>{maturity} months</strong> '
        f'from the date of investment ("Maturity Date").</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'If no Conversion Event occurs prior to the Maturity Date, the following '
        f'action shall apply: <strong>{maturity_action}</strong>.</p>'
    )

    # Section 6 — Information Rights
    if info_rights:
        cn += 1
        sections.append(
            f'<h2>{cn}. Information Rights</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Company shall provide the Investor with: (a) quarterly unaudited '
            f'financial statements within 30 days of each quarter end; (b) annual '
            f'audited financial statements within 90 days of the financial year end; '
            f'and (c) prompt notice of any material adverse events.</p>'
        )

    # Section 7 — MFN (conditional)
    if mfn:
        cn += 1
        sections.append(
            f'<h2>{cn}. Most Favoured Nation</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'If the Company issues any subsequent convertible notes or similar '
            f'instruments with terms more favourable to the holder thereof (including '
            f'a lower valuation cap or higher discount), the terms of this Agreement '
            f'shall automatically be amended to incorporate such more favourable terms.</p>'
        )

    # Section 8 — Representations & Warranties
    cn += 1
    sections.append(
        f'<h2>{cn}. Representations & Warranties</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Company represents that it is duly incorporated under the Companies Act, '
        f'2013 and has the corporate power and authority to enter into this Agreement.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Investor represents that the investment is being made with lawful funds '
        f'and in compliance with applicable laws including FEMA regulations (if '
        f'applicable).</p>'
    )

    # Section 9 — Governing Law
    cn += 1
    sections.append(
        f'<h2>{cn}. Governing Law & Dispute Resolution</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be governed by and construed in accordance with '
        f'<strong>{gov_law}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Any dispute arising out of or in connection with this Agreement shall first '
        f'be attempted to be resolved through good-faith negotiation. If unresolved '
        f'within 30 days, either party may pursue arbitration under the Arbitration '
        f'and Conciliation Act, 1996.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Company:</strong> {company}</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Investor:</strong> {investor}</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Convertible Note Agreement \u2014 {company}", body, exec_date
    )


# ======================================================================
# TEMPLATE 17: SERVICE AGREEMENT / MASTER SERVICE AGREEMENT (MSA)
# ======================================================================

def msa_template() -> dict:
    """Template 17 — Master Service Agreement for B2B engagements."""
    return {
        "name": "Service Agreement / Master Service Agreement (MSA)",
        "description": (
            "A comprehensive Master Service Agreement for B2B service engagements. "
            "Covers scope of services, SLAs, payment terms, IP ownership, "
            "confidentiality, liability caps, and termination provisions."
        ),
        "category": "Business Operations",
        "steps": [
            # Step 1: Parties & Scope
            {
                "step_number": 1,
                "title": "Parties & Scope",
                "description": "Client and service provider details, scope of services, and SLAs.",
                "clauses": [
                    _clause(
                        "msa_client_name",
                        "Client Name",
                        "text",
                        "Full legal name of the client",
                        learn_more=(
                            "Use the exact legal name of the client entity — the party receiving the services. "
                            "For companies, this is the name on their Certificate of Incorporation. For LLPs, "
                            "use the name as registered with MCA. Getting the legal name wrong can make contract "
                            "enforcement difficult if disputes arise."
                        ),
                    ),
                    _clause(
                        "msa_client_address",
                        "Client Address",
                        "textarea",
                        "Registered or principal business address of the client",
                        learn_more=(
                            "The client's address is important for determining jurisdiction and serving notices. "
                            "Use the registered office address for companies or the principal place of business "
                            "for proprietorships. This address will be referenced in the governing law clause "
                            "if you select jurisdiction at the client's location."
                        ),
                    ),
                    _clause(
                        "msa_provider_name",
                        "Service Provider Name",
                        "text",
                        "Full legal name of the service provider",
                        learn_more=(
                            "This is your company's legal name if you are the service provider, or the vendor's "
                            "name if you are the client. The service provider is the party delivering the services. "
                            "Ensure this matches official registration documents to avoid enforceability issues."
                        ),
                    ),
                    _clause(
                        "msa_provider_address",
                        "Service Provider Address",
                        "textarea",
                        "Registered or principal business address of the provider",
                        learn_more=(
                            "Enter the service provider's registered or principal business address. This address "
                            "is used for sending official notices and communications under the agreement. If the "
                            "provider is a startup operating from a co-working space, use the registered office "
                            "address for legal certainty."
                        ),
                    ),
                    _clause(
                        "msa_service_description",
                        "Description of Services",
                        "textarea",
                        "Detailed description of services to be provided",
                        learn_more=(
                            "A clear scope of services helps prevent scope creep and disputes. "
                            "Include deliverables, milestones, and acceptance criteria where "
                            "applicable. Additional services can be covered through Statements "
                            "of Work (SOWs) under this MSA."
                        ),
                    ),
                    _clause(
                        "msa_sla_terms",
                        "Service Level Agreement (SLA)",
                        "textarea",
                        "Key SLA metrics and targets (response times, uptime, quality benchmarks)",
                        required=False,
                        learn_more=(
                            "SLAs define measurable performance standards. Common metrics "
                            "include response time, resolution time, uptime percentage, "
                            "defect rates, and customer satisfaction scores."
                        ),
                    ),
                    _clause(
                        "msa_effective_date",
                        "Effective Date",
                        "date",
                        "Date from which this agreement takes effect",
                        learn_more=(
                            "The effective date is when obligations under the MSA begin. It may differ from the "
                            "signing date if you want the agreement to start on a future date. SLAs, payment "
                            "obligations, and the initial term all run from this date. A common mistake is "
                            "starting work before the effective date, which leaves the work unprotected by the "
                            "agreement's terms."
                        ),
                    ),
                ],
            },
            # Step 2: Payment
            {
                "step_number": 2,
                "title": "Payment",
                "description": "Fee structure, payment terms, and penalty for delayed payment.",
                "clauses": [
                    _clause(
                        "msa_fee_structure",
                        "Fee Structure",
                        "dropdown",
                        "How the service provider will be compensated",
                        options=[
                            "Fixed fee per project/SOW",
                            "Time & material (hourly/daily rate)",
                            "Monthly retainer",
                            "Milestone-based payments",
                            "Hybrid (retainer + variable)",
                        ],
                        learn_more=(
                            "Choose a fee structure that aligns with the nature of work. "
                            "Fixed fees work for well-defined projects. T&M is better for "
                            "evolving scope. Retainers suit ongoing engagements."
                        ),
                        pros=["Fixed fee: Budget certainty", "T&M: Flexibility for scope changes"],
                        cons=["Fixed fee: Risk of scope creep", "T&M: Budget unpredictability"],
                    ),
                    _clause(
                        "msa_fee_amount",
                        "Fee Amount / Rate (INR)",
                        "text",
                        "Amount or rate as applicable (e.g., INR 5,00,000 per month or INR 3,000/hour)",
                        learn_more=(
                            "Specify the fee clearly with the unit — whether it is per month, per hour, per "
                            "project, or per milestone. Ambiguity in fee amounts is the top cause of B2B payment "
                            "disputes. If using time-and-material, specify the rate card for different resource "
                            "levels. Remember that GST (typically 18%) will be charged additionally unless "
                            "explicitly included in the quoted fee."
                        ),
                    ),
                    _clause(
                        "msa_payment_terms",
                        "Payment Terms",
                        "dropdown",
                        "Number of days within which invoices must be paid",
                        options=[
                            "Net 15 days",
                            "Net 30 days",
                            "Net 45 days",
                            "Net 60 days",
                            "Advance payment",
                        ],
                        default="Net 30 days",
                        learn_more=(
                            "Payment terms determine when the client must pay after receiving an invoice. "
                            "'Net 30' means payment is due within 30 days. If you are the provider, shorter "
                            "terms improve cash flow. If you are the client, longer terms give you more "
                            "working capital flexibility. Note: If the provider is an MSME, payment must be "
                            "within 45 days under the MSMED Act regardless of what is agreed here."
                        ),
                        pros=["Shorter terms: Better cash flow for provider", "Longer terms: Working capital flexibility for client"],
                        cons=["Too short: Client may struggle to pay on time", "Too long: Cash flow strain on provider"],
                        common_choice_label="Net 30 is market standard",
                    ),
                    _clause(
                        "msa_late_payment_interest",
                        "Late Payment Interest (% per month)",
                        "number",
                        "Interest charged on overdue payments",
                        default=2,
                        min_value=0,
                        max_value=5,
                        learn_more=(
                            "Late payment interest incentivizes timely payment and compensates the provider for "
                            "delayed cash flow. The standard rate is 1.5-2% per month (18-24% annualized). "
                            "Setting it too high (above 3%) may be challenged as penal or unconscionable. "
                            "Setting it at 0% removes any incentive for timely payment. This interest is separate "
                            "from the MSMED Act's mandatory compound interest of 3x bank rate for MSME vendors."
                        ),
                    ),
                    _clause(
                        "msa_gst_handling",
                        "GST Handling",
                        "dropdown",
                        "How GST is handled on invoices",
                        options=[
                            "GST included in quoted fees",
                            "GST charged additionally at applicable rate",
                            "Reverse charge mechanism",
                        ],
                        default="GST charged additionally at applicable rate",
                        learn_more=(
                            "GST handling determines who bears the tax burden. If GST is included in fees, the "
                            "provider absorbs the tax and the effective revenue is lower. If charged additionally, "
                            "the client pays the base fee plus 18% GST on top. Reverse charge applies in specific "
                            "cases like imports of services. The most common and transparent approach is 'GST charged "
                            "additionally' which lets both parties clearly see the tax component."
                        ),
                        india_note=(
                            "Under GST law, services attract 18% GST (most professional "
                            "services). The provider must issue a GST-compliant tax invoice. "
                            "TDS under Section 194J (professional/technical services at 10%) "
                            "or 194C (contractual services at 1%/2%) of the Income Tax Act "
                            "may apply depending on the nature of services."
                        ),
                    ),
                ],
            },
            # Step 3: IP & Confidentiality
            {
                "step_number": 3,
                "title": "IP & Confidentiality",
                "description": "Intellectual property ownership, confidentiality obligations, and data protection.",
                "clauses": [
                    _clause(
                        "msa_ip_ownership",
                        "IP Ownership",
                        "dropdown",
                        "Who owns the intellectual property created during the engagement",
                        options=[
                            "Client owns all deliverable IP",
                            "Provider retains IP, client gets perpetual license",
                            "Joint ownership",
                            "Provider owns, client gets exclusive license for engagement scope",
                        ],
                        learn_more=(
                            "IP ownership is a critical commercial term. Work-for-hire does "
                            "not automatically apply in India — IP ownership must be "
                            "explicitly assigned via written agreement."
                        ),
                        india_note=(
                            "Under the Indian Copyright Act 1957, the first owner of "
                            "copyright in a work made in the course of employment is the "
                            "employer (Section 17). However, for independent contractors, "
                            "the creator retains ownership unless expressly assigned."
                        ),
                        common_choice_label="Client owns all deliverable IP",
                    ),
                    _clause(
                        "msa_pre_existing_ip",
                        "Pre-existing IP Treatment",
                        "dropdown",
                        "How pre-existing IP of the provider is handled",
                        options=[
                            "Provider retains ownership, grants usage license",
                            "Excluded from scope entirely",
                            "Licensed to client for deliverable use only",
                        ],
                        default="Provider retains ownership, grants usage license",
                        learn_more=(
                            "Pre-existing IP refers to tools, frameworks, code libraries, or methodologies the "
                            "provider already owns before the engagement. It would be unfair to transfer ownership "
                            "of these to the client. The standard approach is for the provider to retain ownership "
                            "but grant the client a license to use it as part of the deliverables. If you exclude "
                            "pre-existing IP entirely, the client may not be able to use the deliverables properly."
                        ),
                        pros=["Retains provider's competitive advantage", "Client gets usage rights for deliverables"],
                        cons=["Client may be dependent on provider for updates to pre-existing IP components"],
                    ),
                    _clause(
                        "msa_confidentiality_period",
                        "Confidentiality Period",
                        "dropdown",
                        "How long confidentiality obligations survive after termination",
                        options=[
                            "2 years after termination",
                            "3 years after termination",
                            "5 years after termination",
                            "Perpetual (no expiry)",
                        ],
                        default="3 years after termination",
                        learn_more=(
                            "The confidentiality survival period determines how long parties must keep each "
                            "other's information secret after the agreement ends. Shorter periods (2 years) are "
                            "easier to agree to but may not protect highly sensitive data. Perpetual confidentiality "
                            "is strongest but harder to enforce and monitor. Three years is the industry standard "
                            "for most B2B agreements and balances protection with practicality."
                        ),
                        common_choice_label="3 years is typical for B2B",
                    ),
                    _clause(
                        "msa_data_protection",
                        "Data Protection Obligations",
                        "toggle",
                        "Whether the agreement includes data protection / DPDP Act compliance obligations",
                        default=True,
                        learn_more=(
                            "Data protection obligations ensure that any personal data shared between parties "
                            "during the engagement is handled in compliance with the Digital Personal Data "
                            "Protection Act, 2023 (DPDP Act). If either party processes personal data of "
                            "customers, employees, or users, this should be enabled. Disabling it when personal "
                            "data is involved creates legal risk and potential penalties under the DPDP Act, "
                            "which can go up to INR 250 Crores for significant breaches."
                        ),
                        warning="Disable only if no personal data is shared during the engagement.",
                        warning_condition={"msa_data_protection": {"eq": False}},
                        india_note=(
                            "If personal data is shared during the engagement, both parties "
                            "must comply with the Digital Personal Data Protection Act, 2023 "
                            "and the IT Act, 2000. A Data Processing Addendum may be required."
                        ),
                    ),
                ],
            },
            # Step 4: Liability & Termination
            {
                "step_number": 4,
                "title": "Liability & Termination",
                "description": "Liability caps, indemnity, termination rights, and dispute resolution.",
                "clauses": [
                    _clause(
                        "msa_liability_cap",
                        "Liability Cap",
                        "dropdown",
                        "Maximum aggregate liability under this agreement",
                        options=[
                            "Limited to fees paid in last 12 months",
                            "Limited to total contract value",
                            "Limited to fees paid in last 6 months",
                            "2x fees paid in last 12 months",
                            "Unlimited",
                        ],
                        default="Limited to fees paid in last 12 months",
                        learn_more=(
                            "A liability cap limits the maximum amount either party can "
                            "claim from the other. This is typically set as a multiple of "
                            "fees paid. Carve-outs (exceptions) usually apply for "
                            "confidentiality breaches, IP infringement, and wilful misconduct."
                        ),
                        common_choice_label="12-month fees is standard",
                    ),
                    _clause(
                        "msa_indemnity",
                        "Indemnification",
                        "dropdown",
                        "Indemnification obligations of the parties",
                        options=[
                            "Mutual indemnification",
                            "Provider indemnifies client only",
                            "Client indemnifies provider only",
                            "No indemnification",
                        ],
                        default="Mutual indemnification",
                        learn_more=(
                            "Indemnification means one party agrees to compensate the other for losses caused "
                            "by their breach. Mutual indemnification is fairest — both parties cover each other "
                            "for their respective breaches. 'Provider indemnifies client only' is common in "
                            "client-drafted agreements but leaves the provider exposed. 'No indemnification' is "
                            "risky as neither party has recourse if the other's actions cause losses. As a "
                            "startup, push for mutual indemnification to ensure balanced protection."
                        ),
                        pros=["Mutual: Balanced and fair", "One-sided: Protects the specified party strongly"],
                        cons=["One-sided: Unfair to the non-protected party", "No indemnification: Neither party has recourse"],
                        warning="No indemnification leaves both parties without recourse for losses.",
                        warning_condition={"msa_indemnity": {"eq": "No indemnification"}},
                    ),
                    _clause(
                        "msa_term_months",
                        "Initial Term (months)",
                        "number",
                        "Duration of the initial term of the agreement",
                        default=12,
                        min_value=1,
                        max_value=60,
                        learn_more=(
                            "The initial term is how long the MSA is valid before it either expires or renews. "
                            "Twelve months is standard for most B2B engagements. Shorter terms (3-6 months) suit "
                            "pilot projects, while longer terms (24-36 months) are common for enterprise contracts. "
                            "The term affects pricing negotiations — providers often offer better rates for longer "
                            "commitments. Consider including an auto-renewal clause to avoid gaps in service."
                        ),
                    ),
                    _clause(
                        "msa_termination_notice",
                        "Termination Notice Period",
                        "dropdown",
                        "Advance notice required for termination without cause",
                        options=[
                            "30 days written notice",
                            "60 days written notice",
                            "90 days written notice",
                        ],
                        default="30 days written notice",
                        learn_more=(
                            "The termination notice period gives both parties time to plan for the end of the "
                            "engagement. Thirty days is standard and allows for transition of work. Ninety days "
                            "is better for complex engagements where transition needs more time. A common mistake "
                            "is setting very short notice periods that do not allow sufficient time for knowledge "
                            "transfer and finding a replacement provider."
                        ),
                    ),
                    _clause(
                        "msa_dispute_resolution",
                        "Dispute Resolution",
                        "dropdown",
                        "Mechanism for resolving disputes",
                        options=[
                            "Arbitration (sole arbitrator) under Arbitration Act 1996",
                            "Arbitration (3-member tribunal) under Arbitration Act 1996",
                            "Mediation followed by arbitration",
                            "Courts of competent jurisdiction",
                        ],
                        default="Arbitration (sole arbitrator) under Arbitration Act 1996",
                        learn_more=(
                            "Dispute resolution determines how disagreements are handled. Arbitration is "
                            "faster and more confidential than court litigation in India. A sole arbitrator "
                            "is cheaper and quicker, while a 3-member tribunal is suitable for high-value "
                            "disputes. Mediation followed by arbitration encourages amicable settlement first. "
                            "Courts should be a last resort due to delays in the Indian judicial system. "
                            "Most B2B contracts in India use arbitration for its efficiency and enforceability."
                        ),
                        india_note=(
                            "Arbitration under the Arbitration and Conciliation Act, 1996 "
                            "is the preferred dispute resolution mechanism in Indian B2B "
                            "contracts. Seat of arbitration determines the procedural law."
                        ),
                    ),
                    _clause(
                        "msa_governing_law_city",
                        "Governing Law & Jurisdiction City",
                        "text",
                        "City whose courts / arbitration seat will have jurisdiction",
                        default="Bengaluru",
                        learn_more=(
                            "The jurisdiction city determines where arbitration proceedings will take place or "
                            "which courts will hear disputes. Choose a city that is convenient for your company. "
                            "Major commercial hubs like Mumbai, Delhi, and Bengaluru have experienced commercial "
                            "courts and arbitration centres. The seat of arbitration also determines the procedural "
                            "law applicable to the arbitration proceedings."
                        ),
                    ),
                ],
            },
        ],
    }


def render_msa(tpl: dict, config: dict, parties: dict) -> str:
    """Render Master Service Agreement HTML."""
    client = config.get("msa_client_name", "[Client Name]")
    client_addr = config.get("msa_client_address", "[Client Address]")
    provider = config.get("msa_provider_name", "[Service Provider]")
    provider_addr = config.get("msa_provider_address", "[Provider Address]")
    services = config.get("msa_service_description", "[Description of Services]")
    sla = config.get("msa_sla_terms", "")
    eff_date = config.get("msa_effective_date", "")
    fee_struct = config.get("msa_fee_structure", "Fixed fee per project/SOW")
    fee_amount = config.get("msa_fee_amount", "[Fee Amount]")
    pay_terms = config.get("msa_payment_terms", "Net 30 days")
    late_int = config.get("msa_late_payment_interest", 2)
    gst = config.get("msa_gst_handling", "GST charged additionally at applicable rate")
    ip_own = config.get("msa_ip_ownership", "Client owns all deliverable IP")
    pre_ip = config.get("msa_pre_existing_ip", "Provider retains ownership, grants usage license")
    conf_period = config.get("msa_confidentiality_period", "3 years after termination")
    data_prot = config.get("msa_data_protection", True)
    liab_cap = config.get("msa_liability_cap", "Limited to fees paid in last 12 months")
    indem = config.get("msa_indemnity", "Mutual indemnification")
    term = config.get("msa_term_months", 12)
    term_notice = config.get("msa_termination_notice", "30 days written notice")
    dispute = config.get("msa_dispute_resolution", "Arbitration (sole arbitrator) under Arbitration Act 1996")
    gov_city = config.get("msa_governing_law_city", "Bengaluru")

    sections: List[str] = []
    cn = 0

    # Parties
    sections.append(
        f'<div class="parties">'
        f'<p>This Master Service Agreement ("Agreement") is entered into on '
        f'{eff_date or "________________________"} by and between:</p>'
        f'<p><strong>Client:</strong> {client}, having its address at {client_addr} '
        f'(hereinafter the "Client")</p>'
        f'<p><strong>Service Provider:</strong> {provider}, having its address at '
        f'{provider_addr} (hereinafter the "Provider")</p>'
        f'</div>'
    )

    # Section 1 — Scope of Services
    cn += 1
    sections.append(
        f'<h2>{cn}. Scope of Services</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Provider shall provide the following services to the Client:</p>'
        f'<p class="clause">{services}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Additional services shall be governed by individual Statements of Work '
        f'("SOWs") executed under this MSA. Each SOW shall incorporate the terms of '
        f'this Agreement.</p>'
    )

    # Section 2 — SLA (conditional)
    if sla:
        cn += 1
        sections.append(
            f'<h2>{cn}. Service Level Agreement</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Provider shall meet the following service levels:</p>'
            f'<p class="clause">{sla}</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Failure to meet agreed SLAs may result in service credits or other '
            f'remedies as specified in the applicable SOW.</p>'
        )

    # Section 3 — Fees & Payment
    cn += 1
    sections.append(
        f'<h2>{cn}. Fees & Payment</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Fee Structure:</strong> {fee_struct}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Fee Amount / Rate:</strong> {fee_amount}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'<strong>Payment Terms:</strong> All invoices shall be payable within '
        f'<strong>{pay_terms}</strong> of receipt of a valid invoice.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'<strong>Late Payment:</strong> Overdue amounts shall attract interest at the '
        f'rate of {late_int}% per month.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.5</span> '
        f'<strong>GST:</strong> {gst}. The Provider shall issue GST-compliant tax '
        f'invoices. TDS as applicable under the Income Tax Act shall be deducted by '
        f'the Client.</p>'
    )

    # Section 4 — Intellectual Property
    cn += 1
    sections.append(
        f'<h2>{cn}. Intellectual Property</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Deliverable IP:</strong> {ip_own}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Pre-existing IP:</strong> {pre_ip}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The Provider warrants that the deliverables shall not infringe upon the '
        f'intellectual property rights of any third party.</p>'
    )

    # Section 5 — Confidentiality
    cn += 1
    sections.append(
        f'<h2>{cn}. Confidentiality</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Each party shall maintain the confidentiality of all Confidential Information '
        f'received from the other party and shall not disclose it to any third party '
        f'without prior written consent.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Confidentiality obligations shall survive termination of this Agreement for '
        f'<strong>{conf_period}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Exceptions: Information that is publicly available, independently developed, '
        f'rightfully received from a third party, or required to be disclosed by law.</p>'
    )

    # Section 6 — Data Protection (conditional)
    if data_prot:
        cn += 1
        sections.append(
            f'<h2>{cn}. Data Protection</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Both parties shall comply with the Digital Personal Data Protection Act, '
            f'2023, the Information Technology Act, 2000, and applicable rules.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Provider shall process personal data only as instructed by the Client '
            f'and shall implement appropriate technical and organizational security '
            f'measures.</p>'
        )

    # Section 7 — Liability
    cn += 1
    sections.append(
        f'<h2>{cn}. Limitation of Liability</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The aggregate liability of either party under this Agreement shall be '
        f'<strong>{liab_cap}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Neither party shall be liable for any indirect, incidental, consequential, '
        f'special, or punitive damages.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The above limitations shall not apply to breaches of confidentiality, IP '
        f'infringement, or wilful misconduct.</p>'
    )

    # Section 8 — Indemnification
    cn += 1
    sections.append(
        f'<h2>{cn}. Indemnification</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Indemnification: <strong>{indem}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The indemnifying party shall defend, indemnify, and hold harmless the other '
        f'party from any claims, damages, losses, or expenses arising from breach of '
        f'representations, warranties, or obligations under this Agreement.</p>'
    )

    # Section 9 — Term & Termination
    cn += 1
    sections.append(
        f'<h2>{cn}. Term & Termination</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall commence on the Effective Date and continue for an '
        f'initial term of <strong>{term} months</strong>, unless terminated earlier.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Either party may terminate this Agreement by providing '
        f'<strong>{term_notice}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Either party may terminate immediately upon material breach by the other '
        f'party that remains uncured for 15 days after written notice.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'Upon termination, the Provider shall deliver all completed work, return '
        f'confidential information, and the Client shall pay for services rendered '
        f'up to the date of termination.</p>'
    )

    # Section 10 — Dispute Resolution
    cn += 1
    sections.append(
        f'<h2>{cn}. Dispute Resolution & Governing Law</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be governed by the laws of India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Dispute resolution: <strong>{dispute}</strong>. The seat of arbitration '
        f'(if applicable) shall be <strong>{gov_city}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The courts at {gov_city} shall have exclusive jurisdiction over any matters '
        f'not subject to arbitration.</p>'
    )

    # Section 11 — General
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement, together with any SOWs, constitutes the entire agreement '
        f'between the parties and supersedes all prior negotiations and agreements.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Neither party may assign this Agreement without the prior written consent '
        f'of the other party.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Amendments to this Agreement shall be in writing and signed by both parties.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Client:</strong> {client}</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Service Provider:</strong> {provider}</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Master Service Agreement \u2014 {client} & {provider}", body, eff_date
    )


# ======================================================================
# TEMPLATE 18: VENDOR AGREEMENT
# ======================================================================

def vendor_agreement_template() -> dict:
    """Template 18 — Vendor Agreement for procurement of goods or services."""
    return {
        "name": "Vendor Agreement",
        "description": (
            "Agreement between a company and its vendor/supplier for procurement "
            "of goods or services. Covers vendor details, delivery terms, pricing, "
            "payment, warranties, quality standards, and MSMED Act compliance."
        ),
        "category": "Business Operations",
        "steps": [
            # Step 1: Vendor Details
            {
                "step_number": 1,
                "title": "Vendor Details",
                "description": "Parties, goods/services to be supplied, and delivery terms.",
                "clauses": [
                    _clause(
                        "va_company_name",
                        "Company Name (Purchaser)",
                        "text",
                        "Registered name of the purchasing company",
                        learn_more=(
                            "Enter the full legal name of the company purchasing goods or services. This is "
                            "the party that will receive the supply and make payments. If the vendor is an "
                            "MSME, the purchaser has additional obligations under the MSMED Act including "
                            "filing half-yearly returns on the MSME Samadhaan portal."
                        ),
                    ),
                    _clause(
                        "va_company_address",
                        "Company Address",
                        "textarea",
                        "Registered address of the purchasing company",
                        learn_more=(
                            "This is the registered office address of the company placing the purchase order. "
                            "Delivery instructions may differ from this address — the delivery location is "
                            "specified separately in individual purchase orders. This address is used for "
                            "sending invoices, notices, and official correspondence."
                        ),
                    ),
                    _clause(
                        "va_vendor_name",
                        "Vendor Name",
                        "text",
                        "Full legal name of the vendor/supplier",
                        learn_more=(
                            "Enter the vendor's exact legal name as it appears on their GST registration "
                            "certificate or Certificate of Incorporation. This must match for GST Input Tax "
                            "Credit claims. If the vendor name on invoices does not match this agreement, "
                            "you may face issues during GST reconciliation and audits."
                        ),
                    ),
                    _clause(
                        "va_vendor_address",
                        "Vendor Address",
                        "textarea",
                        "Registered or principal business address of the vendor",
                        learn_more=(
                            "The vendor's registered or principal business address. This is important for "
                            "determining the applicable GST rate (intra-state CGST+SGST vs inter-state IGST) "
                            "and for serving legal notices. Verify this address matches the vendor's GST "
                            "registration to avoid ITC claim issues."
                        ),
                    ),
                    _clause(
                        "va_supply_type",
                        "Type of Supply",
                        "dropdown",
                        "Whether the vendor supplies goods, services, or both",
                        options=[
                            "Goods only",
                            "Services only",
                            "Goods and Services",
                        ],
                        learn_more=(
                            "The type of supply determines which legal frameworks apply. Goods are governed by "
                            "the Sale of Goods Act, 1930, while services fall under the Indian Contract Act. "
                            "GST rates also differ — goods have varying rates (5%, 12%, 18%, 28%) while services "
                            "typically attract 18%. TDS rates also differ: 1%/2% under Section 194C for "
                            "contracts vs 10% under Section 194J for professional services."
                        ),
                    ),
                    _clause(
                        "va_supply_description",
                        "Description of Goods/Services",
                        "textarea",
                        "Detailed description of the goods or services to be supplied",
                        learn_more=(
                            "Be as specific as possible — include product specifications, HSN/SAC codes for GST "
                            "purposes, quantities, quality grades, and brand/model numbers where applicable. "
                            "A vague description leads to disputes over quality and quantity. For services, "
                            "describe the scope, methodology, and expected outcomes. This description forms "
                            "the basis for acceptance and warranty claims."
                        ),
                    ),
                    _clause(
                        "va_delivery_terms",
                        "Delivery Terms",
                        "dropdown",
                        "Delivery terms and risk transfer point",
                        options=[
                            "Ex-works (vendor premises)",
                            "Delivered at purchaser premises (DAP)",
                            "Free on Board (FOB)",
                            "Cost, Insurance & Freight (CIF)",
                            "As specified in Purchase Order",
                        ],
                        default="Delivered at purchaser premises (DAP)",
                        learn_more=(
                            "Delivery terms define when risk and responsibility transfer from vendor to buyer. "
                            "Ex-works means the buyer bears all risk from the vendor's premises. DAP means the "
                            "vendor is responsible until delivery at the buyer's premises. FOB and CIF are "
                            "typically used for imports/exports. For domestic purchases, DAP is most common as "
                            "it keeps the vendor responsible for transit risk, damage, and insurance."
                        ),
                        pros=["DAP: Less risk for buyer", "Ex-works: Lower price from vendor"],
                        cons=["DAP: Higher vendor pricing", "Ex-works: Buyer manages logistics and risk"],
                    ),
                    _clause(
                        "va_effective_date",
                        "Effective Date",
                        "date",
                        "Date from which this agreement takes effect",
                        learn_more=(
                            "The effective date is when the vendor agreement becomes operative. Purchase orders "
                            "placed before this date are not governed by this agreement. If you have an existing "
                            "vendor relationship, set the effective date to cover ongoing and future orders. The "
                            "agreement term, pricing, and warranty obligations all start from this date."
                        ),
                    ),
                ],
            },
            # Step 2: Payment & Warranties
            {
                "step_number": 2,
                "title": "Payment & Warranties",
                "description": "Pricing, payment terms, warranties, and quality obligations.",
                "clauses": [
                    _clause(
                        "va_pricing_model",
                        "Pricing Model",
                        "dropdown",
                        "How the vendor prices its supplies",
                        options=[
                            "Fixed price per unit",
                            "Fixed price per order / PO",
                            "Rate card / schedule of rates",
                            "Cost plus margin",
                        ],
                        learn_more=(
                            "The pricing model affects your procurement costs and budgeting. Fixed price per "
                            "unit is best for standard products — you know exactly what each unit costs. "
                            "Rate card works when you order different items at different rates. Cost plus margin "
                            "is transparent but requires you to verify the vendor's actual costs. For startups "
                            "buying regularly, negotiate a fixed price per unit with volume discounts."
                        ),
                        pros=["Fixed price: Budget certainty", "Cost plus: Transparency"],
                        cons=["Fixed price: No benefit if costs drop", "Cost plus: Requires cost verification"],
                    ),
                    _clause(
                        "va_payment_terms",
                        "Payment Terms",
                        "dropdown",
                        "Payment timeline after receipt of goods/services and invoice",
                        options=[
                            "Net 15 days",
                            "Net 30 days",
                            "Net 45 days",
                            "Net 60 days",
                            "50% advance, 50% on delivery",
                        ],
                        default="Net 30 days",
                        learn_more=(
                            "Payment terms set when the vendor gets paid after delivering goods/services and "
                            "submitting an invoice. For MSME vendors, there is a hard legal limit of 45 days "
                            "under the MSMED Act — choosing Net 60 for an MSME vendor would violate the law. "
                            "The 50% advance option protects the vendor's cash flow but means the buyer pays "
                            "before receiving the full delivery, which carries risk."
                        ),
                        warning="Exceeding 45-day payment terms for MSME vendors violates the MSMED Act.",
                        warning_condition={"va_payment_terms": {"in": ["Net 60 days"]}},
                        india_note=(
                            "Under the MSMED Act, 2006, buyers must make payment to Micro "
                            "and Small Enterprise vendors within 45 days of acceptance of "
                            "goods/services. Delayed payments attract compound interest at "
                            "3x the bank rate notified by RBI."
                        ),
                        common_choice_label="Net 30 (but max 45 days for MSME vendors)",
                    ),
                    _clause(
                        "va_vendor_msme_status",
                        "Vendor MSME Status",
                        "dropdown",
                        "Whether the vendor is registered as an MSME",
                        options=[
                            "Micro Enterprise",
                            "Small Enterprise",
                            "Medium Enterprise",
                            "Not an MSME",
                        ],
                        learn_more=(
                            "MSME classification is based on the vendor's investment in plant/machinery and "
                            "annual turnover. If the vendor is a Micro or Small Enterprise, the MSMED Act "
                            "mandates payment within 45 days and imposes compound interest (3x RBI bank rate) "
                            "for delayed payments. This interest is NOT tax-deductible for the buyer. Ask the "
                            "vendor for their Udyam Registration Certificate to verify their MSME status. "
                            "Many startups unknowingly violate this law and face claims on the Samadhaan portal."
                        ),
                        india_note=(
                            "If the vendor is a Micro or Small Enterprise under the MSMED "
                            "Act, 2006, payment must be made within 45 days. The buyer must "
                            "file a half-yearly return with the MSME Samadhaan portal. "
                            "Interest on delayed payment is not tax deductible for the buyer."
                        ),
                        warning="Payment to MSME vendors must be within 45 days under MSMED Act.",
                        warning_condition={"va_vendor_msme_status": {"in": ["Micro Enterprise", "Small Enterprise"]}},
                    ),
                    _clause(
                        "va_warranty_period",
                        "Warranty Period",
                        "dropdown",
                        "Duration of warranty on goods/services supplied",
                        options=[
                            "No warranty",
                            "3 months",
                            "6 months",
                            "12 months",
                            "24 months",
                            "As per manufacturer warranty",
                        ],
                        default="12 months",
                        learn_more=(
                            "The warranty period defines how long the vendor guarantees their goods/services "
                            "to be free from defects. During this period, the vendor must repair or replace "
                            "defective goods at no cost. Choosing 'No warranty' is risky — you have no recourse "
                            "if goods are defective after delivery. 12 months is standard for most goods. For "
                            "high-value capital equipment, negotiate 24 months. For consumables, 3-6 months "
                            "may be appropriate."
                        ),
                        warning="No warranty leaves you without recourse for defective goods.",
                        warning_condition={"va_warranty_period": {"eq": "No warranty"}},
                    ),
                    _clause(
                        "va_quality_standards",
                        "Quality Standards",
                        "textarea",
                        "Quality certifications or standards the vendor must comply with (e.g., ISO, BIS)",
                        required=False,
                        learn_more=(
                            "Specifying quality standards ensures consistency. Common Indian "
                            "standards include BIS (Bureau of Indian Standards), ISO "
                            "certifications, and FSSAI (for food products)."
                        ),
                    ),
                    _clause(
                        "va_gst_handling",
                        "GST & Tax Handling",
                        "dropdown",
                        "How GST and taxes are handled",
                        options=[
                            "GST included in price",
                            "GST charged extra at applicable rate",
                            "Reverse charge applicable",
                        ],
                        default="GST charged extra at applicable rate",
                        learn_more=(
                            "GST handling is crucial for proper tax compliance and claiming Input Tax Credit "
                            "(ITC). If GST is included in the price, the vendor absorbs it, which may mean "
                            "the vendor has priced it in already. If GST is charged extra, you pay more but "
                            "can claim ITC to offset your own GST liability. Reverse charge applies for specific "
                            "notified categories of services. Always insist on GST-compliant invoices with the "
                            "vendor's valid GSTIN to claim ITC."
                        ),
                        india_note=(
                            "The purchaser should verify the vendor's GSTIN and ensure "
                            "GST-compliant invoices are received to claim Input Tax Credit "
                            "(ITC). TDS under Section 194C (1% for individuals/HUF, 2% for "
                            "others) applies to contractual payments exceeding INR 30,000 "
                            "per transaction or INR 1,00,000 per annum."
                        ),
                    ),
                ],
            },
            # Step 3: Termination & Liability
            {
                "step_number": 3,
                "title": "Termination & Liability",
                "description": "Agreement term, termination provisions, liability cap, and governing law.",
                "clauses": [
                    _clause(
                        "va_term_months",
                        "Agreement Term (months)",
                        "number",
                        "Duration of the vendor agreement",
                        default=12,
                        min_value=1,
                        max_value=60,
                        learn_more=(
                            "The agreement term sets how long this vendor relationship is formally governed. "
                            "Twelve months is standard for most vendor agreements. Shorter terms (3-6 months) "
                            "are good for trial relationships or seasonal supplies. Longer terms (24-36 months) "
                            "help secure pricing and supply assurance but reduce flexibility if a better vendor "
                            "emerges. Consider pairing longer terms with auto-renewal for continuity."
                        ),
                    ),
                    _clause(
                        "va_auto_renewal",
                        "Auto-Renewal",
                        "toggle",
                        "Whether the agreement automatically renews at the end of the term",
                        default=False,
                        learn_more=(
                            "Auto-renewal means the agreement continues for another term of equal duration "
                            "unless either party gives written notice of non-renewal before the current term "
                            "ends. This ensures continuity of supply but means you must actively decide to "
                            "stop — forgetting to give notice will lock you in. If disabled, the agreement "
                            "simply expires and you must negotiate a new one, which creates a gap in coverage."
                        ),
                        pros=["Continuity of supply relationship"],
                        cons=["May lock in unfavourable terms"],
                    ),
                    _clause(
                        "va_termination_notice",
                        "Termination Notice Period",
                        "dropdown",
                        "Advance notice required for termination without cause",
                        options=[
                            "15 days written notice",
                            "30 days written notice",
                            "60 days written notice",
                            "90 days written notice",
                        ],
                        default="30 days written notice",
                        learn_more=(
                            "The notice period gives both parties time to wind down the relationship gracefully. "
                            "For critical supply relationships, choose a longer period (60-90 days) so the buyer "
                            "can find an alternative vendor. For non-critical supplies, 15-30 days is sufficient. "
                            "Note that termination for cause (material breach) usually has a separate, shorter "
                            "cure period and does not require this notice."
                        ),
                    ),
                    _clause(
                        "va_liability_cap",
                        "Liability Cap",
                        "dropdown",
                        "Maximum aggregate liability of the vendor",
                        options=[
                            "Limited to value of the specific purchase order",
                            "Limited to total payments in last 12 months",
                            "Limited to total contract value",
                            "Unlimited",
                        ],
                        default="Limited to total payments in last 12 months",
                        learn_more=(
                            "The liability cap sets the maximum amount you can recover from the vendor if "
                            "something goes wrong. 'Limited to 12-month payments' is the market standard. "
                            "'Per PO' limits recovery to individual order values, which may be very low. "
                            "'Unlimited' is almost never agreed to by vendors and is unrealistic. Exceptions "
                            "(carve-outs) usually apply for IP infringement, wilful misconduct, and "
                            "confidentiality breaches."
                        ),
                        pros=["Liability cap: Fair risk allocation", "Per PO: Vendor likely to accept"],
                        cons=["Unlimited: Vendor will refuse or raise prices", "Per PO: May not cover consequential losses"],
                    ),
                    _clause(
                        "va_governing_law_city",
                        "Governing Law & Jurisdiction City",
                        "text",
                        "City whose courts will have exclusive jurisdiction",
                        default="Bengaluru",
                        learn_more=(
                            "The jurisdiction city determines where legal proceedings will be initiated in "
                            "case of a dispute. As the buyer, you typically want jurisdiction at your location "
                            "for convenience. Vendors may push for their own city. Choose a location with "
                            "active commercial courts. For MSME vendors, note that disputes may also be "
                            "taken to the MSME Facilitation Council regardless of the jurisdiction clause."
                        ),
                    ),
                ],
            },
        ],
    }


def render_vendor_agreement(tpl: dict, config: dict, parties: dict) -> str:
    """Render Vendor Agreement HTML."""
    company = config.get("va_company_name", "[Purchaser Name]")
    company_addr = config.get("va_company_address", "[Purchaser Address]")
    vendor = config.get("va_vendor_name", "[Vendor Name]")
    vendor_addr = config.get("va_vendor_address", "[Vendor Address]")
    supply_type = config.get("va_supply_type", "Goods and Services")
    supply_desc = config.get("va_supply_description", "[Description]")
    delivery = config.get("va_delivery_terms", "Delivered at purchaser premises (DAP)")
    eff_date = config.get("va_effective_date", "")
    pricing = config.get("va_pricing_model", "Fixed price per unit")
    pay_terms = config.get("va_payment_terms", "Net 30 days")
    msme = config.get("va_vendor_msme_status", "Not an MSME")
    warranty = config.get("va_warranty_period", "12 months")
    quality = config.get("va_quality_standards", "")
    gst = config.get("va_gst_handling", "GST charged extra at applicable rate")
    term = config.get("va_term_months", 12)
    auto_renew = config.get("va_auto_renewal", False)
    term_notice = config.get("va_termination_notice", "30 days written notice")
    liab_cap = config.get("va_liability_cap", "Limited to total payments in last 12 months")
    gov_city = config.get("va_governing_law_city", "Bengaluru")

    sections: List[str] = []
    cn = 0

    # Parties
    sections.append(
        f'<div class="parties">'
        f'<p>This Vendor Agreement ("Agreement") is entered into on '
        f'{eff_date or "________________________"} by and between:</p>'
        f'<p><strong>Purchaser:</strong> {company}, having its registered office at '
        f'{company_addr} (hereinafter the "Purchaser")</p>'
        f'<p><strong>Vendor:</strong> {vendor}, having its address at {vendor_addr} '
        f'(hereinafter the "Vendor")</p>'
        f'</div>'
    )

    # Section 1 — Scope of Supply
    cn += 1
    sections.append(
        f'<h2>{cn}. Scope of Supply</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Vendor shall supply the following ({supply_type}) to the Purchaser:</p>'
        f'<p class="clause">{supply_desc}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Individual orders shall be placed via Purchase Orders ("POs") issued by the '
        f'Purchaser, which shall be governed by the terms of this Agreement.</p>'
    )

    # Section 2 — Delivery
    cn += 1
    sections.append(
        f'<h2>{cn}. Delivery</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Delivery Terms:</strong> {delivery}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Vendor shall deliver goods/services within the timelines specified in '
        f'each Purchase Order. Delay in delivery beyond 7 days without prior written '
        f'intimation may result in cancellation of the PO at the Purchaser\'s discretion.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Risk and title in goods shall pass to the Purchaser upon delivery and '
        f'acceptance at the delivery point.</p>'
    )

    # Section 3 — Pricing & Payment
    cn += 1
    sections.append(
        f'<h2>{cn}. Pricing & Payment</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Pricing Model:</strong> {pricing}. Prices shall be as specified '
        f'in the applicable Purchase Order or rate schedule.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Payment Terms:</strong> {pay_terms} from date of receipt of a valid '
        f'GST-compliant invoice and satisfactory delivery.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'<strong>GST:</strong> {gst}. The Vendor shall provide a valid GSTIN and '
        f'issue GST-compliant tax invoices to enable the Purchaser to claim Input Tax '
        f'Credit.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'TDS shall be deducted by the Purchaser as applicable under the Income Tax '
        f'Act, 1961.</p>'
    )

    # MSME note
    if msme in ("Micro Enterprise", "Small Enterprise", "Medium Enterprise"):
        cn += 1
        sections.append(
            f'<h2>{cn}. MSMED Act Compliance</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Vendor is registered as a <strong>{msme}</strong> under the Micro, '
            f'Small and Medium Enterprises Development Act, 2006.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Purchaser acknowledges its obligation to make payment within the '
            f'timelines prescribed under the MSMED Act (45 days for Micro and Small '
            f'Enterprises). Delayed payments shall attract compound interest at three '
            f'times the bank rate notified by RBI.</p>'
        )

    # Section — Warranty
    cn += 1
    sections.append(
        f'<h2>{cn}. Warranty & Quality</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Vendor warrants that all goods/services shall be free from defects in '
        f'material and workmanship for a period of <strong>{warranty}</strong> from '
        f'the date of delivery/acceptance.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Vendor shall replace or repair (at the Purchaser\'s option) any defective '
        f'goods within 15 days of notification during the warranty period at no '
        f'additional cost.</p>'
    )
    if quality:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The Vendor shall comply with the following quality standards: {quality}</p>'
        )

    # Section — Confidentiality
    cn += 1
    sections.append(
        f'<h2>{cn}. Confidentiality</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Each party shall keep confidential all non-public information received from '
        f'the other party in connection with this Agreement.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Confidentiality obligations shall survive for 2 years after termination of '
        f'this Agreement.</p>'
    )

    # Section — Term & Termination
    cn += 1
    renewal_text = (
        " The Agreement shall automatically renew for successive periods of equal "
        "duration unless either party provides written notice of non-renewal at least "
        "30 days before the end of the then-current term."
        if auto_renew else ""
    )
    sections.append(
        f'<h2>{cn}. Term & Termination</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be effective from {eff_date or "________________________"} '
        f'for a period of <strong>{term} months</strong>.{renewal_text}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Either party may terminate by providing <strong>{term_notice}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Either party may terminate immediately if the other party commits a material '
        f'breach that remains uncured for 15 days after written notice.</p>'
    )

    # Section — Liability
    cn += 1
    sections.append(
        f'<h2>{cn}. Limitation of Liability</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The aggregate liability of the Vendor under this Agreement shall be '
        f'<strong>{liab_cap}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Neither party shall be liable for indirect, consequential, or incidental '
        f'damages, except in cases of wilful misconduct or gross negligence.</p>'
    )

    # Section — Governing Law
    cn += 1
    sections.append(
        f'<h2>{cn}. Governing Law & Dispute Resolution</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be governed by and construed in accordance with the '
        f'laws of India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Any dispute shall be resolved through good-faith negotiation. If unresolved '
        f'within 30 days, the dispute shall be referred to arbitration under the '
        f'Arbitration and Conciliation Act, 1996. The seat of arbitration shall be '
        f'{gov_city}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The courts at {gov_city} shall have exclusive jurisdiction.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Purchaser:</strong> {company}</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Vendor:</strong> {vendor}</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Vendor Agreement \u2014 {company} & {vendor}", body, eff_date
    )


# ======================================================================
# TEMPLATE 19: SaaS AGREEMENT / SOFTWARE LICENSE
# ======================================================================

def saas_agreement_template() -> dict:
    """Template 19 — SaaS Agreement / Software License for cloud-based platforms."""
    return {
        "name": "SaaS Agreement / Software License",
        "description": (
            "End-user software license and SaaS subscription agreement covering "
            "service details, subscription tiers, uptime SLAs, data handling, "
            "licensing scope, usage restrictions, and compliance with IT Act 2000 "
            "and DPDP Act."
        ),
        "category": "Business Operations",
        "steps": [
            # Step 1: Service Details
            {
                "step_number": 1,
                "title": "Service Details",
                "description": "Platform details, subscription tier, and features included.",
                "clauses": [
                    _clause(
                        "saas_provider_name",
                        "Provider / Licensor Name",
                        "text",
                        "Full legal name of the SaaS provider or software licensor",
                        learn_more=(
                            "Enter the legal name of the entity that owns and operates the SaaS platform. "
                            "This is the party granting the license and providing the service. If your startup "
                            "offers a SaaS product, this is your company name. The provider bears responsibility "
                            "for uptime, data security, and support obligations under this agreement."
                        ),
                    ),
                    _clause(
                        "saas_provider_address",
                        "Provider Address",
                        "textarea",
                        "Registered or principal business address of the provider",
                        learn_more=(
                            "The provider's official address for legal notices and correspondence. If the "
                            "provider is a foreign entity offering services in India, the Indian subsidiary "
                            "or local representative's address should be used. This address is also relevant "
                            "for determining GST liability and applicable jurisdiction."
                        ),
                    ),
                    _clause(
                        "saas_customer_name",
                        "Customer / Licensee Name",
                        "text",
                        "Full legal name of the customer subscribing to the service",
                        learn_more=(
                            "The customer is the entity subscribing to and using the SaaS platform. Use the "
                            "exact legal name to ensure invoices, licenses, and data processing obligations are "
                            "properly attributed. If you are subscribing on behalf of a group company, specify "
                            "whether the license extends to affiliates or only the named entity."
                        ),
                    ),
                    _clause(
                        "saas_customer_address",
                        "Customer Address",
                        "textarea",
                        "Registered or principal business address of the customer",
                        learn_more=(
                            "The customer's official address is used for invoicing, sending notices, and "
                            "determining the applicable GST treatment (CGST+SGST for intra-state, IGST for "
                            "inter-state). Ensure this matches your GST registration address to claim Input "
                            "Tax Credit on the subscription fees."
                        ),
                    ),
                    _clause(
                        "saas_platform_name",
                        "Platform / Software Name",
                        "text",
                        "Name of the SaaS platform or software product",
                        learn_more=(
                            "Enter the commercial name of the SaaS platform or software product being licensed. "
                            "This is the brand name customers know, not necessarily the company name. For "
                            "example, the company might be 'XYZ Technologies Pvt Ltd' but the platform could "
                            "be called 'XYZ Cloud'. This name will be used throughout the agreement to refer "
                            "to the service being provided."
                        ),
                    ),
                    _clause(
                        "saas_subscription_tier",
                        "Subscription Tier",
                        "dropdown",
                        "Subscription plan or tier",
                        options=[
                            "Free / Freemium",
                            "Starter / Basic",
                            "Professional / Business",
                            "Enterprise",
                            "Custom / Negotiated",
                        ],
                        default="Professional / Business",
                        learn_more=(
                            "The subscription tier defines the feature set, user limits, and support level "
                            "included in the agreement. Free/Freemium tiers typically have limited features "
                            "and no SLA guarantees. Enterprise and Custom tiers usually include dedicated "
                            "support, custom integrations, and negotiable SLAs. Ensure the chosen tier's "
                            "features match the customer's actual needs — upgrading mid-term may involve "
                            "additional costs or a new agreement."
                        ),
                    ),
                    _clause(
                        "saas_features",
                        "Features Included",
                        "textarea",
                        "Key features and modules included in the subscription",
                        learn_more=(
                            "Clearly listing included features prevents scope disputes. "
                            "Include user limits, storage quotas, API call limits, and "
                            "any add-on modules."
                        ),
                    ),
                    _clause(
                        "saas_effective_date",
                        "Effective Date",
                        "date",
                        "Date from which the subscription begins",
                        learn_more=(
                            "The effective date is when the subscription term begins and the customer gets "
                            "access to the platform. Billing typically starts from this date. If you are the "
                            "provider, ensure onboarding and account setup are completed by this date. If you "
                            "are the customer, negotiate a reasonable setup period before billing begins."
                        ),
                    ),
                ],
            },
            # Step 2: Terms & SLA
            {
                "step_number": 2,
                "title": "Terms & SLA",
                "description": "Uptime guarantees, support levels, data handling, and backup policies.",
                "clauses": [
                    _clause(
                        "saas_uptime_sla",
                        "Uptime SLA",
                        "dropdown",
                        "Guaranteed uptime percentage",
                        options=[
                            "99.0% uptime",
                            "99.5% uptime",
                            "99.9% uptime",
                            "99.99% uptime",
                            "Best effort (no guarantee)",
                        ],
                        default="99.9% uptime",
                        learn_more=(
                            "99.9% uptime allows approximately 8.7 hours of downtime per "
                            "year. 99.99% allows about 52 minutes. Planned maintenance "
                            "windows are typically excluded from SLA calculations."
                        ),
                        common_choice_label="99.9% is industry standard",
                    ),
                    _clause(
                        "saas_support_level",
                        "Support Level",
                        "dropdown",
                        "Level of technical support included",
                        options=[
                            "Email only (24-48 hr response)",
                            "Email + chat (business hours)",
                            "Email + chat + phone (business hours)",
                            "24/7 support with dedicated account manager",
                        ],
                        default="Email + chat (business hours)",
                        learn_more=(
                            "The support level determines how quickly and through which channels the customer "
                            "can get help when issues arise. Email-only support is cheapest but has the slowest "
                            "response times. 24/7 support with a dedicated account manager is premium and "
                            "usually reserved for enterprise-tier subscriptions. For startups, 'Email + chat "
                            "during business hours' is a reasonable balance of cost and responsiveness."
                        ),
                        pros=["Higher support: Faster issue resolution", "Lower support: Reduced cost"],
                        cons=["Higher support: More expensive for provider", "Lower support: Frustrating for critical issues"],
                    ),
                    _clause(
                        "saas_data_hosting",
                        "Data Hosting Location",
                        "dropdown",
                        "Where customer data is hosted",
                        options=[
                            "India (domestic servers)",
                            "India + international (with safeguards)",
                            "Customer choice of region",
                            "Provider's standard infrastructure",
                        ],
                        learn_more=(
                            "Data hosting location matters for regulatory compliance, data sovereignty, and "
                            "latency. India-based hosting ensures compliance with data localization requirements "
                            "for regulated sectors like banking (RBI mandate) and healthcare. International "
                            "hosting may offer better infrastructure but requires compliance with cross-border "
                            "data transfer rules under the DPDP Act. Some government contracts mandate data "
                            "residency in India."
                        ),
                        india_note=(
                            "Under the DPDP Act, 2023, personal data may be transferred "
                            "outside India to all countries except those restricted by the "
                            "Central Government. Certain sectors (e.g., banking, healthcare) "
                            "may have additional data localization requirements from sectoral "
                            "regulators."
                        ),
                    ),
                    _clause(
                        "saas_data_backup",
                        "Data Backup Policy",
                        "dropdown",
                        "How frequently data is backed up",
                        options=[
                            "Daily automated backups",
                            "Real-time / continuous backups",
                            "Weekly backups",
                            "Customer-managed backups",
                        ],
                        default="Daily automated backups",
                        learn_more=(
                            "The backup policy determines how much data you could lose in a disaster scenario. "
                            "Daily backups mean up to 24 hours of data could be lost. Real-time backups minimize "
                            "data loss but are more expensive to implement. Weekly backups are risky for active "
                            "platforms. Customer-managed backups put the responsibility on the customer and "
                            "should only be chosen if the customer has the technical capability."
                        ),
                        warning="Weekly backups risk up to 7 days of data loss in a disaster.",
                        warning_condition={"saas_data_backup": {"eq": "Weekly backups"}},
                    ),
                    _clause(
                        "saas_data_portability",
                        "Data Portability on Termination",
                        "dropdown",
                        "How customer data is handled upon termination",
                        options=[
                            "Data export available for 30 days after termination",
                            "Data export available for 60 days after termination",
                            "Data export available for 90 days after termination",
                            "Immediate deletion upon termination",
                        ],
                        default="Data export available for 30 days after termination",
                        learn_more=(
                            "Data portability determines how long the customer can retrieve their data after "
                            "the subscription ends. Thirty days is standard for most SaaS products. Choosing "
                            "immediate deletion is risky as the customer may lose critical business data. As a "
                            "provider, offering a reasonable export window builds trust. As a customer, ensure "
                            "you have a plan to export data before the window closes. Data should be available "
                            "in standard formats like CSV, JSON, or XML."
                        ),
                        warning="Immediate deletion means no chance to recover data after termination.",
                        warning_condition={"saas_data_portability": {"eq": "Immediate deletion upon termination"}},
                        india_note=(
                            "Under the DPDP Act, data principals have the right to data "
                            "portability. The provider should facilitate data export in a "
                            "machine-readable format."
                        ),
                    ),
                ],
            },
            # Step 3: Licensing & Legal
            {
                "step_number": 3,
                "title": "Licensing & Legal",
                "description": "License scope, usage restrictions, liability, and termination provisions.",
                "clauses": [
                    _clause(
                        "saas_license_type",
                        "License Type",
                        "dropdown",
                        "Type of software license granted",
                        options=[
                            "Subscription (SaaS) - access during term only",
                            "Perpetual license with annual maintenance",
                            "Usage-based / pay-per-use",
                            "Concurrent user license",
                        ],
                        default="Subscription (SaaS) - access during term only",
                        learn_more=(
                            "A SaaS subscription provides access only during the term and "
                            "includes hosting, maintenance, and support. A perpetual license "
                            "grants ongoing usage rights but typically requires separate "
                            "maintenance fees."
                        ),
                    ),
                    _clause(
                        "saas_user_limit",
                        "User Limit",
                        "text",
                        "Maximum number of authorized users (e.g., '50 users' or 'Unlimited')",
                        learn_more=(
                            "The user limit caps how many people can access the platform simultaneously or "
                            "in total. Exceeding this limit typically violates the agreement and may result in "
                            "service suspension. If you expect your team to grow, negotiate a user limit with "
                            "headroom or include a clear process for adding users. Unlimited user licenses are "
                            "rare and typically come with enterprise pricing."
                        ),
                    ),
                    _clause(
                        "saas_restrictions",
                        "Usage Restrictions",
                        "multi_select",
                        "Activities the customer is prohibited from doing",
                        options=[
                            "Reverse engineering or decompilation",
                            "Sublicensing or reselling",
                            "Using for competing product development",
                            "Exceeding usage/API limits",
                            "Sharing login credentials",
                            "Automated scraping or data extraction",
                        ],
                        learn_more=(
                            "Usage restrictions protect the provider's IP and ensure fair "
                            "use. These should be clearly communicated to avoid disputes."
                        ),
                        india_note=(
                            "Under the IT Act, 2000, unauthorized access to computer "
                            "resources is a punishable offence (Section 43, 66). Reverse "
                            "engineering restrictions are generally enforceable under Indian "
                            "contract law."
                        ),
                        common_choice_label="Standard restrictions apply",
                    ),
                    _clause(
                        "saas_subscription_fee",
                        "Subscription Fee (INR)",
                        "text",
                        "Fee amount and billing frequency (e.g., 'INR 50,000/month' or 'INR 5,00,000/year')",
                        learn_more=(
                            "Clearly state the fee amount along with the billing period (monthly, quarterly, "
                            "or annually). Annual plans often come with a discount of 15-20% compared to "
                            "monthly billing. Remember that 18% GST will be charged additionally on SaaS "
                            "subscriptions. For the customer, annual prepayment reduces cost but increases "
                            "lock-in. Specify whether fees are subject to annual price escalation."
                        ),
                    ),
                    _clause(
                        "saas_payment_terms",
                        "Payment Terms",
                        "dropdown",
                        "When payment is due",
                        options=[
                            "Annual upfront payment",
                            "Quarterly in advance",
                            "Monthly in advance",
                            "Net 30 after invoice",
                        ],
                        default="Annual upfront payment",
                        learn_more=(
                            "Payment terms affect cash flow for both parties. Annual upfront is most common "
                            "for SaaS — it gives the provider predictable revenue and often comes with a "
                            "discount for the customer. Quarterly or monthly billing reduces the customer's "
                            "upfront outlay but costs more over time. Net 30 after invoice is typical for "
                            "enterprise deals where the customer needs time for procurement processing."
                        ),
                        pros=["Annual: Discounts and simplicity", "Monthly: Lower initial commitment"],
                        cons=["Annual: Large upfront payment", "Monthly: No discount, higher total cost"],
                    ),
                    _clause(
                        "saas_liability_cap",
                        "Liability Cap",
                        "dropdown",
                        "Maximum aggregate liability of the provider",
                        options=[
                            "Limited to fees paid in last 12 months",
                            "Limited to total contract value",
                            "Limited to fees paid in last 6 months",
                            "Unlimited",
                        ],
                        default="Limited to fees paid in last 12 months",
                        learn_more=(
                            "The liability cap limits the maximum amount the customer can claim from the "
                            "provider if things go wrong (data breach, extended outage, etc.). Twelve months "
                            "of fees is the SaaS industry standard globally. Six months is more favorable to "
                            "the provider. Unlimited liability is almost never agreed to as it creates "
                            "existential risk. Common carve-outs (exceptions to the cap) include data breaches "
                            "due to gross negligence, IP infringement, and breach of confidentiality."
                        ),
                        common_choice_label="12-month fees is industry standard",
                    ),
                    _clause(
                        "saas_term_months",
                        "Subscription Term (months)",
                        "number",
                        "Duration of the initial subscription term",
                        default=12,
                        min_value=1,
                        max_value=60,
                        learn_more=(
                            "The subscription term is the initial duration of the SaaS agreement. Annual "
                            "(12-month) terms are most common for SaaS products. Shorter terms (1-3 months) "
                            "suit trial periods or pilot programs. Longer terms (24-36 months) may come with "
                            "better pricing but reduce flexibility if the product does not meet needs. As a "
                            "startup customer, start with 12 months unless you are very confident about the "
                            "product fit."
                        ),
                    ),
                    _clause(
                        "saas_auto_renewal",
                        "Auto-Renewal",
                        "toggle",
                        "Whether the subscription auto-renews at the end of the term",
                        default=True,
                        learn_more=(
                            "Auto-renewal means the subscription continues for another term unless either "
                            "party provides notice of non-renewal before the current term ends. For providers, "
                            "this ensures recurring revenue. For customers, it provides uninterrupted service "
                            "but requires active management to cancel. Under Indian consumer protection rules, "
                            "auto-renewal terms must be clearly disclosed and customers must have a straightforward "
                            "way to cancel."
                        ),
                        pros=["Uninterrupted service", "Revenue predictability for provider"],
                        cons=["Customer may forget to cancel", "May lock in at old pricing"],
                        india_note=(
                            "Under the Consumer Protection Act, 2019 and Consumer Protection "
                            "(E-Commerce) Rules, 2020, auto-renewal terms must be clearly "
                            "disclosed. Users must have an easy mechanism to cancel."
                        ),
                    ),
                    _clause(
                        "saas_termination_notice",
                        "Termination Notice Period",
                        "dropdown",
                        "Advance notice required for termination or non-renewal",
                        options=[
                            "15 days written notice",
                            "30 days written notice",
                            "60 days written notice",
                            "90 days written notice",
                        ],
                        default="30 days written notice",
                        learn_more=(
                            "The termination notice period determines how far in advance either party must "
                            "communicate their intention to end or not renew the subscription. Thirty days is "
                            "standard. As a customer, shorter notice (15 days) gives more flexibility. As a "
                            "provider, longer notice (60-90 days) helps with revenue planning. Remember to "
                            "set calendar reminders before the notice deadline to avoid unintended auto-renewal."
                        ),
                    ),
                    _clause(
                        "saas_governing_law_city",
                        "Governing Law & Jurisdiction City",
                        "text",
                        "City whose courts will have exclusive jurisdiction",
                        default="Bengaluru",
                        learn_more=(
                            "The governing law and jurisdiction city determine where disputes will be resolved. "
                            "SaaS providers typically choose their company's home city for convenience. "
                            "Enterprise customers may negotiate for their own city. Bengaluru, Mumbai, and "
                            "Delhi are popular choices due to their established commercial courts and technology "
                            "ecosystem. The IT Act, 2000 and DPDP Act, 2023 apply regardless of the jurisdiction "
                            "chosen if the service is offered in India."
                        ),
                    ),
                ],
            },
        ],
    }


def render_saas_agreement(tpl: dict, config: dict, parties: dict) -> str:
    """Render SaaS Agreement / Software License HTML."""
    provider = config.get("saas_provider_name", "[Provider Name]")
    provider_addr = config.get("saas_provider_address", "[Provider Address]")
    customer = config.get("saas_customer_name", "[Customer Name]")
    customer_addr = config.get("saas_customer_address", "[Customer Address]")
    platform = config.get("saas_platform_name", "[Platform Name]")
    tier = config.get("saas_subscription_tier", "Professional / Business")
    features = config.get("saas_features", "[Features]")
    eff_date = config.get("saas_effective_date", "")
    uptime = config.get("saas_uptime_sla", "99.9% uptime")
    support = config.get("saas_support_level", "Email + chat (business hours)")
    hosting = config.get("saas_data_hosting", "India (domestic servers)")
    backup = config.get("saas_data_backup", "Daily automated backups")
    portability = config.get("saas_data_portability", "Data export available for 30 days after termination")
    lic_type = config.get("saas_license_type", "Subscription (SaaS) - access during term only")
    user_limit = config.get("saas_user_limit", "[User Limit]")
    restrictions = config.get("saas_restrictions", [])
    sub_fee = config.get("saas_subscription_fee", "[Fee]")
    pay_terms = config.get("saas_payment_terms", "Annual upfront payment")
    liab_cap = config.get("saas_liability_cap", "Limited to fees paid in last 12 months")
    term = config.get("saas_term_months", 12)
    auto_renew = config.get("saas_auto_renewal", True)
    term_notice = config.get("saas_termination_notice", "30 days written notice")
    gov_city = config.get("saas_governing_law_city", "Bengaluru")

    def _list_html(items: Any) -> str:
        if isinstance(items, list) and items:
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
        return f"<p>{items}</p>" if items else "<p>N/A</p>"

    sections: List[str] = []
    cn = 0

    # Parties
    sections.append(
        f'<div class="parties">'
        f'<p>This SaaS Agreement ("Agreement") is entered into on '
        f'{eff_date or "________________________"} by and between:</p>'
        f'<p><strong>Provider:</strong> {provider}, having its address at '
        f'{provider_addr} (hereinafter the "Provider")</p>'
        f'<p><strong>Customer:</strong> {customer}, having its address at '
        f'{customer_addr} (hereinafter the "Customer")</p>'
        f'</div>'
    )

    # Section 1 — Service Description
    cn += 1
    sections.append(
        f'<h2>{cn}. Service Description</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Provider grants the Customer access to the <strong>{platform}</strong> '
        f'platform ("Service") under the <strong>{tier}</strong> subscription tier.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The following features are included in the subscription:</p>'
        f'<p class="clause">{features}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'<strong>User Limit:</strong> {user_limit}. Additional users may be added '
        f'at the then-current per-user rate.</p>'
    )

    # Section 2 — License Grant
    cn += 1
    sections.append(
        f'<h2>{cn}. License Grant</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>License Type:</strong> {lic_type}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Provider grants the Customer a non-exclusive, non-transferable, '
        f'revocable (during the subscription term) right to access and use the Service '
        f'for the Customer\'s internal business purposes.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'All intellectual property rights in the Service remain with the Provider. '
        f'Nothing in this Agreement transfers ownership of any IP to the Customer.</p>'
    )

    # Section 3 — Usage Restrictions
    cn += 1
    sections.append(
        f'<h2>{cn}. Usage Restrictions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Customer shall not engage in the following activities:</p>'
        f'{_list_html(restrictions)}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Violation of usage restrictions may result in suspension or termination '
        f'of the Service without refund.</p>'
    )

    # Section 4 — Fees & Payment
    cn += 1
    sections.append(
        f'<h2>{cn}. Fees & Payment</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Subscription Fee:</strong> {sub_fee}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Payment Terms:</strong> {pay_terms}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'All fees are exclusive of applicable taxes (GST at 18% will be charged '
        f'additionally). The Provider shall issue GST-compliant invoices.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'The Provider reserves the right to suspend access to the Service if payment '
        f'is overdue by more than 15 days after written notice.</p>'
    )

    # Section 5 — Service Level Agreement
    cn += 1
    sections.append(
        f'<h2>{cn}. Service Level Agreement</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Uptime Guarantee:</strong> The Provider guarantees '
        f'<strong>{uptime}</strong>, measured on a monthly basis. Planned maintenance '
        f'(with at least 24 hours advance notice) is excluded from uptime calculations.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Support:</strong> {support}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'If the Provider fails to meet the uptime SLA in any calendar month, the '
        f'Customer shall be entitled to service credits as follows: (a) below SLA by '
        f'up to 0.5%: 5% credit; (b) below SLA by 0.5%-1%: 10% credit; (c) below '
        f'SLA by more than 1%: 25% credit of that month\'s fee.</p>'
    )

    # Section 6 — Data Handling
    cn += 1
    sections.append(
        f'<h2>{cn}. Data Handling & Security</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Data Hosting:</strong> {hosting}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Backup Policy:</strong> {backup}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The Provider shall implement industry-standard security measures including '
        f'encryption in transit (TLS 1.2+) and at rest (AES-256), access controls, '
        f'and audit logging.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'The Provider shall comply with the Digital Personal Data Protection Act, 2023 '
        f'and the Information Technology Act, 2000 with respect to all personal data '
        f'processed through the Service.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.5</span> '
        f'The Provider shall notify the Customer of any data breach within 72 hours '
        f'of becoming aware of the breach.</p>'
    )

    # Section 7 — Data Portability
    cn += 1
    sections.append(
        f'<h2>{cn}. Data Portability & Deletion</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Upon termination or expiry: <strong>{portability}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Provider shall make data available for export in a commonly used, '
        f'machine-readable format (CSV, JSON, or XML). After the export window, all '
        f'Customer data shall be permanently deleted from the Provider\'s systems.</p>'
    )

    # Section 8 — Liability
    cn += 1
    sections.append(
        f'<h2>{cn}. Limitation of Liability</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The aggregate liability of the Provider under this Agreement shall be '
        f'<strong>{liab_cap}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Provider shall not be liable for any indirect, incidental, consequential, '
        f'special, or punitive damages, including loss of data, revenue, or profits.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The above limitations shall not apply to data breaches caused by Provider\'s '
        f'gross negligence, wilful misconduct, or breach of confidentiality.</p>'
    )

    # Section 9 — Term & Termination
    cn += 1
    renewal_text = (
        " The subscription shall automatically renew for successive periods of equal "
        "duration unless either party provides written notice of non-renewal at least "
        f"{term_notice} before the end of the then-current term."
        if auto_renew else ""
    )
    sections.append(
        f'<h2>{cn}. Term & Termination</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall commence on {eff_date or "________________________"} '
        f'for an initial term of <strong>{term} months</strong>.{renewal_text}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Either party may terminate by providing <strong>{term_notice}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The Provider may terminate immediately if the Customer breaches usage '
        f'restrictions or fails to pay fees within 30 days of a payment reminder.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'The Customer may terminate immediately if the Provider fails to meet the '
        f'uptime SLA for 3 consecutive months.</p>'
    )

    # Section 10 — Governing Law
    cn += 1
    sections.append(
        f'<h2>{cn}. Governing Law & Dispute Resolution</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be governed by and construed in accordance with the '
        f'laws of India, including the Information Technology Act, 2000 and the Digital '
        f'Personal Data Protection Act, 2023.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Any dispute shall first be attempted to be resolved through good-faith '
        f'negotiation. If unresolved within 30 days, the dispute shall be referred to '
        f'arbitration under the Arbitration and Conciliation Act, 1996. The seat of '
        f'arbitration shall be <strong>{gov_city}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The courts at {gov_city} shall have exclusive jurisdiction over any matters '
        f'not subject to arbitration.</p>'
    )

    # Section 11 — General
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement constitutes the entire agreement between the parties and '
        f'supersedes all prior negotiations, representations, and agreements.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Provider may update the Service features and functionality from time to '
        f'time, provided that material changes are communicated to the Customer at '
        f'least 30 days in advance.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Neither party may assign this Agreement without the prior written consent '
        f'of the other party, except in connection with a merger or acquisition.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Provider:</strong> {provider}</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>Customer:</strong> {customer}</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"SaaS Agreement \u2014 {platform}", body, eff_date
    )


# ---------------------------------------------------------------------------
# Registry — makes it easy for the main service to import all templates/renderers
# ---------------------------------------------------------------------------

TIER3A_TEMPLATES: Dict[str, dict] = {
    "posh_policy": posh_policy_template(),
    "convertible_note": convertible_note_template(),
    "msa": msa_template(),
    "vendor_agreement": vendor_agreement_template(),
    "saas_agreement": saas_agreement_template(),
}

TIER3A_RENDERERS: Dict[str, Any] = {
    "posh_policy": render_posh_policy,
    "convertible_note": render_convertible_note,
    "msa": render_msa,
    "vendor_agreement": render_vendor_agreement,
    "saas_agreement": render_saas_agreement,
}
