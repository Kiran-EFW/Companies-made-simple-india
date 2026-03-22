# Compliance Framework

The compliance engine is Anvils' core retention mechanism. It auto-generates regulatory tasks based on entity type, tracks deadlines, sends reminders, and escalates overdue items.

---

## How the Compliance Engine Works

### Task Auto-Generation
The compliance engine generates tasks based on:
1. **Entity type** — Different entities have different filing requirements
2. **Incorporation date** — Drives post-incorporation deadlines (INC-20A within 180 days, first board meeting within 30 days)
3. **Financial year end** — Annual filings anchored to March 31
4. **GST registration status** — Triggers monthly/annual GST return tasks
5. **Employee count** — Triggers EPFO, ESIC, Professional Tax obligations
6. **Foreign investment** — Triggers FEMA/RBI filings (FC-GPR, FLA)

### Task Status Lifecycle
```
UPCOMING → DUE_SOON (within 30 days) → OVERDUE → IN_PROGRESS → COMPLETED
                                                              ↘ NOT_APPLICABLE
```

### Background Automation
- Compliance check runs every **15 minutes** via Celery Beat
- Automatic status transitions: upcoming → due_soon → overdue
- Reminder schedule: **30 / 15 / 7 / 3 / 1 day** before deadline
- Reminders sent via: email, SMS, WhatsApp, in-app notification
- SLA tracking with escalation on breach

---

## Compliance Task Types

### 1. Post-Incorporation Tasks (One-Time)

| Task | Deadline | Entity Types |
|------|----------|-------------|
| INC-20A (Commencement of Business) | 180 days from incorporation | PLC, PubLtd |
| Bank Account Opening | 30 days (recommended) | All |
| First Board Meeting | 30 days from incorporation | PLC, OPC, PubLtd, Section 8 |
| Auditor Appointment (ADT-1) | 30 days from incorporation | PLC, OPC, PubLtd, Section 8 |
| GST Registration | Before first sale (if applicable) | All |
| DPIIT Startup India Registration | Optional, any time | PLC, LLP, Partnership |
| EPFO/PF Registration | If 20+ employees | All |
| ESI Registration | If 10+ employees | All |
| LLP Agreement Filing (Form 3) | 30 days from incorporation | LLP |
| Share Allotment | Within incorporation workflow | PLC, OPC, PubLtd |
| Share Certificate Issue | Within 2 months of allotment | PLC, OPC, PubLtd |

---

### 2. Annual ROC Filings

| Filing | Form | Deadline | Entity Types |
|--------|------|----------|-------------|
| Financial Statements | AOC-4 | 30 days from AGM | PLC, OPC, PubLtd, Section 8 |
| Annual Return | MGT-7 | 60 days from AGM | PLC, PubLtd, Section 8 |
| Annual Return (Small Co) | MGT-7A | 60 days from AGM | OPC, Small Companies |
| Director KYC | DIR-3 KYC | September 30 annually | All MCA companies |
| Auditor Reappointment | ADT-1 | 15 days from AGM | PLC, OPC, PubLtd, Section 8 |
| LLP Annual Return | Form 11 | May 30 | LLP |
| LLP Statement of Accounts | Form 8 | October 30 | LLP |
| Deposit Return | DPT-3 | June 30 | PLC, PubLtd (if applicable) |
| MSME Half-Yearly Return | MSME-1 | Oct 31 (H1), Apr 30 (H2) | PLC, PubLtd (if applicable) |

---

### 3. GST Compliance (Monthly / Annual)

| Return | Frequency | Due Date | Description |
|--------|-----------|----------|-------------|
| GSTR-1 | Monthly | 11th of next month | Outward supplies (sales) |
| GSTR-3B | Monthly | 20th of next month | Summary return with tax payment |
| GSTR-9 | Annual | December 31 | Annual return |

**Applicability**: All entities registered under GST (turnover > Rs 40 Lakhs for goods, Rs 20 Lakhs for services).

---

### 4. TDS Compliance (Quarterly)

| Return | Quarter | Due Date | Description |
|--------|---------|----------|-------------|
| TDS Return Q1 | Apr-Jun | July 31 | Quarterly TDS return |
| TDS Return Q2 | Jul-Sep | October 31 | Quarterly TDS return |
| TDS Return Q3 | Oct-Dec | January 31 | Quarterly TDS return |
| TDS Return Q4 | Jan-Mar | May 31 | Quarterly TDS return |
| Form 16 | Annual | June 15 | TDS certificate for employees |

**Key TDS Sections & Rates:**
| Section | Nature of Payment | Rate |
|---------|------------------|------|
| 194A | Interest (other than securities) | 10% |
| 194C | Contractor payments | 1% (individual) / 2% (others) |
| 194H | Commission/brokerage | 5% |
| 194I | Rent (land/building) | 10% |
| 194J | Professional/technical fees | 10% |
| 194O | E-commerce payments | 1% |

---

### 5. Income Tax (Annual + Quarterly Advance Tax)

