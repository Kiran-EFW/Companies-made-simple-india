# CA Portal — Complete

All features built and build verified (61 pages, 0 errors).

## Frontend Pages (7 routes)

| Route | Page | Status |
|-------|------|--------|
| `/ca` | Dashboard — stats, compliance scores, penalty exposure | Done |
| `/ca/tasks` | Cross-company task list with filters, mark complete | Done |
| `/ca/calendar` | FY compliance calendar (Apr-Mar timeline) | Done |
| `/ca/tax` | Tax Filing Tracker — ITR, TDS quarterly, advance tax, GST returns | Done |
| `/ca/tds` | TDS Calculator — interactive calculator + section rates + due dates | Done |
| `/ca/companies` | Assigned companies list | Done |
| `/ca/companies/[id]` | Company detail — Compliance (with notes), Documents, Audit Pack tabs | Done |

## Backend Endpoints (17 endpoints in `ca_portal.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ca/seed-demo` | POST | Create CA demo user + assign to all companies |
| `/ca/dashboard-summary` | GET | Summary stats |
| `/ca/companies` | GET | List assigned companies |
| `/ca/companies/{id}/compliance` | GET | Company compliance tasks |
| `/ca/companies/{id}/documents` | GET | Company documents |
| `/ca/companies/{id}/filings/{task_id}` | PUT | Mark filing complete |
| `/ca/tasks` | GET | All tasks across companies |
| `/ca/scores` | GET | All company compliance scores |
| `/ca/companies/{id}/score` | GET | Single company score |
| `/ca/companies/{id}/penalties` | GET | Penalty estimates |
| `/ca/companies/{id}/tax-overview` | GET | ITR, TDS, advance tax status |
| `/ca/companies/{id}/gst-dashboard` | GET | GST return schedule |
| `/ca/tds/calculate` | POST | TDS calculator |
| `/ca/tds/sections` | GET | TDS section rates |
| `/ca/tds/due-dates` | GET | TDS quarterly due dates |
| `/ca/companies/{id}/audit-pack` | GET | Audit-ready data export |
| `/ca/companies/{id}/tasks/{task_id}/notes` | GET/POST | Task notes |

## Other Changes

- Login page: CA Demo button added (ca@anvils.in / Anvils123)
- Layout: 6 nav items (Dashboard, Tasks, Calendar, Tax, TDS Calc, Companies)
- Theme: Dark navy sidebar (#0f172a) + teal accents (#0d9488)
- Auth: ca_lead role redirect + assignment-based access control

## To Use

1. Start the backend
2. Call `POST /ca/seed-demo` with `{ "secret": "anvils-demo-2026" }` to create the CA user
3. Log in as ca@anvils.in / Anvils123 (or use the "CA Demo" button on login page)
