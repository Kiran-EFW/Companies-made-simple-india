"""Contract template definitions — Tier 3B (Templates 20–24).

Templates included:
 20. Freelancer Agreement
 21. Internship Agreement
 22. Letter of Intent (LOI)
 23. Power of Attorney (POA)
 24. Legal Notice / Demand Letter

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


# ---------------------------------------------------------------------------
# Shared list-to-HTML helper
# ---------------------------------------------------------------------------

def _list_html(items: Any) -> str:
    if isinstance(items, list) and items:
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    return f"<p>{items}</p>" if items else "<p>N/A</p>"


# ======================================================================
# TEMPLATE 20: FREELANCER AGREEMENT
# ======================================================================

def freelancer_agreement_template() -> dict:
    """Template 20 — Freelancer Agreement."""
    return {
        "name": "Freelancer Agreement",
        "description": (
            "Engagement agreement for hiring freelancers/independent contractors. "
            "Covers scope of work, deliverables, payment terms, IP ownership, "
            "and confidentiality. Essential for startups engaging external talent."
        ),
        "category": "HR & Employment",
        "steps": [
            # Step 1: Engagement Details
            {
                "step_number": 1,
                "title": "Engagement Details",
                "description": "Freelancer information, scope, deliverables, and timeline.",
                "clauses": [
                    _clause(
                        "fa_freelancer_name",
                        "Freelancer Name",
                        "text",
                        "Full legal name of the freelancer/independent contractor",
                        learn_more=(
                            "Enter the freelancer's full legal name as it appears on their PAN card or Aadhaar. "
                            "This is important because TDS certificates (Form 16A) will be issued in this name. "
                            "If the freelancer operates through a company or LLP, use the entity name instead — "
                            "this changes the TDS rate and compliance requirements."
                        ),
                    ),
                    _clause(
                        "fa_freelancer_address",
                        "Freelancer Address",
                        "textarea",
                        "Complete address of the freelancer",
                        learn_more=(
                            "The freelancer's address is used for formal notices and determining GST applicability. "
                            "If the freelancer is based in a different state than your company, inter-state GST "
                            "(IGST) applies instead of CGST+SGST. This address also helps establish that the "
                            "freelancer works independently from their own premises, supporting the contractor "
                            "(not employee) classification."
                        ),
                    ),
                    _clause(
                        "fa_company_name",
                        "Company Name",
                        "text",
                        "Name of the engaging company",
                        learn_more=(
                            "This is the company hiring the freelancer. Use your exact legal name as registered "
                            "with MCA. The company is responsible for deducting TDS on payments to the freelancer "
                            "and issuing TDS certificates. The company is the 'client' in this agreement and "
                            "typically receives the work product and IP upon completion."
                        ),
                    ),
                    _clause(
                        "fa_scope_of_work",
                        "Scope of Work",
                        "textarea",
                        "Detailed description of work to be performed by the freelancer",
                        learn_more=(
                            "Clearly defining the scope is critical. A vague scope "
                            "can lead to disputes about deliverables and may also "
                            "blur the line between a contractor and an employee, "
                            "which has legal implications."
                        ),
                    ),
                    _clause(
                        "fa_deliverables",
                        "Deliverables",
                        "textarea",
                        "List of specific deliverables expected from the freelancer",
                        learn_more=(
                            "Deliverables should be concrete and measurable. Include "
                            "file formats, specifications, and acceptance criteria "
                            "where possible."
                        ),
                    ),
                    _clause(
                        "fa_start_date",
                        "Start Date",
                        "date",
                        "Date when the engagement begins",
                        learn_more=(
                            "The start date is when the freelancer begins work and obligations under this "
                            "agreement take effect. IP assignment, confidentiality, and payment terms all "
                            "commence from this date. Ensure the agreement is signed before or on this date — "
                            "work done before the agreement is signed may not be covered by IP assignment and "
                            "confidentiality clauses."
                        ),
                    ),
                    _clause(
                        "fa_end_date",
                        "End Date",
                        "date",
                        "Expected completion date of the engagement",
                        required=False,
                        learn_more=(
                            "Setting a clear end date is critical for freelancer engagements. Without it, the "
                            "relationship may be treated as an ongoing employment relationship by Indian labour "
                            "authorities, which exposes you to PF, ESI, and other statutory obligations. Even "
                            "for ongoing work, set a project-based end date and renew the agreement for each "
                            "new phase. A common founder mistake is leaving this open-ended."
                        ),
                        warning="Open-ended engagements may be reclassified as employment.",
                        warning_condition={"fa_end_date": {"eq": ""}},
                        india_note=(
                            "An open-ended engagement without a defined end date may "
                            "be construed as an employer-employee relationship by "
                            "labour authorities. Always specify a project duration."
                        ),
                    ),
                    _clause(
                        "fa_milestones",
                        "Milestones",
                        "textarea",
                        "Key milestones and their deadlines (one per line)",
                        required=False,
                        learn_more=(
                            "Milestones break the project into measurable checkpoints with deadlines. They help "
                            "track progress and are especially useful when payments are tied to deliverables. "
                            "Each milestone should have a clear description, expected date, and acceptance "
                            "criteria. For example: 'UI wireframes delivery - 15 days from start' or "
                            "'Backend API integration - 30 days from start'. Milestones also help if you need "
                            "to terminate for non-performance."
                        ),
                    ),
                ],
            },
            # Step 2: Payment & Legal
            {
                "step_number": 2,
                "title": "Payment & Legal",
                "description": "Fees, payment terms, IP ownership, confidentiality, and termination.",
                "clauses": [
                    _clause(
                        "fa_fee_structure",
                        "Fee Structure",
                        "dropdown",
                        "How the freelancer will be compensated",
                        options=[
                            "Fixed project fee",
                            "Hourly rate",
                            "Monthly retainer",
                            "Milestone-based payments",
                        ],
                        learn_more=(
                            "Fixed fees work well for defined projects. Hourly rates "
                            "suit ongoing advisory work. Milestone-based payments "
                            "align incentives for phased deliverables."
                        ),
                        pros=["Clear cost expectations", "Aligned incentives"],
                        cons=["May need renegotiation if scope changes"],
                        common_choice_label="Common for startups: Fixed project fee",
                    ),
                    _clause(
                        "fa_fee_amount",
                        "Fee Amount (INR)",
                        "number",
                        "Total fee or rate in INR (based on fee structure selected)",
                        learn_more=(
                            "Enter the total project fee, hourly rate, or monthly retainer amount depending "
                            "on the fee structure selected. The freelancer will receive this amount minus TDS "
                            "(typically 10% under Section 194J for professional fees exceeding INR 30,000/year). "
                            "Make sure the freelancer understands the net payment after TDS. The company must "
                            "issue a TDS certificate (Form 16A) quarterly."
                        ),
                        india_note=(
                            "TDS at 10% is applicable under Section 194J of the "
                            "Income Tax Act for professional/technical fees exceeding "
                            "INR 30,000 per annum. The company must deduct TDS before "
                            "payment."
                        ),
                    ),
                    _clause(
                        "fa_payment_terms",
                        "Payment Terms",
                        "dropdown",
                        "When payments are due",
                        options=[
                            "100% on completion",
                            "50% advance, 50% on completion",
                            "Monthly invoicing (Net 15)",
                            "Monthly invoicing (Net 30)",
                            "Milestone-based (as agreed)",
                        ],
                        learn_more=(
                            "Payment terms define when the freelancer gets paid. '100% on completion' is "
                            "riskiest for the freelancer and may deter good talent. '50% advance, 50% on "
                            "completion' is the most common for project-based work — it protects both parties. "
                            "Monthly invoicing suits ongoing retainer engagements. Milestone-based payments "
                            "align with project progress and are ideal for longer projects. Freelancers "
                            "commonly request some advance to cover their expenses."
                        ),
                        pros=["Advance payment: Attracts better freelancers", "Milestone-based: Aligned incentives"],
                        cons=["100% advance: Risk if freelancer underdelivers", "100% on completion: May deter top talent"],
                        common_choice_label="Common: 50% advance, 50% on completion",
                    ),
                    _clause(
                        "fa_ip_ownership",
                        "IP Ownership",
                        "dropdown",
                        "Who owns the intellectual property created during the engagement",
                        options=[
                            "All IP belongs to Company",
                            "IP shared — Company gets exclusive license",
                            "Freelancer retains IP, Company gets non-exclusive license",
                        ],
                        learn_more=(
                            "In India, under the Copyright Act 1957 (Section 17), "
                            "when a work is made under a contract for service, the "
                            "copyright belongs to the author (freelancer) unless "
                            "explicitly assigned. Always include an IP assignment "
                            "clause."
                        ),
                        india_note=(
                            "Unlike employees, freelancers retain copyright by "
                            "default under Indian law. An explicit written assignment "
                            "clause is mandatory to transfer IP to the company. "
                            "Section 18 of the Copyright Act requires assignment to "
                            "be in writing."
                        ),
                        pros=["Clear IP ownership avoids future disputes"],
                        cons=["Full assignment may increase freelancer's fee"],
                        common_choice_label="Most protective: All IP belongs to Company",
                    ),
                    _clause(
                        "fa_confidentiality",
                        "Confidentiality",
                        "toggle",
                        "Whether the freelancer is bound by confidentiality obligations",
                        learn_more=(
                            "Confidentiality clauses protect trade secrets and "
                            "proprietary information. Without one, a freelancer "
                            "may freely use or disclose your business information."
                        ),
                        common_choice_label="Recommended: Yes",
                    ),
                    _clause(
                        "fa_non_compete",
                        "Non-Compete Clause",
                        "toggle",
                        "Whether to include restrictions on working with competitors",
                        learn_more=(
                            "A non-compete clause prevents the freelancer from working with your competitors. "
                            "In India, non-compete clauses are generally unenforceable under Section 27 of the "
                            "Indian Contract Act, 1872, which voids agreements that restrain trade. Instead, "
                            "consider using a non-solicitation clause (preventing the freelancer from soliciting "
                            "your clients/employees) which is more enforceable. The toggle here will include "
                            "a limited non-solicitation provision during the term of the agreement."
                        ),
                        india_note=(
                            "Non-compete clauses are largely unenforceable in India "
                            "under Section 27 of the Indian Contract Act, 1872, "
                            "which holds restraint of trade agreements void. "
                            "However, non-solicitation and confidentiality clauses "
                            "during the term are enforceable."
                        ),
                        warning="Non-compete clauses are generally unenforceable in India",
                        common_choice_label="Standard: No (use non-solicitation instead)",
                    ),
                    _clause(
                        "fa_termination_notice",
                        "Termination Notice Period",
                        "dropdown",
                        "Notice period required by either party to terminate the engagement",
                        options=[
                            "7 days written notice",
                            "15 days written notice",
                            "30 days written notice",
                            "Immediate termination for cause",
                        ],
                        learn_more=(
                            "The termination notice period defines how much advance notice is required to end "
                            "the engagement. Fifteen days is standard and gives both parties time to wrap up. "
                            "'Immediate termination for cause' should always be available as an additional "
                            "right — it applies when there is a material breach, fraud, or misconduct. "
                            "The freelancer should be paid for work completed up to the termination date "
                            "regardless of who terminates."
                        ),
                        common_choice_label="Standard: 15 days written notice",
                    ),
                    _clause(
                        "fa_governing_law",
                        "Governing Law (State)",
                        "text",
                        "Indian state whose courts will have jurisdiction",
                        learn_more=(
                            "Enter the Indian state whose laws and courts will govern this agreement. "
                            "Typically, this is the state where your company is registered. If the freelancer "
                            "is in a different state, there could be a dispute about jurisdiction — specifying "
                            "it here resolves that upfront. Common choices are Karnataka, Maharashtra, Delhi, "
                            "or Tamil Nadu depending on where the company operates."
                        ),
                        india_note=(
                            "Freelancer agreements are governed by the Indian "
                            "Contract Act, 1872. GST registration is required for "
                            "freelancers with turnover exceeding INR 20 lakhs "
                            "(INR 10 lakhs in special category states)."
                        ),
                    ),
                ],
            },
        ],
    }


def render_freelancer_agreement(tpl: dict, config: dict, parties: dict) -> str:
    """Render Freelancer Agreement HTML."""
    freelancer = config.get("fa_freelancer_name", "[Freelancer Name]")
    freelancer_addr = config.get("fa_freelancer_address", "[Freelancer Address]")
    company = config.get("fa_company_name", parties.get("company_name", "[Company Name]"))
    scope = config.get("fa_scope_of_work", "[Scope of Work]")
    deliverables = config.get("fa_deliverables", "[Deliverables]")
    start_date = config.get("fa_start_date", "")
    end_date = config.get("fa_end_date", "")
    milestones = config.get("fa_milestones", "")
    fee_structure = config.get("fa_fee_structure", "Fixed project fee")
    fee_amount = config.get("fa_fee_amount", 0)
    payment_terms = config.get("fa_payment_terms", "50% advance, 50% on completion")
    ip_ownership = config.get("fa_ip_ownership", "All IP belongs to Company")
    confidentiality = config.get("fa_confidentiality", True)
    non_compete = config.get("fa_non_compete", False)
    termination_notice = config.get("fa_termination_notice", "15 days written notice")
    governing = config.get("fa_governing_law", "[State]")

    sections: List[str] = []

    # Parties
    sections.append(
        f'<div class="parties">'
        f'<p>This Freelancer Agreement ("Agreement") is entered into between:</p>'
        f'<p><strong>Company:</strong> {company} ("Client")</p>'
        f'<p><strong>Freelancer:</strong> {freelancer} ("Contractor")</p>'
        f'<p><strong>Address:</strong> {freelancer_addr}</p>'
        f'</div>'
    )

    # Section 1 — Engagement & Scope
    cn = 1
    sections.append(
        f'<h2>{cn}. Engagement & Scope of Work</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Client hereby engages the Contractor as an independent contractor '
        f'(not an employee) to perform the following services:</p>'
        f'<p class="clause"><em>{scope}</em></p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Deliverables:</strong></p>'
        f'<p class="clause"><em>{deliverables}</em></p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The Contractor shall perform services with due diligence, skill, and '
        f'care, and in accordance with industry standards.</p>'
    )

    # Section 2 — Term
    cn += 1
    sections.append(
        f'<h2>{cn}. Term</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement commences on '
        f'<strong>{start_date or "________________________"}</strong> '
        f'and shall continue until '
        f'<strong>{end_date or "completion of the project"}</strong>, '
        f'unless terminated earlier in accordance with this Agreement.</p>'
    )
    if milestones:
        milestone_lines = [m.strip() for m in milestones.split("\n") if m.strip()]
        if milestone_lines:
            sections.append(
                f'<p class="clause"><span class="clause-number">{cn}.2</span> '
                f'<strong>Milestones:</strong></p>'
                f'{_list_html(milestone_lines)}'
            )

    # Section 3 — Independent Contractor Status
    cn += 1
    sections.append(
        f'<h2>{cn}. Independent Contractor Status</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Contractor is an independent contractor and not an employee, agent, '
        f'partner, or joint venturer of the Client. The Contractor shall not be '
        f'entitled to any employee benefits including but not limited to provident '
        f'fund, gratuity, ESI, bonus, or leave encashment.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Contractor shall be solely responsible for payment of all taxes, '
        f'including income tax, GST, and professional tax, on amounts received '
        f'under this Agreement.</p>'
    )

    # Section 4 — Compensation
    cn += 1
    sections.append(
        f'<h2>{cn}. Compensation & Payment</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Fee Structure:</strong> {fee_structure}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Fee Amount:</strong> INR {fee_amount:,} (Indian Rupees).</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'<strong>Payment Terms:</strong> {payment_terms}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'All payments shall be subject to deduction of TDS under Section 194J '
        f'of the Income Tax Act, 1961, as applicable. The Client shall provide '
        f'TDS certificates (Form 16A) to the Contractor.</p>'
    )

    # Section 5 — IP Ownership
    cn += 1
    sections.append(
        f'<h2>{cn}. Intellectual Property</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'IP Ownership: <strong>{ip_ownership}</strong>.</p>'
    )
    if ip_ownership == "All IP belongs to Company":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Contractor hereby irrevocably assigns to the Client all right, '
            f'title, and interest in and to all work product, deliverables, and '
            f'intellectual property created under this Agreement, including all '
            f'copyrights, patents, trade secrets, and other proprietary rights.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The Contractor shall execute all documents and take all actions '
            f'reasonably requested by the Client to perfect such assignment.</p>'
        )
    elif ip_ownership == "IP shared — Company gets exclusive license":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Contractor grants the Client a perpetual, irrevocable, worldwide, '
            f'exclusive license to use, modify, reproduce, and distribute all work '
            f'product created under this Agreement.</p>'
        )
    else:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Contractor grants the Client a perpetual, irrevocable, worldwide, '
            f'non-exclusive license to use the deliverables for its business purposes.</p>'
        )

    # Section 6 — Confidentiality
    cn += 1
    if confidentiality:
        sections.append(
            f'<h2>{cn}. Confidentiality</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Contractor shall keep confidential all proprietary information, '
            f'trade secrets, business plans, customer data, and other confidential '
            f'information disclosed by the Client during and after the term of '
            f'this Agreement.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'This obligation shall survive the termination of this Agreement '
            f'for a period of three (3) years.</p>'
        )
    else:
        sections.append(
            f'<h2>{cn}. Confidentiality</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'No specific confidentiality obligations have been agreed upon. '
            f'However, both parties shall act in good faith regarding any '
            f'sensitive information exchanged during the engagement.</p>'
        )

    # Section 7 — Termination
    cn += 1
    sections.append(
        f'<h2>{cn}. Termination</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Either party may terminate this Agreement by providing '
        f'<strong>{termination_notice}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Either party may terminate this Agreement immediately upon material '
        f'breach by the other party that remains uncured for fifteen (15) days '
        f'after written notice.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'Upon termination, the Contractor shall deliver all completed and '
        f'in-progress work to the Client and shall be entitled to payment '
        f'for work completed up to the date of termination.</p>'
    )

    # Section 8 — General Provisions
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Agreement shall be governed by and construed in accordance with '
        f'the laws of <strong>{governing}</strong>, India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Any dispute arising out of this Agreement shall be subject to the '
        f'exclusive jurisdiction of the courts in {governing}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This Agreement constitutes the entire agreement between the parties '
        f'and supersedes all prior negotiations and agreements.</p>'
    )

    if non_compete:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'During the term of this Agreement, the Contractor agrees not to '
            f'directly solicit or engage with the Client\'s existing customers '
            f'or employees for competing purposes.</p>'
        )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>For {company}</strong> (Client)</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{freelancer}</strong> (Contractor)</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Freelancer Agreement \u2014 {freelancer}", body, start_date
    )


# ======================================================================
# TEMPLATE 21: INTERNSHIP AGREEMENT
# ======================================================================

def internship_agreement_template() -> dict:
    """Template 21 — Internship Agreement."""
    return {
        "name": "Internship Agreement",
        "description": (
            "Agreement for engaging interns in your company. Covers internship "
            "duration, stipend, working hours, IP assignment, confidentiality, "
            "and certificate issuance. Suitable for both student and professional "
            "internships."
        ),
        "category": "HR & Employment",
        "steps": [
            # Step 1: Internship Details
            {
                "step_number": 1,
                "title": "Internship Details",
                "description": "Intern information, duration, department, stipend, and working hours.",
                "clauses": [
                    _clause(
                        "ia_intern_name",
                        "Intern Name",
                        "text",
                        "Full name of the intern",
                        learn_more=(
                            "Enter the intern's full legal name. If the intern is a minor (under 18), the "
                            "agreement should ideally be co-signed by a parent or guardian. For student interns, "
                            "the name should match their institution's records to facilitate academic credit "
                            "and certificate verification."
                        ),
                    ),
                    _clause(
                        "ia_intern_institution",
                        "Institution/College",
                        "text",
                        "Name of the educational institution (if applicable)",
                        required=False,
                        learn_more=(
                            "If the intern is a student, mentioning the institution "
                            "helps establish the educational nature of the internship "
                            "and may qualify for academic credit."
                        ),
                    ),
                    _clause(
                        "ia_company_name",
                        "Company Name",
                        "text",
                        "Name of the company offering the internship",
                        learn_more=(
                            "Use your company's registered legal name. This name will appear on the internship "
                            "certificate and any letter of recommendation. For campus recruiting, colleges may "
                            "verify your company's existence through MCA records, so accuracy is important."
                        ),
                    ),
                    _clause(
                        "ia_department",
                        "Department",
                        "text",
                        "Department where the intern will work",
                        learn_more=(
                            "Specifying the department helps define the internship scope and ensures the intern's "
                            "work aligns with their learning objectives. It also helps if the institution requires "
                            "proof that the internship is relevant to the student's field of study. Common examples: "
                            "Engineering, Marketing, Product, Design, Finance, Operations."
                        ),
                    ),
                    _clause(
                        "ia_mentor_name",
                        "Mentor/Supervisor Name",
                        "text",
                        "Name of the assigned mentor or supervisor",
                        learn_more=(
                            "The mentor or supervisor is responsible for guiding the intern, assigning tasks, "
                            "and providing feedback. Colleges often require a supervisor's name for their records "
                            "and may contact them for evaluation. Choose someone with bandwidth to mentor — "
                            "a busy founder or CTO may not be the best choice for day-to-day guidance."
                        ),
                    ),
                    _clause(
                        "ia_duration",
                        "Duration",
                        "dropdown",
                        "Length of the internship",
                        options=[
                            "1 month",
                            "2 months",
                            "3 months",
                            "6 months",
                            "12 months",
                        ],
                        learn_more=(
                            "Longer internships (over 6 months) may raise questions "
                            "about disguised employment. Keep the duration aligned "
                            "with the learning objectives."
                        ),
                        india_note=(
                            "There is no specific internship law in India. However, "
                            "internships exceeding 6 months may be viewed as disguised "
                            "employment by labour authorities, especially if the intern "
                            "is performing work similar to regular employees."
                        ),
                        common_choice_label="Common: 3 months",
                    ),
                    _clause(
                        "ia_start_date",
                        "Start Date",
                        "date",
                        "Date when the internship begins",
                        learn_more=(
                            "The start date is when the intern formally joins. The internship duration runs "
                            "from this date. For student internships, align this with the institution's academic "
                            "calendar to avoid conflicts. The stipend (if applicable) is calculated from this "
                            "date. Ensure the agreement is signed before or on the start date."
                        ),
                    ),
                    _clause(
                        "ia_stipend",
                        "Monthly Stipend (INR)",
                        "number",
                        "Monthly stipend amount in INR (enter 0 if unpaid)",
                        india_note=(
                            "Stipends are not classified as salary under Indian labour "
                            "laws. If the stipend exceeds INR 2,50,000 per annum, TDS "
                            "may be applicable. Unpaid internships are legally "
                            "permissible but discouraged for longer durations."
                        ),
                        learn_more=(
                            "A stipend is distinct from salary. It is meant to cover "
                            "the intern's expenses during the learning period. Unlike "
                            "salary, PF and ESI are generally not applicable on stipends."
                        ),
                        pros=["Attracts better talent", "Shows good faith"],
                        cons=["Additional cost for early-stage startups"],
                    ),
                    _clause(
                        "ia_working_hours",
                        "Working Hours",
                        "dropdown",
                        "Expected working hours per day",
                        options=[
                            "4 hours/day (part-time)",
                            "6 hours/day",
                            "8 hours/day (full-time)",
                            "Flexible hours",
                        ],
                        learn_more=(
                            "Working hours should be appropriate for the internship nature. Full-time (8 hours) "
                            "is standard for dedicated internships. Part-time (4-6 hours) suits students who "
                            "are attending classes simultaneously. Flexible hours work well for remote internships. "
                            "If you set full-time hours, the distinction between intern and employee becomes "
                            "thinner — ensure the role is genuinely educational, not just cheap labour."
                        ),
                        common_choice_label="Standard: 8 hours/day (full-time)",
                    ),
                ],
            },
            # Step 2: Legal Terms
            {
                "step_number": 2,
                "title": "Legal Terms",
                "description": "IP assignment, confidentiality, certificate, and termination terms.",
                "clauses": [
                    _clause(
                        "ia_ip_assignment",
                        "IP Assignment",
                        "dropdown",
                        "Who owns work created by the intern during the internship",
                        options=[
                            "All IP belongs to Company",
                            "Shared — Company gets license",
                            "Intern retains IP",
                        ],
                        learn_more=(
                            "Interns often create valuable work product. Without a "
                            "clear IP clause, ownership can be ambiguous, especially "
                            "for student interns who may want to use the work for "
                            "academic purposes."
                        ),
                        india_note=(
                            "Since interns are not employees, the Copyright Act 1957 "
                            "default gives IP to the author (intern). An explicit "
                            "assignment clause is needed for the company to own the IP."
                        ),
                        common_choice_label="Recommended: All IP belongs to Company",
                    ),
                    _clause(
                        "ia_confidentiality",
                        "Confidentiality",
                        "toggle",
                        "Whether the intern is bound by confidentiality obligations",
                        learn_more=(
                            "Confidentiality obligations prevent the intern from disclosing your proprietary "
                            "information, code, business plans, and client data. This is especially important "
                            "for startups sharing sensitive IP with interns. Even if the intern is from a "
                            "trusted institution, always enable this — interns may unknowingly share information "
                            "with peers or mention it in academic reports. The obligation typically survives "
                            "the end of the internship."
                        ),
                        common_choice_label="Recommended: Yes",
                    ),
                    _clause(
                        "ia_certificate",
                        "Certificate of Completion",
                        "toggle",
                        "Whether the company will issue a certificate upon successful completion",
                        learn_more=(
                            "Providing a certificate is a standard practice and is "
                            "often required by educational institutions for academic "
                            "credit. It costs nothing and builds goodwill."
                        ),
                        common_choice_label="Standard: Yes",
                    ),
                    _clause(
                        "ia_ppo_eligible",
                        "Pre-Placement Offer Eligibility",
                        "toggle",
                        "Whether outstanding interns may be offered full-time employment",
                        required=False,
                        learn_more=(
                            "Pre-placement offers (PPOs) are common in India, "
                            "especially for campus internships. Mentioning PPO "
                            "eligibility motivates the intern and sets expectations."
                        ),
                    ),
                    _clause(
                        "ia_insurance",
                        "Insurance Coverage",
                        "dropdown",
                        "Whether the company provides any insurance for the intern",
                        options=[
                            "No insurance provided",
                            "Group personal accident insurance",
                            "Group health insurance",
                            "Both accident and health insurance",
                        ],
                        learn_more=(
                            "Since interns are not covered by ESI or workmen's compensation, they have no "
                            "statutory safety net if they are injured at the workplace. Providing at least "
                            "group personal accident insurance is recommended, especially for on-site or "
                            "factory-based internships. Health insurance is a nice-to-have but adds cost. "
                            "Some institutions require proof of insurance before approving the internship."
                        ),
                        pros=["Shows duty of care", "Covers liability for workplace accidents"],
                        cons=["Additional cost for the company", "Administrative overhead"],
                        india_note=(
                            "Interns are typically not covered under ESI or workmen's "
                            "compensation. Providing basic accident insurance is "
                            "recommended, especially for on-site internships."
                        ),
                        common_choice_label="Recommended: Group personal accident insurance",
                    ),
                    _clause(
                        "ia_termination",
                        "Termination Notice",
                        "dropdown",
                        "Notice period for terminating the internship",
                        options=[
                            "Immediate (no notice)",
                            "7 days written notice",
                            "15 days written notice",
                        ],
                        learn_more=(
                            "The termination notice period gives both parties time to prepare for the end of "
                            "the internship. Seven days is standard for internships. Immediate termination "
                            "should be reserved for cause (misconduct, breach of confidentiality). If a "
                            "student intern leaves abruptly, it may affect their academic standing — a short "
                            "notice period helps manage this. The company should always be able to terminate "
                            "immediately for serious violations."
                        ),
                        common_choice_label="Standard: 7 days written notice",
                    ),
                    _clause(
                        "ia_code_of_conduct",
                        "Code of Conduct Applicable",
                        "toggle",
                        "Whether the company's code of conduct applies to the intern",
                        learn_more=(
                            "Applying the company's code of conduct to interns sets clear expectations about "
                            "workplace behaviour, dress code, attendance, harassment policies, and data handling. "
                            "This is especially important for POSH compliance, as the POSH Act applies to all "
                            "persons at the workplace including interns. Enabling this protects both the company "
                            "and the intern by establishing shared ground rules."
                        ),
                        common_choice_label="Recommended: Yes",
                    ),
                    _clause(
                        "ia_governing_law",
                        "Governing Law (State)",
                        "text",
                        "Indian state whose courts will have jurisdiction",
                        learn_more=(
                            "Enter the Indian state where your company is registered. This determines which "
                            "state's courts will handle any disputes arising from the internship. Since "
                            "internship disputes rarely go to court, this is primarily a precautionary clause. "
                            "However, it also determines which state's labour laws interpretations may apply "
                            "if the internship is ever challenged as disguised employment."
                        ),
                    ),
                ],
            },
        ],
    }


def render_internship_agreement(tpl: dict, config: dict, parties: dict) -> str:
    """Render Internship Agreement HTML."""
    intern = config.get("ia_intern_name", "[Intern Name]")
    institution = config.get("ia_intern_institution", "")
    company = config.get("ia_company_name", parties.get("company_name", "[Company Name]"))
    department = config.get("ia_department", "[Department]")
    mentor = config.get("ia_mentor_name", "[Mentor Name]")
    duration = config.get("ia_duration", "3 months")
    start_date = config.get("ia_start_date", "")
    stipend = config.get("ia_stipend", 0)
    working_hours = config.get("ia_working_hours", "8 hours/day (full-time)")
    ip_assignment = config.get("ia_ip_assignment", "All IP belongs to Company")
    confidentiality = config.get("ia_confidentiality", True)
    certificate = config.get("ia_certificate", True)
    ppo = config.get("ia_ppo_eligible", False)
    insurance = config.get("ia_insurance", "No insurance provided")
    termination = config.get("ia_termination", "7 days written notice")
    code_of_conduct = config.get("ia_code_of_conduct", True)
    governing = config.get("ia_governing_law", "[State]")

    sections: List[str] = []

    # Parties
    sections.append(
        f'<div class="parties">'
        f'<p>This Internship Agreement ("Agreement") is entered into between:</p>'
        f'<p><strong>Company:</strong> {company} ("Company")</p>'
        f'<p><strong>Intern:</strong> {intern} ("Intern")</p>'
        f'{("<p><strong>Institution:</strong> " + institution + "</p>") if institution else ""}'
        f'</div>'
    )

    # Section 1 — Internship Details
    cn = 1
    sections.append(
        f'<h2>{cn}. Internship Details</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Department:</strong> {department}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Mentor/Supervisor:</strong> {mentor}</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'<strong>Duration:</strong> {duration}, commencing from '
        f'{start_date or "________________________"}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'<strong>Working Hours:</strong> {working_hours}.</p>'
    )

    # Section 2 — Stipend
    cn += 1
    sections.append(
        f'<h2>{cn}. Stipend</h2>'
    )
    if stipend and stipend > 0:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Company shall pay the Intern a monthly stipend of '
            f'<strong>INR {stipend:,}</strong>.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The stipend shall be paid on or before the 7th of the following '
            f'month, subject to applicable tax deductions.</p>'
        )
    else:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'This is an unpaid internship. The Intern acknowledges that no '
            f'monetary compensation shall be provided, and the internship is '
            f'undertaken for learning and experience purposes.</p>'
        )

    # Section 3 — Nature of Engagement
    cn += 1
    sections.append(
        f'<h2>{cn}. Nature of Engagement</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Intern is not an employee of the Company. This internship does '
        f'not create an employer-employee relationship and does not entitle the '
        f'Intern to benefits applicable to regular employees such as provident '
        f'fund, gratuity, bonus, or earned leave.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The primary purpose of this engagement is to provide the Intern with '
        f'practical learning experience in {department}.</p>'
    )

    # Section 4 — IP Assignment
    cn += 1
    sections.append(
        f'<h2>{cn}. Intellectual Property</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'IP Ownership: <strong>{ip_assignment}</strong>.</p>'
    )
    if ip_assignment == "All IP belongs to Company":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'All work product, inventions, designs, code, documents, and other '
            f'materials created by the Intern during the internship shall be the '
            f'exclusive property of the Company. The Intern hereby assigns all '
            f'rights, title, and interest in such work to the Company.</p>'
        )
    elif ip_assignment == "Shared — Company gets license":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Intern grants the Company a perpetual, irrevocable, royalty-free '
            f'license to use all work product created during the internship. The '
            f'Intern may use the work for academic or portfolio purposes.</p>'
        )
    else:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Intern retains intellectual property rights in work created '
            f'during the internship. The Intern grants the Company a non-exclusive '
            f'license to use such work for its business purposes.</p>'
        )

    # Section 5 — Confidentiality
    cn += 1
    if confidentiality:
        sections.append(
            f'<h2>{cn}. Confidentiality</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Intern shall maintain strict confidentiality of all proprietary '
            f'information, trade secrets, client data, and business processes of '
            f'the Company during and after the internship.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Intern shall not disclose, publish, or use any confidential '
            f'information without prior written consent of the Company. This '
            f'obligation survives termination of this Agreement.</p>'
        )
    else:
        sections.append(
            f'<h2>{cn}. Confidentiality</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Both parties shall act in good faith with respect to any sensitive '
            f'information exchanged during the internship.</p>'
        )

    # Section 6 — Certificate & PPO
    cn += 1
    sections.append(
        f'<h2>{cn}. Certificate & Post-Internship</h2>'
    )
    if certificate:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Upon successful completion of the internship, the Company shall '
            f'issue a Certificate of Completion to the Intern.</p>'
        )
    if ppo:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Based on performance, the Intern may be considered for a '
            f'pre-placement offer (PPO) for full-time employment with the '
            f'Company, subject to available positions and mutual agreement.</p>'
        )

    # Section 7 — Termination
    cn += 1
    sections.append(
        f'<h2>{cn}. Termination</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Either party may terminate this internship by providing '
        f'<strong>{termination}</strong>.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Company may terminate the internship immediately in case of '
        f'misconduct, breach of confidentiality, or violation of the code of '
        f'conduct.</p>'
    )
    if code_of_conduct:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The Intern shall comply with the Company\'s code of conduct, '
            f'policies, and workplace rules applicable to regular employees.</p>'
        )

    # Section 8 — General
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Insurance:</strong> {insurance}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'This Agreement shall be governed by the laws of '
        f'<strong>{governing}</strong>, India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This Agreement constitutes the entire understanding between the '
        f'parties regarding the internship.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Agreement as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>For {company}</strong></p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{intern}</strong> (Intern)</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Internship Agreement \u2014 {intern}", body, start_date
    )


# ======================================================================
# TEMPLATE 22: LETTER OF INTENT (LOI)
# ======================================================================

def letter_of_intent_template() -> dict:
    """Template 22 — Letter of Intent (LOI)."""
    return {
        "name": "Letter of Intent (LOI)",
        "description": (
            "A preliminary document outlining the key terms and conditions of a "
            "proposed transaction between parties. Used in M&A, investments, "
            "partnerships, and large commercial deals before executing a "
            "definitive agreement."
        ),
        "category": "Business Operations",
        "steps": [
            # Step 1: Transaction Details
            {
                "step_number": 1,
                "title": "Transaction Details",
                "description": "Parties involved, purpose of LOI, and key commercial terms.",
                "clauses": [
                    _clause(
                        "loi_party_a_name",
                        "Party A (Proposer)",
                        "text",
                        "Name of the party proposing the transaction",
                        learn_more=(
                            "Party A is the entity initiating the transaction — the one making the offer or "
                            "proposal. This could be an investor proposing a funding deal, a company proposing "
                            "a merger, or a buyer proposing an acquisition. Use the exact legal name of the "
                            "entity as the LOI may be referenced in the subsequent definitive agreement."
                        ),
                    ),
                    _clause(
                        "loi_party_b_name",
                        "Party B (Recipient)",
                        "text",
                        "Name of the party receiving the proposal",
                        learn_more=(
                            "Party B is the entity receiving the proposal — the target company in an M&A deal, "
                            "the startup receiving an investment offer, or the partner in a joint venture. "
                            "Both parties should review the LOI carefully even though it may be non-binding, "
                            "as it sets the framework for subsequent negotiations."
                        ),
                    ),
                    _clause(
                        "loi_purpose",
                        "Purpose of LOI",
                        "dropdown",
                        "Type of transaction the LOI relates to",
                        options=[
                            "Investment/Funding",
                            "Merger or Acquisition",
                            "Joint Venture",
                            "Strategic Partnership",
                            "Asset Purchase",
                            "Licensing Agreement",
                            "Supply/Distribution Agreement",
                            "Other",
                        ],
                        learn_more=(
                            "A Letter of Intent signals serious interest and sets the "
                            "framework for negotiations. It helps both parties understand "
                            "expectations before investing time in detailed agreements."
                        ),
                        india_note=(
                            "LOIs are generally non-binding in India unless explicitly "
                            "stated otherwise. Under Section 2(a) of the Indian Contract "
                            "Act, 1872, a proposal must be made with the intention to "
                            "obtain assent to become an offer. Courts have held that LOIs "
                            "expressing intent to negotiate are not enforceable contracts."
                        ),
                    ),
                    _clause(
                        "loi_description",
                        "Transaction Description",
                        "textarea",
                        "Brief description of the proposed transaction",
                        learn_more=(
                            "Describe the transaction at a high level — what is being proposed, why, and "
                            "the expected outcome. For example: 'Series A equity investment of INR 5 Cr in "
                            "exchange for 15% equity stake' or 'Acquisition of 100% shares of Company B by "
                            "Company A'. This description sets expectations and helps both parties align on "
                            "the fundamental nature of the deal before investing in detailed negotiations."
                        ),
                    ),
                    _clause(
                        "loi_key_terms",
                        "Key Commercial Terms",
                        "textarea",
                        "Outline of key commercial terms (valuation, pricing, quantity, etc.)",
                        learn_more=(
                            "Include enough detail to form a basis for negotiation. "
                            "Key terms typically include pricing or valuation, quantity "
                            "or scope, timeline, and payment structure."
                        ),
                    ),
                    _clause(
                        "loi_exclusivity",
                        "Exclusivity Period",
                        "dropdown",
                        "Whether the recipient must negotiate exclusively with the proposer",
                        options=[
                            "No exclusivity",
                            "30 days exclusivity",
                            "60 days exclusivity",
                            "90 days exclusivity",
                        ],
                        learn_more=(
                            "Exclusivity prevents the recipient from negotiating with other parties during "
                            "the specified period. This is a binding clause even in an otherwise non-binding "
                            "LOI. As a proposer (investor or buyer), exclusivity protects your time and money "
                            "spent on due diligence. As a recipient (startup), granting exclusivity reduces "
                            "your leverage, so negotiate a shorter period. If you choose 'No exclusivity', "
                            "the recipient is free to entertain competing offers simultaneously."
                        ),
                        pros=[
                            "Protects proposer's investment in due diligence",
                            "Shows serious commitment from both sides",
                        ],
                        cons=[
                            "Limits the recipient's ability to explore alternatives",
                            "May create pressure to close quickly",
                        ],
                        common_choice_label="Common: 60 days exclusivity",
                    ),
                    _clause(
                        "loi_proposed_value",
                        "Proposed Transaction Value (INR)",
                        "number",
                        "Estimated value of the proposed transaction in INR",
                        required=False,
                        learn_more=(
                            "The proposed transaction value gives a ballpark figure for the deal size. It is "
                            "typically subject to adjustment after due diligence. For investment deals, this "
                            "is the proposed investment amount. For M&A, this is the enterprise value or "
                            "purchase price. Including a value helps set expectations but remember — since "
                            "the LOI is usually non-binding, this value can change during negotiations."
                        ),
                    ),
                ],
            },
            # Step 2: Conditions & Timelines
            {
                "step_number": 2,
                "title": "Conditions & Timelines",
                "description": "Conditions precedent, due diligence, binding nature, and governing law.",
                "clauses": [
                    _clause(
                        "loi_conditions_precedent",
                        "Conditions Precedent",
                        "multi_select",
                        "Conditions that must be fulfilled before the definitive agreement",
                        options=[
                            "Satisfactory due diligence",
                            "Board approval",
                            "Shareholder approval",
                            "Regulatory approvals",
                            "Third-party consents",
                            "Satisfactory legal review",
                            "Financing arrangement",
                            "No material adverse change",
                        ],
                        learn_more=(
                            "Conditions precedent are requirements that must be met "
                            "before the transaction can proceed. They protect both "
                            "parties and provide exit ramps if key assumptions fail."
                        ),
                    ),
                    _clause(
                        "loi_due_diligence_period",
                        "Due Diligence Period",
                        "dropdown",
                        "Time allowed for conducting due diligence",
                        options=[
                            "15 days",
                            "30 days",
                            "45 days",
                            "60 days",
                            "90 days",
                        ],
                        learn_more=(
                            "The due diligence period is the time the proposer gets to investigate the target's "
                            "financials, legal compliance, contracts, IP, and operations. Thirty days is standard "
                            "for smaller deals. Complex M&A transactions may need 60-90 days. For the recipient, "
                            "prepare a virtual data room with organized documents before this period begins "
                            "to speed things up. A common mistake is underestimating the time needed, leading "
                            "to extensions and deal fatigue."
                        ),
                        common_choice_label="Common: 30 days",
                    ),
                    _clause(
                        "loi_binding_nature",
                        "Binding Nature",
                        "dropdown",
                        "Which parts of the LOI are legally binding",
                        options=[
                            "Entirely non-binding",
                            "Non-binding except confidentiality and exclusivity",
                            "Partially binding (key terms binding)",
                            "Fully binding",
                        ],
                        learn_more=(
                            "Most LOIs are non-binding regarding the main transaction "
                            "terms but contain binding clauses for confidentiality, "
                            "exclusivity, and governing law. This allows parties to "
                            "negotiate freely while protecting sensitive information."
                        ),
                        india_note=(
                            "Indian courts have generally upheld that LOIs are not "
                            "enforceable agreements unless there is clear intent to "
                            "create a binding obligation. The Supreme Court in "
                            "Dresser Rand S.A. v. Bindal Agro Chem Ltd. held that "
                            "an LOI is not a concluded contract."
                        ),
                        common_choice_label="Standard: Non-binding except confidentiality and exclusivity",
                    ),
                    _clause(
                        "loi_confidentiality",
                        "Confidentiality (Binding)",
                        "toggle",
                        "Whether the confidentiality clause is binding regardless of the LOI's overall binding nature",
                        learn_more=(
                            "Confidentiality in an LOI protects sensitive information exchanged during "
                            "negotiations and due diligence. Even if the LOI is otherwise non-binding, the "
                            "confidentiality clause should always be binding. Without it, the recipient could "
                            "share your financial data, business plans, or proprietary information with "
                            "competitors or other potential partners. This should almost always be enabled."
                        ),
                        warning="Disabling confidentiality means shared information has no protection.",
                        warning_condition={"loi_confidentiality": {"eq": False}},
                        common_choice_label="Recommended: Yes",
                    ),
                    _clause(
                        "loi_loi_expiry",
                        "LOI Expiry Date",
                        "date",
                        "Date by which the definitive agreement must be signed, or the LOI lapses",
                        learn_more=(
                            "The expiry date creates urgency and prevents the LOI from hanging indefinitely. "
                            "After this date, the LOI lapses and neither party has any obligation to proceed "
                            "(except surviving clauses like confidentiality). Set a realistic date that allows "
                            "sufficient time for due diligence and negotiation of the definitive agreement. "
                            "Typically 60-90 days from signing the LOI. Extensions can be agreed mutually."
                        ),
                    ),
                    _clause(
                        "loi_costs",
                        "Costs & Expenses",
                        "dropdown",
                        "How transaction costs and expenses are borne",
                        options=[
                            "Each party bears its own costs",
                            "Costs shared equally",
                            "Proposer bears all costs",
                        ],
                        learn_more=(
                            "Transaction costs include legal fees, accounting/audit fees, due diligence "
                            "expenses, and valuation costs. 'Each party bears its own costs' is the standard "
                            "approach and is fairest. 'Costs shared equally' works when both parties equally "
                            "benefit from the transaction. 'Proposer bears all costs' may apply when the "
                            "proposer is eager and the recipient is being courted. If the deal falls through, "
                            "each party typically absorbs their own costs regardless."
                        ),
                        common_choice_label="Standard: Each party bears its own costs",
                    ),
                    _clause(
                        "loi_dispute_resolution",
                        "Dispute Resolution",
                        "dropdown",
                        "How disputes regarding the LOI will be resolved",
                        options=[
                            "Arbitration (Arbitration and Conciliation Act, 1996)",
                            "Mediation followed by arbitration",
                            "Courts only",
                        ],
                        learn_more=(
                            "Dispute resolution for an LOI is particularly relevant for the binding clauses "
                            "(confidentiality, exclusivity). Arbitration is faster and more private than "
                            "Indian courts. Mediation followed by arbitration encourages settlement first. "
                            "Courts should be a last resort due to the Indian judicial system's backlog. "
                            "This clause also survives the LOI's expiry for any disputes that arise from "
                            "the binding sections."
                        ),
                        common_choice_label="Standard: Arbitration",
                    ),
                    _clause(
                        "loi_governing_law",
                        "Governing Law (State)",
                        "text",
                        "Indian state whose laws will govern this LOI",
                        learn_more=(
                            "The governing law state determines which state's laws interpret the LOI and where "
                            "disputes are resolved. This is a binding clause that survives even in an otherwise "
                            "non-binding LOI. Choose the state where the proposer or the transaction's primary "
                            "activity is located. For cross-border deals, Indian law typically governs if the "
                            "target company is Indian."
                        ),
                    ),
                ],
            },
        ],
    }


def render_letter_of_intent(tpl: dict, config: dict, parties: dict) -> str:
    """Render Letter of Intent HTML."""
    party_a = config.get("loi_party_a_name", "[Party A]")
    party_b = config.get("loi_party_b_name", "[Party B]")
    purpose = config.get("loi_purpose", "[Purpose]")
    description = config.get("loi_description", "[Transaction Description]")
    key_terms = config.get("loi_key_terms", "[Key Terms]")
    exclusivity = config.get("loi_exclusivity", "No exclusivity")
    proposed_value = config.get("loi_proposed_value", 0)
    conditions = config.get("loi_conditions_precedent", [])
    dd_period = config.get("loi_due_diligence_period", "30 days")
    binding = config.get("loi_binding_nature", "Non-binding except confidentiality and exclusivity")
    confidentiality = config.get("loi_confidentiality", True)
    expiry = config.get("loi_loi_expiry", "")
    costs = config.get("loi_costs", "Each party bears its own costs")
    dispute = config.get("loi_dispute_resolution", "Arbitration (Arbitration and Conciliation Act, 1996)")
    governing = config.get("loi_governing_law", "[State]")

    sections: List[str] = []

    # Parties
    sections.append(
        f'<div class="parties">'
        f'<p>This Letter of Intent ("LOI") is issued by:</p>'
        f'<p><strong>From:</strong> {party_a} ("Party A" / "Proposer")</p>'
        f'<p><strong>To:</strong> {party_b} ("Party B" / "Recipient")</p>'
        f'</div>'
    )

    # Section 1 — Purpose
    cn = 1
    sections.append(
        f'<h2>{cn}. Purpose</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This LOI sets forth the intention of the parties to enter into a '
        f'<strong>{purpose}</strong> transaction, subject to the terms and '
        f'conditions outlined herein and the execution of a definitive agreement.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Transaction Description:</strong></p>'
        f'<p class="clause"><em>{description}</em></p>'
    )

    # Section 2 — Key Terms
    cn += 1
    sections.append(
        f'<h2>{cn}. Key Commercial Terms</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The key terms of the proposed transaction are as follows:</p>'
        f'<p class="clause"><em>{key_terms}</em></p>'
    )
    if proposed_value and proposed_value > 0:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'<strong>Proposed Transaction Value:</strong> INR {proposed_value:,}.</p>'
        )

    # Section 3 — Due Diligence
    cn += 1
    sections.append(
        f'<h2>{cn}. Due Diligence</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'Party A shall be entitled to conduct due diligence on Party B '
        f'(and/or the subject matter of the transaction) for a period of '
        f'<strong>{dd_period}</strong> from the date of this LOI.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'Party B shall provide reasonable access to information, documents, '
        f'and personnel as may be necessary for the due diligence process.</p>'
    )

    # Section 4 — Conditions Precedent
    cn += 1
    sections.append(
        f'<h2>{cn}. Conditions Precedent</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The execution of the definitive agreement shall be subject to the '
        f'following conditions precedent:</p>'
        f'{_list_html(conditions) if conditions else "<p>To be determined during negotiations.</p>"}'
    )

    # Section 5 — Exclusivity
    cn += 1
    sections.append(
        f'<h2>{cn}. Exclusivity</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Exclusivity:</strong> {exclusivity}.</p>'
    )
    if exclusivity != "No exclusivity":
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'During the exclusivity period, Party B shall not solicit, negotiate, '
            f'or enter into any agreement with any third party regarding a similar '
            f'transaction. This exclusivity clause is binding on both parties.</p>'
        )

    # Section 6 — Binding Nature & Confidentiality
    cn += 1
    sections.append(
        f'<h2>{cn}. Binding Nature & Confidentiality</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Binding Nature:</strong> {binding}.</p>'
    )
    if "non-binding" in binding.lower() or "Non-binding" in binding:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Except as expressly stated herein, this LOI does not create a '
            f'legally binding obligation on either party to consummate the '
            f'proposed transaction.</p>'
        )
    if confidentiality:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'<strong>Confidentiality (Binding):</strong> Both parties agree to '
            f'keep the existence and terms of this LOI, and all information '
            f'exchanged during negotiations and due diligence, strictly '
            f'confidential. This obligation is binding regardless of whether '
            f'the transaction is consummated.</p>'
        )

    # Section 7 — Costs & Expenses
    cn += 1
    sections.append(
        f'<h2>{cn}. Costs & Expenses</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'{costs}. Unless otherwise agreed in writing, neither party shall be '
        f'liable for the other party\'s costs incurred in connection with the '
        f'negotiation and execution of this LOI or the definitive agreement.</p>'
    )

    # Section 8 — General
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This LOI shall expire on '
        f'<strong>{expiry or "________________________"}</strong> unless '
        f'a definitive agreement is executed before that date or the parties '
        f'mutually agree to extend.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'<strong>Dispute Resolution:</strong> {dispute}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This LOI shall be governed by the laws of '
        f'<strong>{governing}</strong>, India.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.4</span> '
        f'This LOI may be executed in counterparts and delivered electronically, '
        f'each of which shall be deemed an original.</p>'
    )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Signatures</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the parties have executed this '
        'Letter of Intent as of the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{party_a}</strong> (Proposer)</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{party_b}</strong> (Recipient)</p>'
        '<p>Authorized Signatory</p>'
        '<p>Date: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Letter of Intent \u2014 {purpose}", body
    )


# ======================================================================
# TEMPLATE 23: POWER OF ATTORNEY (POA)
# ======================================================================

def power_of_attorney_template() -> dict:
    """Template 23 — Power of Attorney (POA)."""
    return {
        "name": "Power of Attorney (POA)",
        "description": (
            "A legal instrument authorizing one person (agent/attorney) to act "
            "on behalf of another (principal). Commonly used for property "
            "transactions, business operations, legal proceedings, and "
            "administrative matters in India."
        ),
        "category": "Corporate Governance",
        "steps": [
            # Step 1: Principal & Agent
            {
                "step_number": 1,
                "title": "Principal & Agent",
                "description": "Details of the principal, agent, POA type, and powers granted.",
                "clauses": [
                    _clause(
                        "poa_principal_name",
                        "Principal Name",
                        "text",
                        "Full name of the principal (person granting the power)",
                        learn_more=(
                            "The principal is the person who authorizes another to "
                            "act on their behalf. A company can also be a principal, "
                            "in which case a board resolution authorizing the POA "
                            "is required."
                        ),
                    ),
                    _clause(
                        "poa_principal_address",
                        "Principal Address",
                        "textarea",
                        "Complete address of the principal",
                        learn_more=(
                            "The principal's address is important for identification and is required for stamp "
                            "duty calculation and registration. If the POA involves immovable property, this "
                            "address helps determine the applicable sub-registrar's office. Enter the complete "
                            "address including city, state, and PIN code."
                        ),
                    ),
                    _clause(
                        "poa_agent_name",
                        "Agent / Attorney Name",
                        "text",
                        "Full name of the agent (person receiving the power)",
                        learn_more=(
                            "The agent (also called attorney-in-fact or donee) is "
                            "the person authorized to act on behalf of the principal. "
                            "Choose a trusted individual as they will have legal "
                            "authority to act in your name."
                        ),
                    ),
                    _clause(
                        "poa_agent_address",
                        "Agent Address",
                        "textarea",
                        "Complete address of the agent",
                        learn_more=(
                            "The agent's complete address is needed for identification and to serve any "
                            "notices related to the POA. Third parties dealing with the agent may verify "
                            "this address. If the agent is in a different city from the principal, consider "
                            "the practical implications of the agent executing documents or appearing at "
                            "offices in the principal's location."
                        ),
                    ),
                    _clause(
                        "poa_type",
                        "POA Type",
                        "dropdown",
                        "Type of Power of Attorney",
                        options=[
                            "General Power of Attorney",
                            "Special Power of Attorney",
                        ],
                        learn_more=(
                            "A General POA grants broad authority to act on behalf "
                            "of the principal in multiple matters. A Special POA is "
                            "limited to specific acts or transactions. Special POAs "
                            "are safer as they limit the agent's authority."
                        ),
                        india_note=(
                            "Under the Powers of Attorney Act, 1882, a POA executed "
                            "in India must be stamped as per the applicable state's "
                            "Stamp Act. Stamp duty varies significantly by state. "
                            "A General POA typically attracts higher stamp duty than "
                            "a Special POA."
                        ),
                        pros=["General: Flexibility; Special: Limited risk"],
                        cons=["General: Higher risk of misuse; Special: Limited scope"],
                        common_choice_label="Recommended: Special Power of Attorney",
                    ),
                    _clause(
                        "poa_powers_granted",
                        "Powers Granted",
                        "multi_select",
                        "Specific powers being granted to the agent",
                        options=[
                            "Execute and sign documents",
                            "Operate bank accounts",
                            "Buy/sell/lease immovable property",
                            "Represent in legal proceedings",
                            "File applications with government authorities",
                            "Collect payments and issue receipts",
                            "Enter into contracts",
                            "Manage day-to-day business operations",
                            "Appear before tax authorities",
                            "Handle regulatory compliance and filings",
                        ],
                        learn_more=(
                            "Select only the specific powers the agent needs. Granting too many powers creates "
                            "risk of misuse. For a Special POA, select only what is necessary for the specific "
                            "task. For example, if the POA is only for filing GST returns, select 'Appear before "
                            "tax authorities' and 'File applications with government authorities' only. Bank "
                            "account operation and property powers carry the highest risk and should only be "
                            "granted to highly trusted individuals. Property transactions through POA require "
                            "registration under the Registration Act, 1908."
                        ),
                        india_note=(
                            "For immovable property transactions, the POA must be "
                            "registered under Section 33 of the Registration Act, "
                            "1908. An unregistered POA for property transactions is "
                            "not legally valid. The Supreme Court in Suraj Lamp & "
                            "Industries v. State of Haryana held that sale of "
                            "immovable property through GPA is not legally valid."
                        ),
                    ),
                    _clause(
                        "poa_purpose",
                        "Specific Purpose (if Special POA)",
                        "textarea",
                        "Detailed description of the specific purpose or transaction for which the POA is granted",
                        required=False,
                        depends_on="poa_type",
                        learn_more=(
                            "For a Special POA, clearly describe the specific transaction or purpose. Be as "
                            "detailed as possible — for example: 'To execute the sale deed for property at "
                            "Survey No. 123, Village X, District Y on behalf of the principal' or 'To represent "
                            "the principal before the GST authorities in Appeal No. XYZ'. A vague purpose "
                            "defeats the security advantage of a Special POA."
                        ),
                    ),
                ],
            },
            # Step 2: Terms & Conditions
            {
                "step_number": 2,
                "title": "Terms & Conditions",
                "description": "Duration, revocation, compensation, and governing law.",
                "clauses": [
                    _clause(
                        "poa_duration",
                        "Duration",
                        "dropdown",
                        "How long the POA remains in effect",
                        options=[
                            "Until revoked",
                            "6 months",
                            "1 year",
                            "2 years",
                            "Specific date",
                            "Until completion of specified transaction",
                        ],
                        learn_more=(
                            "A POA 'until revoked' remains valid until the principal "
                            "explicitly revokes it or becomes incapacitated. Setting "
                            "a specific duration is safer as it auto-expires."
                        ),
                        common_choice_label="Recommended: 1 year or until completion",
                    ),
                    _clause(
                        "poa_expiry_date",
                        "Expiry Date (if applicable)",
                        "date",
                        "Specific date on which the POA expires",
                        required=False,
                        depends_on="poa_duration",
                        learn_more=(
                            "Setting a specific expiry date is safer than open-ended or 'until revoked' POAs. "
                            "After this date, the POA automatically becomes invalid and the agent can no longer "
                            "act. This prevents the POA from being used indefinitely if the principal forgets "
                            "to revoke it. Banks and government offices may check the expiry date before "
                            "accepting actions under the POA."
                        ),
                    ),
                    _clause(
                        "poa_revocation",
                        "Revocation Terms",
                        "dropdown",
                        "How the principal can revoke the POA",
                        options=[
                            "Revocable at any time with written notice",
                            "Revocable with 30 days written notice",
                            "Irrevocable (coupled with interest)",
                        ],
                        learn_more=(
                            "Most POAs are revocable. An irrevocable POA is valid "
                            "only when it is 'coupled with interest' — meaning the "
                            "agent has a financial interest in the subject matter. "
                            "Under Section 202 of the Indian Contract Act, a POA "
                            "coupled with interest cannot be revoked."
                        ),
                        india_note=(
                            "Under Section 201 of the Indian Contract Act, 1872, "
                            "a principal may revoke the authority of the agent at "
                            "any time before the authority has been exercised, unless "
                            "the agency is coupled with interest (Section 202)."
                        ),
                        common_choice_label="Standard: Revocable at any time with written notice",
                    ),
                    _clause(
                        "poa_sub_delegation",
                        "Sub-Delegation",
                        "toggle",
                        "Whether the agent can delegate powers to another person",
                        learn_more=(
                            "Sub-delegation allows the agent to appoint a substitute. "
                            "This is generally risky unless specifically needed. The "
                            "maxim 'delegatus non potest delegare' applies."
                        ),
                        common_choice_label="Standard: No",
                    ),
                    _clause(
                        "poa_compensation",
                        "Agent Compensation",
                        "dropdown",
                        "Whether the agent receives compensation for acting under the POA",
                        options=[
                            "No compensation (gratuitous)",
                            "Fixed fee",
                            "Reasonable expenses reimbursed",
                            "Fee plus expenses",
                        ],
                        learn_more=(
                            "Gratuitous (no compensation) POAs are common when the agent is a family member "
                            "or trusted associate. Professional agents or lawyers typically charge a fixed fee "
                            "or fee plus expenses. Even in a gratuitous POA, the principal should reimburse "
                            "reasonable expenses (travel, filing fees, notarization costs) incurred by the "
                            "agent while performing duties. Under Section 222 of the Indian Contract Act, the "
                            "principal is bound to indemnify the agent for expenses properly incurred."
                        ),
                        common_choice_label="Common: Reasonable expenses reimbursed",
                    ),
                    _clause(
                        "poa_indemnity",
                        "Indemnification",
                        "toggle",
                        "Whether the principal indemnifies the agent for actions taken in good faith under the POA",
                        learn_more=(
                            "Indemnification protects the agent from liability for "
                            "actions taken within the scope of the POA and in good "
                            "faith. This encourages the agent to act without fear "
                            "of personal liability."
                        ),
                        common_choice_label="Standard: Yes",
                    ),
                    _clause(
                        "poa_registration_required",
                        "Registration Required",
                        "toggle",
                        "Whether this POA needs to be registered with the Sub-Registrar",
                        learn_more=(
                            "Registration is the process of recording the POA with the Sub-Registrar of "
                            "Assurances in the relevant district. This is MANDATORY for POAs involving "
                            "immovable property (buying, selling, or leasing land/buildings). For other POAs, "
                            "notarization is usually sufficient but registration adds an extra layer of "
                            "authenticity. Registration involves stamp duty costs that vary by state."
                        ),
                        india_note=(
                            "Registration is mandatory for POAs relating to immovable "
                            "property (Section 33, Registration Act, 1908). For other "
                            "POAs, notarization is sufficient. Stamp duty must be paid "
                            "as per the state's Stamp Act."
                        ),
                        warning="POAs for immovable property MUST be registered",
                        common_choice_label="Required for property matters: Yes",
                    ),
                    _clause(
                        "poa_governing_law",
                        "Governing Law (State)",
                        "text",
                        "Indian state whose laws and stamp duty rates apply",
                        learn_more=(
                            "The governing law state is crucial for POAs because stamp duty rates vary "
                            "significantly between Indian states. For example, stamp duty for a General POA "
                            "in Maharashtra is different from Karnataka or Delhi. The POA should be stamped "
                            "and notarized/registered in the state where it will be primarily used. If the "
                            "principal and agent are in different states, use the state where the agent will "
                            "exercise the powers."
                        ),
                    ),
                ],
            },
        ],
    }


def render_power_of_attorney(tpl: dict, config: dict, parties: dict) -> str:
    """Render Power of Attorney HTML."""
    principal = config.get("poa_principal_name", "[Principal Name]")
    principal_addr = config.get("poa_principal_address", "[Principal Address]")
    agent = config.get("poa_agent_name", "[Agent Name]")
    agent_addr = config.get("poa_agent_address", "[Agent Address]")
    poa_type = config.get("poa_type", "Special Power of Attorney")
    powers = config.get("poa_powers_granted", [])
    purpose = config.get("poa_purpose", "")
    duration = config.get("poa_duration", "1 year")
    expiry_date = config.get("poa_expiry_date", "")
    revocation = config.get("poa_revocation", "Revocable at any time with written notice")
    sub_delegation = config.get("poa_sub_delegation", False)
    compensation = config.get("poa_compensation", "No compensation (gratuitous)")
    indemnity = config.get("poa_indemnity", True)
    registration = config.get("poa_registration_required", False)
    governing = config.get("poa_governing_law", "[State]")

    sections: List[str] = []

    # Header
    sections.append(
        f'<div class="parties">'
        f'<p><strong>{poa_type}</strong></p>'
        f'<p>KNOW ALL MEN BY THESE PRESENTS that:</p>'
        f'<p><strong>Principal:</strong> {principal}</p>'
        f'<p><strong>Address:</strong> {principal_addr}</p>'
        f'<p>hereby appoints:</p>'
        f'<p><strong>Agent / Attorney:</strong> {agent}</p>'
        f'<p><strong>Address:</strong> {agent_addr}</p>'
        f'<p>as the true and lawful attorney of the Principal to act on behalf '
        f'of and in the name of the Principal as set forth herein.</p>'
        f'</div>'
    )

    # Section 1 — Grant of Authority
    cn = 1
    sections.append(
        f'<h2>{cn}. Grant of Authority</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Principal hereby grants the Agent the following powers and '
        f'authority to act on behalf of the Principal:</p>'
        f'{_list_html(powers) if powers else "<p>As specified by the Principal.</p>"}'
    )
    if purpose:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'<strong>Specific Purpose:</strong> {purpose}</p>'
        )

    # Section 2 — Scope
    cn += 1
    sections.append(
        f'<h2>{cn}. Scope of Authority</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Agent shall act within the scope of authority granted herein and '
        f'shall not exceed the powers specifically conferred by this '
        f'{poa_type}.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'All acts done by the Agent within the scope of this Power of Attorney '
        f'shall be deemed to have been done by the Principal and shall be '
        f'binding on the Principal.</p>'
    )

    # Section 3 — Duration
    cn += 1
    sections.append(
        f'<h2>{cn}. Duration</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Power of Attorney shall remain in effect for: '
        f'<strong>{duration}</strong>.</p>'
    )
    if expiry_date:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'This POA shall expire on <strong>{expiry_date}</strong>.</p>'
        )
    sections.append(
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'This Power of Attorney shall automatically terminate upon the death '
        f'or incapacity of the Principal, unless it is an irrevocable POA '
        f'coupled with interest.</p>'
    )

    # Section 4 — Revocation
    cn += 1
    sections.append(
        f'<h2>{cn}. Revocation</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Revocation:</strong> {revocation}.</p>'
    )
    if "Irrevocable" in revocation:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'This Power of Attorney is irrevocable as it is coupled with '
            f'interest within the meaning of Section 202 of the Indian Contract '
            f'Act, 1872. The Agent has a subsisting interest in the subject '
            f'matter of this POA.</p>'
        )
    else:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Upon revocation, the Agent shall immediately cease to exercise '
            f'any powers under this POA and shall return all documents and '
            f'property of the Principal.</p>'
        )

    # Section 5 — Sub-Delegation
    cn += 1
    sections.append(
        f'<h2>{cn}. Sub-Delegation</h2>'
    )
    if sub_delegation:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Agent is authorized to appoint one or more substitutes or '
            f'sub-agents to exercise the powers granted hereunder, subject to '
            f'the same terms and conditions.</p>'
        )
    else:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Agent shall not delegate or assign any of the powers granted '
            f'under this POA to any other person without the prior written '
            f'consent of the Principal.</p>'
        )

    # Section 6 — Compensation & Indemnity
    cn += 1
    sections.append(
        f'<h2>{cn}. Compensation & Indemnity</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'<strong>Compensation:</strong> {compensation}.</p>'
    )
    if indemnity:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Principal shall indemnify and hold harmless the Agent from '
            f'and against all claims, losses, damages, and expenses arising '
            f'out of or in connection with any action taken by the Agent in '
            f'good faith and within the scope of this Power of Attorney.</p>'
        )

    # Section 7 — Agent Obligations
    cn += 1
    sections.append(
        f'<h2>{cn}. Agent Obligations</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The Agent shall act in good faith and in the best interest of the '
        f'Principal at all times.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'The Agent shall maintain proper records of all transactions and '
        f'actions taken on behalf of the Principal and shall provide periodic '
        f'reports to the Principal.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.3</span> '
        f'The Agent shall not use the powers granted herein for personal '
        f'benefit or for any purpose other than as specified in this POA.</p>'
    )

    # Section 8 — General
    cn += 1
    sections.append(
        f'<h2>{cn}. General Provisions</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'This Power of Attorney is executed under the provisions of the '
        f'Powers of Attorney Act, 1882, and the Indian Contract Act, 1872.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'This POA shall be governed by the laws of '
        f'<strong>{governing}</strong>, India.</p>'
    )
    if registration:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'This Power of Attorney shall be registered with the '
            f'Sub-Registrar of Assurances as required under the Registration '
            f'Act, 1908. Stamp duty shall be paid as per the applicable state '
            f'Stamp Act.</p>'
        )
    else:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'This Power of Attorney shall be duly notarized. Stamp duty '
            f'shall be paid as per the applicable state Stamp Act.</p>'
        )

    # Signature block
    sections.append(
        '<div class="signature-block"><h2>Executed</h2>'
        '<p class="clause">IN WITNESS WHEREOF, the Principal has executed this '
        'Power of Attorney on the date first written above.</p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{principal}</strong> (Principal / Executant)</p>'
        '<p>Date: ________________________</p></div>'
        '<p class="clause"><strong>Accepted by Agent:</strong></p>'
        '<div class="signature-line"><div class="line"></div>'
        f'<p><strong>{agent}</strong> (Agent / Attorney)</p>'
        '<p>Date: ________________________</p></div>'
        '<p class="clause"><strong>Witnesses:</strong></p>'
        '<div class="signature-line"><div class="line"></div>'
        '<p>1. Name: ________________________</p>'
        '<p>Address: ________________________</p></div>'
        '<div class="signature-line"><div class="line"></div>'
        '<p>2. Name: ________________________</p>'
        '<p>Address: ________________________</p></div></div>'
    )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"{poa_type} \u2014 {principal}", body
    )


# ======================================================================
# TEMPLATE 24: LEGAL NOTICE / DEMAND LETTER
# ======================================================================

def legal_notice_template() -> dict:
    """Template 24 — Legal Notice / Demand Letter."""
    return {
        "name": "Legal Notice / Demand Letter",
        "description": (
            "A formal legal notice or demand letter to be sent before initiating "
            "legal proceedings. Used for breach of contract, payment recovery, "
            "IP infringement, defamation, and other civil disputes. Often a "
            "mandatory pre-litigation step in India."
        ),
        "category": "Dispute Resolution",
        "steps": [
            # Step 1: Parties & Grievance
            {
                "step_number": 1,
                "title": "Parties & Grievance",
                "description": "Sender, recipient, subject matter, facts, legal basis, and demand.",
                "clauses": [
                    _clause(
                        "ln_sender_name",
                        "Sender (Complainant)",
                        "text",
                        "Full name of the sender/complainant",
                        learn_more=(
                            "The sender is the person or entity with the grievance. Use your full legal name "
                            "or your company's registered name. If sending through an advocate, the advocate "
                            "sends 'on behalf of' the sender. The sender's identity establishes standing "
                            "(locus standi) — only the aggrieved party or their authorized representative can "
                            "send a legal notice."
                        ),
                    ),
                    _clause(
                        "ln_sender_address",
                        "Sender Address",
                        "textarea",
                        "Complete address of the sender",
                        learn_more=(
                            "The sender's address is included for identification and for the recipient to "
                            "send a reply. If using an advocate, the advocate's office address may be used "
                            "as the correspondence address. Ensure the address is complete with PIN code "
                            "so any reply or legal proceedings can be properly served."
                        ),
                    ),
                    _clause(
                        "ln_recipient_name",
                        "Recipient (Noticee)",
                        "text",
                        "Full name of the recipient/noticee",
                        learn_more=(
                            "The recipient is the person or entity against whom the grievance exists. Use "
                            "their exact legal name. If the recipient is a company, use the registered company "
                            "name along with the name of a director or authorized representative. Sending the "
                            "notice to the wrong entity or person may render it legally ineffective."
                        ),
                    ),
                    _clause(
                        "ln_recipient_address",
                        "Recipient Address",
                        "textarea",
                        "Complete address of the recipient (notice will be sent here)",
                        learn_more=(
                            "Use the recipient's registered office address (for companies) or residential "
                            "address (for individuals). The notice is legally deemed served when delivered at "
                            "this address, even if the recipient refuses to accept it. For companies, you can "
                            "find the registered address on the MCA portal. Send to both the registered office "
                            "and the last known business address for better chances of actual receipt."
                        ),
                    ),
                    _clause(
                        "ln_subject",
                        "Subject Matter",
                        "dropdown",
                        "Category of the legal notice",
                        options=[
                            "Breach of Contract",
                            "Recovery of Dues/Payment",
                            "Intellectual Property Infringement",
                            "Defamation",
                            "Property Dispute",
                            "Employment Dispute",
                            "Consumer Complaint",
                            "Partnership Dispute",
                            "Cheque Bounce (Section 138 NI Act)",
                            "Other Civil Matter",
                        ],
                        learn_more=(
                            "Legal notices serve as formal communication of grievance "
                            "and demand. They often lead to out-of-court settlement "
                            "and are a prerequisite for certain types of litigation."
                        ),
                        india_note=(
                            "Legal notices are mandatory before filing suits against "
                            "the government (Section 80 CPC). Under the Consumer "
                            "Protection Act, 2019, a notice to the opposite party is "
                            "recommended. For cheque bounce cases under Section 138 "
                            "of the Negotiable Instruments Act, a demand notice must "
                            "be sent within 30 days of cheque return."
                        ),
                    ),
                    _clause(
                        "ln_facts",
                        "Statement of Facts",
                        "textarea",
                        "Detailed factual background of the dispute (chronological order recommended)",
                        learn_more=(
                            "State facts clearly and chronologically. Include dates, "
                            "amounts, agreements referenced, and any prior communication. "
                            "Avoid emotional language and stick to verifiable facts."
                        ),
                    ),
                    _clause(
                        "ln_legal_basis",
                        "Legal Basis",
                        "textarea",
                        "Legal provisions, sections, and acts under which the claim is made",
                        learn_more=(
                            "Cite specific sections of applicable laws to strengthen "
                            "the notice. For example: Section 73 of Indian Contract Act "
                            "for breach damages, Section 138 of NI Act for cheque bounce, "
                            "Section 51 of Copyright Act for infringement."
                        ),
                        india_note=(
                            "For MSME payment disputes, cite Section 15-18 of the "
                            "MSMED Act, 2006, which mandates payment within 45 days "
                            "and entitles the supplier to compound interest at three "
                            "times the bank rate. For consumer disputes, cite the "
                            "Consumer Protection Act, 2019."
                        ),
                    ),
                    _clause(
                        "ln_demand",
                        "Demand / Relief Sought",
                        "textarea",
                        "Specific demand or relief sought from the recipient",
                        learn_more=(
                            "Be specific about what you want: payment of a specific "
                            "amount, cessation of infringing activity, performance "
                            "of obligations, apology, or any other specific relief."
                        ),
                    ),
                    _clause(
                        "ln_amount_claimed",
                        "Amount Claimed (INR)",
                        "number",
                        "Total monetary amount claimed, if applicable (enter 0 if non-monetary)",
                        required=False,
                        learn_more=(
                            "Specify the exact monetary amount you are claiming, including the principal amount, "
                            "interest, and any damages. Be precise — courts look at the amount claimed in the "
                            "notice when assessing the claim. For cheque bounce cases under Section 138 NI Act, "
                            "the amount is the cheque amount. For breach of contract, include both the direct "
                            "loss and any consequential damages you can quantify. Enter 0 for non-monetary "
                            "demands like cease-and-desist or specific performance."
                        ),
                    ),
                ],
            },
            # Step 2: Terms
            {
                "step_number": 2,
                "title": "Terms",
                "description": "Response deadline, consequences, and governing law.",
                "clauses": [
                    _clause(
                        "ln_response_deadline",
                        "Response Deadline",
                        "dropdown",
                        "Time given to the recipient to respond or comply",
                        options=[
                            "7 days",
                            "15 days",
                            "30 days",
                            "45 days",
                            "60 days",
                        ],
                        learn_more=(
                            "The standard response period is 15-30 days. For cheque "
                            "bounce notices under Section 138 NI Act, the payment "
                            "must be made within 15 days of receipt. For government "
                            "notices under Section 80 CPC, 2 months' notice is required."
                        ),
                        india_note=(
                            "For Section 138 NI Act (cheque bounce), the payee must "
                            "send notice within 30 days of receiving 'cheque returned' "
                            "memo and demand payment within 15 days. For government "
                            "bodies, Section 80 CPC requires a 2-month notice period."
                        ),
                        common_choice_label="Standard: 15 days",
                    ),
                    _clause(
                        "ln_consequences",
                        "Consequences of Non-Compliance",
                        "multi_select",
                        "Actions that will be taken if the recipient fails to comply",
                        options=[
                            "File civil suit for recovery",
                            "File criminal complaint",
                            "Approach consumer forum",
                            "Initiate arbitration proceedings",
                            "File complaint with regulatory authority",
                            "Seek injunction from court",
                            "File winding-up petition",
                            "Report to police/cybercrime cell",
                            "Claim interest and damages",
                        ],
                        learn_more=(
                            "Clearly state the consequences to demonstrate seriousness. "
                            "However, avoid making threats that you do not intend to or "
                            "cannot legally follow through on."
                        ),
                    ),
                    _clause(
                        "ln_prior_communication",
                        "Prior Communication Reference",
                        "textarea",
                        "References to any prior emails, letters, or communication regarding this matter",
                        required=False,
                        learn_more=(
                            "Referencing prior communication shows that you attempted to resolve the matter "
                            "before sending a legal notice. Cite specific emails, letters, WhatsApp messages, "
                            "or meeting dates. For example: 'Email dated 15 Jan 2025 requesting payment' or "
                            "'Letter ref no. ABC/2025 sent via courier'. This strengthens your case by "
                            "demonstrating the recipient was given a fair chance to resolve the issue."
                        ),
                    ),
                    _clause(
                        "ln_documents_enclosed",
                        "Documents Enclosed",
                        "textarea",
                        "List of supporting documents enclosed with the notice (if any)",
                        required=False,
                        learn_more=(
                            "Listing enclosed documents adds weight to your notice and puts the recipient on "
                            "notice about the evidence you hold. Common enclosures include copies of contracts, "
                            "invoices, bounced cheque copies, email printouts, and bank statements. Only enclose "
                            "copies, never originals. If you prefer to reserve evidence for court, you can "
                            "leave this blank and state that documents will be produced at the appropriate forum."
                        ),
                    ),
                    _clause(
                        "ln_send_via",
                        "Mode of Sending",
                        "dropdown",
                        "How the notice will be sent to the recipient",
                        options=[
                            "Registered Post with AD",
                            "Speed Post",
                            "Courier with acknowledgment",
                            "Email (with delivery receipt)",
                            "Registered Post and Email both",
                        ],
                        learn_more=(
                            "The mode of sending determines whether you can prove the notice was delivered. "
                            "Registered Post with Acknowledgment Due (RPAD) is the gold standard — Indian "
                            "courts universally accept it as proof of service. Speed Post provides tracking "
                            "but no signed acknowledgment. Email delivery receipts are increasingly accepted "
                            "but should supplement, not replace, physical delivery for important matters. "
                            "Sending via both Registered Post and Email provides the strongest proof of service."
                        ),
                        india_note=(
                            "Registered Post with Acknowledgment Due (AD) is the "
                            "preferred mode for legal notices in India. Courts "
                            "consider RPAD as valid service. Email notices are "
                            "increasingly accepted but should be supplemented with "
                            "physical delivery for important matters."
                        ),
                        common_choice_label="Recommended: Registered Post with AD",
                    ),
                    _clause(
                        "ln_advocate_name",
                        "Advocate Name (if sent through advocate)",
                        "text",
                        "Name of the advocate sending the notice on behalf of the sender",
                        required=False,
                        learn_more=(
                            "A notice sent through an advocate carries more weight. "
                            "However, a legal notice can also be sent directly by "
                            "the aggrieved party without involving a lawyer."
                        ),
                    ),
                    _clause(
                        "ln_advocate_enrollment",
                        "Advocate Enrollment Number",
                        "text",
                        "Bar Council enrollment number of the advocate",
                        required=False,
                        depends_on="ln_advocate_name",
                        learn_more=(
                            "The Bar Council enrollment number uniquely identifies the advocate and confirms "
                            "they are a licensed legal practitioner. This adds credibility to the notice and "
                            "allows the recipient to verify the advocate's credentials through the Bar Council "
                            "of India's website. An advocate sending a notice without their enrollment number "
                            "may not be taken as seriously."
                        ),
                    ),
                    _clause(
                        "ln_governing_law",
                        "Jurisdiction",
                        "text",
                        "City and state whose courts will have jurisdiction",
                        learn_more=(
                            "Jurisdiction determines where legal proceedings will be initiated if the notice "
                            "does not result in resolution. Typically, you can choose the courts where the "
                            "cause of action arose, where the defendant resides, or where the contract was "
                            "to be performed. For cheque bounce cases, jurisdiction lies where the cheque was "
                            "presented or where the payee's bank is located. Enter both city and state for clarity."
                        ),
                    ),
                ],
            },
        ],
    }


def render_legal_notice(tpl: dict, config: dict, parties: dict) -> str:
    """Render Legal Notice / Demand Letter HTML."""
    sender = config.get("ln_sender_name", "[Sender Name]")
    sender_addr = config.get("ln_sender_address", "[Sender Address]")
    recipient = config.get("ln_recipient_name", "[Recipient Name]")
    recipient_addr = config.get("ln_recipient_address", "[Recipient Address]")
    subject = config.get("ln_subject", "[Subject]")
    facts = config.get("ln_facts", "[Statement of Facts]")
    legal_basis = config.get("ln_legal_basis", "[Legal Basis]")
    demand = config.get("ln_demand", "[Demand]")
    amount = config.get("ln_amount_claimed", 0)
    deadline = config.get("ln_response_deadline", "15 days")
    consequences = config.get("ln_consequences", [])
    prior_comm = config.get("ln_prior_communication", "")
    docs_enclosed = config.get("ln_documents_enclosed", "")
    send_via = config.get("ln_send_via", "Registered Post with AD")
    advocate = config.get("ln_advocate_name", "")
    advocate_enroll = config.get("ln_advocate_enrollment", "")
    governing = config.get("ln_governing_law", "[City, State]")

    sections: List[str] = []

    # Header — To/From
    sections.append(
        f'<div class="parties">'
        f'<p><strong>LEGAL NOTICE</strong></p>'
        f'<p><strong>Sent via:</strong> {send_via}</p>'
    )
    if advocate:
        sections.append(
            f'<p><strong>Through:</strong> {advocate}, Advocate'
            f'{" (Enrollment No. " + advocate_enroll + ")" if advocate_enroll else ""}</p>'
        )
    sections.append(
        f'<p><strong>On behalf of:</strong> {sender}</p>'
        f'<p><strong>Address:</strong> {sender_addr}</p>'
        f'<hr>'
        f'<p><strong>To:</strong> {recipient}</p>'
        f'<p><strong>Address:</strong> {recipient_addr}</p>'
        f'</div>'
    )

    # Subject
    sections.append(
        f'<p class="clause"><strong>Subject:</strong> Legal Notice regarding '
        f'{subject}</p>'
    )

    # Section 1 — Notice
    cn = 1
    under_instructions = (
        f"Under instructions from and on behalf of my client, "
        f"<strong>{sender}</strong>, I hereby serve upon you this legal notice "
        f"as follows:"
    ) if advocate else (
        f"I, <strong>{sender}</strong>, hereby serve upon you this legal "
        f"notice as follows:"
    )
    sections.append(
        f'<h2>{cn}. Notice</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'{under_instructions}</p>'
    )

    # Section 2 — Facts
    cn += 1
    sections.append(
        f'<h2>{cn}. Statement of Facts</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'{facts}</p>'
    )
    if prior_comm:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'<strong>Prior Communication:</strong> {prior_comm}</p>'
        )

    # Section 3 — Legal Basis
    cn += 1
    sections.append(
        f'<h2>{cn}. Legal Basis</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'{legal_basis}</p>'
    )

    # Section 4 — Demand
    cn += 1
    sections.append(
        f'<h2>{cn}. Demand</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'In view of the above facts and legal position, '
        f'{"my client demands" if advocate else "I hereby demand"} '
        f'the following:</p>'
        f'<p class="clause"><em>{demand}</em></p>'
    )
    if amount and amount > 0:
        sections.append(
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'<strong>Amount Claimed:</strong> INR {amount:,} (Indian Rupees), '
            f'along with interest as applicable under law.</p>'
        )

    # Section 5 — Deadline
    cn += 1
    sections.append(
        f'<h2>{cn}. Response Deadline</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'You are hereby called upon to comply with the above demand within '
        f'<strong>{deadline}</strong> from the date of receipt of this notice.</p>'
    )

    # Section 6 — Consequences
    cn += 1
    sections.append(
        f'<h2>{cn}. Consequences of Non-Compliance</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'In the event of your failure to comply with the demands stated '
        f'herein within the stipulated time, '
        f'{"my client shall be constrained to" if advocate else "I shall be constrained to"} '
        f'take the following legal action(s) against you, at your risk and '
        f'cost:</p>'
        f'{_list_html(consequences) if consequences else "<p>Initiate appropriate legal proceedings.</p>"}'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'You shall also be liable for all costs, charges, and expenses '
        f'incurred by '
        f'{"my client" if advocate else "the sender"} '
        f'in pursuing the matter, including legal fees.</p>'
    )

    # Section 7 — Documents
    cn += 1
    if docs_enclosed:
        sections.append(
            f'<h2>{cn}. Documents Enclosed</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The following documents are enclosed for your reference:</p>'
            f'<p class="clause"><em>{docs_enclosed}</em></p>'
        )
    else:
        sections.append(
            f'<h2>{cn}. Reservation of Rights</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'{"My client reserves" if advocate else "I reserve"} the right to '
            f'produce relevant documents and evidence at the appropriate forum. '
            f'This notice is without prejudice to any other rights and remedies '
            f'available under law.</p>'
        )

    # Section 8 — Jurisdiction
    cn += 1
    sections.append(
        f'<h2>{cn}. Jurisdiction</h2>'
        f'<p class="clause"><span class="clause-number">{cn}.1</span> '
        f'The courts at <strong>{governing}</strong> shall have exclusive '
        f'jurisdiction over any proceedings arising out of this notice.</p>'
        f'<p class="clause"><span class="clause-number">{cn}.2</span> '
        f'A copy of this notice is being retained for record and shall be '
        f'produced before the appropriate court/forum as and when required.</p>'
    )

    # Signature block
    if advocate:
        sections.append(
            '<div class="signature-block">'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>{advocate}</strong></p>'
            '<p>Advocate</p>'
            f'{("<p>Enrollment No. " + advocate_enroll + "</p>") if advocate_enroll else ""}'
            f'<p>On behalf of {sender}</p>'
            '<p>Date: ________________________</p></div></div>'
        )
    else:
        sections.append(
            '<div class="signature-block">'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>{sender}</strong></p>'
            '<p>Complainant / Sender</p>'
            '<p>Date: ________________________</p></div></div>'
        )

    body = "\n".join(sections)
    return _base_html_wrap(
        f"Legal Notice \u2014 {subject}", body
    )


# ---------------------------------------------------------------------------
# Registry — makes it easy for the main service to import all templates/renderers
# ---------------------------------------------------------------------------

TIER3B_TEMPLATES: Dict[str, dict] = {
    "freelancer_agreement": freelancer_agreement_template(),
    "internship_agreement": internship_agreement_template(),
    "letter_of_intent": letter_of_intent_template(),
    "power_of_attorney": power_of_attorney_template(),
    "legal_notice": legal_notice_template(),
}

TIER3B_RENDERERS: Dict[str, Any] = {
    "freelancer_agreement": render_freelancer_agreement,
    "internship_agreement": render_internship_agreement,
    "letter_of_intent": render_letter_of_intent,
    "power_of_attorney": render_power_of_attorney,
    "legal_notice": render_legal_notice,
}
