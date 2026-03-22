# Operations & Staffing Plan

This document maps every point in the customer journey where human intervention is required, defines the operational roles needed to run the business, and provides staffing projections for different growth stages.

---

## Part 1: Human Intervention Map

The platform is a **technology-enabled services business**. The software automates pricing, form generation, compliance calendar management, document OCR, and portfolio tracking. But every interaction with government portals, banks, and DSC vendors requires a human professional. Below is an honest breakdown.

### What the Platform Genuinely Automates (No Human Needed)

| Capability | How It Works |
|-----------|-------------|
| Entity type recommendation | AI wizard with 5-question flow + LLM enhancement |
| Dynamic pricing calculation | State-wise stamp duty, government fee slabs, plan tiers — all computed in real-time |
| Payment collection | Razorpay checkout — fully automated order creation, verification, receipt |
| Document OCR extraction | LLM vision extracts PAN/Aadhaar/Passport data with confidence scoring |
| MCA form auto-filling | SPICe+, FiLLiP, RUN, INC-9, DIR-2 forms populated from company/director data |
| MOA/AOA drafting | Templates (Table F for PLC, LLP Agreement) with LLM-powered business objects |
| Compliance calendar generation | 50+ task types auto-generated based on entity type, state, incorporation date |
| Deadline reminders | Email/SMS/in-app at 30/15/7/3/1 days before due date |
| Status auto-transitions | Upcoming → Due Soon → Overdue (runs every 15 minutes via Celery Beat) |
| Cap table calculations | Ownership %, dilution preview, round simulation, exit modeling |
| ESOP vesting math | Monthly/quarterly/annual vesting with cliff, pool utilization tracking |
| E-signatures (internal docs) | Token-based signing with audit trail — no login required for signatories |
| Data room sharing | Token-based access with password, expiry, download limits, access logging |
| Investor portfolio view | Cross-company shareholding aggregation — fully self-serve |
| Escalation detection | Auto-escalates stale tasks (>24h) and pending doc reviews (>12h) |
| Task auto-assignment | Load-balanced assignment to staff by department and current workload |
| SLA breach detection | Monitors time-in-status against SLA targets, flags breaches |
| Notification dispatch | Multi-channel delivery (email, SMS, WhatsApp, in-app) |

### Where Humans Must Intervene

#### Stage 1: Incorporation

| Step | What Platform Does | What Human Must Do | Who Does It | Frequency |
|------|-------------------|-------------------|-------------|-----------|
| **Document verification** | AI extracts data, flags issues, scores confidence | Review AI extraction against original document, check photo quality, approve/reject with checklist | Document Reviewer | Every incorporation (3-5 docs per director) |
| **DSC procurement** | Tracks status, stores details | Contact DSC vendor (e-Mudhra/Capricorn), coordinate video KYC per director, procure USB token, ship to director or office | DSC Coordinator | Every incorporation (1 DSC per director) |
| **Name reservation (RUN)** | Auto-fills RUN form | Log into MCA V3 portal with DSC, upload form, pay Rs 1,000 govt fee, monitor approval (1-3 days) | Filing Coordinator | Every incorporation |
| **MCA filing (SPICe+/FiLLiP)** | Auto-generates all forms as drafts | Review drafted forms for accuracy, digitally sign with DSC, log into MCA V3 portal, upload all forms + attachments, pay government fees, submit | Company Secretary | Every incorporation |
| **MCA query response** | Tracks MCA_QUERY status | Read ROC query, prepare response documents, re-upload corrected forms, resubmit | Company Secretary | ~10-15% of filings |
| **Post-incorporation: Bank account** | Checklist item with deadline | Coordinate with partner bank, prepare document package (COI, MOA, AOA, board resolution, PAN), guide founder through KYC | Filing Coordinator | Every incorporation |
| **Post-incorporation: INC-20A** | Auto-drafts form, tracks 180-day deadline | File INC-20A on MCA portal with proof of bank account and share subscription | Company Secretary | Every PLC/PubLtd |
| **Post-incorporation: First board meeting** | Generates agenda (10 items) and minutes template | Schedule meeting, ensure quorum, conduct meeting (or coordinate virtual), get minutes signed, file with ROC | Company Secretary | Every company |
| **Post-incorporation: Auditor appointment** | Generates ADT-1 form, tracks 30-day deadline | Find a qualified CA, get consent, file ADT-1 on MCA portal | CA / CS | Every company (except LLP, Sole Prop) |

