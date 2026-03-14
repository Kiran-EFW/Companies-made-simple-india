"""
Entity Comparison Service — provides side-by-side comparison data for all
Indian business entity types.

Covers: Private Limited, OPC, LLP, Section 8, Sole Proprietorship,
Partnership, and Public Limited.
"""

from typing import Optional, List, Dict, Any


# ---------------------------------------------------------------------------
# Comparison Data
# ---------------------------------------------------------------------------

COMPARISON_DATA: Dict[str, Dict[str, Any]] = {
    "private_limited": {
        "name": "Private Limited Company",
        "governing_law": "Companies Act, 2013",
        "min_members": 2,
        "max_members": 200,
        "min_directors": 2,
        "max_directors": 15,
        "liability": "Limited",
        "separate_entity": True,
        "perpetual_succession": True,
        "can_raise_equity": True,
        "mandatory_audit": True,
        "transferability_of_shares": "Restricted (requires board/member approval)",
        "foreign_ownership_allowed": True,
        "annual_filings": ["AOC-4", "MGT-7", "DIR-3 KYC", "ADT-1"],
        "compliance_level": "High",
        "typical_cost": "Rs 8,000 - Rs 25,000",
        "time_to_incorporate": "7-15 days",
        "tax_rate": "25% (if turnover <= Rs 400 Cr) / 30%",
        "minimum_capital": "No statutory minimum (Rs 1 lakh practical)",
        "ideal_for": "Startups, funded businesses, tech companies",
        "advantages": [
            "Most investor-friendly structure",
            "Limited liability protection",
            "Perpetual succession",
            "Easy to raise equity funding",
            "Eligible for Startup India benefits",
        ],
        "disadvantages": [
            "Higher compliance burden",
            "Mandatory statutory audit",
            "Cannot accept deposits from public",
            "Restrictions on share transfer",
        ],
    },
    "opc": {
        "name": "One Person Company",
        "governing_law": "Companies Act, 2013 (Section 2(62))",
        "min_members": 1,
        "max_members": 1,
        "min_directors": 1,
        "max_directors": 15,
        "liability": "Limited",
        "separate_entity": True,
        "perpetual_succession": True,
        "can_raise_equity": False,
        "mandatory_audit": True,
        "transferability_of_shares": "Not applicable (single member)",
        "foreign_ownership_allowed": False,
        "annual_filings": ["AOC-4", "MGT-7", "DIR-3 KYC"],
        "compliance_level": "Medium",
        "typical_cost": "Rs 6,000 - Rs 18,000",
        "time_to_incorporate": "7-15 days",
        "tax_rate": "25% (if turnover <= Rs 400 Cr) / 30%",
        "minimum_capital": "No statutory minimum",
        "ideal_for": "Solo entrepreneurs, freelancers wanting limited liability",
        "advantages": [
            "Single person ownership",
            "Limited liability",
            "Simpler compliance than Pvt Ltd",
            "No AGM requirement",
            "Separate legal entity",
        ],
        "disadvantages": [
            "Must convert if turnover > Rs 2 Cr or capital > Rs 50 Lakh",
            "Cannot raise equity funding",
            "Only Indian residents and citizens can form",
            "Requires nominee director",
        ],
    },
    "llp": {
        "name": "Limited Liability Partnership",
        "governing_law": "LLP Act, 2008",
        "min_members": 2,
        "max_members": "No limit",
        "min_directors": 2,
        "max_directors": "No limit",
        "liability": "Limited",
        "separate_entity": True,
        "perpetual_succession": True,
        "can_raise_equity": False,
        "mandatory_audit": False,
        "transferability_of_shares": "Not applicable (no shares, partnership interest)",
        "foreign_ownership_allowed": True,
        "annual_filings": ["Form 11 (Annual Return)", "Form 8 (Statement of Accounts)"],
        "compliance_level": "Low-Medium",
        "typical_cost": "Rs 6,000 - Rs 20,000",
        "time_to_incorporate": "10-15 days",
        "tax_rate": "30% (flat rate, no surcharge up to Rs 1 Cr)",
        "minimum_capital": "No minimum",
        "ideal_for": "Professional services, consulting, small businesses",
        "advantages": [
            "Limited liability for all partners",
            "No mandatory audit (if turnover < Rs 40L and capital < Rs 25L)",
            "Flexible management structure",
            "Lower compliance cost than Pvt Ltd",
            "Partners taxed individually on profit share",
        ],
        "disadvantages": [
            "Cannot raise equity funding (no shares)",
            "Cannot issue ESOPs",
            "Less investor-friendly",
            "Must have at least 2 designated partners",
        ],
    },
    "section_8": {
        "name": "Section 8 Company (Non-Profit)",
        "governing_law": "Companies Act, 2013 (Section 8)",
        "min_members": 2,
        "max_members": "No limit",
        "min_directors": 2,
        "max_directors": 15,
        "liability": "Limited",
        "separate_entity": True,
        "perpetual_succession": True,
        "can_raise_equity": False,
        "mandatory_audit": True,
        "transferability_of_shares": "Not applicable",
        "foreign_ownership_allowed": True,
        "annual_filings": ["AOC-4", "MGT-7", "DIR-3 KYC", "INC-12 License renewal"],
        "compliance_level": "High",
        "typical_cost": "Rs 15,000 - Rs 30,000",
        "time_to_incorporate": "30-60 days",
        "tax_rate": "Exempt (with 12A/80G registration)",
        "minimum_capital": "No minimum",
        "ideal_for": "NGOs, foundations, social enterprises, charitable organizations",
        "advantages": [
            "Tax exemptions (12A, 80G)",
            "Can receive donations and CSR funds",
            "No minimum capital requirement",
            "High credibility and trust",
            "No stamp duty on MOA/AOA in most states",
        ],
        "disadvantages": [
            "Profit distribution prohibited",
            "INC-12 license required (longer process)",
            "Higher compliance burden",
            "Activities limited to stated objects",
            "Cannot convert to for-profit company easily",
        ],
    },
    "sole_proprietorship": {
        "name": "Sole Proprietorship",
        "governing_law": "No specific act (various registrations)",
        "min_members": 1,
        "max_members": 1,
        "min_directors": 0,
        "max_directors": 0,
        "liability": "Unlimited",
        "separate_entity": False,
        "perpetual_succession": False,
        "can_raise_equity": False,
        "mandatory_audit": False,
        "transferability_of_shares": "Not applicable",
        "foreign_ownership_allowed": False,
        "annual_filings": ["ITR (Income Tax Return)", "GST Returns (if applicable)"],
        "compliance_level": "Very Low",
        "typical_cost": "Rs 2,000 - Rs 5,000",
        "time_to_incorporate": "1-7 days",
        "tax_rate": "Individual slab rates",
        "minimum_capital": "None",
        "ideal_for": "Micro-businesses, side hustles, freelancers, early-stage testing",
        "advantages": [
            "Easiest to set up",
            "Minimal compliance",
            "Full control and decision-making",
            "Lowest cost to start",
            "Tax benefits under individual slabs",
        ],
        "disadvantages": [
            "Unlimited personal liability",
            "Cannot raise funding",
            "Not a separate legal entity",
            "No perpetual succession",
            "Limited growth potential",
        ],
    },
    "partnership": {
        "name": "Partnership Firm",
        "governing_law": "Indian Partnership Act, 1932",
        "min_members": 2,
        "max_members": 50,
        "min_directors": 0,
        "max_directors": 0,
        "liability": "Unlimited (joint and several)",
        "separate_entity": False,
        "perpetual_succession": False,
        "can_raise_equity": False,
        "mandatory_audit": False,
        "transferability_of_shares": "Not applicable (partnership interest, requires consent)",
        "foreign_ownership_allowed": False,
        "annual_filings": ["ITR (Income Tax Return)", "GST Returns (if applicable)"],
        "compliance_level": "Low",
        "typical_cost": "Rs 3,000 - Rs 10,000",
        "time_to_incorporate": "7-15 days",
        "tax_rate": "30% (flat rate for firms)",
        "minimum_capital": "None",
        "ideal_for": "Traditional businesses, family businesses, professional firms",
        "advantages": [
            "Easy to form with partnership deed",
            "Low compliance requirements",
            "Flexible profit sharing",
            "No minimum capital needed",
            "Registration is optional (but recommended)",
        ],
        "disadvantages": [
            "Unlimited personal liability for all partners",
            "Not a separate legal entity",
            "No perpetual succession",
            "Cannot raise equity funding",
            "Unregistered firm cannot sue in court",
        ],
    },
    "public_limited": {
        "name": "Public Limited Company",
        "governing_law": "Companies Act, 2013",
        "min_members": 7,
        "max_members": "No limit",
        "min_directors": 3,
        "max_directors": 15,
        "liability": "Limited",
        "separate_entity": True,
        "perpetual_succession": True,
        "can_raise_equity": True,
        "mandatory_audit": True,
        "transferability_of_shares": "Freely transferable (no restrictions)",
        "foreign_ownership_allowed": True,
        "annual_filings": [
            "AOC-4", "MGT-7", "DIR-3 KYC", "ADT-1",
            "Secretarial Audit Report", "Corporate Governance Report (if listed)",
        ],
        "compliance_level": "Very High",
        "typical_cost": "Rs 15,000 - Rs 50,000",
        "time_to_incorporate": "15-30 days",
        "tax_rate": "25% (if turnover <= Rs 400 Cr) / 30%",
        "minimum_capital": "Rs 5,00,000 (Rs 5 Lakhs)",
        "ideal_for": "Large companies planning IPO, 7+ shareholders, public fundraising",
        "advantages": [
            "Can raise capital from public (IPO)",
            "Freely transferable shares",
            "Higher credibility and trust",
            "No restriction on number of shareholders",
            "Can list on stock exchanges",
        ],
        "disadvantages": [
            "Highest compliance burden",
            "Mandatory secretarial audit",
            "Minimum 7 shareholders, 3 directors",
            "Mandatory Company Secretary",
            "Subject to SEBI regulations if listed",
            "Cannot restrict share transfers",
        ],
    },
}


