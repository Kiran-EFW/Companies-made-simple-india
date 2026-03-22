# Financial Plan — Technology Costs, Salary Spread & Marketing Strategy

This document covers the full cost structure of running Anvils: technology infrastructure, complete salary spread across all departments, and marketing budget with channel strategy.

---

## Part 1: Technology Operations Cost

### GCP Infrastructure (Current Setup)

| Service | Spec | Monthly Estimate | Notes |
|---------|------|-----------------|-------|
| **Cloud Run — Backend API** | 2 vCPU, 1Gi, min 1 / max 10 instances | Rs 8,000 - 25,000 | Always-on (min 1). Scales with traffic |
| **Cloud Run — Celery Worker** | 2 vCPU, 1Gi, min 1 / max 5, no-cpu-throttling | Rs 8,000 - 15,000 | Always-on, continuous processing |
| **Cloud Run — Celery Beat** | 1 vCPU, 512Mi, min 1 / max 1, no-cpu-throttling | Rs 3,000 - 4,000 | Single instance, always-on |
| **Cloud Run — Frontend** | 1 vCPU, 512Mi, min 0 / max 10 | Rs 2,000 - 10,000 | Scales to zero when idle |
| **Cloud Run — Admin Portal** | 1 vCPU, 512Mi, min 0 / max 5 | Rs 1,000 - 5,000 | Low traffic, scales to zero |
| **Cloud SQL — PostgreSQL 18** | db-perf-optimized-N-8 | Rs 25,000 - 35,000 | Dedicated instance, always-on |
| **Memorystore — Redis 7** | 1GB Basic tier | Rs 5,000 - 7,000 | Always-on, fixed cost |
| **VPC Connector** | cms-india-connector | Rs 1,500 - 2,000 | Fixed networking cost |
| **Artifact Registry** | Docker images | Rs 500 - 1,000 | Storage for container images |
| **Cloud Build** | 3 triggers (backend, frontend, admin) | Rs 1,000 - 3,000 | Per-build pricing, E2_HIGHCPU_8 |
| **Secret Manager** | 2 secrets (DB password, secret key) | Rs 100 | Negligible |
| **Cloud Logging + Monitoring** | Structured logs, alerts | Rs 2,000 - 5,000 | Scales with log volume |
| **GCS (planned)** | Document storage bucket | Rs 1,000 - 5,000 | When document storage moves to cloud |
| **Cloud CDN (planned)** | Static asset caching | Rs 1,000 - 3,000 | When CDN is enabled |

#### GCP Total: Rs 58,000 - 1,20,000/month (~Rs 7 - 14 LPA)

**Cost driver**: Cloud SQL is the biggest fixed cost. The `db-perf-optimized-N-8` tier is expensive. At launch, consider downgrading to `db-f1-micro` or `db-g1-small` (Rs 3,000-8,000/month) and upgrading later.

**Optimized launch estimate (smaller DB tier)**: Rs 35,000 - 60,000/month

---

### Third-Party API Services

| Service | Provider | Pricing Model | Monthly Estimate | Notes |
|---------|----------|-------------|-----------------|-------|
| **Payment Gateway** | Razorpay | 2% per transaction (no monthly fee) | Variable | Deducted from payments, not a separate cost. At Rs 5L revenue = Rs 10,000 TDR |
| **Email** | SendGrid | Free tier: 100/day. Essentials: $19.95/mo (50K emails) | Rs 0 - 1,700 | Free tier sufficient at launch (100 emails/day) |
| **SMS** | Twilio | Rs 0.25-0.50 per SMS (India) | Rs 2,000 - 10,000 | Depends on notification volume. ~5,000-20,000 SMS/month |
| **WhatsApp** | Twilio | Rs 0.50-1.00 per message (India) | Rs 1,000 - 5,000 | Template messages for status updates |
| **LLM — OpenAI** | OpenAI | gpt-4o-mini: $0.15/1M input, $0.60/1M output | Rs 2,000 - 8,000 | Document OCR, entity wizard, copilot. ~500-2000 calls/month |
| **LLM — Google Gemini** | Google AI | gemini-1.5-flash: $0.075/1M input, $0.30/1M output | Rs 1,000 - 4,000 | Fallback provider, lower cost |
| **Error Tracking** | Sentry | Free tier: 5K events. Team: $26/mo | Rs 0 - 2,200 | Free tier sufficient at launch |
| **Domain + SSL** | Cloudflare / Registrar | ~$15/year domain | Rs 100 | Annual cost |

