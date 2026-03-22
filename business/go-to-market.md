# Go-to-Market Strategy

## Customer Acquisition Channels

### 1. Organic Search (SEO)
- **Landing pages**: Entity-specific pages (`/for/founders`, `/for/investors`, `/for/cas`)
- **Feature pages**: 12 dedicated feature detail pages (`/features/*`)
- **Comparison tool**: Entity comparison page (`/compare`) — drives search traffic for "LLP vs Private Limited" queries
- **Educational content**: `/learn` section with regulatory guides
- **Pricing calculator**: Transparent, interactive pricing page attracts founders researching costs

### 2. Product-Led Growth
- **Free cap table builder**: `/cap-table-setup` — free tool that introduces founders to the platform
- **Entity recommendation wizard**: `/wizard` — AI-guided entity selection, no signup required
- **Investor portal**: Token-based access creates awareness among investors who then recommend the platform
- **E-signature access**: Public signing pages (`/sign/[token]`) expose signatories to the platform

### 3. CA/CS Channel (B2B2C)
- CAs invited by founders get the dedicated CA Portal
- CAs managing multiple clients become power users
- CAs recommend Anvils to new clients (network effect)
- CA Portal is free — the revenue comes from the founders' subscriptions and services

### 4. Investor Network
- Investors viewing portfolios via the Investor Portal see the Anvils brand
- Deal sharing feature creates direct founder-investor touchpoints on the platform
- VCs recommending portfolio companies to use Anvils for compliance and cap table

---

## Conversion Funnel

### Stage 1: Awareness
```
Landing Page → Entity Comparison → Pricing Calculator → Feature Pages
```
- Transparent pricing builds trust
- Entity comparison tool answers common "which entity type?" question
- Feature pages demonstrate depth beyond basic incorporation

### Stage 2: Consideration
```
Entity Wizard (AI recommendation) → Free Cap Table Builder → Signup
```
- Wizard provides immediate value (entity recommendation) without requiring signup
- Free cap table tool lets founders experience the product
- Low-friction signup (email + password)

### Stage 3: Conversion (Incorporation)
```
Signup → Onboarding Flow → Entity Selection → Director Details → Payment (Razorpay)
```
- Multi-step onboarding with clear progress indicators
- Dynamic pricing shown before payment (no surprises)
- Razorpay checkout for seamless payment

### Stage 4: Activation (Post-Payment)
```
Payment → Document Upload → AI Verification → Admin Verification
→ Name Reservation → DSC → MCA Filing → Incorporation
→ Post-Incorporation Setup (INC-20A, Bank, Auditor, Board Meeting)
→ FULLY_SETUP
```

25-stage pipeline with real-time tracking in the dashboard. The founder sees their company moving through stages — creating engagement and trust.

### Stage 5: Retention (Compliance Lock-In)
```
FULLY_SETUP → Compliance Calendar Auto-Generated
→ Monthly/Quarterly/Annual Compliance Tasks
→ Subscription Plans → Add-On Services
```

Once incorporated, the compliance calendar creates ongoing dependency:
- Regulatory deadlines with penalties for non-compliance
- Automated reminders ensure the founder stays engaged
- Subscription plans bundle recurring compliance services
- Services marketplace for one-off needs (amendments, registrations)

---

## Company Status Pipeline (25 Stages)

The incorporation pipeline tracks companies through 25 granular statuses:

| # | Status | Description |
|---|--------|-------------|
| 1 | DRAFT | Company created, entity type not selected |
| 2 | ENTITY_SELECTED | Entity type chosen |
| 3 | PAYMENT_PENDING | Pricing shown, awaiting payment |
| 4 | PAYMENT_COMPLETED | Razorpay payment successful |
| 5 | DOCUMENTS_PENDING | Waiting for director documents |
| 6 | DOCUMENTS_UPLOADED | Documents uploaded, awaiting verification |
| 7 | DOCUMENTS_VERIFIED | AI + admin verification passed |
| 8 | NAME_PENDING | Name reservation submitted to MCA |
| 9 | NAME_RESERVED | Name approved by MCA |
| 10 | NAME_REJECTED | Name rejected, resubmission needed |
| 11 | DSC_IN_PROGRESS | Digital Signature Certificate procurement |
| 12 | DSC_OBTAINED | DSCs procured for all directors |
| 13 | FILING_DRAFTED | MCA forms auto-filled |
| 14 | FILING_UNDER_REVIEW | Internal team review |
| 15 | FILING_SUBMITTED | Forms submitted to MCA |
| 16 | MCA_PROCESSING | MCA processing the application |
| 17 | MCA_QUERY | ROC raised a query, response needed |
| 18 | INCORPORATED | Certificate of Incorporation issued |
| 19 | BANK_ACCOUNT_PENDING | Post-incorporation, awaiting bank account |
| 20 | BANK_ACCOUNT_OPENED | Bank account opened |
| 21 | INC20A_PENDING | INC-20A form filing pending |
| 22 | FULLY_SETUP | All post-incorporation tasks complete |

