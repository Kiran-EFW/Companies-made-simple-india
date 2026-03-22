# Technical Architecture

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.1.6 | React framework (SSR/SSG) |
| React | 19.2.3 | UI library |
| TypeScript | 5.9.3 | Type safety |
| Tailwind CSS | v4 | Styling |
| Zustand | 5.0.0 | State management |
| Recharts | 3.8.0 | Charts and data visualization |
| Lucide React | 0.577.0 | Icon library |
| Jest | 29.7.0 | Testing framework |
| React Testing Library | 16.1.0 | Component testing |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.128.8 | Python web framework (async) |
| Python | 3.9+ | Backend language |
| SQLAlchemy | 2.0.48 | ORM |
| Pydantic | 2.12.5 | Data validation |
| Alembic | 1.16.5 | Database migrations |
| Celery | 5.4.0 | Distributed task queue |
| Redis | 5.2.1 | Cache, message broker |
| Uvicorn | 0.39.0 | ASGI server |
| PyJWT | 2.12.0 | Authentication tokens |
| bcrypt | 4.0.1 | Password hashing |

### Third-Party Integrations
| Service | Library/SDK | Purpose |
|---------|------------|---------|
| Razorpay | razorpay 1.4.2 | Payment processing |
| SendGrid | sendgrid 6.11.0 | Transactional email |
| Twilio | twilio 9.4.2 | SMS and WhatsApp |
| OpenAI | openai 2.26.0 | LLM (gpt-4o-mini) |
| Google Gemini | google-generativeai | LLM (gemini-1.5-flash) |
| Instructor | instructor 1.14.5 | Structured LLM output |
| Sentry | sentry-sdk 2.54.0 | Error tracking |
| WeasyPrint | weasyprint 62.3 | PDF generation |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Google Cloud Platform (GCP)                │
│              Region: asia-south1 (Mumbai)                   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Frontend   │  │  Admin Portal│  │  Investor    │     │
│  │   Next.js    │  │  Next.js     │  │  Portal      │     │
│  │   Port 3000  │  │  Port 3001   │  │  (Token)     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         └──────────────────┴─────────────────┘              │
│                           │                                 │
│                           ▼                                 │
│         ┌────────────────────────────────┐                  │
│         │  Backend API (FastAPI)         │                  │
│         │  Port 8000                     │                  │
│         │  35+ API routers @ /api/v1     │                  │
│         └───────────┬────────────────────┘                  │
│                     │                                       │
│           ┌─────────┴──────────┐                            │
│           ▼                    ▼                             │
│     ┌──────────┐        ┌───────────┐                       │
│     │ Cloud SQL│        │Memorystore│                       │
│     │ PG 18   │        │ Redis 7   │                       │
│     │ cms_india│        │ 1GB Basic │                       │
│     └──────────┘        └─────┬─────┘                       │
│                               │                             │
│                    ┌──────────┴──────────┐                  │
│                    ▼                     ▼                   │
│              ┌──────────┐         ┌──────────┐              │
│              │  Celery  │         │  Celery  │              │
│              │  Worker  │         │  Beat    │              │
│              └──────────┘         └──────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