#### Third-Party Total: Rs 6,000 - 30,000/month (~Rs 0.7 - 3.6 LPA)

**At launch (free tiers)**: Rs 3,000 - 8,000/month

---

### Technology Cost Summary

| Phase | Companies | GCP Infra | Third-Party APIs | Total Tech/Month | Annual |
|-------|-----------|-----------|-----------------|-------------------|--------|
| Launch (0-100) | 0-100 | Rs 40,000 | Rs 5,000 | Rs 45,000 | Rs 5.4 LPA |
| Growth (100-500) | 100-500 | Rs 75,000 | Rs 15,000 | Rs 90,000 | Rs 10.8 LPA |
| Scale (500-2000) | 500-2000 | Rs 1,20,000 | Rs 30,000 | Rs 1,50,000 | Rs 18.0 LPA |

---

## Part 2: Full Salary Spread

This covers the **entire organization** — not just operations (covered in [operations-and-staffing.md](operations-and-staffing.md)) but also technology, leadership, and marketing.

### Department Breakdown

#### A. Leadership & Management

| Role | Headcount | Annual CTC | Notes |
|------|-----------|-----------|-------|
| CEO / Founder | 1 | Rs 0 - 12 LPA | Often founder-salary is deferred or minimal pre-revenue |
| COO / Operations Head | 1 | Rs 15 - 25 LPA | Owns service delivery, SLAs, ops team |
| **Subtotal** | **2** | **Rs 15 - 37 LPA** | |

#### B. Technology Team

| Role | Headcount | Annual CTC | Responsibilities |
|------|-----------|-----------|-----------------|
| CTO / Lead Engineer | 1 | Rs 20 - 40 LPA | Architecture, code reviews, infra, security. Could be a cofounder |
| Full-Stack Developer (Senior) | 1 | Rs 12 - 20 LPA | Next.js + FastAPI feature development, API design |
| Full-Stack Developer (Mid) | 1 | Rs 6 - 12 LPA | Frontend pages, backend endpoints, bug fixes |
| Full-Stack Developer (Junior) | 1 | Rs 3 - 6 LPA | UI components, testing, documentation |
| DevOps / Infra (part-time or shared) | 0.5 | Rs 4 - 8 LPA | GCP management, CI/CD, monitoring, scaling. Can be handled by CTO initially |
| **Subtotal** | **3.5 - 4.5** | **Rs 45 - 86 LPA** | |

**Launch optimization**: CTO + 1 mid-level dev can handle the workload for 0-100 companies. Hire junior + senior as you grow.

**Minimal tech team (launch)**: CTO + 1 developer = Rs 26 - 52 LPA

#### C. Operations Team (Service Delivery)

