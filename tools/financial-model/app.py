"""
Anvils Financial Planning Model — Interactive Streamlit App

Run: streamlit run tools/financial-model/app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Anvils Financial Model",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Constants (from codebase) ────────────────────────────────────────────────

ENTITY_MIX_DEFAULT = {
    "Private Limited": 0.55,
    "LLP": 0.15,
    "OPC": 0.10,
    "Partnership": 0.08,
    "Sole Prop": 0.07,
    "Section 8": 0.03,
    "Public Limited": 0.02,
}

INCORP_PLATFORM_FEES = {
    "Private Limited": {"Launch": 4999, "Grow": 7999, "Scale": 12999},
    "LLP": {"Launch": 3999, "Grow": 6499, "Scale": 9999},
    "OPC": {"Launch": 3499, "Grow": 5499, "Scale": 8999},
    "Section 8": {"Launch": 7999, "Grow": 11999, "Scale": 17999},
    "Partnership": {"Launch": 2999, "Grow": 4999, "Scale": 7999},
    "Sole Prop": {"Launch": 499, "Grow": 999, "Scale": 0},
    "Public Limited": {"Launch": 9999, "Grow": 14999, "Scale": 24999},
}

TIER_MIX_DEFAULT = {"Launch": 0.60, "Grow": 0.30, "Scale": 0.10}

SUBSCRIPTION_PLANS_DEFAULT = {
    "Starter": {"monthly": 999, "annual": 9999, "target": "Sole Prop, Partnership"},
    "Growth": {"monthly": 2999, "annual": 29999, "target": "LLP, OPC"},
    "Scale": {"monthly": 4999, "annual": 49999, "target": "Private Limited"},
    "Enterprise": {"monthly": 9999, "annual": 99999, "target": "Public Ltd, Section 8"},
}

# Default roles with department, salary range, and description
DEFAULT_ROLES = [
    # Leadership
    {"role": "CEO / Founder", "dept": "Leadership", "min_ctc": 0, "max_ctc": 12_00_000, "default_ctc": 6_00_000, "default_count": 1, "required": True, "description": "Company direction, fundraising, strategy"},
    {"role": "COO / Operations Head", "dept": "Leadership", "min_ctc": 10_00_000, "max_ctc": 25_00_000, "default_ctc": 15_00_000, "default_count": 0, "required": False, "description": "Service delivery, SLAs, ops team management"},

    # Technology
    {"role": "CTO / Lead Engineer", "dept": "Technology", "min_ctc": 15_00_000, "max_ctc": 40_00_000, "default_ctc": 24_00_000, "default_count": 1, "required": True, "description": "Architecture, code reviews, infra, security"},
    {"role": "Senior Full-Stack Dev", "dept": "Technology", "min_ctc": 10_00_000, "max_ctc": 20_00_000, "default_ctc": 14_00_000, "default_count": 0, "required": False, "description": "Next.js + FastAPI features, API design"},
    {"role": "Mid Full-Stack Dev", "dept": "Technology", "min_ctc": 5_00_000, "max_ctc": 12_00_000, "default_ctc": 8_00_000, "default_count": 1, "required": False, "description": "Frontend pages, backend endpoints, bug fixes"},
    {"role": "Junior Developer", "dept": "Technology", "min_ctc": 2_50_000, "max_ctc": 6_00_000, "default_ctc": 4_00_000, "default_count": 0, "required": False, "description": "UI components, testing, documentation"},

    # Operations — Company Secretary
    {"role": "CS Lead", "dept": "Operations - CS", "min_ctc": 8_00_000, "max_ctc": 15_00_000, "default_ctc": 10_00_000, "default_count": 0, "required": False, "description": "Supervise CS team, quality control on filings"},
    {"role": "Senior CS", "dept": "Operations - CS", "min_ctc": 5_00_000, "max_ctc": 10_00_000, "default_ctc": 7_00_000, "default_count": 1, "required": True, "description": "ROC filings, board resolutions, name reservations"},
    {"role": "Junior CS", "dept": "Operations - CS", "min_ctc": 2_50_000, "max_ctc": 5_00_000, "default_ctc": 3_50_000, "default_count": 1, "required": False, "description": "Document prep, form filling, status tracking"},

    # Operations — Chartered Accountant
    {"role": "CA Lead", "dept": "Operations - CA", "min_ctc": 8_00_000, "max_ctc": 15_00_000, "default_ctc": 10_00_000, "default_count": 0, "required": False, "description": "Tax planning, audit coordination, review filings"},
    {"role": "Senior CA", "dept": "Operations - CA", "min_ctc": 5_00_000, "max_ctc": 10_00_000, "default_ctc": 7_00_000, "default_count": 1, "required": True, "description": "ITR, GST returns, TDS, statutory audit"},
    {"role": "Junior CA / Accountant", "dept": "Operations - CA", "min_ctc": 2_50_000, "max_ctc": 5_00_000, "default_ctc": 3_50_000, "default_count": 0, "required": False, "description": "Bookkeeping, data entry, return prep"},

    # Operations — Filing & Documents
    {"role": "Filing Lead", "dept": "Operations - Filing", "min_ctc": 4_00_000, "max_ctc": 8_00_000, "default_ctc": 5_00_000, "default_count": 0, "required": False, "description": "Manage filing queue, DSC coordination"},
    {"role": "Document Reviewer", "dept": "Operations - Filing", "min_ctc": 2_00_000, "max_ctc": 4_00_000, "default_ctc": 3_00_000, "default_count": 1, "required": True, "description": "KYC verification, document checks, uploads"},
    {"role": "DSC Coordinator", "dept": "Operations - Filing", "min_ctc": 2_00_000, "max_ctc": 4_00_000, "default_ctc": 2_50_000, "default_count": 0, "required": False, "description": "DSC procurement, token dispatch, video KYC"},

    # Customer Success
    {"role": "Customer Success Manager", "dept": "Customer Success", "min_ctc": 4_00_000, "max_ctc": 8_00_000, "default_ctc": 5_00_000, "default_count": 0, "required": False, "description": "Onboarding, support, retention, upsell"},
    {"role": "Customer Success Associate", "dept": "Customer Success", "min_ctc": 2_00_000, "max_ctc": 4_00_000, "default_ctc": 2_50_000, "default_count": 1, "required": False, "description": "Ticket handling, status updates, follow-ups"},

    # Marketing
    {"role": "Head of Marketing", "dept": "Marketing", "min_ctc": 10_00_000, "max_ctc": 20_00_000, "default_ctc": 12_00_000, "default_count": 0, "required": False, "description": "Strategy, channels, brand, CAC optimization"},
    {"role": "Content Writer / SEO", "dept": "Marketing", "min_ctc": 3_00_000, "max_ctc": 8_00_000, "default_ctc": 5_00_000, "default_count": 1, "required": False, "description": "Blog posts, landing pages, SEO articles"},
    {"role": "Performance Marketing", "dept": "Marketing", "min_ctc": 3_00_000, "max_ctc": 8_00_000, "default_ctc": 4_00_000, "default_count": 0, "required": False, "description": "Google Ads, Meta Ads, LinkedIn campaigns"},

    # Finance & Admin
    {"role": "Finance / Accounts", "dept": "Finance & Admin", "min_ctc": 2_00_000, "max_ctc": 5_00_000, "default_ctc": 3_00_000, "default_count": 0, "required": False, "description": "Internal bookkeeping, payroll, vendor payments"},
]


# ─── Session State Initialization ─────────────────────────────────────────────

def init_state():
    if "roles" not in st.session_state:
        st.session_state.roles = [
            {"role": r["role"], "dept": r["dept"], "count": r["default_count"],
             "ctc": r["default_ctc"], "description": r["description"],
             "min_ctc": r["min_ctc"], "max_ctc": r["max_ctc"], "required": r["required"]}
            for r in DEFAULT_ROLES
        ]
    if "sub_plans" not in st.session_state:
        st.session_state.sub_plans = {
            k: {"monthly": v["monthly"], "annual": v["annual"]}
            for k, v in SUBSCRIPTION_PLANS_DEFAULT.items()
        }


init_state()


# ─── Helper Functions ─────────────────────────────────────────────────────────

def format_inr(amount: float) -> str:
    """Format number in Indian Rupee style (lakhs/crores)."""
    if abs(amount) >= 1_00_00_000:
        return f"Rs {amount / 1_00_00_000:.2f} Cr"
    elif abs(amount) >= 1_00_000:
        return f"Rs {amount / 1_00_000:.2f}L"
    elif abs(amount) >= 1000:
        return f"Rs {amount / 1000:.1f}K"
    else:
        return f"Rs {amount:.0f}"


def format_inr_full(amount: float) -> str:
    """Format with full number."""
    if amount >= 1_00_00_000:
        return f"Rs {amount:,.0f} ({amount / 1_00_00_000:.2f} Cr)"
    elif amount >= 1_00_000:
        return f"Rs {amount:,.0f} ({amount / 1_00_000:.2f}L)"
    else:
        return f"Rs {amount:,.0f}"


def calc_blended_incorp_fee() -> float:
    """Calculate blended average incorporation platform fee."""
    total = 0
    for entity, mix_pct in ENTITY_MIX_DEFAULT.items():
        fees = INCORP_PLATFORM_FEES.get(entity, {})
        entity_avg = sum(
            fees.get(tier, 0) * tier_pct
            for tier, tier_pct in TIER_MIX_DEFAULT.items()
        )
        total += entity_avg * mix_pct
    return total


# ─── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.title("Anvils Financial Model")
st.sidebar.markdown("---")

# Growth assumptions
st.sidebar.header("Growth Assumptions")

months_to_model = st.sidebar.slider("Months to project", 12, 36, 24)

month1_incorporations = st.sidebar.number_input(
    "Month 1 incorporations", min_value=0, max_value=100, value=5, step=1
)
monthly_incorp_growth = st.sidebar.slider(
    "Monthly incorporation growth rate", 0, 50, 15, 1,
    help="% increase in new incorporations each month"
)
max_monthly_incorporations = st.sidebar.number_input(
    "Max incorporations/month (capacity)", min_value=10, max_value=500, value=100, step=10
)

st.sidebar.markdown("---")
st.sidebar.header("Subscription Assumptions")

sub_attach_rate = st.sidebar.slider(
    "% of incorporations that subscribe", 30, 90, 60, 5,
    help="What % of newly incorporated companies buy a compliance subscription"
)
annual_billing_pct = st.sidebar.slider(
    "% choosing annual billing", 30, 90, 70, 5,
    help="Higher annual billing = lower churn"
)
monthly_churn = st.sidebar.slider(
    "Monthly churn rate (%)", 0.0, 10.0, 3.0, 0.5,
    help="% of monthly-billed subscribers who cancel each month"
)
annual_churn = st.sidebar.slider(
    "Annual churn rate (%)", 0.0, 30.0, 15.0, 1.0,
    help="% of annual subscribers who don't renew"
)

st.sidebar.markdown("---")
st.sidebar.header("Services Marketplace")

services_attach_rate = st.sidebar.slider(
    "% buying add-on services", 10, 60, 25, 5,
    help="% of customers who buy at least 1 add-on service per year"
)
avg_service_value = st.sidebar.number_input(
    "Avg service order value (Rs)", min_value=500, max_value=20000, value=4000, step=500
)

st.sidebar.markdown("---")
st.sidebar.header("Other Costs")

monthly_tech_cost = st.sidebar.number_input(
    "Monthly tech infra cost (Rs)", min_value=10000, max_value=200000, value=45000, step=5000,
    help="GCP + third-party APIs"
)
monthly_marketing_spend = st.sidebar.number_input(
    "Monthly marketing spend (Rs)", min_value=0, max_value=500000, value=100000, step=10000,
    help="Google Ads, content, CA referrals, events"
)
monthly_office_cost = st.sidebar.number_input(
    "Monthly office / overhead (Rs)", min_value=0, max_value=200000, value=50000, step=5000,
    help="Coworking, tools, legal, misc"
)
razorpay_pct = st.sidebar.slider(
    "Payment gateway fee (%)", 0.0, 3.0, 2.0, 0.1,
    help="Razorpay TDR on all revenue"
)

free_incorp_pct = st.sidebar.slider(
    "% free incorporations (with annual plan)", 0, 80, 0, 5,
    help="Incorporation fee waived if they commit to annual compliance plan"
)


# ─── Main Content ─────────────────────────────────────────────────────────────

st.title("Anvils — Financial Planning Model")
st.caption("Interactive financial model for staffing, revenue, and P&L projections. Adjust inputs in the sidebar and staffing below.")

tab_staff, tab_pricing, tab_revenue, tab_unit, tab_pl, tab_scenario = st.tabs([
    "Staffing & Salaries",
    "Pricing Configuration",
    "Revenue Projections",
    "Unit Economics",
    "P&L Dashboard",
    "Scenario Analysis",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: STAFFING & SALARIES
# ══════════════════════════════════════════════════════════════════════════════

with tab_staff:
    st.header("Team & Salary Configuration")
    st.markdown("Configure your team. Toggle headcount and salary for each role to see the impact on total costs.")

    departments = list(dict.fromkeys(r["dept"] for r in st.session_state.roles))
    dept_totals = {}

    for dept in departments:
        dept_roles = [r for r in st.session_state.roles if r["dept"] == dept]
        with st.expander(f"**{dept}**", expanded=True):
            dept_cost = 0
            dept_heads = 0
            for i, role in enumerate(dept_roles):
                global_idx = st.session_state.roles.index(role)
                cols = st.columns([3, 1.5, 2, 2])
                with cols[0]:
                    st.markdown(f"**{role['role']}**")
                    st.caption(role["description"])
                with cols[1]:
                    count = st.number_input(
                        "Headcount",
                        min_value=0,
                        max_value=10,
                        value=role["count"],
                        step=1,
                        key=f"count_{global_idx}",
                        label_visibility="collapsed",
                    )
                    st.session_state.roles[global_idx]["count"] = count
                with cols[2]:
                    ctc = st.number_input(
                        "Annual CTC (Rs)",
                        min_value=role["min_ctc"],
                        max_value=role["max_ctc"],
                        value=role["ctc"],
                        step=50000,
                        key=f"ctc_{global_idx}",
                        label_visibility="collapsed",
                    )
                    st.session_state.roles[global_idx]["ctc"] = ctc
                    if count > 0:
                        st.caption(f"{format_inr(ctc)}/yr each")
                with cols[3]:
                    line_total = count * ctc
                    if count > 0:
                        st.metric("Line Total", format_inr(line_total))
                    else:
                        st.markdown("*Not hired*")
                    dept_cost += line_total
                    dept_heads += count
                st.markdown("---")

            dept_totals[dept] = {"cost": dept_cost, "heads": dept_heads}

    # Summary
    st.markdown("---")
    st.subheader("Salary Summary")

    total_salary = sum(d["cost"] for d in dept_totals.values())
    total_heads = sum(d["heads"] for d in dept_totals.values())

    col_summary = st.columns(3)
    with col_summary[0]:
        st.metric("Total Headcount", total_heads)
    with col_summary[1]:
        st.metric("Annual Salary Cost", format_inr(total_salary))
    with col_summary[2]:
        st.metric("Monthly Salary Burn", format_inr(total_salary / 12))

    # Department breakdown chart
    dept_df = pd.DataFrame([
        {"Department": dept, "Annual Cost": data["cost"], "Headcount": data["heads"]}
        for dept, data in dept_totals.items()
        if data["heads"] > 0
    ])

    if not dept_df.empty:
        col_charts = st.columns(2)
        with col_charts[0]:
            fig_pie = px.pie(
                dept_df, values="Annual Cost", names="Department",
                title="Salary Distribution by Department",
                hole=0.4,
            )
            fig_pie.update_traces(textinfo="label+percent", textposition="outside")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_charts[1]:
            fig_bar = px.bar(
                dept_df, x="Department", y="Annual Cost",
                title="Annual Cost by Department",
                text="Headcount",
                color="Department",
            )
            fig_bar.update_traces(texttemplate="<b>%{text} people</b>", textposition="outside")
            fig_bar.update_layout(showlegend=False, yaxis_title="Annual CTC (Rs)")
            st.plotly_chart(fig_bar, use_container_width=True)

    # Detailed role table
    with st.expander("View detailed role table"):
        role_data = []
        for r in st.session_state.roles:
            if r["count"] > 0:
                role_data.append({
                    "Role": r["role"],
                    "Department": r["dept"],
                    "Headcount": r["count"],
                    "CTC / Person": format_inr(r["ctc"]),
                    "Total Cost": format_inr(r["count"] * r["ctc"]),
                    "Monthly Cost": format_inr(r["count"] * r["ctc"] / 12),
                })
        if role_data:
            st.dataframe(pd.DataFrame(role_data), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: PRICING CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

with tab_pricing:
    st.header("Pricing Configuration")
    st.markdown("Adjust subscription plan pricing. Incorporation fees come from the codebase defaults.")

    st.subheader("Incorporation Platform Fees (from codebase)")
    incorp_df = pd.DataFrame([
        {"Entity": entity, "Launch": f"Rs {fees['Launch']:,}", "Grow": f"Rs {fees['Grow']:,}",
         "Scale": f"Rs {fees['Scale']:,}" if fees.get("Scale", 0) > 0 else "—"}
        for entity, fees in INCORP_PLATFORM_FEES.items()
    ])
    st.dataframe(incorp_df, use_container_width=True, hide_index=True)

    blended_fee = calc_blended_incorp_fee()
    st.info(f"**Blended avg incorporation fee** (weighted by entity mix & tier distribution): **{format_inr(blended_fee)}**")

    if free_incorp_pct > 0:
        effective_fee = blended_fee * (1 - free_incorp_pct / 100)
        st.warning(f"With {free_incorp_pct}% free incorporations, effective avg fee drops to **{format_inr(effective_fee)}**")

    st.markdown("---")
    st.subheader("Compliance Subscription Plans")
    st.markdown("Adjust pricing below. Changes update all projections instantly.")

    plan_cols = st.columns(len(st.session_state.sub_plans))
    for idx, (plan_name, plan_data) in enumerate(st.session_state.sub_plans.items()):
        with plan_cols[idx]:
            st.markdown(f"**{plan_name}**")
            st.caption(SUBSCRIPTION_PLANS_DEFAULT[plan_name]["target"])
            new_monthly = st.number_input(
                f"Monthly (Rs)",
                min_value=0,
                max_value=50000,
                value=plan_data["monthly"],
                step=100,
                key=f"plan_monthly_{plan_name}",
            )
            new_annual = st.number_input(
                f"Annual (Rs)",
                min_value=0,
                max_value=500000,
                value=plan_data["annual"],
                step=1000,
                key=f"plan_annual_{plan_name}",
            )
            st.session_state.sub_plans[plan_name]["monthly"] = new_monthly
            st.session_state.sub_plans[plan_name]["annual"] = new_annual
            if new_monthly > 0:
                months_equiv = new_annual / new_monthly
                st.caption(f"Annual = {months_equiv:.1f} months")

    # Subscription plan mix
    st.markdown("---")
    st.subheader("Subscription Plan Mix")
    st.markdown("What % of subscribers choose each plan?")

    if "plan_mix" not in st.session_state:
        st.session_state.plan_mix = {"Starter": 15, "Growth": 25, "Scale": 45, "Enterprise": 15}

    mix_cols = st.columns(len(st.session_state.plan_mix))
    for idx, plan_name in enumerate(st.session_state.plan_mix):
        with mix_cols[idx]:
            mix_val = st.number_input(
                f"{plan_name} (%)",
                min_value=0,
                max_value=100,
                value=st.session_state.plan_mix[plan_name],
                step=5,
                key=f"mix_{plan_name}",
            )
            st.session_state.plan_mix[plan_name] = mix_val

    mix_total = sum(st.session_state.plan_mix.values())
    if mix_total != 100:
        st.error(f"Plan mix must total 100%. Currently: {mix_total}%")
    else:
        # Calculate blended monthly subscription revenue per subscriber
        blended_sub = 0
        for plan_name, pct in st.session_state.plan_mix.items():
            plan = st.session_state.sub_plans[plan_name]
            # Weighted by annual vs monthly billing
            monthly_rev = plan["monthly"]
            annual_rev_per_month = plan["annual"] / 12
            effective_per_month = (
                monthly_rev * (1 - annual_billing_pct / 100)
                + annual_rev_per_month * (annual_billing_pct / 100)
            )
            blended_sub += effective_per_month * (pct / 100)

        st.success(f"**Blended monthly revenue per subscriber: {format_inr(blended_sub)}**")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: REVENUE PROJECTIONS
# ══════════════════════════════════════════════════════════════════════════════

with tab_revenue:
    st.header("Revenue Projections")

    # Calculate blended values
    blended_incorp = calc_blended_incorp_fee() * (1 - free_incorp_pct / 100)

    blended_sub_monthly = 0
    for plan_name, pct in st.session_state.plan_mix.items():
        plan = st.session_state.sub_plans[plan_name]
        monthly_rev = plan["monthly"]
        annual_rev_per_month = plan["annual"] / 12
        effective = (
            monthly_rev * (1 - annual_billing_pct / 100)
            + annual_rev_per_month * (annual_billing_pct / 100)
        )
        blended_sub_monthly += effective * (pct / 100)

    # Monthly projection model
    projections = []
    cumulative_subscribers = 0
    cumulative_revenue = 0

    for month in range(1, months_to_model + 1):
        # New incorporations this month (with growth cap)
        new_incorp = min(
            month1_incorporations * ((1 + monthly_incorp_growth / 100) ** (month - 1)),
            max_monthly_incorporations,
        )
        new_incorp = int(new_incorp)

        # New subscribers from this month's incorporations
        new_subs = int(new_incorp * sub_attach_rate / 100)

        # Churn: apply monthly churn to monthly-billed, annual churn spread monthly
        monthly_billed = cumulative_subscribers * (1 - annual_billing_pct / 100)
        annual_billed = cumulative_subscribers * (annual_billing_pct / 100)
        churned_monthly = monthly_billed * (monthly_churn / 100)
        churned_annual = annual_billed * ((annual_churn / 100) / 12)  # Spread annual churn monthly
        total_churned = int(churned_monthly + churned_annual)

        cumulative_subscribers = cumulative_subscribers + new_subs - total_churned
        cumulative_subscribers = max(0, cumulative_subscribers)

        # Revenue
        incorp_revenue = new_incorp * blended_incorp
        sub_revenue = cumulative_subscribers * blended_sub_monthly
        services_revenue = (cumulative_subscribers * services_attach_rate / 100 * avg_service_value) / 12
        total_revenue = incorp_revenue + sub_revenue + services_revenue

        # Costs
        salary_cost = total_salary / 12
        gateway_cost = total_revenue * (razorpay_pct / 100)
        total_cost = salary_cost + monthly_tech_cost + monthly_marketing_spend + monthly_office_cost + gateway_cost

        profit = total_revenue - total_cost
        cumulative_revenue += profit

        projections.append({
            "Month": month,
            "New Incorporations": new_incorp,
            "New Subscribers": new_subs,
            "Churned": total_churned,
            "Active Subscribers": cumulative_subscribers,
            "Incorporation Revenue": incorp_revenue,
            "Subscription Revenue": sub_revenue,
            "Services Revenue": services_revenue,
            "Total Revenue": total_revenue,
            "Salary Cost": salary_cost,
            "Tech Cost": monthly_tech_cost,
            "Marketing Cost": monthly_marketing_spend,
            "Office Cost": monthly_office_cost,
            "Gateway Fee": gateway_cost,
            "Total Cost": total_cost,
            "Monthly P&L": profit,
            "Cumulative P&L": cumulative_revenue,
        })

    proj_df = pd.DataFrame(projections)

    # Key metrics
    col_metrics = st.columns(4)
    final = projections[-1]
    with col_metrics[0]:
        st.metric("Final Month Revenue", format_inr(final["Total Revenue"]),
                   delta=f"{format_inr(final['Monthly P&L'])} profit" if final["Monthly P&L"] >= 0 else f"{format_inr(final['Monthly P&L'])} loss")
    with col_metrics[1]:
        st.metric("Active Subscribers (final)", f"{final['Active Subscribers']:,}")
    with col_metrics[2]:
        # Find break-even month
        be_month = None
        for p in projections:
            if p["Monthly P&L"] >= 0:
                be_month = p["Month"]
                break
        st.metric("Break-Even Month", f"Month {be_month}" if be_month else "Not in range")
    with col_metrics[3]:
        st.metric("Cumulative P&L", format_inr(final["Cumulative P&L"]))

    # Revenue chart
    st.subheader("Monthly Revenue Breakdown")
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Bar(x=proj_df["Month"], y=proj_df["Incorporation Revenue"],
                              name="Incorporation", marker_color="#4CAF50"))
    fig_rev.add_trace(go.Bar(x=proj_df["Month"], y=proj_df["Subscription Revenue"],
                              name="Subscriptions", marker_color="#2196F3"))
    fig_rev.add_trace(go.Bar(x=proj_df["Month"], y=proj_df["Services Revenue"],
                              name="Services", marker_color="#FF9800"))
    fig_rev.add_trace(go.Scatter(x=proj_df["Month"], y=proj_df["Total Cost"],
                                  name="Total Cost", line=dict(color="red", width=3, dash="dash")))
    fig_rev.update_layout(
        barmode="stack",
        title="Revenue vs Cost by Month",
        xaxis_title="Month",
        yaxis_title="Amount (Rs)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=500,
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    # Subscriber growth
    st.subheader("Subscriber Growth")
    fig_subs = make_subplots(specs=[[{"secondary_y": True}]])
    fig_subs.add_trace(
        go.Bar(x=proj_df["Month"], y=proj_df["New Subscribers"], name="New Subscribers",
               marker_color="#66BB6A", opacity=0.7),
        secondary_y=False,
    )
    fig_subs.add_trace(
        go.Bar(x=proj_df["Month"], y=-proj_df["Churned"], name="Churned",
               marker_color="#EF5350", opacity=0.7),
        secondary_y=False,
    )
    fig_subs.add_trace(
        go.Scatter(x=proj_df["Month"], y=proj_df["Active Subscribers"],
                    name="Active Subscribers", line=dict(color="#1565C0", width=3)),
        secondary_y=True,
    )
    fig_subs.update_layout(
        barmode="relative", title="Subscriber Acquisition & Churn",
        height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig_subs.update_yaxes(title_text="New / Churned", secondary_y=False)
    fig_subs.update_yaxes(title_text="Active Subscribers", secondary_y=True)
    st.plotly_chart(fig_subs, use_container_width=True)

    # Data table
    with st.expander("View monthly projection data"):
        display_df = proj_df.copy()
        money_cols = ["Incorporation Revenue", "Subscription Revenue", "Services Revenue",
                       "Total Revenue", "Salary Cost", "Tech Cost", "Marketing Cost",
                       "Office Cost", "Gateway Fee", "Total Cost", "Monthly P&L", "Cumulative P&L"]
        for col in money_cols:
            display_df[col] = display_df[col].apply(lambda x: format_inr(x))
        st.dataframe(display_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: UNIT ECONOMICS
# ══════════════════════════════════════════════════════════════════════════════

with tab_unit:
    st.header("Unit Economics")
    st.markdown("How much does it cost to acquire and serve each customer, and what do they generate in revenue?")

    # Calculate ops capacity
    ops_roles = [r for r in st.session_state.roles if r["dept"].startswith("Operations")]
    ops_heads = sum(r["count"] for r in ops_roles)
    ops_salary = sum(r["count"] * r["ctc"] for r in ops_roles)

    cs_roles = [r for r in st.session_state.roles if r["dept"] == "Customer Success"]
    cs_heads = sum(r["count"] for r in cs_roles)

    # Capacity estimates
    clients_per_cs = 30  # CS staff can handle ~30 active accounts
    clients_per_ops = 25  # Ops team member handles ~25 companies

    max_clients_cs = max(cs_heads * clients_per_cs, 50)  # Assume founder handles CS if no one hired
    max_clients_ops = ops_heads * clients_per_ops if ops_heads > 0 else 15

    service_capacity = min(max_clients_cs, max_clients_ops) if ops_heads > 0 else 15

    col_cap = st.columns(3)
    with col_cap[0]:
        st.metric("Ops Team Size", ops_heads)
    with col_cap[1]:
        st.metric("Max Active Clients (capacity)", service_capacity)
    with col_cap[2]:
        cost_per_client_month = (ops_salary / 12) / max(service_capacity, 1)
        st.metric("Ops Cost / Client / Month", format_inr(cost_per_client_month))

    st.markdown("---")
    st.subheader("Cost to Serve Per Customer Per Month")

    # Per-plan cost to serve
    plan_analysis = []
    for plan_name, plan_data in st.session_state.sub_plans.items():
        monthly_rev = plan_data["monthly"]
        annual_rev_per_month = plan_data["annual"] / 12
        effective_rev = (
            monthly_rev * (1 - annual_billing_pct / 100)
            + annual_rev_per_month * (annual_billing_pct / 100)
        )
        plan_pct = st.session_state.plan_mix.get(plan_name, 25) / 100

        # Estimate professional time needed by plan tier
        time_multiplier = {
            "Starter": 0.5,
            "Growth": 1.0,
            "Scale": 1.5,
            "Enterprise": 2.5,
        }.get(plan_name, 1.0)

        direct_cost = cost_per_client_month * time_multiplier
        gateway = effective_rev * razorpay_pct / 100
        tech_alloc = monthly_tech_cost / max(service_capacity, 1)
        total_cost_per = direct_cost + gateway + tech_alloc

        margin = effective_rev - total_cost_per
        margin_pct = (margin / effective_rev * 100) if effective_rev > 0 else 0

        plan_analysis.append({
            "Plan": plan_name,
            "Monthly Revenue": effective_rev,
            "Professional Cost": direct_cost,
            "Gateway Fee": gateway,
            "Tech Allocation": tech_alloc,
            "Total Cost": total_cost_per,
            "Margin": margin,
            "Margin %": margin_pct,
            "Mix %": plan_pct * 100,
        })

    plan_df = pd.DataFrame(plan_analysis)

    # Display as colored table
    for _, row in plan_df.iterrows():
        cols = st.columns([2, 2, 2, 2, 2])
        with cols[0]:
            st.markdown(f"**{row['Plan']}**")
            st.caption(f"Mix: {row['Mix %']:.0f}%")
        with cols[1]:
            st.metric("Revenue/mo", format_inr(row["Monthly Revenue"]))
        with cols[2]:
            st.metric("Cost/mo", format_inr(row["Total Cost"]))
        with cols[3]:
            color = "normal" if row["Margin"] >= 0 else "inverse"
            st.metric("Margin/mo", format_inr(row["Margin"]), delta=f"{row['Margin %']:.0f}%")
        with cols[4]:
            if row["Margin %"] < 0:
                st.error("LOSS MAKER")
            elif row["Margin %"] < 20:
                st.warning("Low margin")
            elif row["Margin %"] < 40:
                st.info("Healthy")
            else:
                st.success("High margin")

    # Margin chart
    st.markdown("---")
    fig_margin = go.Figure()
    fig_margin.add_trace(go.Bar(
        x=plan_df["Plan"], y=plan_df["Monthly Revenue"],
        name="Revenue", marker_color="#4CAF50",
    ))
    fig_margin.add_trace(go.Bar(
        x=plan_df["Plan"], y=plan_df["Total Cost"],
        name="Cost", marker_color="#F44336",
    ))
    fig_margin.update_layout(
        barmode="group", title="Revenue vs Cost by Plan",
        yaxis_title="Rs / month / customer", height=400,
    )
    st.plotly_chart(fig_margin, use_container_width=True)

    # LTV Analysis
    st.markdown("---")
    st.subheader("Customer Lifetime Value (LTV)")

    effective_monthly_churn = (
        (1 - annual_billing_pct / 100) * (monthly_churn / 100)
        + (annual_billing_pct / 100) * ((annual_churn / 100) / 12)
    )
    avg_lifetime_months = 1 / effective_monthly_churn if effective_monthly_churn > 0 else 60

    blended_rev = sum(r["Monthly Revenue"] * r["Mix %"] / 100 for _, r in plan_df.iterrows())
    blended_cost = sum(r["Total Cost"] * r["Mix %"] / 100 for _, r in plan_df.iterrows())

    ltv_revenue = blended_rev * min(avg_lifetime_months, 60) + blended_incorp
    ltv_cost = blended_cost * min(avg_lifetime_months, 60)
    ltv_margin = ltv_revenue - ltv_cost

    cac_estimate = monthly_marketing_spend / max(month1_incorporations * 2, 1)  # rough mid-range

    col_ltv = st.columns(4)
    with col_ltv[0]:
        st.metric("Avg Customer Lifetime", f"{min(avg_lifetime_months, 60):.0f} months")
    with col_ltv[1]:
        st.metric("LTV (Revenue)", format_inr(ltv_revenue))
    with col_ltv[2]:
        st.metric("CAC (estimated)", format_inr(cac_estimate))
    with col_ltv[3]:
        ltv_cac = ltv_revenue / cac_estimate if cac_estimate > 0 else 0
        st.metric("LTV:CAC Ratio", f"{ltv_cac:.1f}x",
                   delta="Healthy" if ltv_cac >= 3 else "Needs improvement")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: P&L DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

with tab_pl:
    st.header("Profit & Loss Dashboard")

    # Annual summary
    years_data = []
    for year in range(1, (months_to_model // 12) + 1):
        start = (year - 1) * 12
        end = min(year * 12, len(projections))
        year_rows = projections[start:end]

        yr = {
            "Year": year,
            "Incorporations": sum(r["New Incorporations"] for r in year_rows),
            "End Subscribers": year_rows[-1]["Active Subscribers"] if year_rows else 0,
            "Incorporation Revenue": sum(r["Incorporation Revenue"] for r in year_rows),
            "Subscription Revenue": sum(r["Subscription Revenue"] for r in year_rows),
            "Services Revenue": sum(r["Services Revenue"] for r in year_rows),
            "Total Revenue": sum(r["Total Revenue"] for r in year_rows),
            "Salary Cost": sum(r["Salary Cost"] for r in year_rows),
            "Tech Cost": sum(r["Tech Cost"] for r in year_rows),
            "Marketing Cost": sum(r["Marketing Cost"] for r in year_rows),
            "Office Cost": sum(r["Office Cost"] for r in year_rows),
            "Gateway Fee": sum(r["Gateway Fee"] for r in year_rows),
            "Total Cost": sum(r["Total Cost"] for r in year_rows),
        }
        yr["Net Profit"] = yr["Total Revenue"] - yr["Total Cost"]
        yr["Margin %"] = (yr["Net Profit"] / yr["Total Revenue"] * 100) if yr["Total Revenue"] > 0 else 0
        years_data.append(yr)

    # Year summary cards
    year_cols = st.columns(len(years_data))
    for idx, yr in enumerate(years_data):
        with year_cols[idx]:
            st.subheader(f"Year {yr['Year']}")
            st.metric("Revenue", format_inr(yr["Total Revenue"]))
            st.metric("Cost", format_inr(yr["Total Cost"]))
            pnl_delta = "Profit" if yr["Net Profit"] >= 0 else "Loss"
            st.metric("Net P&L", format_inr(yr["Net Profit"]),
                       delta=f"{yr['Margin %']:.0f}% margin")
            st.metric("Subscribers (end)", yr["End Subscribers"])
            st.metric("Incorporations", yr["Incorporations"])

    # P&L waterfall
    st.markdown("---")
    st.subheader("Cost Structure Breakdown")

    for yr in years_data:
        with st.expander(f"**Year {yr['Year']} — Detailed P&L**", expanded=(yr["Year"] == 1)):
            fig_waterfall = go.Figure(go.Waterfall(
                name="P&L",
                orientation="v",
                measure=["absolute", "absolute", "absolute", "total",
                          "absolute", "absolute", "absolute", "absolute", "absolute", "total",
                          "total"],
                x=["Incorporation Rev", "Subscription Rev", "Services Rev", "Total Revenue",
                    "Salaries", "Tech Infra", "Marketing", "Office/Overhead", "Gateway Fees", "Total Costs",
                    "Net P&L"],
                y=[yr["Incorporation Revenue"], yr["Subscription Revenue"], yr["Services Revenue"], None,
                   -yr["Salary Cost"], -yr["Tech Cost"], -yr["Marketing Cost"],
                   -yr["Office Cost"], -yr["Gateway Fee"], None,
                   None],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": "#4CAF50"}},
                decreasing={"marker": {"color": "#F44336"}},
                totals={"marker": {"color": "#2196F3"}},
            ))
            fig_waterfall.update_layout(
                title=f"Year {yr['Year']} P&L Waterfall",
                height=450,
                showlegend=False,
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)

            # Cost breakdown pie
            cost_breakdown = {
                "Salaries": yr["Salary Cost"],
                "Technology": yr["Tech Cost"],
                "Marketing": yr["Marketing Cost"],
                "Office/Overhead": yr["Office Cost"],
                "Payment Gateway": yr["Gateway Fee"],
            }
            cost_df = pd.DataFrame([
                {"Category": k, "Amount": v} for k, v in cost_breakdown.items() if v > 0
            ])
            if not cost_df.empty:
                fig_cost_pie = px.pie(cost_df, values="Amount", names="Category",
                                      title=f"Year {yr['Year']} Cost Breakdown")
                fig_cost_pie.update_traces(textinfo="label+percent", textposition="outside")
                st.plotly_chart(fig_cost_pie, use_container_width=True)

    # Cumulative P&L chart
    st.markdown("---")
    st.subheader("Cumulative Profit / Loss Over Time")
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=proj_df["Month"], y=proj_df["Cumulative P&L"],
        fill="tozeroy",
        fillcolor="rgba(76, 175, 80, 0.3)" if projections[-1]["Cumulative P&L"] >= 0 else "rgba(244, 67, 54, 0.3)",
        line=dict(color="#4CAF50" if projections[-1]["Cumulative P&L"] >= 0 else "#F44336", width=3),
        name="Cumulative P&L",
    ))
    fig_cum.add_hline(y=0, line_dash="dash", line_color="gray")

    # Mark break-even
    for p in projections:
        if p["Cumulative P&L"] >= 0:
            fig_cum.add_annotation(
                x=p["Month"], y=0,
                text=f"Cumulative break-even: Month {p['Month']}",
                showarrow=True, arrowhead=2,
                bgcolor="yellow",
            )
            break

    fig_cum.update_layout(
        title="Cumulative P&L",
        xaxis_title="Month", yaxis_title="Rs",
        height=400,
    )
    st.plotly_chart(fig_cum, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: SCENARIO ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

with tab_scenario:
    st.header("Scenario Analysis")
    st.markdown("Compare the impact of different decisions side-by-side.")

    st.subheader("What-If: Minimum Viable Team")

    # Calculate minimum team
    min_team = [r for r in st.session_state.roles if r["required"] and r["count"] > 0]
    min_salary = sum(r["ctc"] * r["count"] for r in min_team)
    min_heads = sum(r["count"] for r in min_team)

    current_salary = total_salary
    current_heads = total_heads

    col_min = st.columns(2)
    with col_min[0]:
        st.markdown("**Current Team**")
        st.metric("Headcount", current_heads)
        st.metric("Annual Salary", format_inr(current_salary))
        st.metric("Monthly Burn (salary only)", format_inr(current_salary / 12))

    with col_min[1]:
        st.markdown("**Minimum Required Team** (marked as required)")
        st.metric("Headcount", min_heads)
        st.metric("Annual Salary", format_inr(min_salary))
        st.metric("Monthly Savings", format_inr((current_salary - min_salary) / 12))

    st.markdown("---")
    st.subheader("What-If: Free Incorporation Impact")

    # Compare 0% free vs 40% free vs 80% free
    scenarios = [
        {"name": "No free incorporations", "free_pct": 0},
        {"name": "40% free (with annual plan)", "free_pct": 40},
        {"name": "80% free (aggressive)", "free_pct": 80},
    ]

    # For each scenario, calculate Year 1 and Year 2 revenue
    blended_fee_full = calc_blended_incorp_fee()

    scenario_results = []
    for scenario in scenarios:
        effective_fee = blended_fee_full * (1 - scenario["free_pct"] / 100)
        # If free incorp, assume higher attach rate
        adjusted_attach = min(sub_attach_rate + scenario["free_pct"] * 0.3, 95)

        yr1_incorp_rev = 0
        yr1_sub_rev = 0
        yr2_sub_rev = 0
        cum_subs = 0

        for month in range(1, 25):
            new_incorp = min(
                month1_incorporations * ((1 + monthly_incorp_growth / 100) ** (month - 1)),
                max_monthly_incorporations,
            )
            new_subs = int(new_incorp * adjusted_attach / 100)

            monthly_billed = cum_subs * (1 - annual_billing_pct / 100)
            annual_billed = cum_subs * (annual_billing_pct / 100)
            churned = int(monthly_billed * (monthly_churn / 100) + annual_billed * ((annual_churn / 100) / 12))
            cum_subs = max(0, cum_subs + new_subs - churned)

            incorp_rev = new_incorp * effective_fee
            sub_rev = cum_subs * blended_sub_monthly if "blended_sub_monthly" in dir() else cum_subs * 3500

            if month <= 12:
                yr1_incorp_rev += incorp_rev
                yr1_sub_rev += sub_rev
            else:
                yr2_sub_rev += sub_rev

        scenario_results.append({
            "Scenario": scenario["name"],
            "Attach Rate": f"{adjusted_attach:.0f}%",
            "Y1 Incorp Revenue": yr1_incorp_rev,
            "Y1 Sub Revenue": yr1_sub_rev,
            "Y1 Total": yr1_incorp_rev + yr1_sub_rev,
            "Y2 Sub Revenue": yr2_sub_rev,
            "End Subscribers (M24)": cum_subs,
        })

    scenario_df = pd.DataFrame(scenario_results)

    # Display scenarios
    scen_cols = st.columns(len(scenario_results))
    for idx, scen in enumerate(scenario_results):
        with scen_cols[idx]:
            st.markdown(f"**{scen['Scenario']}**")
            st.caption(f"Attach rate: {scen['Attach Rate']}")
            st.metric("Year 1 Revenue", format_inr(scen["Y1 Total"]))
            st.metric("Year 2 Sub Revenue", format_inr(scen["Y2 Sub Revenue"]))
            st.metric("Subscribers (Month 24)", f"{scen['End Subscribers (M24)']:,}")

    st.info("Free incorporations reduce Year 1 revenue but increase subscriber attach rate, "
            "leading to higher recurring revenue in Year 2+. The trade-off typically pays back within 12-18 months.")

    # Staffing scenario comparison
    st.markdown("---")
    st.subheader("Staffing Scenarios: Revenue Per Employee")

    if total_heads > 0:
        rev_per_employee = final["Total Revenue"] * 12 / total_heads

        st.markdown(f"""
        | Metric | Value |
        |---|---|
        | Current headcount | {total_heads} |
        | Projected annual revenue (current month rate) | {format_inr(final['Total Revenue'] * 12)} |
        | **Revenue per employee** | **{format_inr(rev_per_employee)}** |
        | Target (healthy SaaS) | Rs 20-40L per employee |
        | Current capacity (max clients) | ~{service_capacity} active companies |
        | Utilization (at {final['Active Subscribers']} subscribers) | {min(final['Active Subscribers'] / max(service_capacity, 1) * 100, 100):.0f}% |
        """)

        if rev_per_employee < 10_00_000:
            st.warning("Revenue per employee is below Rs 10L. Either revenue needs to grow or team needs to be leaner.")
        elif rev_per_employee < 20_00_000:
            st.info("Revenue per employee is between Rs 10-20L. Approaching healthy levels.")
        else:
            st.success("Revenue per employee is above Rs 20L. Healthy unit economics.")

    # Key recommendations
    st.markdown("---")
    st.subheader("Key Recommendations Based on Current Configuration")

    recommendations = []

    # Check if Starter plan is profitable
    starter_data = next((r for _, r in plan_df.iterrows() if r["Plan"] == "Starter"), None)
    if starter_data is not None and starter_data["Margin"] < 0:
        recommendations.append(
            f"**Starter plan is losing Rs {abs(starter_data['Margin']):.0f}/customer/month.** "
            f"Consider raising price to Rs {int(starter_data['Total Cost'] * 1.2)}/month or reducing scope."
        )

    # Check team size vs revenue
    if total_heads > 0 and final["Total Revenue"] * 12 / total_heads < 15_00_000:
        recommendations.append(
            "**Team is oversized for projected revenue.** Consider delaying hires until "
            f"subscriber count exceeds {service_capacity * 0.7:.0f}."
        )

    # Check if break-even is too far
    if be_month and be_month > 18:
        recommendations.append(
            f"**Break-even at Month {be_month} is late.** Reduce monthly burn or increase "
            "subscriber growth rate. Target: break-even by Month 12-14."
        )
    elif be_month is None:
        recommendations.append(
            "**No break-even in projection range.** Revenue growth is too slow or costs are "
            "too high. Reduce headcount or increase pricing."
        )

    # Check salary as % of cost
    salary_pct = (total_salary / 12) / final["Total Cost"] * 100 if final["Total Cost"] > 0 else 0
    if salary_pct > 70:
        recommendations.append(
            f"**Salaries are {salary_pct:.0f}% of total costs.** This is high even for a services "
            "business. Automation of document review and form filling should be prioritized."
        )

    # Check marketing efficiency
    if monthly_marketing_spend > 0 and month1_incorporations > 0:
        cac = monthly_marketing_spend / month1_incorporations
        if cac > 10000:
            recommendations.append(
                f"**CAC is Rs {cac:,.0f} which is high.** Focus on CA channel (CAC Rs 200-500) "
                "and SEO (zero marginal CAC) over paid ads."
            )

    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.success("Configuration looks healthy. No major flags.")


# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(
    "Anvils Financial Model v1.0 | Data sourced from `pricing_engine.py` and `services_catalog.py` | "
    "Adjust inputs in the sidebar and staffing tab to model different scenarios."
)
