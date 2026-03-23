# Anvils — Platform Inventory & Persona Activity Map

Comprehensive inventory of everything built on the Anvils platform, with independent analysis of every activity for each customer persona, broken down by entity type (Private Limited, LLP, OPC).

---

## Table of Contents

1. [Platform Inventory Summary](#1-platform-inventory-summary)
2. [Founder Persona](#2-founder-persona)
3. [CA (Chartered Accountant) Persona](#3-ca-chartered-accountant-persona)
4. [CS (Company Secretary) Persona](#4-cs-company-secretary-persona)
5. [Investor Persona](#5-investor-persona)
6. [Admin/Ops Persona](#6-adminops-persona)
7. [Entity-Type Breakdown](#7-entity-type-breakdown)
8. [Gap Analysis](#8-gap-analysis)

---

## 1. Platform Inventory Summary

### Frontend Applications

| App | Pages | Stack |
|-----|-------|-------|
| **Main Frontend** (`/frontend`) | 68 pages | Next.js, React 19, TypeScript |
| **Admin Portal** (`/admin-portal`) | 18 pages | Next.js, React, TypeScript |
| **Total** | **86 pages** | |

### Backend

| Component | Count |
|-----------|-------|
| API Routers | 28 |
| Endpoints | ~285 |
| Models (files) | 32 |
| Model Classes | 70+ |
| Services | 59 |
| AI Agents | 5 |
| Celery Workers | 3 |

### Infrastructure

| Layer | Technology |
|-------|-----------|
| Compute | GCP Cloud Run (3 services) |
| Database | PostgreSQL 18 (Cloud SQL) |
| Cache | Redis 7 (Memorystore) |
| Task Queue | Celery + Redis |
| Storage | GCS Buckets |
| CI/CD | Cloud Build (path-filtered) |
| Container | Docker + Artifact Registry |

---

## 2. Founder Persona

The founder is the primary user. Their journey spans from pre-incorporation through ongoing company management. **What a founder needs depends heavily on their entity type.**

### 2.1 Incorporation

The incorporation workflow is fully entity-specific. Different entity types go through completely different filing processes with different government forms.

#### Private Limited Company (Pvt Ltd)

| Step | Action | Gov Form | Backend Service |
|------|--------|----------|-----------------|
| 1 | DSC Procurement (all directors) | Class 3 DSC | `dsc_service.py` |
| 2 | DIN Application | DIR-3 | `incorporation_service.py` |
| 3 | Name Reservation | RUN (INC-1) | `incorporation_service.py` |
| 4 | SPICe+ Part A | INC-32 Part A | `mca_form_service.py` |
| 5 | SPICe+ Part B | INC-32 Part B | `mca_form_service.py` |
| 6 | MOA & AOA Drafting | INC-33, INC-34 | `contract_template_service.py` |
| 7 | MCA Filing | Complete package | `incorporation_service.py` |

**Unique requirements:** Minimum 2 directors, minimum 2 shareholders, authorized share capital declaration, registered office address proof.

**Post-incorporation (one-time):**
- INC-20A (Commencement of Business Declaration) — within 180 days
- First Board Meeting — within 30 days of incorporation
- Open bank account
- Apply for PAN/TAN (auto via SPICe+)
- GST Registration (if applicable)

#### One Person Company (OPC)

| Step | Action | Gov Form | Backend Service |
|------|--------|----------|-----------------|
| 1 | Nominee Declaration | INC-3 | `incorporation_service.py` |
| 2 | DSC Procurement (sole member) | Class 3 DSC | `dsc_service.py` |
| 3 | DIN Application | DIR-3 | `incorporation_service.py` |
| 4 | Name Reservation | RUN (INC-1) | `incorporation_service.py` |
| 5 | SPICe+ Filing (with INC-3) | INC-32 | `mca_form_service.py` |
| 6 | MOA & AOA (OPC format) | INC-33, INC-34 | `contract_template_service.py` |
| 7 | MCA Filing | Complete package | `incorporation_service.py` |

**Unique requirements:** Only 1 director/member allowed, must nominate a successor (INC-3), paid-up capital capped at Rs 50L, turnover capped at Rs 2Cr (else mandatory conversion to Pvt Ltd).

**Post-incorporation:**
- Same as Pvt Ltd except: NO AGM required, NO board meetings required, financial statements due within 180 days of FY end (not after AGM).

#### LLP (Limited Liability Partnership)

| Step | Action | Gov Form | Backend Service |
|------|--------|----------|-----------------|
| 1 | DSC Procurement (designated partners) | Class 3 DSC | `dsc_service.py` |
| 2 | DPIN Application | DIR-3 | `incorporation_service.py` |
| 3 | Name Reservation | RUN-LLP | `incorporation_service.py` |
| 4 | FiLLiP Filing | FiLLiP | `incorporation_service.py` |
| 5 | LLP Agreement Drafting | Partnership deed | `contract_template_service.py` |
| 6 | ROC Filing (Form 3) | Form 3 | `incorporation_service.py` |

**Unique requirements:** Minimum 2 designated partners, LLP Agreement must be filed within 30 days of incorporation, no concept of share capital — profit-sharing ratios defined in agreement.

**Post-incorporation:**
- File LLP Agreement with ROC (Form 3) within 30 days
- Open bank account
- GST Registration (if applicable)
- NO board meetings, NO AGM, NO statutory registers (member/share/transfer registers)

**Frontend pages used:** `/pricing` (entity selection), `/dashboard` (pipeline tracking), `/dashboard/connect` (existing company).
**Backend:** `companies.py`, `wizard.py`, `documents.py`, `post_incorporation.py` routers.

---

### 2.2 Compliance Calendar

Compliance obligations differ dramatically by entity type. This is the core ongoing value of the platform.

#### Private Limited — 18+ Annual Compliance Tasks

| Category | Task | Frequency | Deadline | Penalty |
|----------|------|-----------|----------|---------|
| **ROC Filings** | AOC-4 (Financial Statements) | Annual | 30 days after AGM | Rs 100/day |
| | MGT-7 (Annual Return) | Annual | 60 days after AGM | Rs 100/day |
| | DIR-3 KYC (per director) | Annual | Sep 30 | Rs 5,000 flat |
| | ADT-1 (Auditor Appointment) | Annual | 15 days after AGM | Rs 100/day |
| **Board Meetings** | Q1 Board Meeting | Quarterly | Jun 30 | Rs 25,000 |
| | Q2 Board Meeting | Quarterly | Sep 30 | Rs 25,000 |
| | Q3 Board Meeting | Quarterly | Dec 31 | Rs 25,000 |
| | Q4 Board Meeting | Quarterly | Mar 31 | Rs 25,000 |
| **Shareholder** | AGM (Annual General Meeting) | Annual | Sep 30 | Rs 1,00,000 |
| **Tax** | Income Tax Return | Annual | Oct 31 | Rs 10,000 |
| | Advance Tax Q1-Q4 | Quarterly | Jun 15, Sep 15, Dec 15, Mar 15 | 1%/month (234C) |
| **TDS** | TDS Return Q1-Q4 | Quarterly | Jul 31, Oct 31, Jan 31, May 31 | Rs 200/day |
| | Form 16/16A Issuance | Annual | Jun 15 | — |

**Total annual compliance events: 18+**

#### OPC — 4 Annual Compliance Tasks

| Category | Task | Frequency | Deadline | Penalty |
|----------|------|-----------|----------|---------|
| **ROC Filings** | AOC-4 (Financial Statements) | Annual | 180 days from FY end | Rs 100/day |
| | MGT-7A (Simplified Annual Return) | Annual | 60 days after AOC-4 | Rs 100/day |
| | DIR-3 KYC | Annual | Sep 30 | Rs 5,000 |
| **Tax** | Income Tax Return | Annual | Oct 31 | Rs 10,000 |

**No board meetings. No AGM. No TDS returns (unless employees/vendors paid). No advance tax (unless liability > Rs 10,000). Total: 4 mandatory tasks.**

#### LLP — 4 Annual Compliance Tasks

| Category | Task | Frequency | Deadline | Penalty |
|----------|------|-----------|----------|---------|
| **ROC Filings** | Form 11 (LLP Annual Return) | Annual | May 30 | Rs 100/day |
| | Form 8 (Statement of Solvency) | Annual | Oct 30 | Rs 100/day |
| | DIR-3 KYC (designated partners) | Annual | Sep 30 | Rs 5,000 |
| **Tax** | ITR-5 (LLP Income Tax) | Annual | Oct 31 | Rs 10,000 |

**No board meetings. No AGM. No AOC-4/MGT-7. No TDS/advance tax by default. Total: 4 mandatory tasks.**

**Frontend:** `/dashboard/compliance` — Compliance score, calendar, overdue tracker, penalty calculator, TDS calculator.
**Backend:** `compliance.py` router, `compliance_engine.py` service — auto-generates entity-specific task calendars.

---

### 2.3 Cap Table Management

**Applies to:** Pvt Ltd, OPC. **Does NOT apply to:** LLP (no share capital — partners have profit-sharing ratios instead).

| Activity | Frontend | Backend | Notes |
|----------|----------|---------|-------|
| Add shareholders | `/dashboard/cap-table` (Add Shareholder tab) | `cap_table.py` | Name, shares, face value, type, PAN |
| Issue shares | `/dashboard/cap-table` (Issue Shares tab) | `cap_table.py` | Guided wizard with allotment details |
| Record transfers | `/dashboard/cap-table` (Record Transfer tab) | `cap_table.py` | SH-4 form documentation |
| View ownership chart | `/dashboard/cap-table` (Overview tab) | `cap_table.py` | Pie chart + shareholder table |
| Transaction history | `/dashboard/cap-table` (Transaction History tab) | `cap_table.py` | All allotments and transfers |
| Generate share certificates | `/dashboard/cap-table` | `cap_table.py` | HTML certificate per shareholder |
| Round simulator | `/dashboard/cap-table` (Round Simulator tab) | `cap_table.py` | Model dilution from new rounds |
| Exit scenarios | `/dashboard/cap-table` (Exit Scenarios tab) | `cap_table.py` | Calculate payouts at different valuations |
| Waterfall analysis | `/dashboard/cap-table` (Waterfall tab) | `cap_table.py` | Liquidation preference modeling (1x, 1.5x, participating) |

**LLP alternative:** LLP Agreement defines profit-sharing ratios. No cap table concept. Partner changes require an amendment to the LLP Agreement (Form 3 filing with ROC).

---

### 2.4 ESOP Management

**Applies to:** Pvt Ltd (primary use case). **Can apply to:** OPC (rare). **Does NOT apply to:** LLP (no share capital).

| Activity | Frontend | Backend |
|----------|----------|---------|
| Create ESOP plan | `/dashboard/esop` (Plans tab) | `esop.py` router |
| Set vesting schedule | Plan creation wizard | `esop_service.py` |
| Issue grants to employees | `/dashboard/esop` (Grants tab) | `esop.py` |
| Generate grant letters | Grant detail view | `legal_document_service.py` |
| Send for e-signature | Grant detail actions | `esign_service.py` |
| Exercise vested options | `/dashboard/esop` (Grant actions) | `esop_service.py` → `cap_table_service.py` |
| Track pool utilization | `/dashboard/esop` (Pool Summary tab) | `esop.py` |
| Board/shareholder approval flow | `/dashboard/esop` (Approval Flow tab) | `esop_service.py` |

**Pvt Ltd specifics:** ESOP requires board resolution + special resolution (75% shareholder approval). Exercise price must be at or above FMV (Rule 11UA valuation required).

**OPC:** Technically possible but rarely used — solo founder companies don't typically have employee equity programs.

---

### 2.5 Fundraising & Deal Management

**Applies to:** Pvt Ltd (primary), OPC (rare — must convert to Pvt Ltd if raising above limits).
**Does NOT apply to:** LLP (partners can contribute capital via LLP Agreement amendment, not through investment rounds).

| Activity | Frontend | Backend |
|----------|----------|---------|
| Create funding round | `/dashboard/fundraising` | `fundraising.py` |
| Set instrument type | Round creation (equity, SAFE, CCD, debt) | `fundraising.py` |
| Add investors | Round detail page | `fundraising.py` |
| Track investor status | Round detail (committed → received → signed → issued) | `fundraising.py` |
| Link legal documents | Round detail (SHA, SSA, term sheet) | `fundraising.py` |
| Initiate closing room | Round actions | `esign_service.py` |
| Monitor e-signing | Closing room view | `esign_service.py` |
| Complete share allotment | Post-close action | `cap_table_service.py` |
| Share deal with investors | Round actions | `fundraising.py` → `investor_portal.py` |
| View investor interests | Round detail | `companies.py` |

**OPC limitation:** If paid-up capital exceeds Rs 50L or turnover exceeds Rs 2Cr, OPC must mandatorily convert to Pvt Ltd. Fundraising typically triggers this conversion.

---

### 2.6 Board Meetings & Statutory Registers

**Applies to:** Pvt Ltd (mandatory quarterly + AGM), OPC (no mandatory meetings), LLP (no board meetings).

| Activity | Pvt Ltd | OPC | LLP |
|----------|---------|-----|-----|
| Schedule board meeting | Mandatory quarterly | Not required | N/A — no board |
| Send meeting notice | Required (7+ days) | N/A | N/A |
| Record attendance | Director attendance | N/A | N/A |
| Create agenda | Standard agenda items | N/A | N/A |
| Record minutes | Mandatory with signatures | N/A | N/A |
| Pass resolutions | Board + special resolutions | Written resolutions (sole member) | Partner consent |
| Sign minutes electronically | Via e-sign service | N/A | N/A |
| AGM | Mandatory (within 6 months of FY end) | Not required | N/A |
| Maintain statutory registers | Members, Directors, Shares, Transfers, Charges | Same (but simpler — 1 member) | No statutory registers |

**Frontend:** `/dashboard/meetings` (create, manage, notice, attendance, minutes, resolutions, export), `/dashboard/registers`.
**Backend:** `meetings.py`, `statutory_registers.py` routers.

---

### 2.7 Documents & Legal Templates

Available to all entity types, but the relevant templates differ.

| Category | Pvt Ltd Templates | OPC Templates | LLP Templates |
|----------|-------------------|---------------|---------------|
| Startup Essentials | Founders' Agreement, SHA, SSA, NDA, IP Assignment | Same (simplified) | Partnership Deed, NDA |
| Fundraising | Term Sheet, SAFE, CCD, SPA, SHA | Same (with OPC conversion note) | N/A |
| HR & Employment | Employment Agreement, Offer Letter, ESOP Grant Letter | Same | Same (no ESOP) |
| Corporate Governance | Board Resolution, AGM Notice, Minutes Template | Written Resolution Template | Partner Resolution |
| Equity | Share Transfer Form (SH-4), PAS-1 | Same | N/A |
| Compliance | DIR-3 KYC, INC-20A, ADT-1 | DIR-3 KYC, INC-20A | Form 11, Form 8 |

**Frontend:** `/dashboard/documents` — Browse by category, generate, request signatures.
**Backend:** `legal_docs.py`, `documents.py`, `contract_template_service.py`.

---

### 2.8 Data Room

Applies equally to all entity types. Used primarily during fundraising or due diligence.

| Activity | Frontend | Backend |
|----------|----------|---------|
| Create folders | `/dashboard/data-room` | `data_room.py` |
| Upload documents | Folder detail view | `data_room.py` |
| Version documents | File actions | `data_room.py` |
| Create share links | Share panel | `data_room.py` |
| Set permissions (view/download, expiry, password) | Share link settings | `data_room.py` |
| Track access logs | Access analytics | `data_room.py` |
| Revoke access | Share link management | `data_room.py` |

**15 backend endpoints** for folder/file/share-link CRUD.

---

### 2.9 Valuations (Fair Market Value)

**Applies to:** Pvt Ltd (for ESOP exercise price, fundraising), OPC (rare). **Less relevant for:** LLP.

| Activity | Frontend | Backend |
|----------|----------|---------|
| Calculate NAV valuation | `/dashboard/valuations` | `valuations.py` |
| Calculate DCF valuation | `/dashboard/valuations` | `valuations.py` |
| Save valuation record | Valuation actions | `valuations.py` |
| View valuation history | `/dashboard/valuations` | `valuations.py` |
| Use for ESOP pricing | Referenced from ESOP module | `valuation_service.py` |

**Rule 11UA compliance:** FMV required for ESOP exercise pricing and equity issuance to non-residents.

---

### 2.10 Accounting Integration

Applies to all entity types equally.

| Activity | Frontend | Backend |
|----------|----------|---------|
| Connect Zoho Books (OAuth) | `/dashboard/accounting` | `accounting.py` |
| Connect Tally Prime | `/dashboard/accounting` | `accounting.py` |
| Sync financial data | Dashboard action | `accounting.py` |
| Disconnect integration | Settings | `accounting.py` |

---

### 2.11 GST & Tax

| Activity | Pvt Ltd | OPC | LLP |
|----------|---------|-----|-----|
| GST dashboard (GSTR-1, 3B, 9) | Full GST tracking | Same | Same |
| TDS tracking (quarterly returns) | Mandatory if deducting | Rarely applicable | Rarely applicable |
| Advance tax installments | Quarterly if liability > Rs 10K | Same | Same |
| ITR filing tracking | ITR-6 | ITR-6 | ITR-5 |
| Tax audit (44AB) | If turnover > Rs 1Cr | Same | Same |

**Frontend:** `/dashboard/gst`, `/dashboard/tax`.
**Backend:** `compliance.py` (GST dashboard, tax overview, audit pack endpoints).

---

### 2.12 Other Founder Activities

| Activity | Pages | All Entities? |
|----------|-------|---------------|
| **Stakeholder profiles** | `/dashboard/stakeholders` | Yes |
| **Team management** (invite, roles) | `/dashboard/team` | Yes |
| **Billing & subscription** | `/dashboard/billing` | Yes |
| **Notifications** | `/dashboard/notifications` | Yes |
| **Company profile** | `/dashboard/company-info` | Yes |
| **Services marketplace** | `/dashboard/services` | Yes |
| **AI Copilot chat** | Widget on dashboard | Yes |
| **Educational content** | `/learn` | Yes |

---

## 3. CA (Chartered Accountant) Persona

### Status: FULLY BUILT

**Role:** `CA_LEAD` | **Portal:** `/ca` (7 dedicated pages) | **API Endpoints:** 18 | **Frontend API Functions:** 17

### 3.1 Access Model

- Multi-company assignment via `CAAssignment` table (CA linked to N companies)
- Read-only access to company compliance data, documents, and tasks
- Can mark filings complete and add task notes (write access for task management only)
- Professional dark teal/navy UI theme distinct from founder dashboard

### 3.2 Activity Map

| Activity | Page | Endpoints | Entity Differences |
|----------|------|-----------|-------------------|
| **Portfolio dashboard** | `/ca` | `GET /ca/dashboard-summary`, `GET /ca/scores` | Shows all entity types mixed |
| **View assigned companies** | `/ca/companies` | `GET /ca/companies` | Entity type shown per company |
| **Company compliance detail** | `/ca/companies/[id]` | `GET /ca/companies/{id}/compliance` | Tasks differ by entity type |
| **Mark filing complete** | `/ca/companies/[id]` (modal) | `PUT /ca/companies/{id}/filings/{task_id}` | Same flow, different forms |
| **Add task notes** | `/ca/companies/[id]` (notes section) | `POST /ca/companies/{id}/tasks/{task_id}/notes` | Same across entities |
| **View all tasks (cross-company)** | `/ca/tasks` | `GET /ca/tasks?status=` | Entity-specific task types |
| **Compliance calendar (FY view)** | `/ca/calendar` | Uses `/ca/tasks` data | LLPs have fewer entries |
| **Tax overview (ITR/TDS/advance)** | `/ca/tax` | `GET /ca/companies/{id}/tax-overview` | ITR form differs (ITR-5 vs ITR-6) |
| **GST dashboard** | `/ca/tax` | `GET /ca/companies/{id}/gst-dashboard` | Same across entities |
| **TDS calculator** | `/ca/tds` | `POST /ca/tds/calculate`, `GET /ca/tds/sections` | Same calculation engine |
| **TDS due dates reference** | `/ca/tds` | `GET /ca/tds/due-dates?quarter=` | Same quarterly deadlines |
| **Audit pack export** | `/ca/companies/[id]` (Audit Pack tab) | `GET /ca/companies/{id}/audit-pack` | Checklist differs by entity |
| **Penalty estimation** | `/ca` dashboard banner | `GET /ca/companies/{id}/penalties` | Penalty rates vary |
| **View documents** | `/ca/companies/[id]` (Documents tab) | `GET /ca/companies/{id}/documents` | Document types differ |

### 3.3 CA Services by Entity Type

| Service | Pvt Ltd | OPC | LLP |
|---------|---------|-----|-----|
| ITR Filing | ITR-6 (Rs 4,999) | ITR-6 (Rs 4,999) | ITR-5 (Rs 2,999) |
| GST Monthly Filing | Rs 999/mo | Rs 999/mo | Rs 999/mo |
| GST Annual Return (GSTR-9) | Rs 4,999 | Rs 4,999 | Rs 4,999 |
| TDS Quarterly Return | Rs 2,499/qtr | Rarely needed | Rarely needed |
| Statutory Audit | Rs 14,999 | Rs 14,999 (if applicable) | Rs 14,999 (if applicable) |
| Monthly Bookkeeping | Rs 2,999-5,999/mo | Rs 2,999/mo | Rs 2,999/mo |
| Payroll Processing | Rs 1,999/mo | Rarely needed | Rs 1,999/mo |

### 3.4 CA Journey

```
Login → Dashboard (portfolio overview, penalty alerts)
  ├→ Companies → Company Detail → Compliance Tasks → Mark Complete / Add Notes
  ├→ All Tasks → Filter by status → Mark Complete
  ├→ Calendar → FY timeline → Navigate to company
  ├→ Tax → Select company → View ITR/TDS/GST/Advance Tax status
  └→ TDS Calculator → Calculate TDS for any section
```

---

## 4. CS (Company Secretary) Persona

### Status: BACKEND INFRASTRUCTURE ONLY — NO FRONTEND PORTAL

**Role:** `CS_LEAD` | **Portal:** None (no `/cs` pages) | **Backend endpoints:** 25+ (via `/ops` — internal only)

### 4.1 What's Built

**Backend infrastructure:**
- `CS_LEAD` role defined in `UserRole` enum
- Filing task types mapped to `StaffDepartment.CS` in `assignment_service.py`
- Auto-assignment logic (load-balanced across available CS staff)
- Task lifecycle: UNASSIGNED → ASSIGNED → IN_PROGRESS → COMPLETED
- Escalation framework (SLA breach triggers escalation to CS_LEAD)
- Performance metrics calculation
- Task handoff between CS staff

### 4.2 CS-Assigned Filing Tasks by Entity Type

| Task Type | Pvt Ltd | OPC | LLP |
|-----------|---------|-----|-----|
| SPICe+ Part A | Yes | Yes | No |
| SPICe+ Part B | Yes | Yes | No |
| FiLLiP Filing | No | No | Yes |
| MOA/AOA Drafting | Yes | Yes (OPC format) | No |
| LLP Agreement | No | No | Yes |
| MCA Filing | Yes | Yes | No |
| ROC Filing | Yes | Yes | Yes |
| INC-12 License | No | No | No (Section 8 only) |
| Nominee Declaration (INC-3) | No | Yes | No |
| INC-20A (Commencement) | Yes | Yes | No |
| Board Meeting coordination | Yes | No | No |
| MGT-7 / MGT-7A | Yes / No | No / Yes | No |
| Form 11 (LLP Annual Return) | No | No | Yes |

### 4.3 What's Missing

- **No `/cs` frontend portal** — CS staff have no web interface to view/manage their tasks
- **No CS-specific dashboard** — unlike the CA portal which has 7 pages
- **No CS onboarding flow** — no way to invite or register CS users through the platform
- **No CS assignment UI** — admins can only assign CS tasks via API or admin portal

### 4.4 CS vs CA Portal Comparison

| Dimension | CA Portal | CS Portal |
|-----------|-----------|-----------|
| Frontend pages | 7 fully built | 0 (none) |
| API endpoints | 18 (customer-facing) | 25+ (internal `/ops` only) |
| Assignment model | Company-centric (`CAAssignment`) | Task-centric (`FilingTask`) |
| View paradigm | "My companies → their tasks" | "My queue → execute task" |
| Services | Tax, GST, audit, bookkeeping | Incorporation, ROC filings, amendments |
| UX | Professional dark theme | N/A |

---

## 5. Investor Persona

### Status: FULLY BUILT (token-based + authenticated)

### 5.1 Two Access Modes

**Token-Based Access (no login required):**
- Founder generates a unique portal token for each investor
- Investor opens `/investor/[token]` to access their dashboard
- No signup, no password, no account creation needed

**Authenticated Access:**
- Investor creates an account and logs in
- Links to stakeholder profiles across multiple companies
- Full portfolio view

### 5.2 Investor Activity Map

| Activity | Page | Endpoints | Notes |
|----------|------|-----------|-------|
| **View portfolio** | `/investor/[token]` | `GET /investor-portal/{token}/portfolio` | All companies, shares, percentages |
| **View cap table** | `/investor/[token]/cap-table` | `GET /investor-portal/{token}/cap-table` | Full cap table with ownership highlighted |
| **View funding rounds** | `/investor/[token]/rounds` | `GET /investor-portal/{token}/rounds` | All rounds + investor participation |
| **View ESOP grants** | `/investor/[token]` | `GET /investor-portal/{token}/grants` | Option grants + vesting schedule |
| **Download documents** | `/investor/[token]` | `GET /investor-portal/{token}/documents` | SHA, SSA, pitch deck, etc. |
| **Discover companies** | `/investor/[token]/discover` | `GET /investor-portal/{token}/discover` | Browse fundraising companies |
| **Express interest** | Discovery page | `POST /investor-portal/{token}/express-interest` | Show interest in a company |
| **View shared deals** | `/investor/[token]` | `GET /investor-portal/{token}/my-interests` | Deals shared by founders |
| **Accept/reject deals** | Deal detail | Token-based actions | Accept/pass on shared deals |

### 5.3 Entity Type Relevance

| Feature | Pvt Ltd | OPC | LLP |
|---------|---------|-----|-----|
| Portfolio tracking | Full shareholding | Full shareholding | N/A (partners, not shareholders) |
| Cap table access | Full cap table | Full cap table | N/A |
| Funding round visibility | All rounds | All rounds | N/A |
| ESOP grant tracking | If employee-investor | Rare | N/A |
| Document access | SHA, SSA, term sheet | Same | LLP Agreement (if partner) |
| Company discovery | Fundraising companies | Same | Same |

**Marketing pages:** `/for/investors` — explains investor portal, has token entry form.
**Backend:** `investor_portal.py` router (10+ endpoints), `fundraising.py` (deal sharing).

---

## 6. Admin/Ops Persona

### Status: FULLY BUILT (separate admin-portal app)

### 6.1 Admin Portal Pages (18 pages)

| Section | Pages | Activities |
|---------|-------|-----------|
| **Dashboard** | `/` | KPI cards (total companies, revenue, active tasks), recent activity feed |
| **Pipeline** | `/pipeline` | Kanban board of all companies by status (25 statuses from draft → fully_setup) |
| **Companies** | `/companies`, `/companies/[id]` | List all companies, detail view with tabs (overview, documents, tasks, notes, communication, payments) |
| **Ops / Tasks** | `/ops/tasks`, `/ops/tasks/[id]` | Filing task management — create, assign, claim, status update, bulk operations |
| **Ops / Review Queue** | `/ops/review` | Document verification queue — claim reviews, approve/reject documents |
| **Ops / Escalations** | `/ops/escalations` | SLA breach escalation management — view, resolve escalation logs |
| **Ops / Workload** | `/ops/workload` | Staff workload dashboard — task distribution across team |
| **Ops / Staff** | `/ops/staff` | Staff management — departments, seniority, hierarchy |
| **Ops / Escalation Rules** | `/ops/escalation-rules` | Configure SLA thresholds and escalation triggers |
| **Analytics** | `/analytics` | Revenue analytics, conversion funnels, cohort analysis |
| **Messages** | `/messages`, `/messages/[id]` | Customer communication — inbox, reply, internal notes |
| **Settings** | `/settings` | Portal configuration |

### 6.2 Admin Activities by Company Entity Type

| Activity | Pvt Ltd | OPC | LLP |
|----------|---------|-----|-----|
| Pipeline management | 25 statuses (draft → fully_setup) | Same pipeline | Same pipeline |
| Filing task generation | 7 incorporation steps | 7 incorporation steps | 6 incorporation steps |
| Task assignment (CS) | SPICe+, MOA/AOA, MCA Filing | SPICe+, INC-3, MOA/AOA | FiLLiP, LLP Agreement, ROC |
| Task assignment (CA) | AOC-4, GST, PAN/TAN, ADT-1 | AOC-4, PAN/TAN | Form 8, PAN/TAN |
| Document verification | Director docs, MOA, AOA, DSC | Same + INC-3 (nominee) | Partner docs, LLP Agreement |
| SLA monitoring | Same SLA rules | Same SLA rules | Same SLA rules |
| Customer messaging | Same channel | Same channel | Same channel |

### 6.3 Admin Backend (ops.py — 30+ endpoints)

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Filing Tasks | 10 | Create, list, get, update, assign, claim, generate, handoff, delete |
| Review Queue | 4 | List, add, claim, verify document |
| Escalations | 5 | List, resolve, CRUD for escalation rules |
| Workload | 3 | Dashboard, my performance, all performance |
| Staff | 2 | List staff, update hierarchy |
| Bulk Operations | 2 | Bulk assign, bulk status update |

---

## 7. Entity-Type Breakdown

### Summary: What Each Entity Type Needs from the Platform

| Capability | Private Limited | OPC | LLP |
|------------|-----------------|-----|-----|
| **Incorporation** | 7-step (SPICe+ A&B) | 7-step (SPICe+ with INC-3) | 6-step (FiLLiP) |
| **Cap Table** | Full (shareholders, transfers, certificates) | Full (1 member) | N/A (partner ratios in agreement) |
| **ESOP** | Full (plans, grants, vesting, exercise) | Possible but rare | N/A |
| **Fundraising** | Full (rounds, instruments, closing room) | Limited (conversion triggers) | N/A (capital via agreement amendment) |
| **Board Meetings** | Mandatory quarterly + AGM | Not required | N/A |
| **Statutory Registers** | Members, Directors, Shares, Transfers, Charges | Same (1 member, 1 director) | N/A |
| **Compliance Tasks** | 18+/year | 4/year | 4/year |
| **ROC Filings** | AOC-4, MGT-7, ADT-1, DIR-3 KYC | AOC-4, MGT-7A, DIR-3 KYC | Form 11, Form 8, DIR-3 KYC |
| **Tax** | ITR-6, TDS quarterly, advance tax, GST | ITR-6, GST (if applicable) | ITR-5, GST (if applicable) |
| **Data Room** | Full | Full | Full |
| **Documents/Templates** | Full library | Subset (no fundraising docs unless converting) | LLP-specific templates |
| **Valuations** | NAV, DCF (for ESOP/fundraising) | Rare | N/A |
| **Accounting Integration** | Full | Full | Full |
| **Services Marketplace** | Full catalog (50+ services) | Subset | Subset |
| **Investor Portal** | Full | Limited | N/A |
| **CA Portal Usage** | Heavy (18+ annual tasks) | Light (4 tasks) | Light (4 tasks) |
| **CS Involvement** | Heavy (incorporation + annual filings) | Moderate | Moderate (different forms) |

### Platform Value by Entity Type

| Entity | Primary Value | Secondary Value | Platform Stickiness |
|--------|--------------|-----------------|---------------------|
| **Pvt Ltd** | Compliance automation (18+ tasks, Rs 1L+ penalty exposure) | Equity management, fundraising | Very High — board meetings, AGM, TDS, advance tax create recurring dependency |
| **OPC** | Simplified incorporation + basic compliance | Growth path guidance (when to convert to Pvt Ltd) | Moderate — only 4 annual tasks, less ongoing engagement |
| **LLP** | Cost-effective incorporation + partner management | LLP Agreement management, Form 11/8 compliance | Moderate — simpler compliance, but agreement amendments are complex |

---

## 8. Gap Analysis

### 8.1 What's Fully Built and Works

| Component | Status | Notes |
|-----------|--------|-------|
| Founder dashboard (all modules) | Production-ready | 17 major workflows, 68 pages |
| CA Portal | Production-ready | 7 pages, 18 endpoints, professional UX |
| Admin Portal | Production-ready | 18 pages, 30+ endpoints |
| Investor Portal (token-based) | Production-ready | 3 pages, 10+ endpoints |
| Incorporation workflows (Pvt Ltd, OPC, LLP) | Built | Entity-specific routing and forms |
| Compliance engine | Built | Entity-specific rule database, auto-generation |
| Cap table + ESOP + Fundraising | Built | Full equity management suite |
| Meetings + Registers | Built | Board/shareholder meeting workflow |
| Data Room | Built | Folder/file/share-link management |
| Services catalog | Built | 50+ services with pricing |
| AI Copilot | Built | 5 AI agents, context-aware chat |
| Notifications | Built | Email, SMS, in-app |

### 8.2 What's Infrastructure-Only (Backend Built, No Frontend)

| Component | Backend Status | Frontend Status | Priority |
|-----------|---------------|-----------------|----------|
| **CS Portal** | Full infrastructure (role, task mapping, auto-assignment, escalation) | No pages exist | High — CS is critical for incorporation fulfillment |
| **Auditor Portal** | Role not defined | No pages | Low — Phase 2+ |

### 8.3 What's Missing Entirely

| Gap | Impact | Entity Types Affected |
|-----|--------|----------------------|
| LLP partner management (cap table equivalent) | LLPs can't manage partner ratios in-platform | LLP |
| LLP Agreement amendment workflow | Partner changes require manual process | LLP |
| OPC → Pvt Ltd conversion automation | Users must manually handle mandatory conversion | OPC |
| OPC nominee change workflow | INC-3 filing not automated | OPC |
| Mobile app | No native mobile experience | All |
| Accounting integration sync UI (beyond connect/disconnect) | Limited financial visibility | All |

### 8.4 Persona Coverage Score

| Persona | Pages | Endpoints | Workflow Coverage | Score |
|---------|-------|-----------|-------------------|-------|
| **Founder (Pvt Ltd)** | 68 | ~200 | Complete | 95% |
| **Founder (OPC)** | 68 (shared) | ~200 | Most modules work, some irrelevant | 80% |
| **Founder (LLP)** | 68 (shared) | ~200 | Cap table/ESOP/meetings don't apply | 65% |
| **CA** | 7 | 18 | Complete for tax/compliance | 90% |
| **CS** | 0 | 25+ (internal) | Backend only, no portal | 30% |
| **Investor** | 3 + marketing | 10+ | Token-based portfolio + discovery | 85% |
| **Admin** | 18 | 30+ | Full ops management | 90% |

### 8.5 Key Observations

1. **Pvt Ltd is the strongest use case.** The platform was designed around Pvt Ltd workflows — cap table, ESOP, fundraising, board meetings, AGM, comprehensive compliance. This entity type uses 95%+ of platform features.

2. **LLP is underserved.** Major modules (cap table, ESOP, fundraising, meetings) don't apply. The LLP-specific value is limited to incorporation + 4 annual compliance tasks + accounting. Consider building LLP-specific features: partner ratio management, profit-sharing agreements, LLP Agreement amendment workflow.

3. **OPC is a growth path.** OPC founders will eventually convert to Pvt Ltd (mandatory if exceeding caps). The platform should guide this conversion and make it seamless. Current gap: no automated OPC → Pvt Ltd conversion flow.

4. **CA Portal is the most complete professional portal.** 7 pages, 18 endpoints, professional UX — ready for onboarding. Key differentiator from competitors who don't offer CA-facing tools.

5. **CS Portal needs frontend urgently.** The entire incorporation fulfillment relies on CS task execution, but CSs have no interface. This is the biggest operational gap — CS staff currently need direct API access or admin portal workarounds.

6. **Investor Portal is lean but effective.** Token-based access is a strong differentiator — investors don't need accounts. The discovery feature (browsing fundraising companies) creates network effects.