**Key constraint**: MCA V3 portal has no public API. Every filing requires manual DSC-based login, form upload, payment, and submission. There is no way to automate MCA submissions.

#### Stage 2: Ongoing Compliance

| Task | What Platform Does | What Human Must Do | Who Does It | Frequency |
|------|-------------------|-------------------|-------------|-----------|
| **AOC-4 (Financial Statements)** | Tracks deadline, sends reminders | Prepare financial statements, get them audited, draft AOC-4, sign with DSC, upload to MCA, pay fee | Chartered Accountant | Annual (per company) |
| **MGT-7 (Annual Return)** | Tracks deadline, sends reminders | Compile shareholder and director data, fill MGT-7, sign with DSC, submit to MCA | Company Secretary | Annual (per company) |
| **DIR-3 KYC** | Tracks deadline per director | Each director must personally file via MCA portal with Aadhaar + mobile OTP. Staff can coordinate but cannot file on behalf | Filing Coordinator (coordination only) | Annual (per director) |
| **GST returns (GSTR-1, 3B)** | Tracks deadlines, TDS calculator | Compile invoice data, reconcile with GSTR-2A/2B, file on GST portal, make tax payment via challan | Chartered Accountant | Monthly |
| **TDS quarterly returns** | Calculator with section rates, due dates | Compute TDS deducted, prepare return (Form 24Q/26Q/27Q), file on TRACES portal, issue Form 16/16A | Chartered Accountant | Quarterly |
| **ITR filing** | Tracks deadline | Prepare computation of income, fill ITR-5/6, file on Income Tax portal, pay outstanding tax | Chartered Accountant | Annual |
| **Board meetings** | Templates for agenda, minutes, resolutions | Actually hold the meeting (in-person or virtual), ensure quorum, pass resolutions, sign minutes | Company Secretary | Quarterly (4/year) |
| **AGM** | Tracks September 30 deadline | Prepare notice (21 days advance), conduct meeting, pass resolutions, file MGT-15 if required | Company Secretary | Annual |
| **Statutory audit** | Tracks deadline | Engage external auditor, provide books of accounts, coordinate audit, obtain audit report | Chartered Accountant | Annual |
| **EPFO/ESIC monthly** | Tracks deadline | Calculate employee contributions, file on EPFO/ESIC portal, make challan payment | Payroll / Accountant | Monthly |
| **Professional Tax** | Tracks deadline | File on state PT portal, pay challan | Chartered Accountant | Monthly/Annual |
| **FC-GPR / FLA** | Tracks deadline | File FC-GPR on RBI FIRMS portal within 30 days of foreign allotment, file annual FLA return | Company Secretary | Per event / Annual |

**Key constraint**: GST portal, IT portal, TRACES, EPFO/ESIC portals, and RBI FIRMS portal have no open APIs for third-party automated filing. Each requires credential-based login and manual submission.

#### Stage 3: Services Marketplace (100% Human Fulfillment)

| Service Category | What Platform Does | What Human Must Do |
|-----------------|-------------------|-------------------|
| **GST Registration** | Collects payment, creates service request | CA logs into GST portal, fills REG-01, uploads documents, tracks ARN, handles queries |
| **Trademark Registration** | Collects payment, tracks status | Agent files TM-A on IP India portal, handles objections, appears at hearings if needed |
| **FSSAI License** | Collects payment, tracks status | Agent files application on FSSAI portal, coordinates physical inspection (state/central license) |
| **Director/Partner Changes** | Collects payment, tracks status | CS files DIR-12/DIR-11 on MCA portal, drafts board resolution, updates statutory registers |
| **Share Transfer/Allotment** | Collects payment, tracks status | CS files SH-4/PAS-3 on MCA portal, updates share certificates, board resolution |
| **Capital Increase** | Collects payment, tracks status | CS files SH-7 on MCA portal, drafts special resolution, updates MOA |
| **Name/Office Change** | Collects payment, tracks status | CS files INC-24/INC-22 on MCA, handles ROC approval, updates all registrations |
| **Company Closure** | Collects payment, tracks status | CS files STK-2 on MCA, ensures no liabilities, obtains NOCs from IT/GST |
| **Monthly Bookkeeping** | Collects payment, tracks status | Accountant processes transactions in Tally/Zoho, reconciles bank statements, prepares MIS |
| **Payroll Processing** | Collects payment, tracks status | Accountant calculates salaries, TDS, EPF/ESI, generates payslips, files challans |
| **Statutory Audit** | Collects payment, tracks status | External CA auditor conducts full audit of books, issues audit report |
| **Legal Notice Drafting** | Collects payment, tracks status | Lawyer/CS drafts legal notice, reviews with client, sends via registered post |

