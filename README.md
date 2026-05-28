# PlotIQ — AI-Powered Land Discovery & Verification Platform

> AI-assisted land due diligence and discovery for Hyderabad, Telangana.  
> Covers Phases 0–3: Foundation, Core Discovery, Intelligence Layer, and Location & Geospatial Intelligence.

---

## What It Does

PlotIQ is **not** a classifieds portal. It layers intelligence on top of listings:

- **Natural language search** — "2 acres near ORR under 50 lakhs" → structured filter + semantic vector search
- **AI Confidence Score** — 6-dimension trust score (0–100) with per-dimension breakdown and radial chart
- **Legal Document Analyzer** — OCR + Groq LLM extracts parties, risks, missing approvals from EC / Sale Deed / Patta
- **Price Intelligence** — Ridge regression with P10/P50/P90 confidence interval, comparables, price trend chart
- **Location Intelligence** — Overpass API POI overlay (schools, hospitals, metro, highways), flood risk layer
- **Future Growth Signals** — 16 curated Hyderabad infrastructure projects with growth tier label
- **Admin Trust Dashboard** — Verification queue, approve/reject/scam actions, audit log
- **Seller Listing Creation** — 3-step form (location pin → plot details → document upload)

---

## Project Structure

```
PlotIQ/
├── frontend/                  # Vite + React + TypeScript
│   ├── src/
│   │   ├── components/        # UI primitives, map, listing tabs, search, seller
│   │   ├── pages/             # DiscoverPage, ListingDetailPage, SellerPage,
│   │   │                      #   AdminDashboard, LegalPage
│   │   ├── hooks/             # TanStack Query wrappers
│   │   ├── stores/            # Zustand (mapStore, authStore)
│   │   └── lib/               # axios API client, RequireAuth guards
│   ├── public/
│   │   └── hyderabad_flood_zones.geojson
│   └── .env.example
│
├── backend/                   # FastAPI Python service
│   ├── app/
│   │   ├── api/               # listings, search, documents, admin, webhooks
│   │   ├── services/          # listing, search, document, price, poi, growth, admin
│   │   ├── workers/           # Celery tasks (score, embedding, document)
│   │   ├── models/            # SQLAlchemy ORM (7 tables)
│   │   ├── schemas/           # Pydantic v2 request/response schemas
│   │   └── core/              # config, database, auth (Clerk JWT)
│   ├── tests/
│   │   └── test_properties.py # 11 Hypothesis property-based tests
│   └── requirements.txt
│
├── ai/                        # AI pipeline
│   ├── chains/                # NL query parser, document analyzer (Groq)
│   ├── scorers/               # 6 confidence score dimensions + engine
│   ├── embeddings/            # sentence-transformers all-MiniLM-L6-v2
│   └── price_model/           # scikit-learn Ridge regression
│
├── seed/
│   ├── seed.py                # Main seed script
│   ├── seed_data.py           # 8 Hyderabad localities
│   ├── growth_signals_data.py # 16 curated infrastructure projects
│   └── SEED_DATA.md
│
├── docker-compose.yml         # Local Postgres + Redis
├── .env.example               # Backend env vars template
└── README.md
```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Node.js 18+ | Frontend |
| Python 3.10+ | Backend + AI layer |
| Docker & Docker Compose | Local Postgres + Redis |
| Supabase project | PostgreSQL + **PostGIS** + **pgvector** extensions must be enabled |
| Clerk account | Auth — Google OAuth + Phone OTP |
| Groq API key | LLM for NL query parsing and document analysis |
| Cloudflare R2 bucket | Document and image storage |
| Google Maps JS API key | Map view, POI overlay, static map thumbnails |
| OpenRouter API key | Optional fallback LLM |

---

## Local Development Setup

### 1. Clone and configure environment

```bash
git clone https://github.com/Chirag-Keshav/PlotIQ.git
cd PlotIQ

# Backend env vars
cp .env.example .env
# Edit .env and fill in DATABASE_URL, REDIS_URL, CLERK_SECRET_KEY, GROQ_API_KEY, etc.

# Frontend env vars
cp frontend/.env.example frontend/.env
# Edit frontend/.env and fill in VITE_CLERK_PUBLISHABLE_KEY, VITE_API_BASE_URL, VITE_GOOGLE_MAPS_API_KEY
```

### 2. Start local services (Postgres + Redis)

```bash
docker-compose up -d
```

> **Supabase note:** For PostGIS + pgvector support, point `DATABASE_URL` at your Supabase project and ensure both extensions are enabled (`CREATE EXTENSION postgis; CREATE EXTENSION vector;`). The docker-compose Postgres is for basic local testing only.

### 3. Set up the backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend (auto-reload)
uvicorn app.main:app --reload --port 8000
```

The backend checks DB and Redis connectivity at startup and logs the result.

### 4. Start Celery worker (document analysis + score computation)

```bash
# In a separate terminal, from the backend/ directory:
celery -A app.workers.celery_app worker --loglevel=info
```

### 5. Seed the database

```bash
# From the repo root:
python seed/seed.py
```

This will:
1. Clear existing listings, comparables, and growth signals
2. Insert **64 plot listings** across 8 Hyderabad localities
3. Generate **pgvector embeddings** (all-MiniLM-L6-v2) for each listing
4. Seed **confidence score breakdowns** distributed across high/medium/low tiers (≥10 each)
5. Insert **16 growth signal records** (HMDA layouts, NHAI highways, HMRL metro, industrial parks)
6. Run **validation queries** (count, tier distribution, bounding box, embedding check)

See `seed/SEED_DATA.md` for full dataset documentation and regeneration instructions.

### 6. Set up the frontend

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:3000
```

