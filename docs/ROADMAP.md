# Companies Made Simple India — 10-Phase Roadmap

> Last updated: 2026-03-14
> Overall progress: **~35-40% complete** (Phase 1 mostly done, Phases 2-10 pending)

---

## Phase Overview

| Phase | Name | Focus | Status |
|-------|------|-------|--------|
| 1 | Foundation Completion | Finish core MVP — real payments, chatbot, fix mocks | ~78% |
| 2 | Real AI Integration | Connect Gemini/GPT-4, real OCR, real name validation | 0% |
| 3 | Full Incorporation Workflows | OPC, LLP, Section 8 entity-specific forms & flows | ~20% |
| 4 | Notifications & Communication | Email, SMS, WhatsApp, in-app notification system | 0% |
| 5 | Admin & Operations Dashboard | Full ops dashboard, team roles, SLA tracking | ~15% |
| 6 | Post-Incorporation Services | Bank account, INC-20A, DPIIT, GST registration | ~5% |
| 7 | Compliance Autopilot Engine | Calendar, smart reminders, auto-draft filings | 0% |
| 8 | Expanded Entity Types & Workflows | Partnership, Public Ltd, Producer Co, Nidhi Co, Foreign Branch | 0% |
| 9 | Infrastructure & DevOps | PostgreSQL, Redis, GCS, Cloud Run, CI/CD, monitoring | ~10% |
| 10 | Ecosystem & Scale | Cap table, fundraising, marketplace, analytics | 0% |

---

## Phase 1: Foundation Completion (~78% done)

**Goal**: Finish the core MVP so a user can go through a complete (still simulated) incorporation flow with real payments.

### What's Done
- [x] Core platform (auth, JWT, user management)
- [x] Landing page with entity cards and trust signals
- [x] Entity selection wizard (5-question AI-guided)
- [x] Dynamic pricing calculator (31 states, 5 entity types, 3 tiers)
- [x] Multi-step onboarding flow (names, directors, payment)
- [x] Dashboard with real-time pipeline tracking (16 statuses)
- [x] Live agent terminal logs (polls every 2s)
- [x] Document upload and simulated OCR processing
- [x] Admin document verification queue
- [x] Process orchestrator (state machine triggering agents in sequence)
- [x] Database models (Users, Companies, Directors, Documents, Tasks, AgentLogs)

### What's Remaining
- [ ] **1.1** Razorpay payment integration (replace mock payment endpoint)
  - [ ] 1.1.1 Create Razorpay account, get API keys
  - [ ] 1.1.2 Backend: Razorpay order creation endpoint
  - [ ] 1.1.3 Backend: Payment verification webhook
  - [ ] 1.1.4 Frontend: Razorpay checkout.js integration in onboarding step 3
  - [ ] 1.1.5 Payment receipt generation and storage
  - [ ] 1.1.6 Refund handling endpoint
