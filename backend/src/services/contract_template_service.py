"""Contract template definitions with clause-level customization and educational content.

Each template is defined as a dict with:
- metadata (name, description, category)
- wizard steps (ordered groups of clauses)
- clause definitions (with educational content, input types, defaults, warnings)

Supports: Founder Agreement, NDA, Employment Agreement, Consultancy Agreement.
All templates include India-specific legal references and educational guidance.
"""

from typing import Any, Optional, Dict, List
from jinja2 import Template

from src.services.contract_templates_tier2 import TIER2_TEMPLATES, TIER2_RENDERERS
from src.services.contract_templates_tier3a import TIER3A_TEMPLATES, TIER3A_RENDERERS
from src.services.contract_templates_tier3b import TIER3B_TEMPLATES, TIER3B_RENDERERS


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
    """Build a clause definition dict with all optional educational fields."""
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
# ContractTemplateService
# ---------------------------------------------------------------------------

class ContractTemplateService:
    """Manages legal document template definitions and rendering."""

    def __init__(self) -> None:
        self._templates = self._build_templates()

    # -- public API ---------------------------------------------------------

    def get_available_templates(self) -> List[dict]:
        """Return list of available template metadata (no clause details)."""
        result = []
        for key, tpl in self._templates.items():
            result.append({
                "template_type": key,
                "name": tpl["name"],
                "description": tpl["description"],
                "category": tpl["category"],
                "total_steps": len(tpl["steps"]),
                "total_clauses": sum(len(s["clauses"]) for s in tpl["steps"]),
            })
        return result

    def get_template_definition(self, template_type: str) -> Optional[dict]:
        """Return full template definition with flat clause list and clause_ids per step.

        Transforms the internal structure (clauses nested inside steps) to the
        API-friendly format expected by the frontend:
        {
            "template_type": ...,
            "name": ...,
            "steps": [{"step_number": 1, "title": ..., "clause_ids": [...]}],
            "clauses": [{"id": ..., "title": ..., ...}]  # flat list
        }
        """
        tpl = self._templates.get(template_type)
        if not tpl:
            return None

        flat_clauses: List[dict] = []
        api_steps: List[dict] = []

        for step in tpl["steps"]:
            clause_ids = [c["id"] for c in step.get("clauses", [])]
            api_steps.append({
                "step_number": step["step_number"],
                "title": step["title"],
                "description": step.get("description", ""),
                "clause_ids": clause_ids,
            })
            for c in step.get("clauses", []):
                # Normalize 'label' -> 'title' for frontend consistency
                clause_copy = dict(c)
                if "label" in clause_copy and "title" not in clause_copy:
                    clause_copy["title"] = clause_copy.pop("label")
                # Normalize options: if options is a list of strings, convert to objects
                if "options" in clause_copy and clause_copy["options"]:
                    if isinstance(clause_copy["options"][0], str):
                        clause_copy["options"] = [
                            {"value": o, "label": o} for o in clause_copy["options"]
                        ]
                flat_clauses.append(clause_copy)

        return {
            "template_type": template_type,
            "name": tpl["name"],
            "description": tpl["description"],
            "category": tpl["category"],
            "steps": api_steps,
            "clauses": flat_clauses,
        }

    def get_clause_preview_text(self, template_type: str, clause_id: str, value: Any) -> str:
        """Generate preview text for a single clause given a value."""
        tpl = self._templates.get(template_type)
        if not tpl:
            return ""
        for step in tpl["steps"]:
            for clause in step["clauses"]:
                if clause["id"] == clause_id:
                    pt = clause.get("preview_template", "")
                    if pt and value is not None:
                        try:
                            return pt.format(value=value)
                        except (KeyError, IndexError):
                            return pt
                    return ""
        return ""

    def validate_clauses_config(self, template_type: str, config: dict) -> dict:
        """Validate clause config against template. Returns {errors, warnings}."""
        result: Dict[str, List[str]] = {"errors": [], "warnings": []}
        tpl = self._templates.get(template_type)
        if not tpl:
            result["errors"].append(f"Unknown template type: {template_type}")
            return result

        clause_map: Dict[str, dict] = {}
        for step in tpl["steps"]:
            for clause in step["clauses"]:
                clause_map[clause["id"]] = clause

        # Check required clauses
        for cid, cdef in clause_map.items():
            # Skip if clause depends on a disabled parent
            dep = cdef.get("depends_on")
            if dep and not config.get(dep):
                continue
            if cdef.get("required") and cid not in config:
                result["errors"].append(f"Missing required clause: {cdef['label']}")

        # Check option validity
        for cid, val in config.items():
            cdef = clause_map.get(cid)
            if not cdef:
                continue
            if "options" in cdef and val not in cdef["options"]:
                if cdef["input_type"] != "multi_select":
                    result["errors"].append(
                        f"Invalid value for {cdef['label']}: {val}"
                    )
            if cdef.get("min_value") is not None and isinstance(val, (int, float)):
                if val < cdef["min_value"]:
                    result["errors"].append(
                        f"{cdef['label']} must be at least {cdef['min_value']}"
                    )
            if cdef.get("max_value") is not None and isinstance(val, (int, float)):
                if val > cdef["max_value"]:
                    result["errors"].append(
                        f"{cdef['label']} must be at most {cdef['max_value']}"
                    )

        # Check conditional warnings
        for cid, cdef in clause_map.items():
            wc = cdef.get("warning_condition")
            if not wc:
                continue
            if self._check_warning_condition(wc, config):
                result["warnings"].append(cdef.get("warning", ""))

        # Standalone warnings based on values
        if config.get("vesting_enabled") is False:
            w = clause_map.get("vesting_enabled", {}).get("warning")
            if w:
                result["warnings"].append(w)

        return result

    def render_html(
        self,
        template_type: str,
        clauses_config: dict,
        parties: Optional[dict] = None,
    ) -> str:
        """Render full document HTML using Jinja2."""
        tpl = self._templates.get(template_type)
        if not tpl:
            return "<p>Unknown template type.</p>"

        renderer = self._renderers.get(template_type)
        if renderer:
            return renderer(tpl, clauses_config, parties or {})
        return "<p>Rendering not available for this template type.</p>"

    # -- template builders --------------------------------------------------

    def _build_templates(self) -> dict:
        """Build all template definitions."""
        self._renderers: Dict[str, Any] = {
            "founder_agreement": self._render_founder_agreement,
            "nda": self._render_nda,
            "employment_agreement": self._render_employment_agreement,
            "consultancy_agreement": self._render_consultancy_agreement,
            "shareholders_agreement": self._render_shareholders_agreement,
            "term_sheet": self._render_term_sheet,
            "advisor_agreement": self._render_advisor_agreement,
            "esop_plan": self._render_esop_plan,
        }
        # Merge Tier 2, 3A, 3B renderers
        self._renderers.update(TIER2_RENDERERS)
        self._renderers.update(TIER3A_RENDERERS)
        self._renderers.update(TIER3B_RENDERERS)

        templates = {
            "founder_agreement": self._founder_agreement(),
            "nda": self._nda(),
            "employment_agreement": self._employment_agreement(),
            "consultancy_agreement": self._consultancy_agreement(),
            "shareholders_agreement": self._shareholders_agreement(),
            "term_sheet": self._term_sheet(),
            "advisor_agreement": self._advisor_agreement(),
            "esop_plan": self._esop_plan(),
        }
        # Merge Tier 2, 3A, 3B templates
        templates.update(TIER2_TEMPLATES)
        templates.update(TIER3A_TEMPLATES)
        templates.update(TIER3B_TEMPLATES)
        return templates

    # -- private helpers ----------------------------------------------------

    @staticmethod
    def _check_warning_condition(condition: dict, config: dict) -> bool:
        """Evaluate a simple warning condition against the config."""
        op = condition.get("operator", "eq")
        field = condition.get("field", "")
        expected = condition.get("value")
        actual = config.get(field)

        if op == "eq":
            return actual == expected
        if op == "and":
            clauses = condition.get("clauses", [])
            return all(
                ContractTemplateService._check_warning_condition(c, config)
                for c in clauses
            )
        return False

    # ======================================================================
    # TEMPLATE 1: FOUNDER / CO-FOUNDER AGREEMENT
    # ======================================================================

    def _founder_agreement(self) -> dict:
        return {
            "name": "Founder / Co-Founder Agreement",
            "description": (
                "A comprehensive agreement between co-founders covering equity, "
                "vesting, roles, IP, exit terms, and more. Essential for any "
                "startup with multiple founders."
            ),
            "category": "Startup Essentials",
            "steps": [
                self._fa_step1_basic_info(),
                self._fa_step2_equity(),
                self._fa_step3_vesting(),
                self._fa_step4_roles(),
                self._fa_step5_ip(),
                self._fa_step6_restrictive_covenants(),
                self._fa_step7_exit(),
                self._fa_step8_miscellaneous(),
            ],
        }

    # -- Step 1 -------------------------------------------------------------

    @staticmethod
    def _fa_step1_basic_info() -> dict:
        return {
            "step_number": 1,
            "title": "Basic Information",
            "description": "Core details about your company and this agreement.",
            "clauses": [
                _clause(
                    "effective_date", "Effective Date", "date",
                    "The date from which this agreement becomes legally binding.",
                    preview_template="This Agreement is effective as of {value}.",
                ),
                _clause(
                    "company_name", "Company Name", "text",
                    "The registered or proposed name of the company.",
                    preview_template='The company shall be known as "{value}".',
                ),
                _clause(
                    "company_type", "Company Type", "dropdown",
                    "The legal structure determines governance rules and founder liability.",
                    options=["Private Limited", "LLP", "OPC"],
                    default="Private Limited",
                    preview_template="The company shall be incorporated as a {value} company.",
                ),
                _clause(
                    "num_founders", "Number of Founders", "number",
                    "Total number of co-founders who will be party to this agreement.",
                    min_value=2, max_value=10, default=2,
                    preview_template="This agreement is entered into by {value} co-founders.",
                ),
            ],
        }

    # -- Step 2 -------------------------------------------------------------

    @staticmethod
    def _fa_step2_equity() -> dict:
        return {
            "step_number": 2,
            "title": "Equity & Ownership",
            "description": "How ownership is divided among founders.",
            "clauses": [
                _clause(
                    "equity_split", "Equity Split", "custom",
                    "How ownership is divided among founders. This is the single most important decision you will make.",
                    learn_more=(
                        "Equal splits (50-50) are common for 2 co-founders but can create deadlocks. "
                        "Consider: Who had the original idea? Who is contributing more capital? "
                        "Who will work full-time vs part-time? In India, equity is represented through "
                        "shares — for a Private Limited company, the minimum authorized capital is "
                        "\u20b91 lakh."
                    ),
                    pros=[
                        "Simple and feels fair",
                        "Avoids difficult conversations early on",
                        "Easier to agree upon",
                    ],
                    cons=[
                        "Doesn't reflect different contributions",
                        "Can cause resentment later",
                        "Creates voting deadlocks with even number of founders",
                    ],
                    india_note=(
                        "Under the Companies Act 2013, share allotment must comply with Section 62. "
                        "Different share classes (equity vs preference) have different rights. "
                        "Consider sweat equity provisions under Section 54."
                    ),
                    warning="Equal equity split with an even number of founders creates deadlock risk.",
                    warning_condition={
                        "operator": "and",
                        "clauses": [
                            {"field": "equity_split", "operator": "eq", "value": "equal"},
                            {"field": "_even_founders", "operator": "eq", "value": True},
                        ],
                    },
                    preview_template="The equity shall be divided as follows: {value}.",
                ),
                _clause(
                    "share_class", "Share Class", "dropdown",
                    "Whether all founders get the same type of shares or some get preference shares with different rights.",
                    options=["Equity Shares", "Equity + Preference Shares"],
                    default="Equity Shares",
                    learn_more=(
                        "Equity shares carry voting rights and proportional dividends. "
                        "Preference shares can have fixed dividends and priority in liquidation "
                        "but may have limited voting. Most early-stage startups issue only equity "
                        "shares to founders."
                    ),
                    india_note=(
                        "Under Companies Act 2013, preference shares must be redeemed within "
                        "20 years. Section 43 defines equity and preference share capital."
                    ),
                    common_choice_label="Most startups choose: Equity Shares only",
                    preview_template="The company shall issue {value} to the founders.",
                ),
                _clause(
                    "capital_contribution", "Capital Contribution", "dropdown",
                    "How much money each founder puts in initially.",
                    options=["Equal", "Proportional to Equity", "Custom Amounts"],
                    default="Equal",
                    learn_more=(
                        "Capital contribution is the initial money founders invest. It can be "
                        "equal regardless of equity split, or proportional. For a Private Limited "
                        "company, minimum paid-up capital has no statutory minimum anymore "
                        "(removed in 2015 amendment), but you need at least \u20b91 lakh authorized capital."
                    ),
                    common_choice_label="Most startups choose: Equal contribution",
                    preview_template="Capital contribution shall be {value} among the founders.",
                ),
            ],
        }

    # -- Step 3 -------------------------------------------------------------

    @staticmethod
    def _fa_step3_vesting() -> dict:
        return {
            "step_number": 3,
            "title": "Vesting",
            "description": "Whether and how founders earn their equity over time.",
            "clauses": [
                _clause(
                    "vesting_enabled", "Enable Vesting", "toggle",
                    "Whether founders earn their equity over time rather than receiving it all upfront.",
                    default=True,
                    learn_more=(
                        "Vesting protects all founders. If a co-founder leaves after 3 months, "
                        "without vesting they keep all their shares. With vesting, unvested shares "
                        "return to the company. Standard is 4 years with 1-year cliff. This means: "
                        "if you leave before 1 year, you get nothing. After 1 year, you get 25%. "
                        "Then monthly/quarterly after that."
                    ),
                    pros=[
                        "Protects against early departures",
                        "Aligns incentives",
                        "Required by most investors",
                        "Industry standard practice",
                    ],
                    cons=[
                        "Founders don't 'own' all shares immediately",
                        "Adds complexity",
                        "Need to track vesting schedule",
                    ],
                    india_note=(
                        "In India, founder vesting is typically implemented through share transfer "
                        "restrictions in the Shareholders Agreement rather than stock options. "
                        "The shares are allotted upfront but subject to buyback at par value if "
                        "the founder leaves early."
                    ),
                    warning=(
                        "Most investors will require founder vesting. Not having vesting creates "
                        "significant risk if a co-founder leaves early."
                    ),
                    common_choice_label="Most startups choose: Yes",
                    preview_template="Founder equity shall {value} be subject to vesting.",
                ),
                _clause(
                    "vesting_period", "Vesting Period", "dropdown",
                    "The total time over which equity fully vests.",
                    options=["3 years", "4 years", "5 years"],
                    default="4 years",
                    common_choice_label="Industry standard: 4 years",
                    depends_on="vesting_enabled",
                    preview_template="The vesting period shall be {value} from the effective date.",
                ),
                _clause(
                    "cliff_period", "Cliff Period", "dropdown",
                    "Minimum time before any equity vests. If a founder leaves before the cliff, they get nothing.",
                    options=["6 months", "1 year", "18 months"],
                    default="1 year",
                    common_choice_label="Industry standard: 1 year",
                    depends_on="vesting_enabled",
                    preview_template="The cliff period shall be {value}.",
                ),
                _clause(
                    "acceleration_on_exit", "Acceleration on Exit", "dropdown",
                    "Whether vesting accelerates if the company is acquired.",
                    options=["No acceleration", "Single trigger", "Double trigger"],
                    default="Double trigger",
                    learn_more=(
                        "Single trigger: All shares vest immediately upon acquisition. "
                        "Double trigger: Shares vest only if the founder is also terminated/"
                        "forced out after acquisition. Double trigger is more investor-friendly "
                        "as it keeps founders incentivized to stay through transition."
                    ),
                    pros=[
                        "Single trigger: Rewards founders on exit",
                        "Double trigger: Keeps founders post-acquisition",
                    ],
                    cons=[
                        "Single trigger: Acquirer may not want fully vested founders who can leave",
                        "Double trigger: Founders may not benefit if they want to leave",
                    ],
                    common_choice_label="Investor-preferred: Double trigger",
                    depends_on="vesting_enabled",
                    preview_template="Upon a change of control event, vesting acceleration shall be: {value}.",
                ),
            ],
        }

    # -- Step 4 -------------------------------------------------------------

    @staticmethod
    def _fa_step4_roles() -> dict:
        return {
            "step_number": 4,
            "title": "Roles & Responsibilities",
            "description": "Define each founder's role and how decisions are made.",
            "clauses": [
                _clause(
                    "founder_roles", "Founder Roles & Designations", "custom",
                    "Each founder's title and primary responsibilities.",
                    learn_more=(
                        "Clearly defining roles prevents overlap and conflict. Common founder "
                        "roles: CEO (strategy, fundraising), CTO (technology, product), "
                        "COO (operations), CFO (finance). In Indian startups, one founder is "
                        "typically designated as the Managing Director under the Companies Act."
                    ),
                    india_note=(
                        "Under Companies Act 2013, a Managing Director (Section 2(54)) has "
                        "substantial powers of management. The designation carries legal "
                        "significance for liability and compliance."
                    ),
                    required=False,
                    preview_template="The founders shall serve in the following capacities: {value}.",
                ),
                _clause(
                    "time_commitment", "Time Commitment", "dropdown",
                    "How much time each founder commits to the company.",
                    options=["Full-time", "Part-time with transition to full-time", "Part-time"],
                    default="Full-time",
                    warning=(
                        "Part-time commitment from founders often leads to conflicts. "
                        "Consider setting a clear transition timeline."
                    ),
                    warning_condition={
                        "field": "time_commitment",
                        "operator": "eq",
                        "value": "Part-time",
                    },
                    common_choice_label="Most startups require: Full-time",
                    preview_template="Each founder shall commit on a {value} basis to the company.",
                ),
                _clause(
                    "decision_making", "Decision Making", "dropdown",
                    "How key business decisions are made among founders.",
                    options=[
                        "Unanimous",
                        "Simple majority",
                        "Board decides",
                        "CEO decides day-to-day with board for major decisions",
                    ],
                    default="CEO decides day-to-day with board for major decisions",
                    learn_more=(
                        "Unanimous decisions can create gridlock. Board-based decisions work "
                        "well when you have investors. CEO-decides for day-to-day with board "
                        "for major decisions (above \u20b9X threshold) is the most practical approach."
                    ),
                    common_choice_label="Most practical: CEO + Board for major decisions",
                    preview_template="Business decisions shall be made by: {value}.",
                ),
            ],
        }

    # -- Step 5 -------------------------------------------------------------

    @staticmethod
    def _fa_step5_ip() -> dict:
        return {
            "step_number": 5,
            "title": "Intellectual Property",
            "description": "Who owns the ideas, code, designs, and inventions.",
            "clauses": [
                _clause(
                    "ip_assignment", "IP Assignment", "dropdown",
                    "Who owns the intellectual property created by founders.",
                    options=[
                        "All IP to company",
                        "Existing IP licensed, new IP assigned",
                        "Custom",
                    ],
                    default="All IP to company",
                    learn_more=(
                        "This is critical. Without clear IP assignment, a departing founder "
                        "could claim ownership of code, designs, or inventions they created. "
                        "Best practice: ALL IP created for the company belongs to the company. "
                        "Founders can retain personal/prior IP but grant the company a license."
                    ),
                    india_note=(
                        "Under Indian Copyright Act 1957, the author (creator) is the first "
                        "owner of copyright, UNLESS it was created during employment. For "
                        "founders, an explicit assignment is needed. Patent rights follow the "
                        "Patents Act 1970."
                    ),
                    common_choice_label="Most startups choose: All IP to company",
                    warning="Investors will typically require all IP to be assigned to the company.",
                    warning_condition={
                        "field": "ip_assignment",
                        "operator": "eq",
                        "value": "Custom",
                    },
                    preview_template="All intellectual property created by founders shall be: {value}.",
                ),
                _clause(
                    "prior_ip", "Prior IP", "dropdown",
                    "Whether founders have existing IP they are bringing into the company.",
                    options=[
                        "No prior IP",
                        "List and license to company",
                        "List and exclude",
                    ],
                    default="No prior IP",
                    learn_more=(
                        "If a founder has existing code, patents, or designs that the company "
                        "will use, this must be clearly documented. The company should get at "
                        "minimum a perpetual, royalty-free license."
                    ),
                    preview_template="Regarding prior intellectual property: {value}.",
                ),
                _clause(
                    "improvements_to_prior_ip", "Improvements to Prior IP", "dropdown",
                    "Who owns improvements made to a founder's prior IP during company work.",
                    options=[
                        "Company owns all improvements",
                        "Founder retains improvements",
                        "Shared ownership",
                    ],
                    default="Company owns all improvements",
                    common_choice_label="Most startups choose: Company owns all improvements",
                    preview_template="Improvements to prior IP shall be owned as follows: {value}.",
                ),
            ],
        }

    # -- Step 6 -------------------------------------------------------------

    @staticmethod
    def _fa_step6_restrictive_covenants() -> dict:
        return {
            "step_number": 6,
            "title": "Restrictive Covenants",
            "description": "Non-compete, non-solicitation, and confidentiality terms.",
            "clauses": [
                _clause(
                    "non_compete_enabled", "Non-Compete Clause", "toggle",
                    "Whether founders agree not to work for competitors during and after leaving.",
                    default=True,
                    learn_more=(
                        "Non-compete clauses restrict a founder from starting or joining a "
                        "competing business. During the agreement, this is standard. "
                        "Post-termination non-competes are tricky in India."
                    ),
                    india_note=(
                        "IMPORTANT: Section 27 of the Indian Contract Act 1872 makes "
                        "post-employment non-compete agreements generally VOID and unenforceable "
                        "in India. Unlike the US/UK, you cannot enforce a non-compete after "
                        "someone leaves. However, non-competes DURING employment/engagement are "
                        "valid. Courts may enforce narrowly drafted non-solicitation clauses."
                    ),
                    common_choice_label="Standard: Yes (during tenure)",
                    preview_template="Non-compete obligations: {value}.",
                ),
                _clause(
                    "non_compete_duration", "Non-Compete Duration", "dropdown",
                    "How long the non-compete lasts after a founder leaves.",
                    options=[
                        "During tenure only",
                        "6 months post-exit",
                        "1 year post-exit",
                        "2 years post-exit",
                    ],
                    default="During tenure only",
                    india_note=(
                        "Remember: Post-termination non-compete is generally unenforceable "
                        "under Section 27 of the Indian Contract Act. Include it for deterrent "
                        "value but do not rely on it legally."
                    ),
                    depends_on="non_compete_enabled",
                    preview_template="The non-compete restriction shall apply: {value}.",
                ),
                _clause(
                    "non_solicit_enabled", "Non-Solicitation Clause", "toggle",
                    "Whether founders agree not to poach employees or clients after leaving.",
                    default=True,
                    learn_more=(
                        "Non-solicitation prevents departing founders from taking employees or "
                        "clients with them. Unlike non-compete, Indian courts have been more "
                        "willing to enforce reasonable non-solicitation clauses."
                    ),
                    common_choice_label="Highly recommended: Yes",
                    preview_template="Non-solicitation obligations: {value}.",
                ),
                _clause(
                    "confidentiality_duration", "Confidentiality Duration", "dropdown",
                    "How long confidentiality obligations last after a founder leaves.",
                    options=["2 years", "5 years", "Perpetual"],
                    default="Perpetual",
                    common_choice_label="Standard: Perpetual for trade secrets, 2-5 years for other info",
                    preview_template="Confidentiality obligations shall survive for: {value}.",
                ),
            ],
        }

    # -- Step 7 -------------------------------------------------------------

    @staticmethod
    def _fa_step7_exit() -> dict:
        return {
            "step_number": 7,
            "title": "Exit & Separation",
            "description": "What happens when a founder leaves or wants to sell shares.",
            "clauses": [
                _clause(
                    "good_leaver_bad_leaver", "Good Leaver / Bad Leaver", "toggle",
                    "Whether departing founders are treated differently based on why they left.",
                    default=True,
                    learn_more=(
                        "Good leaver (resignation for personal reasons, death, disability): "
                        "keeps vested shares at fair market value. Bad leaver (fired for cause, "
                        "competing business, breach): loses unvested shares AND may have to sell "
                        "vested shares at par/nominal value. This is the most important "
                        "protection for remaining founders."
                    ),
                    pros=[
                        "Protects against bad faith departures",
                        "Standard in investor agreements",
                        "Fair to remaining founders",
                    ],
                    cons=[
                        "Can be subjective — who defines 'cause'?",
                        "May discourage founders from leaving even when they should",
                    ],
                    common_choice_label="Strongly recommended: Yes",
                    preview_template="Good leaver / bad leaver provisions: {value}.",
                ),
                _clause(
                    "voluntary_exit_notice", "Voluntary Exit Notice Period", "dropdown",
                    "How much notice a founder must give before leaving.",
                    options=["30 days", "60 days", "90 days", "180 days"],
                    default="90 days",
                    common_choice_label="Standard: 90 days",
                    preview_template="A departing founder must provide {value} written notice.",
                ),
                _clause(
                    "share_transfer_restriction", "Share Transfer Restrictions", "dropdown",
                    "What happens when a founder wants to sell their shares.",
                    options=[
                        "Right of First Refusal",
                        "Tag-along and Drag-along",
                        "Board approval required",
                        "All of the above",
                    ],
                    default="All of the above",
                    learn_more=(
                        "ROFR (Right of First Refusal): Other founders get first chance to buy. "
                        "Tag-along: If one founder sells, others can join the sale on same terms. "
                        "Drag-along: If majority sells, they can force minority to sell too. "
                        "These protect both majority and minority shareholders."
                    ),
                    india_note=(
                        "For Private Limited companies, Section 2(68) of Companies Act 2013 "
                        "requires restrictions on share transfer. This is actually mandated by "
                        "law, so you must have some transfer restrictions."
                    ),
                    common_choice_label="Most comprehensive: All of the above",
                    preview_template="Share transfer restrictions: {value}.",
                ),
                _clause(
                    "deadlock_resolution", "Deadlock Resolution", "dropdown",
                    "How to resolve situations where founders cannot agree.",
                    options=[
                        "Mediator",
                        "Arbitration",
                        "Shotgun clause",
                        "Step-up buyout",
                    ],
                    default="Mediator",
                    learn_more=(
                        "Shotgun clause (Texas Shootout): One founder names a price, the other "
                        "must either buy at that price or sell at that price. This is dramatic "
                        "but effective. Arbitration: A neutral third party decides. "
                        "Mediation: A mediator helps negotiate. Step-up buyout: Sealed bids, "
                        "highest bidder buys out the other."
                    ),
                    india_note=(
                        "Arbitration in India is governed by the Arbitration and Conciliation "
                        "Act, 1996. Mumbai, Delhi, and Bangalore are common seats of arbitration. "
                        "Institutional arbitration (SIAC, ICC) is preferred for higher-value disputes."
                    ),
                    common_choice_label="Most practical: Mediation first, then Arbitration",
                    preview_template="Deadlock resolution mechanism: {value}.",
                ),
            ],
        }

    # -- Step 8 -------------------------------------------------------------

    @staticmethod
    def _fa_step8_miscellaneous() -> dict:
        return {
            "step_number": 8,
            "title": "Miscellaneous",
            "description": "Governing law, dispute resolution, and amendment process.",
            "clauses": [
                _clause(
                    "governing_law", "Governing Law (State)", "dropdown",
                    "Which state's courts will have jurisdiction over disputes.",
                    options=[
                        "Maharashtra", "Karnataka", "Delhi",
                        "Tamil Nadu", "Telangana", "Other",
                    ],
                    default="Maharashtra",
                    learn_more=(
                        "Choose the state where your company is registered or where most "
                        "founders are based. This determines which courts handle disputes."
                    ),
                    common_choice_label="Most choose: State of company registration",
                    preview_template="This agreement shall be governed by the laws of the State of {value}.",
                ),
                _clause(
                    "dispute_resolution", "Dispute Resolution", "dropdown",
                    "How disputes under this agreement will be resolved.",
                    options=[
                        "Courts only",
                        "Arbitration",
                        "Mediation then Arbitration",
                    ],
                    default="Mediation then Arbitration",
                    common_choice_label="Most effective: Mediation then Arbitration",
                    preview_template="Disputes shall be resolved through: {value}.",
                ),
                _clause(
                    "amendment_process", "Amendment Process", "dropdown",
                    "How this agreement can be changed in the future.",
                    options=[
                        "Unanimous written consent",
                        "Majority consent",
                        "Board resolution",
                    ],
                    default="Unanimous written consent",
                    common_choice_label="Standard: Unanimous written consent",
                    preview_template="This agreement may be amended by: {value}.",
                ),
                _clause(
                    "termination_events", "Termination Events", "multi_select",
                    "Events that automatically terminate this agreement.",
                    options=[
                        "Mutual written agreement",
                        "Material breach uncured for 30 days",
                        "Insolvency of a founder",
                        "Company dissolution",
                        "IPO or acquisition",
                    ],
                    default=[
                        "Mutual written agreement",
                        "Material breach uncured for 30 days",
                        "Company dissolution",
                    ],
                    preview_template="This agreement shall terminate upon: {value}.",
                ),
            ],
        }

    # ======================================================================
    # TEMPLATE 2: NDA
    # ======================================================================

    def _nda(self) -> dict:
        return {
            "name": "Non-Disclosure Agreement (NDA)",
            "description": (
                "Protect confidential information when sharing with potential "
                "investors, partners, contractors, or employees."
            ),
            "category": "Startup Essentials",
            "steps": [
                self._nda_step1_parties(),
                self._nda_step2_scope(),
                self._nda_step3_obligations(),
                self._nda_step4_general(),
            ],
        }

    @staticmethod
    def _nda_step1_parties() -> dict:
        return {
            "step_number": 1,
            "title": "Parties & Type",
            "description": "Who is involved and what kind of NDA is this.",
            "clauses": [
                _clause(
                    "nda_type", "NDA Type", "dropdown",
                    "Whether both parties share confidential info, or just one.",
                    options=[
                        "Mutual",
                        "One-way - I am disclosing",
                        "One-way - I am receiving",
                    ],
                    default="Mutual",
                    learn_more=(
                        "Mutual NDAs are used between two companies exploring a partnership or "
                        "deal. One-way NDAs are for when you are sharing your idea with potential "
                        "investors, contractors, or partners."
                    ),
                    common_choice_label="For investors/partners: One-way (you disclose)",
                    preview_template="This is a {value} Non-Disclosure Agreement.",
                ),
                _clause(
                    "disclosing_party_name", "Disclosing Party Name", "text",
                    "Name of the party sharing confidential information.",
                    preview_template="Disclosing Party: {value}.",
                ),
                _clause(
                    "disclosing_party_type", "Disclosing Party Type", "dropdown",
                    "Legal entity type of the disclosing party.",
                    options=["Individual", "Company", "LLP"],
                    default="Company",
                ),
                _clause(
                    "receiving_party_name", "Receiving Party Name", "text",
                    "Name of the party receiving confidential information.",
                    preview_template="Receiving Party: {value}.",
                ),
                _clause(
                    "receiving_party_type", "Receiving Party Type", "dropdown",
                    "Legal entity type of the receiving party.",
                    options=["Individual", "Company", "LLP"],
                    default="Company",
                ),
                _clause(
                    "purpose", "Purpose", "textarea",
                    "The specific purpose for which confidential information will be shared.",
                    preview_template="The confidential information is disclosed for the purpose of: {value}.",
                ),
            ],
        }

    @staticmethod
    def _nda_step2_scope() -> dict:
        return {
            "step_number": 2,
            "title": "Scope of Confidential Information",
            "description": "What information is covered and what is excluded.",
            "clauses": [
                _clause(
                    "confidential_info_definition", "Confidential Information", "multi_select",
                    "What types of information are considered confidential.",
                    options=[
                        "Technical data & source code",
                        "Business plans & strategies",
                        "Financial information",
                        "Customer & vendor lists",
                        "Trade secrets & know-how",
                        "Marketing plans",
                        "Product roadmaps",
                        "Employee information",
                    ],
                    default=[
                        "Technical data & source code",
                        "Business plans & strategies",
                        "Financial information",
                        "Trade secrets & know-how",
                    ],
                    preview_template="Confidential Information shall include: {value}.",
                ),
                _clause(
                    "exclusions", "Standard Exclusions", "multi_select",
                    "Standard exclusions from confidentiality obligations.",
                    options=[
                        "Publicly available information",
                        "Already known to recipient",
                        "Independently developed",
                        "Received from third party without restriction",
                        "Required by law/court order",
                    ],
                    default=[
                        "Publicly available information",
                        "Already known to recipient",
                        "Independently developed",
                        "Received from third party without restriction",
                        "Required by law/court order",
                    ],
                    common_choice_label="Standard: Select all exclusions",
                    preview_template="Exclusions from confidentiality: {value}.",
                ),
            ],
        }

    @staticmethod
    def _nda_step3_obligations() -> dict:
        return {
            "step_number": 3,
            "title": "Obligations & Remedies",
            "description": "Duration, permitted disclosures, and legal remedies.",
            "clauses": [
                _clause(
                    "confidentiality_period", "Confidentiality Period", "dropdown",
                    "How long the receiving party must keep information confidential.",
                    options=[
                        "1 year", "2 years", "3 years", "5 years",
                        "Until info becomes public",
                    ],
                    default="3 years",
                    common_choice_label="Standard: 2-3 years",
                    preview_template="Confidentiality obligations shall survive for {value} after disclosure.",
                ),
                _clause(
                    "permitted_disclosures", "Permitted Disclosures", "multi_select",
                    "Who the recipient can share confidential info with.",
                    options=[
                        "Employees with need-to-know",
                        "Legal advisors",
                        "Accountants/auditors",
                        "Potential investors (under sub-NDA)",
                        "Board members",
                    ],
                    default=[
                        "Employees with need-to-know",
                        "Legal advisors",
                    ],
                    preview_template="Permitted disclosures: {value}.",
                ),
                _clause(
                    "return_of_materials", "Return of Materials", "toggle",
                    "Whether the recipient must return/destroy confidential materials after the agreement ends.",
                    default=True,
                    common_choice_label="Recommended: Yes",
                    preview_template="Return/destruction of materials upon termination: {value}.",
                ),
                _clause(
                    "remedies", "Remedies for Breach", "dropdown",
                    "What legal remedies are available if the NDA is breached.",
                    options=[
                        "Injunctive relief only",
                        "Injunctive relief + damages",
                        "Liquidated damages",
                    ],
                    default="Injunctive relief + damages",
                    india_note=(
                        "Indian courts can grant injunctive relief (court orders to stop "
                        "disclosure) under Order XXXIX of the Code of Civil Procedure. "
                        "Specific Relief Act 1963 also allows specific performance."
                    ),
                    preview_template="Remedies for breach: {value}.",
                ),
            ],
        }

    @staticmethod
    def _nda_step4_general() -> dict:
        return {
            "step_number": 4,
            "title": "General Terms",
            "description": "Governing law, dispute resolution, and term of the NDA.",
            "clauses": [
                _clause(
                    "governing_law_nda", "Governing Law", "dropdown",
                    "Which state's laws govern this NDA.",
                    options=[
                        "Maharashtra", "Karnataka", "Delhi",
                        "Tamil Nadu", "Telangana",
                    ],
                    default="Maharashtra",
                    preview_template="This NDA shall be governed by the laws of the State of {value}.",
                ),
                _clause(
                    "dispute_resolution_nda", "Dispute Resolution", "dropdown",
                    "How disputes under this NDA will be resolved.",
                    options=["Courts", "Arbitration", "Mediation then Arbitration"],
                    default="Arbitration",
                    preview_template="Disputes shall be resolved through: {value}.",
                ),
                _clause(
                    "term", "Term of NDA", "dropdown",
                    "How long this NDA remains in effect.",
                    options=[
                        "1 year", "2 years", "3 years",
                        "Until terminated by either party with 30 days notice",
                    ],
                    default="2 years",
                    preview_template="This NDA shall remain in effect for: {value}.",
                ),
            ],
        }

    # ======================================================================
    # TEMPLATE 3: EMPLOYMENT AGREEMENT
    # ======================================================================

    def _employment_agreement(self) -> dict:
        return {
            "name": "Employment Agreement",
            "description": (
                "A comprehensive employment agreement covering compensation, "
                "benefits, IP assignment, restrictive covenants, and termination "
                "terms. Tailored for Indian labour law."
            ),
            "category": "HR & Employment",
            "steps": [
                self._emp_step1_details(),
                self._emp_step2_compensation(),
                self._emp_step3_terms(),
                self._emp_step4_ip(),
                self._emp_step5_restrictive(),
                self._emp_step6_termination(),
            ],
        }

    @staticmethod
    def _emp_step1_details() -> dict:
        return {
            "step_number": 1,
            "title": "Employee Details",
            "description": "Basic information about the employee and their role.",
            "clauses": [
                _clause("employee_name", "Employee Name", "text",
                        "Full legal name of the employee.",
                        preview_template="Employee: {value}."),
                _clause("designation", "Designation", "text",
                        "Job title for the employee.",
                        preview_template="Designation: {value}."),
                _clause("department", "Department", "text",
                        "Department the employee will be part of.",
                        preview_template="Department: {value}."),
                _clause("reporting_to", "Reporting To", "text",
                        "Name and designation of the reporting manager.",
                        preview_template="Reporting to: {value}."),
                _clause(
                    "employment_type", "Employment Type", "dropdown",
                    "Type of employment arrangement.",
                    options=["Full-time", "Part-time", "Fixed-term contract"],
                    default="Full-time",
                    preview_template="Employment type: {value}.",
                ),
            ],
        }

    @staticmethod
    def _emp_step2_compensation() -> dict:
        return {
            "step_number": 2,
            "title": "Compensation",
            "description": "Salary structure, bonuses, and equity.",
            "clauses": [
                _clause(
                    "ctc", "Cost to Company (CTC)", "number",
                    "Cost to Company \u2014 total annual compensation in INR.",
                    india_note=(
                        "CTC in India typically includes: Basic salary (40-50% of CTC), HRA, "
                        "special allowance, PF employer contribution (12% of basic), gratuity "
                        "provision, and other benefits."
                    ),
                    min_value=0,
                    preview_template="The annual CTC shall be INR {value}.",
                ),
                _clause(
                    "salary_breakup", "Salary Breakup", "dropdown",
                    "How the CTC is broken down into components.",
                    options=["Standard Indian structure", "Custom"],
                    default="Standard Indian structure",
                    learn_more=(
                        "Standard structure: Basic (40-50%), HRA (40-50% of basic for metros, "
                        "30-40% for non-metros), Special Allowance (remaining), PF (12% of "
                        "basic), Gratuity (4.81% of basic)."
                    ),
                    preview_template="Salary structure: {value}.",
                ),
                _clause(
                    "bonus", "Bonus", "dropdown",
                    "Whether the employee receives any bonus.",
                    options=["No bonus", "Performance-based", "Fixed annual bonus", "Discretionary"],
                    default="Performance-based",
                    preview_template="Bonus: {value}.",
                ),
                _clause(
                    "equity_for_employee", "Employee Equity", "dropdown",
                    "Whether the employee receives stock options or equity.",
                    options=["No equity", "ESOP grant", "Sweat equity"],
                    default="No equity",
                    india_note=(
                        "ESOP in India is governed by Section 62(1)(b) of Companies Act 2013 "
                        "and SEBI ESOP Guidelines for listed companies. ESOPs must vest over "
                        "minimum 1 year. There are tax implications at exercise (perquisite tax) "
                        "and sale (capital gains)."
                    ),
                    preview_template="Equity component: {value}.",
                ),
            ],
        }

    @staticmethod
    def _emp_step3_terms() -> dict:
        return {
            "step_number": 3,
            "title": "Terms of Employment",
            "description": "Probation, notice period, working hours, and leave.",
            "clauses": [
                _clause(
                    "probation_period", "Probation Period", "dropdown",
                    "Trial period during which either party can terminate with shorter notice.",
                    options=["No probation", "3 months", "6 months"],
                    default="6 months",
                    common_choice_label="Standard in India: 6 months",
                    preview_template="Probation period: {value}.",
                ),
                _clause(
                    "notice_period", "Notice Period", "dropdown",
                    "Notice required before resignation or termination.",
                    options=["15 days", "1 month", "2 months", "3 months"],
                    default="2 months",
                    common_choice_label="Standard: 1-2 months",
                    india_note=(
                        "In India, notice periods can be bought out (payment in lieu of notice). "
                        "Standard practice ranges from 1-3 months depending on seniority."
                    ),
                    preview_template="Notice period: {value}.",
                ),
                _clause(
                    "working_hours", "Working Hours", "dropdown",
                    "Expected working hours.",
                    options=[
                        "Standard (9 hours/day, 48 hours/week)",
                        "Flexible",
                    ],
                    default="Standard (9 hours/day, 48 hours/week)",
                    india_note=(
                        "Under the Shops and Establishments Act (varies by state), working hours "
                        "are capped. The Factories Act limits to 48 hours/week. IT/ITES companies "
                        "often have exemptions for flexible hours."
                    ),
                    preview_template="Working hours: {value}.",
                ),
                _clause(
                    "leave_policy", "Leave Policy", "dropdown",
                    "Annual leave entitlement.",
                    options=[
                        "As per company policy",
                        "12 casual + 12 sick + 15 earned",
                        "Custom",
                    ],
                    default="As per company policy",
                    india_note=(
                        "Under state Shops & Establishments Acts, employees are entitled to "
                        "minimum earned/privilege leave (typically 1 day per 20 days worked). "
                        "National and festival holidays are mandatory."
                    ),
                    preview_template="Leave policy: {value}.",
                ),
            ],
        }

    @staticmethod
    def _emp_step4_ip() -> dict:
        return {
            "step_number": 4,
            "title": "IP & Confidentiality",
            "description": "Intellectual property ownership and confidentiality obligations.",
            "clauses": [
                _clause(
                    "ip_ownership_employment", "IP Ownership", "dropdown",
                    "Ownership of intellectual property created during employment.",
                    options=[
                        "All work IP belongs to company",
                        "Company owns work-related IP only",
                    ],
                    default="All work IP belongs to company",
                    india_note=(
                        "Under Indian Copyright Act, work created in the course of employment "
                        "belongs to the employer (Section 17(c)). However, an explicit clause "
                        "strengthens this."
                    ),
                    common_choice_label="Standard: All work IP to company",
                    preview_template="IP ownership: {value}.",
                ),
                _clause(
                    "confidentiality_employment", "Confidentiality Obligations", "toggle",
                    "Whether the employee signs confidentiality obligations.",
                    default=True,
                    common_choice_label="Essential: Yes",
                    preview_template="Confidentiality obligations: {value}.",
                ),
                _clause(
                    "invention_disclosure", "Invention Disclosure", "toggle",
                    "Whether the employee must disclose all inventions made during employment.",
                    default=True,
                    common_choice_label="Recommended: Yes",
                    preview_template="Invention disclosure requirement: {value}.",
                ),
            ],
        }

    @staticmethod
    def _emp_step5_restrictive() -> dict:
        return {
            "step_number": 5,
            "title": "Restrictive Covenants",
            "description": "Non-compete and non-solicitation restrictions.",
            "clauses": [
                _clause(
                    "non_compete_employment", "Non-Compete", "toggle",
                    "Whether the employee agrees not to join competitors.",
                    default=True,
                    india_note=(
                        "REMINDER: Post-employment non-compete is unenforceable in India under "
                        "Section 27 of Indian Contract Act 1872. Include for deterrent value "
                        "only. Non-compete DURING employment is enforceable."
                    ),
                    preview_template="Non-compete: {value}.",
                ),
                _clause(
                    "non_solicit_employment", "Non-Solicitation", "toggle",
                    "Whether the employee agrees not to poach co-workers or clients.",
                    default=True,
                    common_choice_label="Recommended: Yes",
                    preview_template="Non-solicitation: {value}.",
                ),
                _clause(
                    "non_solicit_duration_employment", "Non-Solicitation Duration", "dropdown",
                    "Duration of non-solicitation after leaving.",
                    options=["6 months", "1 year", "2 years"],
                    default="1 year",
                    depends_on="non_solicit_employment",
                    preview_template="Non-solicitation duration: {value} post-employment.",
                ),
            ],
        }

    @staticmethod
    def _emp_step6_termination() -> dict:
        return {
            "step_number": 6,
            "title": "Termination",
            "description": "Grounds for termination, severance, and gratuity.",
            "clauses": [
                _clause(
                    "termination_for_cause", "Termination for Cause", "multi_select",
                    "Grounds for immediate termination without notice.",
                    options=[
                        "Fraud or dishonesty",
                        "Material breach of agreement",
                        "Conviction of criminal offense",
                        "Repeated performance failures",
                        "Breach of confidentiality",
                        "Insubordination",
                    ],
                    default=[
                        "Fraud or dishonesty",
                        "Material breach of agreement",
                        "Breach of confidentiality",
                    ],
                    preview_template="Termination for cause grounds: {value}.",
                ),
                _clause(
                    "severance", "Severance Pay", "dropdown",
                    "Payment made to employee upon termination.",
                    options=[
                        "No severance",
                        "1 month salary",
                        "As per policy",
                        "Negotiable",
                    ],
                    default="No severance",
                    india_note=(
                        "Under the Industrial Disputes Act, workmen (earning below "
                        "\u20b918,000/month) are entitled to retrenchment compensation of "
                        "15 days' average pay for every completed year of service. "
                        "Managers/executives rely on contractual severance."
                    ),
                    preview_template="Severance: {value}.",
                ),
                _clause(
                    "gratuity_mention", "Gratuity Mention", "toggle",
                    "Whether to explicitly mention gratuity eligibility.",
                    default=True,
                    india_note=(
                        "Under the Payment of Gratuity Act, employees completing 5+ years "
                        "are entitled to gratuity: 15 days' wages x years of service. This is "
                        "mandatory by law for establishments with 10+ employees."
                    ),
                    preview_template="Gratuity provisions: {value}.",
                ),
            ],
        }

    # ======================================================================
    # TEMPLATE 4: CONSULTANCY AGREEMENT
    # ======================================================================

    def _consultancy_agreement(self) -> dict:
        return {
            "name": "Consultancy Agreement",
            "description": (
                "Engage consultants and freelancers with clear terms covering "
                "scope, payment, IP ownership, confidentiality, and termination."
            ),
            "category": "HR & Employment",
            "steps": [
                self._con_step1_parties(),
                self._con_step2_payment(),
                self._con_step3_ip(),
                self._con_step4_confidentiality(),
                self._con_step5_termination(),
            ],
        }

    @staticmethod
    def _con_step1_parties() -> dict:
        return {
            "step_number": 1,
            "title": "Parties & Scope",
            "description": "Who is involved and what work will be done.",
            "clauses": [
                _clause("consultant_name", "Consultant Name", "text",
                        "Full legal name of the consultant or consulting entity.",
                        preview_template="Consultant: {value}."),
                _clause(
                    "consultant_type", "Consultant Type", "dropdown",
                    "Legal entity type of the consultant.",
                    options=["Individual", "Company", "LLP"],
                    default="Individual",
                    preview_template="Consultant entity type: {value}.",
                ),
                _clause("scope_of_work", "Scope of Work", "textarea",
                        "Detailed description of the services to be provided.",
                        preview_template="Scope of work: {value}."),
                _clause("deliverables", "Deliverables", "textarea",
                        "Specific deliverables expected from the consultant.",
                        preview_template="Deliverables: {value}."),
                _clause("start_date", "Start Date", "date",
                        "Date the engagement begins.",
                        preview_template="Engagement starts on: {value}."),
                _clause("end_date", "End Date", "date",
                        "Date the engagement ends (leave blank for ongoing).",
                        required=False,
                        preview_template="Engagement ends on: {value}."),
            ],
        }

    @staticmethod
    def _con_step2_payment() -> dict:
        return {
            "step_number": 2,
            "title": "Payment",
            "description": "How and when the consultant will be paid.",
            "clauses": [
                _clause(
                    "payment_type", "Payment Type", "dropdown",
                    "How the consultant will be paid.",
                    options=["Fixed fee", "Hourly rate", "Milestone-based", "Retainer"],
                    default="Fixed fee",
                    preview_template="Payment type: {value}.",
                ),
                _clause(
                    "payment_amount", "Payment Amount (INR)", "number",
                    "Amount in INR (per hour, per month, or total \u2014 depending on payment type).",
                    min_value=0,
                    preview_template="Payment amount: INR {value}.",
                ),
                _clause(
                    "payment_schedule", "Payment Schedule", "dropdown",
                    "When payments are due.",
                    options=[
                        "Monthly",
                        "On milestone completion",
                        "Upon delivery",
                        "50% advance + 50% on completion",
                    ],
                    default="Monthly",
                    preview_template="Payment schedule: {value}.",
                ),
                _clause(
                    "invoicing", "Invoicing", "dropdown",
                    "How invoicing works.",
                    options=["Consultant invoices", "Auto-generated"],
                    default="Consultant invoices",
                    india_note=(
                        "Consultants must issue GST invoices if their turnover exceeds "
                        "\u20b920 lakhs (\u20b910 lakhs for special category states). TDS at 10% "
                        "under Section 194J applies to professional/technical services fees."
                    ),
                    preview_template="Invoicing method: {value}.",
                ),
            ],
        }

    @staticmethod
    def _con_step3_ip() -> dict:
        return {
            "step_number": 3,
            "title": "IP & Deliverables",
            "description": "Who owns the work product.",
            "clauses": [
                _clause(
                    "ip_ownership_consultancy", "IP Ownership", "dropdown",
                    "Who owns the intellectual property created during the engagement.",
                    options=[
                        "All IP to client",
                        "Joint ownership",
                        "Consultant retains, client gets license",
                    ],
                    default="All IP to client",
                    learn_more=(
                        "For consultants (unlike employees), IP does NOT automatically belong "
                        "to the hiring company under Indian law. You MUST have an explicit "
                        "assignment clause."
                    ),
                    india_note=(
                        "Unlike employment, there is no automatic copyright assignment for "
                        "commissioned work under Indian Copyright Act (except for certain "
                        "categories like photographs, paintings). An explicit written assignment "
                        "is essential."
                    ),
                    common_choice_label="Recommended: All IP to client",
                    preview_template="IP ownership: {value}.",
                ),
                _clause(
                    "existing_tools", "Pre-existing Tools", "dropdown",
                    "What happens to consultant's pre-existing tools, libraries, or frameworks used in the project.",
                    options=[
                        "Consultant retains rights to pre-existing tools",
                        "All tools become client property",
                    ],
                    default="Consultant retains rights to pre-existing tools",
                    common_choice_label="Fair: Consultant retains pre-existing tools, grants license",
                    preview_template="Pre-existing tools: {value}.",
                ),
            ],
        }

    @staticmethod
    def _con_step4_confidentiality() -> dict:
        return {
            "step_number": 4,
            "title": "Confidentiality & Restrictions",
            "description": "Confidentiality, non-compete, and exclusivity.",
            "clauses": [
                _clause(
                    "confidentiality_consultancy", "Confidentiality", "toggle",
                    "Whether the consultant has confidentiality obligations.",
                    default=True,
                    common_choice_label="Essential: Yes",
                    preview_template="Confidentiality obligations: {value}.",
                ),
                _clause(
                    "non_compete_consultancy", "Non-Compete", "toggle",
                    "Whether the consultant is restricted from working with competitors.",
                    default=False,
                    india_note=(
                        "Section 27 restrictions apply. During engagement is enforceable; "
                        "post-engagement is not."
                    ),
                    preview_template="Non-compete restriction: {value}.",
                ),
                _clause(
                    "exclusivity", "Exclusivity", "toggle",
                    "Whether the consultant works exclusively for you or can take other clients.",
                    default=False,
                    preview_template="Exclusivity: {value}.",
                ),
            ],
        }

    @staticmethod
    def _con_step5_termination() -> dict:
        return {
            "step_number": 5,
            "title": "Termination & Liability",
            "description": "Notice period, liability cap, and indemnification.",
            "clauses": [
                _clause(
                    "termination_notice_consultancy", "Termination Notice", "dropdown",
                    "Notice period for termination by either party.",
                    options=["7 days", "15 days", "30 days", "60 days"],
                    default="30 days",
                    common_choice_label="Standard: 30 days",
                    preview_template="Termination notice period: {value}.",
                ),
                _clause(
                    "liability_cap", "Liability Cap", "dropdown",
                    "Maximum liability for either party.",
                    options=[
                        "Total fees paid",
                        "2x fees paid",
                        "No cap",
                        "Custom amount",
                    ],
                    default="Total fees paid",
                    common_choice_label="Standard: Total fees paid",
                    preview_template="Liability cap: {value}.",
                ),
                _clause(
                    "indemnification", "Indemnification", "toggle",
                    "Whether the consultant indemnifies the client against third-party claims.",
                    default=True,
                    learn_more=(
                        "Indemnification means the consultant will compensate you for losses "
                        "caused by their work \u2014 e.g., if they deliver code that infringes "
                        "someone's patent, they cover the damages."
                    ),
                    common_choice_label="Recommended: Yes",
                    preview_template="Indemnification: {value}.",
                ),
            ],
        }

    # ======================================================================
    # HTML RENDERING
    # ======================================================================

    @staticmethod
    def _base_html_wrap(title: str, body_html: str, date_str: str = "") -> str:
        """Wrap body content in the base legal document HTML shell."""
        tpl = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ title }}</title>