| Role | Headcount (Launch → Scale) | Annual CTC Range | Department |
|------|--------------------------|-----------------|------------|
| CS Lead | 0 → 1 | Rs 10 - 15 LPA | Company Secretary |
| Senior Company Secretary | 1 → 4 | Rs 6 - 10 LPA each | Company Secretary |
| Junior Company Secretary | 1 → 4 | Rs 3 - 5 LPA each | Company Secretary |
| CA Lead | 0 → 1 | Rs 10 - 15 LPA | Chartered Accountant |
| Senior Chartered Accountant | 1 → 3 | Rs 6 - 10 LPA each | Chartered Accountant |
| Junior Chartered Accountant | 0 → 2 | Rs 3 - 5 LPA each | Chartered Accountant |
| Filing Lead | 0 → 1 | Rs 5 - 8 LPA | Filing & Documents |
| Document Reviewers | 1 → 3 | Rs 2.5 - 4 LPA each | Filing & Documents |
| DSC Coordinator | 0 → 1 | Rs 2.5 - 4 LPA | Filing & Documents |
| Customer Success Manager | 0 → 1 | Rs 5 - 8 LPA | Customer Success |
| Customer Success Associates | 1 → 3 | Rs 2.5 - 4 LPA each | Customer Success |
| Bookkeeper (outsourced) | Outsourced | Rs 3 - 5 LPA | Accounts |

**Ops subtotal at launch (6 people)**: Rs 30 - 46 LPA
**Ops subtotal at scale (25 people)**: Rs 1.5 - 2.5 Cr/year

(See [operations-and-staffing.md](operations-and-staffing.md) for detailed job descriptions and qualifications.)

#### D. Marketing & Growth Team

| Role | Headcount | Annual CTC | Responsibilities |
|------|-----------|-----------|-----------------|
| Head of Marketing / Growth | 1 | Rs 12 - 20 LPA | Strategy, channels, brand, CAC optimization |
| Content Writer / SEO | 1 | Rs 4 - 8 LPA | Blog posts, landing pages, educational content, entity comparison articles |
| Performance Marketing (part-time / agency) | 0.5 | Rs 3 - 6 LPA | Google Ads, Meta Ads, LinkedIn campaigns |
| Social Media / Community (part-time) | 0.5 | Rs 2 - 4 LPA | Twitter/X, LinkedIn, founder communities |
| **Subtotal** | **2 - 3** | **Rs 21 - 38 LPA** | |

**Launch optimization**: Founder handles growth + 1 content writer. Hire marketing lead once you have product-market fit.

**Minimal marketing team (launch)**: 1 content writer = Rs 4 - 8 LPA

#### E. Finance & Admin

| Role | Headcount | Annual CTC | Responsibilities |
|------|-----------|-----------|-----------------|
| Finance / Accounts (part-time) | 0.5 | Rs 2 - 4 LPA | Internal bookkeeping, payroll, GST, vendor payments |
| Office Admin (if physical office) | 0 - 1 | Rs 2 - 3 LPA | Office management, courier, supplies |
| **Subtotal** | **0.5 - 1.5** | **Rs 2 - 7 LPA** | |

---

### Total Salary Spread by Phase

#### Launch Phase (0-100 Companies)

| Department | Headcount | Annual Cost |
|-----------|-----------|-------------|
| Leadership (Founder + COO) | 2 | Rs 15 LPA (founder minimal + ops head) |
| Technology (CTO + 1 dev) | 2 | Rs 30 LPA |
| Operations (minimal team) | 6 | Rs 38 LPA |
| Marketing (1 content writer) | 1 | Rs 6 LPA |
| Finance (part-time) | 0.5 | Rs 3 LPA |
| **Total** | **~11.5** | **~Rs 92 LPA** |

Monthly burn: **~Rs 7.7 LPA/month**

#### Growth Phase (100-500 Companies)

| Department | Headcount | Annual Cost |
|-----------|-----------|-------------|
| Leadership | 2 | Rs 30 LPA |
| Technology | 4 | Rs 55 LPA |
| Operations | 15 | Rs 1.13 Cr |
| Marketing | 3 | Rs 28 LPA |
| Finance | 1 | Rs 5 LPA |
| **Total** | **~25** | **~Rs 2.3 Cr** |

Monthly burn: **~Rs 19 LPA/month**

#### Scale Phase (500-2000 Companies)

