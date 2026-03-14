# Companies Made Simple India

> AI-powered company incorporation and compliance platform for Indian entrepreneurs.
> From idea → incorporated entity → fully compliant business.

## Vision

Build India's first **AI-native** company incorporation platform that combines the product polish of Stripe Atlas, the lifecycle approach of SeedLegals, and deep India-specific regulatory expertise — powered by AI with human expert verification.

## What We Support

| Entity Type | Status |
|-------------|--------|
| Private Limited Company | ✅ Phase 1 |
| One Person Company (OPC) | ✅ Phase 1 |
| Limited Liability Partnership (LLP) | ✅ Phase 1 |
| Section 8 Company (Non-Profit) | 🔜 Phase 2 |
| Sole Proprietorship | 🔜 Phase 2 |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, Tailwind CSS 4, TypeScript |
| Backend | FastAPI (Python), SQLAlchemy, Pydantic |
| Database | PostgreSQL (prod) / SQLite (dev) |
| AI | Google Gemini / OpenAI (planned) |

## Project Structure

```
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── routers/      # API route modules
│   │   ├── services/     # Business logic
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # DB connection
│   │   └── main.py       # App entrypoint
│   └── requirements.txt
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # Pages (App Router)
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities & API client
│   └── package.json
└── docs/                 # Documentation
    ├── VISION.md
    └── ARCHITECTURE.md
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the app.
API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Key Features (Foundation)

- **Entity Selection Wizard** — AI-guided company type recommendation
- **Dynamic Pricing Calculator** — Real-time cost breakdown with state-wise stamp duty
- **Modular Pricing** — Platform fee + transparent government costs (zero markup)
- **All-Inclusive View** — Total shown before checkout, no hidden fees
