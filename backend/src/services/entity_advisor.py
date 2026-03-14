"""
Entity Advisor — recommends the best company type based on wizard answers.

Uses decision tree as primary logic with optional LLM enhancement for
personalized reasoning when an API key is available.
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


def recommend_entity(
    is_solo: bool,
    seeking_funding: bool,
    expected_revenue: str,  # "below_50l", "50l_to_2cr", "above_2cr"
    is_nonprofit: bool,
    has_foreign_involvement: bool = False,
    is_professional_services: bool = False,
    is_family_business: bool = False,
    num_founders: int = 2,
    planning_ipo: bool = False,
    business_description: str = "",
    use_llm: bool = True,
) -> dict:
    """
    Recommend the best entity type based on founder's situation.

    Returns a recommendation with primary choice, alternatives, and reasoning.
    Uses decision tree logic as the base, optionally enhanced with LLM reasoning.
    """
    # Always run the decision tree first (fast, deterministic)
    decision_tree_result = _decision_tree_recommend(
        is_solo=is_solo,
        seeking_funding=seeking_funding,
        expected_revenue=expected_revenue,
        is_nonprofit=is_nonprofit,
        has_foreign_involvement=has_foreign_involvement,
        is_professional_services=is_professional_services,
        is_family_business=is_family_business,
        num_founders=num_founders,
        planning_ipo=planning_ipo,
    )

    # Optionally enhance with LLM reasoning
    if use_llm and business_description:
        try:
            llm_enhancement = _get_llm_enhancement(
                decision_tree_result=decision_tree_result,
                is_solo=is_solo,
                seeking_funding=seeking_funding,
                expected_revenue=expected_revenue,
                is_nonprofit=is_nonprofit,
                has_foreign_involvement=has_foreign_involvement,
                is_professional_services=is_professional_services,
                business_description=business_description,
            )
            if llm_enhancement:
                decision_tree_result["llm_reasoning"] = llm_enhancement.get("reasoning", "")
                decision_tree_result["llm_additional_considerations"] = llm_enhancement.get(
                    "additional_considerations", []
                )
                # LLM can adjust the match score slightly based on context
                if llm_enhancement.get("score_adjustment"):
                    adj = llm_enhancement["score_adjustment"]
                    current_score = decision_tree_result["recommended"]["match_score"]
                    new_score = max(50, min(100, current_score + adj))
                    decision_tree_result["recommended"]["match_score"] = new_score
        except Exception as exc:
            logger.warning("LLM enhancement for entity advisor failed: %s", exc)
            # Decision tree result is still valid, just without LLM reasoning

    return decision_tree_result


def _decision_tree_recommend(
    is_solo: bool,
    seeking_funding: bool,
    expected_revenue: str,
    is_nonprofit: bool,
    has_foreign_involvement: bool = False,
    is_professional_services: bool = False,
    is_family_business: bool = False,
    num_founders: int = 2,
    planning_ipo: bool = False,
) -> dict:
    """
    Core decision tree logic for entity recommendation.
    Deterministic, no external dependencies.
    """
    recommendations: List[Dict[str, Any]] = []

    # -- Non-Profit Path --
    if is_nonprofit:
        recommendations.append({
            "entity_type": "section_8",
            "name": "Section 8 Company",
            "match_score": 95,
            "pros": [
                "Recognized non-profit legal structure",
                "Tax exemptions available (12A/80G)",
                "No minimum capital requirement",
                "Can receive donations and grants",
            ],
            "cons": [
                "Higher compliance burden",
                "Profit distribution prohibited",
                "INC-12 license required (longer process)",
                "Regular audits mandatory",
            ],
            "best_for": "NGOs, social enterprises, foundations, charitable organizations",
        })
        return _build_response(recommendations)

    # -- Public Limited / IPO Path --
    if planning_ipo or num_founders >= 7:
        recommendations.append({
            "entity_type": "public_limited",
            "name": "Public Limited Company",
            "match_score": 95 if planning_ipo else 80,
            "pros": [
                "Can raise capital from public through IPO",
                "Freely transferable shares",
                "Higher credibility and market trust",
                "No limit on number of shareholders",
                "Can list on stock exchanges",
            ],
            "cons": [
                "Highest compliance burden among all entities",
                "Minimum 7 shareholders, 3 directors required",
                "Mandatory secretarial audit",
                "Mandatory Company Secretary appointment",
                "Subject to SEBI regulations if listed",
            ],
            "best_for": "Large companies planning IPO, 7+ shareholders, public fundraising",
        })
        if not planning_ipo:
            # Also recommend Private Limited as alternative
            recommendations.append({
                "entity_type": "private_limited",
                "name": "Private Limited Company",
                "match_score": 85,
                "pros": [
                    "Lower compliance than Public Ltd",
                    "Limited liability protection",
                    "Can raise equity from investors",
                    "Easier to manage with fewer compliance requirements",
                ],
                "cons": [
                    "Maximum 200 shareholders",
                    "Cannot raise capital from general public",
                    "Shares transfer restricted",
                ],
                "best_for": "Growth businesses not yet ready for public listing",
            })
        else:
            recommendations.append({
                "entity_type": "private_limited",
                "name": "Private Limited Company",
                "match_score": 70,
                "pros": [
                    "Start as Pvt Ltd and convert to Public Ltd later",
                    "Lower initial compliance",
                    "Limited liability",
                ],
                "cons": [
                    "Will need conversion to Public Ltd before IPO",
                    "Maximum 200 shareholders",
                ],
                "best_for": "Companies planning IPO in 2-3 years (start private, convert later)",
            })
        return _build_response(recommendations)

    # -- Solo Founder Path --
    if is_solo:
        if expected_revenue == "above_2cr" or seeking_funding:
            # Solo but high-growth -- start with Pvt Ltd
            recommendations.append({
                "entity_type": "private_limited",
                "name": "Private Limited Company",
                "match_score": 90,
                "pros": [
                    "Investor-friendly structure",
                    "Limited liability protection",
                    "Perpetual succession",
                    "Easier to raise funding",
                ],
                "cons": [
                    "Requires minimum 2 directors (you can add a nominee)",
                    "Higher compliance burden",
                    "Mandatory audits",
                ],
                "best_for": "Growth-oriented solo founders planning to raise funding",
            })
            recommendations.append({
                "entity_type": "opc",
                "name": "One Person Company",
                "match_score": 75,
                "pros": [
                    "Single person ownership and control",
                    "Limited liability",
                    "Simpler compliance than Pvt Ltd",
                ],
                "cons": [
                    "Must convert to Pvt Ltd if turnover > Rs 2 Cr or capital > Rs 50 Lakh",
                    "Cannot raise equity funding",
                    "Less investor-friendly",
                ],
                "best_for": "Solo founders starting lean",
            })
        else:
            # Solo, moderate revenue
            recommendations.append({
                "entity_type": "opc",
                "name": "One Person Company",
                "match_score": 92,
                "pros": [
                    "Perfect for solo entrepreneurs",
                    "Limited liability protection",
                    "Simpler compliance than Pvt Ltd",
                    "Full ownership and control",
                ],
                "cons": [
                    "Must convert to Pvt Ltd if turnover > Rs 2 Cr or capital > Rs 50 Lakh",
                    "Cannot raise equity funding",
                    "Requires a nominee director",
                ],
                "best_for": "Solo freelancers, consultants, and small business owners",
            })
            recommendations.append({
                "entity_type": "sole_proprietorship",
                "name": "Sole Proprietorship",
                "match_score": 70,
                "pros": [
                    "Easiest to set up",
                    "Minimal compliance",
                    "Full control",
                    "Lowest cost",
                ],
                "cons": [
                    "No limited liability -- personal assets at risk",
                    "Cannot raise funding",
                    "Not a separate legal entity",
                ],
                "best_for": "Micro-businesses, side hustles, early-stage testing",
            })

    # -- Team / Multi-Founder Path --
    else:
        if seeking_funding or expected_revenue == "above_2cr":
            recommendations.append({
                "entity_type": "private_limited",
                "name": "Private Limited Company",
                "match_score": 95,
                "pros": [
                    "Most investor-friendly structure in India",
                    "Limited liability for all shareholders",
                    "Perpetual succession -- company survives founders",
                    "Easy to issue ESOPs and share options",
                    "Eligible for Startup India benefits",
                ],
                "cons": [
                    "Higher compliance burden (4 board meetings/yr, AGM, annual filings)",
                    "Mandatory statutory audit",
                    "More expensive to maintain",
                ],
                "best_for": "Funded startups, tech companies, growth businesses",
            })
        elif is_professional_services:
            recommendations.append({
                "entity_type": "llp",
                "name": "Limited Liability Partnership",
                "match_score": 95,
                "pros": [
                    "Ideal for professional services (CA, CS, lawyers, consultants)",
                    "Limited liability for all partners",
                    "No mandatory audit if turnover < Rs 40L and capital < Rs 25L",
                    "Flexible profit sharing via LLP Agreement",
                    "Lower compliance than Pvt Ltd",
                ],
                "cons": [
                    "Cannot raise equity funding (no shares)",
                    "Partners are taxed individually",
                    "Less investor-friendly than Pvt Ltd",
                ],
                "best_for": "Professional services firms, consulting, advisory",
            })
        elif is_family_business:
            # Family/traditional businesses -- Partnership is a strong fit
            recommendations.append({
                "entity_type": "partnership",
                "name": "Partnership Firm",
                "match_score": 88,
                "pros": [
                    "Simple and easy to form with partnership deed",
                    "Flexible profit sharing among family members",
                    "Low compliance requirements",
                    "No minimum capital needed",
                    "Well-suited for traditional and family businesses",
                ],
                "cons": [
                    "Unlimited personal liability for all partners",
                    "Not a separate legal entity",
                    "No perpetual succession",
                    "Cannot raise equity funding",
                    "Unregistered firm cannot sue in court",
                ],
                "best_for": "Family businesses, traditional trades, local businesses",
            })
            recommendations.append({
                "entity_type": "llp",
                "name": "Limited Liability Partnership",
                "match_score": 78,
                "pros": [
                    "Limited liability protection (unlike partnership)",
                    "Separate legal entity",
                    "Can convert from partnership easily",
                ],
                "cons": [
                    "Slightly higher compliance than partnership",
                    "Cannot raise equity funding",
                    "Requires MCA registration",
                ],
                "best_for": "Family businesses wanting limited liability protection",
            })
            recommendations.append({
                "entity_type": "private_limited",
                "name": "Private Limited Company",
                "match_score": 65,
                "pros": [
                    "Most versatile structure",
                    "Can raise funding later",
                    "Limited liability",
                ],
                "cons": [
                    "Higher compliance burden",
                    "More expensive to run",
                ],
                "best_for": "Family businesses planning significant growth",
            })
        else:
            recommendations.append({
                "entity_type": "llp",
                "name": "Limited Liability Partnership",
                "match_score": 85,
                "pros": [
                    "Limited liability for all partners",
                    "Flexible management structure",
                    "No mandatory audit for small LLPs",
                    "Lower compliance cost",
                ],
                "cons": [
                    "Cannot issue shares or raise equity funding",
                    "Must convert to Pvt Ltd for investor funding",
                ],
                "best_for": "Small businesses, bootstrapped teams, service firms",
            })
            recommendations.append({
                "entity_type": "private_limited",
                "name": "Private Limited Company",
                "match_score": 75,
                "pros": [
                    "Most versatile structure",
                    "Can raise funding later",
                    "Limited liability",
                ],
                "cons": [
                    "Higher compliance burden",
                    "More expensive to run",
                ],
                "best_for": "Teams planning to scale or raise funding in the future",
            })
            # Add partnership as an option for non-funded teams
            recommendations.append({
                "entity_type": "partnership",
                "name": "Partnership Firm",
                "match_score": 60,
                "pros": [
                    "Simplest multi-person structure",
                    "Lowest cost to set up",
                    "Minimal compliance",
                    "Flexible profit sharing",
                ],
                "cons": [
                    "Unlimited personal liability",
                    "Not a separate legal entity",
                    "No perpetual succession",
                ],
                "best_for": "Traditional businesses, short-term ventures, family firms",
            })

    # Add foreign involvement note
    if has_foreign_involvement:
        for rec in recommendations:
            if rec["entity_type"] in ("private_limited", "llp"):
                rec["pros"].append("Allows foreign directors/partners (with FDI compliance)")
            if rec["entity_type"] == "partnership":
                rec["cons"].append("Foreign nationals face restrictions in partnership firms")

    return _build_response(recommendations)


def _build_response(recommendations: List[Dict[str, Any]]) -> dict:
    """Build the recommendation response."""
    if not recommendations:
        recommendations = [{
            "entity_type": "private_limited",
            "name": "Private Limited Company",
            "match_score": 80,
            "pros": ["Most versatile structure"],
            "cons": ["Higher compliance"],
            "best_for": "Most businesses",
        }]

    # Sort by match score descending
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "recommended": recommendations[0],
        "alternatives": recommendations[1:],
        "total_options": len(recommendations),
    }


# ---------------------------------------------------------------------------
# LLM Enhancement (optional)
# ---------------------------------------------------------------------------

def _get_llm_enhancement(
    decision_tree_result: dict,
    is_solo: bool,
    seeking_funding: bool,
    expected_revenue: str,
    is_nonprofit: bool,
    has_foreign_involvement: bool,
    is_professional_services: bool,
    business_description: str,
) -> Optional[Dict[str, Any]]:
    """
    Use LLM to generate personalized reasoning for the recommendation.
    Runs synchronously (called from sync context).
    Returns None if LLM is unavailable.
    """
    from src.services.llm_service import llm_service

    if llm_service.provider == "mock":
        # Return a mock LLM enhancement
        recommended = decision_tree_result.get("recommended", {})
        return {
            "reasoning": (
                f"Based on your business description ('{business_description}'), "
                f"a {recommended.get('name', 'Private Limited Company')} is the most suitable "
                f"structure. This entity type provides {', '.join(recommended.get('pros', [])[:2])}."
            ),
            "additional_considerations": [
                "Consider your 3-5 year growth plan when choosing an entity type.",
                "You can always convert from one entity type to another as your business evolves.",
                "Consult a CA or CS for tax implications specific to your industry.",
            ],
            "score_adjustment": 0,
        }

    system_prompt = (
        "You are an expert advisor on Indian business entity structures. "
        "Given a founder's situation and a recommended entity type, provide:\n"
        "1. A personalized 2-3 sentence reasoning for why this entity is best\n"
        "2. 2-3 additional considerations specific to their business\n"
        "3. A score adjustment (-5 to +5) if the business description suggests "
        "the recommendation should be more or less confident\n\n"
        "Respond in JSON with keys: reasoning, additional_considerations (list), score_adjustment (int)"
    )

    recommended = decision_tree_result.get("recommended", {})
    user_msg = (
        f"Business description: {business_description}\n"
        f"Recommended entity: {recommended.get('name', '')}\n"
        f"Solo founder: {is_solo}\n"
        f"Seeking funding: {seeking_funding}\n"
        f"Expected revenue: {expected_revenue}\n"
        f"Non-profit: {is_nonprofit}\n"
        f"Foreign involvement: {has_foreign_involvement}\n"
        f"Professional services: {is_professional_services}\n\n"
        f"Provide personalized reasoning for this recommendation."
    )

    try:
        loop = asyncio.new_event_loop()
        try:
            response = loop.run_until_complete(
                llm_service.chat(
                    system_prompt=system_prompt,
                    user_message=user_msg,
                    temperature=0.3,
                    max_tokens=512,
                )
            )
        finally:
            loop.close()

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(response[start:end])
            else:
                return None

        # Clamp score adjustment
        if "score_adjustment" in result:
            result["score_adjustment"] = max(-5, min(5, int(result["score_adjustment"])))

        return result

    except Exception as exc:
        logger.warning("LLM entity advisor enhancement failed: %s", exc)
        return None