<style>
@page { size: A4; margin: 25mm 20mm; }
body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #1a1a1a;
    max-width: 210mm;
    margin: 0 auto;
    padding: 20mm;
}
h1 {
    font-family: "Helvetica Neue", Arial, sans-serif;
    text-align: center;
    font-size: 18pt;
    margin-bottom: 4px;
    color: #111;
}
h2 {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 13pt;
    margin-top: 28px;
    margin-bottom: 8px;
    color: #222;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
}
h3 {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    margin-top: 16px;
    margin-bottom: 4px;
    color: #333;
}
.doc-date {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 24px;
}
.clause {
    margin-bottom: 12px;
    text-align: justify;
}
.clause-number {
    font-weight: bold;
}
.signature-block {
    margin-top: 48px;
    page-break-inside: avoid;
}
.signature-line {
    display: inline-block;
    width: 45%;
    margin-top: 40px;
    vertical-align: top;
}
.signature-line .line {
    border-bottom: 1px solid #333;
    height: 1px;
    margin-bottom: 6px;
    width: 90%;
}
.signature-line p {
    margin: 2px 0;
    font-size: 10pt;
    color: #444;
}
ol { padding-left: 24px; }
ol li { margin-bottom: 6px; }
.disclaimer {
    margin-top: 32px;
    padding: 12px;
    background: #f9f9f9;
    border: 1px solid #ddd;
    font-size: 9pt;
    color: #666;
}
</style>
</head>
<body>
<h1>{{ title }}</h1>
{% if date_str %}<p class="doc-date">Date: {{ date_str }}</p>{% endif %}
{{ body_html }}
<div class="disclaimer">
<strong>Disclaimer:</strong> This document is generated as a template and does not
constitute legal advice. Please have this document reviewed by a qualified legal
professional before execution.
</div>
</body>
</html>""")
        return tpl.render(title=title, body_html=body_html, date_str=date_str)

    # -- Founder Agreement renderer -----------------------------------------

    def _render_founder_agreement(
        self, tpl: dict, config: dict, parties: dict
    ) -> str:
        company = config.get("company_name", "[Company Name]")
        date_str = config.get("effective_date", "")
        num = config.get("num_founders", 2)
        co_type = config.get("company_type", "Private Limited")

        sections: List[str] = []
        clause_num = 0

        # Section 1 — Preamble
        clause_num += 1
        sections.append(
            f'<h2>{clause_num}. Preamble</h2>'
            f'<p class="clause">This Co-Founder Agreement ("Agreement") is entered into '
            f'as of {date_str or "[Date]"} by and between {num} co-founders '
            f'(collectively, the "Founders") of <strong>{company}</strong>, '
            f'a {co_type} company incorporated / to be incorporated under the laws of India.</p>'
        )

        # Section 2 — Equity
        clause_num += 1
        equity = config.get("equity_split", "as mutually agreed")
        share_class = config.get("share_class", "Equity Shares")
        capital = config.get("capital_contribution", "Equal")
        sections.append(
            f'<h2>{clause_num}. Equity & Ownership</h2>'
            f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
            f'The equity among the Founders shall be divided as: {equity}.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.2</span> '
            f'The Company shall issue {share_class} to the Founders.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.3</span> '
            f'The initial capital contribution shall be {capital} among the Founders.</p>'
        )

        # Section 3 — Vesting
        clause_num += 1
        vesting_html = f'<h2>{clause_num}. Vesting</h2>'
        if config.get("vesting_enabled"):
            vp = config.get("vesting_period", "4 years")
            cliff = config.get("cliff_period", "1 year")
            accel = config.get("acceleration_on_exit", "Double trigger")
            vesting_html += (
                f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
                f'Each Founder\'s equity shall be subject to vesting over a period of {vp}, '
                f'with a cliff period of {cliff}.</p>'
                f'<p class="clause"><span class="clause-number">{clause_num}.2</span> '
                f'Upon a Change of Control, vesting acceleration shall be: {accel}.</p>'
            )
        else:
            vesting_html += (
                f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
                f'Founder equity shall not be subject to vesting and shall vest '
                f'immediately upon allotment.</p>'
            )
        sections.append(vesting_html)

        # Section 4 — Roles
        clause_num += 1
        tc = config.get("time_commitment", "Full-time")
        dm = config.get("decision_making", "CEO decides day-to-day with board for major decisions")
        sections.append(
            f'<h2>{clause_num}. Roles & Responsibilities</h2>'
            f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
            f'Each Founder shall serve in the capacity as mutually agreed and as set '
            f'out in Schedule A hereto.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.2</span> '
            f'Each Founder shall commit on a {tc} basis to the Company.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.3</span> '
            f'Decision-making process: {dm}.</p>'
        )

        # Section 5 — IP
        clause_num += 1
        ip = config.get("ip_assignment", "All IP to company")
        prior = config.get("prior_ip", "No prior IP")
        improvements = config.get("improvements_to_prior_ip", "Company owns all improvements")
        sections.append(
            f'<h2>{clause_num}. Intellectual Property</h2>'
            f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
            f'IP assignment: {ip}. Each Founder hereby irrevocably assigns to the Company '
            f'all right, title, and interest in any Intellectual Property created in '
            f'connection with the Company\'s business.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.2</span> '
            f'Prior IP: {prior}.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.3</span> '
            f'Improvements to prior IP: {improvements}.</p>'
        )

        # Section 6 — Restrictive Covenants
        clause_num += 1
        rc_html = f'<h2>{clause_num}. Restrictive Covenants</h2>'
        if config.get("non_compete_enabled"):
            ncd = config.get("non_compete_duration", "During tenure only")
            rc_html += (
                f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
                f'Each Founder agrees not to engage in any Competing Business: {ncd}.</p>'
            )
        if config.get("non_solicit_enabled", True):
            rc_html += (
                f'<p class="clause"><span class="clause-number">{clause_num}.2</span> '
                f'Each Founder agrees not to solicit employees, clients, or customers of '
                f'the Company for a period after departure.</p>'
            )
        cd = config.get("confidentiality_duration", "Perpetual")
        rc_html += (
            f'<p class="clause"><span class="clause-number">{clause_num}.3</span> '
            f'Confidentiality obligations shall survive for: {cd}.</p>'
        )
        sections.append(rc_html)

        # Section 7 — Exit
        clause_num += 1
        notice = config.get("voluntary_exit_notice", "90 days")
        transfer = config.get("share_transfer_restriction", "All of the above")
        deadlock = config.get("deadlock_resolution", "Mediator")
        exit_html = f'<h2>{clause_num}. Exit & Separation</h2>'
        if config.get("good_leaver_bad_leaver"):
            exit_html += (
                f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
                f'Good Leaver / Bad Leaver provisions shall apply. A Good Leaver shall '
                f'retain vested shares at fair market value. A Bad Leaver shall forfeit '
                f'unvested shares and may be required to transfer vested shares at par value.</p>'
            )
        exit_html += (
            f'<p class="clause"><span class="clause-number">{clause_num}.2</span> '
            f'A departing Founder shall provide {notice} written notice.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.3</span> '
            f'Share transfer restrictions: {transfer}.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.4</span> '
            f'Deadlock resolution: {deadlock}.</p>'
        )
        sections.append(exit_html)

        # Section 8 — Miscellaneous
        clause_num += 1
        gov = config.get("governing_law", "Maharashtra")
        dr = config.get("dispute_resolution", "Mediation then Arbitration")
        amend = config.get("amendment_process", "Unanimous written consent")
        events = config.get("termination_events", [])
        events_str = ", ".join(events) if isinstance(events, list) else str(events)
        sections.append(
            f'<h2>{clause_num}. General Provisions</h2>'
            f'<p class="clause"><span class="clause-number">{clause_num}.1</span> '
            f'This Agreement shall be governed by the laws of the State of {gov}, India.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.2</span> '
            f'Dispute resolution: {dr}.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.3</span> '
            f'This Agreement may be amended by: {amend}.</p>'
            f'<p class="clause"><span class="clause-number">{clause_num}.4</span> '
            f'This Agreement shall terminate upon: {events_str}.</p>'
        )

        # Signature block
        sig_lines = ""
        for i in range(1, num + 1):
            sig_lines += (
                f'<div class="signature-line">'
                f'<div class="line"></div>'
                f'<p><strong>Founder {i}</strong></p>'
                f'<p>Name: ________________________</p>'
                f'<p>Date: ________________________</p>'
                f'</div>\n'
            )
        sections.append(
            f'<div class="signature-block"><h2>Signatures</h2>'
            f'<p class="clause">IN WITNESS WHEREOF, the Founders have executed this '
            f'Agreement as of the date first written above.</p>{sig_lines}</div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap(
            f"Co-Founder Agreement \u2014 {company}", body, date_str
        )

    # -- NDA renderer -------------------------------------------------------

    def _render_nda(self, tpl: dict, config: dict, parties: dict) -> str:
        nda_type = config.get("nda_type", "Mutual")
        dp = config.get("disclosing_party_name", "[Disclosing Party]")
        dp_type = config.get("disclosing_party_type", "Company")
        rp = config.get("receiving_party_name", "[Receiving Party]")
        rp_type = config.get("receiving_party_type", "Company")
        purpose = config.get("purpose", "[Purpose]")
        gov = config.get("governing_law_nda", "Maharashtra")
        date_str = ""

        sections: List[str] = []
        cn = 0

        cn += 1
        sections.append(
            f'<h2>{cn}. Parties</h2>'
            f'<p class="clause">This {nda_type} Non-Disclosure Agreement is entered into between:</p>'
            f'<p class="clause"><strong>Disclosing Party:</strong> {dp} ({dp_type})</p>'
            f'<p class="clause"><strong>Receiving Party:</strong> {rp} ({rp_type})</p>'
            f'<p class="clause">For the purpose of: {purpose}.</p>'
        )

        cn += 1
        ci = config.get("confidential_info_definition", [])
        ci_str = ", ".join(ci) if isinstance(ci, list) else str(ci)
        excl = config.get("exclusions", [])
        excl_str = ", ".join(excl) if isinstance(excl, list) else str(excl)
        sections.append(
            f'<h2>{cn}. Confidential Information</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'"Confidential Information" means information relating to: {ci_str}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Confidential Information shall not include information that is: {excl_str}.</p>'
        )

        cn += 1
        period = config.get("confidentiality_period", "3 years")
        perm = config.get("permitted_disclosures", [])
        perm_str = ", ".join(perm) if isinstance(perm, list) else str(perm)
        rom = "shall" if config.get("return_of_materials", True) else "shall not be required to"
        remedies = config.get("remedies", "Injunctive relief + damages")
        sections.append(
            f'<h2>{cn}. Obligations</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Receiving Party shall maintain confidentiality for a period of {period}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Permitted disclosures: {perm_str}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Upon termination, the Receiving Party {rom} return or destroy all '
            f'confidential materials.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Remedies for breach: {remedies}.</p>'
        )

        cn += 1
        dr = config.get("dispute_resolution_nda", "Arbitration")
        term = config.get("term", "2 years")
        sections.append(
            f'<h2>{cn}. General Terms</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'This Agreement shall be governed by the laws of {gov}, India.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Disputes shall be resolved by: {dr}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'This Agreement shall remain in effect for: {term}.</p>'
        )

        sections.append(
            '<div class="signature-block"><h2>Signatures</h2>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>Disclosing Party:</strong> {dp}</p>'
            '<p>Date: ________________________</p></div>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>Receiving Party:</strong> {rp}</p>'
            '<p>Date: ________________________</p></div></div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap("Non-Disclosure Agreement", body, date_str)

    # -- Employment Agreement renderer --------------------------------------

    def _render_employment_agreement(
        self, tpl: dict, config: dict, parties: dict
    ) -> str:
        emp = config.get("employee_name", "[Employee Name]")
        desig = config.get("designation", "[Designation]")
        dept = config.get("department", "")
        reporting = config.get("reporting_to", "")
        emp_type = config.get("employment_type", "Full-time")
        company_name = parties.get("company_name", "[Company]")

        sections: List[str] = []
        cn = 0

        cn += 1
        sections.append(
            f'<h2>{cn}. Appointment</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'<strong>{company_name}</strong> ("Company") hereby appoints '
            f'<strong>{emp}</strong> ("Employee") as <strong>{desig}</strong>'
            f'{" in the " + dept + " department" if dept else ""}'
            f'{", reporting to " + reporting if reporting else ""}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Employment type: {emp_type}.</p>'
        )

        cn += 1
        ctc = config.get("ctc", 0)
        breakup = config.get("salary_breakup", "Standard Indian structure")
        bonus = config.get("bonus", "No bonus")
        equity = config.get("equity_for_employee", "No equity")
        sections.append(
            f'<h2>{cn}. Compensation</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Employee\'s annual Cost to Company (CTC) shall be INR {ctc:,}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Salary structure: {breakup}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Bonus: {bonus}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Equity: {equity}.</p>'
        )

        cn += 1
        prob = config.get("probation_period", "6 months")
        notice = config.get("notice_period", "2 months")
        hours = config.get("working_hours", "Standard (9 hours/day, 48 hours/week)")
        leave = config.get("leave_policy", "As per company policy")
        sections.append(
            f'<h2>{cn}. Terms of Employment</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Probation period: {prob}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Notice period: {notice}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Working hours: {hours}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Leave policy: {leave}.</p>'
        )

        cn += 1
        ip = config.get("ip_ownership_employment", "All work IP belongs to company")
        conf = "shall" if config.get("confidentiality_employment", True) else "shall not"
        inv = "shall" if config.get("invention_disclosure", True) else "shall not"
        sections.append(
            f'<h2>{cn}. Intellectual Property & Confidentiality</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'IP ownership: {ip}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Employee {conf} be bound by confidentiality obligations as set out herein.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The Employee {inv} be required to disclose all inventions made during employment.</p>'
        )

        cn += 1
        rc_html = f'<h2>{cn}. Restrictive Covenants</h2>'
        if config.get("non_compete_employment"):
            rc_html += (
                f'<p class="clause"><span class="clause-number">{cn}.1</span> '
                f'During the term of employment, the Employee shall not engage in any '
                f'Competing Business.</p>'
            )
        if config.get("non_solicit_employment"):
            dur = config.get("non_solicit_duration_employment", "1 year")
            rc_html += (
                f'<p class="clause"><span class="clause-number">{cn}.2</span> '
                f'The Employee shall not solicit employees or clients of the Company for '
                f'a period of {dur} after separation.</p>'
            )
        sections.append(rc_html)

        cn += 1
        causes = config.get("termination_for_cause", [])
        causes_str = "; ".join(causes) if isinstance(causes, list) else str(causes)
        sev = config.get("severance", "No severance")
        term_html = (
            f'<h2>{cn}. Termination</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Grounds for termination for cause: {causes_str}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Severance: {sev}.</p>'
        )
        if config.get("gratuity_mention"):
            term_html += (
                f'<p class="clause"><span class="clause-number">{cn}.3</span> '
                f'The Employee shall be eligible for gratuity in accordance with the '
                f'Payment of Gratuity Act, 1972, upon completing 5 years of continuous service.</p>'
            )
        sections.append(term_html)

        sections.append(
            '<div class="signature-block"><h2>Signatures</h2>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>For the Company:</strong></p>'
            '<p>Name: ________________________</p>'
            '<p>Date: ________________________</p></div>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>Employee:</strong> {emp}</p>'
            '<p>Date: ________________________</p></div></div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap(
            f"Employment Agreement \u2014 {emp}", body
        )

    # -- Consultancy Agreement renderer -------------------------------------

    def _render_consultancy_agreement(
        self, tpl: dict, config: dict, parties: dict
    ) -> str:
        consultant = config.get("consultant_name", "[Consultant Name]")
        c_type = config.get("consultant_type", "Individual")
        scope = config.get("scope_of_work", "[Scope]")
        deliverables = config.get("deliverables", "[Deliverables]")
        start = config.get("start_date", "[Start Date]")
        end = config.get("end_date", "")
        client = parties.get("company_name", "[Client]")

        sections: List[str] = []
        cn = 0

        cn += 1
        duration_text = f"from {start}" + (f" to {end}" if end else " on an ongoing basis")
        sections.append(
            f'<h2>{cn}. Engagement</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'<strong>{client}</strong> ("Client") hereby engages '
            f'<strong>{consultant}</strong> ({c_type}) ("Consultant") {duration_text}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Scope of work: {scope}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Deliverables: {deliverables}.</p>'
        )

        cn += 1
        ptype = config.get("payment_type", "Fixed fee")
        amt = config.get("payment_amount", 0)
        sched = config.get("payment_schedule", "Monthly")
        inv = config.get("invoicing", "Consultant invoices")
        sections.append(
            f'<h2>{cn}. Payment</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Payment type: {ptype}. Amount: INR {amt:,}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Payment schedule: {sched}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Invoicing: {inv}. TDS shall be deducted as applicable under Section 194J '
            f'of the Income Tax Act.</p>'
        )

        cn += 1
        ip = config.get("ip_ownership_consultancy", "All IP to client")
        tools = config.get("existing_tools", "Consultant retains rights to pre-existing tools")
        sections.append(
            f'<h2>{cn}. Intellectual Property</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'IP ownership: {ip}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Pre-existing tools: {tools}.</p>'
        )

        cn += 1
        conf = "shall" if config.get("confidentiality_consultancy", True) else "shall not"
        nc = "shall" if config.get("non_compete_consultancy") else "shall not"
        excl = "exclusive" if config.get("exclusivity") else "non-exclusive"
        sections.append(
            f'<h2>{cn}. Confidentiality & Restrictions</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Consultant {conf} maintain strict confidentiality of all Client information.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Consultant {nc} be restricted from working with competitors during the engagement.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'This is an {excl} engagement.</p>'
        )

        cn += 1
        notice = config.get("termination_notice_consultancy", "30 days")
        cap = config.get("liability_cap", "Total fees paid")
        indem = "shall" if config.get("indemnification", True) else "shall not"
        sections.append(
            f'<h2>{cn}. Termination & Liability</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Either party may terminate with {notice} written notice.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Liability cap: {cap}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The Consultant {indem} indemnify the Client against all third-party '
            f'claims arising from the Consultant\'s work.</p>'
        )

        sections.append(
            '<div class="signature-block"><h2>Signatures</h2>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>Client:</strong> {client}</p>'
            '<p>Date: ________________________</p></div>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>Consultant:</strong> {consultant}</p>'
            '<p>Date: ________________________</p></div></div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap(
            f"Consultancy Agreement \u2014 {consultant}", body, start
        )

    # ======================================================================
    # TEMPLATE 5: SHAREHOLDERS' AGREEMENT (SHA)
    # ======================================================================

    def _shareholders_agreement(self) -> dict:
        return {
            "name": "Shareholders' Agreement",
            "description": (
                "Governs the rights and obligations of shareholders, covering "
                "share transfers, board composition, reserved matters, exit "
                "provisions, and anti-dilution protections."
            ),
            "category": "Startup Essentials",
            "steps": [
                self._sha_step1_company_shareholders(),
                self._sha_step2_share_capital(),
                self._sha_step3_governance(),
                self._sha_step4_anti_dilution(),
                self._sha_step5_exit(),
            ],
        }

    @staticmethod
    def _sha_step1_company_shareholders() -> dict:
        return {
            "step_number": 1,
            "title": "Company & Shareholders",
            "description": "Basic details about the company and parties to this agreement.",
            "clauses": [
                _clause(
                    "sha_company_name", "Company Name", "text",
                    "The registered name of the company",
                ),
                _clause(
                    "sha_company_type", "Company Type", "dropdown",
                    "Legal structure of the company",
                    options=["Private Limited", "LLP"],
                ),
                _clause(
                    "sha_num_shareholders", "Number of Shareholders", "number",
                    "Number of shareholders party to this agreement",
                    min_value=2,
                    max_value=20,
                ),
                _clause(
                    "sha_effective_date", "Effective Date", "date",
                    "Date from which this agreement is effective",
                ),
            ],
        }

    @staticmethod
    def _sha_step2_share_capital() -> dict:
        return {
            "step_number": 2,
            "title": "Share Capital & Transfers",
            "description": "Authorized capital, pre-emptive rights, and transfer restrictions.",
            "clauses": [
                _clause(
                    "sha_authorized_capital", "Authorized Share Capital (INR)", "number",
                    "Total authorized share capital in INR",
                    india_note=(
                        "Under Companies Act 2013, authorized capital must be specified "
                        "in the MOA. Stamp duty is payable on authorized capital, which "
                        "varies by state (0.1% to 0.15%)."
                    ),
                ),
                _clause(
                    "sha_preemptive_rights", "Pre-emptive Rights", "toggle",
                    "Whether existing shareholders get first right to buy new shares",
                    learn_more=(
                        "Pre-emptive rights (Right of First Refusal on new issuances) "
                        "protect shareholders from dilution. When the company issues new "
                        "shares, existing shareholders can buy proportionally to maintain "
                        "their ownership percentage."
                    ),
                    india_note=(
                        "Section 62 of Companies Act 2013 provides statutory pre-emptive "
                        "rights for existing shareholders on new share issuances. However, "
                        "this can be overridden by special resolution."
                    ),
                    common_choice_label="Standard: Yes",
                ),
                _clause(
                    "sha_transfer_restrictions", "Transfer Restrictions", "dropdown",
                    "Restrictions on transferring shares to third parties",
                    options=[
                        "ROFR only",
                        "ROFR + Tag-along",
                        "ROFR + Tag-along + Drag-along",
                        "Board approval required",
                    ],
                    learn_more=(
                        "ROFR: Other shareholders get first chance to buy. Tag-along: "
                        "Minority can join a sale on same terms. Drag-along: Majority can "
                        "force minority to sell. Board approval: Any transfer needs board "
                        "consent."
                    ),
                    india_note=(
                        "Private Limited companies must have transfer restrictions under "
                        "Section 2(68) of Companies Act 2013. This is a legal requirement, "
                        "not optional."
                    ),
                    common_choice_label="Most comprehensive: ROFR + Tag + Drag",
                ),
                _clause(
                    "sha_lock_in_period", "Lock-in Period", "dropdown",
                    "Minimum period before shares can be transferred",
                    options=["No lock-in", "1 year", "2 years", "3 years"],
                    common_choice_label="Common for founders: 2 years",
                ),
            ],
        }

    @staticmethod
    def _sha_step3_governance() -> dict:
        return {
            "step_number": 3,
            "title": "Governance & Board",
            "description": "Board composition, reserved matters, quorum, and information rights.",
            "clauses": [
                _clause(
                    "sha_board_composition", "Board Composition", "dropdown",
                    "How board seats are allocated",
                    options=[
                        "Equal representation",
                        "Proportional to shareholding",
                        "Fixed seats + investor nominee",
                        "Custom",
                    ],
                    india_note=(
                        "Under Companies Act 2013, Private Limited must have minimum 2 "
                        "directors. Maximum 15 (can be increased by special resolution). "
                        "At least 1 director must be resident in India (stayed 182+ days)."
                    ),
                    common_choice_label="Post-investment: Fixed + investor nominee",
                ),
                _clause(
                    "sha_reserved_matters", "Reserved Matters", "multi_select",
                    "Decisions requiring shareholder approval (not just board)",
                    options=[
                        "Issue new shares",
                        "Take debt above threshold",
                        "Change business direction",
                        "Hire/fire senior management",
                        "Enter related party transactions",
                        "Amend AOA/MOA",
                        "Declare dividends",
                        "Approve annual budget",
                        "Acquire/sell major assets",
                        "File for insolvency",
                    ],
                    learn_more=(
                        "Reserved matters protect minority shareholders by requiring their "
                        "consent for critical decisions. Without these, a majority shareholder "
                        "could make unilateral decisions that harm minority interests."
                    ),
                    common_choice_label="Standard: Select all",
                ),
                _clause(
                    "sha_quorum", "Quorum", "dropdown",
                    "Minimum attendance for valid shareholder meetings",
                    options=[
                        "Simple majority",
                        "Two-thirds",
                        "All shareholders",
                        "Majority including lead investor",
                    ],
                ),
                _clause(
                    "sha_information_rights", "Information Rights", "toggle",
                    "Whether all shareholders get regular financial reports and updates",
                    common_choice_label="Standard: Yes",
                ),
            ],
        }

    @staticmethod
    def _sha_step4_anti_dilution() -> dict:
        return {
            "step_number": 4,
            "title": "Anti-Dilution & Investment",
            "description": "Protection mechanisms for investors and valuation methods.",
            "clauses": [
                _clause(
                    "sha_anti_dilution", "Anti-Dilution Protection", "dropdown",
                    "Protection for investors if company raises at a lower valuation",
                    options=[
                        "No protection",
                        "Full ratchet",
                        "Weighted average (broad-based)",
                        "Weighted average (narrow-based)",
                    ],
                    learn_more=(
                        "Full ratchet: Most investor-friendly \u2014 adjusts price to lowest "
                        "future round price. Weighted average: More balanced \u2014 adjusts "
                        "proportionally based on how much was raised at the lower price. "
                        "Broad-based includes all shares; narrow-based excludes some."
                    ),
                    india_note=(
                        "Anti-dilution provisions are contractual in India. They're enforced "
                        "through the SHA, not by statute. Most VCs in India insist on "
                        "weighted average (broad-based) anti-dilution."
                    ),
                    common_choice_label="Investor-standard: Weighted average (broad-based)",
                ),
                _clause(
                    "sha_liquidation_preference", "Liquidation Preference", "dropdown",
                    "Priority of payout to investors on liquidation/exit",
                    options=[
                        "1x non-participating",
                        "1x participating",
                        "2x non-participating",
                        "No preference",
                    ],
                    learn_more=(
                        "1x non-participating: Investor gets back their investment OR their "
                        "pro-rata share, whichever is higher. 1x participating: Investor gets "
                        "back investment PLUS their pro-rata share of remaining. 2x: Investor "
                        "gets 2x their investment first."
                    ),
                    common_choice_label="Founder-friendly: 1x non-participating",
                ),
                _clause(
                    "sha_valuation_method", "Valuation Method", "dropdown",
                    "How company is valued for share transactions",
                    options=[
                        "Mutual agreement",
                        "Independent valuer",
                        "Formula-based",
                        "Last round valuation",
                    ],
                ),
            ],
        }

    @staticmethod
    def _sha_step5_exit() -> dict:
        return {
            "step_number": 5,
            "title": "Exit & Dispute Resolution",
            "description": "Exit events, deadlock mechanisms, non-compete, and governing law.",
            "clauses": [
                _clause(
                    "sha_exit_events", "Exit Events", "multi_select",
                    "Events that constitute an exit",
                    options=[
                        "IPO",
                        "Trade sale (100% acquisition)",
                        "Strategic sale (majority stake)",
                        "Buyback by company",
                        "Winding up",
                    ],
                ),
                _clause(
                    "sha_deadlock_mechanism", "Deadlock Mechanism", "dropdown",
                    "Resolution when shareholders can't agree",
                    options=[
                        "Mediation then arbitration",
                        "Russian roulette",
                        "Texas shootout",
                        "Put/call options",
                    ],
                    india_note=(
                        "Arbitration is governed by Arbitration and Conciliation Act 1996. "
                        "Indian courts will enforce arbitration clauses. Institutional "
                        "arbitration (SIAC, LCIA, ICC) is preferred for cross-border disputes."
                    ),
                    common_choice_label="Most practical: Mediation then arbitration",
                ),
                _clause(
                    "sha_non_compete", "Non-Compete", "dropdown",
                    "Non-compete obligations for shareholders",
                    options=[
                        "During shareholding only",
                        "During + 1 year post-exit",
                        "During + 2 years post-exit",
                    ],
                    india_note=(
                        "Post-exit non-compete may be unenforceable under Section 27 of "
                        "Indian Contract Act 1872, but during shareholding is valid."
                    ),
                ),
                _clause(
                    "sha_governing_law", "Governing Law", "dropdown",
                    "Which state's laws govern",
                    options=[
                        "Maharashtra",
                        "Karnataka",
                        "Delhi",
                        "Tamil Nadu",
                        "Telangana",
                    ],
                ),
                _clause(
                    "sha_confidentiality", "Confidentiality", "toggle",
                    "Whether shareholders have perpetual confidentiality obligations",
                    common_choice_label="Standard: Yes",
                ),
            ],
        }

    # -- Shareholders' Agreement renderer -----------------------------------

    def _render_shareholders_agreement(
        self, tpl: dict, config: dict, parties: dict
    ) -> str:
        company = config.get("sha_company_name", "[Company Name]")
        co_type = config.get("sha_company_type", "Private Limited")
        num_sh = config.get("sha_num_shareholders", 2)
        date_str = config.get("sha_effective_date", "")
        auth_cap = config.get("sha_authorized_capital", 0)

        sections: List[str] = []
        cn = 0

        # Section 1 - Parties
        cn += 1
        sections.append(
            f'<h2>{cn}. Parties & Recitals</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'This Shareholders\' Agreement ("Agreement") is entered into as of '
            f'{date_str or "[Date]"} by and among {num_sh} shareholders '
            f'(collectively, the "Shareholders") of <strong>{company}</strong>, '
            f'a {co_type} company incorporated under the laws of India.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Shareholders wish to set out their respective rights and '
            f'obligations in relation to the Company and its management.</p>'
        )

        # Section 2 - Share Capital & Transfers
        cn += 1
        preemptive = "shall have" if config.get("sha_preemptive_rights") else "shall not have"
        transfer = config.get("sha_transfer_restrictions", "ROFR only")
        lock_in = config.get("sha_lock_in_period", "No lock-in")
        sections.append(
            f'<h2>{cn}. Share Capital & Transfer Restrictions</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The authorized share capital of the Company is INR {auth_cap:,}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Existing Shareholders {preemptive} pre-emptive rights on any new '
            f'issuance of shares by the Company.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Share transfer restrictions: {transfer}. No Shareholder shall transfer '
            f'any shares except in compliance with the transfer restrictions set out herein.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Lock-in period: {lock_in}. During the lock-in period, no Shareholder '
            f'shall transfer, pledge, or encumber any shares.</p>'
        )

        # Section 3 - Governance
        cn += 1
        board = config.get("sha_board_composition", "Equal representation")
        reserved = config.get("sha_reserved_matters", [])
        reserved_str = ", ".join(reserved) if isinstance(reserved, list) else str(reserved)
        quorum = config.get("sha_quorum", "Simple majority")
        info = "shall" if config.get("sha_information_rights") else "shall not"
        sections.append(
            f'<h2>{cn}. Governance & Board</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Board composition: {board}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The following matters shall require prior approval of the Shareholders '
            f'(Reserved Matters): {reserved_str}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Quorum for shareholder meetings: {quorum}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'The Company {info} provide all Shareholders with regular financial '
            f'reports, management updates, and access to company records.</p>'
        )

        # Section 4 - Anti-Dilution & Investment
        cn += 1
        anti_d = config.get("sha_anti_dilution", "No protection")
        liq_pref = config.get("sha_liquidation_preference", "No preference")
        val_method = config.get("sha_valuation_method", "Mutual agreement")
        sections.append(
            f'<h2>{cn}. Anti-Dilution & Investment Protection</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Anti-dilution protection: {anti_d}. In the event of a down-round, '
            f'the protected Shareholders shall be entitled to adjustment of their '
            f'conversion price accordingly.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Liquidation preference: {liq_pref}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Valuation for share transactions shall be determined by: {val_method}.</p>'
        )

        # Section 5 - Exit & Disputes
        cn += 1
        exits = config.get("sha_exit_events", [])
        exits_str = ", ".join(exits) if isinstance(exits, list) else str(exits)
        deadlock = config.get("sha_deadlock_mechanism", "Mediation then arbitration")
        non_compete = config.get("sha_non_compete", "During shareholding only")
        gov_law = config.get("sha_governing_law", "Maharashtra")
        conf = "shall" if config.get("sha_confidentiality") else "shall not"
        sections.append(
            f'<h2>{cn}. Exit & Dispute Resolution</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Exit events: {exits_str}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Deadlock resolution mechanism: {deadlock}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Non-compete: {non_compete}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'This Agreement shall be governed by the laws of the State of {gov_law}, India.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.5</span> '
            f'Each Shareholder {conf} have perpetual confidentiality obligations '
            f'with respect to the Company\'s proprietary information.</p>'
        )

        # Signature block
        sig_lines = ""
        for i in range(1, num_sh + 1):
            sig_lines += (
                f'<div class="signature-line">'
                f'<div class="line"></div>'
                f'<p><strong>Shareholder {i}</strong></p>'
                f'<p>Name: ________________________</p>'
                f'<p>Date: ________________________</p>'
                f'</div>\n'
            )
        sections.append(
            f'<div class="signature-block"><h2>Signatures</h2>'
            f'<p class="clause">IN WITNESS WHEREOF, the Shareholders have executed '
            f'this Agreement as of the date first written above.</p>{sig_lines}</div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap(
            f"Shareholders' Agreement \u2014 {company}", body, date_str
        )

    # ======================================================================
    # TEMPLATE 6: TERM SHEET
    # ======================================================================

    def _term_sheet(self) -> dict:
        return {
            "name": "Term Sheet",
            "description": (
                "A non-binding document outlining the key terms of an investment. "
                "Sets the framework for negotiation before the definitive agreements "
                "are drafted."
            ),
            "category": "Fundraising",
            "steps": [
                self._ts_step1_deal_overview(),
                self._ts_step2_investor_rights(),
                self._ts_step3_restrictions(),
                self._ts_step4_closing(),
            ],
        }

    @staticmethod
    def _ts_step1_deal_overview() -> dict:
        return {
            "step_number": 1,
            "title": "Deal Overview",
            "description": "Core terms of the investment round.",
            "clauses": [
                _clause(
                    "ts_company_name", "Company Name", "text",
                    "Company receiving the investment",
                ),
                _clause(
                    "ts_investor_name", "Lead Investor", "text",
                    "Name of the lead investor",
                ),
                _clause(
                    "ts_round_type", "Round Type", "dropdown",
                    "Type of funding round",
                    options=[
                        "Pre-Seed",
                        "Seed",
                        "Series A",
                        "Series B",
                        "Bridge Round",
                    ],
                ),
                _clause(
                    "ts_investment_amount", "Investment Amount (INR)", "number",
                    "Total investment amount in INR",
                    preview_template="The Investor shall invest INR {value} in the Company.",
                ),
                _clause(
                    "ts_pre_money_valuation", "Pre-Money Valuation (INR)", "number",
                    "Pre-money valuation of the company in INR",
                    learn_more=(
                        "Pre-money valuation = what the company is worth BEFORE the "
                        "investment. Post-money = pre-money + investment amount. Your "
                        "dilution = investment / post-money valuation."
                    ),
                ),
                _clause(
                    "ts_instrument", "Investment Instrument", "dropdown",
                    "Type of investment instrument",
                    options=[
                        "Equity (shares)",
                        "Compulsorily Convertible Preference Shares (CCPS)",
                        "Compulsorily Convertible Debentures (CCD)",
                        "SAFE/iSAFE",
                    ],
                    india_note=(
                        "CCPS and CCDs are most common for Indian startup fundraising. "
                        "They offer downside protection while converting to equity. "
                        "iSAFE (Indian Simple Agreement for Future Equity) was introduced "
                        "by iSPIRT for early-stage rounds."
                    ),
                    common_choice_label="Most common: CCPS",
                ),
            ],
        }

    @staticmethod
    def _ts_step2_investor_rights() -> dict:
        return {
            "step_number": 2,
            "title": "Investor Rights",
            "description": "Board seat, anti-dilution, liquidation preference, and other rights.",
            "clauses": [
                _clause(
                    "ts_board_seat", "Board Seat", "toggle",
                    "Whether the investor gets a board seat",
                    common_choice_label="Standard for lead investor: Yes",
                ),
                _clause(
                    "ts_anti_dilution", "Anti-Dilution Protection", "dropdown",
                    "Anti-dilution protection type",
                    options=[
                        "No protection",
                        "Weighted average (broad-based)",
                        "Weighted average (narrow-based)",
                        "Full ratchet",
                    ],
                    common_choice_label="Standard: Weighted average (broad-based)",
                ),
                _clause(
                    "ts_liquidation_preference", "Liquidation Preference", "dropdown",
                    "Priority on liquidation/exit",
                    options=[
                        "1x non-participating",
                        "1x participating",
                        "2x non-participating",
                    ],
                    common_choice_label="Founder-friendly: 1x non-participating",
                ),
                _clause(
                    "ts_information_rights", "Information Rights", "toggle",
                    "Right to receive quarterly financial statements and annual audited accounts",
                    common_choice_label="Standard: Yes",
                ),
                _clause(
                    "ts_pro_rata_rights", "Pro-Rata Rights", "toggle",
                    "Right to participate in future rounds to maintain ownership percentage",
                    common_choice_label="Standard: Yes",
                ),
            ],
        }

    @staticmethod
    def _ts_step3_restrictions() -> dict:
        return {
            "step_number": 3,
            "title": "Restrictions & Protective Provisions",
            "description": "Founder vesting, ESOP pool, reserved matters, and non-compete.",
            "clauses": [
                _clause(
                    "ts_founder_vesting", "Founder Vesting", "toggle",
                    "Whether founders must have vesting schedules",
                    learn_more=(
                        "Investors almost always require founder vesting to ensure founders "
                        "stay committed. Typically 4-year vesting with 1-year cliff. "
                        "Existing service time may be credited."
                    ),
                    common_choice_label="Almost always required: Yes",
                ),
                _clause(
                    "ts_esop_pool", "ESOP Pool Size", "dropdown",
                    "Size of employee stock option pool",
                    options=["10%", "15%", "20%", "As mutually agreed"],
                    learn_more=(
                        "The ESOP pool is typically created from the pre-money valuation, "
                        "meaning existing shareholders bear the dilution, not the new "
                        "investor. Negotiate this carefully."
                    ),
                    india_note=(
                        "Under Companies Act 2013 Section 62(1)(b), companies can issue "
                        "stock options to employees. The ESOP pool size affects your "
                        "effective valuation."
                    ),
                    common_choice_label="Standard: 10-15%",
                ),
                _clause(
                    "ts_reserved_matters", "Reserved Matters", "multi_select",
                    "Decisions requiring investor consent",
                    options=[
                        "New share issuance",
                        "Debt above threshold",
                        "Change of control",
                        "Related party transactions",
                        "Change in business",
                        "Winding up",
                        "Amendment of SHA/AOA",
                    ],
                ),
                _clause(
                    "ts_non_compete_founders", "Founder Non-Compete", "dropdown",
                    "Non-compete for founders",
                    options=[
                        "During employment + 2 years",
                        "During employment + 1 year",
                        "During employment only",
                    ],
                ),
            ],
        }

    @staticmethod
    def _ts_step4_closing() -> dict:
        return {
            "step_number": 4,
            "title": "Closing & Other Terms",
            "description": "Conditions precedent, exclusivity, binding clauses, and governing law.",
            "clauses": [
                _clause(
                    "ts_conditions_precedent", "Conditions Precedent", "multi_select",
                    "Conditions that must be met before closing",
                    options=[
                        "Satisfactory due diligence",
                        "Legal documentation",
                        "Regulatory approvals",
                        "Key employee retention",
                        "IP assignment to company",
                        "No material adverse change",
                    ],
                ),
                _clause(
                    "ts_exclusivity_period", "Exclusivity Period", "dropdown",
                    "Period during which company cannot negotiate with other investors",
                    options=["30 days", "45 days", "60 days", "90 days"],
                    common_choice_label="Standard: 45-60 days",
                ),
                _clause(
                    "ts_binding_clauses", "Binding Clauses", "multi_select",
                    "Which clauses are legally binding (rest is non-binding)",
                    options=[
                        "Confidentiality",
                        "Exclusivity",
                        "Governing law",
                        "Dispute resolution",
                    ],
                    learn_more=(
                        "A term sheet is generally non-binding EXCEPT for specific clauses "
                        "like confidentiality and exclusivity. This allows negotiation "
                        "flexibility while protecting key interests."
                    ),
                    common_choice_label="Standard: All four",
                ),
                _clause(
                    "ts_governing_law", "Governing Law", "dropdown",
                    "Governing law for binding clauses",
                    options=[
                        "Maharashtra",
                        "Karnataka",
                        "Delhi",
                        "Tamil Nadu",
                        "Telangana",
                    ],
                ),
            ],
        }

    # -- Term Sheet renderer ------------------------------------------------

    def _render_term_sheet(
        self, tpl: dict, config: dict, parties: dict
    ) -> str:
        company = config.get("ts_company_name", "[Company Name]")
        investor = config.get("ts_investor_name", "[Investor Name]")
        round_type = config.get("ts_round_type", "[Round]")
        amount = config.get("ts_investment_amount", 0)
        pre_money = config.get("ts_pre_money_valuation", 0)
        instrument = config.get("ts_instrument", "Equity (shares)")
        date_str = ""

        sections: List[str] = []
        cn = 0

        # Section 1 - Deal Overview
        cn += 1
        post_money = pre_money + amount if pre_money and amount else 0
        dilution = (
            f"{(amount / post_money * 100):.1f}%" if post_money else "N/A"
        )
        sections.append(
            f'<h2>{cn}. Deal Overview</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'<strong>{investor}</strong> ("Investor") proposes to invest in '
            f'<strong>{company}</strong> ("Company") on the terms set out below.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Round type: {round_type}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Investment amount: INR {amount:,}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Pre-money valuation: INR {pre_money:,}. Post-money valuation: '
            f'INR {post_money:,}. Dilution: {dilution}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.5</span> '
            f'Investment instrument: {instrument}.</p>'
        )

        # Section 2 - Investor Rights
        cn += 1
        board = "shall" if config.get("ts_board_seat") else "shall not"
        anti_d = config.get("ts_anti_dilution", "No protection")
        liq = config.get("ts_liquidation_preference", "1x non-participating")
        info = "shall" if config.get("ts_information_rights") else "shall not"
        pro_rata = "shall" if config.get("ts_pro_rata_rights") else "shall not"
        sections.append(
            f'<h2>{cn}. Investor Rights</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Investor {board} be entitled to a seat on the Board of Directors.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Anti-dilution protection: {anti_d}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Liquidation preference: {liq}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'The Investor {info} have the right to receive quarterly financial '
            f'statements and annual audited accounts.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.5</span> '
            f'The Investor {pro_rata} have pro-rata rights to participate in '
            f'future financing rounds.</p>'
        )

        # Section 3 - Restrictions
        cn += 1
        vesting = "shall" if config.get("ts_founder_vesting") else "shall not"
        esop = config.get("ts_esop_pool", "10%")
        reserved = config.get("ts_reserved_matters", [])
        reserved_str = ", ".join(reserved) if isinstance(reserved, list) else str(reserved)
        nc = config.get("ts_non_compete_founders", "During employment only")
        sections.append(
            f'<h2>{cn}. Restrictions & Protective Provisions</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Founders {vesting} be subject to vesting schedules.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Company shall create an ESOP pool of {esop} of the fully diluted '
            f'share capital, carved from the pre-money valuation.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The following decisions shall require prior written consent of the '
            f'Investor (Reserved Matters): {reserved_str}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Founder non-compete: {nc}.</p>'
        )

        # Section 4 - Closing
        cn += 1
        cps = config.get("ts_conditions_precedent", [])
        cps_str = ", ".join(cps) if isinstance(cps, list) else str(cps)
        excl = config.get("ts_exclusivity_period", "45 days")
        binding = config.get("ts_binding_clauses", [])
        binding_str = ", ".join(binding) if isinstance(binding, list) else str(binding)
        gov = config.get("ts_governing_law", "Maharashtra")
        sections.append(
            f'<h2>{cn}. Closing & Other Terms</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Conditions precedent to closing: {cps_str}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Exclusivity period: {excl}. During this period, the Company shall not '
            f'solicit, negotiate, or enter into any agreement with any third party '
            f'for any equity financing.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The following clauses of this Term Sheet are legally binding: '
            f'{binding_str}. All other provisions are non-binding and are intended '
            f'as a framework for negotiation only.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'The binding clauses shall be governed by the laws of the State of '
            f'{gov}, India.</p>'
        )

        # Signature block
        sections.append(
            '<div class="signature-block"><h2>Signatures</h2>'
            '<p class="clause">This Term Sheet is executed as a statement of intent '
            'and, except for the binding clauses identified above, does not constitute '
            'a legally binding obligation on either party.</p>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>For the Company:</strong> {company}</p>'
            '<p>Name: ________________________</p>'
            '<p>Date: ________________________</p></div>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>For the Investor:</strong> {investor}</p>'
            '<p>Name: ________________________</p>'
            '<p>Date: ________________________</p></div></div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap(
            f"Term Sheet \u2014 {company} ({round_type})", body, date_str
        )

    # ======================================================================
    # TEMPLATE 7: ADVISOR AGREEMENT
    # ======================================================================

    def _advisor_agreement(self) -> dict:
        return {
            "name": "Advisor Agreement",
            "description": (
                "Formalizes the relationship with startup advisors, covering "
                "advisory scope, time commitment, equity compensation, vesting, "
                "and confidentiality."
            ),
            "category": "Team",
            "steps": [
                self._adv_step1_details(),
                self._adv_step2_compensation(),
                self._adv_step3_ip_confidentiality(),
            ],
        }

    @staticmethod
    def _adv_step1_details() -> dict:
        return {
            "step_number": 1,
            "title": "Advisor Details & Scope",
            "description": "Who the advisor is, their area of expertise, and scope of engagement.",
            "clauses": [
                _clause(
                    "adv_advisor_name", "Advisor Name", "text",
                    "Full name of the advisor",
                ),
                _clause(
                    "adv_company_name", "Company Name", "text",
                    "Company receiving advisory services",
                ),
                _clause(
                    "adv_advisory_area", "Advisory Area", "dropdown",
                    "Primary area of advisory",
                    options=[
                        "Strategy & Business Development",
                        "Technology & Product",
                        "Finance & Fundraising",
                        "Legal & Compliance",
                        "Marketing & Growth",
                        "Industry-specific",
                    ],
                ),
                _clause(
                    "adv_scope", "Scope of Advisory", "textarea",
                    "Description of specific advisory services to be provided",
                ),
                _clause(
                    "adv_time_commitment", "Time Commitment", "dropdown",
                    "Expected time commitment from the advisor",
                    options=[
                        "2 hours/month",
                        "4 hours/month",
                        "8 hours/month",
                        "As needed",
                    ],
                    common_choice_label="Standard: 4 hours/month",
                ),
                _clause(
                    "adv_term", "Advisory Term", "dropdown",
                    "Duration of the advisory engagement",
                    options=["6 months", "1 year", "2 years", "Until terminated"],
                    common_choice_label="Standard: 1 year",
                ),
            ],
        }

    @staticmethod
    def _adv_step2_compensation() -> dict:
        return {
            "step_number": 2,
            "title": "Compensation & Equity",
            "description": "How the advisor is compensated for their services.",
            "clauses": [
                _clause(
                    "adv_compensation_type", "Compensation Type", "dropdown",
                    "How the advisor is compensated",
                    options=[
                        "Equity only",
                        "Cash only",
                        "Cash + Equity",
                        "No compensation",
                    ],
                    learn_more=(
                        "Most startup advisors receive equity (0.25% to 2% depending on "
                        "stage and contribution level). Cash compensation is less common "
                        "for early-stage startups."
                    ),
                    common_choice_label="Most common: Equity only",
                ),
                _clause(
                    "adv_equity_percentage", "Equity Percentage", "text",
                    "Equity percentage offered (e.g., 0.5%)",
                    learn_more=(
                        "Standard advisor equity: Pre-seed/Seed: 0.5-1%. Series A+: "
                        "0.25-0.5%. These are typically issued as stock options vesting "
                        "over the advisory term."
                    ),
                    india_note=(
                        "Advisor equity in Indian companies is typically structured as "
                        "ESOPs under Section 62(1)(b) of Companies Act 2013, or as direct "
                        "share allotment (which requires board resolution and compliance "
                        "with Section 62)."
                    ),
                ),
                _clause(
                    "adv_vesting_schedule", "Vesting Schedule", "dropdown",
                    "How equity vests over time",
                    options=[
                        "Monthly over 1 year",
                        "Monthly over 2 years",
                        "Quarterly over 1 year",
                        "Milestone-based",
                    ],
                    common_choice_label="Standard: Monthly over 1 year (no cliff)",
                ),
                _clause(
                    "adv_cash_compensation", "Cash Compensation (INR/month)", "number",
                    "Monthly cash payment in INR (if applicable)",
                    required=False,
                ),
            ],
        }

    @staticmethod
    def _adv_step3_ip_confidentiality() -> dict:
        return {
            "step_number": 3,
            "title": "IP, Confidentiality & Termination",
            "description": "Intellectual property assignment, confidentiality, and termination terms.",
            "clauses": [
                _clause(
                    "adv_ip_assignment", "IP Assignment", "toggle",
                    "Whether advisor assigns IP created during advisory to the company",
                    common_choice_label="Recommended: Yes",
                    india_note=(
                        "Unlike employees, advisor IP does not automatically vest in the "
                        "company. An explicit assignment clause is essential under Indian "
                        "Copyright Act 1957."
                    ),
                ),
                _clause(
                    "adv_confidentiality", "Confidentiality", "toggle",
                    "Whether advisor has confidentiality obligations",
                    common_choice_label="Essential: Yes",
                ),
                _clause(
                    "adv_termination_notice", "Termination Notice", "dropdown",
                    "Notice period for termination by either party",
                    options=["7 days", "15 days", "30 days"],
                    common_choice_label="Standard: 30 days",
                ),
            ],
        }

    # -- Advisor Agreement renderer -----------------------------------------

    def _render_advisor_agreement(
        self, tpl: dict, config: dict, parties: dict
    ) -> str:
        advisor = config.get("adv_advisor_name", "[Advisor Name]")
        company = config.get("adv_company_name", "[Company Name]")
        area = config.get("adv_advisory_area", "[Advisory Area]")
        scope = config.get("adv_scope", "[Scope]")
        time_commit = config.get("adv_time_commitment", "4 hours/month")
        term = config.get("adv_term", "1 year")
        date_str = ""

        sections: List[str] = []
        cn = 0

        # Section 1 - Engagement
        cn += 1
        sections.append(
            f'<h2>{cn}. Advisory Engagement</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'<strong>{company}</strong> ("Company") hereby engages '
            f'<strong>{advisor}</strong> ("Advisor") as an advisor in the area of '
            f'{area}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Scope of advisory services: {scope}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Time commitment: {time_commit}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'This engagement shall be for a term of {term}.</p>'
        )

        # Section 2 - Compensation
        cn += 1
        comp_type = config.get("adv_compensation_type", "Equity only")
        equity_pct = config.get("adv_equity_percentage", "0.5%")
        vesting = config.get("adv_vesting_schedule", "Monthly over 1 year")
        cash = config.get("adv_cash_compensation", 0)
        comp_html = (
            f'<h2>{cn}. Compensation</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Compensation type: {comp_type}.</p>'
        )
        if comp_type in ("Equity only", "Cash + Equity"):
            comp_html += (
                f'<p class="clause"><span class="clause-number">{cn}.2</span> '
                f'The Advisor shall receive {equity_pct} equity in the Company, '
                f'vesting as follows: {vesting}.</p>'
            )
        if comp_type in ("Cash only", "Cash + Equity") and cash:
            comp_html += (
                f'<p class="clause"><span class="clause-number">{cn}.3</span> '
                f'The Advisor shall receive a monthly cash payment of INR {cash:,}.</p>'
            )
        sections.append(comp_html)

        # Section 3 - IP & Confidentiality
        cn += 1
        ip = "shall" if config.get("adv_ip_assignment") else "shall not"
        conf = "shall" if config.get("adv_confidentiality") else "shall not"
        notice = config.get("adv_termination_notice", "30 days")
        sections.append(
            f'<h2>{cn}. Intellectual Property, Confidentiality & Termination</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'The Advisor {ip} assign to the Company all intellectual property '
            f'created in connection with the advisory engagement.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Advisor {conf} be bound by confidentiality obligations with '
            f'respect to the Company\'s proprietary information.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Either party may terminate this Agreement by providing {notice} '
            f'written notice to the other party.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Upon termination, unvested equity (if any) shall be forfeited, and '
            f'vested equity shall be retained by the Advisor.</p>'
        )

        # Signature block
        sections.append(
            '<div class="signature-block"><h2>Signatures</h2>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>For the Company:</strong> {company}</p>'
            '<p>Name: ________________________</p>'
            '<p>Date: ________________________</p></div>'
            '<div class="signature-line"><div class="line"></div>'
            f'<p><strong>Advisor:</strong> {advisor}</p>'
            '<p>Date: ________________________</p></div></div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap(
            f"Advisor Agreement \u2014 {advisor}", body, date_str
        )

    # ======================================================================
    # TEMPLATE 8: ESOP PLAN + GRANT LETTER
    # ======================================================================

    def _esop_plan(self) -> dict:
        return {
            "name": "ESOP Plan + Grant Letter",
            "description": (
                "Employee Stock Option Plan (ESOP) for your company, including "
                "the plan document and individual grant letters. Essential for "
                "attracting and retaining talent in Indian startups."
            ),
            "category": "Equity",
            "steps": [
                self._esop_step1_plan_basics(),
                self._esop_step2_vesting_exercise(),
                self._esop_step3_taxation(),
                self._esop_step4_termination(),
            ],
        }

    @staticmethod
    def _esop_step1_plan_basics() -> dict:
        return {
            "step_number": 1,
            "title": "Plan Basics",
            "description": "Core details of the ESOP plan.",
            "clauses": [
                _clause(
                    "esop_company_name", "Company Name", "text",
                    "Registered name of the company",
                ),
                _clause(
                    "esop_pool_size", "ESOP Pool Size (options)", "number",
                    "Total number of options in the ESOP pool",
                    india_note=(
                        "Under Companies Act 2013, ESOPs can be issued under Section "
                        "62(1)(b). The company must pass a special resolution (75% "
                        "majority) to create the ESOP pool. Board resolution alone is "
                        "not sufficient."
                    ),
                ),
                _clause(
                    "esop_pool_percentage", "ESOP Pool Percentage", "text",
                    "ESOP pool as percentage of fully diluted capital (e.g., 10%)",
                    learn_more=(
                        "Standard ESOP pools: 10-15% at seed stage, expanding to 15-20% "
                        "by Series A. The pool is typically created before fundraising so "
                        "dilution falls on existing shareholders."
                    ),
                    common_choice_label="Standard: 10-15%",
                ),
                _clause(
                    "esop_effective_date", "Effective Date", "date",
                    "Date from which the ESOP plan is effective",
                ),
                _clause(
                    "esop_eligible_participants", "Eligible Participants", "multi_select",
                    "Who can receive ESOPs",
                    options=[
                        "Full-time employees",
                        "Part-time employees",
                        "Directors (non-independent)",
                        "Consultants/advisors",
                        "Employees of subsidiary companies",
                    ],
                    india_note=(
                        "Under Companies Act 2013, ESOPs can be granted to permanent "
                        "employees working in India or outside India, and to directors "
                        "(excluding independent directors and promoter holding >10%). "
                        "Promoters holding >10% cannot receive ESOPs."
                    ),
                ),
            ],
        }

    @staticmethod
    def _esop_step2_vesting_exercise() -> dict:
        return {
            "step_number": 2,
            "title": "Vesting & Exercise",
            "description": "Vesting schedule, cliff, exercise price, and exercise window.",
            "clauses": [
                _clause(
                    "esop_vesting_period", "Vesting Period", "dropdown",
                    "Total vesting period",
                    options=["3 years", "4 years", "5 years"],
                    india_note=(
                        "Under Companies Act 2013, there is a mandatory minimum vesting "
                        "period of 1 year from the date of grant. The company cannot allow "
                        "exercise before this minimum period."
                    ),
                    common_choice_label="Standard: 4 years",
                ),
                _clause(
                    "esop_cliff", "Cliff Period", "dropdown",
                    "Minimum period before any options vest",
                    options=[
                        "No cliff (start vesting from year 1)",
                        "1 year cliff",
                        "6 month cliff",
                    ],
                    learn_more=(
                        "The cliff is the minimum period before any options vest. With a "
                        "1-year cliff, if the employee leaves before 1 year, they get "
                        "nothing. After the cliff, options vest monthly or quarterly."
                    ),
                    common_choice_label="Standard: 1 year cliff",
                ),
                _clause(
                    "esop_vesting_schedule", "Vesting Schedule", "dropdown",
                    "How frequently options vest after the cliff",
                    options=["Monthly", "Quarterly", "Annually"],
                    common_choice_label="Most common: Monthly",
                ),
                _clause(
                    "esop_exercise_price", "Exercise Price", "dropdown",
                    "Price at which employee can buy shares on exercise",
                    options=[
                        "Fair Market Value at grant",
                        "Par value (\u20b910)",
                        "Discount to FMV",
                        "Fixed price set by board",
                    ],
                    india_note=(
                        "For unlisted companies, FMV is determined by a registered valuer "
                        "using DCF method as prescribed under Rule 11UA of Income Tax "
                        "Rules. Exercise at below FMV triggers perquisite tax on the "
                        "difference."
                    ),
                    common_choice_label="Most common for startups: Par value or nominal",
                ),
                _clause(
                    "esop_exercise_window", "Exercise Window", "dropdown",
                    "Window within which vested options must be exercised",
                    options=[
                        "30 days after vesting",
                        "90 days after vesting",
                        "Until termination + 90 days",
                        "5 years from vesting",
                    ],
                    common_choice_label="Standard: Until termination + 90 days",
                ),
            ],
        }

    @staticmethod
    def _esop_step3_taxation() -> dict:
        return {
            "step_number": 3,
            "title": "Taxation & Compliance",
            "description": "Tax treatment, DPIIT recognition, and buyback provisions.",
            "clauses": [
                _clause(
                    "esop_tax_timing", "Tax Timing", "dropdown",
                    "When tax is payable on ESOPs",
                    options=[
                        "Tax at exercise (perquisite) + capital gains at sale",
                        "Tax deferred to sale (if eligible startup)",
                    ],
                    learn_more=(
                        "Standard taxation: Perquisite tax (as salary income) at exercise "
                        "on (FMV - exercise price), then capital gains tax at sale. For "
                        "eligible startups (recognized by DPIIT), tax on perquisite can be "
                        "deferred up to 5 years or until sale, whichever is earlier "
                        "(Section 80-IAC benefit)."
                    ),
                    india_note=(
                        "Finance Act 2020 introduced ESOP tax deferral for DPIIT-recognized "
                        "startups. The perquisite tax is deferred to the earliest of: "
                        "(a) 5 years from allotment, (b) date of sale, (c) date of leaving "
                        "the company. TDS obligation shifts accordingly."
                    ),
                ),
                _clause(
                    "esop_dpiit_recognized", "DPIIT Recognized Startup", "toggle",
                    "Whether the company is DPIIT-recognized startup (affects tax treatment)",
                    learn_more=(
                        "DPIIT recognition provides significant tax benefits for ESOP "
                        "holders. To qualify: company must be incorporated as Pvt Ltd or "
                        "LLP, turnover below \u20b9100 crore in any FY, and working towards "
                        "innovation/development."
                    ),
                ),
                _clause(
                    "esop_buyback_provision", "Buyback Provision", "toggle",
                    "Whether the company can buy back vested options from departing employees",
                    learn_more=(
                        "A buyback provision allows the company to repurchase vested shares "
                        "from departing employees, preventing ex-employees from remaining "
                        "shareholders. This is common in unlisted companies where there's "
                        "no public market for shares."
                    ),
                    common_choice_label="Recommended: Yes",
                ),
            ],
        }

    @staticmethod
    def _esop_step4_termination() -> dict:
        return {
            "step_number": 4,
            "title": "Termination & Special Events",
            "description": "Treatment of options on termination, change of control, and death/disability.",
            "clauses": [
                _clause(
                    "esop_termination_treatment", "Termination Treatment", "dropdown",
                    "What happens to options when employment ends",
                    options=[
                        "Unvested options lapse, vested options exercisable for 90 days",
                        "All options lapse",
                        "Accelerated vesting on termination without cause",
                        "Board discretion",
                    ],
                    common_choice_label="Standard: Unvested lapse, vested exercisable 90 days",
                ),
                _clause(
                    "esop_change_of_control", "Change of Control", "dropdown",
                    "Whether vesting accelerates on company sale/acquisition",
                    options=[
                        "No acceleration",
                        "Full acceleration",
                        "Partial acceleration (50%)",
                        "Board discretion",
                    ],
                    learn_more=(
                        "Acceleration on change of control rewards employees when the "
                        "company is acquired. Full acceleration means all options vest "
                        "immediately. Partial means a percentage accelerates."
                    ),
                    common_choice_label="Employee-friendly: Full acceleration",
                ),
                _clause(
                    "esop_death_disability", "Death or Disability", "dropdown",
                    "Treatment of options on death or permanent disability",
                    options=[
                        "Vested options exercisable by nominee for 1 year",
                        "Full acceleration for nominee",
                        "All options lapse",
                    ],
                    india_note=(
                        "Under Indian Succession Act, the nominee of the deceased can "
                        "exercise vested options. The company should maintain clear records "
                        "of nominees. Nomination provisions under Companies Act 2013 "
                        "Section 72 apply."
                    ),
                    common_choice_label="Fair: Vested options exercisable by nominee for 1 year",
                ),
            ],
        }

    # -- ESOP Plan renderer -------------------------------------------------

    def _render_esop_plan(
        self, tpl: dict, config: dict, parties: dict
    ) -> str:
        company = config.get("esop_company_name", "[Company Name]")
        pool_size = config.get("esop_pool_size", 0)
        pool_pct = config.get("esop_pool_percentage", "10%")
        eff_date = config.get("esop_effective_date", "")
        eligible = config.get("esop_eligible_participants", [])
        eligible_str = ", ".join(eligible) if isinstance(eligible, list) else str(eligible)

        sections: List[str] = []
        cn = 0

        # Section 1 - Plan Overview
        cn += 1
        sections.append(
            f'<h2>{cn}. Plan Overview</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'<strong>{company}</strong> ("Company") hereby establishes this '
            f'Employee Stock Option Plan ("ESOP Plan" or "Plan") effective as of '
            f'{eff_date or "[Date]"}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The total ESOP pool shall consist of {pool_size:,} options, '
            f'representing {pool_pct} of the fully diluted share capital of the Company.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'Eligible participants: {eligible_str}.</p>'
        )

        # Section 2 - Vesting & Exercise
        cn += 1
        vp = config.get("esop_vesting_period", "4 years")
        cliff = config.get("esop_cliff", "1 year cliff")
        sched = config.get("esop_vesting_schedule", "Monthly")
        price = config.get("esop_exercise_price", "Fair Market Value at grant")
        window = config.get("esop_exercise_window", "Until termination + 90 days")
        sections.append(
            f'<h2>{cn}. Vesting & Exercise</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Options shall vest over a total period of {vp}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'Cliff period: {cliff}. No options shall vest before the expiry of the '
            f'cliff period.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'After the cliff period, options shall vest on a {sched} basis.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.4</span> '
            f'Exercise price: {price}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.5</span> '
            f'Exercise window: {window}.</p>'
        )

        # Section 3 - Taxation
        cn += 1
        tax = config.get(
            "esop_tax_timing",
            "Tax at exercise (perquisite) + capital gains at sale",
        )
        dpiit = config.get("esop_dpiit_recognized", False)
        buyback = "shall" if config.get("esop_buyback_provision") else "shall not"
        tax_html = (
            f'<h2>{cn}. Taxation & Compliance</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'Tax treatment: {tax}.</p>'
        )
        if dpiit:
            tax_html += (
                f'<p class="clause"><span class="clause-number">{cn}.2</span> '
                f'The Company is a DPIIT-recognized startup. Eligible employees may '
                f'benefit from deferred perquisite taxation under Section 80-IAC of the '
                f'Income Tax Act, as amended by Finance Act 2020.</p>'
            )
        else:
            tax_html += (
                f'<p class="clause"><span class="clause-number">{cn}.2</span> '
                f'The Company is not currently DPIIT-recognized. Standard perquisite '
                f'tax rules shall apply at the time of exercise.</p>'
            )
        tax_html += (
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'The Company {buyback} have the right to buy back vested shares from '
            f'departing employees at fair market value as determined by an independent '
            f'registered valuer.</p>'
        )
        sections.append(tax_html)

        # Section 4 - Termination & Special Events
        cn += 1
        term_treat = config.get(
            "esop_termination_treatment",
            "Unvested options lapse, vested options exercisable for 90 days",
        )
        coc = config.get("esop_change_of_control", "No acceleration")
        death = config.get(
            "esop_death_disability",
            "Vested options exercisable by nominee for 1 year",
        )
        sections.append(
            f'<h2>{cn}. Termination & Special Events</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'On termination of employment: {term_treat}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'On change of control (acquisition/sale): {coc}.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'On death or permanent disability of the option holder: {death}.</p>'
        )

        # Section 5 - Administration
        cn += 1
        sections.append(
            f'<h2>{cn}. Administration</h2>'
            f'<p class="clause"><span class="clause-number">{cn}.1</span> '
            f'This Plan shall be administered by the Board of Directors or a '
            f'Compensation Committee appointed by the Board.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.2</span> '
            f'The Board shall have the authority to determine the number of options '
            f'to be granted, the exercise price, vesting schedule, and other terms '
            f'for each individual grant, subject to the overall terms of this Plan.</p>'
            f'<p class="clause"><span class="clause-number">{cn}.3</span> '
            f'This Plan has been approved by special resolution of the shareholders '
            f'in accordance with Section 62(1)(b) of the Companies Act 2013.</p>'
        )

        # Signature block
        sections.append(
            '<div class="signature-block"><h2>Authorization</h2>'
            '<p class="clause">Approved and adopted by the Board of Directors of '
            f'{company}.</p>'
            '<div class="signature-line"><div class="line"></div>'
            '<p><strong>Authorized Signatory</strong></p>'
            '<p>Name: ________________________</p>'
            '<p>Designation: ________________________</p>'
            '<p>Date: ________________________</p></div></div>'
        )

        body = "\n".join(sections)
        return self._base_html_wrap(
            f"Employee Stock Option Plan \u2014 {company}", body, eff_date
        )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
contract_template_service = ContractTemplateService()