| Department | Headcount | Annual Cost |
|-----------|-----------|-------------|
| Leadership | 3 | Rs 50 LPA |
| Technology | 6 | Rs 85 LPA |
| Operations | 25 | Rs 1.94 Cr |
| Marketing | 4 | Rs 38 LPA |
| Finance | 2 | Rs 7 LPA |
| **Total** | **~40** | **~Rs 3.7 Cr** |

Monthly burn: **~Rs 31 LPA/month**

---

## Part 3: Complete Cost Structure

### Launch Phase — Monthly P&L Model

| Line Item | Monthly Cost | Annual Cost |
|-----------|-------------|-------------|
| **Salaries** | Rs 7.7L | Rs 92 LPA |
| **Technology (GCP + APIs)** | Rs 0.45L | Rs 5.4 LPA |
| **Marketing spend** | Rs 1.0L | Rs 12 LPA |
| **Office / coworking** | Rs 0.5L | Rs 6 LPA |
| **Legal / accounting (own compliance)** | Rs 0.25L | Rs 3 LPA |
| **Miscellaneous (tools, subscriptions)** | Rs 0.3L | Rs 3.6 LPA |
| **Total Monthly Burn** | **Rs 10.2L** | **~Rs 1.22 Cr** |

### Revenue Required to Break Even (Launch)

| Scenario | Incorporations/month | Compliance subs | Service orders/month | Monthly Revenue | Status |
|----------|---------------------|----------------|---------------------|----------------|--------|
| Break-even | 30 @ Rs 7K avg | 50 @ Rs 3K avg | 20 @ Rs 4K avg | Rs 4.4L | Loss (Rs 5.8L gap) |
| Sustainable | 50 @ Rs 7K avg | 150 @ Rs 3.5K avg | 40 @ Rs 5K avg | Rs 10.7L | Break-even |
| Profitable | 80 @ Rs 8K avg | 300 @ Rs 4K avg | 60 @ Rs 5K avg | Rs 19.4L | Profitable |

**Key insight**: Compliance subscriptions are the path to profitability. Incorporation revenue alone cannot cover the cost structure. You need ~150+ active compliance subscribers at an avg of Rs 3,500/month to break even.

---

## Part 4: Marketing Strategy & Budget

### Channel Strategy

#### Channel 1: SEO & Content Marketing (40% of budget)

**Why**: Indian founders actively search "how to register private limited company," "LLP vs Pvt Ltd," "GST registration process." Ranking for these terms brings high-intent organic traffic at zero marginal cost.

**Execution**:
- **Entity comparison articles**: "LLP vs Private Limited — Which is Right for You?" (10-15 long-form articles)
- **Process guides**: "How to Incorporate a Company in India — Step by Step" (one per entity type)
- **Compliance guides**: "Annual Compliance for Private Limited Company — Complete Checklist"
- **State-specific landing pages**: "Company Registration in Maharashtra" (28 state pages)
- **Pricing transparency pages**: Already built — `/pricing` with interactive calculator
- **Free tools**: Entity wizard (`/wizard`), cap table builder (`/cap-table-setup`), entity comparison (`/compare`)

**Budget**: Rs 40,000/month (content writer salary + freelance articles)
**Timeline**: 3-6 months for meaningful organic traffic
**Target**: 5,000 - 20,000 organic visitors/month by Month 6

#### Channel 2: Performance Marketing — Google Ads (25% of budget)

**Why**: High-intent search ads for "company registration online India" capture founders actively looking to incorporate.

**Execution**:
- **Search campaigns**: "register private limited company," "LLP registration online," "company incorporation India"
- **Estimated CPC**: Rs 30-80 for incorporation keywords, Rs 15-40 for compliance keywords
- **Landing pages**: Dedicated pages per entity type with pricing and CTA
- **Retargeting**: Show ads to wizard users who didn't convert

**Budget**: Rs 25,000/month
**Target CPA**: Rs 500-1,500 per lead, Rs 2,000-5,000 per paying customer
**Expected conversions**: 5-15 paying customers/month