---

## Environment Variables

### Backend (`.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (Supabase) |
| `REDIS_URL` | Redis connection string (Upstash) |
| `CLERK_SECRET_KEY` | Clerk backend secret key |
| `CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `CLERK_WEBHOOK_SECRET` | Clerk webhook signing secret (SVIX) |
| `GROQ_API_KEY` | Groq LLM API key (`llama-4-scout-17b`) |
| `OPENROUTER_API_KEY` | OpenRouter fallback LLM key |
| `R2_BUCKET` | Cloudflare R2 bucket name |
| `R2_ENDPOINT` | R2 S3-compatible endpoint URL |
| `R2_ACCESS_KEY` | R2 access key ID |
| `R2_SECRET_KEY` | R2 secret access key |
| `GOOGLE_MAPS_API_KEY` | Google Maps JS API key |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed origins (default: `http://localhost:3000`) |

### Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key (same as backend) |
| `VITE_API_BASE_URL` | Backend API base URL (e.g. `http://localhost:8000/api/v1`) |
| `VITE_GOOGLE_MAPS_API_KEY` | Google Maps JS API key |

---

## API Reference

With the backend running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: `GET http://localhost:8000/health`

### Key endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | None | DB + Redis + storage status |
| `POST` | `/api/v1/search` | None | NL + semantic search |
| `GET` | `/api/v1/listings` | None | Paginated listing list |
| `GET` | `/api/v1/listings/{id}` | None | Full listing detail |
| `POST` | `/api/v1/listings` | Seller | Create listing (TOS required, 5/day limit) |
| `GET` | `/api/v1/listings/{id}/score` | None | Confidence score breakdown |
| `GET` | `/api/v1/listings/{id}/price-estimate` | None | P10/P50/P90 + comparables + trend |
| `GET` | `/api/v1/listings/{id}/pois` | None | Nearby POIs (Overpass API, Redis cached) |
| `GET` | `/api/v1/listings/{id}/growth-signals` | None | Growth signals + tier label |
| `GET` | `/api/v1/listings/{id}/documents` | Auth | Document list with AI analysis |
| `POST` | `/api/v1/listings/{id}/documents` | Auth | Upload document (triggers async analysis) |
| `POST` | `/api/v1/listings/{id}/report` | Auth | Submit grievance report |
| `GET` | `/api/v1/admin/queue` | Admin | Pending verification queue |
| `POST` | `/api/v1/admin/listings/{id}/action` | Admin | approve / request_docs / reject / mark_scam |
| `GET` | `/api/v1/admin/metrics` | Admin | Trust dashboard metrics |
| `POST` | `/api/v1/webhooks/clerk` | SVIX | Clerk user sync webhook |

---

## Running Tests

```bash
# From the repo root
pip install pytest hypothesis

# Run all property-based tests (Properties 1–11)
pytest backend/tests/test_properties.py -v

# Run all backend tests
pytest backend/tests/ -v
```

The 11 properties tested:

| # | Property |
|---|---|
| 1 | `ListingCreate` serialization round-trip |
| 2 | `DocumentAnalysis` serialization round-trip |
| 3 | `SearchFilters` query-string round-trip |
| 4 | Validation error identifies bad field by name |
| 5 | Confidence score always in [0, 100] |
| 6 | Pricing anomaly flagged iff Z-score > 2.0 |
| 7 | Price classification matches P25/P75 thresholds |
| 8 | Negotiation range = [P25×area, P50×area] in lakhs |
| 9 | Embedding always returns exactly 384 floats |
| 10 | Growth tier label matches approved/under-construction count rules |
| 11 | Listing status matches score thresholds + fraud signal override |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vite + React 19 + TypeScript + Tailwind CSS v4 |
| State | Zustand (map state) + TanStack Query (server state) |
| Auth | Clerk (Google OAuth + Phone OTP) |
| Maps | Google Maps JS API (`@react-google-maps/api`) |
| Charts | Recharts (price trend line chart, confidence radial chart) |
| Backend | FastAPI + SQLAlchemy (async) + Alembic |
| Database | PostgreSQL + PostGIS + pgvector (Supabase) |
| Cache | Redis (Upstash) |
| Task Queue | Celery + Redis (score, embedding, document analysis workers) |
| LLM | Groq `llama-4-scout-17b` + OpenRouter fallback |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-dim, runs locally) |
| Price Model | scikit-learn Ridge regression + bootstrap resampling |
| OCR | pdfplumber (text PDF) + pytesseract (scanned images) |
| Storage | Cloudflare R2 (S3-compatible) |

---

## Compliance

PlotIQ is an informational platform, not a real estate broker or legal advisor.  
All AI-generated outputs include mandatory non-dismissible disclaimers:

- **Confidence Score** — "AI confidence score is a model estimate and does not constitute legal title certification."
- **Price Estimates** — "Price estimates are model outputs and are not a valuation or guarantee."
- **Document Analysis** — "This is an AI-generated summary only. Consult a licensed lawyer for legal advice."
- **Growth Signals** — "Growth signals are based on announced or approved projects. This is not investment advice."

KYC data (Aadhaar, PAN) is never transmitted to any LLM API endpoint.  
Full Terms of Service, Privacy Policy, and Grievance contact are available at `/legal`.
