# Product Features

Complete feature inventory of the Anvils platform, organized by module.

---

## 1. Company Incorporation

### Entity Type Recommender (AI Wizard)
- 5-question AI-guided wizard to recommend the best entity type
- Questions cover: solo vs team, funding intent, expected revenue, non-profit status, foreign involvement
- Recommends from 7 entity types with reasoning
- LLM-enhanced decision tree with fallback to deterministic logic

### Incorporation Pipeline
Full lifecycle tracking across 25 statuses:

```
DRAFT → ENTITY_SELECTED → PAYMENT_PENDING → PAYMENT_COMPLETED
→ DOCUMENTS_PENDING → DOCUMENTS_UPLOADED → DOCUMENTS_VERIFIED
→ NAME_PENDING → NAME_RESERVED (or NAME_REJECTED)
→ DSC_IN_PROGRESS → DSC_OBTAINED
→ FILING_DRAFTED → FILING_UNDER_REVIEW → FILING_SUBMITTED → MCA_PROCESSING
→ MCA_QUERY (loop back if ROC raises questions)
→ INCORPORATED
→ BANK_ACCOUNT_PENDING → BANK_ACCOUNT_OPENED
→ INC20A_PENDING → FULLY_SETUP
```

### Entity-Specific Workflows
- **Private Limited**: SPICe+ (INC-32) Part A/B, RUN name reservation, DIN application, integrated PAN/TAN/GST/EPFO/ESIC
- **OPC**: Nominee director declaration (INC-3), consent form, conversion threshold monitoring (Rs 2 Cr / Rs 50 Lakh)
- **LLP**: FiLLiP form, DPIN application, RUN-LLP, LLP Agreement drafting (13 sections), Form 3
- **Section 8**: INC-12 license application, income projection, name suffix enforcement, Regional Director mapping (31 states)
- **Sole Proprietorship**: GST registration-first flow, Udyam/MSME registration, Shop & Establishment Act guidance (state-wise)
- **Partnership**: Partnership deed drafting, ROF registration (state-wise), PAN application
- **Public Limited**: Modified SPICe+ (7 shareholders, 3 directors minimum), secretarial audit, CS compliance

### DSC (Digital Signature Certificate)
- Procurement tracking and status management
- Support for signing, combo, foreign signing, and foreign combo DSC types
- 1-3 year validity options
- USB token procurement

### Document Collection
- Upload with OCR extraction (AI-powered via LLM vision)
- Supported documents: Aadhaar, PAN, Passport, Utility Bill, Bank Statement, Photo, Pitch Deck
- AI verification with confidence scoring
- Cross-document validation (name/DOB consistency)
- Admin verification queue with approve/reject workflow

### Pricing Calculator
- Dynamic pricing by entity type, state, plan tier, and authorized capital
- Transparent breakdown: platform fee + government fee + stamp duty + DSC
- State-wise stamp duty for all 28 states and UTs
- Government fee slabs based on authorized capital
- State optimization tips (cheapest state for incorporation)

---

## 2. Cap Table Management

- Shareholder registry with name, email, PAN, shares, share type (equity/preference), face value
- Promoter classification
- Real-time ownership percentage calculation
- Share transaction history (allotments, transfers, buybacks)
- Dilution preview for proposed transactions
- Round simulation (model future funding rounds)
- Exit simulation (model exit scenarios)
- Scenario saving for comparison
- Cap table export
- StakeholderProfile linking for cross-company portfolio views

---

## 3. ESOP (Employee Stock Option Plans)

### Plan Management
- Create plans with pool size, exercise price, effective/expiry dates
- Exercise price basis: face value, FMV, or custom
- Default vesting schedules: monthly, quarterly, or annually
- Configurable cliff period (e.g., 12 months)
- Plan statuses: Draft → Board Approved → Shareholder Approved → Active → Frozen → Terminated
- Board and shareholder resolution tracking with document links
- DPIIT recognition support (Section 80-IAC tax deferral for 5 years)