#### Channel 3: LinkedIn & Twitter/X (15% of budget)

**Why**: Founders and CAs are active on LinkedIn. Startup ecosystem on Twitter/X. Build credibility and thought leadership.

**Execution**:
- **LinkedIn posts**: Regulatory updates, compliance tips, entity comparison insights (3-4x/week)
- **LinkedIn ads**: Target: "Founder," "Director," "Chartered Accountant" titles in India
- **Twitter/X**: Startup ecosystem engagement, product updates, compliance deadline reminders
- **Founder communities**: Post in startup WhatsApp/Telegram groups, Reddit r/IndianStartups

**Budget**: Rs 15,000/month (organic effort + occasional boosted posts)
**Target**: 1,000-5,000 LinkedIn followers in 6 months

#### Channel 4: CA/CS Channel (B2B2C) (10% of budget)

**Why**: CAs manage 10-50 companies each. One CA onboarded = 10-50 potential compliance subscribers. This is the highest-leverage channel.

**Execution**:
- **CA outreach**: Direct outreach to CA firms in major cities (Mumbai, Delhi, Bangalore, Chennai, Hyderabad)
- **CA Portal as the pitch**: "Free compliance dashboard for all your clients"
- **CA referral program**: Rs 500-1,000 per client who subscribes through their CA
- **CA webinars**: Monthly webinar on compliance updates, featuring the CA Portal
- **ICAI/ICSI partnerships**: Presence at CA/CS conferences and chapter events

**Budget**: Rs 10,000/month (travel, webinar tools, referral payouts)
**Target**: 10-20 CAs onboarded in first 6 months, each bringing 5-10 clients

#### Channel 5: Product-Led Growth (10% of budget)

**Why**: Free tools bring users into the funnel without marketing spend.

**Existing PLG assets**:
- Entity wizard (`/wizard`) — free, no signup required
- Cap table builder (`/cap-table-setup`) — free tool
- Pricing calculator (`/pricing`) — transparent, interactive
- Investor portal — investors see the brand when viewing portfolio
- E-signature pages — signatories see the brand when signing

**New PLG opportunities**:
- **Free compliance checker**: "Enter your CIN, see your upcoming deadlines" — high viral potential
- **Free GST deadline tracker**: Enter GSTIN, get return calendar — attracts CA audience
- **Free startup cost calculator**: "How much does it cost to start a company in [state]?"

**Budget**: Rs 10,000/month (development time for new tools, hosting)

---

### Marketing Budget by Phase

#### Launch (Month 1-6)

| Channel | Monthly Budget | Annual Budget | Expected Outcome |
|---------|---------------|--------------|-----------------|
| SEO & Content | Rs 40,000 | Rs 4.8 LPA | 5K-20K organic visitors/month by M6 |
| Google Ads | Rs 25,000 | Rs 3.0 LPA | 5-15 paying customers/month |
| LinkedIn & Twitter | Rs 15,000 | Rs 1.8 LPA | Brand awareness, 1K followers |
| CA/CS Channel | Rs 10,000 | Rs 1.2 LPA | 10-20 CAs onboarded |
| Product-Led Growth | Rs 10,000 | Rs 1.2 LPA | Free tool traffic |
| **Total** | **Rs 1,00,000** | **Rs 12 LPA** | |

#### Growth (Month 7-18)

| Channel | Monthly Budget | Annual Budget | Notes |
|---------|---------------|--------------|-------|
| SEO & Content | Rs 60,000 | Rs 7.2 LPA | Hire dedicated content writer |
| Google Ads | Rs 75,000 | Rs 9.0 LPA | Scale winning campaigns |
| LinkedIn Ads | Rs 40,000 | Rs 4.8 LPA | Targeted B2B campaigns |
| CA/CS Channel | Rs 30,000 | Rs 3.6 LPA | Scale referral program |
| Product-Led Growth | Rs 20,000 | Rs 2.4 LPA | Launch new free tools |
| PR & Events | Rs 25,000 | Rs 3.0 LPA | Startup events, media coverage |
| **Total** | **Rs 2,50,000** | **Rs 30 LPA** | |