The marketplace is a **lead generation and payment collection layer**. All actual service delivery is manual. The admin marks service requests through statuses: `pending → accepted → in_progress → documents_needed → completed`.

#### Stage 4: Ongoing Operations

| Activity | What Platform Does | What Human Must Do |
|----------|-------------------|-------------------|
| **Customer communication** | In-app messaging, notification system | Respond to customer queries, request missing documents, explain filing status |
| **Escalation handling** | Auto-detects stale tasks (>24h), doc reviews (>12h), SLA breaches (>48h). Notifies and reassigns | Review escalation, diagnose root cause, take corrective action, close escalation |
| **CA assignment** | Database tracks assignments | Manually assign CAs to new companies based on workload and expertise |
| **Quality review** | N/A | Senior CS/CA reviews filed forms before submission for accuracy |
| **MCA query response** | Tracks status | Read ROC query, prepare response, coordinate with client for additional documents |
| **Refund processing** | Payment records in database | Process refund via Razorpay dashboard, update payment status |
| **Onboarding calls** | N/A | Welcome call to new customers, explain process, set expectations |

---

## Part 2: Operational Roles & Job Descriptions

### Department Structure

```
Operations Head
├── CS Department (Company Secretaries)
│   ├── CS Lead
│   ├── Senior CS
│   └── Junior CS (2-3)
├── CA Department (Chartered Accountants)
│   ├── CA Lead
│   ├── Senior CA
│   └── Junior CA (1-2)
├── Filing & Document Team
│   ├── Filing Lead
│   ├── Document Reviewers (2-3)
│   └── DSC Coordinator (1)
├── Customer Success
│   ├── CS Manager
│   └── Customer Success Associates (1-2)
└── Accounts & Bookkeeping (can be outsourced)
    └── Bookkeeper / Accountant (1-2)
```

---

### Role 1: Operations Head

**Purpose**: Owns the end-to-end delivery of all customer services. Manages SLA compliance, team performance, and process optimization.

**Responsibilities**:
- Monitor SLA dashboard and resolve critical breaches
- Review weekly pipeline metrics (conversion rate, avg processing time, SLA compliance %)
- Manage team hiring, training, and performance reviews
- Define and update SOPs for all filing workflows
- Handle VIP and escalated customer issues
- Coordinate with product team on workflow automation gaps
- Own revenue metrics for services marketplace

**Qualifications**:
- 8+ years in company law, compliance, or CA/CS firm operations
- ACS (Associate Company Secretary) or ACA (Associate Chartered Accountant) preferred
- Experience managing a team of 10+ professionals
- Comfortable with SaaS dashboards and data-driven operations

**Compensation range**: Rs 15-25 LPA

---

### Role 2: Company Secretary (CS) — Lead & Staff

**Purpose**: Handles all MCA filings, board meeting documentation, statutory registers, and corporate governance tasks.

#### CS Lead

**Responsibilities**:
- Review and approve all MCA filings before submission (quality gate)
- Handle MCA queries and ROC objections
- Manage Section 8 license applications (INC-12) and complex filings
- Train junior CS staff on filing procedures
- Own the filing SLA for CS department
- Coordinate with directors for DSC signing

**Qualifications**:
- ACS (Associate Company Secretary) — mandatory
- FCS (Fellow Company Secretary) — preferred
- 5+ years of company incorporation and annual filing experience
- MCA V3 portal proficiency
- Experience with all entity types (PLC, OPC, LLP, Section 8, Public Limited)

**Compensation range**: Rs 10-15 LPA

#### Senior CS

**Responsibilities**:
- File SPICe+/FiLLiP/RUN forms on MCA portal
- Draft and file AOC-4, MGT-7, DIR-3 KYC, ADT-1
- Prepare board meeting agendas, minutes, and resolutions
- Handle director changes (DIR-12), share allotments (PAS-3), and transfers (SH-4)
- File INC-20A commencement declarations
- Maintain statutory registers

