"""Compliance Autopilot Engine — generates compliance calendars and tracks deadlines.

Master compliance rules database for all Indian entity types with automatic
deadline calculation, penalty estimation, and compliance health scoring.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.models.company import Company, EntityType
from src.models.compliance_task import ComplianceTask, ComplianceTaskType, ComplianceTaskStatus
from src.models.user import User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Master Compliance Rules
# ---------------------------------------------------------------------------

COMPLIANCE_RULES: Dict[str, Any] = {
    "private_limited": [
        # ── ROC Annual Filings ─────────────────────────────────────────
        {
            "type": "aoc_4",
            "title": "AOC-4 (Financial Statements)",
            "frequency": "annual",
            "due_rule": "within_30_days_of_agm",
            "description": (
                "File financial statements (Balance Sheet, P&L, Cash Flow, Notes) "
                "with ROC within 30 days of AGM. (Companies Act 2013, § 137)"
            ),
            "penalty_per_day": 100,
            "max_penalty": 1000000,  # Rs 10 lakh cap per MCA
            "section": "137",
        },
        {
            "type": "mgt_7",
            "title": "MGT-7 (Annual Return)",
            "frequency": "annual",
            "due_rule": "within_60_days_of_agm",
            "description": (
                "File annual return with ROC within 60 days of AGM. Contains "
                "company details, shareholding pattern, and director info. (§ 92)"
            ),
            "penalty_per_day": 100,
            "max_penalty": 500000,  # Rs 5 lakh cap per § 92(5)
            "section": "92",
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC (Director KYC)",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": (
                "Every DIN holder must file DIR-3 KYC annually by September 30. "
                "First-time filers use DIR-3 KYC (web form for subsequent years). "
                "Failure leads to DIN deactivation. (Rule 12A, Companies (Appointment "
                "and Qualification of Directors) Rules, 2014)"
            ),
            "penalty_per_day": 0,
            "penalty_late_fee": 5000,
            "section": "Rule 12A",
        },
        {
            "type": "adt_1_renewal",
            "title": "ADT-1 (Auditor Appointment)",
            "frequency": "annual",
            "due_rule": "within_15_days_of_agm",
            "description": (
                "File notice of auditor appointment/reappointment within 15 days "
                "of AGM. (§ 139(1), Rule 4 of Companies (Audit and Auditors) Rules)"
            ),
            "penalty_per_day": 100,
            "max_penalty": None,
            "section": "139",
        },
        # ── Board Meetings (§ 173) ─────────────────────────────────────
        # Section 173(1): Minimum 4 board meetings per year.
        # Maximum gap between two consecutive meetings: 120 days.
        # Using quarter-end dates as suggested deadlines, but the 120-day
        # gap rule is the actual legal requirement.
        {
            "type": "board_meeting_q1",
            "title": "Board Meeting — Q1 (Apr-Jun)",
            "frequency": "quarterly",
            "due_rule": "june_30",
            "description": (
                "Minimum 4 board meetings per year, with max 120-day gap between "
                "consecutive meetings. (§ 173(1)). Penalty: Rs 25,000 on company + "
                "Rs 5,000 per director for each default."
            ),
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
            "section": "173",
        },
        {
            "type": "board_meeting_q2",
            "title": "Board Meeting — Q2 (Jul-Sep)",
            "frequency": "quarterly",
            "due_rule": "september_30",
            "description": "Quarterly board meeting. Max 120-day gap rule applies. (§ 173(1))",
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
        },
        {
            "type": "board_meeting_q3",
            "title": "Board Meeting — Q3 (Oct-Dec)",
            "frequency": "quarterly",
            "due_rule": "december_31",
            "description": "Quarterly board meeting. Max 120-day gap rule applies. (§ 173(1))",
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
        },
        {
            "type": "board_meeting_q4",
            "title": "Board Meeting — Q4 (Jan-Mar)",
            "frequency": "quarterly",
            "due_rule": "march_31",
            "description": "Quarterly board meeting. Max 120-day gap rule applies. (§ 173(1))",
            "penalty_per_day": 0,
            "penalty_fixed": 25000,
        },
        # ── AGM (§ 96) ────────────────────────────────────────────────
        {
            "type": "agm",
            "title": "Annual General Meeting",
            "frequency": "annual",
            "due_rule": "agm_dynamic",
            "description": (
                "First AGM: within 9 months from close of first FY (§ 96(1)). "
                "Subsequent AGMs: within 6 months of FY end AND within 15 months "
                "of last AGM. Max gap between two AGMs: 15 months. "
                "Penalty: up to Rs 1 lakh on company + Rs 5,000/day for "
                "continuing default. (§ 99)"
            ),
            "penalty_per_day": 5000,
            "penalty_fixed": 100000,
            "section": "96, 99",
        },
        # ── Income Tax ─────────────────────────────────────────────────
        {
            "type": "itr_filing",
            "title": "Income Tax Return",
            "frequency": "annual",
            "due_rule": "october_31",
            "description": (
                "File ITR by October 31 (companies subject to audit under § 44AB) "
                "or July 31 (otherwise). (Income Tax Act § 139(1)). "
                "Late fee: Rs 5,000 (if filed by Dec 31) or Rs 10,000 (after). "
                "Interest: 1% per month under § 234A."
            ),
            "penalty_per_day": 0,
            "penalty_late_fee": 10000,
        },
        # ── Advance Tax (§ 208-211, IT Act) ────────────────────────────
        {
            "type": "advance_tax_q1",
            "title": "Advance Tax — Q1 (15%)",
            "frequency": "quarterly",
            "due_rule": "june_15",
            "description": "Pay 15% of estimated annual tax liability. (IT Act § 211)",
            "penalty_interest": "1% per month under § 234C",
        },
        {
            "type": "advance_tax_q2",
            "title": "Advance Tax — Q2 (45% cumulative)",
            "frequency": "quarterly",
            "due_rule": "september_15",
            "description": "Cumulative 45% of estimated tax liability. (IT Act § 211)",
        },
        {
            "type": "advance_tax_q3",
            "title": "Advance Tax — Q3 (75% cumulative)",
            "frequency": "quarterly",
            "due_rule": "december_15",
            "description": "Cumulative 75% of estimated tax liability. (IT Act § 211)",
        },
        {
            "type": "advance_tax_q4",
            "title": "Advance Tax — Q4 (100%)",
            "frequency": "quarterly",
            "due_rule": "march_15",
            "description": "Full 100% of estimated tax liability due. (IT Act § 211)",
        },
        # ── TDS Returns (IT Act § 200) ────────────────────────────────
        {
            "type": "tds_return_q1",
            "title": "TDS Return — Q1 (Apr-Jun)",
            "frequency": "quarterly",
            "due_rule": "july_31",
            "description": (
                "File quarterly TDS return (24Q/26Q/27Q). Late fee: Rs 200/day "
                "under § 234E (capped at TDS amount). Penalty up to Rs 1 lakh "
                "under § 271H for failure to file."
            ),
            "penalty_per_day": 200,
            "max_penalty": None,
        },
        {
            "type": "tds_return_q2",
            "title": "TDS Return — Q2 (Jul-Sep)",
            "frequency": "quarterly",
            "due_rule": "october_31",
            "description": "File quarterly TDS return for Q2. (IT Act § 200(3))",
            "penalty_per_day": 200,
        },
        {
            "type": "tds_return_q3",
            "title": "TDS Return — Q3 (Oct-Dec)",
            "frequency": "quarterly",
            "due_rule": "january_31",
            "description": "File quarterly TDS return for Q3. (IT Act § 200(3))",
            "penalty_per_day": 200,
        },
        {
            "type": "tds_return_q4",
            "title": "TDS Return — Q4 (Jan-Mar)",
            "frequency": "quarterly",
            "due_rule": "may_31",
            "description": "File quarterly TDS return for Q4. (IT Act § 200(3))",
            "penalty_per_day": 200,
        },
        {
            "type": "form_16",
            "title": "Form 16 / 16A Issuance",
            "frequency": "annual",
            "due_rule": "june_15",
            "description": (
                "Issue Form 16 (salary TDS certificate) to employees and "
                "Form 16A (non-salary TDS) to vendors by June 15. (IT Act § 203)"
            ),
        },
    ],

    "opc": [
        # OPC is exempt from AGM (§ 96(1) proviso) but must file AOC-4
        # within 180 days of FY end (§ 137 read with Rule 12 proviso).
        {
            "type": "aoc_4",
            "title": "AOC-4 (Financial Statements — OPC)",
            "frequency": "annual",
            "due_rule": "within_180_days_of_fy_end",
            "description": (
                "OPC files AOC-4 within 180 days from close of FY (no AGM "
                "required). (§ 137, OPC proviso)"
            ),
            "penalty_per_day": 100,
            "section": "137",
        },
        {
            "type": "mgt_7",
            "title": "MGT-7A (Annual Return — OPC)",
            "frequency": "annual",
            "due_rule": "within_60_days_of_fy_end_plus_180",
            "description": (
                "OPC files simplified MGT-7A within 60 days from date of "
                "AOC-4 filing. (§ 92)"
            ),
            "penalty_per_day": 100,
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC (Director KYC)",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": "Director must file annual KYC by Sep 30. Late fee: Rs 5,000.",
            "penalty_late_fee": 5000,
        },
        # OPC with 2+ board meetings per year (§ 173(5) exemption: only
        # 1 meeting per half-year required, minimum 90-day gap)
        {
            "type": "board_meeting_h1",
            "title": "Board Meeting — H1 (Apr-Sep)",
            "frequency": "semi_annual",
            "due_rule": "september_30",
            "description": (
                "OPC: minimum 1 board meeting per half-year, minimum 90-day gap. "
                "(§ 173(5) proviso for OPC)"
            ),
            "penalty_fixed": 25000,
        },
        {
            "type": "board_meeting_h2",
            "title": "Board Meeting — H2 (Oct-Mar)",
            "frequency": "semi_annual",
            "due_rule": "march_31",
            "description": "OPC: Second half-year board meeting. (§ 173(5) proviso)",
            "penalty_fixed": 25000,
        },
        {
            "type": "itr_filing",
            "title": "Income Tax Return",
            "frequency": "annual",
            "due_rule": "october_31",
            "description": "File ITR by Oct 31 (if audit applicable) or Jul 31.",
            "penalty_late_fee": 10000,
        },
    ],

    "llp": [
        # LLP Act 2008, Rule 24 & 25 of LLP Rules 2009
        {
            "type": "form_11",
            "title": "Form 11 (LLP Annual Return)",
            "frequency": "annual",
            "due_rule": "may_30",
            "description": (
                "File LLP Annual Return within 60 days of FY end (i.e., by May 30). "
                "(LLP Act § 35, Rule 25 of LLP Rules 2009). "
                "Late fee: Rs 100/day of delay (no cap)."
            ),
            "penalty_per_day": 100,
        },
        {
            "type": "form_8",
            "title": "Form 8 (Statement of Account & Solvency)",
            "frequency": "annual",
            "due_rule": "october_30",
            "description": (
                "File Statement of Account & Solvency within 30 days from end of "
                "6 months of FY end (i.e., by Oct 30 for March FY end). "
                "(LLP Act § 34, Rule 24 of LLP Rules 2009). "
                "Late fee: Rs 100/day of delay."
            ),
            "penalty_per_day": 100,
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC (Partner KYC)",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": (
                "All DPIN holders must file annual KYC by September 30. "
                "Late fee: Rs 5,000, DPIN deactivated until filed."
            ),
            "penalty_late_fee": 5000,
        },
        {
            "type": "itr_filing",
            "title": "Income Tax Return (ITR-5)",
            "frequency": "annual",
            "due_rule": "october_31",
            "description": (
                "LLP files ITR-5 by Oct 31 (if audit applicable under § 44AB, "
                "i.e., turnover > Rs 1 crore) or Jul 31 (otherwise)."
            ),
            "penalty_late_fee": 10000,
        },
    ],

    "section_8": [
        {
            "type": "aoc_4",
            "title": "AOC-4 (Financial Statements)",
            "frequency": "annual",
            "due_rule": "within_30_days_of_agm",
            "description": "File financial statements with ROC within 30 days of AGM. (§ 137)",
            "penalty_per_day": 100,
            "max_penalty": 1000000,
        },
        {
            "type": "mgt_7",
            "title": "MGT-7 (Annual Return)",
            "frequency": "annual",
            "due_rule": "within_60_days_of_agm",
            "description": "File annual return within 60 days of AGM. (§ 92)",
            "penalty_per_day": 100,
        },
        {
            "type": "dir_3_kyc",
            "title": "DIR-3 KYC",
            "frequency": "annual",
            "due_rule": "september_30",
            "description": "Director annual KYC by September 30.",
            "penalty_late_fee": 5000,
        },
        {
            "type": "agm",
            "title": "Annual General Meeting",
            "frequency": "annual",
            "due_rule": "agm_dynamic",
            "description": (
                "First AGM within 9 months of first FY close; subsequent AGMs "
                "within 6 months of FY end. (§ 96)"
            ),
            "penalty_fixed": 100000,
        },
        # Section 8 companies: minimum 2 board meetings per year (§ 173(5))
        {
            "type": "board_meeting_h1",
            "title": "Board Meeting — H1 (Apr-Sep)",
            "frequency": "semi_annual",
            "due_rule": "september_30",
            "description": (
                "Section 8 company: minimum 1 board meeting per half-year, "
                "minimum 90-day gap. (§ 173(5) exemption for Section 8)"
            ),
            "penalty_fixed": 25000,
        },
        {
            "type": "board_meeting_h2",
            "title": "Board Meeting — H2 (Oct-Mar)",
            "frequency": "semi_annual",
            "due_rule": "march_31",
            "description": "Section 8 company: Second half-year board meeting.",
            "penalty_fixed": 25000,
        },
    ],

    "public_limited": [],  # extends private_limited — handled in code

    # ------------------------------------------------------------------
    # Cross-entity rules (applied based on conditions, not entity type)
    # ------------------------------------------------------------------
    "_universal": [
        # ── Day-0 / Post-Incorporation (one-time) ─────────────────────
        {
            "type": "first_board_meeting",
            "title": "First Board Meeting",
            "frequency": "one_time",
            "due_rule": "within_30_days_of_incorporation",
            "description": (
                "First board meeting must be held within 30 days of incorporation. "
                "Agenda: appoint first auditor, adopt common seal (optional), "
                "confirm registered office, allot shares, authorize bank account. "
                "(§ 173(1))"
            ),
            "condition": "post_incorporation",
        },
        {
            "type": "auditor_appointment",
            "title": "First Auditor Appointment (ADT-1)",
            "frequency": "one_time",
            "due_rule": "within_30_days_of_incorporation",
            "description": (
                "Board must appoint first auditor within 30 days of incorporation. "
                "Auditor holds office until conclusion of first AGM. File ADT-1 "
                "within 15 days of appointment. (§ 139(6))"
            ),
            "condition": "post_incorporation",
        },
        {
            "type": "inc_20a",
            "title": "INC-20A (Commencement of Business)",
            "frequency": "one_time",
            "due_rule": "within_180_days_of_incorporation",
            "description": (
                "File declaration that every subscriber has paid the value of "
                "shares agreed. Company cannot commence business until filed. "
                "Filing fee: Rs 500. Penalty: Rs 50,000 on company + Rs 1,000/day "
                "per officer in default. (§ 10A)"
            ),
            "penalty_fixed": 50000,
            "penalty_per_day": 1000,
            "condition": "post_incorporation",
        },
        {
            "type": "share_certificate_issue",
            "title": "Issue Share Certificates",
            "frequency": "one_time",
            "due_rule": "within_60_days_of_incorporation",
            "description": (
                "Issue share certificates to all subscribers within 60 days of "
                "allotment/incorporation. (§ 56(4))"
            ),
            "condition": "post_incorporation",
        },
        # ── MSME-1 — Semi-annual delayed payment reporting ────────────
        # (MSMED Act 2006 § 22 read with Companies Act § 405)
        {
            "type": "msme_1_h1",
            "title": "MSME-1 (H1: Apr-Sep delayed payments)",
            "frequency": "semi_annual",
            "due_rule": "october_31",
            "description": (
                "Report all outstanding payments to MSME vendors delayed beyond "
                "45 days for Apr-Sep half-year. Applicable to ALL companies with "
                "MSME suppliers. (MSMED Act § 22, MCA Order dt. 22-01-2019)"
            ),
            "penalty_note": "Interest payable at 3x bank rate on delayed amount.",
            "condition": "has_msme_vendors",
        },
        {
            "type": "msme_1_h2",
            "title": "MSME-1 (H2: Oct-Mar delayed payments)",
            "frequency": "semi_annual",
            "due_rule": "april_30",
            "description": (
                "Report all outstanding payments to MSME vendors delayed beyond "
                "45 days for Oct-Mar half-year."
            ),
            "penalty_note": "Interest payable at 3x bank rate on delayed amount.",
            "condition": "has_msme_vendors",
        },
        # ── FEMA/RBI — FDI tracking ──────────────────────────────────
        {
            "type": "fla_return",
            "title": "FLA Return (RBI)",
            "frequency": "annual",
            "due_rule": "july_15",
            "description": (
                "Annual return of Foreign Liabilities and Assets to RBI. "
                "Mandatory if company has received FDI or made overseas investment. "
                "(FEMA Regulations)"
            ),
            "penalty_note": "Non-filing may result in FEMA penalty proceedings.",
            "condition": "has_foreign_investment",
        },
        # ── DPT-3 — Return of Deposits (§ 73/74) ────────────────────
        {
            "type": "dpt_3",
            "title": "DPT-3 (Return of Deposits)",
            "frequency": "annual",
            "due_rule": "june_30",
            "description": (
                "Annual return of deposits and transactions NOT considered as "
                "deposits (e.g., inter-corporate loans, director loans). Must be "
                "filed by June 30 each year. Required for all companies that have "
                "accepted deposits or have outstanding loan transactions. "
                "(§ 73/74 read with Rule 16 of Companies (Acceptance of Deposits) "
                "Rules, 2014)"
            ),
            "penalty_note": (
                "Company: Rs 1 crore or twice the deposit amount (whichever is lower). "
                "Officers: Rs 25 lakh or twice the deposit (whichever is lower). (§ 76A)"
            ),
            "condition": "private_limited_or_public",
        },
        # ── GST Annual Return ─────────────────────────────────────────
        {
            "type": "gstr_9_annual",
            "title": "GSTR-9 (Annual GST Return)",
            "frequency": "annual",
            "due_rule": "december_31",
            "description": (
                "Annual consolidated GST return. Mandatory for all regular GST "
                "registrants with aggregate turnover > Rs 2 crore. "
                "Exempt if turnover ≤ Rs 2 crore. (CGST Act § 44)"
            ),
            "penalty_per_day": 200,
            "max_penalty_note": (
                "Late fee: Rs 100 CGST + Rs 100 SGST per day. "
                "Capped at 0.04% of turnover in the state/UT "
                "(0.02% CGST + 0.02% SGST). (§ 47(2) CGST Act)"
            ),
            "condition": "gst_registered",
        },
        # ── GSTR-1 — Monthly outward supplies (§ 37) ──────────────────
        # Monthly filers: turnover > Rs 5 crore. Due 11th of next month.
        *[
            {
                "type": f"gstr_1_m{m:02d}",
                "title": f"GSTR-1 (Outward Supplies — {month_name})",
                "frequency": "monthly",
                "due_rule": f"11th_of_month_after_{m:02d}",
                "description": (
                    f"File monthly GSTR-1 for {month_name} by 11th of the "
                    "following month. Contains B2B invoice details, B2C "
                    "large/small, credit/debit notes, exports, HSN summary. "
                    "(CGST Act § 37, Rule 59)"
                ),
                "penalty_per_day": 50,
                "max_penalty_note": (
                    "Late fee: Rs 25 CGST + Rs 25 SGST per day. "
                    "Cap: Rs 10,000 (turnover > Rs 5 crore), Rs 5,000 "
                    "(Rs 1.5-5 crore), Rs 2,000 (< Rs 1.5 crore), "
                    "Rs 500 (nil return). (§ 47)"
                ),
                "section": "37",
                "condition": "gst_monthly_filer",
            }
            for m, month_name in [
                (1, "April"), (2, "May"), (3, "June"), (4, "July"),
                (5, "August"), (6, "September"), (7, "October"),
                (8, "November"), (9, "December"), (10, "January"),
                (11, "February"), (12, "March"),
            ]
        ],
        # ── GSTR-1 — Quarterly (QRMP scheme, turnover ≤ Rs 5 crore) ─
        {
            "type": "gstr_1_q1",
            "title": "GSTR-1 (Outward Supplies — Q1 Apr-Jun)",
            "frequency": "quarterly",
            "due_rule": "july_13",
            "description": (
                "Quarterly GSTR-1 for QRMP filers (turnover ≤ Rs 5 crore). "
                "Due 13th of the month following the quarter. Contains "
                "all outward supply invoices for the quarter. (§ 37, Rule 59)"
            ),
            "penalty_per_day": 50,
            "section": "37",
            "condition": "gst_quarterly_filer",
        },
        {
            "type": "gstr_1_q2",
            "title": "GSTR-1 (Outward Supplies — Q2 Jul-Sep)",
            "frequency": "quarterly",
            "due_rule": "october_13",
            "description": "Quarterly GSTR-1 for Q2 (QRMP). (§ 37)",
            "penalty_per_day": 50,
            "condition": "gst_quarterly_filer",
        },
        {
            "type": "gstr_1_q3",
            "title": "GSTR-1 (Outward Supplies — Q3 Oct-Dec)",
            "frequency": "quarterly",
            "due_rule": "january_13",
            "description": "Quarterly GSTR-1 for Q3 (QRMP). (§ 37)",
            "penalty_per_day": 50,
            "condition": "gst_quarterly_filer",
        },
        {
            "type": "gstr_1_q4",
            "title": "GSTR-1 (Outward Supplies — Q4 Jan-Mar)",
            "frequency": "quarterly",
            "due_rule": "april_13",
            "description": "Quarterly GSTR-1 for Q4 (QRMP). (§ 37)",
            "penalty_per_day": 50,
            "condition": "gst_quarterly_filer",
        },
        # ── GSTR-3B — Monthly summary + tax payment (§ 39) ──────────
        *[
            {
                "type": f"gstr_3b_m{m:02d}",
                "title": f"GSTR-3B (Summary Return — {month_name})",
                "frequency": "monthly",
                "due_rule": f"20th_of_month_after_{m:02d}",
                "description": (
                    f"Monthly GSTR-3B for {month_name}. Summary return for "
                    "self-assessed tax payment. Must reconcile ITC with "
                    "GSTR-2B auto-populated data. Due 20th of next month. "
                    "(CGST Act § 39, Rule 61)"
                ),
                "penalty_per_day": 50,
                "max_penalty_note": (
                    "Late fee: Rs 25 CGST + Rs 25 SGST per day. "
                    "Interest: 18% p.a. on net tax liability paid late (§ 50(1)). "
                    "24% p.a. on wrongly claimed ITC (§ 50(3)). "
                    "Cap: Rs 10,000/5,000/2,000 by turnover slab; Rs 500 nil. (§ 47)"
                ),
                "section": "39",
                "condition": "gst_monthly_filer",
            }
            for m, month_name in [
                (1, "April"), (2, "May"), (3, "June"), (4, "July"),
                (5, "August"), (6, "September"), (7, "October"),
                (8, "November"), (9, "December"), (10, "January"),
                (11, "February"), (12, "March"),
            ]
        ],
        # ── GSTR-3B — Quarterly (QRMP scheme) ────────────────────────
        # Due date varies by state category:
        # Category 1 (Southern/Western states): 22nd
        # Category 2 (Northern/Eastern states): 24th
        {
            "type": "gstr_3b_q1",
            "title": "GSTR-3B (Summary Return — Q1 Apr-Jun)",
            "frequency": "quarterly",
            "due_rule": "gstr3b_quarterly_q1",
            "description": (
                "Quarterly GSTR-3B for QRMP filers. Due 22nd (Category 1 "
                "states: MH, KA, KL, TN, GJ, AP, TG, GA, etc.) or 24th "
                "(Category 2 states: DL, UP, HR, PB, RJ, WB, etc.) of the "
                "month following the quarter. (§ 39, Rule 61)"
            ),
            "penalty_per_day": 50,
            "section": "39",
            "condition": "gst_quarterly_filer",
        },
        {
            "type": "gstr_3b_q2",
            "title": "GSTR-3B (Summary Return — Q2 Jul-Sep)",
            "frequency": "quarterly",
            "due_rule": "gstr3b_quarterly_q2",
            "description": "Quarterly GSTR-3B for Q2 (QRMP). (§ 39)",
            "penalty_per_day": 50,
            "condition": "gst_quarterly_filer",
        },
        {
            "type": "gstr_3b_q3",
            "title": "GSTR-3B (Summary Return — Q3 Oct-Dec)",
            "frequency": "quarterly",
            "due_rule": "gstr3b_quarterly_q3",
            "description": "Quarterly GSTR-3B for Q3 (QRMP). (§ 39)",
            "penalty_per_day": 50,
            "condition": "gst_quarterly_filer",
        },
        {
            "type": "gstr_3b_q4",
            "title": "GSTR-3B (Summary Return — Q4 Jan-Mar)",
            "frequency": "quarterly",
            "due_rule": "gstr3b_quarterly_q4",
            "description": "Quarterly GSTR-3B for Q4 (QRMP). (§ 39)",
            "penalty_per_day": 50,
            "condition": "gst_quarterly_filer",
        },
        # ── CMP-08 — Quarterly statement for Composition dealers ─────
        {
            "type": "cmp_08_q1",
            "title": "CMP-08 (Composition — Q1 Apr-Jun)",
            "frequency": "quarterly",
            "due_rule": "july_18",
            "description": (
                "Quarterly self-assessed tax statement for Composition "
                "scheme dealers. Due 18th of the month after quarter. "
                "Tax rates: 1% (manufacturers/traders), 5% (restaurants), "
                "6% (service providers). (§ 10, Rule 62)"
            ),
            "penalty_per_day": 50,
            "section": "10",
            "condition": "gst_composition",
        },
        {
            "type": "cmp_08_q2",
            "title": "CMP-08 (Composition — Q2 Jul-Sep)",
            "frequency": "quarterly",
            "due_rule": "october_18",
            "description": "Quarterly CMP-08 for Q2. (§ 10, Rule 62)",
            "penalty_per_day": 50,
            "condition": "gst_composition",
        },
        {
            "type": "cmp_08_q3",
            "title": "CMP-08 (Composition — Q3 Oct-Dec)",
            "frequency": "quarterly",
            "due_rule": "january_18",
            "description": "Quarterly CMP-08 for Q3. (§ 10, Rule 62)",
            "penalty_per_day": 50,
            "condition": "gst_composition",
        },
        {
            "type": "cmp_08_q4",
            "title": "CMP-08 (Composition — Q4 Jan-Mar)",
            "frequency": "quarterly",
            "due_rule": "april_18",
            "description": "Quarterly CMP-08 for Q4. (§ 10, Rule 62)",
            "penalty_per_day": 50,
            "condition": "gst_composition",
        },
        # ── GSTR-4 — Annual return for Composition dealers ───────────
        {
            "type": "gstr_4_annual",
            "title": "GSTR-4 (Composition Annual Return)",
            "frequency": "annual",
            "due_rule": "april_30",
            "description": (
                "Annual return for Composition scheme taxpayers. "
                "Due April 30 of the following FY. Contains consolidated "
                "details of self-assessed tax, purchases, and turnover. "
                "(CGST Act § 39(2), Rule 62)"
            ),
            "penalty_per_day": 50,
            "max_penalty_note": (
                "Late fee: Rs 25 CGST + Rs 25 SGST per day. "
                "Cap: Rs 2,000 (non-nil), Rs 500 (nil). (§ 47)"
            ),
            "section": "39",
            "condition": "gst_composition",
        },
        # ── GSTR-9C — Reconciliation statement (turnover > Rs 5 crore)
        {
            "type": "gstr_9c",
            "title": "GSTR-9C (GST Reconciliation Statement)",
            "frequency": "annual",
            "due_rule": "december_31",
            "description": (
                "Self-certified reconciliation statement filed along with "
                "GSTR-9. Mandatory for taxpayers with aggregate turnover "
                "exceeding Rs 5 crore. From FY 2020-21 onwards, CA/CMA "
                "certification is no longer required — self-certified by "
                "authorized signatory. (§ 44, Rule 80(3))"
            ),
            "penalty_per_day": 0,
            "penalty_note": "Filed as Part-B of GSTR-9. Same late fee applies.",
            "condition": "gst_turnover_above_5cr",
        },
        # ── BEN-2 (Significant Beneficial Ownership — § 90) ──────────
        {
            "type": "ben_2",
            "title": "BEN-2 (Significant Beneficial Ownership)",
            "frequency": "event_based",
            "due_rule": "within_30_days_of_ben1",
            "description": (
                "Company must file BEN-2 within 30 days of receiving BEN-1 "
                "declaration from a significant beneficial owner (SBO). SBO = "
                "individual holding ≥ 10% shares/voting rights/right to receive "
                "dividends, or exercising significant influence/control. "
                "BEN-1 must be filed by the SBO within 30 days of acquiring "
                "significant beneficial ownership. (§ 90, Companies (Significant "
                "Beneficial Owners) Rules, 2018)"
            ),
            "penalty_note": (
                "Company: Rs 10 lakh + Rs 1,000/day for continuing default. "
                "Officer: Rs 2.5 lakh + Rs 1,000/day. (§ 90(10)-(11))"
            ),
            "condition": "private_limited_or_public",
        },
        # ── MGT-14 (Filing of Resolutions — § 117) ───────────────────
        {
            "type": "mgt_14",
            "title": "MGT-14 (Filing of Special Resolutions)",
            "frequency": "event_based",
            "due_rule": "within_30_days_of_resolution",
            "description": (
                "File copy of special resolutions and certain board resolutions "
                "with ROC within 30 days of passing. Required for: change in "
                "registered office, increase in authorized capital, issue of "
                "shares, appointment of MD/manager, approval of related party "
                "transactions, etc. (§ 117)"
            ),
            "penalty_per_day": 100,
            "penalty_note": (
                "Company: Rs 5 lakh. Officer: Rs 1 lakh. (§ 117(2))"
            ),
            "condition": "private_limited_or_public",
        },
    ],


    # ------------------------------------------------------------------
    # State-aware rules (PT, LWF) — added dynamically based on company.state
    # ------------------------------------------------------------------
    "_state_rules": {
        # ── States with Professional Tax legislation ──────────────────
        "Maharashtra": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (MH)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "MH: PT payment. Rs 200/month (Rs 300 in Feb). Maharashtra State Tax on Professions Act.",
            },
            {
                "type": "lwf_h1",
                "title": "LWF — H1 (MH)",
                "frequency": "semi_annual",
                "due_rule": "june_30",
                "description": "MH LWF: June contribution (Maharashtra Labour Welfare Fund Act).",
            },
            {
                "type": "lwf_h2",
                "title": "LWF — H2 (MH)",
                "frequency": "semi_annual",
                "due_rule": "december_31",
                "description": "MH LWF: December contribution.",
            },
        ],
        "Karnataka": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (KA)",
                "frequency": "monthly",
                "due_rule": "monthly_20th",
                "description": "KA: PT due by 20th. Slab-based (max Rs 200/month). Feb annual return.",
            },
            {
                "type": "lwf_h2",
                "title": "LWF — Annual (KA)",
                "frequency": "annual",
                "due_rule": "january_15",
                "description": "KA LWF: Annual contribution by Jan 15.",
            },
        ],
        "Telangana": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (TS)",
                "frequency": "monthly",
                "due_rule": "monthly_10th",
                "description": "TS: PT due by 10th. Max Rs 200/month. Telangana Tax on Professions Act.",
            },
        ],
        "Tamil Nadu": [
            {
                "type": "pt_annual",
                "title": "Professional Tax — H1 (TN)",
                "frequency": "semi_annual",
                "due_rule": "september_30",
                "description": "TN: PT half-yearly (Apr-Sep). Max Rs 2,500/year. Tamil Nadu Tax on Professions Act.",
            },
            {
                "type": "pt_annual",
                "title": "Professional Tax — H2 (TN)",
                "frequency": "semi_annual",
                "due_rule": "march_31",
                "description": "TN: PT half-yearly (Oct-Mar).",
            },
        ],
        "Gujarat": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (GJ)",
                "frequency": "monthly",
                "due_rule": "monthly_15th",
                "description": "GJ: PT due by 15th. Max Rs 200/month (Rs 300 in Feb). Gujarat Professions Tax Act.",
            },
        ],
        "Andhra Pradesh": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (AP)",
                "frequency": "monthly",
                "due_rule": "monthly_10th",
                "description": "AP: PT due by 10th. Max Rs 200/month. AP Tax on Professions Act.",
            },
        ],
        "Kerala": [
            {
                "type": "pt_annual",
                "title": "Professional Tax — H1 (KL)",
                "frequency": "semi_annual",
                "due_rule": "september_30",
                "description": "KL: PT half-yearly (Apr-Sep). Kerala Municipalities Act / Panchayat Raj Act.",
            },
            {
                "type": "pt_annual",
                "title": "Professional Tax — H2 (KL)",
                "frequency": "semi_annual",
                "due_rule": "march_31",
                "description": "KL: PT half-yearly (Oct-Mar). Max Rs 2,500/year.",
            },
        ],
        "West Bengal": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (WB)",
                "frequency": "monthly",
                "due_rule": "monthly_21st",
                "description": "WB: PT due by 21st. Max Rs 200/month. West Bengal State Tax on Professions Act.",
            },
            {
                "type": "lwf_h1",
                "title": "LWF — H1 (WB)",
                "frequency": "semi_annual",
                "due_rule": "june_15",
                "description": "WB LWF: June contribution (West Bengal Labour Welfare Fund Act).",
            },
            {
                "type": "lwf_h2",
                "title": "LWF — H2 (WB)",
                "frequency": "semi_annual",
                "due_rule": "december_15",
                "description": "WB LWF: December contribution.",
            },
        ],
        "Madhya Pradesh": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (MP)",
                "frequency": "monthly",
                "due_rule": "monthly_10th",
                "description": "MP: PT due by 10th. Max Rs 208/month. Madhya Pradesh Vritti Kar Adhiniyam.",
            },
        ],
        "Odisha": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (OD)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "OD: PT due by month-end. Max Rs 200/month. Odisha Entry Tax / PT Act.",
            },
        ],
        "Assam": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (AS)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "AS: PT due by month-end. Max Rs 208/month. Assam Professions Tax Act.",
            },
        ],
        "Bihar": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (BR)",
                "frequency": "monthly",
                "due_rule": "monthly_15th",
                "description": "BR: PT due by 15th. Max Rs 208/month. Bihar Tax on Professions Act.",
            },
        ],
        "Jharkhand": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (JH)",
                "frequency": "monthly",
                "due_rule": "monthly_15th",
                "description": "JH: PT due by 15th. Max Rs 208/month. Jharkhand Tax on Professions Act.",
            },
        ],
        "Chhattisgarh": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (CG)",
                "frequency": "monthly",
                "due_rule": "monthly_10th",
                "description": "CG: PT due by 10th. Max Rs 208/month. Chhattisgarh Vritti Kar Adhiniyam.",
            },
        ],
        "Punjab": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (PB)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "PB: PT due by month-end. Under Punjab Finance Act provisions.",
            },
        ],
        "Meghalaya": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (ML)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "ML: PT due by month-end. Meghalaya Professions Tax Act.",
            },
        ],
        "Tripura": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (TR)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "TR: PT due by month-end. Tripura Professions Tax Act. Max Rs 208/month.",
            },
        ],
        "Manipur": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (MN)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "MN: PT due by month-end. Manipur Professions Tax Act. Max Rs 200/month.",
            },
        ],
        "Sikkim": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (SK)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "SK: PT due by month-end. Sikkim Tax on Professions Act.",
            },
        ],
        "Mizoram": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (MZ)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "MZ: PT due by month-end. Mizoram Professions, Trades Taxation Act.",
            },
        ],
        "Goa": [
            {
                "type": "pt_monthly",
                "title": "Professional Tax — Payment (GA)",
                "frequency": "monthly",
                "due_rule": "monthly_last_day",
                "description": "GA: PT due by month-end. Goa Tax on Professions Act. Max Rs 200/month.",
            },
        ],
        # ── States with NO Professional Tax (Constitutional cap — Art 276) ──
        # Rajasthan, Haryana, Uttarakhand, Himachal Pradesh, J&K, Ladakh,
        # Arunachal Pradesh, Nagaland, Delhi (UT) — no PT levy currently.
        # No entries needed for these states.
    },


    # ------------------------------------------------------------------
    # Labor/Payroll rules (applied based on employee count)
    # ------------------------------------------------------------------
    "_labor_rules": [
        {
            "type": "epfo_monthly",
            "title": "EPFO — Monthly PF Deposit & Return",
            "frequency": "monthly",
            "due_rule": "monthly_15th",
            "description": (
                "Deposit employer + employee PF contribution (12% + 12%) by 15th of "
                "following month. File ECR (Electronic Challan cum Return). "
                "Mandatory if 20+ employees."
            ),
            "penalty_note": "Interest @ 12% p.a. on delayed deposits. Damages up to 100%.",
            "condition": "employees_gte_20",
        },
        {
            "type": "esic_monthly",
            "title": "ESIC — Monthly ESI Deposit",
            "frequency": "monthly",
            "due_rule": "monthly_15th",
            "description": (
                "Deposit employer (3.25%) + employee (0.75%) ESI contribution by 15th of "
                "following month. Mandatory if 10+ employees with salary up to Rs 21,000/month."
            ),
            "penalty_note": "Interest @ 12% p.a. on delayed deposits.",
            "condition": "employees_gte_10",
        },
    ],

    "sole_proprietorship": [
        {
            "type": "itr_filing",
            "title": "Income Tax Return (ITR-3/4)",
            "frequency": "annual",
            "due_rule": "july_31",
            "description": "File ITR by July 31.",
        },
    ],

    "partnership": [
        {
            "type": "itr_filing",
            "title": "Income Tax Return (ITR-5)",
            "frequency": "annual",
            "due_rule": "july_31",
            "description": "File ITR-5 by July 31.",
        },
    ],
}


# ---------------------------------------------------------------------------
# Penalty Rates
# ---------------------------------------------------------------------------

PENALTY_RATES: Dict[str, Dict[str, Any]] = {
    "aoc_4": {
        "description": "Late filing of AOC-4 (§ 137)",
        "per_day": 100,
        "max": 1000000,  # Rs 10 lakh cap
        "additional": "Company and every officer in default liable. (§ 137(3))",
    },
    "mgt_7": {
        "description": "Late filing of MGT-7 (§ 92)",
        "per_day": 100,
        "max": 500000,  # Rs 5 lakh cap per § 92(5)
        "additional": "Company: Rs 100/day (max Rs 5 lakh). Officer: Rs 50,000 to Rs 5,00,000. (§ 92(5)-(6))",
    },
    "dir_3_kyc": {
        "description": "Late DIR-3 KYC (Rule 12A)",
        "per_day": 0,
        "fixed": 5000,
        "additional": "DIN deactivated until KYC filed. Rs 5,000 late fee to reactivate.",
    },
    "adt_1_renewal": {
        "description": "Late ADT-1 filing (§ 139)",
        "per_day": 100,
        "max": None,
        "additional": "Company: Rs 25,000 to Rs 5,00,000. Officer: Rs 10,000 to Rs 1,00,000. (§ 139(9))",
    },
    "board_meeting_q1": {
        "description": "Failure to hold Board Meeting (§ 173)",
        "per_day": 0,
        "fixed": 25000,
        "additional": "Company: Rs 25,000. Each director: Rs 5,000 per meeting missed. (§ 173(4))",
    },
    "board_meeting_q2": {"per_day": 0, "fixed": 25000},
    "board_meeting_q3": {"per_day": 0, "fixed": 25000},
    "board_meeting_q4": {"per_day": 0, "fixed": 25000},
    "board_meeting_h1": {"per_day": 0, "fixed": 25000},
    "board_meeting_h2": {"per_day": 0, "fixed": 25000},
    "agm": {
        "description": "Failure to hold AGM (§ 96, 99)",
        "per_day": 5000,
        "fixed": 100000,
        "additional": (
            "Company: up to Rs 1,00,000. Every officer in default: up to Rs 5,000. "
            "Continued default: Rs 5,000/day. NCLT may call AGM on application. (§ 99)"
        ),
    },
    "inc_20a": {
        "description": "Late INC-20A — Commencement of Business (§ 10A)",
        "per_day": 1000,
        "fixed": 50000,
        "additional": (
            "Company: Rs 50,000. Officers: Rs 1,000/day for continuing default. "
            "Company cannot commence business until filed. ROC may initiate "
            "striking off if not filed within 180 days. (§ 10A(2))"
        ),
    },
    "tds_return_q1": {
        "description": "Late TDS Return (§ 234E IT Act)",
        "per_day": 200,
        "max": None,  # capped at TDS amount collectible
        "additional": (
            "Rs 200/day (§ 234E), capped at TDS amount. "
            "Additional penalty Rs 10,000 to Rs 1,00,000 under § 271H. "
            "Interest: 1.5% per month on TDS not deposited (§ 201(1A))."
        ),
    },
    "tds_return_q2": {"per_day": 200, "max": None},
    "tds_return_q3": {"per_day": 200, "max": None},
    "tds_return_q4": {"per_day": 200, "max": None},
    "itr_filing": {
        "description": "Late ITR filing (§ 234F IT Act)",
        "per_day": 0,
        "fixed": 10000,
        "additional": (
            "Rs 5,000 if filed by Dec 31; Rs 10,000 if after. "
            "If total income ≤ Rs 5 lakh: max Rs 1,000. "
            "Interest: 1% per month under § 234A on unpaid tax."
        ),
    },
    "form_11": {
        "description": "Late LLP Form 11 (LLP Act § 35, Rule 25)",
        "per_day": 100,
        "max": None,
        "additional": "Rs 100/day per designated partner. No cap.",
    },
    "form_8": {
        "description": "Late LLP Form 8 (LLP Act § 34, Rule 24)",
        "per_day": 100,
        "max": None,
        "additional": "Rs 100/day per designated partner. No cap.",
    },
    "msme_1_h1": {
        "description": "MSME-1 delayed payment reporting (MSMED Act § 22)",
        "per_day": 0,
        "fixed": 0,
        "additional": (
            "Interest at 3x bank rate payable on delayed amount to MSME "
            "vendors. Buyer liable under MSMED Act § 16. No separate MCA penalty "
            "for MSME-1 non-filing, but persistent default may trigger action "
            "by MSEFC (Micro and Small Enterprises Facilitation Council)."
        ),
    },
    "msme_1_h2": {
        "description": "MSME-1 delayed payment reporting",
        "per_day": 0,
        "fixed": 0,
        "additional": "Same as H1. Interest at 3x bank rate on delayed payments.",
    },
    "dpt_3": {
        "description": "Late DPT-3 — Return of Deposits (§ 73/74)",
        "per_day": 0,
        "fixed": 0,
        "additional": (
            "Company: up to Rs 1 crore or twice the deposit (whichever lower). "
            "Officers: up to Rs 25 lakh or twice the deposit. "
            "Imprisonment: up to 7 years for directors. (§ 76A)"
        ),
    },
    "ben_2": {
        "description": "Late BEN-2 — Significant Beneficial Ownership (§ 90)",
        "per_day": 1000,
        "fixed": 1000000,  # Rs 10 lakh
        "additional": (
            "Company: Rs 10 lakh + Rs 1,000/day continuing default. "
            "Officer: Rs 2.5 lakh + Rs 1,000/day. (§ 90(10)-(11))"
        ),
    },
    "mgt_14": {
        "description": "Late MGT-14 — Filing of Resolutions (§ 117)",
        "per_day": 100,
        "fixed": 0,
        "additional": "Company: up to Rs 5 lakh. Officer: up to Rs 1 lakh. (§ 117(2))",
    },
    "fc_gpr": {
        "description": "Late FC-GPR filing with RBI",
        "per_day": 0,
        "fixed": 0,
        "additional": "FEMA penalty proceedings. Compounding fee by RBI. Must file within 30 days of allotment.",
    },
    "fla_return": {
        "description": "Late FLA Return to RBI",
        "per_day": 0,
        "fixed": 0,
        "additional": "Non-filing may attract FEMA penalty proceedings.",
    },
    "epfo_monthly": {
        "description": "Late PF deposit (EPF Act 1952)",
        "per_day": 0,
        "fixed": 0,
        "additional": (
            "Interest: 12% p.a. on delayed deposits. "
            "Damages: 5% to 100% of arrears based on delay period. "
            "Employer contribution: 12% (3.67% EPF + 8.33% EPS). (§ 7Q, § 14B)"
        ),
    },
    "esic_monthly": {
        "description": "Late ESI deposit (ESI Act 1948)",
        "per_day": 0,
        "fixed": 0,
        "additional": (
            "Interest: 12% p.a. on delayed deposits. "
            "Employer: 3.25%, Employee: 0.75%. "
            "Threshold: 10+ employees with salary ≤ Rs 21,000/month."
        ),
    },
    "gstr_9_annual": {
        "description": "Late GSTR-9 (CGST Act § 44, § 47)",
        "per_day": 200,
        "max": None,
        "additional": (
            "Late fee: Rs 100 CGST + Rs 100 SGST per day of delay. "
            "Capped at 0.04% of turnover in the state/UT "
            "(0.02% CGST + 0.02% SGST). NOT 0.25% — that was the old rule. "
            "Exempt if aggregate turnover ≤ Rs 2 crore. (CGST Act § 47(2))"
        ),
    },
    "gstr_9c": {
        "description": "Late GSTR-9C — filed with GSTR-9 (§ 44, Rule 80(3))",
        "per_day": 0,
        "fixed": 0,
        "additional": "Filed as Part-B of GSTR-9. Same late fee as GSTR-9 applies.",
    },
    "gstr_4_annual": {
        "description": "Late GSTR-4 — Composition annual return (§ 39(2))",
        "per_day": 50,
        "max": 2000,
        "additional": (
            "Late fee: Rs 25 CGST + Rs 25 SGST per day. "
            "Cap: Rs 2,000 (non-nil), Rs 500 (nil return). (§ 47)"
        ),
    },
}

# Generate per-month and per-quarter GSTR penalty entries dynamically
for m in range(1, 13):
    _k1 = f"gstr_1_m{m:02d}"
    _k3b = f"gstr_3b_m{m:02d}"
    PENALTY_RATES[_k1] = {
        "description": f"Late GSTR-1 monthly (§ 37, § 47)",
        "per_day": 50,
        "max": 10000,
        "additional": (
            "Rs 25 CGST + Rs 25 SGST per day. Cap by turnover slab: "
            "Rs 10,000 (> Rs 5 cr), Rs 5,000 (Rs 1.5-5 cr), "
            "Rs 2,000 (< Rs 1.5 cr), Rs 500 (nil). (§ 47)"
        ),
    }
    PENALTY_RATES[_k3b] = {
        "description": f"Late GSTR-3B monthly (§ 39, § 47, § 50)",
        "per_day": 50,
        "max": 10000,
        "additional": (
            "Rs 25 CGST + Rs 25 SGST per day. Cap same as GSTR-1. "
            "Plus interest: 18% p.a. on net cash tax liability (§ 50(1)); "
            "24% p.a. on wrongly claimed ITC (§ 50(3))."
        ),
    }

for q in range(1, 5):
    PENALTY_RATES[f"gstr_1_q{q}"] = {
        "description": f"Late GSTR-1 quarterly/QRMP (§ 37, § 47)",
        "per_day": 50,
        "max": 5000,
        "additional": (
            "Rs 25 CGST + Rs 25 SGST per day. QRMP filers (≤ Rs 5 cr turnover). "
            "Cap: Rs 5,000 or Rs 2,000 by turnover slab. (§ 47)"
        ),
    }
    PENALTY_RATES[f"gstr_3b_q{q}"] = {
        "description": f"Late GSTR-3B quarterly/QRMP (§ 39, § 47)",
        "per_day": 50,
        "max": 5000,
        "additional": (
            "Rs 25 CGST + Rs 25 SGST per day. Plus interest: 18% p.a. (§ 50). "
            "Cap: Rs 5,000 or Rs 2,000 by turnover slab."
        ),
    }
    PENALTY_RATES[f"cmp_08_q{q}"] = {
        "description": f"Late CMP-08 — Composition quarterly (§ 10, Rule 62)",
        "per_day": 50,
        "max": 2000,
        "additional": (
            "Rs 25 CGST + Rs 25 SGST per day. "
            "Cap: Rs 2,000 (non-nil), Rs 500 (nil). "
            "Interest: 18% p.a. on late tax payment (§ 50)."
        ),
    }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class ComplianceEngine:
    """Core compliance calendar engine with deadline calculation and scoring."""

    # ── Calendar Generation ──────────────────────────────────────────────

    def generate_calendar(
        self,
        company: Company,
        financial_year: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Generate all compliance deadlines for a company for a given FY.

        Args:
            company: Company model instance.
            financial_year: FY start year (e.g. 2025 for FY 2025-26). Defaults to current FY.
        """
        entity = company.entity_type
        if isinstance(entity, EntityType):
            entity = entity.value

        if financial_year is None:
            today = date.today()
            financial_year = today.year if today.month >= 4 else today.year - 1

        fy_start = date(financial_year, 4, 1)
        fy_end = date(financial_year + 1, 3, 31)

        # Get rules — public_limited uses private_limited rules
        rules = list(COMPLIANCE_RULES.get(entity, []))
        if entity == "public_limited" and not rules:
            rules = list(COMPLIANCE_RULES.get("private_limited", []))

        # Add universal rules (MSME-1, FEMA/FLA, DPT-3, GSTR-9, share certs)
        universal = COMPLIANCE_RULES.get("_universal", [])
        for ur in universal:
            cond = ur.get("condition", "")
            # Filter by condition
            if cond == "private_limited_or_public" and entity not in ("private_limited", "public_limited"):
                continue
            if cond == "post_incorporation" and entity in ("sole_proprietorship", "partnership"):
                continue
            # MSME-1, FLA, GST: apply broadly (user can mark not_applicable)
            rules.append(ur)

        # Add state-aware rules (PT, LWF)
        state_name = getattr(company, "state", "") or ""
        state_rules_map = COMPLIANCE_RULES.get("_state_rules", {})
        if state_name in state_rules_map:
            rules.extend(state_rules_map[state_name])

        # Add labor rules (EPFO/ESIC) based on employee count
        num_employees = getattr(company, "employee_count", 0) or 0
        labor_rules = COMPLIANCE_RULES.get("_labor_rules", [])
        for lr in labor_rules:
            cond = lr.get("condition", "")
            if cond == "employees_gte_20" and num_employees < 20:
                continue
            if cond == "employees_gte_10" and num_employees < 10:
                continue
            rules.append(lr)

        calendar: List[Dict[str, Any]] = []
        for rule in rules:
            due = self.calculate_deadline(rule, company, fy_start, fy_end)
            if not due:
                continue
            
            # Condition check for universal rules
            cond = rule.get("condition", "")
            company_data = getattr(company, "data", {}) or {}
            
            if cond == "has_msme_vendors" and not company_data.get("has_msme_vendors"):
                continue
            if cond == "has_foreign_investment" and not company_data.get("has_fdi"):
                continue
            if cond == "gst_registered" and not company_data.get("gstin"):
                continue
            if cond == "gst_monthly_filer" and not (
                company_data.get("gstin") and company_data.get("gst_filing_frequency") == "monthly"
            ):
                continue
            if cond == "gst_quarterly_filer" and not (
                company_data.get("gstin") and company_data.get("gst_filing_frequency") == "quarterly"
            ):
                continue
            if cond == "gst_composition" and not (
                company_data.get("gstin") and company_data.get("gst_scheme") == "composition"
            ):
                continue
            if cond == "gst_turnover_above_5cr" and not (
                company_data.get("gstin") and company_data.get("gst_turnover_above_5cr")
            ):
                continue
            if cond == "private_limited_or_public" and entity not in ("private_limited", "public_limited"):
                continue
            if cond == "post_incorporation" and entity in ("sole_proprietorship", "partnership"):
                continue

            days_until = (due - date.today()).days

            status = "upcoming"
            if days_until < 0:
                status = "overdue"
            elif days_until <= 30:
                status = "due_soon"

            title = rule["title"]
            description = rule.get("description", "")
            
            # February Spike logic for Professional Tax (MH, KA)
            if rule["type"] == "pt_monthly" and due.month == 2 and state_name in ["Maharashtra", "Karnataka"]:
                title += " (Annual Spike)"
                if state_name == "Maharashtra":
                    description = "MH: February PT is Rs 300 (standard is Rs 200)."
                else:
                    description = "KA: February PT includes annual enrollment spike."

            calendar.append({
                "type": rule["type"],
                "title": title,
                "description": description,
                "frequency": rule["frequency"],
                "due_date": due.isoformat(),
                "days_remaining": max(days_until, 0),
                "status": status,
                "financial_year": f"{financial_year}-{financial_year + 1}",
            })

        # Sort by due_date
        calendar.sort(key=lambda x: x["due_date"] or "9999-12-31")
        return calendar

    # ── Deadline Calculation ─────────────────────────────────────────────

    def calculate_deadline(
        self,
        rule: Dict[str, Any],
        company: Company,
        fy_start: date,
        fy_end: date,
    ) -> Optional[date]:
        """Calculate actual due date from a compliance rule."""
        due_rule = rule.get("due_rule", "")

        # Fixed-date rules
        fixed_dates = {
            "april_13": date(fy_start.year, 4, 13),
            "april_18": date(fy_start.year, 4, 18),
            "april_30": date(fy_start.year, 4, 30),
            "may_30": date(fy_start.year, 5, 30),
            "may_31": date(fy_start.year, 5, 31),
            "june_15": date(fy_start.year, 6, 15),
            "june_30": date(fy_start.year, 6, 30),
            "july_13": date(fy_start.year, 7, 13),
            "july_15": date(fy_start.year, 7, 15),
            "july_18": date(fy_start.year, 7, 18),
            "july_31": date(fy_start.year, 7, 31),
            "september_15": date(fy_start.year, 9, 15),
            "september_30": date(fy_start.year, 9, 30),
            "october_13": date(fy_start.year, 10, 13),
            "october_18": date(fy_start.year, 10, 18),
            "october_30": date(fy_start.year, 10, 30),
            "october_31": date(fy_start.year, 10, 31),
            "december_15": date(fy_start.year, 12, 15),
            "december_31": date(fy_start.year, 12, 31),
            "january_13": date(fy_end.year, 1, 13),
            "january_18": date(fy_end.year, 1, 18),
            "january_31": date(fy_end.year, 1, 31),
            "march_15": date(fy_end.year, 3, 15),
            "march_31": date(fy_end.year, 3, 31),
        }

        if due_rule in fixed_dates:
            return fixed_dates[due_rule]

        # AGM-relative rules (§ 96 Companies Act 2013)
        # First AGM: within 9 months from close of first financial year
        # Subsequent AGMs: within 6 months from close of FY
        # Max gap between two consecutive AGMs: 15 months
        inc_date = getattr(company, "incorporation_date", None)
        if inc_date and isinstance(inc_date, datetime):
            inc_date = inc_date.date()

        is_first_fy = False
        if inc_date:
            # First FY ends on March 31 following incorporation
            first_fy_end = date(inc_date.year + 1, 3, 31) if inc_date.month >= 4 else date(inc_date.year, 3, 31)
            is_first_fy = (fy_end == first_fy_end)

        if is_first_fy:
            # First AGM: 9 months from close of first FY (§ 96(1))
            agm_deadline = fy_end + timedelta(days=270)  # ~9 months
        else:
            # Subsequent AGM: 6 months from FY end (September 30 for March FY)
            agm_deadline = date(fy_start.year, 9, 30)

        if due_rule == "agm_dynamic":
            return agm_deadline
        if due_rule == "within_6_months_of_fy_end":
            return agm_deadline
        if due_rule == "at_agm":
            return agm_deadline
        if due_rule == "within_15_days_of_agm":
            return agm_deadline + timedelta(days=15)
        if due_rule == "within_30_days_of_agm":
            return agm_deadline + timedelta(days=30)
        if due_rule == "within_60_days_of_agm":
            return agm_deadline + timedelta(days=60)

        # OPC-specific
        if due_rule == "within_180_days_of_fy_end":
            return fy_end + timedelta(days=180)
        if due_rule == "within_60_days_of_fy_end_plus_180":
            return fy_end + timedelta(days=240)

        # Board meeting max gap
        if due_rule == "gap_max_120_days":
            return fy_start + timedelta(days=120)

        # Incorporation-relative rules (Day 0 sequence)
        if not inc_date:
            inc_date = getattr(company, "incorporation_date", None)
            if inc_date and isinstance(inc_date, datetime):
                inc_date = inc_date.date()

        if inc_date:
            if due_rule == "within_30_days_of_incorporation":
                return inc_date + timedelta(days=30)
            if due_rule == "within_60_days_of_incorporation":
                return inc_date + timedelta(days=60)
            if due_rule == "within_180_days_of_incorporation":
                return inc_date + timedelta(days=180)

        # Event-based rules (BEN-2, MGT-14) — cannot calculate exact date
        # without knowing the event date. Return end of current FY as a
        # reminder placeholder.
        if due_rule in ("within_30_days_of_ben1", "within_30_days_of_resolution"):
            return fy_end

        # Monthly rules — return next occurrence (15th/20th/last day of current month)
        today = date.today()
        if due_rule == "monthly_15th":
            target = date(today.year, today.month, 15)
            if target < today:
                # Next month
                if today.month == 12:
                    target = date(today.year + 1, 1, 15)
                else:
                    target = date(today.year, today.month + 1, 15)
            return target

        if due_rule == "monthly_20th":
            target = date(today.year, today.month, 20)
            if target < today:
                if today.month == 12:
                    target = date(today.year + 1, 1, 20)
                else:
                    target = date(today.year, today.month + 1, 20)
            return target

        if due_rule == "monthly_10th":
            target = date(today.year, today.month, 10)
            if target < today:
                if today.month == 12:
                    target = date(today.year + 1, 1, 10)
                else:
                    target = date(today.year, today.month + 1, 10)
            return target

        if due_rule == "monthly_21st":
            target = date(today.year, today.month, 21)
            if target < today:
                if today.month == 12:
                    target = date(today.year + 1, 1, 21)
                else:
                    target = date(today.year, today.month + 1, 21)
            return target

        if due_rule == "monthly_last_day":
            import calendar as cal_mod
            last_day = cal_mod.monthrange(today.year, today.month)[1]
            target = date(today.year, today.month, last_day)
            if target < today:
                if today.month == 12:
                    last_day = cal_mod.monthrange(today.year + 1, 1)[1]
                    target = date(today.year + 1, 1, last_day)
                else:
                    last_day = cal_mod.monthrange(today.year, today.month + 1)[1]
                    target = date(today.year, today.month + 1, last_day)
            return target

        # ── GST Monthly due rules ─────────────────────────────────────
        # Pattern: "11th_of_month_after_MM" or "20th_of_month_after_MM"
        # where MM is the FY month (01=April, 12=March)
        import re as _re
        m_match = _re.match(r"(\d+)(?:th|st|nd|rd)_of_month_after_(\d{2})$", due_rule)
        if m_match:
            day_of_month = int(m_match.group(1))
            fy_month_num = int(m_match.group(2))  # 01=April, 12=March
            # Map FY month to calendar month: 01→Apr(4), 12→Mar(3)
            cal_month = (fy_month_num + 3) % 12 or 12
            # "month after" the return period month
            next_month = cal_month + 1
            year = fy_start.year if cal_month >= 4 else fy_end.year
            if next_month > 12:
                next_month = 1
                year += 1
            return date(year, next_month, day_of_month)

        # ── GSTR-3B quarterly staggered due rules ────────────────────
        # Category 1 states (Southern/Western): 22nd
        # Category 2 states (Northern/Eastern): 24th
        GSTR3B_CAT1_STATES = {
            "Maharashtra", "Karnataka", "Kerala", "Tamil Nadu",
            "Gujarat", "Goa", "Andhra Pradesh", "Telangana",
            "Madhya Pradesh", "Chhattisgarh", "Puducherry",
            "Daman and Diu", "Dadra and Nagar Haveli",
            "Andaman and Nicobar Islands", "Lakshadweep",
        }
        if due_rule.startswith("gstr3b_quarterly_q"):
            q_num = int(due_rule[-1])
            state_name_local = getattr(company, "state", "") or ""
            day_of = 22 if state_name_local in GSTR3B_CAT1_STATES else 24
            # Q1→Jul, Q2→Oct, Q3→Jan, Q4→Apr (month after quarter end)
            q_months = {1: (7, fy_start.year), 2: (10, fy_start.year),
                        3: (1, fy_end.year), 4: (4, fy_end.year)}
            month, year = q_months[q_num]
            return date(year, month, day_of)

        logger.warning("Unknown due_rule: %s", due_rule)
        return None

    # ── Task CRUD ────────────────────────────────────────────────────────

    def create_compliance_tasks(
        self,
        db: Session,
        company_id: int,
    ) -> List[ComplianceTask]:
        """Create ComplianceTask records for the next 12 months."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return []

        calendar = self.generate_calendar(company)
        created: List[ComplianceTask] = []

        for entry in calendar:
            # Check if task already exists for this type and approximate period
            task_type_str = entry["type"]
            try:
                task_type = ComplianceTaskType(task_type_str)
            except ValueError:
                logger.warning("Unknown ComplianceTaskType: %s — skipping", task_type_str)
                continue

            existing = (
                db.query(ComplianceTask)
                .filter(
                    ComplianceTask.company_id == company_id,
                    ComplianceTask.task_type == task_type,
                    ComplianceTask.due_date != None,
                )
                .first()
            )
            if existing:
                continue

            due_date = None
            if entry["due_date"]:
                due_date = datetime.fromisoformat(entry["due_date"])
                due_date = due_date.replace(tzinfo=timezone.utc)

            status = ComplianceTaskStatus.UPCOMING
            if entry["status"] == "overdue":
                status = ComplianceTaskStatus.OVERDUE
            elif entry["status"] == "due_soon":
                status = ComplianceTaskStatus.DUE_SOON

            task = ComplianceTask(
                company_id=company_id,
                task_type=task_type,
                title=entry["title"],
                description=entry.get("description", ""),
                due_date=due_date,
                status=status,
            )
            db.add(task)
            created.append(task)

        db.commit()
        for t in created:
            db.refresh(t)
        return created

    # ── Queries ──────────────────────────────────────────────────────────

    def check_overdue_tasks(self, db: Session) -> List[ComplianceTask]:
        """Find all overdue compliance tasks across all companies."""
        now = datetime.now(timezone.utc)
        tasks = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.due_date < now,
                ComplianceTask.status.notin_([
                    ComplianceTaskStatus.COMPLETED,
                    ComplianceTaskStatus.NOT_APPLICABLE,
                ]),
            )
            .all()
        )
        # Update status to OVERDUE
        for t in tasks:
            if t.status != ComplianceTaskStatus.OVERDUE:
                t.status = ComplianceTaskStatus.OVERDUE
        db.commit()
        return tasks

    def get_upcoming_deadlines(
        self,
        db: Session,
        company_id: int,
        days: int = 30,
    ) -> List[ComplianceTask]:
        """Get deadlines coming up in next N days."""
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)
        return (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.due_date >= now,
                ComplianceTask.due_date <= future,
                ComplianceTask.status.notin_([
                    ComplianceTaskStatus.COMPLETED,
                    ComplianceTaskStatus.NOT_APPLICABLE,
                ]),
            )
            .order_by(ComplianceTask.due_date)
            .all()
        )

    # ── Penalty Calculator ───────────────────────────────────────────────

    def calculate_penalty(
        self,
        task_type: str,
        days_overdue: int,
    ) -> Dict[str, Any]:
        """Calculate MCA/IT penalty for late filing."""
        rates = PENALTY_RATES.get(task_type, {})
        if not rates:
            return {
                "task_type": task_type,
                "days_overdue": days_overdue,
                "estimated_penalty": 0,
                "note": "No penalty information available for this task type.",
            }

        per_day = rates.get("per_day", 0)
        fixed = rates.get("fixed", 0)
        max_penalty = rates.get("max", None)

        penalty = fixed + (per_day * max(days_overdue, 0))
        if max_penalty is not None and penalty > max_penalty:
            penalty = max_penalty

        return {
            "task_type": task_type,
            "days_overdue": days_overdue,
            "per_day_rate": per_day,
            "fixed_penalty": fixed,
            "estimated_penalty": penalty,
            "description": rates.get("description", ""),
            "additional_notes": rates.get("additional", ""),
        }

    # ── Compliance Score ─────────────────────────────────────────────────

    def get_compliance_score(
        self,
        db: Session,
        company_id: int,
    ) -> Dict[str, Any]:
        """Calculate compliance health score (0-100)."""
        all_tasks = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.company_id == company_id,
                ComplianceTask.status != ComplianceTaskStatus.NOT_APPLICABLE,
            )
            .all()
        )

        if not all_tasks:
            return {
                "score": 100,
                "grade": "A+",
                "total_tasks": 0,
                "completed": 0,
                "overdue": 0,
                "due_soon": 0,
                "upcoming": 0,
                "message": "No compliance tasks found. Generate tasks to start tracking.",
            }

        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.COMPLETED)
        overdue = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.OVERDUE)
        due_soon = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.DUE_SOON)
        in_progress = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.IN_PROGRESS)
        upcoming = sum(1 for t in all_tasks if t.status == ComplianceTaskStatus.UPCOMING)

        # Scoring algorithm:
        # Start from 100.
        # -15 points per overdue task
        # -5 points per due_soon task not in_progress
        # +0 for upcoming (neutral)
        # Completed tasks don't reduce score
        score = 100
        score -= overdue * 15
        score -= max(0, due_soon - in_progress) * 5
        score = max(0, min(100, score))

        # Grade
        if score >= 90:
            grade = "A+"
        elif score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B+"
        elif score >= 60:
            grade = "B"
        elif score >= 50:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"

        # Estimated total penalty exposure
        total_penalty = 0
        now = datetime.now(timezone.utc)
        for t in all_tasks:
            if t.status == ComplianceTaskStatus.OVERDUE and t.due_date:
                days_over = (now - t.due_date).days
                penalty_info = self.calculate_penalty(t.task_type.value, days_over)
                total_penalty += penalty_info.get("estimated_penalty", 0)

        return {
            "score": score,
            "grade": grade,
            "total_tasks": total,
            "completed": completed,
            "overdue": overdue,
            "due_soon": due_soon,
            "in_progress": in_progress,
            "upcoming": upcoming,
            "estimated_penalty_exposure": total_penalty,
            "message": (
                "Excellent compliance record!" if score >= 90
                else "Good standing — address due items." if score >= 70
                else "Action required — overdue filings detected." if score >= 50
                else "Critical — immediate action needed to avoid penalties."
            ),
        }


    # ── SMS Reminders ──────────────────────────────────────────────────

    def check_and_send_reminders(self, db: Session) -> int:
        """Send SMS reminders for compliance tasks due within 7 days.

        Queries all pending/upcoming tasks due within 7 days, looks up the
        company owner's phone and notification preferences, and dispatches
        SMS reminders via sms_service.

        Returns the number of reminders sent.
        """
        from src.services.sms_service import sms_service
        from src.models.notification import NotificationPreference

        now = datetime.now(timezone.utc)
        upcoming = now + timedelta(days=7)

        tasks = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.due_date >= now,
                ComplianceTask.due_date <= upcoming,
                ComplianceTask.status.notin_([
                    ComplianceTaskStatus.COMPLETED,
                    ComplianceTaskStatus.NOT_APPLICABLE,
                ]),
            )
            .all()
        )

        sent_count = 0
        for task in tasks:
            try:
                company = (
                    db.query(Company)
                    .filter(Company.id == task.company_id)
                    .first()
                )
                if not company:
                    continue

                owner = (
                    db.query(User)
                    .filter(User.id == company.user_id)
                    .first()
                )
                if not owner or not owner.phone:
                    continue

                prefs = (
                    db.query(NotificationPreference)
                    .filter(NotificationPreference.user_id == owner.id)
                    .first()
                )
                if not prefs or not prefs.sms_enabled or not prefs.compliance_reminders:
                    continue

                due_str = task.due_date.strftime("%d %b %Y") if task.due_date else "soon"
                sms_service.send_compliance_reminder_sms(
                    owner.phone, task.title or task.task_type, due_str
                )
                sent_count += 1
            except Exception:
                logger.exception(
                    "Failed to send compliance reminder for task %d", task.id
                )

        return sent_count


    # ── Event-Triggered Compliance Tasks ──────────────────────────────

    # Events that should auto-create compliance tasks when they occur.
    # Format: event_name → list of tasks to generate
    EVENT_TRIGGERS: Dict[str, List[Dict[str, Any]]] = {
        "shareholding_change": [
            {
                "type": "ben_2_filing",
                "title": "BEN-2 — Significant Beneficial Owner Return (§ 90)",
                "description": (
                    "File BEN-2 with ROC within 30 days of receiving BEN-1 "
                    "declaration from a member. Required whenever a Significant "
                    "Beneficial Owner acquires or changes beneficial interest."
                ),
                "deadline_days": 30,
                "section": "90(4A)",
                "form": "BEN-2",
                "penalty_per_day": 100,
            },
            {
                "type": "mgt_14_shareholding",
                "title": "MGT-14 — Board Resolution for Share Allotment/Transfer",
                "description": (
                    "File MGT-14 with ROC within 30 days of passing board "
                    "resolution for share allotment, transfer, or other changes "
                    "requiring § 117 filing."
                ),
                "deadline_days": 30,
                "section": "117",
                "form": "MGT-14",
                "penalty_per_day": 100,
            },
        ],
        "share_allotment": [
            {
                "type": "pas_3_filing",
                "title": "PAS-3 — Return of Allotment (§ 39)",
                "description": (
                    "File PAS-3 with ROC within 30 days of allotment of shares. "
                    "Must include board resolution, list of allottees, and details "
                    "of consideration received."
                ),
                "deadline_days": 30,
                "section": "39(4)",
                "form": "PAS-3",
                "penalty_per_day": 100,
            },
        ],
        "director_appointment": [
            {
                "type": "dir_12_appointment",
                "title": "DIR-12 — Director Appointment Filing (§ 170)",
                "description": (
                    "File DIR-12 with ROC within 30 days of appointment of a "
                    "new director. Director must have valid DIN."
                ),
                "deadline_days": 30,
                "section": "170(2)",
                "form": "DIR-12",
                "penalty_per_day": 100,
            },
        ],
        "director_resignation": [
            {
                "type": "dir_12_resignation",
                "title": "DIR-12 — Director Resignation Filing (§ 168)",
                "description": (
                    "File DIR-12 with ROC within 30 days of director's resignation. "
                    "Director must file DIR-11 independently within 30 days."
                ),
                "deadline_days": 30,
                "section": "168(1)",
                "form": "DIR-12",
                "penalty_per_day": 100,
            },
        ],
        "auditor_appointment": [
            {
                "type": "adt_1_filing",
                "title": "ADT-1 — Auditor Appointment Filing (§ 139)",
                "description": (
                    "File ADT-1 with ROC within 15 days of appointment of "
                    "statutory auditor at AGM."
                ),
                "deadline_days": 15,
                "section": "139(1)",
                "form": "ADT-1",
                "penalty_per_day": 300,
            },
        ],
        "registered_office_change": [
            {
                "type": "inc_22_filing",
                "title": "INC-22 — Registered Office Change (§ 12)",
                "description": (
                    "File INC-22 with ROC within 30 days of change of registered "
                    "office address. Must include proof of new address."
                ),
                "deadline_days": 30,
                "section": "12(4)",
                "form": "INC-22",
                "penalty_per_day": 100,
            },
        ],
        "capital_increase": [
            {
                "type": "sh_7_filing",
                "title": "SH-7 — Authorized Capital Increase (§ 64)",
                "description": (
                    "File SH-7 with ROC within 30 days of passing special "
                    "resolution for increase in authorized share capital."
                ),
                "deadline_days": 30,
                "section": "64(1)",
                "form": "SH-7",
                "penalty_per_day": 100,
            },
        ],
        "board_resolution_special": [
            {
                "type": "mgt_14_resolution",
                "title": "MGT-14 — Special Resolution Filing (§ 117)",
                "description": (
                    "File MGT-14 with ROC within 30 days of passing a special "
                    "resolution or board resolution requiring § 117/179(3) filing."
                ),
                "deadline_days": 30,
                "section": "117",
                "form": "MGT-14",
                "penalty_per_day": 100,
            },
        ],
        "charge_creation": [
            {
                "type": "chg_1_filing",
                "title": "CHG-1 — Charge Creation/Modification (§ 77)",
                "description": (
                    "File CHG-1 with ROC within 30 days of creation or "
                    "modification of charge on company assets."
                ),
                "deadline_days": 30,
                "section": "77(1)",
                "form": "CHG-1",
                "penalty_per_day": 100,
            },
        ],
        "charge_satisfaction": [
            {
                "type": "chg_4_filing",
                "title": "CHG-4 — Charge Satisfaction (§ 82)",
                "description": (
                    "File CHG-4 with ROC within 30 days of satisfaction of "
                    "charge (repayment of secured loan/debenture)."
                ),
                "deadline_days": 30,
                "section": "82(1)",
                "form": "CHG-4",
                "penalty_per_day": 100,
            },
        ],
        "loan_or_investment": [
            {
                "type": "mgt_14_loan",
                "title": "MGT-14 — Loan/Investment Resolution Filing (§ 186)",
                "description": (
                    "File MGT-14 with ROC within 30 days of board resolution "
                    "approving loan, guarantee, security, or investment under § 186."
                ),
                "deadline_days": 30,
                "section": "186 / 117",
                "form": "MGT-14",
                "penalty_per_day": 100,
            },
        ],
        "rpt_approval": [
            {
                "type": "mgt_14_rpt",
                "title": "MGT-14 — Related Party Transaction Filing (§ 188)",
                "description": (
                    "File MGT-14 with ROC within 30 days of passing board/"
                    "shareholder resolution approving related party transaction."
                ),
                "deadline_days": 30,
                "section": "188 / 117",
                "form": "MGT-14",
                "penalty_per_day": 100,
            },
        ],
    }

    # Threshold triggers: auto-create tasks when company crosses metrics
    THRESHOLD_TRIGGERS: Dict[str, Dict[str, Any]] = {
        "employees_gte_10": {
            "field": "employee_count",
            "operator": "gte",
            "value": 10,
            "tasks": [
                {
                    "type": "esic_registration",
                    "title": "ESI Registration — Mandatory (≥10 employees)",
                    "description": (
                        "Register with ESIC within 15 days of crossing 10 "
                        "employees (with salary ≤ Rs 21,000/month). File Form 01."
                    ),
                    "deadline_days": 15,
                },
            ],
        },
        "employees_gte_20": {
            "field": "employee_count",
            "operator": "gte",
            "value": 20,
            "tasks": [
                {
                    "type": "epfo_registration",
                    "title": "EPF Registration — Mandatory (≥20 employees)",
                    "description": (
                        "Register with EPFO within 30 days of crossing 20 "
                        "employees. File application on EPFO Unified Portal."
                    ),
                    "deadline_days": 30,
                },
            ],
        },
    }

    def create_event_tasks(
        self,
        db: Session,
        company: Company,
        event_name: str,
        event_date: Optional[date] = None,
        notes: str = "",
    ) -> List[ComplianceTask]:
        """Create compliance tasks triggered by a corporate event.

        Args:
            db: Database session
            company: Company the event occurred for
            event_name: Key from EVENT_TRIGGERS (e.g., 'share_allotment')
            event_date: When the event occurred (defaults to today)
            notes: Additional context about the event

        Returns:
            List of created ComplianceTask instances
        """
        triggers = self.EVENT_TRIGGERS.get(event_name, [])
        if not triggers:
            logger.warning("Unknown compliance event: %s", event_name)
            return []

        if event_date is None:
            event_date = date.today()

        created: List[ComplianceTask] = []
        for trigger in triggers:
            deadline = event_date + timedelta(days=trigger["deadline_days"])

            # Check for duplicate (same type, same company, similar deadline)
            existing = (
                db.query(ComplianceTask)
                .filter(
                    ComplianceTask.company_id == company.id,
                    ComplianceTask.task_type == trigger["type"],
                    ComplianceTask.due_date == deadline.isoformat(),
                    ComplianceTask.status.in_(["upcoming", "in_progress"]),
                )
                .first()
            )
            if existing:
                continue

            task = ComplianceTask(
                company_id=company.id,
                task_type=trigger["type"],
                title=trigger["title"],
                description=trigger["description"],
                due_date=deadline.isoformat(),
                status="upcoming",
                priority="high",
                notes=(
                    f"Event: {event_name} on {event_date.isoformat()}. "
                    f"Form: {trigger.get('form', 'N/A')} | "
                    f"Section: {trigger.get('section', 'N/A')}. "
                    + (notes or "")
                ),
            )
            db.add(task)
            created.append(task)

        if created:
            db.commit()
            for t in created:
                db.refresh(t)
            logger.info(
                "Created %d event-triggered tasks for company %d (event=%s)",
                len(created), company.id, event_name,
            )

        return created

    def check_threshold_triggers(
        self,
        db: Session,
        company: Company,
    ) -> List[ComplianceTask]:
        """Check if company has crossed any metric thresholds and create tasks.

        Should be called whenever company metrics (employee_count, etc.) are updated.
        """
        created: List[ComplianceTask] = []
        company_data = getattr(company, "data", {}) or {}
        triggered_keys = company_data.get("_triggered_thresholds", [])

        for key, trigger in self.THRESHOLD_TRIGGERS.items():
            if key in triggered_keys:
                continue  # Already triggered

            field_val = getattr(company, trigger["field"], 0) or 0
            threshold = trigger["value"]
            op = trigger["operator"]

            crossed = False
            if op == "gte" and field_val >= threshold:
                crossed = True
            elif op == "gt" and field_val > threshold:
                crossed = True

            if not crossed:
                continue

            for task_def in trigger["tasks"]:
                deadline = date.today() + timedelta(days=task_def["deadline_days"])
                task = ComplianceTask(
                    company_id=company.id,
                    task_type=task_def["type"],
                    title=task_def["title"],
                    description=task_def["description"],
                    due_date=deadline.isoformat(),
                    status="upcoming",
                    priority="high",
                    notes=f"Auto-triggered: {key} threshold crossed.",
                )
                db.add(task)
                created.append(task)

            # Mark as triggered so we don't create duplicates
            triggered_keys.append(key)

        if created:
            company_data["_triggered_thresholds"] = triggered_keys
            company.data = company_data
            db.commit()
            for t in created:
                db.refresh(t)

        return created


# Module-level singleton
compliance_engine = ComplianceEngine()
