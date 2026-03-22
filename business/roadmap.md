# Product Roadmap

> Last updated: March 2026
> Overall progress: ~85% complete

---

## Phase Overview

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 1 | Foundation Completion | Complete | 100% |
| 2 | Real AI Integration | Complete | 100% |
| 3 | Full Incorporation Workflows | Complete | 100% |
| 4 | Notifications & Communication | Complete (core) | 85% |
| 5 | Admin & Operations Dashboard | Complete (core) | 85% |
| 6 | Post-Incorporation Services | Complete | 90% |
| 7 | Compliance Autopilot Engine | Complete (core) | 80% |
| 8 | Expanded Entity Types | Complete (core) | 80% |
| 9 | Infrastructure & DevOps | Complete (core) | 75% |
| 10 | Ecosystem & Scale | Complete (core) | 70% |

---

## Phase 1: Foundation Completion (100%)

**Goal**: Core MVP — complete incorporation flow with real payments.

**What was built:**
- Core platform: auth, JWT, user management
- Landing page with entity cards and trust signals
- Entity selection wizard (5-question AI-guided)
- Dynamic pricing calculator (28 states, 7 entity types, 3 tiers)
- Multi-step onboarding flow (names, directors, payment)
- Dashboard with real-time pipeline tracking (25 statuses)
- Document upload with OCR processing
- Admin document verification queue
- Razorpay payment integration
- Chatbot with FAQ knowledge base
- Error handling and form validation
- User profile management
- Basic email notifications via SendGrid

---

## Phase 2: Real AI Integration (100%)

**Goal**: Replace all simulated AI with real LLM and Vision AI calls.

**What was built:**
- **LLM Service Abstraction** — Unified service supporting OpenAI (gpt-4o-mini) and Google Gemini (1.5 Flash) with automatic fallback. Methods: `chat()`, `chat_with_history()`, `structured_output()`, `vision_extract()`
- **Document Parser** — Real LLM vision extraction for PAN, Aadhaar, Passport, Utility Bill. Confidence scoring (0.0-1.0). Cross-document validation
- **Name Validator** — ~50 MCA prohibited words, Soundex phonetic similarity, LLM-based deep validation
- **Legal Document Service** — MOA/AOA templates (Table F for PLC, OPC, Section 8, LLP). LLM-powered business objects generation
- **MCA Form Service** — SPICe+ (INC-32), FiLLiP, RUN/RUN-LLP, INC-9, DIR-2, INC-22 auto-fill. Business rule validation, ROC jurisdiction mapping
- **Entity Advisor Enhancement** — Decision tree with LLM enhancement. Partnership, Public Limited, family business, IPO planning paths

---

## Phase 3: Full Incorporation Workflows (100%)

**Goal**: Entity-specific incorporation flows for all supported types.

**What was built:**
- **Private Limited**: SPICe+ workflow, DIN application, name reservation, integrated PAN/TAN/GST
- **OPC**: Nominee declaration (INC-3), consent form, conversion threshold monitoring
- **LLP**: FiLLiP form, DPIN application, LLP Agreement drafting (13 sections), Form 3
- **Section 8**: INC-12 license application, income projection, name suffix enforcement, Regional Director mapping
- **Sole Proprietorship**: GST registration-first flow, Udyam/MSME, Shop Act guidance (31 states)
- **DSC Service**: Procurement, status checking, verification, document signing
- **Workflow UI**: Visual stepper with progress bar, expandable descriptions, "Trigger Next Step"

---

## Phase 4: Notifications & Communication (85%)

**Goal**: Full notification infrastructure — email, SMS, WhatsApp, in-app.

**What was built:**
- Notification model (6 types, 4 channels)
- Notification service with send/read/preferences
- Email templates (Jinja2-based branded HTML): welcome, payment, status update, compliance reminder
- Notification bell with unread badge (30s polling)
- Full notification pages with filter tabs and preferences

**Remaining:**
- Real SMS via Twilio + DLT registration (India-specific)
- Real WhatsApp Business API
- WebSocket/SSE real-time delivery (currently polling)
- Async queue (Redis/Pub/Sub) for notification dispatch
- Channel escalation logic (email → SMS → WhatsApp)

---

## Phase 5: Admin & Operations Dashboard (85%)

**Goal**: Full backend operations portal.

**What was built:**
- RBAC with 7 platform roles
- Admin models: AdminLog (audit), InternalNote, CompanyPriority
- SLA service with breach detection and metrics
- Admin router: pipeline management, team management, analytics, messaging, notes
- Admin Dashboard: metric cards, pipeline kanban, recent activity, SLA breaches
- Company detail view (6 tabs: Overview, Documents, Tasks, Notes, Communication, Payments)
- Team management and analytics pages

**Remaining:**
- MCA interaction management (query tracking, rejection workflow)
- MOA/AOA review interface with track changes
- Real-time Slack integration for SLA breach escalation

---

## Phase 6: Post-Incorporation Services (90%)

**Goal**: Services that kick in after Certificate of Incorporation.