**Qualifications**:
- ACS (Associate Company Secretary) — mandatory
- 3+ years of MCA filing experience
- Proficient with DSC-based MCA portal submissions
- Experience with SPICe+, FiLLiP, and annual return forms

**Compensation range**: Rs 6-10 LPA

#### Junior CS

**Responsibilities**:
- Prepare draft filings (data entry into MCA forms)
- Coordinate with clients for missing information and documents
- Track filing status on MCA portal
- Update company status on the Anvils admin dashboard
- Assist with LLP filings (Form 8, Form 11)
- Manage DIR-3 KYC coordination with directors

**Qualifications**:
- CS Executive pass or CS Professional (pursuing)
- 0-2 years experience (can be a CS trainee)
- Familiarity with MCA portal
- Strong attention to detail

**Compensation range**: Rs 3-5 LPA

---

### Role 3: Chartered Accountant (CA) — Lead & Staff

**Purpose**: Handles all tax filings (ITR, GST, TDS), statutory audit coordination, and financial compliance.

#### CA Lead

**Responsibilities**:
- Review and sign off on all ITR filings before submission
- Handle complex tax matters (advance tax calculations, FEMA compliance, transfer pricing)
- Coordinate statutory audits across client portfolio
- Manage GST reconciliation and annual return (GSTR-9) filings
- Train junior CAs on filing procedures
- Own CA department SLA

**Qualifications**:
- ACA (Associate Chartered Accountant) — mandatory
- FCA (Fellow Chartered Accountant) — preferred
- 5+ years in tax compliance and statutory audit
- Experience with IT portal, GST portal, TRACES
- Multi-client portfolio management experience

**Compensation range**: Rs 10-15 LPA

#### Senior CA

**Responsibilities**:
- File monthly GST returns (GSTR-1, GSTR-3B)
- File quarterly TDS returns (Form 24Q, 26Q, 27Q)
- Prepare and file income tax returns (ITR-5, ITR-6)
- Handle GST registration applications
- Calculate and file advance tax installments
- Issue Form 16/16A certificates
- Coordinate with external auditors for statutory audit

**Qualifications**:
- ACA (Associate Chartered Accountant) — mandatory
- 2-4 years in tax practice
- Proficient with GST portal, IT portal, TRACES
- Experience with multi-company tax filing

**Compensation range**: Rs 6-10 LPA

#### Junior CA

**Responsibilities**:
- Prepare tax computations and draft returns
- Compile invoice data for GST returns
- Process TDS calculations using platform calculator
- Track filing deadlines and flag approaching due dates
- Assist with audit documentation and schedules
- Update compliance task status on the platform

**Qualifications**:
- CA Intermediate pass or CA Final (pursuing)
- 0-2 years experience (can be a CA articleship candidate)
- Familiarity with Tally/Zoho Books
- Basic knowledge of IT Act and GST Act

**Compensation range**: Rs 3-5 LPA

---

### Role 4: Filing Coordinator / Document Reviewer

**Purpose**: Handles document verification, DSC procurement, name reservations, and coordination tasks that don't require CS/CA qualifications.

#### Filing Lead

**Responsibilities**:
- Manage document verification queue (assign reviewers, monitor SLA)
- Oversee DSC procurement pipeline
- Handle RUN/RUN-LLP name reservation filings
- Coordinate DIR-3 KYC with directors across all companies
- Manage bank account opening coordination
- Track and resolve document re-upload requests

**Qualifications**:
- Bachelor's degree (B.Com, BBA, or Law preferred)
- 3+ years in company registration or CA/CS firm back-office
- MCA portal familiarity
- Strong organizational and coordination skills

**Compensation range**: Rs 5-8 LPA

#### Document Reviewer

**Responsibilities**:
- Review uploaded documents against AI extraction results
- Verify PAN card details (name, PAN number, DOB, photo match)
- Verify Aadhaar details (name, address, DOB consistency)
- Check photo quality (clear face, white background, proper dimensions)
- Cross-validate name/DOB across PAN and Aadhaar
- Approve or reject with clear customer-facing reason
- Flag suspicious documents for escalation