---

## Upsell Strategy

### Layer 1: Free Platform Features
Every authenticated user gets access to core platform features at no additional cost:
- Cap Table, ESOP, Fundraising, Compliance Calendar, Valuations, Stakeholders, Board Meetings, Legal Docs, E-Sign, Data Room, GST/Tax Dashboard, Accounting Integration, Statutory Registers

**Purpose**: Maximize platform adoption and data lock-in.

### Layer 2: Incorporation (One-Time Revenue)
- Entry point: Rs 499 (Sole Prop) to Rs 24,999 (Public Ltd)
- 3 tiers per entity type: Launch, Grow, Scale
- Higher tiers include more services (DSC, compliance setup)

**Purpose**: Acquire the customer and capture company data.

### Layer 3: Compliance Subscription (Recurring Revenue)
- 5 plans: Starter (Rs 999/mo) → Peace of Mind (Rs 9,999/mo)
- Positioned after incorporation when compliance urgency is highest
- Compliance calendar creates urgency (penalties for missing deadlines)

**Purpose**: Convert one-time customers into recurring subscribers.

### Layer 4: Services Marketplace (Transactional Revenue)
- 50+ services across 6 categories
- Surfaced contextually (e.g., "Your GST registration is due" → "Order GST Registration" button)
- Each service purchase generates platform fee revenue

**Purpose**: Capture every compliance and regulatory need as a revenue event.

---

## Retention Mechanics

### 1. Compliance Calendar (Regulatory Lock-In)
- Auto-generated compliance tasks based on entity type
- Penalties for non-compliance (Rs 100/day, director disqualification, company strike-off)
- Reminders at 30/15/7/3/1 days before deadline
- This is not optional — it's a legal requirement

### 2. Data Gravity
- Company data (directors, shareholders, documents, cap table, funding history) accumulates over time
- Switching costs increase as more data enters the platform
- Data room becomes the single source of truth for investors and auditors

### 3. Multi-Stakeholder Dependencies
- CAs manage their clients through the platform (switching means losing their dashboard)
- Investors access portfolios through the platform (switching means losing visibility)
- Team members (directors, shareholders) are invited and linked

### 4. AI Copilot Stickiness
- Context-aware assistant learns from company data
- Proactive suggestions based on company state
- Becomes more valuable as more data enters the system

### 5. Progressive Feature Discovery
- Post-incorporation: compliance calendar surfaces
- First funding round: fundraising module surfaces
- Team growth: ESOP module surfaces
- Each lifecycle event unlocks new platform value

---

## Pricing Strategy

### Transparency as a Feature
- Every fee broken down: platform fee + government fee + stamp duty
- State-wise stamp duty calculator (founders can see which state is cheapest)
- No hidden charges — builds trust in a market where CA pricing is opaque

### Entity-Matched Pricing
- Subscription plans mapped to entity types (Starter for Sole Prop, Scale for PLC)
- Services filtered by entity type (only show relevant services)
- Government fees shown separately (Anvils doesn't mark up government fees)

### Annual Discount
- Annual plans save ~17% vs monthly billing
- Encourages upfront commitment and reduces churn
- Example: Scale plan — Rs 4,999/mo (Rs 59,988/yr) vs Rs 49,999/yr (save Rs 9,989)

---

## Key Metrics to Track

| Metric | Description |
|--------|-------------|
| Incorporation Conversion Rate | Wizard starts → Completed payment |
| Time to Incorporation | Payment → Certificate of Incorporation |
| Subscription Attach Rate | Incorporated companies → Active subscription |
| Monthly Service Revenue | Revenue from marketplace purchases |
| CA Portal Adoption | CAs invited → CAs actively using portal |
| Investor Portal Views | Token-based portal page views |
| Compliance Score Average | Platform-wide average compliance health |
| Churn Rate | Monthly subscription cancellations |
| Net Revenue Retention | Expansion revenue (upgrades + services) vs churn |
| CAC (Customer Acquisition Cost) | Marketing spend / new paying customers |
| LTV (Lifetime Value) | Average revenue per customer over lifetime |
