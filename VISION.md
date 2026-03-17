# Anvils Platform — Product Vision & Architecture

## What Anvils Is

Anvils is the equity, governance, and compliance platform for Indian companies. It serves three user types across the full company lifecycle — from incorporation to fundraising to ongoing compliance.

## Users

### Founders
Company owners who need to incorporate, manage equity, raise funds, stay compliant, and handle legal documents. They are the primary paying customer.

### CAs & CSs (Chartered Accountants / Company Secretaries)
Professional advisors invited by founders. They manage compliance calendars, file returns, track deadlines, and ensure the company stays on the right side of the law.

### Investors
Shareholders and potential investors who need visibility into their portfolio — cap table, ESOP grants, data room documents, and company financials.

---

## Revenue Model

### 1. Incorporation (One-Time)
Platform fee + government fees + stamp duty + DSC. Collected during the onboarding flow via Razorpay. Ranges from Rs 499 (Sole Prop) to Rs 24,999 (Public Limited) depending on entity type and plan tier.

### 2. Compliance Subscription (Recurring)
Monthly or annual plans for ongoing compliance management:

| Plan | Monthly | Annual | Target |
|------|---------|--------|--------|
| Starter | Rs 999 | Rs 9,999 | Sole Prop & Partnership |
| Growth | Rs 2,999 | Rs 29,999 | LLP & OPC |
| Scale | Rs 4,999 | Rs 49,999 | Private Limited |
| Enterprise | Rs 9,999 | Rs 99,999 | Public Limited & Section 8 |
| Peace of Mind | Rs 9,999 | Rs 99,999 | All entity types, full coverage |

### 3. Add-On Services (One-Time per Service)
50+ services across 6 categories — GST registration, trademark, ROC filings, statutory audit, bookkeeping, amendments, and more. Each has a platform fee and optional government fee.

---

## Platform Architecture

### Three Separate Apps

| App | URL | Audience | Purpose |
|-----|-----|----------|---------|
| Marketing + Platform | anvils.in | Public + Authenticated users | Landing pages, dashboard, features |
| Admin Portal | admin.anvils.in | Internal team | Pipeline ops, fulfillment, analytics |
| Investor Portal | anvils.in/investor/[token] | External investors | Lightweight portfolio view |

### The Admin Portal (Separate App)
Internal operations tool. Pipeline Kanban, service request fulfillment, SLA tracking, compliance oversight, revenue analytics, team management. Lives at `/admin-portal` in the codebase.

### The Investor Portal (Token-Based)
Lightweight, no-login-needed portfolio view for external investors. Lives at `/investor/[token]` routes. Separate from the main dashboard — intentionally minimal.

---

## Dashboard Architecture

### Core Principle: Company-Scoped, Role-Based

Every dashboard page is scoped to a selected company. The sidebar shows modules filtered by the user's role. One shell, multiple perspectives.

