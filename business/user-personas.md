# User Personas & Permissions

Detailed profiles for each user type on the Anvils platform, with onboarding flows, feature access, and permission matrices.

---

## 1. Founders (Primary Paying Customers)

### Profile
- **Who**: Company owners, entrepreneurs, startup founders
- **Goal**: Incorporate, manage equity, raise funds, stay compliant, handle legal documents
- **Pain points**: Opaque CA pricing, scattered compliance deadlines, spreadsheet-based cap tables, manual fundraising coordination

### Onboarding Journey

```
Landing Page → Pricing Calculator → Signup
→ Entity Selection Wizard (AI-guided, 5 questions)
→ Onboarding Flow:
    Step 1: Proposed company names (up to 2)
    Step 2: Director details (name, DIN, PAN, Aadhaar, photo, DSC)
    Step 3: Payment (Razorpay checkout)
→ Dashboard (pipeline view — tracks incorporation progress)
→ Document Upload → AI Verification → Admin Verification
→ Name Reservation → DSC → MCA Filing → Incorporation
→ Post-Incorporation Setup (INC-20A, bank account, first board meeting, auditor)
→ Dashboard (full feature view — cap table, compliance, fundraising, etc.)
```

**Alternate path — existing companies:**
```
Signup → Dashboard → "Connect Existing Company" → Enter CIN → Full Dashboard
```

### Dashboard Modules Available
- Overview (company state & next actions)
- Cap Table (full CRUD)
- ESOP (plan creation, grants, vesting)
- Stakeholders (directors, shareholders, advisors)
- Fundraising (rounds, investors, closing room)
- Valuations (FMV calculations)
- Compliance Calendar (view, track, delegate)
- Board Meetings (create, manage, minutes)
- Statutory Registers (view, maintain)
- Legal Documents (templates, AI drafting)
- E-Signatures (initiate, track)
- Data Room (manage, share)
- GST Dashboard (returns, deadlines)
- Tax Dashboard (ITR, TDS, advance tax)
- Accounting (Zoho Books / Tally integration)
- Services Marketplace (order add-on services)
- Subscription Management (plan selection, upgrade)
- Billing (payment history, invoices)
- Settings (company info, team, integrations)
- Profile (personal info, password)
- Notifications (center + preferences)

---

## 2. Chartered Accountants & Company Secretaries

### Profile
- **Who**: Professional advisors — CAs, CSs, tax consultants
- **Goal**: Manage compliance, file returns, track deadlines across multiple client companies
- **Pain points**: Managing clients via WhatsApp/email, no unified dashboard, manual deadline tracking

### Access Model
- Invited by founders with `CA_LEAD` role
- See only companies assigned to them
- Dedicated CA Portal at `/ca` (separate from founder dashboard)

### Onboarding Journey

```
Founder invites CA via email → CA receives invitation with token
→ CA logs in (or signs up) → Accepts invitation
→ CA Portal Dashboard (shows assigned companies)
→ Cross-company compliance calendar, task list, tax tracker
```

### CA Portal Pages
- **Dashboard** (`/ca`) — Stats, compliance scores, penalty exposure
- **Tasks** (`/ca/tasks`) — Cross-company task list with filters, mark complete
- **Calendar** (`/ca/calendar`) — FY compliance calendar (April-March)
- **Tax** (`/ca/tax`) — Tax filing tracker (ITR, TDS quarterly, advance tax, GST)
- **TDS** (`/ca/tds`) — TDS calculator with section rates and due dates
- **Companies** (`/ca/companies`) — All assigned companies list
- **Company Detail** (`/ca/companies/[id]`) — Compliance, Documents, Audit Pack tabs

### CA-Specific Features
- Task notes system (add/view notes per compliance task)
- Audit pack export (documents packaged for auditors)
- Compliance score generation
- Penalty exposure estimation
- Multi-company task aggregation
- Filing completion workflow (mark tasks as filed)

---

## 3. Investors

### Profile
- **Who**: Angel investors, VCs, institutional investors, strategic partners, existing shareholders
- **Goal**: View portfolio holdings, access data rooms, discover investment opportunities
- **Pain points**: No portfolio view across companies, scattered cap table data, manual document access

### Access Models