- [ ] **1.2** Basic chatbot agent
  - [ ] 1.2.1 RAG knowledge base: Indian company law FAQ, incorporation process, entity comparison
  - [ ] 1.2.2 Backend: Chatbot API endpoint with conversation history
  - [ ] 1.2.3 Frontend: Chat widget component (floating bottom-right)
  - [ ] 1.2.4 Context-aware responses (knows user's company status)
- [ ] **1.3** Error handling & edge cases
  - [ ] 1.3.1 Global error boundary in frontend
  - [ ] 1.3.2 API error response standardization
  - [ ] 1.3.3 Form validation improvements (PAN format, Aadhaar checksum, phone validation)
  - [ ] 1.3.4 Session expiry handling (JWT refresh or re-login flow)
- [ ] **1.4** User profile management
  - [ ] 1.4.1 Profile edit page (name, phone, email, password change)
  - [ ] 1.4.2 Email verification flow
  - [ ] 1.4.3 Phone OTP verification
- [ ] **1.5** Basic email notifications
  - [ ] 1.5.1 Welcome email on signup
  - [ ] 1.5.2 Payment confirmation email
  - [ ] 1.5.3 Status change emails (name approved, incorporated, etc.)

---

## Phase 2: Real AI Integration (0% done)

**Goal**: Replace all simulated/mock AI with real LLM and Vision AI calls.

- [ ] **2.1** LLM integration (Gemini / GPT-4)
  - [ ] 2.1.1 API key management (env vars, key rotation)
  - [ ] 2.1.2 LLM service abstraction layer (swap between Gemini/OpenAI)
  - [ ] 2.1.3 Prompt engineering for entity recommendation (replace hardcoded decision tree)
  - [ ] 2.1.4 Structured output parsing with `instructor` library
  - [ ] 2.1.5 Token usage tracking and cost monitoring
  - [ ] 2.1.6 Rate limiting and fallback handling
- [ ] **2.2** Real Document OCR (Google Vision AI)
  - [ ] 2.2.1 Google Cloud Vision API setup
  - [ ] 2.2.2 PAN card OCR extraction (name, PAN number, DOB, father's name)
  - [ ] 2.2.3 Aadhaar card OCR extraction (name, Aadhaar number, address, DOB)
  - [ ] 2.2.4 Passport OCR extraction
  - [ ] 2.2.5 Utility bill / bank statement address extraction
  - [ ] 2.2.6 Photo quality validation (face detection, resolution check)
  - [ ] 2.2.7 Cross-document validation (name match PAN ↔ Aadhaar, address consistency)
  - [ ] 2.2.8 Confidence scoring and human review threshold
- [ ] **2.3** Real name availability checking
  - [ ] 2.3.1 MCA company name search scraper/API integration
  - [ ] 2.3.2 Trademark database (IP India) search integration
  - [ ] 2.3.3 Phonetic similarity engine (Soundex/Metaphone for Hindi + English)
  - [ ] 2.3.4 Name suggestion generator using LLM
  - [ ] 2.3.5 Prohibited/undesirable name database
- [ ] **2.4** Real MOA/AOA generation
  - [ ] 2.4.1 Legal template library (Table F for Pvt Ltd, Table I for LLP Agreement)
  - [ ] 2.4.2 LLM-driven business objects clause generation
  - [ ] 2.4.3 Custom clause insertion based on user preferences
  - [ ] 2.4.4 PDF generation with proper legal formatting
- [ ] **2.5** AI form auto-fill for MCA e-forms
  - [ ] 2.5.1 SPICe+ (INC-32) XML/PDF form population
  - [ ] 2.5.2 FiLLiP form population (for LLP)
  - [ ] 2.5.3 RUN / RUN-LLP name reservation form
  - [ ] 2.5.4 INC-9, DIR-2, INC-22 declaration forms
  - [ ] 2.5.5 Form validation against MCA business rules

---

## Phase 3: Full Incorporation Workflows (~20% done)

**Goal**: Complete entity-specific incorporation flows for all Tier 1 + Section 8 entities.

### What's Done
- [x] Private Limited Company basic flow (simulated end-to-end)
- [x] Database supports OPC, LLP, Section 8 entity types
- [x] Pricing engine covers all Tier 1 + Section 8

### What's Remaining
- [ ] **3.1** Private Limited Company — complete workflow
  - [ ] 3.1.1 DSC procurement integration (Class 2/3 DSC vendor API)
  - [ ] 3.1.2 DIN application (DIR-3) auto-fill and tracking
  - [ ] 3.1.3 RUN name reservation form auto-fill + MCA submission
  - [ ] 3.1.4 SPICe+ Part A (name) + Part B (incorporation) split workflow
  - [ ] 3.1.5 Integrated PAN/TAN/GST/EPFO/ESIC application within SPICe+
  - [ ] 3.1.6 MCA fee calculator (capital-based slab)
  - [ ] 3.1.7 Stamp duty e-payment integration (state-wise)
  - [ ] 3.1.8 Digital signature workflow (DSC-based signing of forms)
  - [ ] 3.1.9 MCA V3 portal submission tracking
  - [ ] 3.1.10 MCA query/rejection response workflow
- [ ] **3.2** One Person Company (OPC) — full workflow
  - [ ] 3.2.1 Nominee director declaration (INC-3) generation
  - [ ] 3.2.2 Nominee consent form generation
  - [ ] 3.2.3 Single director onboarding flow (UI simplification)
  - [ ] 3.2.4 OPC-specific MOA/AOA templates
  - [ ] 3.2.5 Conversion threshold monitoring (₹2 Cr turnover / ₹50 Lakh capital)
  - [ ] 3.2.6 Auto-alert when approaching conversion threshold
- [ ] **3.3** LLP — full workflow
  - [ ] 3.3.1 FiLLiP form auto-fill + submission
  - [ ] 3.3.2 DPIN (Designated Partner Identification Number) application
  - [ ] 3.3.3 RUN-LLP name reservation
  - [ ] 3.3.4 LLP Agreement drafting (AI + legal templates)
  - [ ] 3.3.5 Capital contribution vs profit sharing ratio configuration
  - [ ] 3.3.6 Designated partner vs partner role management in UI
  - [ ] 3.3.7 Form 3 (LLP Agreement filing with ROC)
- [ ] **3.4** Section 8 Company — full workflow
  - [ ] 3.4.1 INC-12 license application drafting
  - [ ] 3.4.2 Projected income/expenditure statement for 3 years
  - [ ] 3.4.3 Declaration of directors (no salary/dividend clauses)
  - [ ] 3.4.4 Section 8 specific MOA (non-profit objects, no dividend distribution)
  - [ ] 3.4.5 Regional Director license tracking
  - [ ] 3.4.6 Post-license SPICe+ filing workflow
  - [ ] 3.4.7 Name requirements enforcement ("Foundation"/"Association"/"Forum" suffix)
- [ ] **3.5** Sole Proprietorship — basic workflow
  - [ ] 3.5.1 GST registration as primary incorporation step
  - [ ] 3.5.2 MSME/Udyam registration integration
  - [ ] 3.5.3 Shop & Establishment Act registration guidance (state-wise)
  - [ ] 3.5.4 Simplified onboarding (single person, no directors flow)

---

## Phase 4: Notifications & Communication (0% done)

**Goal**: Build the full notification infrastructure — email, SMS, WhatsApp, in-app.

- [ ] **4.1** Email system (SendGrid)
  - [ ] 4.1.1 SendGrid account setup and API integration
  - [ ] 4.1.2 Email template system (branded HTML templates)
  - [ ] 4.1.3 Transactional emails: signup, payment, status changes, document requests
  - [ ] 4.1.4 Compliance reminder emails (30/15/7/3/1 day schedule)
  - [ ] 4.1.5 Email delivery tracking (open rates, bounce handling)
  - [ ] 4.1.6 Unsubscribe management
- [ ] **4.2** SMS system (Twilio)
  - [ ] 4.2.1 Twilio account setup, DLT registration (India-specific)
  - [ ] 4.2.2 OTP verification for phone numbers
  - [ ] 4.2.3 Status update SMS (incorporation complete, filing due, etc.)
  - [ ] 4.2.4 SMS template approval (DLT compliance)
- [ ] **4.3** WhatsApp Business API
  - [ ] 4.3.1 WhatsApp Business API setup (Meta Business Manager)
  - [ ] 4.3.2 Template messages (status updates, reminders)
  - [ ] 4.3.3 Interactive messages (quick replies, buttons)
  - [ ] 4.3.4 Document sharing via WhatsApp (COI, PAN card)
  - [ ] 4.3.5 WhatsApp chatbot integration (connect to AI chatbot agent)
- [ ] **4.4** In-app notification system
  - [ ] 4.4.1 Notification model in database (type, read/unread, action URL)
  - [ ] 4.4.2 Backend: WebSocket or SSE for real-time notifications
  - [ ] 4.4.3 Frontend: Notification bell with unread count
  - [ ] 4.4.4 Notification preferences page (per channel: email/SMS/WhatsApp/in-app)
- [ ] **4.5** Notification queue & orchestration
  - [ ] 4.5.1 Cloud Pub/Sub or Redis queue for async notification dispatch
  - [ ] 4.5.2 Notification scheduler (cron-based for compliance reminders)
  - [ ] 4.5.3 Channel priority logic (escalate: email → SMS → WhatsApp → phone call)
  - [ ] 4.5.4 Notification logging and audit trail

---

## Phase 5: Admin & Operations Dashboard (~15% done)

**Goal**: Build the full backend operations portal for CS/CA teams.

### What's Done
- [x] Basic document verification queue (approve/reject)
- [x] AI extraction display with confidence scores

### What's Remaining
- [ ] **5.1** Role-based access control
  - [ ] 5.1.1 Admin roles: Super Admin, Head of Ops, CS Lead, CA Lead, Filing Coordinator, Customer Success
  - [ ] 5.1.2 Permission matrix (who can approve what)
  - [ ] 5.1.3 Admin user management (invite, deactivate, role assignment)
  - [ ] 5.1.4 Audit log for all admin actions
- [ ] **5.2** Incorporation pipeline management
  - [ ] 5.2.1 Kanban board view (companies moving through stages)
  - [ ] 5.2.2 Assign company to specific CS/CA team member
  - [ ] 5.2.3 Priority flagging (urgent, VIP, escalation)
  - [ ] 5.2.4 Company detail view with full history timeline
  - [ ] 5.2.5 Document review interface (side-by-side: original doc + AI extraction)
  - [ ] 5.2.6 MOA/AOA review and edit interface (inline editing with track changes)
  - [ ] 5.2.7 Form review interface (SPICe+, FiLLiP fields with override capability)
- [ ] **5.3** SLA tracking and alerts
  - [ ] 5.3.1 SLA timer per company per stage (based on Phase 3.4 SLA table)
  - [ ] 5.3.2 SLA breach alerts (Slack/email to team lead)
  - [ ] 5.3.3 Dashboard: SLA compliance metrics (% on time, avg processing time)
  - [ ] 5.3.4 Escalation workflow (auto-escalate to Head of Ops on SLA breach)
- [ ] **5.4** MCA interaction management
  - [ ] 5.4.1 MCA query tracking (ROC/RD queries with response deadlines)
  - [ ] 5.4.2 Rejection handling workflow (reason parsing, corrective action, re-filing)
  - [ ] 5.4.3 Name resubmission management
  - [ ] 5.4.4 Government liaison notes and communication log
- [ ] **5.5** Customer communication from admin
  - [ ] 5.5.1 In-context messaging (admin sends message to customer from company view)
  - [ ] 5.5.2 Document request workflow (request specific doc from customer)
  - [ ] 5.5.3 Phone/video call scheduling (Calendly or custom)
  - [ ] 5.5.4 Internal notes (visible only to team, not to customer)
- [ ] **5.6** Reporting and analytics
  - [ ] 5.6.1 Daily/weekly incorporation summary (filed, approved, rejected)
  - [ ] 5.6.2 Revenue dashboard (payments received, pending, refunds)
  - [ ] 5.6.3 Agent performance (AI accuracy rates, human override rates)
  - [ ] 5.6.4 Customer pipeline funnel (signup → wizard → payment → incorporated)
  - [ ] 5.6.5 State-wise and entity-wise breakdown charts

---

## Phase 6: Post-Incorporation Services (~5% done)

**Goal**: Build the services that kick in after COI is issued.

### What's Done
- [x] Post-incorporation section in dashboard (placeholder cards)
- [x] Bank links (Mercury, ICICI, HDFC) shown after incorporation

### What's Remaining
- [ ] **6.1** Bank account opening integration
  - [ ] 6.1.1 Partner bank APIs (ICICI, HDFC, Kotak — startup banking programs)
  - [ ] 6.1.2 Pre-fill bank application from company data (CIN, PAN, directors)
  - [ ] 6.1.3 Document package for bank (COI, MOA, AOA, board resolution)
  - [ ] 6.1.4 Bank account status tracking in dashboard
  - [ ] 6.1.5 Mercury / Razorpay X integration for digital-first banking
- [ ] **6.2** INC-20A (Commencement of Business)
  - [ ] 6.2.1 Auto-draft INC-20A form
  - [ ] 6.2.2 Bank account verification (proof of subscription money receipt)
  - [ ] 6.2.3 180-day deadline tracker with escalating reminders
  - [ ] 6.2.4 Filing submission and tracking
- [ ] **6.3** DPIIT Startup India registration
  - [ ] 6.3.1 Eligibility checker (< 10 years old, < ₹100 Cr turnover, innovation test)
  - [ ] 6.3.2 Auto-fill DPIIT application form
  - [ ] 6.3.3 Innovation description generation (LLM-assisted)
  - [ ] 6.3.4 DPIIT certificate tracking
  - [ ] 6.3.5 Benefits guide (tax exemption, self-certification, IPR fast-track)
- [ ] **6.4** GST registration
  - [ ] 6.4.1 GST REG-01 form auto-fill
  - [ ] 6.4.2 HSN/SAC code recommendation based on business description
  - [ ] 6.4.3 Principal place of business documentation
  - [ ] 6.4.4 Authorized signatory setup
  - [ ] 6.4.5 GST certificate tracking and download
- [ ] **6.5** First board meeting setup
  - [ ] 6.5.1 Board meeting agenda template (first meeting: allotment of shares, appoint auditor, registered office, common seal)
  - [ ] 6.5.2 Board resolution templates (10+ standard resolutions)
  - [ ] 6.5.3 Minutes of meeting template and generation
  - [ ] 6.5.4 Virtual meeting scheduling (Zoom/Google Meet link generation)
- [ ] **6.6** Auditor appointment
  - [ ] 6.6.1 Auditor panel (CA firms in our network)
  - [ ] 6.6.2 ADT-1 form auto-fill and filing
  - [ ] 6.6.3 Auditor consent letter (Form ADT-1 attachment)
  - [ ] 6.6.4 30-day deadline tracker from incorporation

---

## Phase 7: Compliance Autopilot Engine (0% done)

**Goal**: Build the ongoing compliance management system — the core lifecycle value prop.

- [ ] **7.1** Compliance calendar engine
  - [ ] 7.1.1 Master compliance rule database (entity type → list of obligations with deadlines)
  - [ ] 7.1.2 Dynamic deadline calculator (financial year end, incorporation date, AGM date)
  - [ ] 7.1.3 Calendar UI (monthly/quarterly/yearly view with color-coded urgency)
  - [ ] 7.1.4 Upcoming deadlines widget on dashboard
  - [ ] 7.1.5 iCal / Google Calendar export
- [ ] **7.2** Annual ROC filings auto-draft
  - [ ] 7.2.1 AOC-4 (financial statements) auto-draft from accounting data
  - [ ] 7.2.2 MGT-7 (annual return) auto-draft from company profile
  - [ ] 7.2.3 MGT-7A (simplified annual return for small companies)
  - [ ] 7.2.4 DIR-3 KYC auto-fill for all directors annually
  - [ ] 7.2.5 ADT-1 (auditor reappointment) tracker
  - [ ] 7.2.6 Form 11 (LLP annual return) auto-draft
  - [ ] 7.2.7 Form 8 (LLP Statement of Accounts) auto-draft
- [ ] **7.3** GST compliance module
  - [ ] 7.3.1 Invoice data import (manual upload, or Zoho/Tally integration)
  - [ ] 7.3.2 GSTR-1 (outward supplies) auto-population
  - [ ] 7.3.3 GSTR-3B (summary return) auto-population
  - [ ] 7.3.4 GST reconciliation (GSTR-2A/2B matching)
  - [ ] 7.3.5 GST payment challan generation
  - [ ] 7.3.6 GSTR-9 (annual return) preparation
- [ ] **7.4** TDS compliance module
  - [ ] 7.4.1 TDS rate calculator (section-wise: 194A, 194C, 194J, etc.)
  - [ ] 7.4.2 TDS challan generation (Form 26QB, etc.)
  - [ ] 7.4.3 Quarterly TDS return preparation (Form 24Q, 26Q, 27Q)
  - [ ] 7.4.4 Form 16/16A generation
  - [ ] 7.4.5 TDS payment reminder with due dates
- [ ] **7.5** Board meeting and AGM support
  - [ ] 7.5.1 Quarterly board meeting scheduler (4 per year, gap < 120 days)
  - [ ] 7.5.2 AGM scheduler (within 6 months of FY end)
  - [ ] 7.5.3 Agenda generator (context-aware: what resolutions are due)
  - [ ] 7.5.4 Minutes template with AI pre-fill
  - [ ] 7.5.5 Resolution tracker (ordinary vs special)
  - [ ] 7.5.6 MGT-15 (filing of resolutions with ROC)
- [ ] **7.6** Risk monitoring and alerts
  - [ ] 7.6.1 Compliance gap detection (missed filings, overdue KYC)
  - [ ] 7.6.2 Penalty calculator (late filing fees as per MCA schedule)
  - [ ] 7.6.3 Regulatory change monitor (MCA circulars, notifications)
  - [ ] 7.6.4 Director disqualification risk alert (DIN deactivation warning)
  - [ ] 7.6.5 Strike-off risk alert (2 consecutive years of non-filing)
- [ ] **7.7** Accounting software integrations
  - [ ] 7.7.1 Zoho Books API integration (fetch trial balance, P&L, balance sheet)
  - [ ] 7.7.2 Tally integration (via Tally XML export or TDL connector)
  - [ ] 7.7.3 Manual financial data upload (Excel/CSV)
  - [ ] 7.7.4 Data mapping to MCA form fields

---

## Phase 8: Expanded Entity Types & Workflows (0% done)

**Goal**: Add Tier 2 and Tier 3 entity types.

- [ ] **8.1** Partnership Firm
  - [ ] 8.1.1 Partnership deed drafting (AI + templates)
  - [ ] 8.1.2 Registration with Registrar of Firms (state-wise)
  - [ ] 8.1.3 PAN application for partnership
  - [ ] 8.1.4 Partner management (add/remove/retire)
- [ ] **8.2** Public Limited Company
  - [ ] 8.2.1 Modified SPICe+ workflow (min 7 shareholders, 3 directors)
  - [ ] 8.2.2 Prospectus/Statement in lieu of prospectus
  - [ ] 8.2.3 Higher compliance requirements (additional filings, stricter timelines)
  - [ ] 8.2.4 SEBI-ready documentation framework
- [ ] **8.3** Producer Company
  - [ ] 8.3.1 Producer eligibility verification (5+ producers or 2+ institutions)
  - [ ] 8.3.2 Producer-specific MOA (objects limited to production, harvesting, procurement)
  - [ ] 8.3.3 Limited return of surplus mechanism
  - [ ] 8.3.4 Rural-friendly onboarding (simplified UI, regional language support)
- [ ] **8.4** Nidhi Company
  - [ ] 8.4.1 Minimum 200 members verification
  - [ ] 8.4.2 NDH-4 (Nidhi declaration) form
  - [ ] 8.4.3 Net-owned funds compliance tracking
  - [ ] 8.4.4 Deposit-lending ratio monitoring
- [ ] **8.5** Foreign Company Branch Office
  - [ ] 8.5.1 RBI approval workflow (FC-GPR, FC-TRS)
  - [ ] 8.5.2 Liaison/Branch/Project Office differentiation
  - [ ] 8.5.3 FEMA compliance tracking
  - [ ] 8.5.4 Annual Activity Certificate filing
  - [ ] 8.5.5 Multi-currency pricing support
- [ ] **8.6** Entity wizard expansion
  - [ ] 8.6.1 Update wizard to cover all 10 entity types
  - [ ] 8.6.2 Add 2 more questions (foreign involvement detail, member count)
  - [ ] 8.6.3 Comparison table UI (all entities side-by-side)

---

## Phase 9: Infrastructure & DevOps (~10% done)

**Goal**: Production-ready infrastructure, security, and deployment.

### What's Done
- [x] SQLAlchemy models (PostgreSQL-compatible)
- [x] Environment variable support (.env)

### What's Remaining
- [ ] **9.1** Database migration to PostgreSQL
  - [ ] 9.1.1 Set up Cloud SQL (PostgreSQL) instance
  - [ ] 9.1.2 Alembic migration setup and initial migration scripts
  - [ ] 9.1.3 Data migration from SQLite to PostgreSQL
  - [ ] 9.1.4 Connection pooling configuration
  - [ ] 9.1.5 Database backup automation (daily snapshots)
- [ ] **9.2** Redis caching layer
  - [ ] 9.2.1 Redis instance setup (Cloud Memorystore)
  - [ ] 9.2.2 Session caching
  - [ ] 9.2.3 Pricing calculation caching (invalidate on config change)
  - [ ] 9.2.4 Rate limiting implementation
  - [ ] 9.2.5 Agent task queue (replace threading with Redis-based queue)
- [ ] **9.3** Document storage (Google Cloud Storage)
  - [ ] 9.3.1 GCS bucket setup with encryption (CMEK)
  - [ ] 9.3.2 Migrate local file storage to GCS
  - [ ] 9.3.3 Signed URL generation for secure document access
  - [ ] 9.3.4 Document retention policy (7 years for legal docs)
  - [ ] 9.3.5 Virus scanning on upload (ClamAV or Cloud DLP)
- [ ] **9.4** Cloud deployment
  - [ ] 9.4.1 Dockerize backend (FastAPI) and frontend (Next.js)
  - [ ] 9.4.2 Cloud Run service deployment (backend)
  - [ ] 9.4.3 Cloud Run or Vercel deployment (frontend)
  - [ ] 9.4.4 Custom domain setup + SSL (companies-made-simple.in)
  - [ ] 9.4.5 Cloud CDN for static assets
  - [ ] 9.4.6 Load testing and auto-scaling configuration
- [ ] **9.5** CI/CD pipeline
  - [ ] 9.5.1 GitHub Actions: lint + type check on PR
  - [ ] 9.5.2 GitHub Actions: run tests on PR
  - [ ] 9.5.3 Cloud Build: auto-deploy to staging on merge to `develop`
  - [ ] 9.5.4 Cloud Build: deploy to production on merge to `main` (with approval)
  - [ ] 9.5.5 Database migration in CI pipeline
- [ ] **9.6** Security hardening
  - [ ] 9.6.1 Move JWT secret to Secret Manager
  - [ ] 9.6.2 API rate limiting (per user, per IP)
  - [ ] 9.6.3 CORS configuration for production domains
  - [ ] 9.6.4 Input sanitization audit (SQL injection, XSS prevention)
  - [ ] 9.6.5 OWASP dependency scanning
  - [ ] 9.6.6 Data encryption at rest and in transit
  - [ ] 9.6.7 PII data handling compliance (Aadhaar masking, PAN masking in logs)
- [ ] **9.7** Monitoring and observability
  - [ ] 9.7.1 Cloud Logging setup (structured logs from FastAPI)
  - [ ] 9.7.2 Sentry integration (error tracking, frontend + backend)
  - [ ] 9.7.3 Uptime monitoring (Cloud Monitoring or Better Uptime)
  - [ ] 9.7.4 Application performance monitoring (request latency, DB query times)
  - [ ] 9.7.5 Custom dashboards (GCP Cloud Monitoring)
  - [ ] 9.7.6 Alert policies (error rate > 5%, latency > 2s, downtime)
- [ ] **9.8** Testing infrastructure
  - [ ] 9.8.1 Backend: pytest test suite (unit + integration tests)
  - [ ] 9.8.2 Frontend: Jest + React Testing Library
  - [ ] 9.8.3 End-to-end tests (Playwright or Cypress)
  - [ ] 9.8.4 API contract tests
  - [ ] 9.8.5 Load testing scripts (Locust or k6)

---

## Phase 10: Ecosystem & Scale (0% done)

**Goal**: Build the growth features — fundraising tools, marketplace, analytics, PWA.

- [ ] **10.1** Cap table management
  - [ ] 10.1.1 Shareholder registry (names, shares, % holding)
  - [ ] 10.1.2 Share transfer tracking (SH-4 form auto-generation)
  - [ ] 10.1.3 Share allotment workflow (PAS-3 return of allotment)
  - [ ] 10.1.4 ESOP pool management
  - [ ] 10.1.5 Cap table visualization (pie chart, waterfall)
- [ ] **10.2** Fundraising tools
  - [ ] 10.2.1 Term sheet templates (equity, SAFE, convertible note)
  - [ ] 10.2.2 Valuation calculator (DCF, comparable, revenue multiple)
  - [ ] 10.2.3 Investment agreement drafting (SHA, SSA)
  - [ ] 10.2.4 PAS-3, MGT-14 filings for share allotment post-fundraise
  - [ ] 10.2.5 Investor data room (secure document sharing)
- [ ] **10.3** Partner perks marketplace
  - [ ] 10.3.1 AWS / GCP / Azure startup credits integration
  - [ ] 10.3.2 Notion, Slack, Figma startup plans
  - [ ] 10.3.3 Legal, accounting, HR partner directory
  - [ ] 10.3.4 Insurance partner integration (D&O, key person, health)
  - [ ] 10.3.5 Co-working space partnerships
- [ ] **10.4** Business intelligence dashboard
  - [ ] 10.4.1 Company health score (compliance status, filing status, financials)
  - [ ] 10.4.2 Benchmarking against similar companies
  - [ ] 10.4.3 Growth metrics tracking (revenue, users, burn rate)
  - [ ] 10.4.4 AI-generated business insights
- [ ] **10.5** Advanced platform features
  - [ ] 10.5.1 Multi-language support (Hindi, Tamil, Bengali, Marathi, Telugu)
  - [ ] 10.5.2 White-label offering for CA/CS firms
  - [ ] 10.5.3 API access for third-party integrations
  - [ ] 10.5.4 Bulk incorporation tools (for incubators/accelerators)
  - [ ] 10.5.5 Referral program (refer a founder, get ₹500 credit)
  - [ ] 10.5.6 Progressive Web App (PWA) for mobile-like experience

---

## Dependencies Between Phases

```
Phase 1 ──→ Phase 2 ──→ Phase 3
   │            │            │
   │            └──→ Phase 4 ┘
   │                    │
   └──→ Phase 5 ────────┘
            │
            └──→ Phase 6 ──→ Phase 7
                                │
Phase 9 (can run parallel) ─────┘
            │
            └──→ Phase 8
                    │
                    └──→ Phase 10
```

**Critical path**: Phase 1 → Phase 2 → Phase 3 → Phase 6 → Phase 7

**Can be parallelized**:
- Phase 4 (notifications) can start alongside Phase 2
- Phase 5 (admin) can start alongside Phase 3
- Phase 9 (infra) should start early and run continuously
- Phase 8 (expanded entities) depends on Phase 3 patterns being established
- Phase 10 (ecosystem) depends on core platform stability