External Services:
├── Razorpay (payments)
├── SendGrid (email)
├── Twilio (SMS/WhatsApp)
├── OpenAI / Google Gemini (AI/LLM)
└── Zoho Books / Tally Prime (accounting)
```

### Three Frontend Applications

| App | Location | Port | Audience |
|-----|----------|------|----------|
| Main Platform | `/frontend` | 3000 | Founders, CAs, Investors (authenticated) |
| Admin Portal | `/admin-portal` | 3001 | Internal operations team |
| Investor Portal | `/frontend` (routes) | 3000 | External investors (token-based, no login) |

### Backend API

- Single FastAPI application serving all frontends
- RESTful structure: `/api/v1/*`
- Stateless design (horizontally scalable)
- JWT-based authentication (24-hour tokens)
- 37 API router modules

---

## Infrastructure (GCP)

### Compute — Cloud Run (Serverless Containers)

| Service | CPU | Memory | Min/Max Instances |
|---------|-----|--------|-------------------|
| Backend API | 2 | 1Gi | 1/10 |
| Frontend | 1 | 512Mi | 0/10 |
| Admin Portal | 1 | 512Mi | 0/5 |
| Celery Worker | 2 | 1Gi | 1/5 |
| Celery Beat | 1 | 512Mi | 1/1 |

### Database — Cloud SQL
- **Engine**: PostgreSQL 18
- **Instance**: `cms-india`
- **Machine**: `db-perf-optimized-N-8`
- **Database**: `cms_india`
- **Connection**: Unix domain socket via VPC connector

### Cache — Memorystore
- **Engine**: Redis 7
- **Size**: 1GB Basic tier
- **Uses**: Celery broker (db 1), cache (db 0), rate limiting

### Networking
- **VPC Connector**: `cms-india-connector` (CIDR: 10.8.0.0/28)
- **Purpose**: Secure Cloud Run → Cloud SQL / Memorystore connectivity

### Container Registry
- **Artifact Registry**: `cms-india` (Docker format, asia-south1)

---

## Database Schema

### 35+ Data Models

**Core Entities:**
- `User` — Platform users (founders, CAs, admins)
- `Company` — Companies being incorporated/managed
- `Director` — Company directors with DSC tracking
- `Shareholder` — Cap table shareholders
- `Stakeholder` / `StakeholderProfile` — Generic stakeholder relationships, cross-company profiles
- `CompanyMember` — Team members with roles and invitations

**Equity Management:**
- `ESOPPlan` — Employee stock option plans
- `ESOPGrant` — Individual ESOP grants
- `FundingRound` — Investment rounds
- `RoundInvestor` — Investors per funding round
- `Valuation` — FMV calculations (Rule 11UA)
- `ConversionEvent` — SAFE/CCD/Note conversion tracking

**Compliance & Governance:**
- `ComplianceTask` — Regulatory compliance deadlines
- `FilingTask` — MCA filing tasks
- `Meeting` — Board meetings, AGM, EGM
- `StatutoryRegister` — Company registers

**Documents & Signatures:**
- `Document` — Uploaded/generated documents
- `LegalTemplate` — Document templates
- `ESignDocument` / `ESignRequest` / `ESignSignatory` — E-signature system
- `DataRoomFolder` / `DataRoomFile` / `DataRoomShareLink` — Data room

**Payments & Billing:**
- `Payment` — Razorpay payment records
- `ServiceCatalog` / `ServiceRequest` — Services marketplace
- `Invoice` — Generated invoices

**Operations:**
- `CAAssignment` — CA/CS assignments to companies
- `AdminLog` — Admin action audit trail
- `InternalNote` — Staff-only notes
- `Notification` / `NotificationPreference` — Notification system
- `Message` — Admin-founder messaging
- `DealShare` — Deal sharing with investors
- `InvestorInterest` — Investor interest tracking
- `AccountingConnection` — Zoho/Tally connections

---

## API Structure

Base URL: `/api/v1`

### Core Routers (37 modules)

| Router | Endpoints | Purpose |
|--------|-----------|---------|
| `/auth` | Login, signup, token | Authentication |
| `/companies` | CRUD, status | Company management |
| `/payments` | Orders, verification | Razorpay integration |
| `/pricing` | Calculator, plans | Dynamic pricing |
| `/compliance` | Calendar, tasks, TDS | Compliance engine |
| `/cap-table` | Shareholders, transfers | Cap table management |
| `/esop` | Plans, grants, exercise | ESOP management |
| `/fundraising` | Rounds, investors, closing | Fundraising module |
| `/valuations` | FMV calculations | Valuations |
| `/esign` | Requests, signing | E-signatures |
| `/documents` | Upload, verification | Document management |
| `/legal-docs` | Templates, drafts | Legal documents |
| `/data-room` | Folders, files, sharing | Data room |
| `/meetings` | Board, AGM, minutes | Meeting management |
| `/statutory-registers` | Company registers | Statutory registers |
| `/accounting` | Zoho, Tally | Accounting integration |
| `/services` | Catalog, requests | Services marketplace |
| `/stakeholders` | Profiles, linking | Stakeholder management |
| `/company-members` | Invite, accept, manage | Team management |
| `/ca-portal` | Dashboard, tasks, tax | CA portal |
| `/copilot` | Chat, suggestions | AI assistant |
| `/investor-portal` | Portfolio, companies | Investor portal |
| `/chatbot` | Chat, suggestions | Support chatbot |
| `/notifications` | List, preferences | Notifications |
| `/messages` | Send, receive | Admin messaging |
| `/admin` | Pipeline, analytics, SLA | Admin operations |
| `/wizard` | Entity recommendation | Incorporation wizard |

---

## Security

### Authentication
- Email + password signup/login
- Password hashing: bcrypt
- JWT tokens: HS256 algorithm, 24-hour expiration
- Bearer token in `Authorization` header
- User status check (is_active) on every request

### Role-Based Access Control (RBAC)
- 7 platform roles: user, admin, super_admin, cs_lead, ca_lead, filing_coordinator, customer_success
- Company-scoped access (users only see their own companies)
- Dashboard sidebar filtered by role
- Token-based investor access (no login required)

### Security Middleware
1. **CORS** — Whitelist: localhost:3000, frontend Cloud Run URL, admin Cloud Run URL
2. **Security Headers** — X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection
3. **Rate Limiting** — 120 requests/minute per IP (sliding window)
4. **PII Masking** — Automatic detection and masking in logs
5. **Request Logging** — Structured JSON logging with duration measurement

### Secrets Management
- Production: GCP Secret Manager for all API keys and credentials
- Development: `.env` file with local defaults
- Keys managed: DATABASE_URL, SECRET_KEY, Razorpay, SendGrid, Twilio, OpenAI, Gemini

---

## CI/CD Pipeline

### Cloud Build Triggers (Path-Filtered)

| Trigger | Config | Filter | Deploys |
|---------|--------|--------|---------|
| Backend | `backend/cloudbuild.yaml` | `backend/**` | API + Worker + Beat |
| Frontend | `frontend/cloudbuild.yaml` | `frontend/**` | Frontend |
| Admin | `admin-portal/cloudbuild.yaml` | `admin-portal/**` | Admin Portal |

### Deployment Workflow
1. Push to `main` branch
2. Cloud Build detects path changes
3. Relevant trigger fires
4. Docker container built and pushed to Artifact Registry
5. Cloud Run service deployed with new image
6. Health checks verify deployment

---

## Background Jobs (Celery)

### Configuration
- Broker: Redis (database 1)
- Result backend: Redis
- Serializer: JSON
- Timezone: Asia/Kolkata
- Task timeout: 5 minutes (hard), 4 minutes (soft)
- Max tasks per worker: 100

### Scheduled Tasks (Celery Beat)
- **Compliance reminders**: Every 15 minutes — check for due-soon tasks, send reminders, update statuses
- **Escalation checks**: Every 15 minutes — detect SLA breaches, escalate, notify admins
- **Document expiration**: Periodic — mark expired e-signature links, archive old documents

### Async Tasks
- Email sending (non-blocking dispatch with retry)
- PDF generation (document conversion)
- Accounting data sync (Zoho/Tally)

---

## Monitoring & Observability

| Tool | Purpose |
|------|---------|
| GCP Cloud Logging | Structured JSON logs from backend |
| Sentry | Real-time error tracking (frontend + backend) |
| Flower | Celery task monitoring (port 5555) |
| GCP Cloud Monitoring | Custom dashboards, alert policies |

---

## Local Development

### Docker Compose Stack
- PostgreSQL 15
- Redis 7
- Backend (FastAPI, port 8000)
- Celery Worker + Beat
- Flower (port 5555)
- Frontend (Next.js, port 3000)

### Development Fallbacks
- Database: SQLite or PostgreSQL (configurable)
- LLM: Console logging fallback (no API key required)
- Email: Console logging
- SMS: Console logging
- Payments: Mock mode (auto-approved)