### Grant Management
- Issue grants with customizable vesting per grant
- Grant statuses: Draft → Offered → Accepted → Active → Partially Exercised → Fully Exercised → Lapsed → Cancelled
- Grantee details: name, email, employee ID, designation
- Exercise tracking (options exercised, options lapsed)
- Grant letter generation
- E-signature integration for grant acceptance
- Pool utilization summary

---

## 4. Fundraising

### Funding Rounds
- Round types: Seed, Series A, B, C, etc.
- Instrument types: Equity, CCPS, CCD, SAFE, Convertible Note
- Pre-money and post-money valuation tracking
- Price per share calculation
- Target amount and amount raised tracking
- ESOP pool expansion percentage
- Valuation cap and discount rate (SAFE/convertible)
- Interest rate and maturity months (convertible notes)
- Round statuses: Draft → Term Sheet → Due Diligence → Documentation → Closing → Closed

### Investor Management
- Add investors with type classification: angel, VC, institutional, strategic
- Track: commitment, funds received, documents signed, shares issued
- Per-investor investment amount and shares allotted
- Linked to shareholder records post-allotment
- Conversion tracking for SAFE/CCD/Note instruments

### Closing Room
- Link term sheet, SHA, and SSA documents
- Initiate e-signature process for all parties
- Track signing status across all signatories
- Complete share allotment post-closing

### Deal Sharing
- Founders share specific deals with selected investors
- Investors receive access via their portal
- Share message from founder included
- Revocable access (founder can revoke at any time)
- Trust-based privacy model

---

## 5. Compliance Engine & Calendar

### Automated Task Generation
- Compliance tasks auto-generated based on:
  - Entity type
  - State of incorporation
  - Incorporation date
  - Financial year end
  - GST/TDS applicability
  - Employee count
- Task statuses: Upcoming, Due Soon (30 days), Overdue, In Progress, Completed, Not Applicable

### Task Categories
- Post-incorporation (one-time): INC-20A, bank account, first board meeting, auditor appointment, GST registration
- Annual ROC filings: AOC-4, MGT-7, DIR-3 KYC, ADT-1, Form 8/11 (LLP)
- GST: GSTR-1, GSTR-3B (monthly), GSTR-9 (annual)
- TDS: Quarterly returns (Q1-Q4), Form 16
- Income Tax: ITR filing, quarterly advance tax
- Board meetings: Quarterly (gap < 120 days), AGM
- Labor: EPFO monthly, ESIC monthly, Professional Tax, Labor Welfare Fund
- FEMA/RBI: FC-GPR (within 30 days of allotment), FLA Return (annual)

### Compliance Scoring
- Health score calculation based on task completion rates
- Penalty exposure estimation
- Overdue task tracking with urgency levels

### Background Automation
- 15-minute interval compliance check runner
- Automated status transitions (upcoming → due soon → overdue)
- Email/SMS reminder system (30/15/7/3/1 day schedule)
- SLA tracking and escalation

---

## 6. Legal Documents & Templates

### Template-Based Generation
- 50+ legal document templates tiered by entity type
- Modular clause library with customization
- AI-powered business objects and clause generation
- Template categories: shareholder agreements, employment agreements, service agreements, fundraising documents

### Document Workflow
- Draft creation with template selection
- Clause configuration (select/deselect modular clauses)
- Party management (add signatories)
- AI-assisted content generation
- Preview before finalization
- Send for e-signature directly from draft

---

## 7. E-Signatures

### Signature Request System
- Multi-party signing support
- Signing order: parallel or sequential
- Signatory access via secure token (no login required)
- Signature types: drawn, typed, uploaded
- Optional OTP verification per signatory

### Tracking & Audit
- Request statuses: Draft → Sent → Partially Signed → Completed → Cancelled → Expired
- Per-signatory status: Pending → Email Sent → Viewed → Signed → Declined
- Full audit log: IP address, user agent, timestamp for every action
- Reminder system with configurable intervals
- Certificate generation for completed signatures

