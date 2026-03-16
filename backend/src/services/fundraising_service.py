"""
Fundraising Service — generates term sheet templates, valuation calculators,
post-fundraise filing requirements, and manages funding rounds with
investor tracking, closing room, and share allotment.

Supports equity rounds, SAFE notes, and convertible notes.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from src.models.funding_round import (
    FundingRound, RoundInvestor, FundingRoundStatus, InstrumentType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Post-fundraise filing requirements
# ---------------------------------------------------------------------------

POST_FUNDRAISE_FILINGS = [
    {
        "form": "PAS-3",
        "title": "Return of Allotment",
        "deadline": "Within 15 days of allotment",
        "description": (
            "File return of allotment with ROC after issuing shares to investors. "
            "Must include details of allottees, shares allotted, and consideration."
        ),
        "fee": 200,
        "attachments": [
            "Board Resolution for allotment",
            "List of allottees (PAS-4)",
            "Valuation report (if shares issued at premium)",
        ],
    },
    {
        "form": "MGT-14",
        "title": "Filing of Board/Shareholder Resolutions",
        "deadline": "Within 30 days of passing the resolution",
        "description": (
            "File special resolutions passed for share allotment, "
            "increase in authorized capital, or alteration of AOA."
        ),
        "fee": 200,
        "attachments": [
            "Certified true copy of the resolution",
            "Explanatory statement under Section 102",
        ],
    },
    {
        "form": "SH-7",
        "title": "Notice of Increase in Share Capital",
        "deadline": "Within 30 days of increase in authorized capital",
        "description": (
            "If authorized capital needs to be increased to accommodate "
            "new shares, file SH-7 with ROC."
        ),
        "fee": "Based on increase in capital (Rs 200 - Rs 5,000+)",
        "attachments": [
            "Ordinary resolution for increase",
            "Altered MOA",
        ],
    },
    {
        "form": "FC-GPR",
        "title": "Foreign Currency - Gross Provisional Return",
        "deadline": "Within 30 days of allotment to foreign investor",
        "description": (
            "Mandatory filing with RBI if shares are allotted to a foreign "
            "investor (FDI). Filed on the FIRMS portal."
        ),
        "fee": "No government fee (filed on RBI portal)",
        "attachments": [
            "Board Resolution",
            "KYC of foreign investor",
            "FIRC (Foreign Inward Remittance Certificate)",
            "Valuation certificate from CA/Merchant Banker",
            "CS certificate",
        ],
        "applicable_for": "Foreign investment only",
    },
    {
        "form": "DIR-12",
        "title": "Changes in Directors",
        "deadline": "Within 30 days of change",
        "description": (
            "If investor nominees are appointed to the board, "
            "file DIR-12 for appointment of new directors."
        ),
        "fee": 200,
        "attachments": [
            "DIR-2 (Consent to act as Director)",
            "Board Resolution for appointment",
        ],
        "applicable_for": "If new directors are appointed as part of funding round",
    },
    {
        "form": "AOC-2",
        "title": "Related Party Transaction Disclosure",
        "deadline": "Within 30 days of board meeting",
        "description": (
            "If any transaction with the investor is a related party transaction, "
            "disclose via AOC-2."
        ),
        "fee": 200,
        "applicable_for": "If related party transactions exist",
    },
]


class FundraisingService:
    """Service for fundraising templates and calculations."""

    def generate_term_sheet(
        self,
        template_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate term sheet template.

        Types: equity, safe, convertible_note
        """
        if template_type == "equity":
            return self._generate_equity_term_sheet(details)
        elif template_type == "safe":
            return self._generate_safe_term_sheet(details)
        elif template_type == "convertible_note":
            return self._generate_convertible_note_term_sheet(details)
        else:
            return {"error": f"Unknown template type: {template_type}"}

    def calculate_valuation(
        self,
        method: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Basic valuation calculator.

        Methods: revenue_multiple, dcf_simplified
        """
        if method == "revenue_multiple":
            return self._valuation_revenue_multiple(inputs)
        elif method == "dcf_simplified":
            return self._valuation_dcf_simplified(inputs)
        else:
            return {"error": f"Unknown valuation method: {method}"}

    def get_post_fundraise_filings(self) -> List[Dict[str, Any]]:
        """List of filings needed after a fundraise."""
        return {
            "filings": POST_FUNDRAISE_FILINGS,
            "total_filings": len(POST_FUNDRAISE_FILINGS),
            "note": (
                "The exact filings required depend on the nature of the investment "
                "(domestic vs foreign, equity vs convertible, etc.). "
                "Consult a qualified CS/CA for your specific situation."
            ),
        }

    # ------------------------------------------------------------------
    # Term Sheet Templates
    # ------------------------------------------------------------------

    def _generate_equity_term_sheet(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate equity round term sheet template."""
        company_name = details.get("company_name", "[Company Name]")
        investor_name = details.get("investor_name", "[Investor Name]")
        investment_amount = details.get("investment_amount", 0)
        pre_money_valuation = details.get("pre_money_valuation", 0)
        post_money_valuation = pre_money_valuation + investment_amount
        equity_percentage = round(
            (investment_amount / post_money_valuation * 100), 2
        ) if post_money_valuation > 0 else 0

        return {
            "template_type": "equity",
            "title": "Term Sheet - Equity Investment",
            "status": "Non-Binding",
            "sections": {
                "1_parties": {
                    "title": "Parties",
                    "company": company_name,
                    "investor": investor_name,
                },
                "2_investment": {
                    "title": "Investment Terms",
                    "investment_amount": f"Rs {investment_amount:,}/-",
                    "pre_money_valuation": f"Rs {pre_money_valuation:,}/-",
                    "post_money_valuation": f"Rs {post_money_valuation:,}/-",
                    "equity_percentage": f"{equity_percentage}%",
                    "instrument": "Equity Shares (Compulsorily Convertible Preference Shares if FDI)",
                    "price_per_share": details.get("price_per_share", "To be determined based on valuation"),
                },
                "3_investor_rights": {
                    "title": "Investor Rights",
                    "items": [
                        "Board seat / Board observer right",
                        "Information rights (monthly MIS, quarterly financials)",
                        "Anti-dilution protection (broad-based weighted average)",
                        "Pro-rata participation rights in future rounds",
                        "Right of first refusal (ROFR) on share transfers",
                        "Tag-along rights",
                        "Drag-along rights (on majority investor consent)",
                    ],
                },
                "4_founder_obligations": {
                    "title": "Founder Obligations",
                    "items": [
                        f"Founders' shares subject to {details.get('vesting_period', '4-year')} vesting with 1-year cliff",
                        "Full-time commitment to the company",
                        "Non-compete for 2 years post-departure",
                        "Non-solicitation of employees for 1 year",
                        "IP assignment to the company",
                    ],
                },
                "5_conditions_precedent": {
                    "title": "Conditions Precedent to Closing",
                    "items": [
                        "Satisfactory due diligence",
                        "Execution of definitive agreements (SHA, SSA, Employment Agreements)",
                        "Board and shareholder approvals",
                        "No material adverse change",
                        "Legal opinion from company's counsel",
                    ],
                },
                "6_governance": {
                    "title": "Governance",
                    "board_composition": details.get(
                        "board_composition",
                        "3 directors: 2 founders + 1 investor nominee"
                    ),
                    "reserved_matters": [
                        "Change in business or MOA/AOA",
                        "Issue of new securities",
                        "Related party transactions above threshold",
                        "Annual budget approval",
                        "Appointment/removal of key personnel",
                    ],
                },
                "7_exit": {
                    "title": "Exit / Liquidity",
                    "items": [
                        "IPO target timeline: 5-7 years",
                        "Buyback right after 5 years if no liquidity event",
                        "Right to transfer shares to affiliates",
                    ],
                },
            },
            "metadata": {
                "generated_date": date.today().isoformat(),
                "disclaimer": (
                    "This is a template term sheet for informational purposes only. "
                    "It is non-binding and should be reviewed by legal counsel before use."
                ),
            },
        }

    def _generate_safe_term_sheet(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SAFE (Simple Agreement for Future Equity) term sheet."""
        company_name = details.get("company_name", "[Company Name]")
        investor_name = details.get("investor_name", "[Investor Name]")
        investment_amount = details.get("investment_amount", 0)
        valuation_cap = details.get("valuation_cap", 0)
        discount_rate = details.get("discount_rate", 20)

        return {
            "template_type": "safe",
            "title": "Term Sheet - SAFE (Simple Agreement for Future Equity)",
            "status": "Non-Binding",
            "sections": {
                "1_parties": {
                    "title": "Parties",
                    "company": company_name,
                    "investor": investor_name,
                },
                "2_investment": {
                    "title": "Investment Terms",
                    "investment_amount": f"Rs {investment_amount:,}/-",
                    "instrument": "SAFE Note (converts to equity on trigger event)",
                    "valuation_cap": f"Rs {valuation_cap:,}/-" if valuation_cap else "No cap",
                    "discount_rate": f"{discount_rate}%",
                },
                "3_conversion_triggers": {
                    "title": "Conversion Triggers",
                    "items": [
                        "Equity Financing: Converts at the lower of valuation cap or discount to round price",
                        "Liquidity Event: Converts at valuation cap",
                        "Dissolution: Investor receives investment amount back (priority over common stock)",
                    ],
                },
                "4_conversion_mechanics": {
                    "title": "Conversion Mechanics",
                    "content": (
                        f"On an equity financing round, the SAFE converts into equity at the lower of:\n"
                        f"(a) A price based on the valuation cap of Rs {valuation_cap:,}/-\n"
                        f"(b) A {discount_rate}% discount to the price paid by new investors\n\n"
                        f"The investor will receive the type of shares issued in the financing round."
                    ),
                },
                "5_most_favored_nation": {
                    "title": "Most Favored Nation (MFN)",
                    "content": (
                        "If the Company issues any subsequent SAFE notes with more favorable terms "
                        "(lower cap or higher discount), this SAFE will be amended to match."
                    ),
                },
                "6_pro_rata_rights": {
                    "title": "Pro-Rata Rights",
                    "content": (
                        "The investor has the right to participate pro-rata in the financing round "
                        "that triggers conversion of this SAFE."
                    ),
                },
            },
            "india_specific_notes": [
                "SAFE notes are not explicitly defined under Indian law. Structure as CCPS (Compulsorily Convertible Preference Shares) for legal validity.",
                "If investor is foreign, comply with FEMA/FDI regulations (FC-GPR filing).",
                "Ensure conversion terms comply with Companies Act, 2013 share issuance requirements.",
                "Stamp duty may apply on CCPS issuance.",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "disclaimer": (
                    "This template is adapted for Indian legal context. "
                    "SAFE notes should be structured as CCPS to ensure legal enforceability. "
                    "Consult legal counsel before use."
                ),
            },
        }

    def _generate_convertible_note_term_sheet(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate convertible note term sheet."""
        company_name = details.get("company_name", "[Company Name]")
        investor_name = details.get("investor_name", "[Investor Name]")
        investment_amount = details.get("investment_amount", 0)
        valuation_cap = details.get("valuation_cap", 0)
        discount_rate = details.get("discount_rate", 20)
        interest_rate = details.get("interest_rate", 8)
        maturity_months = details.get("maturity_months", 24)

        return {
            "template_type": "convertible_note",
            "title": "Term Sheet - Convertible Note",
            "status": "Non-Binding",
            "sections": {
                "1_parties": {
                    "title": "Parties",
                    "company": company_name,
                    "investor": investor_name,
                },
                "2_note_terms": {
                    "title": "Note Terms",
                    "principal_amount": f"Rs {investment_amount:,}/-",
                    "interest_rate": f"{interest_rate}% per annum (simple interest)",
                    "maturity": f"{maturity_months} months from issuance",
                    "valuation_cap": f"Rs {valuation_cap:,}/-" if valuation_cap else "No cap",
                    "discount_rate": f"{discount_rate}%",
                },
                "3_conversion": {
                    "title": "Conversion",
                    "automatic_conversion": (
                        "On a Qualified Financing (equity round raising at least "
                        f"Rs {investment_amount * 2:,}/-), the note automatically converts "
                        f"into equity at the lower of the valuation cap or "
                        f"{discount_rate}% discount to round price."
                    ),
                    "optional_conversion": (
                        "At maturity, the investor may elect to convert the outstanding "
                        "principal and accrued interest into equity at the valuation cap."
                    ),
                    "repayment": (
                        "If not converted by maturity, the investor may demand repayment "
                        "of principal plus accrued interest."
                    ),
                },
                "4_security": {
                    "title": "Security",
                    "content": "Unsecured obligation of the Company.",
                },
                "5_events_of_default": {
                    "title": "Events of Default",
                    "items": [
                        "Failure to pay principal or interest when due",
                        "Breach of representations or covenants",
                        "Insolvency or winding up proceedings",
                        "Material adverse change in the business",
                    ],
                },
            },
            "india_specific_notes": [
                "Convertible notes are governed by Companies Act, 2013 (Section 71 for debentures).",
                "Structure as Compulsorily Convertible Debentures (CCD) for regulatory compliance.",
                "For foreign investors, CCDs must comply with FEMA pricing guidelines.",
                "Maximum tenure for CCD: 10 years (as per RBI guidelines).",
                "Interest rate must comply with RBI ECB guidelines for foreign investors.",
                "File FC-GPR with RBI within 30 days of issuance to foreign investors.",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "disclaimer": (
                    "This template is adapted for Indian legal context. "
                    "Convertible notes should be structured as CCDs for legal enforceability. "
                    "Consult legal counsel before use."
                ),
            },
        }

    # ------------------------------------------------------------------
    # Funding Round CRUD
    # ------------------------------------------------------------------

    def create_round(
        self, db: Session, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new funding round."""
        instrument = InstrumentType.EQUITY
        if data.get("instrument_type"):
            instrument = InstrumentType(data["instrument_type"])

        pre_money = data.get("pre_money_valuation")
        target = data.get("target_amount")
        post_money = None
        price_per_share = data.get("price_per_share")

        if pre_money and target:
            post_money = pre_money + target

        round_obj = FundingRound(
            company_id=company_id,
            round_name=data["round_name"],
            instrument_type=instrument,
            pre_money_valuation=pre_money,
            post_money_valuation=post_money,
            price_per_share=price_per_share,
            target_amount=target,
            valuation_cap=data.get("valuation_cap"),
            discount_rate=data.get("discount_rate"),
            interest_rate=data.get("interest_rate"),
            maturity_months=data.get("maturity_months"),
            esop_pool_expansion_pct=data.get("esop_pool_expansion_pct", 0.0),
            notes=data.get("notes"),
        )
        db.add(round_obj)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(round_obj)
        return self._serialize_round(round_obj)

    def get_round(
        self, db: Session, round_id: int, company_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get round with investors and documents."""
        round_obj = (
            db.query(FundingRound)
            .filter(
                FundingRound.id == round_id,
                FundingRound.company_id == company_id,
            )
            .first()
        )
        if not round_obj:
            return None

        investors = (
            db.query(RoundInvestor)
            .filter(RoundInvestor.funding_round_id == round_id)
            .all()
        )

        result = self._serialize_round(round_obj)
        result["investors"] = [self._serialize_investor(inv) for inv in investors]
        return result

    def list_rounds(
        self, db: Session, company_id: int
    ) -> List[Dict[str, Any]]:
        """List all rounds for a company."""
        rounds = (
            db.query(FundingRound)
            .filter(FundingRound.company_id == company_id)
            .order_by(FundingRound.created_at.desc())
            .all()
        )
        result = []
        for r in rounds:
            data = self._serialize_round(r)
            investor_count = (
                db.query(RoundInvestor)
                .filter(RoundInvestor.funding_round_id == r.id)
                .count()
            )
            data["investor_count"] = investor_count
            result.append(data)
        return result

    def update_round(
        self, db: Session, round_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update round details and recalculate valuations."""
        round_obj = (
            db.query(FundingRound)
            .filter(
                FundingRound.id == round_id,
                FundingRound.company_id == company_id,
            )
            .first()
        )
        if not round_obj:
            return {"error": "Round not found"}

        for field in [
            "round_name", "pre_money_valuation", "post_money_valuation",
            "price_per_share", "target_amount", "valuation_cap",
            "discount_rate", "interest_rate", "maturity_months",
            "esop_pool_expansion_pct", "notes",
        ]:
            if field in data and data[field] is not None:
                setattr(round_obj, field, data[field])

        if data.get("instrument_type"):
            round_obj.instrument_type = InstrumentType(data["instrument_type"])
        if data.get("status"):
            round_obj.status = FundingRoundStatus(data["status"])

        # Recalculate post-money if pre-money changed
        if round_obj.pre_money_valuation and round_obj.amount_raised:
            round_obj.post_money_valuation = (
                round_obj.pre_money_valuation + round_obj.amount_raised
            )

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(round_obj)
        return self._serialize_round(round_obj)

    # ------------------------------------------------------------------
    # Investor Management
    # ------------------------------------------------------------------

    def add_investor(
        self, db: Session, round_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add an investor to a round."""
        round_obj = (
            db.query(FundingRound)
            .filter(
                FundingRound.id == round_id,
                FundingRound.company_id == company_id,
            )
            .first()
        )
        if not round_obj:
            return {"error": "Round not found"}

        investor = RoundInvestor(
            funding_round_id=round_id,
            company_id=company_id,
            investor_name=data["investor_name"],
            investor_email=data.get("investor_email"),
            investor_type=data.get("investor_type", "angel"),
            investor_entity=data.get("investor_entity"),
            investment_amount=data["investment_amount"],
            share_type=data.get("share_type", "equity"),
            notes=data.get("notes"),
        )
        db.add(investor)

        # Update amount raised
        round_obj.amount_raised = (round_obj.amount_raised or 0) + data["investment_amount"]
        if round_obj.pre_money_valuation:
            round_obj.post_money_valuation = (
                round_obj.pre_money_valuation + round_obj.amount_raised
            )

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(investor)
        return self._serialize_investor(investor)

    def update_investor(
        self, db: Session, investor_id: int, company_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update investor details and status flags."""
        investor = (
            db.query(RoundInvestor)
            .filter(
                RoundInvestor.id == investor_id,
                RoundInvestor.company_id == company_id,
            )
            .first()
        )
        if not investor:
            return {"error": "Investor not found"}

        old_amount = investor.investment_amount

        for field in [
            "investor_name", "investor_email", "investor_type",
            "investor_entity", "investment_amount", "share_type",
            "committed", "funds_received", "documents_signed",
            "shares_issued", "notes",
        ]:
            if field in data and data[field] is not None:
                setattr(investor, field, data[field])

        # Update amount_raised if investment_amount changed
        if "investment_amount" in data and data["investment_amount"] is not None:
            round_obj = db.query(FundingRound).filter(
                FundingRound.id == investor.funding_round_id
            ).first()
            if round_obj:
                round_obj.amount_raised = (
                    (round_obj.amount_raised or 0) - old_amount + data["investment_amount"]
                )
                if round_obj.pre_money_valuation:
                    round_obj.post_money_valuation = (
                        round_obj.pre_money_valuation + round_obj.amount_raised
                    )

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(investor)
        return self._serialize_investor(investor)

    def remove_investor(
        self, db: Session, investor_id: int, company_id: int
    ) -> Dict[str, Any]:
        """Remove an investor from a round."""
        investor = (
            db.query(RoundInvestor)
            .filter(
                RoundInvestor.id == investor_id,
                RoundInvestor.company_id == company_id,
            )
            .first()
        )
        if not investor:
            return {"error": "Investor not found"}

        round_obj = db.query(FundingRound).filter(
            FundingRound.id == investor.funding_round_id
        ).first()
        if round_obj:
            round_obj.amount_raised = max(
                0, (round_obj.amount_raised or 0) - investor.investment_amount
            )
            if round_obj.pre_money_valuation:
                round_obj.post_money_valuation = (
                    round_obj.pre_money_valuation + round_obj.amount_raised
                )

        db.delete(investor)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        return {"message": "Investor removed"}

    # ------------------------------------------------------------------
    # Document Linking & Closing Room
    # ------------------------------------------------------------------

    def link_document(
        self, db: Session, round_id: int, company_id: int,
        doc_type: str, document_id: int
    ) -> Dict[str, Any]:
        """Link a legal document (term_sheet/sha/ssa) to a round."""
        round_obj = (
            db.query(FundingRound)
            .filter(
                FundingRound.id == round_id,
                FundingRound.company_id == company_id,
            )
            .first()
        )
        if not round_obj:
            return {"error": "Round not found"}

        if doc_type == "term_sheet":
            round_obj.term_sheet_document_id = document_id
        elif doc_type == "sha":
            round_obj.sha_document_id = document_id
        elif doc_type == "ssa":
            round_obj.ssa_document_id = document_id
        else:
            return {"error": f"Unknown document type: {doc_type}"}

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        return {"message": f"{doc_type} linked successfully", "document_id": document_id}

    def initiate_closing(
        self, db: Session, round_id: int, company_id: int,
        user_id: int, documents_to_sign: List[str]
    ) -> Dict[str, Any]:
        """Start the closing room — send SHA/SSA for e-sign."""
        from src.services.esign_service import esign_service
        from src.schemas.esign import SignatureRequestCreate, SignatoryCreate

        round_obj = (
            db.query(FundingRound)
            .filter(
                FundingRound.id == round_id,
                FundingRound.company_id == company_id,
            )
            .first()
        )
        if not round_obj:
            return {"error": "Round not found"}

        investors = (
            db.query(RoundInvestor)
            .filter(
                RoundInvestor.funding_round_id == round_id,
                RoundInvestor.committed == True,
            )
            .all()
        )

        if not investors:
            return {"error": "No committed investors found"}

        results = {}

        for doc_type in documents_to_sign:
            doc_id = None
            if doc_type == "sha":
                doc_id = round_obj.sha_document_id
            elif doc_type == "ssa":
                doc_id = round_obj.ssa_document_id

            if not doc_id:
                results[doc_type] = {"status": "skipped", "reason": "No document linked"}
                continue

            signatories = []
            for idx, inv in enumerate(investors):
                if inv.investor_email:
                    signatories.append(
                        SignatoryCreate(
                            name=inv.investor_name,
                            email=inv.investor_email,
                            designation=inv.investor_type or "Investor",
                            signing_order=idx + 1,
                        )
                    )

            if not signatories:
                results[doc_type] = {"status": "skipped", "reason": "No signatories with email"}
                continue

            sig_data = SignatureRequestCreate(
                legal_document_id=doc_id,
                title=f"{round_obj.round_name} - {doc_type.upper()}",
                message=f"Please review and sign the {doc_type.upper()} for {round_obj.round_name}.",
                signing_order="parallel",
                expires_in_days=30,
                signatories=signatories,
            )

            sig_request = esign_service.create_signature_request(
                db=db, user_id=user_id, data=sig_data
            )

            if doc_type == "sha":
                round_obj.sha_signature_request_id = sig_request.id
            elif doc_type == "ssa":
                round_obj.ssa_signature_request_id = sig_request.id

            results[doc_type] = {
                "status": "sent",
                "signature_request_id": sig_request.id,
            }

        round_obj.status = FundingRoundStatus.CLOSING

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "message": "Closing room initiated",
            "round_id": round_id,
            "documents": results,
        }

    def get_closing_room_status(
        self, db: Session, round_id: int, company_id: int
    ) -> Dict[str, Any]:
        """Check signing status for the closing room."""
        from src.models.esign import SignatureRequest, Signatory

        round_obj = (
            db.query(FundingRound)
            .filter(
                FundingRound.id == round_id,
                FundingRound.company_id == company_id,
            )
            .first()
        )
        if not round_obj:
            return {"error": "Round not found"}

        documents = {}

        for doc_type, sig_req_id in [
            ("sha", round_obj.sha_signature_request_id),
            ("ssa", round_obj.ssa_signature_request_id),
        ]:
            if not sig_req_id:
                documents[doc_type] = {"status": "not_initiated"}
                continue

            sig_req = db.query(SignatureRequest).filter(
                SignatureRequest.id == sig_req_id
            ).first()

            if not sig_req:
                documents[doc_type] = {"status": "not_found"}
                continue

            signatories = db.query(Signatory).filter(
                Signatory.signature_request_id == sig_req_id
            ).all()

            documents[doc_type] = {
                "status": sig_req.status.value if hasattr(sig_req.status, 'value') else str(sig_req.status),
                "signature_request_id": sig_req_id,
                "signatories": [
                    {
                        "name": s.name,
                        "email": s.email,
                        "status": s.status.value if hasattr(s.status, 'value') else str(s.status),
                        "signed_at": s.signed_at.isoformat() if s.signed_at else None,
                    }
                    for s in signatories
                ],
            }

        return {
            "round_id": round_id,
            "round_name": round_obj.round_name,
            "round_status": round_obj.status.value,
            "documents": documents,
        }

    # ------------------------------------------------------------------
    # Share Allotment (Post-Close)
    # ------------------------------------------------------------------

    def complete_allotment(
        self, db: Session, round_id: int, company_id: int,
        investor_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Allot shares to investors after closing.
        Creates Shareholder records via cap_table_service.
        """
        from src.services.cap_table_service import cap_table_service, AllotmentEntry

        round_obj = (
            db.query(FundingRound)
            .filter(
                FundingRound.id == round_id,
                FundingRound.company_id == company_id,
            )
            .first()
        )
        if not round_obj:
            return {"error": "Round not found"}

        query = db.query(RoundInvestor).filter(
            RoundInvestor.funding_round_id == round_id,
            RoundInvestor.shares_issued == False,
        )
        if investor_ids:
            query = query.filter(RoundInvestor.id.in_(investor_ids))

        investors = query.all()
        if not investors:
            return {"error": "No investors eligible for allotment"}

        price_per_share = round_obj.price_per_share or 10.0

        entries = []
        for inv in investors:
            shares = int(inv.investment_amount / price_per_share) if price_per_share > 0 else 0
            if shares <= 0:
                continue

            inv.shares_allotted = shares
            entries.append(AllotmentEntry(
                name=inv.investor_name,
                shares=shares,
                share_type=inv.share_type or "equity",
                face_value=10.0,
                paid_up_value=price_per_share,
                price_per_share=price_per_share,
                email=inv.investor_email,
                is_promoter=False,
            ))

        if not entries:
            return {"error": "No valid allotments to make (check price_per_share)"}

        allotment_result = cap_table_service.record_allotment(
            db, company_id, entries
        )

        # Mark investors as shares issued and link shareholder IDs
        for inv in investors:
            if inv.shares_allotted and inv.shares_allotted > 0:
                inv.shares_issued = True

        round_obj.allotment_completed = True
        round_obj.allotment_date = datetime.now(timezone.utc)
        round_obj.status = FundingRoundStatus.CLOSED

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "message": f"Shares allotted to {len(entries)} investor(s)",
            "round_id": round_id,
            "allotment": allotment_result,
            "post_fundraise_filings": POST_FUNDRAISE_FILINGS,
        }

    # ------------------------------------------------------------------
    # Serializers
    # ------------------------------------------------------------------

    def _serialize_round(self, r: FundingRound) -> Dict[str, Any]:
        """Serialize a FundingRound to dict."""
        return {
            "id": r.id,
            "company_id": r.company_id,
            "round_name": r.round_name,
            "instrument_type": r.instrument_type.value if r.instrument_type else "equity",
            "pre_money_valuation": r.pre_money_valuation,
            "post_money_valuation": r.post_money_valuation,
            "price_per_share": r.price_per_share,
            "target_amount": r.target_amount,
            "amount_raised": r.amount_raised or 0,
            "valuation_cap": r.valuation_cap,
            "discount_rate": r.discount_rate,
            "interest_rate": r.interest_rate,
            "maturity_months": r.maturity_months,
            "esop_pool_expansion_pct": r.esop_pool_expansion_pct or 0,
            "status": r.status.value if r.status else "draft",
            "term_sheet_document_id": r.term_sheet_document_id,
            "sha_document_id": r.sha_document_id,
            "ssa_document_id": r.ssa_document_id,
            "allotment_date": r.allotment_date.isoformat() if r.allotment_date else None,
            "allotment_completed": r.allotment_completed or False,
            "notes": r.notes,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }

    def _serialize_investor(self, inv: RoundInvestor) -> Dict[str, Any]:
        """Serialize a RoundInvestor to dict."""
        return {
            "id": inv.id,
            "funding_round_id": inv.funding_round_id,
            "company_id": inv.company_id,
            "investor_name": inv.investor_name,
            "investor_email": inv.investor_email,
            "investor_type": inv.investor_type,
            "investor_entity": inv.investor_entity,
            "investment_amount": inv.investment_amount,
            "shares_allotted": inv.shares_allotted or 0,
            "share_type": inv.share_type,
            "committed": inv.committed or False,
            "funds_received": inv.funds_received or False,
            "documents_signed": inv.documents_signed or False,
            "shares_issued": inv.shares_issued or False,
            "shareholder_id": inv.shareholder_id,
            "notes": inv.notes,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
        }

    # ------------------------------------------------------------------
    # Valuation Calculators
    # ------------------------------------------------------------------

    def _valuation_revenue_multiple(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simple revenue multiple valuation."""
        annual_revenue = inputs.get("annual_revenue", 0)
        industry = inputs.get("industry", "general")
        growth_rate = inputs.get("growth_rate", 0)  # Annual growth rate in %

        # Industry-wise typical revenue multiples for Indian startups
        industry_multiples = {
            "saas": {"low": 5, "mid": 10, "high": 20},
            "fintech": {"low": 4, "mid": 8, "high": 15},
            "ecommerce": {"low": 1, "mid": 3, "high": 6},
            "edtech": {"low": 3, "mid": 6, "high": 12},
            "healthtech": {"low": 3, "mid": 7, "high": 14},
            "d2c": {"low": 1.5, "mid": 3, "high": 5},
            "b2b": {"low": 3, "mid": 6, "high": 10},
            "marketplace": {"low": 2, "mid": 5, "high": 10},
            "general": {"low": 2, "mid": 4, "high": 8},
        }

        multiples = industry_multiples.get(industry, industry_multiples["general"])

        # Adjust multiple based on growth rate
        growth_premium = 1.0
        if growth_rate > 100:
            growth_premium = 1.5
        elif growth_rate > 50:
            growth_premium = 1.25
        elif growth_rate > 25:
            growth_premium = 1.1

        adjusted_multiples = {
            k: round(v * growth_premium, 1) for k, v in multiples.items()
        }

        valuations = {
            k: int(annual_revenue * v) for k, v in adjusted_multiples.items()
        }

        return {
            "method": "revenue_multiple",
            "inputs": {
                "annual_revenue": annual_revenue,
                "industry": industry,
                "growth_rate": f"{growth_rate}%",
            },
            "multiples": adjusted_multiples,
            "valuations": {
                "conservative": f"Rs {valuations['low']:,}/-",
                "moderate": f"Rs {valuations['mid']:,}/-",
                "aggressive": f"Rs {valuations['high']:,}/-",
            },
            "raw_valuations": valuations,
            "note": (
                "Revenue multiples are indicative and vary based on profitability, "
                "market size, competitive moat, and current market conditions. "
                "Actual valuation is negotiated between founders and investors."
            ),
        }

    def _valuation_dcf_simplified(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified DCF (Discounted Cash Flow) valuation."""
        current_revenue = inputs.get("current_revenue", 0)
        growth_rates = inputs.get("growth_rates", [50, 40, 30, 25, 20])  # 5 years
        profit_margin = inputs.get("profit_margin", 15)  # %
        discount_rate = inputs.get("discount_rate", 25)  # % (typical for startups)
        terminal_multiple = inputs.get("terminal_multiple", 5)

        # Project cash flows for 5 years
        projected_revenues = []
        projected_cash_flows = []
        revenue = current_revenue

        for i, growth in enumerate(growth_rates[:5]):
            revenue = revenue * (1 + growth / 100)
            cash_flow = revenue * (profit_margin / 100)
            projected_revenues.append(int(revenue))
            projected_cash_flows.append(int(cash_flow))

        # Discount cash flows
        discounted_cash_flows = []
        for i, cf in enumerate(projected_cash_flows):
            dcf = cf / ((1 + discount_rate / 100) ** (i + 1))
            discounted_cash_flows.append(int(dcf))

        # Terminal value
        terminal_value = projected_cash_flows[-1] * terminal_multiple if projected_cash_flows else 0
        discounted_terminal = int(
            terminal_value / ((1 + discount_rate / 100) ** len(projected_cash_flows))
        )

        # Enterprise value
        enterprise_value = sum(discounted_cash_flows) + discounted_terminal

        return {
            "method": "dcf_simplified",
            "inputs": {
                "current_revenue": current_revenue,
                "growth_rates": growth_rates[:5],
                "profit_margin": f"{profit_margin}%",
                "discount_rate": f"{discount_rate}%",
                "terminal_multiple": f"{terminal_multiple}x",
            },
            "projections": [
                {
                    "year": i + 1,
                    "revenue": projected_revenues[i],
                    "cash_flow": projected_cash_flows[i],
                    "discounted_cash_flow": discounted_cash_flows[i],
                }
                for i in range(len(projected_revenues))
            ],
            "terminal_value": terminal_value,
            "discounted_terminal_value": discounted_terminal,
            "enterprise_value": enterprise_value,
            "enterprise_value_display": f"Rs {enterprise_value:,}/-",
            "note": (
                "This is a simplified DCF model for indicative purposes only. "
                "Actual DCF valuations require detailed financial projections, "
                "market analysis, and should be performed by a qualified valuation expert. "
                "A registered valuer's report is required for share allotment at premium."
            ),
        }


    # ------------------------------------------------------------------
    # Convertible Instrument Conversion
    # ------------------------------------------------------------------

    def preview_conversion(
        self,
        db: Session,
        company_id: int,
        round_id: int,
        trigger_round_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Preview SAFE/CCD/Note → equity conversion without persisting.

        Args:
            company_id: The company ID
            round_id: The convertible round being converted
            trigger_round_id: Optional equity round that triggers conversion
        """
        from src.models.shareholder import Shareholder

        conv_round = (
            db.query(FundingRound)
            .filter(FundingRound.id == round_id, FundingRound.company_id == company_id)
            .first()
        )
        if not conv_round:
            return {"error": "Convertible round not found"}

        if conv_round.instrument_type not in (
            InstrumentType.SAFE, InstrumentType.CCD, InstrumentType.CONVERTIBLE_NOTE
        ):
            return {"error": "Round is not a convertible instrument"}

        # Get trigger round price (if any)
        trigger_price = None
        if trigger_round_id:
            trigger_round = (
                db.query(FundingRound)
                .filter(FundingRound.id == trigger_round_id, FundingRound.company_id == company_id)
                .first()
            )
            if trigger_round and trigger_round.price_per_share:
                trigger_price = trigger_round.price_per_share

        # Get total shares for cap-price calc
        total_shares_result = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )
        total_shares = sum(s.shares for s in total_shares_result) if total_shares_result else 10000

        investors = (
            db.query(RoundInvestor)
            .filter(
                RoundInvestor.funding_round_id == round_id,
                RoundInvestor.converted == False,
            )
            .all()
        )

        previews = []
        for inv in investors:
            result = self._calculate_conversion(
                conv_round, inv, trigger_price, total_shares
            )
            previews.append({
                "investor_id": inv.id,
                "investor_name": inv.investor_name,
                "principal": inv.investment_amount,
                **result,
            })

        return {
            "round_name": conv_round.round_name,
            "instrument_type": conv_round.instrument_type.value,
            "valuation_cap": conv_round.valuation_cap,
            "discount_rate": conv_round.discount_rate,
            "trigger_price_per_share": trigger_price,
            "total_existing_shares": total_shares,
            "conversions": previews,
        }

    def convert_instrument(
        self,
        db: Session,
        company_id: int,
        round_id: int,
        trigger_round_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute SAFE/CCD/Note → equity conversion.

        Creates ConversionEvent records, adds shareholders to cap table,
        and marks investors as converted.
        """
        from src.models.conversion_event import ConversionEvent
        from src.models.shareholder import Shareholder
        from src.services.cap_table_service import cap_table_service, ShareholderEntry

        conv_round = (
            db.query(FundingRound)
            .filter(FundingRound.id == round_id, FundingRound.company_id == company_id)
            .first()
        )
        if not conv_round:
            return {"error": "Convertible round not found"}

        if conv_round.instrument_type not in (
            InstrumentType.SAFE, InstrumentType.CCD, InstrumentType.CONVERTIBLE_NOTE
        ):
            return {"error": "Round is not a convertible instrument"}

        trigger_price = None
        if trigger_round_id:
            trigger_round = (
                db.query(FundingRound)
                .filter(FundingRound.id == trigger_round_id, FundingRound.company_id == company_id)
                .first()
            )
            if trigger_round and trigger_round.price_per_share:
                trigger_price = trigger_round.price_per_share

        total_shares_result = (
            db.query(Shareholder)
            .filter(Shareholder.company_id == company_id)
            .all()
        )
        total_shares = sum(s.shares for s in total_shares_result) if total_shares_result else 10000

        investors = (
            db.query(RoundInvestor)
            .filter(
                RoundInvestor.funding_round_id == round_id,
                RoundInvestor.converted == False,
            )
            .all()
        )

        if not investors:
            return {"error": "No unconverted investors in this round"}

        converted = []
        for inv in investors:
            calc = self._calculate_conversion(conv_round, inv, trigger_price, total_shares)

            # Create conversion event
            event = ConversionEvent(
                funding_round_id=round_id,
                company_id=company_id,
                trigger_round_id=trigger_round_id,
                conversion_price=calc["conversion_price"],
                conversion_method=calc["conversion_method"],
                interest_accrued=calc["interest_accrued"],
                principal_amount=inv.investment_amount,
                total_conversion_amount=calc["total_amount"],
                shares_issued=calc["shares_issued"],
                price_per_share_used=calc["conversion_price"],
            )
            db.add(event)
            db.flush()

            # Add as shareholder
            entry = ShareholderEntry(
                name=inv.investor_name,
                shares=calc["shares_issued"],
                percentage=0.0,  # Will be recalculated
                email=inv.investor_email,
                is_promoter=False,
            )
            cap_table_service.add_shareholder(db, company_id, entry)

            # Mark investor as converted
            inv.converted = True
            inv.conversion_event_id = event.id
            inv.shares_issued = True
            inv.shares_allotted = calc["shares_issued"]

            converted.append({
                "investor_name": inv.investor_name,
                "conversion_event_id": event.id,
                "shares_issued": calc["shares_issued"],
                "conversion_price": calc["conversion_price"],
                "conversion_method": calc["conversion_method"],
            })

        db.commit()
        return {"converted_count": len(converted), "conversions": converted}

    def _calculate_conversion(
        self,
        conv_round: FundingRound,
        investor: RoundInvestor,
        trigger_price: Optional[float],
        total_shares: int,
    ) -> Dict[str, Any]:
        """Calculate conversion price and shares for a single investor."""
        principal = investor.investment_amount
        interest_accrued = 0.0

        # Interest accrual for CCD/Notes
        if conv_round.instrument_type in (InstrumentType.CCD, InstrumentType.CONVERTIBLE_NOTE):
            rate = conv_round.interest_rate or 0
            months = conv_round.maturity_months or 12
            interest_accrued = principal * (rate / 100) * (months / 12)

        total_amount = principal + interest_accrued

        # Calculate possible conversion prices
        prices = {}

        if conv_round.valuation_cap and total_shares > 0:
            prices["valuation_cap"] = conv_round.valuation_cap / total_shares

        if conv_round.discount_rate and trigger_price:
            prices["discount"] = trigger_price * (1 - conv_round.discount_rate / 100)

        if trigger_price:
            prices["trigger_price"] = trigger_price

        # Use lowest price (most favorable to investor)
        if prices:
            best_method = min(prices, key=prices.get)
            conversion_price = prices[best_method]
        else:
            # Fallback: use face value
            best_method = "face_value"
            conversion_price = 10.0

        shares_issued = int(total_amount / conversion_price) if conversion_price > 0 else 0

        return {
            "conversion_price": round(conversion_price, 2),
            "conversion_method": best_method,
            "interest_accrued": round(interest_accrued, 2),
            "total_amount": round(total_amount, 2),
            "shares_issued": shares_issued,
            "all_prices": {k: round(v, 2) for k, v in prices.items()},
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
fundraising_service = FundraisingService()