**Qualifications**:
- Bachelor's degree (any stream)
- 1+ year in document verification, KYC operations, or back-office processing
- Eye for detail — able to spot mismatches and quality issues
- Comfortable with AI confidence scores and verification checklists

**Compensation range**: Rs 2.5-4 LPA

#### DSC Coordinator

**Responsibilities**:
- Place DSC orders with vendors (e-Mudhra, Capricorn, Sify)
- Coordinate video KYC for each director
- Track DSC issuance and USB token delivery
- Maintain DSC expiry tracking across all companies
- Handle DSC renewal for existing clients
- Troubleshoot DSC issues (token not working, driver issues)

**Qualifications**:
- Bachelor's degree (any stream)
- 1+ year working with DSC vendors
- Familiarity with DSC types (Class 2, Class 3, Signing, Combo)
- Good coordination and follow-up skills

**Compensation range**: Rs 2.5-4 LPA

---

### Role 5: Customer Success

**Purpose**: Manages customer relationships, handles queries, onboarding calls, and ensures customer satisfaction.

#### Customer Success Manager

**Responsibilities**:
- Conduct onboarding calls for new customers (set expectations, explain process)
- Handle customer queries via in-app messaging and email
- Coordinate document re-upload requests with clear instructions
- Manage VIP and Urgent-priority customers
- Monitor customer satisfaction and collect feedback
- Upsell compliance subscriptions and marketplace services
- Handle cancellation and refund requests

**Qualifications**:
- Bachelor's degree (any stream)
- 3+ years in customer-facing roles (SaaS, fintech, or professional services)
- Excellent communication (English + Hindi mandatory, regional languages a plus)
- Comfortable explaining regulatory concepts in layman's terms
- Experience with CRM and ticketing systems

**Compensation range**: Rs 5-8 LPA

#### Customer Success Associate

**Responsibilities**:
- Respond to customer messages within SLA (same-day for premium, 24h for standard)
- Follow up on pending document uploads
- Update customers on filing status changes
- Coordinate between CS/CA team and customer when additional info is needed
- Handle basic queries about compliance deadlines and service status

**Qualifications**:
- Bachelor's degree (any stream)
- 0-2 years in customer support or operations
- Good written communication
- Comfortable with dashboard-based tools

**Compensation range**: Rs 2.5-4 LPA

---

### Role 6: Bookkeeper / Accountant (Can Be Outsourced)

**Purpose**: Handles monthly bookkeeping for customers on accounting subscriptions or bookkeeping add-on services.

**Responsibilities**:
- Process monthly transactions in Tally Prime or Zoho Books
- Reconcile bank statements
- Prepare monthly financial statements (P&L, Balance Sheet, Cash Flow)
- Manage accounts payable and accounts receivable entries
- Generate invoices and payment receipts
- Prepare data for GST return filing (pass to CA team)

**Qualifications**:
- B.Com with proficiency in Tally Prime and/or Zoho Books
- 2+ years of bookkeeping experience
- Familiarity with Indian accounting standards
- Ability to manage 15-20 client accounts

**Compensation range**: Rs 3-5 LPA (or outsourced at Rs 1,500-3,000/client/month)

---

## Part 3: Staffing Projections

### Launch Phase (0-100 Active Companies)

| Role | Headcount | Monthly Cost (LPA/12) | Notes |
|------|-----------|----------------------|-------|
| Operations Head | 1 | Rs 1.5L | Can double as CS Lead initially |
| Company Secretary (Senior) | 1 | Rs 0.7L | Handles all MCA filings |
| Company Secretary (Junior) | 1 | Rs 0.3L | Assists with drafting and coordination |
| Chartered Accountant (Senior) | 1 | Rs 0.7L | Handles GST, TDS, ITR for all clients |
| Document Reviewer | 1 | Rs 0.3L | Also handles DSC coordination |
| Customer Success Associate | 1 | Rs 0.3L | Also handles admin messaging |
| **Total** | **6** | **~Rs 3.8L/month** | **~Rs 46 LPA** |

**Capacity**: ~15-20 incorporations/month, ~50-80 compliance clients

---

### Growth Phase (100-500 Active Companies)