#### A. Token-Based External Portal (No Login Required)
```
Founder shares secure link → Investor opens /investor/[token]
→ Portfolio Overview (all companies they hold shares in)
→ Company Detail (cap table, funding history, data room)
→ Deal Discovery (shared deals from founders)
```

**Features:**
- Portfolio overview with cross-company shareholdings
- Share holdings and percentages per company
- Company financials (if shared by founder)
- Data room documents (if shared)
- ESOP grants (if applicable)
- Funding round information (if shared)

#### B. Authenticated Investor Account
```
Login → Dashboard (read-only sidebar)
→ Overview, Cap Table, ESOP, Stakeholders, Fundraising, Data Room
→ Multi-company view
```

### Investor Engagement
- **Deal sharing**: Founders explicitly share deals with specific investors
- **Interest expression**: Investors can express interest in companies and deals
- **Portfolio tracking**: View holdings, ownership percentages across multiple companies
- **Document access**: Read-only access to data room files shared by founders

---

## 4. Admin / Operations Team

### Profile
- **Who**: Internal Anvils staff — CS leads, CA leads, filing coordinators, customer success managers
- **Goal**: Manage incorporation pipeline, track SLAs, fulfill service requests, monitor revenue
- **Pain points**: Manual pipeline tracking, SLA breaches, lack of visibility into operations

### Role Hierarchy

| Role | Access Level |
|------|-------------|
| Super Admin | Full access, user management, all analytics |
| Admin | Full operations access |
| CS Lead | Company pipeline, compliance oversight |
| CA Lead | Compliance management, CA portal admin |
| Filing Coordinator | Document review, MCA filing management |
| Customer Success | Customer communication, service requests |

### Seniority Levels
Junior → Mid → Senior → Lead → Head

### Admin Portal Features
- **Pipeline Kanban** — Companies moving through incorporation stages
- **Company Detail** — Full history, documents, tasks, notes, communication, payments
- **Assignment** — Assign companies to specific staff members
- **Priority Flagging** — Normal, Urgent, VIP
- **SLA Dashboard** — Breach detection, compliance metrics
- **Analytics** — Pipeline funnel, revenue dashboard, entity/state distribution
- **Team Management** — Invite staff, assign roles, track performance
- **Customer Communication** — In-context messaging with founders
- **Internal Notes** — Staff-only notes per company
- **Audit Logging** — All admin actions tracked with IP address

---

## Permission Matrix

### Dashboard Module Access by Role

| Module | Founder | CA/CS | Investor (Auth) | Investor (Token) | Admin |
|--------|---------|-------|-----------------|-------------------|-------|
| Overview | Full | Read | Read | Read | Full |
| Cap Table | Full | Read | Read | Read | View |
| ESOP | Full | Read | Read | -- | View |
| Stakeholders | Full | Read | Read | -- | View |
| Fundraising | Full | -- | Read | Read (if shared) | View |
| Valuations | Full | Read | -- | -- | View |
| Compliance Calendar | Full | Full | -- | -- | Monitor |
| Board Meetings | Full | Full | -- | -- | View |
| Statutory Registers | Full | Full | -- | -- | View |
| Legal Documents | Full | Read | -- | -- | View |
| E-Signatures | Full | Read | -- | -- | Monitor |
| Data Room | Full | Read | Read | Read (if shared) | Monitor |
| GST | Full | Full | -- | -- | Monitor |
| Tax | Full | Full | -- | -- | Monitor |
| Accounting | Full | Read | -- | -- | -- |
| Services Marketplace | Full | -- | -- | -- | Manage |
| Subscription | Full | -- | -- | -- | View |
| Billing | Full | -- | -- | -- | View |
| Settings | Full | -- | -- | -- | Full |
| Team/Members | Full | -- | -- | -- | Full |
| Notifications | Full | Full | Receive | -- | Send |

### Key Permission Rules
- **Company Scoping**: Users can only access companies they own, are invited to, or hold shares in
- **CA Access**: CAs see only companies assigned to them via `CAAssignment`
- **Investor Access**: Token-based access limited to shared data only; authenticated access is read-only
- **Admin Access**: Admins can view all companies but cannot modify founder data directly
- **Invitation Required**: No user can access a company without being the owner or receiving an invitation