```
┌─────────────────────────────────────────────────────────┐
│  [Anvils Logo]   [Company Selector ▼]   [Bell] [Avatar] │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  SIDEBAR     │   PAGE CONTENT                           │
│              │   (scoped to selected company)           │
│  Overview    │                                          │
│              │                                          │
│  EQUITY      │                                          │
│  Cap Table   │                                          │
│  ESOP        │                                          │
│  Stakeholders│                                          │
│              │                                          │
│  FUNDRAISING │                                          │
│  Rounds      │                                          │
│  Valuations  │                                          │
│              │                                          │
│  COMPLIANCE  │                                          │
│  Calendar    │                                          │
│  Meetings    │                                          │
│  Registers   │                                          │
│              │                                          │
│  DOCUMENTS   │                                          │
│  Legal Docs  │                                          │
│  E-Signatures│                                          │
│  Data Room   │                                          │
│              │                                          │
│  FINANCE     │                                          │
│  GST         │                                          │
│  Tax         │                                          │
│  Accounting  │                                          │
│              │                                          │
│  SERVICES    │                                          │
│  Marketplace │                                          │
│  Subscription│                                          │
│  Billing     │                                          │
│              │                                          │
│  ─────────── │                                          │
│  Settings    │                                          │
│  Profile     │                                          │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Role-Based Sidebar Visibility

| Module | Founder | CA/CS | Investor |
|--------|---------|-------|----------|
| Overview | Full | Read | Read |
| Cap Table | Full | Read | Read |
| ESOP | Full | Read | Read |
| Stakeholders | Full | Read | Read |
| Fundraising | Full | -- | Read |
| Valuations | Full | Read | -- |
| Compliance Calendar | Full | Full | -- |
| Board Meetings | Full | Full | -- |
| Statutory Registers | Full | Full | -- |
| Legal Documents | Full | Read | -- |
| E-Signatures | Full | Read | -- |
| Data Room | Full | Read | Read |
| GST | Full | Full | -- |
| Tax | Full | Full | -- |
| Accounting | Full | Read | -- |
| Services Marketplace | Full | -- | -- |
| Subscription | Full | -- | -- |
| Billing | Full | -- | -- |
| Settings | Full | -- | -- |

### Entry Points

**Founder (new, incorporating):**
Landing → Pricing → Signup → Onboarding (pay) → Dashboard (pipeline view) → Incorporated → Post-setup view

**Founder (existing company):**
Landing → Signup → Dashboard → "Connect Existing Company" → Enter CIN/name → Dashboard (post-setup view)

**CA/CS:**
Invited by founder → Login → Dashboard (compliance-focused sidebar)

**Investor (external):**
Token link → /investor/[token] → Lightweight portfolio (no login needed)

**Investor (with account):**
Login → Dashboard (read-only equity + data room sidebar)

### Empty State (No Company)
Instead of redirecting to pricing, the dashboard overview shows:

- **Incorporate a New Company** — Start from scratch, we handle MCA filing
- **Connect an Existing Company** — Already incorporated? Add your CIN and start managing
- **I Was Invited** — Check for pending team invitations

### Services & Billing (Inside Dashboard)

**Subscription Management:**
- Current plan display with billing cycle
- Plan comparison scoped to company's entity type
- Upgrade/downgrade with Razorpay
- Cancel with confirmation

**Service Marketplace:**
- Browse by category (Registration, Compliance, Tax, Accounting, Amendments, Legal)
- Each service shows platform fee, government fee, total, frequency
- "Order" button → Razorpay payment → Service request created
- Active service requests with status tracking

**Billing History:**
- All payments (incorporation + subscription + services)
- Invoice download
- Receipt generation

---

## Route Structure

```
PUBLIC
/                           Homepage
/pricing                    Pricing + plans + calculator + catalog
/for/founders               Persona landing page
/for/investors              Persona landing page
/for/cas                    Persona landing page
/features/*                 Feature detail pages (12 pages)
/wizard                     Entity type recommender
/compare                    Entity comparison tool
/cap-table-setup            Free cap table builder
/learn                      Educational content
/sign/[token]               E-signature (public, token-based)
/investor/[token]           Investor portfolio (token-based)
/investor/[token]/company/* Investor company detail
/investor/[token]/discover  Investor discovery

AUTH
/login                      Login
/signup                     Signup
/onboarding                 Incorporation flow + payment

DASHBOARD (authenticated, company-scoped)
/dashboard                  Overview (adapts to state + role)
/dashboard/cap-table        Cap table management
/dashboard/esop             ESOP plans, grants, vesting
/dashboard/stakeholders     Shareholders, directors, advisors
/dashboard/fundraising      Funding rounds, closing room
/dashboard/valuations       FMV calculations (Rule 11UA)
/dashboard/compliance       Compliance calendar + deadlines
/dashboard/meetings         Board & shareholder meetings
/dashboard/registers        Statutory registers
/dashboard/documents        Legal docs, templates, AI drafting
/dashboard/signatures       E-signature tracking
/dashboard/data-room        Secure document sharing
/dashboard/gst              GST returns + deadlines
/dashboard/tax              Income tax, TDS, audit
/dashboard/accounting       Zoho Books / Tally integration
/dashboard/services         Service marketplace (company-scoped)
/dashboard/subscription     Plan selection + management
/dashboard/billing          Payment history + invoices
/dashboard/settings         Company profile, team, integrations
/dashboard/profile          User profile + password
/dashboard/notifications    Notification center + preferences
```

---

## Design Principles

1. **Company-scoped everything.** Every dashboard action happens in the context of a selected company. No ambiguity.
2. **Role-based, not app-based.** One dashboard shell, sidebar adapts to role. No separate apps for CAs or investors.
3. **No dead ends.** Empty states always offer a next action — never just "go to pricing."
4. **Payment where the intent is.** Service purchases happen inside the dashboard where the user understands the context, not on a disconnected page.
5. **Progressive disclosure.** Show what's relevant to the company's current state. Pre-incorporation sees pipeline. Post-incorporation sees features. Don't overwhelm.
6. **Clean light theme.** Professional B2B SaaS aesthetic. No glassmorphism in the dashboard.
