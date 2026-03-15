"""Founder Education Service — structured learning journey for first-time founders.

Provides stage-by-stage educational content with:
- Deep explanations of each stage of company building
- Why each legal document matters (with real-world scenarios)
- Contextual links between templates ("after X, do Y")
- Common founder mistakes and how to avoid them
- India-specific legal requirements and deadlines
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class FounderEducationService:
    """Provides structured educational content for founders."""

    def get_learning_path(self) -> Dict[str, Any]:
        """Return the complete founder learning journey."""
        return {
            "title": "Founder's Legal & Compliance Journey",
            "subtitle": "Everything you need to know — from incorporation to fundraising",
            "stages": self._build_stages(),
            "quick_tips": self._build_quick_tips(),
        }

    def get_stage(self, stage_id: str) -> Dict[str, Any]:
        """Return a specific stage with full content."""
        stages = {s["id"]: s for s in self._build_stages()}
        return stages.get(stage_id, {"error": "Stage not found"})

    def get_template_context(self, template_type: str) -> Dict[str, Any]:
        """Return educational context for a specific template — why it matters,
        when to use it, what comes before/after."""
        contexts = self._build_template_contexts()
        return contexts.get(template_type, {"error": "Template context not found"})

    def get_stage_for_template(self, template_type: str) -> Dict[str, Any]:
        """Return which stage a template belongs to and its position in the journey."""
        for stage in self._build_stages():
            for doc in stage.get("documents", []):
                if doc["template_type"] == template_type:
                    return {
                        "stage_id": stage["id"],
                        "stage_title": stage["title"],
                        "stage_number": stage["stage_number"],
                        "position_in_stage": next(
                            (i for i, d in enumerate(stage["documents"]) if d["template_type"] == template_type), 0
                        ) + 1,
                    }
        return {"error": "Template not found in any stage"}

    # ------------------------------------------------------------------
    # Stage definitions
    # ------------------------------------------------------------------

    def _build_stages(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "incorporation",
                "stage_number": 1,
                "title": "Incorporation & Setup",
                "icon": "building",
                "description": "Get your company legally registered and set up the foundation.",
                "why_it_matters": (
                    "Incorporation is the legal birth of your company. Without it, you cannot open a business "
                    "bank account, raise funding, hire employees formally, or enter into enforceable contracts "
                    "as a company. In India, most startups incorporate as a Private Limited Company under the "
                    "Companies Act 2013 because it offers limited liability protection, allows foreign investment "
                    "(critical for VC funding), and is the structure investors prefer.\n\n"
                    "The incorporation process involves: (1) obtaining Digital Signature Certificates (DSC) for "
                    "directors, (2) reserving a company name via RUN (Reserve Unique Name) on the MCA portal, "
                    "(3) filing SPICe+ form with MoA and AoA, and (4) receiving the Certificate of Incorporation "
                    "with CIN, PAN, and TAN.\n\n"
                    "Common mistake: Many founders delay incorporation while building their product. This is risky "
                    "because without a legal entity, IP ownership is ambiguous, co-founder disputes have no legal "
                    "framework, and early employees/contractors have no enforceable agreements."
                ),
                "key_deadlines": [
                    "INC-20A: Declaration of commencement of business — within 180 days of incorporation",
                    "First Board Meeting: Within 30 days of incorporation",
                    "Appointment of Auditor: Within 30 days of incorporation (ADT-1 within 15 days)",
                    "Open Bank Account: Immediately after receiving CIN",
                    "GST Registration: If turnover exceeds Rs 40 Lakhs (Rs 20 Lakhs for services)",
                ],
                "documents": [
                    {
                        "template_type": "board_resolution",
                        "name": "Board Resolution",
                        "why_needed": (
                            "Your very first corporate act after incorporation. You need board resolutions to "
                            "open a bank account, appoint an auditor, adopt the company seal, and authorize "
                            "directors to sign on behalf of the company. Without these resolutions, banks will "
                            "refuse to open your account."
                        ),
                        "when_to_create": "Immediately after incorporation — at your first board meeting",
                        "priority": "critical",
                    },
                ],
                "next_stage": "co_founder",
                "estimated_timeline": "1-3 weeks",
            },
            {
                "id": "co_founder",
                "stage_number": 2,
                "title": "Co-Founder Alignment",
                "icon": "handshake",
                "description": "Formalize the relationship between co-founders before building together.",
                "why_it_matters": (
                    "Co-founder disputes are the #1 reason startups fail in the early stages. A verbal agreement "
                    "about 'splitting equity 50-50' means nothing legally. You need a written Founder Agreement "
                    "that covers equity splits, vesting schedules, roles, IP assignment, and what happens if "
                    "someone leaves.\n\n"
                    "In India, equity without vesting is especially dangerous. If a co-founder gets 40% equity "
                    "on day one and leaves after 3 months, they walk away with 40% of your company having "
                    "contributed almost nothing. A 4-year vesting schedule with 1-year cliff is the industry "
                    "standard that protects everyone.\n\n"
                    "Real scenario: Two founders start with 50-50 split. One leaves after 6 months. Without a "
                    "vesting clause, the departed founder still owns 50% and can block major decisions, refuse "
                    "to sign investor documents, or demand a buyout at inflated prices. A Founder Agreement with "
                    "vesting would have limited their equity to what they earned."
                ),
                "key_deadlines": [
                    "Execute before any significant work begins",
                    "Must be in place before accepting any external investment",
                    "IP assignment clause is retroactive — covers work done before signing",
                ],
                "documents": [
                    {
                        "template_type": "founder_agreement",
                        "name": "Founder / Co-Founder Agreement",
                        "why_needed": (
                            "The most important document for any startup with multiple founders. It defines "
                            "who owns what, how decisions are made, what happens when someone leaves, and "
                            "ensures all IP belongs to the company (not individual founders)."
                        ),
                        "when_to_create": "Before or immediately after incorporation",
                        "priority": "critical",
                    },
                    {
                        "template_type": "nda",
                        "name": "Non-Disclosure Agreement",
                        "why_needed": (
                            "Protect your idea and business plans when discussing with potential co-founders, "
                            "advisors, or early team members. While NDAs are not always enforceable for 'ideas', "
                            "they establish a legal framework and signal professionalism."
                        ),
                        "when_to_create": "Before sharing confidential information with anyone",
                        "priority": "recommended",
                    },
                    {
                        "template_type": "ip_assignment",
                        "name": "IP Assignment Agreement",
                        "why_needed": (
                            "Ensures any code, designs, content, or inventions created by founders are legally "
                            "owned by the company, not by individual founders. Under Indian Copyright Act Section 17, "
                            "the default owner of a work is the author — not the company. You need explicit "
                            "assignment to transfer IP ownership."
                        ),
                        "when_to_create": "At the time of signing the Founder Agreement",
                        "priority": "critical",
                    },
                ],
                "next_stage": "team_building",
            },
            {
                "id": "team_building",
                "stage_number": 3,
                "title": "Hiring & Team Building",
                "icon": "users",
                "description": "Bring on employees, contractors, and advisors with proper legal agreements.",
                "why_it_matters": (
                    "Every person who works for your company needs a proper agreement. This protects both "
                    "parties and ensures IP ownership, confidentiality, and clear terms. In India, employment "
                    "law varies by state, and getting it wrong can lead to labour court disputes, PF/ESI "
                    "penalties, and even criminal liability for directors.\n\n"
                    "Key distinctions: Employees get PF, ESI, gratuity, and are governed by labour laws. "
                    "Contractors/freelancers are independent and you pay them invoices + TDS. Misclassifying "
                    "employees as contractors to avoid PF/ESI is a common mistake that can result in back-payment "
                    "demands and penalties from EPFO."
                ),
                "key_deadlines": [
                    "PF registration: Mandatory when you have 20+ employees",
                    "ESI registration: Mandatory for 10+ employees (salary up to Rs 21,000/month)",
                    "TDS on salaries: Section 192 — deposit by 7th of next month",
                    "TDS on contractor payments: Section 194J — 10% TDS if payment exceeds Rs 30,000/year",
                    "Shops & Establishments Act registration: Within 30 days of commencing business (state-specific)",
                ],
                "documents": [
                    {
                        "template_type": "offer_letter",
                        "name": "Offer Letter",
                        "why_needed": (
                            "The first formal document a potential employee receives. It outlines compensation, "
                            "designation, joining date, and key terms. While not as detailed as an employment "
                            "agreement, it serves as the basis for the hire."
                        ),
                        "when_to_create": "After selecting a candidate, before they resign from current job",
                        "priority": "critical",
                    },
                    {
                        "template_type": "employment_agreement",
                        "name": "Employment Agreement",
                        "why_needed": (
                            "The comprehensive contract that governs the employment relationship. Covers "
                            "compensation structure (CTC breakdown), probation, notice period, IP assignment, "
                            "confidentiality, non-compete, and termination terms."
                        ),
                        "when_to_create": "On or before the joining date of the employee",
                        "priority": "critical",
                    },
                    {
                        "template_type": "consultancy_agreement",
                        "name": "Consultancy Agreement",
                        "why_needed": (
                            "For hiring contractors, freelancers, or consultants. Clearly establishes that the "
                            "person is NOT an employee (avoiding PF/ESI obligations) and ensures IP for work "
                            "done belongs to the company."
                        ),
                        "when_to_create": "Before the consultant begins any work",
                        "priority": "critical",
                    },
                    {
                        "template_type": "freelancer_agreement",
                        "name": "Freelancer Agreement",
                        "why_needed": (
                            "Similar to a consultancy agreement but tailored for short-term, project-based "
                            "freelance engagements. Includes milestone-based payments and deliverable definitions."
                        ),
                        "when_to_create": "Before engaging any freelancer",
                        "priority": "recommended",
                    },
                    {
                        "template_type": "internship_agreement",
                        "name": "Internship Agreement",
                        "why_needed": (
                            "Formalizes internship terms including stipend, duration, project scope, and IP "
                            "assignment. Protects the company from claims that an intern was actually an employee."
                        ),
                        "when_to_create": "Before the intern starts",
                        "priority": "recommended",
                    },
                    {
                        "template_type": "advisor_agreement",
                        "name": "Advisor Agreement",
                        "why_needed": (
                            "Formalizes the relationship with advisors who provide strategic guidance. Typically "
                            "includes equity compensation (0.25-1% with vesting), scope of advisory, and time "
                            "commitment expectations."
                        ),
                        "when_to_create": "When onboarding an advisor, before granting any equity",
                        "priority": "recommended",
                    },
                ],
                "next_stage": "equity_esop",
            },
            {
                "id": "equity_esop",
                "stage_number": 4,
                "title": "Equity & ESOP Planning",
                "icon": "chart-pie",
                "description": "Set up your ESOP pool and share structure before fundraising.",
                "why_it_matters": (
                    "Before you raise funding, you need a clean cap table and an ESOP pool. Investors will "
                    "almost always require a 10-15% ESOP pool as a condition of investment, and they will want "
                    "it created BEFORE their investment (so their shares are not diluted by the ESOP).\n\n"
                    "Setting up ESOP early gives you a powerful tool to attract and retain talent without "
                    "spending cash. In India, ESOPs are governed by Section 62(1)(b) of the Companies Act "
                    "2013 and require shareholder approval via special resolution. The ESOP scheme must have "
                    "a minimum vesting period of 1 year (as per SEBI guidelines for listed companies, though "
                    "private companies often follow this as best practice).\n\n"
                    "Tax implication: Employees pay tax at two points — (1) at exercise (difference between "
                    "FMV and exercise price is taxed as perquisite under Section 17(2)) and (2) at sale "
                    "(capital gains tax). Understanding this helps you design an ESOP scheme that employees "
                    "actually want."
                ),
                "key_deadlines": [
                    "ESOP scheme approval: Special resolution at general meeting (Section 62(1)(b))",
                    "PAS-3 filing: Within 15 days of share allotment under ESOP",
                    "SH-7 filing: If authorized capital increase is needed (within 30 days)",
                    "Board resolution for ESOP grants: Before each grant",
                ],
                "documents": [
                    {
                        "template_type": "esop_plan",
                        "name": "ESOP Plan + Grant Letter",
                        "why_needed": (
                            "The master ESOP scheme document that defines the pool size, vesting schedule, "
                            "exercise price, and all terms. Individual grant letters are then issued to each "
                            "employee/advisor who receives options."
                        ),
                        "when_to_create": "Before your first fundraise, or when you want to start granting equity to team",
                        "priority": "critical",
                    },
                    {
                        "template_type": "board_resolution",
                        "name": "Board Resolution (ESOP Pool Creation)",
                        "why_needed": (
                            "Board must approve the creation of the ESOP pool and recommend it to shareholders. "
                            "This resolution is a prerequisite for the shareholder special resolution."
                        ),
                        "when_to_create": "Before the general meeting that approves the ESOP scheme",
                        "priority": "critical",
                    },
                    {
                        "template_type": "share_transfer",
                        "name": "Share Transfer Agreement",
                        "why_needed": (
                            "If equity restructuring is needed before fundraising (e.g., buying back a departed "
                            "founder's shares), you need a formal share transfer agreement with SH-4 form."
                        ),
                        "when_to_create": "When any share transfer occurs between shareholders",
                        "priority": "as-needed",
                    },
                ],
                "next_stage": "fundraising",
            },
            {
                "id": "fundraising",
                "stage_number": 5,
                "title": "Fundraising & Investment",
                "icon": "rocket",
                "description": "Raise your first round with proper legal structure.",
                "why_it_matters": (
                    "Fundraising is where legal documents become critically important. A Term Sheet sets the "
                    "commercial terms, while a Shareholders Agreement (SHA) is the comprehensive legal contract "
                    "that governs the investor-founder relationship for years to come.\n\n"
                    "In India, most early-stage investments are structured as equity rounds with the following "
                    "flow: (1) Term Sheet (non-binding, except exclusivity), (2) Due Diligence, (3) SHA + SSA "
                    "(Share Subscription Agreement), (4) Board and shareholder resolutions, (5) Share allotment "
                    "and PAS-3 filing.\n\n"
                    "Key concepts every founder must understand: Pre-money vs post-money valuation, anti-dilution "
                    "protection (full ratchet vs weighted average), liquidation preference (1x non-participating "
                    "is standard in India), board composition, information rights, drag-along and tag-along "
                    "rights, and founder vesting (yes, investors will require founders to vest).\n\n"
                    "Common mistake: Signing a Term Sheet without understanding liquidation preference. A 2x "
                    "participating preferred means the investor gets 2x their money back PLUS their pro-rata "
                    "share of remaining proceeds. This can dramatically reduce founder payout at exit."
                ),
                "key_deadlines": [
                    "PAS-3: Return of allotment within 15 days of share issuance",
                    "FC-GPR: If foreign investor, file with RBI within 30 days",
                    "FLA Return: Annual filing with RBI if foreign investment received",
                    "SH-7: If authorized capital increase needed (within 30 days)",
                    "MGT-14: File special resolution with ROC within 30 days",
                ],
                "documents": [
                    {
                        "template_type": "term_sheet",
                        "name": "Term Sheet",
                        "why_needed": (
                            "The starting point of any fundraise. Sets out key commercial terms: valuation, "
                            "investment amount, investor rights, board seats. Usually non-binding except for "
                            "exclusivity and confidentiality clauses."
                        ),
                        "when_to_create": "When you have a serious investor ready to commit",
                        "priority": "critical",
                    },
                    {
                        "template_type": "shareholder_agreement",
                        "name": "Shareholders Agreement (SHA)",
                        "why_needed": (
                            "The most important fundraising document. Governs the relationship between founders "
                            "and investors for the life of the investment. Covers board composition, reserved "
                            "matters, information rights, anti-dilution, exit provisions, and more."
                        ),
                        "when_to_create": "After Term Sheet is signed, as part of the definitive documents",
                        "priority": "critical",
                    },
                    {
                        "template_type": "convertible_note",
                        "name": "Convertible Note / iSAFE",
                        "why_needed": (
                            "An alternative to priced equity rounds, especially at pre-seed/seed stage. The "
                            "investor gives money now, and it converts to equity at the next priced round "
                            "(usually with a discount or valuation cap). Faster to execute than a full SHA."
                        ),
                        "when_to_create": "When raising a bridge round or pre-seed investment",
                        "priority": "recommended",
                    },
                    {
                        "template_type": "nda",
                        "name": "NDA (for investor discussions)",
                        "why_needed": (
                            "While many VCs refuse to sign NDAs, angel investors and strategic investors "
                            "often will. Useful when sharing detailed financials, technology details, or "
                            "customer data during due diligence."
                        ),
                        "when_to_create": "Before sharing confidential information with potential investors",
                        "priority": "optional",
                    },
                ],
                "next_stage": "operations",
            },
            {
                "id": "operations",
                "stage_number": 6,
                "title": "Business Operations & Contracts",
                "icon": "briefcase",
                "description": "Set up vendor, client, and service agreements for daily operations.",
                "why_it_matters": (
                    "As your company starts operating, you need standardized agreements for every business "
                    "relationship — with vendors, clients, service providers, and partners. Using proper "
                    "contracts protects your company from disputes, ensures clear payment terms, and "
                    "establishes IP ownership for any work done.\n\n"
                    "In India, contracts are governed by the Indian Contract Act 1872. For a contract to be "
                    "valid, it needs: free consent, lawful consideration, competent parties, and lawful object. "
                    "Stamp duty on agreements varies by state and type — not stamping a contract can make it "
                    "inadmissible in court."
                ),
                "key_deadlines": [
                    "GST invoicing: Within 30 days of supply of services",
                    "TDS deposits: 7th of the following month",
                    "Annual contracts: Review and renew before expiry",
                ],
                "documents": [
                    {
                        "template_type": "msa",
                        "name": "Master Service Agreement (MSA)",
                        "why_needed": (
                            "The umbrella agreement with clients that defines general terms. Individual projects "
                            "are then governed by Statements of Work (SOWs) under the MSA, making it easier "
                            "to onboard new projects without renegotiating everything."
                        ),
                        "when_to_create": "When onboarding a new client or major customer",
                        "priority": "critical",
                    },
                    {
                        "template_type": "vendor_agreement",
                        "name": "Vendor Agreement",
                        "why_needed": (
                            "Governs your relationship with suppliers and service providers. Protects against "
                            "delivery delays, quality issues, and ensures data protection when sharing "
                            "company information with vendors."
                        ),
                        "when_to_create": "Before engaging any significant vendor",
                        "priority": "recommended",
                    },
                    {
                        "template_type": "saas_agreement",
                        "name": "SaaS Agreement / Software License",
                        "why_needed": (
                            "If you sell software, this is your primary customer contract. Defines licensing "
                            "terms, SLA commitments, data handling, and limitation of liability. For SaaS "
                            "companies, this replaces the traditional MSA."
                        ),
                        "when_to_create": "Before onboarding your first paying customer",
                        "priority": "critical",
                    },
                    {
                        "template_type": "letter_of_intent",
                        "name": "Letter of Intent (LOI)",
                        "why_needed": (
                            "A preliminary document that outlines the intent to enter into a formal agreement. "
                            "Useful for large deals, partnerships, or acquisitions where both parties want to "
                            "establish terms before committing to a full contract."
                        ),
                        "when_to_create": "At the start of significant business negotiations",
                        "priority": "as-needed",
                    },
                ],
                "next_stage": "compliance_governance",
            },
            {
                "id": "compliance_governance",
                "stage_number": 7,
                "title": "Compliance & Governance",
                "icon": "shield-check",
                "description": "Stay compliant with ongoing legal requirements and hold proper meetings.",
                "why_it_matters": (
                    "Running a company in India comes with ongoing compliance obligations that, if ignored, "
                    "result in penalties, director disqualification, and even company strike-off. The Companies "
                    "Act 2013 requires regular board meetings, annual general meetings, statutory filings, "
                    "and maintenance of registers.\n\n"
                    "Directors can be personally liable for non-compliance. Under Section 164(2), a director "
                    "is disqualified if the company has not filed annual returns for 3 continuous years or has "
                    "not repaid deposits. This disqualification affects ALL companies where the person is a "
                    "director, not just the defaulting company.\n\n"
                    "The Annual Compliance Calendar for a typical Private Limited Company includes: 4 board "
                    "meetings per year (minimum), 1 AGM within 6 months of FY end, AOC-4 within 30 days of "
                    "AGM, MGT-7/MGT-7A within 60 days of AGM, ITR filing by September 30, GST returns "
                    "monthly/quarterly, TDS returns quarterly, PF/ESI returns monthly."
                ),
                "key_deadlines": [
                    "Board Meetings: Minimum 4 per year, gap not exceeding 120 days",
                    "AGM: Within 6 months of FY end (i.e., by September 30)",
                    "AOC-4: Within 30 days of AGM",
                    "MGT-7/MGT-7A: Within 60 days of AGM",
                    "ITR: By September 30 (if audit required) or July 31",
                    "DIR-3 KYC: Annually by September 30 for all directors",
                ],
                "documents": [
                    {
                        "template_type": "agm_notice",
                        "name": "AGM Notice",
                        "why_needed": (
                            "Formal notice to shareholders for the Annual General Meeting. Must be sent at "
                            "least 21 clear days before the AGM. Includes agenda items, proxy form, and "
                            "explanatory statements for special business."
                        ),
                        "when_to_create": "21+ days before the scheduled AGM date",
                        "priority": "critical",
                    },
                    {
                        "template_type": "egm_notice",
                        "name": "EGM Notice",
                        "why_needed": (
                            "For urgent matters that cannot wait until the next AGM — like approving a new "
                            "funding round, changing the registered office, or approving related party "
                            "transactions that require shareholder approval."
                        ),
                        "when_to_create": "When urgent shareholder approval is needed between AGMs",
                        "priority": "as-needed",
                    },
                    {
                        "template_type": "circular_resolution",
                        "name": "Circular / Written Resolution",
                        "why_needed": (
                            "Alternative to holding a physical board meeting. Under Section 175, the board "
                            "can pass resolutions by circulation if approved by majority of directors. Saves "
                            "time for routine matters."
                        ),
                        "when_to_create": "For routine board approvals that do not require discussion",
                        "priority": "recommended",
                    },
                    {
                        "template_type": "annual_compliance_checklist",
                        "name": "Annual Compliance Checklist",
                        "why_needed": (
                            "A comprehensive checklist to ensure nothing is missed during annual compliance. "
                            "Covers all MCA filings, tax returns, PF/ESI compliance, and statutory "
                            "register updates."
                        ),
                        "when_to_create": "At the start of each financial year, and review quarterly",
                        "priority": "critical",
                    },
                ],
                "next_stage": "policies",
            },
            {
                "id": "policies",
                "stage_number": 8,
                "title": "Policies & Legal Protection",
                "icon": "document-text",
                "description": "Establish company policies for data privacy, workplace safety, and legal protection.",
                "why_it_matters": (
                    "As your company grows, you need formal policies that protect both the company and its "
                    "stakeholders. Some policies are legally mandatory (POSH for companies with 10+ employees), "
                    "while others (Privacy Policy, Terms of Service) are essential for doing business, "
                    "especially online.\n\n"
                    "The DPDP Act 2023 (Digital Personal Data Protection Act) is India's equivalent of GDPR. "
                    "If you collect any personal data (even just email addresses from a signup form), you need "
                    "a compliant privacy policy. Violations can attract penalties up to Rs 250 Crores."
                ),
                "key_deadlines": [
                    "POSH Policy: Must be in place when company has 10+ employees",
                    "POSH ICC: Internal Complaints Committee must be constituted for 10+ employees",
                    "Privacy Policy: Must be published before collecting any personal data",
                    "Terms of Service: Must be accessible on your website/app before launch",
                ],
                "documents": [
                    {
                        "template_type": "privacy_policy",
                        "name": "Privacy Policy",
                        "why_needed": (
                            "Legally required under DPDP Act 2023 if you collect any personal data. "
                            "Must disclose what data you collect, why, how you process it, and user rights. "
                            "Required by app stores (Google Play, Apple App Store) for app listing."
                        ),
                        "when_to_create": "Before launching your website or app",
                        "priority": "critical",
                    },
                    {
                        "template_type": "terms_of_service",
                        "name": "Terms of Service",
                        "why_needed": (
                            "The legal agreement between your company and users of your product/service. "
                            "Limits your liability, defines acceptable use, and establishes dispute resolution "
                            "mechanisms. Essential for any online business."
                        ),
                        "when_to_create": "Before launching your product/service",
                        "priority": "critical",
                    },
                    {
                        "template_type": "posh_policy",
                        "name": "POSH Policy",
                        "why_needed": (
                            "Mandatory under the POSH Act 2013 for organizations with 10+ employees. "
                            "Must include ICC constitution, complaint procedures, and awareness guidelines. "
                            "Non-compliance can result in penalties and license cancellation."
                        ),
                        "when_to_create": "When your team reaches 10 employees",
                        "priority": "mandatory",
                    },
                    {
                        "template_type": "legal_notice",
                        "name": "Legal Notice / Demand Letter",
                        "why_needed": (
                            "When you need to formally demand action from a defaulting party — unpaid invoices, "
                            "contract breaches, IP infringement. Sending a legal notice is often a prerequisite "
                            "before filing a lawsuit in India."
                        ),
                        "when_to_create": "When a dispute arises that requires formal legal action",
                        "priority": "as-needed",
                    },
                    {
                        "template_type": "power_of_attorney",
                        "name": "Power of Attorney",
                        "why_needed": (
                            "Authorizes someone to act on behalf of the company or a director. Commonly needed "
                            "when a director cannot personally appear for property transactions, bank work, or "
                            "government filings."
                        ),
                        "when_to_create": "When delegation of authority is needed",
                        "priority": "as-needed",
                    },
                ],
                "next_stage": None,
            },
        ]

    # ------------------------------------------------------------------
    # Template-level contextual connections
    # ------------------------------------------------------------------

    def _build_template_contexts(self) -> Dict[str, Dict[str, Any]]:
        return {
            "founder_agreement": {
                "before_this": [],
                "after_this": ["ip_assignment", "nda", "esop_plan"],
                "tip": (
                    "You have completed your Founder Agreement. Next, ensure all founders sign an IP "
                    "Assignment Agreement to formally transfer any pre-existing IP to the company. "
                    "Then consider setting up your ESOP pool before your first fundraise."
                ),
                "common_mistakes": [
                    "Not including vesting — all equity should vest over 4 years with 1-year cliff",
                    "Equal splits by default — split based on contribution, commitment, and risk taken",
                    "Missing IP assignment clause — code written before incorporation still belongs to the individual",
                    "No exit provisions — define good leaver vs bad leaver clearly",
                ],
            },
            "nda": {
                "before_this": [],
                "after_this": ["founder_agreement", "consultancy_agreement", "advisor_agreement"],
                "tip": (
                    "NDAs should be signed before sharing any confidential information. "
                    "For co-founder discussions, follow up with a formal Founder Agreement. "
                    "For consultants and advisors, pair the NDA with their engagement agreement."
                ),
                "common_mistakes": [
                    "Making it too broad — courts strike down vague confidentiality definitions",
                    "Unreasonable duration — 2-3 years is standard, not perpetual",
                    "Not specifying what is NOT confidential — publicly available info, prior knowledge",
                ],
            },
            "employment_agreement": {
                "before_this": ["offer_letter"],
                "after_this": ["esop_plan", "posh_policy"],
                "tip": (
                    "After signing the employment agreement, consider granting ESOPs to key employees "
                    "as a retention tool. Once you have 10+ employees, you must implement a POSH policy."
                ),
                "common_mistakes": [
                    "Not including IP assignment clause — employee-created IP may not belong to company",
                    "Overly broad non-compete — Indian courts rarely enforce non-competes post-employment",
                    "Not specifying CTC breakdown — ambiguity leads to disputes during separation",
                ],
            },
            "term_sheet": {
                "before_this": ["founder_agreement", "esop_plan", "nda"],
                "after_this": ["shareholder_agreement", "board_resolution"],
                "tip": (
                    "Before signing a Term Sheet, ensure your Founder Agreement and ESOP plan are in "
                    "place. After the Term Sheet, you will negotiate the detailed Shareholders Agreement "
                    "and pass board resolutions for share allotment."
                ),
                "common_mistakes": [
                    "Not negotiating the ESOP pool size — investors want it pre-money, diluting founders",
                    "Ignoring liquidation preference terms — understand 1x non-participating vs participating",
                    "Signing exclusivity without a time limit — 30-45 days is standard",
                    "Not understanding anti-dilution protection types",
                ],
            },
            "shareholder_agreement": {
                "before_this": ["term_sheet", "founder_agreement"],
                "after_this": ["board_resolution"],
                "tip": (
                    "The SHA is the binding version of the Term Sheet. After signing, pass board "
                    "resolutions for share allotment and file PAS-3 with the ROC within 15 days."
                ),
                "common_mistakes": [
                    "Founder-unfriendly reserved matters list — negotiate to limit investor vetoes",
                    "Missing drag-along threshold — should require 75%+ shareholder approval",
                    "Not negotiating information rights scope — monthly financials is excessive for seed stage",
                ],
            },
            "esop_plan": {
                "before_this": ["founder_agreement", "board_resolution"],
                "after_this": ["employment_agreement", "advisor_agreement"],
                "tip": (
                    "ESOP scheme must be approved by shareholder special resolution. Once approved, "
                    "you can issue grant letters to employees and advisors. Remember: the ESOP pool "
                    "size is usually negotiated during fundraising."
                ),
                "common_mistakes": [
                    "Setting exercise price too high — defeats the purpose of employee incentive",
                    "Not explaining tax implications to employees — perquisite tax at exercise",
                    "Missing acceleration clause — what happens to vesting on acquisition/exit",
                ],
            },
            "privacy_policy": {
                "before_this": [],
                "after_this": ["terms_of_service"],
                "tip": (
                    "Your Privacy Policy and Terms of Service work together. Both should be published "
                    "before your product goes live. If you collect user data, DPDP Act compliance is mandatory."
                ),
                "common_mistakes": [
                    "Copy-pasting from another company — must reflect YOUR actual data practices",
                    "Not covering third-party data sharing — analytics tools, payment processors",
                    "Missing data breach notification procedure — 72 hours under DPDP Act",
                ],
            },
            "consultancy_agreement": {
                "before_this": ["nda"],
                "after_this": [],
                "tip": (
                    "Always pair a Consultancy Agreement with an NDA. Ensure the IP assignment clause "
                    "is airtight — under Indian law, the consultant owns their work unless explicitly assigned."
                ),
                "common_mistakes": [
                    "Misclassifying employees as consultants to avoid PF/ESI",
                    "Not defining deliverables clearly — leads to payment disputes",
                    "Missing TDS clause — you must deduct 10% TDS under Section 194J",
                ],
            },
            "board_resolution": {
                "before_this": [],
                "after_this": [],
                "tip": (
                    "Board resolutions are needed for almost every major corporate action. Maintain a "
                    "proper minutes book — Section 118 requires minutes to be prepared within 30 days."
                ),
                "common_mistakes": [
                    "Not maintaining quorum — minimum 2 directors or 1/3 of total, whichever is higher",
                    "Backdating resolutions — illegal and can invalidate the action",
                    "Not filing form with ROC where required — some resolutions need MGT-14 filing",
                ],
            },
            "convertible_note": {
                "before_this": ["nda", "term_sheet"],
                "after_this": ["shareholder_agreement"],
                "tip": (
                    "Convertible notes are faster than priced rounds but create future obligations. "
                    "Ensure the conversion terms (discount, cap) are clearly defined. The note will "
                    "convert at the next priced round into equity."
                ),
                "common_mistakes": [
                    "Not setting a valuation cap — unlimited dilution risk for the investor",
                    "Missing maturity date — what happens if no priced round occurs",
                    "Not understanding the conversion mechanics at the next round",
                ],
            },
            "msa": {
                "before_this": [],
                "after_this": ["saas_agreement"],
                "tip": (
                    "An MSA provides the umbrella terms for client relationships. Individual projects "
                    "are governed by SOWs (Statements of Work) that reference the MSA."
                ),
                "common_mistakes": [
                    "Unlimited liability — always cap liability to fees received in last 12 months",
                    "Missing indemnification terms — define who is responsible for third-party claims",
                    "Not specifying payment terms clearly — Net 30 is standard in India",
                ],
            },
            "ip_assignment": {
                "before_this": ["founder_agreement"],
                "after_this": [],
                "tip": (
                    "IP Assignment should be signed alongside or immediately after the Founder Agreement. "
                    "It covers ALL IP created by founders, including work done before incorporation."
                ),
                "common_mistakes": [
                    "Not listing pre-existing IP — what the founder is NOT assigning",
                    "Missing future IP clause — IP created during employment must auto-assign",
                    "Not recording the assignment with the Patent/Copyright office where applicable",
                ],
            },
            "offer_letter": {
                "before_this": [],
                "after_this": ["employment_agreement"],
                "tip": (
                    "The Offer Letter is a preliminary document. Follow it up with a detailed "
                    "Employment Agreement on or before the joining date."
                ),
                "common_mistakes": [
                    "Making the offer letter too detailed — it should be concise, the employment agreement has the detail",
                    "Not including a validity period — candidates may hold the offer indefinitely",
                    "Missing conditions (background verification, medical fitness)",
                ],
            },
            "share_transfer": {
                "before_this": ["board_resolution"],
                "after_this": [],
                "tip": (
                    "Share transfers require board approval (check your articles), SH-4 form execution, "
                    "stamp duty payment, and register of members update."
                ),
                "common_mistakes": [
                    "Not checking transfer restrictions in Articles of Association or SHA",
                    "Not paying stamp duty — 0.015% of consideration or market value",
                    "Not filing with ROC where required",
                ],
            },
            "terms_of_service": {
                "before_this": ["privacy_policy"],
                "after_this": [],
                "tip": (
                    "Terms of Service should be published alongside your Privacy Policy before launch. "
                    "Include dispute resolution, limitation of liability, and acceptable use."
                ),
                "common_mistakes": [
                    "Not making Terms accessible — must be easily findable on website",
                    "Copy-pasting US terms — Indian law differs significantly",
                    "Missing jurisdiction clause — specify Indian courts and city",
                ],
            },
            "posh_policy": {
                "before_this": [],
                "after_this": [],
                "tip": (
                    "POSH is mandatory for 10+ employees. Constitute an ICC, conduct awareness "
                    "training, and file an annual report with the District Officer."
                ),
                "common_mistakes": [
                    "Not constituting the ICC — requires external member from women's organization",
                    "Not conducting annual awareness sessions",
                    "Not filing the annual report with District Officer",
                ],
            },
            "vendor_agreement": {
                "before_this": ["nda"],
                "after_this": [],
                "tip": "Always pair vendor agreements with NDAs if the vendor will access company data or systems.",
                "common_mistakes": [
                    "Not including SLA and penalty clauses for service quality",
                    "Missing data protection obligations",
                    "Not defining clear termination and transition terms",
                ],
            },
            "saas_agreement": {
                "before_this": ["privacy_policy", "terms_of_service"],
                "after_this": [],
                "tip": (
                    "Your SaaS Agreement should reference your Privacy Policy for data handling. "
                    "Include uptime SLA commitments and data portability provisions."
                ),
                "common_mistakes": [
                    "Not defining SLA with remedies for downtime",
                    "Missing data ownership clause — customer data belongs to the customer",
                    "Not addressing data export/portability on contract termination",
                ],
            },
            "freelancer_agreement": {
                "before_this": ["nda"],
                "after_this": [],
                "tip": "Always get an NDA signed before sharing project details. Include clear IP assignment and milestone-based payments.",
                "common_mistakes": [
                    "Treating freelancers as employees without the benefits",
                    "Not defining deliverables precisely enough",
                    "Missing IP assignment — freelancer owns their work by default under Indian Copyright Act",
                ],
            },
            "internship_agreement": {
                "before_this": [],
                "after_this": ["offer_letter"],
                "tip": "If converting interns to full-time, issue a formal offer letter and employment agreement at the end of the internship.",
                "common_mistakes": [
                    "Not paying stipend — unpaid internships risk being classified as bonded labour",
                    "Not including IP assignment for intern-created work",
                    "Missing duration and scope — open-ended internships create ambiguity",
                ],
            },
            "agm_notice": {
                "before_this": ["board_resolution"],
                "after_this": ["annual_compliance_checklist"],
                "tip": "The board must first approve the AGM date and agenda. After the AGM, complete all post-AGM filings (AOC-4, MGT-7).",
                "common_mistakes": [
                    "Not sending notice 21 clear days in advance — invalidates the AGM",
                    "Missing explanatory statement for special business items",
                    "Not including proxy form — mandatory under Section 105",
                ],
            },
            "egm_notice": {
                "before_this": ["board_resolution"],
                "after_this": [],
                "tip": "EGM can be called by the board or requisitioned by shareholders holding 10%+ of voting rights.",
                "common_mistakes": [
                    "Not sending 21 clear days notice (same as AGM)",
                    "Passing matters as ordinary resolution when special resolution is required",
                ],
            },
            "circular_resolution": {
                "before_this": [],
                "after_this": [],
                "tip": "Circular resolutions cannot be used for matters that require discussion at a board meeting (like approving financial statements).",
                "common_mistakes": [
                    "Using for restricted matters — Section 175(1) prohibits certain matters",
                    "Not getting majority approval of all directors (not just those present)",
                ],
            },
            "annual_compliance_checklist": {
                "before_this": ["agm_notice"],
                "after_this": [],
                "tip": "Use this checklist at the start of each financial year. Set calendar reminders for each deadline to avoid penalties.",
                "common_mistakes": [
                    "Missing DIR-3 KYC deadline — directors get deactivated DINs",
                    "Not filing AOC-4 within 30 days of AGM — Rs 100/day penalty",
                    "Forgetting ADT-1 for auditor reappointment",
                ],
            },
            "letter_of_intent": {
                "before_this": ["nda"],
                "after_this": ["msa", "shareholder_agreement"],
                "tip": "LOIs are usually non-binding. Clearly state which clauses are binding (typically confidentiality and exclusivity).",
                "common_mistakes": [
                    "Making the LOI accidentally binding — courts may enforce detailed LOIs",
                    "Not including a sunset clause — LOI should expire if not converted to definitive agreement",
                ],
            },
            "power_of_attorney": {
                "before_this": [],
                "after_this": [],
                "tip": "POA must be on proper stamp paper. A general POA gives broad powers — prefer specific POA for specific tasks.",
                "common_mistakes": [
                    "Giving general POA when specific POA would suffice — limits abuse risk",
                    "Not registering the POA where required (e.g., property transactions)",
                    "Not revoking POA when no longer needed",
                ],
            },
            "legal_notice": {
                "before_this": [],
                "after_this": [],
                "tip": "Sending a legal notice is often a prerequisite before filing a civil suit. Keep it factual and professional.",
                "common_mistakes": [
                    "Being too aggressive in tone — may be used against you in court",
                    "Not giving a reasonable response time — 15-30 days is standard",
                    "Not sending via registered post/speed post with acknowledgement due",
                ],
            },
            "advisor_agreement": {
                "before_this": ["nda"],
                "after_this": ["esop_plan"],
                "tip": (
                    "Advisor agreements should be paired with an NDA and, if equity is involved, "
                    "an ESOP grant letter. Define the advisory scope and time commitment clearly."
                ),
                "common_mistakes": [
                    "Granting equity without vesting — advisors should vest over 2 years",
                    "Not defining the time commitment — '2 hours per month' is clearer than 'as needed'",
                    "Missing IP assignment for any work the advisor contributes",
                ],
            },
        }

    # ------------------------------------------------------------------
    # Quick tips for the learning path homepage
    # ------------------------------------------------------------------

    def _build_quick_tips(self) -> List[Dict[str, str]]:
        return [
            {
                "title": "Incorporate Before Building",
                "content": (
                    "Don't wait until you have a product to incorporate. Without a legal entity, "
                    "you can't protect IP, open a business bank account, or raise investment."
                ),
                "category": "timing",
            },
            {
                "title": "Vesting Is Non-Negotiable",
                "content": (
                    "All founder equity should vest over 4 years with a 1-year cliff. This "
                    "protects all co-founders from someone leaving early with a large stake."
                ),
                "category": "equity",
            },
            {
                "title": "IP Belongs to the Creator by Default",
                "content": (
                    "Under Indian law (Copyright Act 1957, Section 17), the author owns the "
                    "work — not the company. You need explicit IP assignment agreements for "
                    "every founder, employee, and contractor."
                ),
                "category": "legal",
            },
            {
                "title": "ESOP Pool Before Fundraising",
                "content": (
                    "Create your ESOP pool before raising investment. Investors will insist on "
                    "it being created pre-money, meaning it dilutes founders, not investors."
                ),
                "category": "fundraising",
            },
            {
                "title": "Compliance Is Not Optional",
                "content": (
                    "Missing MCA filings can disqualify your directors and get your company "
                    "struck off. Set calendar reminders for all deadlines."
                ),
                "category": "compliance",
            },
            {
                "title": "Stamp Duty Matters",
                "content": (
                    "Unstamped agreements are inadmissible as evidence in Indian courts. "
                    "Always check state-specific stamp duty requirements for your agreements."
                ),
                "category": "legal",
            },
            {
                "title": "10 Employees = POSH Mandatory",
                "content": (
                    "Once you have 10 or more employees, the POSH Act requires you to have a "
                    "policy, constitute an Internal Complaints Committee, and conduct awareness training."
                ),
                "category": "compliance",
            },
            {
                "title": "Non-Competes Are Mostly Unenforceable",
                "content": (
                    "Section 27 of the Indian Contract Act 1872 makes post-employment "
                    "non-compete clauses generally unenforceable in India. Focus on "
                    "non-solicitation and confidentiality instead."
                ),
                "category": "legal",
            },
        ]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
founder_education_service = FounderEducationService()