**What was built:**
- Entity-specific post-incorporation checklists with computed deadlines
- INC-20A auto-drafting and 180-day deadline tracker
- GST REG-01 auto-fill with HSN/SAC recommendations
- Board meeting agenda templates (first meeting: 10 items, regular: 5)
- Board resolution templates (7 types)
- Minutes of meeting template generation
- ADT-1 auditor appointment form
- Deadline checking with urgency levels

**Remaining:**
- Partner bank APIs (ICICI, HDFC, Kotak) for bank account opening
- Real DPIIT registration API integration

---

## Phase 7: Compliance Autopilot Engine (80%)

**Goal**: Ongoing compliance management system — the core lifecycle value prop.

**What was built:**
- Compliance calendar engine with dynamic deadline calculation
- 50+ compliance task types auto-generated per entity
- Calendar UI (monthly/quarterly/yearly with color-coded urgency)
- Annual ROC filing tracking (AOC-4, MGT-7, DIR-3 KYC, ADT-1, Form 8/11)
- GST compliance module (GSTR-1, GSTR-3B, GSTR-9)
- TDS module with section-wise rate calculator and quarterly due dates
- Board meeting scheduler (quarterly gap < 120 days, AGM within 6 months of FY end)
- Compliance scoring and penalty exposure estimation
- Background task runner (15-minute intervals)

**Remaining:**
- Real Zoho Books API integration (currently connection framework only)
- Real Tally integration (XML export connector)
- MCA circular monitoring for regulatory changes
- iCal / Google Calendar export

---

## Phase 8: Expanded Entity Types (80%)

**Goal**: Full support for all 7 entity types.

**What was built:**
- Partnership firm: deed drafting, ROF registration, PAN application, partner management
- Public Limited: modified SPICe+ workflow, secretarial audit, CS compliance
- Entity wizard covers all 7 types
- Pricing engine covers all entity types with state-wise calculations

**Remaining:**
- Producer Company support
- Nidhi Company support
- Foreign Company Branch Office
- SEBI-ready documentation framework
- Multi-currency pricing support

---

## Phase 9: Infrastructure & DevOps (75%)

**Goal**: Production-ready infrastructure, security, and deployment.

**What was built:**
- PostgreSQL 18 on Cloud SQL
- Redis 7 on Memorystore
- Cloud Run deployment (backend, frontend, admin, worker, beat)
- Artifact Registry for Docker images
- Cloud Build CI/CD with path-filtered triggers
- VPC connector for secure internal networking
- Security middleware (CORS, rate limiting, PII masking, security headers)
- Sentry error tracking
- Docker Compose for local development
- Alembic database migrations

**Remaining:**
- Google Cloud Storage for document storage (currently local)
- Signed URL generation for secure document access
- Virus scanning on upload (ClamAV or Cloud DLP)
- End-to-end tests (Playwright or Cypress)
- Load testing scripts (Locust or k6)
- OWASP dependency scanning
- Custom Cloud Monitoring dashboards and alert policies

---

## Phase 10: Ecosystem & Scale (70%)

**Goal**: Growth features — fundraising tools, marketplace, analytics.

**What was built:**
- Cap table management (shareholder registry, transfers, allotments, dilution preview, round/exit simulation)
- ESOP management (plans, grants, vesting, exercise, pool tracking)
- Fundraising module (rounds, instruments, investors, closing room, deal sharing)
- Valuation module (DCF, Comparable, Asset-Based, Revenue Multiple, Rule 11UA)
- Services marketplace (50+ services, 6 categories)
- Investor portal (token-based + authenticated)
- AI copilot with live company context
- Data room with sharing, retention, and access control

**Remaining:**
- Partner perks marketplace (AWS/GCP credits, Notion, Slack startup plans)
- Business intelligence dashboard (company health score, benchmarking)
- Multi-language support (Hindi, Tamil, Bengali, Marathi, Telugu)
- White-label offering for CA/CS firms
- Public API for third-party integrations
- Bulk incorporation tools (for incubators/accelerators)
- Referral program (refer a founder, get Rs 500 credit)
- Progressive Web App (PWA) for mobile experience

---

## Phase Dependencies

```
Phase 1 ──→ Phase 2 ──→ Phase 3
   │            │            │
   │            └──→ Phase 4 ┘
   │                    │
   └──→ Phase 5 ────────┘
            │
            └──→ Phase 6 ──→ Phase 7
                                │
Phase 9 (parallel) ─────────────┘
            │
            └──→ Phase 8
                    │
                    └──→ Phase 10
```

**Critical path**: Phase 1 → 2 → 3 → 6 → 7

**Parallelizable**: Phase 4 (notifications), Phase 5 (admin), Phase 9 (infra)

---

## Next Priorities

### High Priority
1. Real accounting integration (Zoho Books OAuth, Tally XML connector)
2. Google Cloud Storage for document storage
3. Real SMS/WhatsApp via Twilio with DLT registration
4. End-to-end testing suite

### Medium Priority
5. MCA query/rejection workflow in admin portal
6. WebSocket/SSE for real-time notifications
7. Multi-language support (starting with Hindi)
8. Public API for third-party integrations

### Future
9. Producer Company and Nidhi Company entity types
10. Partner perks marketplace
11. White-label offering for CA/CS firms
12. Progressive Web App (PWA)
13. Referral program
