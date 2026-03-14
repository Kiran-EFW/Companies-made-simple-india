# Architecture: Companies Made Simple India

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│   Web App (Next.js)  │  Mobile (Future)  │  WhatsApp    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                    API GATEWAY                           │
│            FastAPI (/api/v1) + Auth                      │
├─────────────────────────────────────────────────────────┤
│                  CORE SERVICES                           │
│   Pricing Engine  │  Entity Advisor  │  Incorporation   │
│   Compliance      │  Document AI     │  Notifications   │
├─────────────────────────────────────────────────────────┤
│                    AI AGENTS                             │
│   Name Validator  │  Doc Processor  │  Form Filler      │
│   MOA/AOA Drafter │  Chatbot        │  Risk Monitor     │
├─────────────────────────────────────────────────────────┤
│                  DATA LAYER                              │
│   PostgreSQL  │  Document Store  │  Audit Log           │
└─────────────────────────────────────────────────────────┘
```

## Key Services

### Pricing Engine
Dynamically calculates incorporation costs based on:
- Entity type (Pvt Ltd, OPC, LLP, Section 8)
- State of registration (stamp duty varies dramatically)
- Authorized capital / contribution amount
- Number of directors/partners
- DSC requirements

### Entity Advisor
AI-guided wizard that recommends the best company type based on:
- Solo vs team
- Funding plans
- Revenue expectations
- Profit vs non-profit
- Foreign involvement

### AI + Backend Team Collaboration
```
AI Agent processes → creates draft → queued for review
Backend team reviews → approves/corrects → returns to pipeline
System files → tracks status → notifies user
```

## Data Models

- **User**: Authentication, profile, contact
- **Company**: Entity type, status, pipeline stage, pricing snapshot
- **Director**: Personal details, documents, DSC status
- **Document**: Uploaded files, OCR results, verification status
- **Task**: Agent tasks with status tracking
- **PricingConfig**: State-wise stamp duty, fee slabs (admin-managed)