| Role | Headcount | Monthly Cost | Notes |
|------|-----------|-------------|-------|
| Operations Head | 1 | Rs 1.7L | |
| CS Lead | 1 | Rs 1.0L | Quality review, complex filings |
| Senior CS | 2 | Rs 1.4L | MCA filings |
| Junior CS | 2 | Rs 0.6L | Drafting, coordination |
| CA Lead | 1 | Rs 1.0L | Tax review, audit coordination |
| Senior CA | 1 | Rs 0.7L | GST, TDS, ITR filing |
| Junior CA | 1 | Rs 0.3L | Data preparation |
| Filing Lead | 1 | Rs 0.5L | Doc verification, DSC, name reservation |
| Document Reviewers | 2 | Rs 0.5L | |
| DSC Coordinator | 1 | Rs 0.3L | |
| Customer Success Manager | 1 | Rs 0.6L | |
| Customer Success Associate | 1 | Rs 0.3L | |
| Bookkeeper (outsourced) | -- | Rs 0.5L | Outsourced, ~30 clients |
| **Total** | **15 + outsourced** | **~Rs 9.4L/month** | **~Rs 1.13 Cr/year** |

**Capacity**: ~50-60 incorporations/month, ~300-500 compliance clients

---

### Scale Phase (500-2000 Active Companies)

| Role | Headcount | Monthly Cost | Notes |
|------|-----------|-------------|-------|
| Operations Head | 1 | Rs 2.0L | |
| CS Lead | 1 | Rs 1.2L | |
| Senior CS | 4 | Rs 2.8L | |
| Junior CS | 4 | Rs 1.2L | |
| CA Lead | 1 | Rs 1.2L | |
| Senior CA | 3 | Rs 2.1L | |
| Junior CA | 2 | Rs 0.6L | |
| Filing Lead | 1 | Rs 0.6L | |
| Document Reviewers | 3 | Rs 0.8L | |
| DSC Coordinator | 1 | Rs 0.3L | |
| Customer Success Manager | 1 | Rs 0.6L | |
| Customer Success Associates | 3 | Rs 0.8L | |
| Bookkeepers (outsourced) | -- | Rs 2.0L | ~100 clients |
| **Total** | **25 + outsourced** | **~Rs 16.2L/month** | **~Rs 1.94 Cr/year** |

**Capacity**: ~100-150 incorporations/month, ~1,000-2,000 compliance clients

---

## Part 4: Seasonal Staffing Considerations

### Peak Filing Periods

| Period | What's Due | Impact |
|--------|-----------|--------|
| **July** | ITR filing deadline (non-audit), TDS Q1 return | CA team at 150% load |
| **September 30** | AGM deadline, DIR-3 KYC deadline | CS + CA at 150% load |
| **October** | ITR filing deadline (audit cases), TDS Q2, AOC-4 (30 days post-AGM) | Full team at 200% load |
| **November-December** | MGT-7 (60 days post-AGM), GSTR-9 (Dec 31) | CS + CA at 150% load |
| **March** | Financial year closing, advance tax Q4, annual PT | CA team at 150% load |

### Mitigation Strategies

1. **Seasonal contractors**: Hire 3-5 CS/CA interns or semi-qualified staff for Aug-Dec peak
2. **Staggered AGMs**: Encourage clients to hold AGMs in July-August to spread filing load
3. **Batch processing**: Process DIR-3 KYC in batches (July-August) before September 30 deadline
4. **Outsource bookkeeping**: Always outsource bookkeeping — it scales linearly and margins are thin
5. **Automation priority**: Invest in automating document review (highest volume, most repetitive) to free up staff during peak

---

## Part 5: SLA Targets (Built into Platform)

The platform already enforces these SLA targets (from [sla_service.py](backend/src/services/sla_service.py)):

| Transition | Target | Staff Responsible |
|-----------|--------|-------------------|
| Payment completed → Documents pending | 4 hours | Auto (system) |
| Documents uploaded → Documents verified | 24 hours | Document Reviewer |
| Documents verified → Name reserved | 48 hours | Filing Coordinator |
| Name reserved → Filing drafted | 72 hours | Junior CS |
| Filing drafted → Filing under review | 24 hours | Senior CS / CS Lead |
| Filing under review → Filing submitted | 48 hours | Senior CS |
| Filing submitted → MCA processing | 24 hours | Auto (system status update) |
| MCA processing → Incorporated | 168 hours (7 days) | External (MCA/ROC) |
| Incorporated → Bank account pending | 24 hours | Customer Success |

