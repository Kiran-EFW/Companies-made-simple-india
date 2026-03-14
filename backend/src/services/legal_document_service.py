"""
Legal Document Service — generates MOA, AOA, and LLP Agreement templates.

Supports Private Limited, OPC, LLP, and Section 8 entity types.
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
                        "address": d.get("address", ""),
                        "shares_subscribed": max(1, (authorized_capital // 10) // max(len(directors), 1)),
                    }
                    for d in directors
                ],
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
                        "address": d.get("address", ""),
                    }
                    for d in directors
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
            "10_dispute_resolution": {
                "section_number": "10",
                "title": "Dispute Resolution",
                "content": (
                    "Any dispute arising out of or in connection with this Agreement shall first "
                    "be referred to mediation. If mediation fails, the dispute shall be referred "
                    "to arbitration in accordance with the Arbitration and Conciliation Act, 1996."
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

async def _generate_business_objects_with_llm(
    business_description: str,
    entity_type: str,
) -> List[str]:
    """
    Use LLM to generate custom business objects clause from user's description.
    Falls back to generic objects if LLM is unavailable.
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
        "3. Be legally precise\n"
        "4. Cover the core business and related activities\n\n"
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
                return objects
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
        """Generate Memorandum of Association based on entity type."""
        if directors is None:
            directors = []

        # Generate business objects (LLM-enhanced or default)
        if business_description:
            business_objects = await _generate_business_objects_with_llm(
                business_description, entity_type
            )
        else:
            business_objects = _default_business_objects("general business activities")

        if entity_type == "private_limited" or entity_type == "public_limited":
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
        else:
            # Default to private limited
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
        """Generate Articles of Association."""
        if directors is None:
            directors = []

        if entity_type == "llp":
            # LLPs don't have AOA, they have LLP Agreement (generated via MOA)
            return {
                "document_type": "Not Applicable",
                "entity_type": "llp",
                "message": "LLPs use an LLP Agreement instead of AOA. Use generate_moa() for LLP.",
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
        """Generate both MOA and AOA (or LLP Agreement) as a complete set."""
        moa = await self.generate_moa(
            company_name, entity_type, state, authorized_capital,
            business_description, directors
        )
        aoa = await self.generate_aoa(
            company_name, entity_type, authorized_capital, directors
        )

        return {
            "company_name": company_name,
            "entity_type": entity_type,
            "documents": {
                "moa": moa,
                "aoa": aoa,
            },
            "generated_date": date.today().isoformat(),
            "status": "draft",
            "notes": (
                "These are draft documents generated based on templates. "
                "They should be reviewed by a qualified Company Secretary or "
                "legal professional before filing with MCA."
            ),
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
legal_document_service = LegalDocumentService()