---

## 8. Data Room

### Folder Management
- Hierarchical folder structure with parent/child relationships
- Pre-built folder types: Incorporation, Compliance, Financials, Agreements, Cap Table, Board Meetings, IP, HR, Tax, Custom
- Sort order customization

### File Management
- Version tracking (linked to previous versions)
- File metadata: filename, size, MIME type, description, tags
- Archive functionality
- Upload tracking (who uploaded, when)

### Sharing & Access Control
- Token-based secure share links
- Optional password protection
- Expiry dates on share links
- Download limits (max downloads per link)
- Granular access control (folder-level, file-level)
- Access logging with IP and user agent

### Data Retention
- Retention categories: Permanent, 8 Years (books of accounts), 6 Years (tax), 3 Years (DPDP), Custom
- Automatic retention_until calculation
- Archive and purge workflows

---

## 9. AI Copilot

### Context-Aware Assistant
- Real-time company data integration:
  - Compliance status and upcoming deadlines
  - Cap table summary and ownership percentages
  - Funding round status (ongoing/closed)
  - ESOP plan utilization
  - Director and DSC status
  - Pending actions based on company status
- Page-aware responses (knows which dashboard page the user is on)
- Proactive suggestions with priority and category
- Conversation history support

### Capabilities
- Regulatory requirement explanations
- Compliance risk alerts
- Pending action identification
- Feature guidance and navigation help
- Investment round milestone tracking
- Document drafting guidance

### Rate Limiting
- 20 messages per 60 seconds per user
- Dual LLM provider support (OpenAI gpt-4o-mini / Google Gemini 1.5 Flash)
- Automatic provider fallback

---

## 10. Support Chatbot

- FAQ-based knowledge base for common questions
- Entity-type specific content
- Company context awareness (knows entity type, current status)
- Keyword-based search matching
- Suggested questions feature
- Separate from AI Copilot (rule-based, lower cost)

---

## 11. Investor Portal

### Token-Based Access (No Login Required)
- Secure token link: `/investor/[token]`
- Portfolio overview across companies
- Share holdings and percentages
- Company financials (if shared)
- Data room documents (if shared)
- ESOP grants (if applicable)
- Funding round information (if shared)

### Authenticated Investor Access
- Full login to main dashboard
- Read-only modules: Overview, Cap Table, ESOP, Stakeholders, Fundraising, Data Room
- Multi-company portfolio view

### Deal Discovery
- Shared deals appear based on explicit founder sharing
- Express interest in companies and deals
- Message from founder included with shared deals

---

## 12. CA Portal

### Dedicated Dashboard
- Overview with stats, compliance scores, and penalty exposure
- Assigned companies list with status indicators
- Cross-company task aggregation

### Compliance Management
- Full compliance calendar (April-March financial year)
- Task management with status updates and notes
- Filing completion tracking
- Audit pack preparation and export

### Tax & TDS
- Tax filing tracker (ITR, TDS quarterly, advance tax, GST returns)
- TDS calculator with section-wise rates and due dates
- GST dashboard

---

## 13. Services Marketplace

- 50+ add-on services across 6 categories:
  - **Registration**: GST, MSME, Trademark, IEC, FSSAI, DPIIT, PT, ESI, EPFO, ISO
  - **Compliance**: Annual ROC filing, LLP filing, DIR-3 KYC, ADT-1, INC-20A
  - **Tax**: ITR filing, GST returns, TDS returns, statutory audit
  - **Accounting**: Monthly bookkeeping (basic/standard), payroll processing
  - **Amendments**: Director changes, share transfer/allotment, capital increase, office change, name change, company closure, LLP partner changes
  - **Legal**: Trademark objection, legal notice drafting, virtual registered office
- Transparent pricing: platform fee + government fee per service
- Order tracking and fulfillment status
- Razorpay payment integration

---

## 14. Finance Modules