| Filing | Due Date | Entity Types |
|--------|----------|-------------|
| ITR Filing | October 31 (if audit required), July 31 (others) | All |
| Advance Tax Q1 | June 15 (15% of estimated tax) | All (if tax > Rs 10,000) |
| Advance Tax Q2 | September 15 (45% cumulative) | All |
| Advance Tax Q3 | December 15 (75% cumulative) | All |
| Advance Tax Q4 | March 15 (100% cumulative) | All |

**ITR Forms by Entity:**
| Entity Type | ITR Form |
|-------------|----------|
| Private Limited, OPC, Public Ltd, Section 8 | ITR-6 |
| LLP, Partnership | ITR-5 |
| Sole Proprietorship | ITR-3 or ITR-4 |

---

### 6. Board Meetings & AGM

| Requirement | Frequency | Rule | Entity Types |
|-------------|-----------|------|-------------|
| Board Meeting | Quarterly | Min 4/year, gap < 120 days | PLC, OPC, PubLtd, Section 8 |
| Annual General Meeting (AGM) | Annual | Within 6 months of FY end (Sep 30) | PLC, PubLtd, Section 8 |

**Board Meeting Q1**: April - June
**Board Meeting Q2**: July - September
**Board Meeting Q3**: October - December
**Board Meeting Q4**: January - March

**OPC Exception**: OPC requires only 1 board meeting per half-year (gap < 90 days).

---

### 7. Labor & Payroll Compliance

| Filing | Frequency | Due Date | Applicability |
|--------|-----------|----------|---------------|
| EPFO (Provident Fund) | Monthly | 15th of next month | 20+ employees |
| ESIC | Monthly | 15th of next month | 10+ employees (salary < Rs 21,000) |
| Professional Tax | Monthly | As per state rules | State-specific |
| Professional Tax (Annual) | Annual | As per state rules | State-specific |
| Labor Welfare Fund (H1) | Half-yearly | As per state rules | State-specific |
| Labor Welfare Fund (H2) | Half-yearly | As per state rules | State-specific |

---

### 8. FEMA / RBI Compliance (Foreign Investment)

| Filing | Due Date | Trigger |
|--------|----------|---------|
| FC-GPR (Foreign Currency - General Permission Route) | Within 30 days of share allotment to foreign investor | Foreign investment received |
| FLA Return (Foreign Liabilities & Assets) | July 15 annually | Any foreign investment/liability |

---

## Entity-Type Applicability Matrix

| Task Category | PLC | OPC | LLP | Section 8 | Sole Prop | Partnership | PubLtd |
|---------------|-----|-----|-----|-----------|-----------|-------------|--------|
| AOC-4 / MGT-7 | Yes | Yes (MGT-7A) | No | Yes | No | No | Yes |
| Form 8 / Form 11 | No | No | Yes | No | No | No | No |
| DIR-3 KYC | Yes | Yes | Yes (DPIN) | Yes | No | No | Yes |
| ADT-1 | Yes | Yes | No | Yes | No | No | Yes |
| Board Meetings (4/yr) | Yes | 2/yr | No | Yes | No | No | Yes |
| AGM | Yes | No | No | Yes | No | No | Yes |
| GST Returns | If registered | If registered | If registered | If registered | If registered | If registered | If registered |
| TDS Returns | If applicable | If applicable | If applicable | If applicable | If applicable | If applicable | If applicable |
| ITR | ITR-6 | ITR-6 | ITR-5 | ITR-6 | ITR-3/4 | ITR-5 | ITR-6 |
| Statutory Audit | If turnover > Rs 1 Cr | If turnover > Rs 1 Cr | If turnover > Rs 40 L or contribution > Rs 25 L | Yes (all) | No | No | Yes (all) |
| Secretarial Audit | No | No | No | No | No | No | Yes |
| INC-20A | Yes | No | No | No | No | No | Yes |
| EPFO/ESIC | If 20+/10+ emp | If 20+/10+ emp | If 20+/10+ emp | If 20+/10+ emp | If 20+/10+ emp | If 20+/10+ emp | If 20+/10+ emp |
| FC-GPR / FLA | If FDI | If FDI | If FDI | If FDI | No | No | If FDI |

---

## Compliance Scoring

The platform calculates a **compliance health score** for each company:

- **Green (90-100%)**: All tasks completed on time
- **Yellow (70-89%)**: Some tasks due soon or in progress
- **Orange (50-69%)**: Multiple overdue tasks
- **Red (< 50%)**: Critical non-compliance, risk of penalties

### Penalty Exposure Estimation
The platform estimates penalty exposure based on:
- Number of overdue filings
- Days overdue per filing
- Applicable penalty rates (Rs 100/day for ROC, Rs 100/day for GST, etc.)
- Director disqualification risk (2 consecutive years of non-filing)
- Strike-off risk assessment

---

## Compliance Calendar Views

### For Founders
- Monthly/quarterly/yearly calendar view
- Color-coded urgency (green, yellow, orange, red)
- Upcoming deadlines widget on dashboard
- Click-through to task detail and completion

### For CAs
- Cross-company calendar view (all assigned companies)
- Financial year timeline (April - March)
- Task aggregation with filters (by company, by status, by type)
- Audit pack export for auditors
- Notes system per task

### For Admin
- Platform-wide compliance monitoring
- SLA compliance metrics
- Escalation tracking
- Penalty exposure across all companies