#### Scale (Month 18+)

| Channel | Monthly Budget | Annual Budget | Notes |
|---------|---------------|--------------|-------|
| SEO & Content | Rs 80,000 | Rs 9.6 LPA | Multiple writers, video content |
| Google Ads | Rs 1,50,000 | Rs 18.0 LPA | Nationwide campaigns |
| LinkedIn + Meta Ads | Rs 80,000 | Rs 9.6 LPA | Retargeting, lookalike audiences |
| CA/CS Channel | Rs 50,000 | Rs 6.0 LPA | National CA partnership program |
| Product-Led Growth | Rs 30,000 | Rs 3.6 LPA | Advanced free tools |
| PR, Events, Partnerships | Rs 60,000 | Rs 7.2 LPA | Incubator partnerships, media |
| **Total** | **Rs 4,50,000** | **Rs 54 LPA** | |

---

### Key Marketing Metrics

| Metric | Target (Launch) | Target (Growth) | Target (Scale) |
|--------|----------------|-----------------|----------------|
| Website visitors/month | 5,000 | 25,000 | 100,000 |
| Signup conversion rate | 3-5% | 5-8% | 8-12% |
| Signups/month | 150-250 | 1,250-2,000 | 8,000-12,000 |
| Paid conversion rate | 5-10% | 10-15% | 15-20% |
| Paying customers/month | 10-25 | 125-300 | 1,200-2,400 |
| CAC (blended) | Rs 4,000-10,000 | Rs 2,000-4,000 | Rs 1,000-2,500 |
| LTV (12-month) | Rs 15,000-30,000 | Rs 25,000-50,000 | Rs 40,000-80,000 |
| LTV:CAC ratio | 3:1 - 4:1 | 6:1 - 12:1 | 16:1 - 32:1 |

---

## Part 5: Consolidated Annual Budget

### Launch Phase (Year 1)

| Category | Annual Cost | % of Total |
|----------|-----------|-----------|
| Salaries (11.5 people) | Rs 92 LPA | 62% |
| Technology (GCP + APIs) | Rs 5.4 LPA | 4% |
| Marketing (spend + team) | Rs 18 LPA | 12% |
| Office / Coworking | Rs 6 LPA | 4% |
| Legal, Compliance, Insurance | Rs 4 LPA | 3% |
| Tools & Subscriptions (Slack, Notion, GitHub, etc.) | Rs 3 LPA | 2% |
| Travel & Misc | Rs 3 LPA | 2% |
| **Contingency (15%)** | Rs 20 LPA | 13% |
| **Total Year 1 Budget** | **~Rs 1.5 Cr** | |

### Growth Phase (Year 2)

| Category | Annual Cost | % of Total |
|----------|-----------|-----------|
| Salaries (25 people) | Rs 2.3 Cr | 63% |
| Technology | Rs 10.8 LPA | 3% |
| Marketing | Rs 36 LPA | 10% |
| Office | Rs 12 LPA | 3% |
| Legal, Compliance | Rs 5 LPA | 1% |
| Tools & Subscriptions | Rs 5 LPA | 1% |
| Travel | Rs 5 LPA | 1% |
| **Contingency (15%)** | Rs 42 LPA | 11% |
| **Total Year 2 Budget** | **~Rs 3.2 Cr** | |

### Scale Phase (Year 3)

| Category | Annual Cost | % of Total |
|----------|-----------|-----------|
| Salaries (40 people) | Rs 3.7 Cr | 63% |
| Technology | Rs 18 LPA | 3% |
| Marketing | Rs 60 LPA | 10% |
| Office | Rs 18 LPA | 3% |
| Legal, Compliance | Rs 8 LPA | 1% |
| Tools & Subscriptions | Rs 6 LPA | 1% |
| Travel | Rs 8 LPA | 1% |
| **Contingency (15%)** | Rs 63 LPA | 11% |
| **Total Year 3 Budget** | **~Rs 5.5 Cr** | |