### GST Management
- Return tracking: GSTR-1, GSTR-3B, GSTR-9
- Deadline management with reminders
- Filing status dashboard

### Tax Management
- Income tax return tracking
- Advance tax quarterly tracking
- TDS calculation engine with section-wise rates (194A, 194C, 194J, etc.)
- TDS quarterly return due dates

### Accounting Integration
- **Zoho Books**: OAuth2 connection, token refresh, organization selection, invoice/bill sync
- **Tally Prime**: XML HTTP API connection, company mapping
- Connection status tracking (connected/disconnected/error)

---

## 15. Board Meetings & Statutory Registers

### Meeting Management
- Meeting types: Board Meeting, AGM, EGM, Committee Meeting (Audit, Nomination, CSR)
- Meeting workflow: Scheduled → Notice Sent → In Progress → Minutes Draft → Minutes Signed → Completed
- Agenda items with presenter assignment
- Attendance tracking with quorum verification
- Resolution tracking (ordinary/special) with voting
- Virtual meeting support (link generation)
- Notice and minutes generation

### Statutory Registers
- Register of Members (shareholders)
- Register of Directors
- Register of Charges
- Register of Contracts
- Minute Book (board decisions)
- Stock Transfer Register

---

## 16. Notifications

### Multi-Channel Delivery
- In-app notifications with bell icon and unread count
- Email (SendGrid) with branded HTML templates
- SMS (Twilio) with DLT-compliant templates
- WhatsApp (Twilio) with template messages

### Notification Types
- Status updates (company status changes)
- Document requests
- Payment confirmations
- Compliance reminders (30/15/7/3/1 day schedule)
- Task assignments
- Escalation alerts
- Admin messages

### User Preferences
- Per-channel toggle (email, SMS, WhatsApp, in-app)
- Category preferences (status updates, payment alerts, compliance reminders, marketing)

---

## 17. Admin Portal

### Pipeline Management
- Company list with filters (status, entity type, assigned agent, priority, date range)
- Kanban board view for visual pipeline tracking
- Company assignment to staff members
- Priority flagging (Normal, Urgent, VIP)
- Company detail view with 6 tabs: Overview, Documents, Tasks, Notes, Communication, Payments

### Team Management
- Staff invitation and role assignment
- 7 roles: Super Admin, Admin, CS Lead, CA Lead, Filing Coordinator, Customer Success, User
- Staff seniority levels: Junior, Mid, Senior, Lead, Head

### SLA Tracking
- SLA targets per status transition
- Breach detection and alerts
- Compliance metrics (% on time, avg processing time)
- Escalation workflows

### Analytics
- Pipeline funnel (signup → wizard → payment → incorporated)
- Revenue dashboard (payments received, pending, refunds)
- Entity-wise and state-wise distribution
- Customer communication (in-context messaging, internal notes)
- Audit logging for all admin actions

---

## 18. Valuations

- Fair Market Value (FMV) calculations per Rule 11UA
- Valuation methods: DCF, Comparable Company, Asset-Based, Revenue Multiple
- SAFE post-money valuation support
- Valuation report generation with timestamps
- Used for: tax reporting, ESOP exercise pricing, investment decisions

---

## 19. Team & Membership

### Company Members
- Invite members via email with token-based acceptance
- Roles: Owner, Director (DIN required), Shareholder, Company Secretary, Auditor, Advisor, Viewer
- Invitation statuses: Pending, Accepted, Declined, Revoked
- Optional DIN and designation fields for directors
- Personal invite messages
- Member management (update role, remove)

---

## 20. Platform Features (Free with Every Account)

These features are available to all authenticated users regardless of subscription plan:

- Cap Table Management
- ESOP Management
- Fundraising Tools
- Compliance Calendar
- Valuations (Rule 11UA & DCF)
- Stakeholder Management
- Board Meetings
- Legal Documents & E-Sign
- Data Room
- GST & Tax Dashboard
- Accounting Integration (Zoho Books & Tally)
- Statutory Registers
