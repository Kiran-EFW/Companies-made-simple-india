"""
Legal Document Service — generates MOA, AOA, LLP Agreement, Partnership
Deed, and Sole Proprietorship Declaration templates.

Supports Private Limited, OPC, LLP, Section 8, Partnership,
Sole Proprietorship, and Public Limited entity types.
Uses LLM to generate custom business objects clauses when available.
Output is JSON/dict for now (PDF generation deferred to Phase 9).
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import date

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Template Constants
# ---------------------------------------------------------------------------

# Standard MOA clauses shared across entity types
_MOA_COMMON_CLAUSES = {
    "liability_clause": (
        "The liability of the members is limited and this liability is limited to "
        "the amount unpaid, if any, on the shares held by them."
    ),
    "subscription_clause": (
        "We, the several persons whose names, addresses, descriptions and occupations "
        "are subscribed below, are desirous of being formed into a company in pursuance "
        "of this Memorandum of Association, and we respectively agree to take the number "
        "of shares in the capital of the Company set against our respective names."
    ),
}

# Section 8 specific objects (charitable)
_SECTION_8_OBJECTS = [
    "To promote education, art, science, sports, research, social welfare, religion, "
    "charity, protection of environment or any such other object.",
    "To apply the profits, if any, or other income in promoting the objects of the company.",
    "To prohibit payment of any dividend to its members.",
]

# Standard AOA adoption references
_AOA_TABLE_REFERENCES = {
    "private_limited": "Table F of Schedule I to the Companies Act, 2013",
    "opc": "Table F of Schedule I (modified for OPC) to the Companies Act, 2013",
    "section_8": "Table F of Schedule I (modified for Section 8) to the Companies Act, 2013",
    "public_limited": "Table F of Schedule I to the Companies Act, 2013",
}


# ---------------------------------------------------------------------------
# MOA Templates
# ---------------------------------------------------------------------------

def _generate_moa_private_limited(
    company_name: str,
    state: str,
    authorized_capital: int,
    business_objects: List[str],
    directors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate MOA for Private Limited Company (Table F format)."""
    return {
        "document_type": "Memorandum of Association",
        "format": "Table F",
        "entity_type": "private_limited",
        "clauses": {
            "I_name_clause": {
                "clause_number": "I",
                "title": "Name Clause",
                "content": f"The name of the Company is \"{company_name}\".",
            },
            "II_registered_office_clause": {
                "clause_number": "II",
                "title": "Registered Office Clause",
                "content": (
                    f"The Registered Office of the Company will be situated in the "
                    f"State of {state}."
                ),
            },
            "III_objects_clause": {
                "clause_number": "III",
                "title": "Objects Clause",
                "sub_clauses": {
                    "A_main_objects": {
                        "title": "The Main Objects of the Company",
                        "objects": business_objects,
                    },
                    "B_matters_incidental": {
                        "title": "Matters which are necessary for furtherance of the objects",
                        "objects": [
                            "To carry on any other business which may seem to the company capable "
                            "of being conveniently carried on in connection with the above.",
                            "To acquire and undertake the whole or any part of the business, property "
                            "and liabilities of any person or company.",
                            "To apply for, purchase, or otherwise acquire any patents, brevets "
                            "d'invention, licences, concessions, and the like.",
                            "To enter into partnership or into any arrangement for sharing profits, "
                            "union of interests, co-operation, joint venture, reciprocal concession.",
                            "To take or otherwise acquire and hold shares in any other company.",
                            "To promote any company or companies for the purpose of acquiring all "
                            "or any of the property, rights and liabilities of this Company.",
                        ],
                    },
                },
            },
            "IV_liability_clause": {
                "clause_number": "IV",
                "title": "Liability Clause",
                "content": _MOA_COMMON_CLAUSES["liability_clause"],
            },
            "V_capital_clause": {
                "clause_number": "V",
                "title": "Capital Clause",
                "content": (
                    f"The Authorized Share Capital of the Company is Rs. {authorized_capital:,}/- "
                    f"(Rupees {_number_to_words(authorized_capital)} only) divided into "
                    f"{authorized_capital // 10} equity shares of Rs. 10/- each."
                ),
                "authorized_capital": authorized_capital,
                "share_value": 10,
                "total_shares": authorized_capital // 10,
            },
            "VI_subscription_clause": {
                "clause_number": "VI",
                "title": "Subscription Clause",
                "content": _MOA_COMMON_CLAUSES["subscription_clause"],
                "subscribers": [
                    {
                        "name": d.get("full_name", ""),
                        "father_name": d.get("father_name", ""),
                        "pan": d.get("pan", ""),
                        "address": d.get("address", ""),
                        "occupation": d.get("occupation", ""),
                        "nationality": d.get("nationality", "Indian"),
                        "shares_subscribed": max(1, (authorized_capital // 10) // max(len(directors), 1)),
                    }
                    for d in directors
                ],
                "witnesses": [
                    {
                        "witness_number": 1,
                        "name": "",
                        "address": "",
                        "occupation": "",
                        "note": (
                            "Witness to the above signatures "
                            "(as required under Schedule I, Companies Act, 2013)"
                        ),
                    },
                    {
                        "witness_number": 2,
                        "name": "",
                        "address": "",
                        "occupation": "",
                        "note": (
                            "Witness to the above signatures "
                            "(as required under Schedule I, Companies Act, 2013)"
                        ),
                    },
                ],
                "filing_note": (
                    "This subscription clause must be filed as part of Form SPICe+ "
                    "(INC-32) with the Registrar of Companies. All subscribers must "
                    "sign in the presence of at least one witness who shall attest the "
                    "signatures (Schedule I, Companies Act, 2013)."
                ),
            },
        },
        "metadata": {
            "generated_date": date.today().isoformat(),
            "company_name": company_name,
            "state": state,
            "authorized_capital": authorized_capital,
        },
    }


def _generate_moa_opc(
    company_name: str,
    state: str,
    authorized_capital: int,
    business_objects: List[str],
    directors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate MOA for One Person Company (Modified Table F)."""
    moa = _generate_moa_private_limited(
        company_name, state, authorized_capital, business_objects, directors
    )
    moa["format"] = "Modified Table F (OPC)"
    moa["entity_type"] = "opc"

    # OPC-specific modifications
    moa["clauses"]["VII_nominee_clause"] = {
        "clause_number": "VII",
        "title": "Nominee Clause",
        "content": (
            "In the event of the death or incapacity of the sole member, "
            "the nominee shall become the member of the Company. "
            "The name and details of the nominee are as specified in Form INC-3."
        ),
    }

    return moa


def _generate_moa_section_8(
    company_name: str,
    state: str,
    business_objects: List[str],
    directors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate MOA for Section 8 Company (Non-profit)."""
    # Merge charitable objects with user-specified business objects
    all_objects = _SECTION_8_OBJECTS + business_objects

    return {
        "document_type": "Memorandum of Association",
        "format": "Section 8 (Non-Profit)",
        "entity_type": "section_8",
        "clauses": {
            "I_name_clause": {
                "clause_number": "I",
                "title": "Name Clause",
                "content": f"The name of the Company is \"{company_name}\".",
            },
            "II_registered_office_clause": {
                "clause_number": "II",
                "title": "Registered Office Clause",
                "content": (
                    f"The Registered Office of the Company will be situated in the "
                    f"State of {state}."
                ),
            },
            "III_objects_clause": {
                "clause_number": "III",
                "title": "Objects Clause",
                "sub_clauses": {
                    "A_charitable_objects": {
                        "title": "Charitable Objects",
                        "objects": all_objects,
                    },
                },
            },
            "IV_application_of_income": {
                "clause_number": "IV",
                "title": "Application of Income",
                "content": (
                    "The income and property of the Company, howsoever derived, shall be "
                    "applied solely towards the promotion of the objects of the Company. "
                    "No portion thereof shall be paid or transferred, directly or indirectly, "
                    "by way of dividend, bonus or otherwise howsoever by way of profit "
                    "to persons who at any time are or have been members of the Company "
                    "or to any of them or to any persons claiming through any of them."
                ),
            },
            "V_liability_clause": {
                "clause_number": "V",
                "title": "Liability Clause",
                "content": (
                    "The liability of the members is limited. Every member of the Company "
                    "undertakes to contribute to the assets of the Company in the event of "
                    "its being wound up while he/she is a member or within one year after "
                    "he/she ceases to be a member, for payment of the debts and liabilities "
                    "of the Company."
                ),
            },
            "VI_subscription_clause": {
                "clause_number": "VI",
                "title": "Subscription Clause",
                "content": _MOA_COMMON_CLAUSES["subscription_clause"],
                "subscribers": [
                    {
                        "name": d.get("full_name", ""),
                        "father_name": d.get("father_name", ""),
                        "pan": d.get("pan", ""),
                        "address": d.get("address", ""),
                        "occupation": d.get("occupation", ""),
                        "nationality": d.get("nationality", "Indian"),
                    }
                    for d in directors
                ],
                "witnesses": [
                    {
                        "witness_number": 1,
                        "name": "",
                        "address": "",
                        "occupation": "",
                        "note": (
                            "Witness to the above signatures "
                            "(as required under Schedule I, Companies Act, 2013)"
                        ),
                    },
                    {
                        "witness_number": 2,
                        "name": "",
                        "address": "",
                        "occupation": "",
                        "note": (
                            "Witness to the above signatures "
                            "(as required under Schedule I, Companies Act, 2013)"
                        ),
                    },
                ],
            },
        },
        "metadata": {
            "generated_date": date.today().isoformat(),
            "company_name": company_name,
            "state": state,
            "is_section_8": True,
        },
    }


def _generate_llp_agreement(
    company_name: str,
    state: str,
    business_objects: List[str],
    partners: List[Dict[str, Any]],
    capital_contribution: int,
) -> Dict[str, Any]:
    """Generate LLP Agreement template."""
    num_partners = max(len(partners), 2)
    per_partner_share = round(100.0 / num_partners, 2)

    return {
        "document_type": "LLP Agreement",
        "format": "LLP Agreement (under LLP Act, 2008)",
        "entity_type": "llp",
        "sections": {
            "1_definitions": {
                "section_number": "1",
                "title": "Definitions and Interpretation",
                "content": (
                    f"In this Agreement, unless the context otherwise requires: "
                    f"\"LLP\" means {company_name}; \"Partners\" means the partners "
                    f"of the LLP as listed in Schedule I; \"Designated Partners\" means "
                    f"the partners designated as such under the LLP Act, 2008."
                ),
            },
            "2_name_and_office": {
                "section_number": "2",
                "title": "Name and Registered Office",
                "content": (
                    f"The name of the LLP shall be \"{company_name}\". "
                    f"The registered office of the LLP shall be situated in the State of {state}."
                ),
            },
            "3_business_objects": {
                "section_number": "3",
                "title": "Business of the LLP",
                "objects": business_objects,
            },
            "4_capital_contribution": {
                "section_number": "4",
                "title": "Capital Contribution",
                "content": (
                    f"The total capital contribution of the LLP shall be "
                    f"Rs. {capital_contribution:,}/- as contributed by the partners "
                    f"in the proportions set out in Schedule II."
                ),
                "total_contribution": capital_contribution,
                "partner_contributions": [
                    {
                        "name": p.get("full_name", ""),
                        "contribution": capital_contribution // num_partners,
                        "percentage": per_partner_share,
                    }
                    for p in partners
                ],
            },
            "5_profit_sharing": {
                "section_number": "5",
                "title": "Profit and Loss Sharing",
                "content": (
                    "The profits and losses of the LLP shall be shared among the "
                    "Partners in the ratio of their respective capital contributions, "
                    "unless otherwise agreed in writing by all Partners."
                ),
                "profit_ratios": [
                    {"name": p.get("full_name", ""), "share_percent": per_partner_share}
                    for p in partners
                ],
            },
            "6_management": {
                "section_number": "6",
                "title": "Management and Designated Partners",
                "content": (
                    "The business of the LLP shall be managed by the Designated Partners. "
                    "Each Designated Partner shall have equal authority in the management "
                    "of the LLP unless otherwise specified in this Agreement."
                ),
                "designated_partners": [
                    p.get("full_name", "") for p in partners
                    if p.get("is_designated_partner", True)
                ],
            },
            "7_meetings": {
                "section_number": "7",
                "title": "Meetings",
                "content": (
                    "The Partners shall hold at least one meeting in each half of the calendar year. "
                    "Decisions shall be taken by a majority of the Partners present and voting, "
                    "unless a higher majority is required by this Agreement or the LLP Act."
                ),
            },
            "8_admission_retirement": {
                "section_number": "8",
                "title": "Admission and Retirement of Partners",
                "content": (
                    "A new partner may be admitted with the unanimous consent of all existing partners. "
                    "A partner may retire from the LLP by giving not less than 30 days written notice."
                ),
            },
            "9_dissolution": {
                "section_number": "9",
                "title": "Dissolution",
                "content": (
                    "The LLP may be dissolved by agreement of all partners or by an order of the "
                    "Tribunal under the LLP Act, 2008. Upon dissolution, the assets of the LLP "
                    "shall be applied in satisfaction of its debts and liabilities."
                ),
            },
            "10_rights_duties": {
                "section_number": "10",
                "title": "Rights and Duties of Partners",
                "content": (
                    "Each Partner shall have the right to: (a) participate in the management "
                    "of the LLP; (b) access the books of account and records of the LLP; "
                    "(c) receive a share of profits as per Section 5 above. "
                    "Each Partner shall have the duty to: (a) act in good faith and in the "
                    "best interest of the LLP; (b) render true accounts and full information "
                    "of all things affecting the LLP; (c) indemnify the LLP for any loss "
                    "caused by fraud or wilful neglect; (d) not carry on any business of "
                    "the same nature as and competing with the LLP without the consent of "
                    "the other Partners."
                ),
            },
            "11_mutual_agency": {
                "section_number": "11",
                "title": "Mutual Agency",
                "content": (
                    "Every Partner is an agent of the LLP for the purposes of the business "
                    "of the LLP (Section 26, LLP Act, 2008). The acts of a Partner in the "
                    "ordinary course of business shall bind the LLP. However, no Partner "
                    "shall have the authority to: (a) submit a claim or dispute relating to "
                    "the LLP to arbitration; (b) open a banking account on behalf of the LLP "
                    "in his own name; (c) compromise or relinquish any claim of the LLP; "
                    "(d) acquire immovable property on behalf of the LLP; (e) transfer any "
                    "property of the LLP — without prior written consent of all Partners."
                ),
            },
            "12_accounts_and_audit": {
                "section_number": "12",
                "title": "Accounts, Audit, and Annual Filings",
                "content": (
                    "The LLP shall maintain proper books of account. The accounts shall be "
                    "audited annually if the turnover exceeds Rs. 40 lakhs or the capital "
                    "contribution exceeds Rs. 25 lakhs (LLP Act, 2008). The Designated "
                    "Partners shall ensure timely filing of: (a) Form 8 — Statement of "
                    "Account and Solvency (within 30 days of 6 months from FY end); "
                    "(b) Form 11 — Annual Return (within 60 days of FY end). Late filing "
                    "attracts a penalty of Rs. 100 per day."
                ),
            },
            "13_dispute_resolution": {
                "section_number": "13",
                "title": "Dispute Resolution",
                "content": (
                    "Any dispute arising out of or in connection with this Agreement shall first "
                    "be referred to mediation. If mediation fails, the dispute shall be referred "
                    "to arbitration in accordance with the Arbitration and Conciliation Act, 1996. "
                    "The seat of arbitration shall be in the State of " + state + "."
                ),
            },
            "14_governing_law": {
                "section_number": "14",
                "title": "Governing Law",
                "content": (
                    "This Agreement shall be governed by and construed in accordance with the "
                    "Limited Liability Partnership Act, 2008 and the rules made thereunder, "
                    "and the laws of India. In the event any provision of this Agreement is "
                    "not covered or is silent, the First Schedule of the LLP Act, 2008 shall "
                    "apply by default."
                ),
            },
            "15_form3_filing": {
                "section_number": "15",
                "title": "Filing and Registration",
                "content": (
                    "This Agreement, or any subsequent amendment thereto, shall be filed "
                    "with the Registrar of Companies in Form 3 (LLP Rules, 2009) within "
                    "30 days of incorporation or amendment, as applicable. The Agreement "
                    "must be: (a) printed on state-specific non-judicial stamp paper of "
                    "the value prescribed under the applicable State Stamp Act; "
                    "(b) notarized by a Notary Public; (c) digitally signed by a "
                    "Designated Partner using a valid Digital Signature Certificate (DSC) "
                    "issued by a Certifying Authority licensed under the IT Act, 2000, "
                    "before upload to the MCA portal. Aadhaar-based e-Sign is not "
                    "accepted for Form 3 filing. Failure to file within 30 days "
                    "attracts a penalty of Rs. 100 per day of default."
                ),
            },
        },
        "metadata": {
            "generated_date": date.today().isoformat(),
            "company_name": company_name,
            "state": state,
            "total_partners": num_partners,
            "total_capital": capital_contribution,
        },
    }


# ---------------------------------------------------------------------------
# Partnership Deed Template (Indian Partnership Act, 1932)
# ---------------------------------------------------------------------------

def _generate_partnership_deed(
    firm_name: str,
    state: str,
    business_objects: List[str],
    partners: List[Dict[str, Any]],
    capital_contribution: int,
) -> Dict[str, Any]:
    """
    Generate Partnership Deed under the Indian Partnership Act, 1932.

    Covers all mandatory and recommended clauses: Sections 4-69.
    Registration is optional but strongly recommended (Section 69
    consequences — unregistered firms cannot sue third parties).
    """
    num_partners = max(len(partners), 2)
    per_partner_share = round(100.0 / num_partners, 2)
    per_partner_capital = capital_contribution // num_partners

    return {
        "document_type": "Partnership Deed",
        "format": "Partnership Deed (under Indian Partnership Act, 1932)",
        "entity_type": "partnership",
        "sections": {
            "1_definitions": {
                "section_number": "1",
                "title": "Definitions and Interpretation",
                "content": (
                    f"In this Deed, unless the context otherwise requires: "
                    f"\"Firm\" means the partnership firm carrying on business under "
                    f"the name and style of \"{firm_name}\"; \"Partners\" means the "
                    f"partners named herein; \"Act\" means the Indian Partnership "
                    f"Act, 1932."
                ),
            },
            "2_name_and_office": {
                "section_number": "2",
                "title": "Name and Principal Place of Business",
                "content": (
                    f"The name of the Firm shall be \"{firm_name}\". The principal "
                    f"place of business shall be situated in the State of {state}. "
                    f"The Firm may establish branch offices at such other places "
                    f"as the Partners may decide by mutual consent."
                ),
            },
            "3_nature_of_business": {
                "section_number": "3",
                "title": "Nature of Business (Section 4)",
                "objects": business_objects,
                "content": (
                    "The Firm shall carry on the business as described above and "
                    "such other allied or incidental activities as the Partners "
                    "may mutually agree upon from time to time."
                ),
            },
            "4_commencement_and_duration": {
                "section_number": "4",
                "title": "Commencement and Duration",
                "content": (
                    "The partnership shall be deemed to have commenced on the date "
                    "of execution of this Deed and shall continue as a partnership "
                    "at will unless dissolved by mutual agreement of all Partners, "
                    "by notice under Section 43 of the Act, or by operation of law "
                    "(Section 42)."
                ),
            },
            "5_capital_contribution": {
                "section_number": "5",
                "title": "Capital Contribution (Section 13(c))",
                "content": (
                    f"The total capital of the Firm shall be Rs. {capital_contribution:,}/- "
                    f"(Rupees {_number_to_words(capital_contribution)} only), contributed "
                    f"by the Partners as set out below. Additional capital may be "
                    f"introduced with the consent of all Partners."
                ),
                "total_capital": capital_contribution,
                "partner_contributions": [
                    {
                        "name": p.get("full_name", ""),
                        "father_name": p.get("father_name", ""),
                        "address": p.get("address", ""),
                        "pan": p.get("pan", ""),
                        "contribution": per_partner_capital,
                        "percentage": per_partner_share,
                    }
                    for p in partners
                ],
            },
            "6_profit_loss_sharing": {
                "section_number": "6",
                "title": "Profit and Loss Sharing (Section 13(b))",
                "content": (
                    "The net profits or losses of the Firm, after deducting all "
                    "expenses, salaries, interest on capital and other outgoings, "
                    "shall be divided among the Partners in the following ratio. "
                    "Profits shall be distributed quarterly or at such intervals "
                    "as the Partners may decide."
                ),
                "profit_ratios": [
                    {"name": p.get("full_name", ""), "share_percent": per_partner_share}
                    for p in partners
                ],
            },
            "7_interest_on_capital": {
                "section_number": "7",
                "title": "Interest on Capital (Section 13(d))",
                "content": (
                    "Each Partner shall be entitled to interest on their capital "
                    "contribution at the rate of 12% per annum (or such other rate "
                    "as the Partners may agree). Interest on capital shall be "
                    "payable only out of the profits of the Firm. No interest "
                    "shall be charged on drawings unless agreed otherwise."
                ),
            },
            "8_drawings_and_salary": {
                "section_number": "8",
                "title": "Drawings and Salary",
                "content": (
                    "Each Partner shall be entitled to draw a monthly salary "
                    "as mutually agreed and recorded in a supplementary agreement. "
                    "Drawings against anticipated profit shall not exceed "
                    "50% of the estimated share of the Partner for the current "
                    "accounting period. Interest on excess drawings shall be "
                    "charged at the rate of 12% per annum."
                ),
            },
            "9_management_and_duties": {
                "section_number": "9",
                "title": "Management and Duties (Sections 9, 12, 13(a))",
                "content": (
                    "All Partners shall participate in the management of the Firm. "
                    "Each Partner shall: (a) attend to the business diligently and "
                    "devote adequate time; (b) act in good faith and in the best "
                    "interest of the Firm; (c) render true accounts and full "
                    "information of all things affecting the Firm to any Partner "
                    "(Section 9); (d) indemnify the Firm for any loss caused by "
                    "fraud or wilful neglect (Section 10); (e) not carry on any "
                    "competing business without the consent of all Partners "
                    "(Section 16)."
                ),
            },
            "10_mutual_agency": {
                "section_number": "10",
                "title": "Mutual Agency (Sections 18-22, 25-27)",
                "content": (
                    "Each Partner is an agent of the Firm and of the other Partners "
                    "for the purpose of the business of the Firm (Section 18). "
                    "Acts done in the ordinary course of business shall bind the "
                    "Firm (Section 19). Notwithstanding the above, no Partner "
                    "shall, without the prior written consent of all Partners: "
                    "(a) submit any claim of the Firm to arbitration; "
                    "(b) open a bank account in their own name on behalf of the Firm; "
                    "(c) compromise or relinquish any claim of the Firm; "
                    "(d) acquire immovable property on behalf of the Firm; "
                    "(e) transfer any property of the Firm; "
                    "(f) admit any liability in a suit against the Firm (Section 22)."
                ),
            },
            "11_banking_and_accounts": {
                "section_number": "11",
                "title": "Banking and Books of Account",
                "content": (
                    "The Firm shall maintain a bank account in the name of the Firm. "
                    "The account shall be operated jointly by at least two Partners "
                    "or as the Partners may decide. The Firm shall maintain proper "
                    "books of account including a cash book, ledger, and journal. "
                    "The accounts shall be closed on 31st March of each year and "
                    "a balance sheet and profit and loss account shall be prepared. "
                    "Each Partner shall have access to and may inspect and copy "
                    "the books of account of the Firm (Section 12)."
                ),
            },
            "12_admission_of_new_partner": {
                "section_number": "12",
                "title": "Admission of New Partner (Section 31)",
                "content": (
                    "No person shall be admitted as a partner into the Firm without "
                    "the consent of all existing Partners (Section 31(1)). A new "
                    "partner shall not be liable for any act of the Firm done before "
                    "they became a partner (Section 31(2)). An amended Deed shall "
                    "be executed upon admission of any new Partner."
                ),
            },
            "13_retirement_and_expulsion": {
                "section_number": "13",
                "title": "Retirement, Expulsion, and Death (Sections 32-35)",
                "content": (
                    "A Partner may retire from the Firm: (a) with the consent of "
                    "all Partners; (b) by giving not less than 90 days written "
                    "notice to all other Partners (in a partnership at will). "
                    "A retiring Partner shall be entitled to their share of the "
                    "capital and accumulated profits as on the date of retirement. "
                    "A Partner may be expelled by a majority of the Partners if "
                    "such power is conferred by a contract between the Partners, "
                    "and only if the expulsion is in good faith (Section 33). "
                    "On the death of a Partner, the Firm shall not be dissolved "
                    "unless so provided herein; the legal heirs of the deceased "
                    "Partner shall be entitled to the deceased Partner's share "
                    "as on the date of death (Section 35)."
                ),
            },
            "14_non_compete_and_confidentiality": {
                "section_number": "14",
                "title": "Non-Compete and Confidentiality (Section 16)",
                "content": (
                    "No Partner shall, during the subsistence of the partnership, "
                    "carry on any business of the same nature as and competing with "
                    "that of the Firm without the consent of all other Partners "
                    "(Section 16(a)). If a Partner derives any profit for themselves "
                    "from any transaction of the Firm, they shall account for that "
                    "profit and pay it to the Firm (Section 16(b)). All Partners "
                    "shall keep confidential the affairs and trade secrets of the "
                    "Firm during the partnership and for a period of 2 years "
                    "after retirement or dissolution."
                ),
            },
            "15_goodwill": {
                "section_number": "15",
                "title": "Goodwill (Section 14)",
                "content": (
                    "The goodwill of the Firm is the property of the Firm. "
                    "Unless otherwise agreed, on dissolution each Partner's share "
                    "of the goodwill shall be in proportion to their profit-sharing "
                    "ratio. The valuation of goodwill on retirement or admission "
                    "shall be determined by mutual agreement or, failing that, "
                    "on the basis of the average of the profits of the last "
                    "three completed financial years."
                ),
            },
            "16_dissolution": {
                "section_number": "16",
                "title": "Dissolution (Sections 40-44)",
                "content": (
                    "The Firm may be dissolved: (a) by agreement of all Partners; "
                    "(b) compulsorily, when all Partners or all but one become "
                    "insolvent (Section 41); (c) by notice in writing by any "
                    "Partner to all other Partners in a partnership at will "
                    "(Section 43); (d) by order of the Court under Section 44. "
                    "Upon dissolution, the assets of the Firm shall be applied "
                    "in the following order: (i) payment of debts to third parties; "
                    "(ii) repayment of advances made by Partners; (iii) return of "
                    "capital to Partners; (iv) distribution of surplus, if any, "
                    "in the profit-sharing ratio (Section 48)."
                ),
            },
            "17_indemnity": {
                "section_number": "17",
                "title": "Indemnity (Section 13(f))",
                "content": (
                    "Each Partner shall indemnify the Firm and the other Partners "
                    "for any loss caused by their fraud or wilful neglect in the "
                    "conduct of the business of the Firm (Section 13(f)). A "
                    "Partner acting within the scope of their authority shall be "
                    "indemnified by the Firm for liabilities incurred in the "
                    "ordinary course of business (Section 13(e))."
                ),
            },
            "18_dispute_resolution": {
                "section_number": "18",
                "title": "Dispute Resolution (Section 46)",
                "content": (
                    "Any dispute arising out of or in connection with this Deed "
                    "shall first be referred to mediation between the Partners. "
                    "If mediation fails within 30 days, the dispute shall be "
                    "referred to arbitration under the Arbitration and Conciliation "
                    f"Act, 1996. The seat of arbitration shall be in {state}. "
                    "Until a dispute is resolved, the Partners shall continue "
                    "to perform their obligations under this Deed."
                ),
            },
            "19_registration": {
                "section_number": "19",
                "title": "Registration with Registrar of Firms (Sections 56-59, 69)",
                "content": (
                    "The Partners agree to register this Firm with the Registrar "
                    "of Firms for the State in which the principal place of business "
                    "is situated, by filing an application in Form C "
                    "(Section 58, Indian Partnership Act, 1932). Registration is "
                    "optional but strongly recommended. An unregistered firm "
                    "cannot: (a) file a suit against any third party in any court; "
                    "(b) claim a set-off in any proceeding (Section 69). "
                    "The application shall be signed by all Partners or their "
                    "authorised agents and accompanied by the prescribed fee. "
                    "Any change in the Firm — admission, retirement, change of "
                    "name or business — must be notified to the Registrar."
                ),
            },
            "20_stamp_duty": {
                "section_number": "20",
                "title": "Stamp Duty and Execution",
                "content": (
                    "This Deed shall be printed on non-judicial stamp paper of the "
                    "value prescribed under the applicable State Stamp Act. "
                    "Partnership deeds are NOT filed through the MCA portal; they "
                    "are filed physically with the Registrar of Firms. Each Partner "
                    "shall sign this Deed in the presence of at least two witnesses."
                ),
            },
            "21_governing_law": {
                "section_number": "21",
                "title": "Governing Law",
                "content": (
                    "This Deed shall be governed by and construed in accordance with "
                    "the Indian Partnership Act, 1932 and the rules made thereunder, "
                    "and the laws of India. In the event any provision of this Deed "
                    "is silent, the provisions of the Indian Partnership Act, 1932 "
                    "shall apply."
                ),
            },
        },
        "schedules": {
            "schedule_I_partners": {
                "title": "Schedule I — Partners",
                "partners": [
                    {
                        "name": p.get("full_name", ""),
                        "father_name": p.get("father_name", ""),
                        "address": p.get("address", ""),
                        "pan": p.get("pan", ""),
                        "aadhar_last_four": p.get("aadhar_last_four", ""),
                        "occupation": p.get("occupation", ""),
                        "nationality": p.get("nationality", "Indian"),
                    }
                    for p in partners
                ],
            },
            "schedule_II_capital": {
                "title": "Schedule II — Capital Contributions",
                "contributions": [
                    {
                        "name": p.get("full_name", ""),
                        "contribution": per_partner_capital,
                        "percentage": per_partner_share,
                    }
                    for p in partners
                ],
            },
        },
        "metadata": {
            "generated_date": date.today().isoformat(),
            "firm_name": firm_name,
            "state": state,
            "total_partners": num_partners,
            "total_capital": capital_contribution,
            "registration_note": (
                "Registration with Registrar of Firms is optional but strongly "
                "recommended. Without registration, the firm cannot enforce its "
                "rights against third parties in court (Section 69)."
            ),
        },
    }


# ---------------------------------------------------------------------------
# Sole Proprietorship Declaration / Affidavit Template
# ---------------------------------------------------------------------------

def _generate_sole_prop_declaration(
    business_name: str,
    state: str,
    business_objects: List[str],
    proprietor: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate Sole Proprietorship Declaration / Affidavit.

    A sole proprietorship has no separate legal entity; this generates the
    standard declaration/affidavit format used for bank account opening,
    GST registration, MSME Udyam registration, and Shop & Establishment
    Act registration.
    """
    return {
        "document_type": "Sole Proprietorship Declaration",
        "format": "Affidavit / Declaration",
        "entity_type": "sole_proprietorship",
        "sections": {
            "1_declaration": {
                "section_number": "1",
                "title": "Declaration",
                "content": (
                    f"I, {proprietor.get('full_name', '_______________')}, "
                    f"S/o / D/o / W/o {proprietor.get('father_name', '_______________')}, "
                    f"aged {proprietor.get('age', '____')} years, residing at "
                    f"{proprietor.get('address', '_______________')}, do hereby "
                    f"solemnly declare and affirm as follows:"
                ),
            },
            "2_business_details": {
                "section_number": "2",
                "title": "Business Details",
                "items": [
                    {
                        "item_number": "i",
                        "content": (
                            f"That I am the sole proprietor of the business carried on "
                            f"under the name and style of \"{business_name}\"."
                        ),
                    },
                    {
                        "item_number": "ii",
                        "content": (
                            f"That the principal place of business is situated at "
                            f"{proprietor.get('business_address', proprietor.get('address', '_______________'))}, "
                            f"in the State of {state}."
                        ),
                    },
                    {
                        "item_number": "iii",
                        "content": "That the nature of business activities is as follows:",
                        "business_objects": business_objects,
                    },
                    {
                        "item_number": "iv",
                        "content": (
                            "That the business is owned and managed solely by me and "
                            "no other person has any share, interest or claim in the "
                            "said business."
                        ),
                    },
                    {
                        "item_number": "v",
                        "content": (
                            f"That my Permanent Account Number (PAN) is "
                            f"{proprietor.get('pan', '_______________')} and my "
                            f"Aadhaar number is {proprietor.get('aadhaar', 'XXXX-XXXX-____')}."
                        ),
                    },
                    {
                        "item_number": "vi",
                        "content": (
                            "That the business was commenced / will commence on "
                            f"{proprietor.get('commencement_date', '_______________')}."
                        ),
                    },
                    {
                        "item_number": "vii",
                        "content": (
                            "That I have not been adjudicated as an insolvent and "
                            "there are no legal proceedings pending against me that "
                            "would affect the conduct of this business."
                        ),
                    },
                    {
                        "item_number": "viii",
                        "content": (
                            "That the above statements are true and correct to the best "
                            "of my knowledge and belief. I understand that making a false "
                            "declaration is punishable under the Indian Penal Code."
                        ),
                    },
                ],
            },
            "3_proprietor_details": {
                "section_number": "3",
                "title": "Proprietor Details",
                "proprietor": {
                    "name": proprietor.get("full_name", ""),
                    "father_name": proprietor.get("father_name", ""),
                    "address": proprietor.get("address", ""),
                    "pan": proprietor.get("pan", ""),
                    "aadhaar": proprietor.get("aadhaar", ""),
                    "occupation": proprietor.get("occupation", ""),
                    "nationality": proprietor.get("nationality", "Indian"),
                    "date_of_birth": proprietor.get("date_of_birth", ""),
                    "email": proprietor.get("email", ""),
                    "phone": proprietor.get("phone", ""),
                },
            },
            "4_stamp_duty_and_notarization": {
                "section_number": "4",
                "title": "Stamp Duty and Notarization",
                "content": (
                    "This declaration/affidavit must be executed on non-judicial "
                    "stamp paper of the value prescribed under the applicable State "
                    "Stamp Act (typically Rs. 10 to Rs. 100 for affidavits, varying "
                    "by state). It must be notarized by a Notary Public or sworn "
                    "before a Magistrate/Executive Magistrate."
                ),
            },
        },
        "registration_guidance": {
            "gst_registration": {
                "title": "GST Registration",
                "content": (
                    "GST registration is mandatory if annual turnover exceeds "
                    "Rs. 20,00,000 (Rs. 10,00,000 for special category states). "
                    "Voluntary registration is available below the threshold. "
                    "Apply online at www.gst.gov.in using PAN and Aadhaar."
                ),
                "threshold": 2000000,
                "documents_required": [
                    "PAN Card of Proprietor",
                    "Aadhaar Card of Proprietor",
                    "Bank account statement / cancelled cheque",
                    "Address proof of business premises",
                    "Photograph of Proprietor",
                    "Electricity bill / rent agreement for business address",
                ],
            },
            "msme_udyam_registration": {
                "title": "MSME Udyam Registration",
                "content": (
                    "Udyam registration is free of cost and done online at "
                    "udyamregistration.gov.in. Aadhaar number of the proprietor "
                    "is mandatory. The registration provides benefits including "
                    "priority sector lending, collateral-free loans, and "
                    "government tender preferences."
                ),
                "mandatory_documents": [
                    "Aadhaar Number of Proprietor (mandatory)",
                    "PAN and GST details (if available)",
                    "Bank account details",
                    "Business activity details (NIC code)",
                ],
            },
            "shop_and_establishment": {
                "title": "Shop & Establishment Act Registration",
                "content": (
                    "Registration under the applicable State Shop and "
                    "Establishment Act must be obtained within 30 days of "
                    "commencement of business. This is a state-level registration "
                    "with the local municipal body or labour department. "
                    "Requirements vary by state."
                ),
            },
        },
        "metadata": {
            "generated_date": date.today().isoformat(),
            "business_name": business_name,
            "state": state,
            "proprietor_name": proprietor.get("full_name", ""),
            "registration_note": (
                "A sole proprietorship is not a separate legal entity. The "
                "proprietor and the business are legally the same. This declaration "
                "serves as the foundational document for obtaining GST, bank "
                "account, Udyam, and other registrations."
            ),
        },
    }


# ---------------------------------------------------------------------------
# AOA Templates
# ---------------------------------------------------------------------------

def _generate_aoa(
    company_name: str,
    entity_type: str,
    authorized_capital: int,
    directors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate Articles of Association."""
    table_ref = _AOA_TABLE_REFERENCES.get(entity_type, _AOA_TABLE_REFERENCES["private_limited"])
    num_directors = max(len(directors), 2)

    aoa: Dict[str, Any] = {
        "document_type": "Articles of Association",
        "entity_type": entity_type,
        "table_reference": table_ref,
        "articles": {
            "1_preliminary": {
                "article_number": "1",
                "title": "Preliminary",
                "content": (
                    f"The regulations contained in {table_ref} shall apply to the Company "
                    f"so far as they are not inconsistent with these Articles."
                ),
            },
            "2_share_capital": {
                "article_number": "2",
                "title": "Share Capital and Variation of Rights",
                "content": (
                    f"The Authorized Share Capital of the Company is Rs. {authorized_capital:,}/- "
                    f"divided into {authorized_capital // 10} equity shares of Rs. 10/- each. "
                    f"The Company may, by ordinary resolution, increase the share capital."
                ),
            },
            "3_transfer_of_shares": {
                "article_number": "3",
                "title": "Transfer and Transmission of Shares",
                "content": (
                    "No share shall be transferred to any person who is not a member of the "
                    "Company without the prior approval of the Board of Directors. "
                    "The Board may, in its absolute discretion, decline to register any "
                    "transfer of shares."
                ),
            },
            "4_directors": {
                "article_number": "4",
                "title": "Directors",
                "content": (
                    f"The minimum number of directors shall be {num_directors} and the maximum "
                    f"shall be 15. The first directors of the Company shall be the persons "
                    f"named in the subscription to the Memorandum of Association."
                ),
                "first_directors": [d.get("full_name", "") for d in directors],
            },
            "5_board_meetings": {
                "article_number": "5",
                "title": "Board Meetings",
                "content": (
                    "The Board shall meet at least four times in each calendar year with a "
                    "maximum gap of 120 days between two consecutive meetings. "
                    "The quorum for a Board meeting shall be one-third of the total strength "
                    "or two directors, whichever is greater."
                ),
            },
            "6_general_meetings": {
                "article_number": "6",
                "title": "General Meetings",
                "content": (
                    "The Company shall hold an Annual General Meeting within six months from "
                    "the close of its financial year. Extraordinary General Meetings may be "
                    "called by the Board at any time."
                ),
            },
            "7_accounts_and_audit": {
                "article_number": "7",
                "title": "Accounts and Audit",
                "content": (
                    "The Company shall maintain proper books of accounts. The books shall be "
                    "audited by a qualified Chartered Accountant appointed at each AGM. "
                    "The financial year of the Company shall end on 31st March."
                ),
            },
            "8_dividends": {
                "article_number": "8",
                "title": "Dividends",
                "content": (
                    "The Company may, in general meeting, declare dividends. No dividend shall "
                    "be paid otherwise than out of profits of the Company. The Board may pay "
                    "interim dividends."
                ),
            },
            "9_borrowing_powers": {
                "article_number": "9",
                "title": "Borrowing Powers",
                "content": (
                    "The Board of Directors may, from time to time, borrow money for the "
                    "purposes of the Company. The total borrowings shall not exceed the "
                    "aggregate of paid-up share capital and free reserves without shareholder "
                    "approval by special resolution."
                ),
            },
            "10_common_seal": {
                "article_number": "10",
                "title": "Common Seal",
                "content": (
                    "The Company may have a common seal. The seal shall not be affixed to any "
                    "instrument except by the authority of a resolution of the Board."
                ),
            },
            "11_winding_up": {
                "article_number": "11",
                "title": "Winding Up",
                "content": (
                    "If the Company shall be wound up, the surplus assets shall be divided "
                    "among the members in proportion to the amount paid up on the shares held "
                    "by them respectively."
                ),
            },
        },
        "metadata": {
            "generated_date": date.today().isoformat(),
            "company_name": company_name,
            "entity_type": entity_type,
            "authorized_capital": authorized_capital,
        },
    }

    # OPC-specific modifications
    if entity_type == "opc":
        aoa["articles"]["12_opc_provisions"] = {
            "article_number": "12",
            "title": "OPC-Specific Provisions",
            "content": (
                "The Company, being a One Person Company, shall not be required to hold "
                "an Annual General Meeting. All resolutions may be passed by the sole member "
                "by entering them in the minutes book. The Company shall convert to a "
                "Private Limited Company if its paid-up share capital exceeds fifty lakh rupees "
                "or its average annual turnover exceeds two crore rupees."
            ),
        }

    # Section 8-specific modifications
    if entity_type == "section_8":
        aoa["articles"]["8_dividends"]["content"] = (
            "No dividend shall be paid to any member of the Company. "
            "All income and property of the Company shall be applied solely towards "
            "the promotion of its objects."
        )
        aoa["articles"]["12_section_8_provisions"] = {
            "article_number": "12",
            "title": "Section 8 Provisions",
            "content": (
                "The Company is licensed under Section 8 of the Companies Act, 2013. "
                "The profits, if any, or other income shall be applied solely for promoting "
                "the objects of the Company and no dividend shall be paid to the members."
            ),
        }

    return aoa


# ---------------------------------------------------------------------------
# LLM-powered business objects generation
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Legal disclaimer for all AI-generated legal content
# ---------------------------------------------------------------------------

DOCUMENT_DISCLAIMER = (
    "IMPORTANT DISCLAIMER: This document has been generated using AI assistance "
    "and standard templates. It is provided for informational and reference "
    "purposes only and does NOT constitute legal advice. Before using this "
    "document for any legal, regulatory, or compliance purpose:\n"
    "1. Have it reviewed by a qualified Company Secretary (CS) or Advocate.\n"
    "2. Verify all clauses comply with the latest Companies Act, 2013 amendments "
    "and applicable MCA notifications.\n"
    "3. Ensure all factual details (names, addresses, capital, objects) are "
    "accurate and match your actual company records.\n"
    "4. State-specific stamp duty and registration requirements may apply.\n"
    "Anvils Pvt Ltd is not liable for any consequences arising from the use "
    "of AI-generated legal documents without professional review."
)


async def _generate_business_objects_with_llm(
    business_description: str,
    entity_type: str,
) -> List[str]:
    """
    Use LLM to generate custom business objects clause from user's description.
    Falls back to generic objects if LLM is unavailable.

    Note: LLM-generated clauses must be reviewed by a CS/Advocate before filing.
    The Companies Act 2013 requires objects clauses to be legally precise.
    """
    from src.services.llm_service import llm_service

    if llm_service.provider == "mock":
        return _default_business_objects(business_description)

    system_prompt = (
        "You are an expert Indian company law attorney specializing in drafting "
        "Memorandum of Association (MOA) clauses. Given a business description, "
        "generate 5-8 specific, well-drafted Main Objects clauses suitable for "
        "an Indian company's MOA under the Companies Act, 2013.\n\n"
        "Each object should:\n"
        "1. Start with 'To' followed by a verb\n"
        "2. Be specific but broad enough for future business expansion\n"
        "3. Be legally precise and use standard MOA drafting language\n"
        "4. Cover the core business and related/ancillary activities\n"
        "5. NOT include any activity that requires a special licence (e.g., banking, "
        "insurance, NBFC, chit fund) unless the business description explicitly mentions it\n"
        "6. NOT include objects related to charitable/non-profit activities for non-Section 8 companies\n\n"
        "Return only a JSON array of strings."
    )

    user_msg = (
        f"Business description: {business_description}\n"
        f"Entity type: {entity_type}\n"
        f"Generate MOA Main Objects clauses."
    )

    try:
        response = await llm_service.chat(
            system_prompt=system_prompt,
            user_message=user_msg,
            temperature=0.3,
            max_tokens=1024,
        )
        import json
        try:
            objects = json.loads(response)
            if isinstance(objects, list) and len(objects) > 0:
                # Validate: each object should start with "To"
                validated = []
                for obj in objects:
                    obj_str = str(obj).strip()
                    if obj_str and obj_str[0:2].lower() == "to":
                        validated.append(obj_str)
                    else:
                        logger.warning("Skipping malformed MOA object: %s", obj_str[:50])
                return validated if validated else _default_business_objects(business_description)
        except json.JSONDecodeError:
            # Try to extract JSON array
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                objects = json.loads(response[start:end])
                if isinstance(objects, list):
                    return objects
    except Exception as exc:
        logger.warning("LLM business objects generation failed: %s", exc)

    return _default_business_objects(business_description)


async def _customize_clause_with_llm(
    clause_content: str,
    customization_request: str,
) -> str:
    """Use LLM to customize a specific clause based on user request."""
    from src.services.llm_service import llm_service

    if llm_service.provider == "mock":
        return clause_content + f"\n[Customized as per request: {customization_request}]"

    system_prompt = (
        "You are an expert Indian company law attorney. Modify the given legal clause "
        "according to the user's request while maintaining legal validity and compliance "
        "with the Companies Act, 2013. Return only the modified clause text."
    )

    user_msg = (
        f"Original clause:\n{clause_content}\n\n"
        f"Modification requested: {customization_request}"
    )

    try:
        response = await llm_service.chat(
            system_prompt=system_prompt,
            user_message=user_msg,
            temperature=0.2,
            max_tokens=512,
        )
        return response.strip()
    except Exception:
        return clause_content


def _default_business_objects(description: str) -> List[str]:
    """Generate default business objects when LLM is unavailable."""
    desc_lower = description.lower()

    objects = [
        f"To carry on the business of {description} and all activities "
        f"connected therewith or incidental thereto.",
    ]

    if any(w in desc_lower for w in ["tech", "software", "digital", "it", "app"]):
        objects.extend([
            "To design, develop, maintain, and market software applications, "
            "websites, mobile applications, and digital platforms.",
            "To provide information technology consulting, outsourcing, and "
            "managed services to clients across industries.",
            "To engage in data analytics, artificial intelligence, machine learning, "
            "and other emerging technology services.",
        ])
    elif any(w in desc_lower for w in ["consult", "advisory", "professional"]):
        objects.extend([
            "To provide management consulting, advisory, and professional services "
            "to businesses and organizations.",
            "To conduct research, surveys, and studies for clients in various industries.",
            "To organize training programs, workshops, seminars, and conferences.",
        ])
    elif any(w in desc_lower for w in ["trade", "commerce", "retail", "wholesale"]):
        objects.extend([
            "To carry on the business of trading, importing, exporting, buying, selling, "
            "and dealing in goods, commodities, and merchandise of all kinds.",
            "To establish and operate retail and wholesale outlets, warehouses, "
            "and distribution centers.",
            "To engage in e-commerce and online marketplace operations.",
        ])
    else:
        objects.extend([
            "To carry on any other business or activity which may seem to the Company "
            "capable of being conveniently carried on in connection with the above.",
            "To acquire, hold, manage, develop, and dispose of any property, "
            "assets, and investments.",
            "To enter into contracts, agreements, and arrangements with any person, "
            "firm, or body corporate for furthering the objects of the Company.",
        ])

    objects.extend([
        "To borrow or raise money in such manner as the Company shall think fit "
        "and to secure the repayment thereof.",
        "To invest and deal with the moneys of the Company not immediately required "
        "in such manner as may from time to time be determined.",
    ])

    return objects


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _number_to_words(n: int) -> str:
    """Convert number to Indian English words (simplified for common amounts)."""
    if n <= 0:
        return "zero"

    units = ["", "one", "two", "three", "four", "five", "six", "seven",
             "eight", "nine", "ten", "eleven", "twelve", "thirteen",
             "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty",
            "seventy", "eighty", "ninety"]

    if n < 20:
        return units[n]
    if n < 100:
        return tens[n // 10] + (" " + units[n % 10] if n % 10 else "")

    parts = []
    crore = n // 10000000
    if crore:
        parts.append(_number_to_words(crore) + " crore")
        n %= 10000000

    lakh = n // 100000
    if lakh:
        parts.append(_number_to_words(lakh) + " lakh")
        n %= 100000

    thousand = n // 1000
    if thousand:
        parts.append(_number_to_words(thousand) + " thousand")
        n %= 1000

    hundred = n // 100
    if hundred:
        parts.append(_number_to_words(hundred) + " hundred")
        n %= 100

    if n:
        parts.append(_number_to_words(n))

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Main Service Class
# ---------------------------------------------------------------------------

class LegalDocumentService:
    """
    Service for generating MOA, AOA, and LLP Agreement documents.
    Output is JSON/dict — PDF generation is deferred to Phase 9.
    """

    async def generate_moa(
        self,
        company_name: str,
        entity_type: str,
        state: str,
        authorized_capital: int = 100000,
        business_description: str = "",
        directors: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate the primary formation document based on entity type.

        Returns MOA for companies, LLP Agreement for LLPs, Partnership
        Deed for partnerships, and Sole Proprietorship Declaration for
        sole proprietorships.
        """
        if directors is None:
            directors = []

        # Generate business objects (LLM-enhanced or default)
        if business_description:
            business_objects = await _generate_business_objects_with_llm(
                business_description, entity_type
            )
        else:
            business_objects = _default_business_objects("general business activities")

        if entity_type in ("private_limited", "public_limited"):
            return _generate_moa_private_limited(
                company_name, state, authorized_capital, business_objects, directors
            )
        elif entity_type == "opc":
            return _generate_moa_opc(
                company_name, state, authorized_capital, business_objects, directors
            )
        elif entity_type == "section_8":
            return _generate_moa_section_8(
                company_name, state, business_objects, directors
            )
        elif entity_type == "llp":
            return _generate_llp_agreement(
                company_name, state, business_objects, directors, authorized_capital
            )
        elif entity_type == "partnership":
            return _generate_partnership_deed(
                company_name, state, business_objects, directors, authorized_capital
            )
        elif entity_type == "sole_proprietorship":
            proprietor = directors[0] if directors else {}
            return _generate_sole_prop_declaration(
                company_name, state, business_objects, proprietor
            )
        else:
            logger.warning("Unknown entity_type %r, defaulting to private_limited", entity_type)
            return _generate_moa_private_limited(
                company_name, state, authorized_capital, business_objects, directors
            )

    async def generate_aoa(
        self,
        company_name: str,
        entity_type: str,
        authorized_capital: int = 100000,
        directors: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate Articles of Association (companies only)."""
        if directors is None:
            directors = []

        if entity_type == "llp":
            return {
                "document_type": "Not Applicable",
                "entity_type": "llp",
                "message": "LLPs use an LLP Agreement instead of AOA. Use generate_moa() for LLP.",
            }

        if entity_type == "partnership":
            return {
                "document_type": "Not Applicable",
                "entity_type": "partnership",
                "message": (
                    "Partnership firms use a Partnership Deed instead of AOA. "
                    "Use generate_moa() to generate the Partnership Deed."
                ),
            }

        if entity_type == "sole_proprietorship":
            return {
                "document_type": "Not Applicable",
                "entity_type": "sole_proprietorship",
                "message": (
                    "Sole proprietorships use a Declaration/Affidavit instead of AOA. "
                    "Use generate_moa() to generate the Sole Proprietorship Declaration."
                ),
            }

        return _generate_aoa(company_name, entity_type, authorized_capital, directors)

    async def customize_clause(
        self,
        document: Dict[str, Any],
        clause_key: str,
        customization_request: str,
    ) -> Dict[str, Any]:
        """
        Customize a specific clause in a generated document using LLM.
        Returns the updated document.
        """
        # Navigate to the clause
        clauses = document.get("clauses") or document.get("articles") or document.get("sections", {})
        if clause_key not in clauses:
            return document

        clause = clauses[clause_key]
        original_content = clause.get("content", "")

        if original_content:
            customized = await _customize_clause_with_llm(
                original_content, customization_request
            )
            clause["content"] = customized
            clause["is_customized"] = True

        return document

    async def generate_full_document_set(
        self,
        company_name: str,
        entity_type: str,
        state: str,
        authorized_capital: int = 100000,
        business_description: str = "",
        directors: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate the full document set for any entity type."""
        primary_doc = await self.generate_moa(
            company_name, entity_type, state, authorized_capital,
            business_description, directors
        )
        secondary_doc = await self.generate_aoa(
            company_name, entity_type, authorized_capital, directors
        )

        # Label documents appropriately per entity type
        doc_labels = {
            "llp": ("llp_agreement", "aoa"),
            "partnership": ("partnership_deed", "aoa"),
            "sole_proprietorship": ("declaration", "aoa"),
        }
        primary_key, secondary_key = doc_labels.get(entity_type, ("moa", "aoa"))

        review_notes = {
            "partnership": (
                "This is a draft Partnership Deed. It should be reviewed by a "
                "qualified lawyer, printed on stamp paper, notarized, and filed "
                "with the Registrar of Firms (Form C)."
            ),
            "sole_proprietorship": (
                "This is a draft declaration/affidavit. It should be reviewed, "
                "printed on stamp paper, and notarized. Use it for GST, bank "
                "account, Udyam, and Shop & Establishment registrations."
            ),
        }
        notes = review_notes.get(entity_type, (
            "These are draft documents generated based on templates. "
            "They should be reviewed by a qualified Company Secretary or "
            "legal professional before filing with MCA."
        ))

        return {
            "company_name": company_name,
            "entity_type": entity_type,
            "documents": {
                primary_key: primary_doc,
                secondary_key: secondary_doc,
            },
            "generated_date": date.today().isoformat(),
            "status": "draft",
            "notes": notes,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
legal_document_service = LegalDocumentService()