---

## Part 6: Revenue vs Cost Scenarios

### Year 1 — Path to Sustainability

| Month | Incorporations | Compliance Subs (cumulative) | Service Orders | Monthly Revenue | Monthly Cost | Profit/Loss |
|-------|---------------|----------------------------|---------------|----------------|-------------|-------------|
| M1 | 5 | 0 | 0 | Rs 35K | Rs 10.2L | (Rs 9.8L) |
| M3 | 15 | 10 | 5 | Rs 1.6L | Rs 10.5L | (Rs 8.9L) |
| M6 | 30 | 40 | 15 | Rs 4.3L | Rs 11.0L | (Rs 6.7L) |
| M9 | 45 | 90 | 25 | Rs 7.6L | Rs 11.5L | (Rs 3.9L) |
| M12 | 60 | 150 | 35 | Rs 11.4L | Rs 12.0L | (Rs 0.6L) |

**Break-even point**: ~Month 12-14, with ~150 active compliance subscribers

**Cumulative Year 1 loss**: ~Rs 80L - 1 Cr (requires funding or bootstrapping reserves)

### Year 2 — Growth & Profitability

| Quarter | Monthly Revenue | Monthly Cost | Monthly Profit | Cumulative |
|---------|----------------|-------------|----------------|-----------|
| Q1 Y2 | Rs 14L | Rs 16L | (Rs 2L) | Loss |
| Q2 Y2 | Rs 20L | Rs 18L | Rs 2L | Break-even |
| Q3 Y2 | Rs 28L | Rs 20L | Rs 8L | Profitable |
| Q4 Y2 | Rs 35L | Rs 22L | Rs 13L | Profitable |

**Year 2 net**: Rs 20-40L profit (depending on growth rate)

---

## Part 7: Key Financial Insights

### 1. Salaries Are 60%+ of Costs
Technology is cheap (3-4% of total). The business is labor-intensive because every government filing requires a human. Reducing headcount through automation is the single biggest lever for profitability.

### 2. Compliance Subscriptions Drive Break-Even
Incorporation is one-time revenue with high margin but doesn't recur. Compliance subscriptions at Rs 3,000-5,000/month per client create the recurring base that covers fixed costs. The target is 150+ subscribers to break even.

### 3. Marketing ROI Is Highest on SEO and CA Channel
- **SEO**: Zero marginal cost after content is created. Organic traffic compounds over time. Best long-term ROI.
- **CA channel**: One CA brings 10-50 clients. CAC per client via CA referral is Rs 100-200 (vs Rs 4,000-10,000 via Google Ads). Invest heavily here.
- **Google Ads**: Necessary for early traction but expensive. Target CPA under Rs 3,000.

### 4. Seasonal Cash Flow Is Lumpy
- **July-December**: Peak filing season = higher service revenue but also need temporary staff
- **January-March**: Lower filing revenue, good time for product development
- **April-June**: Incorporation activity picks up (new financial year)

Plan cash reserves for 3 months of runway at all times.

### 5. Cloud SQL Is Overprovisioned
The current `db-perf-optimized-N-8` PostgreSQL instance costs Rs 25,000-35,000/month. For 0-100 companies, a `db-g1-small` (Rs 5,000-8,000/month) is sufficient. Save Rs 20,000/month at launch.

### 6. Razorpay TDR Is a Hidden Cost
At 2% transaction fee on all revenue, Razorpay takes Rs 2 for every Rs 100 collected. On Rs 1 Cr annual revenue, that is Rs 2 LPA. Factor this into pricing — it is not a technology cost, it is a cost of revenue.