class EntityComparisonService:
    """Service for comparing Indian business entity types."""

    def compare(self, entity_types: List[str]) -> Dict[str, Any]:
        """
        Compare multiple entity types side by side.

        Args:
            entity_types: List of entity type keys to compare.

        Returns:
            Side-by-side comparison data.
        """
        comparison: Dict[str, Any] = {}
        valid_types: List[str] = []

        for et in entity_types:
            if et in COMPARISON_DATA:
                comparison[et] = COMPARISON_DATA[et]
                valid_types.append(et)

        if not valid_types:
            return {
                "error": "No valid entity types provided",
                "available_types": list(COMPARISON_DATA.keys()),
            }

        # Build comparison rows for easy rendering
        comparison_fields = [
            "name", "governing_law", "min_members", "max_members",
            "min_directors", "max_directors", "liability", "separate_entity",
            "perpetual_succession", "can_raise_equity", "mandatory_audit",
            "transferability_of_shares", "foreign_ownership_allowed",
            "annual_filings", "compliance_level", "typical_cost",
            "time_to_incorporate", "tax_rate", "minimum_capital", "ideal_for",
        ]

        rows: List[Dict[str, Any]] = []
        for field in comparison_fields:
            row = {
                "field": field,
                "label": field.replace("_", " ").title(),
                "values": {},
            }
            for et in valid_types:
                row["values"][et] = COMPARISON_DATA[et].get(field, "N/A")
            rows.append(row)

        return {
            "entity_types": valid_types,
            "entities": comparison,
            "comparison_rows": rows,
            "total_compared": len(valid_types),
        }

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """Get summary of all entity types."""
        summaries: List[Dict[str, Any]] = []

        for key, data in COMPARISON_DATA.items():
            summaries.append({
                "entity_type": key,
                "name": data["name"],
                "governing_law": data["governing_law"],
                "liability": data["liability"],
                "min_members": data["min_members"],
                "max_members": data["max_members"],
                "can_raise_equity": data["can_raise_equity"],
                "mandatory_audit": data["mandatory_audit"],
                "compliance_level": data["compliance_level"],
                "typical_cost": data["typical_cost"],
                "time_to_incorporate": data["time_to_incorporate"],
                "ideal_for": data["ideal_for"],
                "separate_entity": data["separate_entity"],
            })

        return summaries


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
entity_comparison_service = EntityComparisonService()