Escalation rules auto-trigger at:
- **Document review pending > 12 hours** → Notify CS Lead
- **Filing task stale > 24 hours** → Notify CS Lead
- **Filing task overdue > 48 hours** → Notify + reassign to CS Lead
- **SLA breach > 72 hours (high/urgent)** → Escalate to Admin/Operations Head

---

## Part 6: Unit Economics per Customer

### Incorporation Customer

| Item | Revenue | Cost (Staff Time) | Margin |
|------|---------|-------------------|--------|
| Platform fee (avg) | Rs 7,000 | ~4 hours staff time @ Rs 300/hr = Rs 1,200 | Rs 5,800 (83%) |
| DSC procurement | Included in platform fee | 1 hour coordination = Rs 300 | -- |
| Document review | Included | 30 min per director = Rs 150 | -- |
| MCA filing | Included | 2 hours CS time = Rs 600 | -- |
| Post-incorporation | Included | 1.5 hours = Rs 450 | -- |

**Gross margin on incorporation: ~75-85%** (higher for simpler entities like Sole Prop)

### Compliance Subscription Customer

| Plan | Monthly Revenue | Monthly Staff Cost | Monthly Margin |
|------|---------------|-------------------|----------------|
| Starter (Rs 999) | Rs 999 | ~2 hours/month = Rs 600 | Rs 399 (40%) |
| Growth (Rs 2,999) | Rs 2,999 | ~4 hours/month = Rs 1,200 | Rs 1,799 (60%) |
| Scale (Rs 4,999) | Rs 4,999 | ~6 hours/month = Rs 1,800 | Rs 3,199 (64%) |
| Enterprise (Rs 9,999) | Rs 9,999 | ~10 hours/month = Rs 3,000 | Rs 6,999 (70%) |
| Peace of Mind (Rs 9,999) | Rs 9,999 | ~8 hours/month = Rs 2,400 | Rs 7,599 (76%) |

**Key insight**: Higher plans have better margins because the platform automates calendar/reminders (fixed cost), while staff time only grows linearly with filing complexity.

### Marketplace Service

| Service | Revenue | Staff Cost | Margin |
|---------|---------|-----------|--------|
| GST Registration (Rs 1,499) | Rs 1,499 | ~2 hours = Rs 600 | Rs 899 (60%) |
| Annual ROC Filing (Rs 7,999) | Rs 7,999 | ~4 hours = Rs 1,200 | Rs 6,799 (85%) |
| ITR Filing - Company (Rs 9,999) | Rs 9,999 | ~6 hours = Rs 1,800 | Rs 8,199 (82%) |
| Monthly Bookkeeping (Rs 2,999) | Rs 2,999 | ~8 hours = Rs 2,400 | Rs 599 (20%) |
| Statutory Audit (Rs 14,999) | Rs 14,999 | ~12 hours = Rs 3,600 | Rs 11,399 (76%) |

**Key insight**: Bookkeeping has the worst margins. Consider outsourcing entirely or pricing it higher.

---

## Part 7: What to Automate Next (Highest Impact)

Priority list of automation investments to reduce staffing needs:

| Priority | Automation | Current State | Impact | Saves |
|----------|-----------|--------------|--------|-------|
| 1 | **Auto-approve high-confidence documents** | AI extracts + human reviews ALL docs | Auto-approve when AI confidence > 95% and all cross-checks pass. Human reviews only flagged docs | 60-70% of reviewer time |
| 2 | **GSP (GST Suvidha Provider) integration** | Manual GST portal filing | File GSTR-1, GSTR-3B via GSP API (ClearTax, Masters India) | 1-2 CA hours/client/month |
| 3 | **DSC vendor API integration** | Manual phone/email coordination | Place DSC orders via vendor API, track status automatically | 1 full-time role |
| 4 | **Tally/Zoho auto-pull for financial data** | Manual data compilation | Pull trial balance, P&L, BS for AOC-4/ITR auto-drafting | 2-3 hours/filing |
| 5 | **Bulk DIR-3 KYC coordination** | Manual email/call per director | Automated email + SMS with step-by-step instructions and deadline | 50% of filing coordinator time in Sep |
| 6 | **Bank account opening API** | Manual coordination with banks | Partner bank APIs (ICICI, HDFC startup programs) for digital account opening | 1 hour per incorporation |
