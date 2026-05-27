# PlotIQ — AI-Powered Land Discovery & Verification Platform

> AI-assisted land due diligence and discovery for Hyderabad, Telangana.

## Project Structure

```
PlotIQ/
├── frontend/       # Vite + React web application
├── backend/        # FastAPI Python service
├── ai/             # LangChain chains, scorers, MCP tools
├── seed/           # Seed data scripts and dataset
├── docker-compose.yml
├── .env.example
└── README.md
```

## Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- A Supabase project with PostGIS + pgvector extensions enabled
- A Clerk account (auth)
- A Groq API key (LLM)
- A Cloudflare R2 bucket (file storage)
- A Google Maps JS API key (maps)

## Local Development Setup

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd PlotIQ
cp .env.example .env
# Fill in all values in .env
```

### 2. Start local services (Postgres + Redis)

```bash
docker-compose up -d
```

> **Note:** For full functionality, connect to Supabase (PostGIS + pgvector required). The docker-compose Postgres is for local dev without Supabase.

### 3. Set up backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 4. Seed the database

```bash
cd seed
python seed.py
```

See `seed/SEED_DATA.md` for details on regenerating the dataset.

### 5. Set up frontend

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:3000
```

## Environment Variables

See `.env.example` for all required variables. Key vars:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (Supabase) |
| `REDIS_URL` | Redis connection string (Upstash) |
| `CLERK_SECRET_KEY` | Clerk backend secret key |
| `CLERK_PUBLISHABLE_KEY` | Clerk frontend publishable key |
| `GROQ_API_KEY` | Groq LLM API key |
| `OPENROUTER_API_KEY` | OpenRouter fallback LLM key |
| `R2_BUCKET` | Cloudflare R2 bucket name |
| `R2_ENDPOINT` | Cloudflare R2 S3-compatible endpoint |
| `R2_ACCESS_KEY` | R2 access key |
| `R2_SECRET_KEY` | R2 secret key |
| `GOOGLE_MAPS_API_KEY` | Google Maps JS API key |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk key for frontend |
| `VITE_API_BASE_URL` | Backend API base URL |
| `VITE_GOOGLE_MAPS_API_KEY` | Maps key for frontend |

## API Documentation

With the backend running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## Database Seeding

```bash
cd seed
python seed.py
```

This will:
1. Run all Alembic migrations
2. Insert 60 Hyderabad plot listings across 8 localities
3. Generate pgvector embeddings for each listing
4. Insert 15+ growth signal records
5. Validate spatial queries (radius, bounding box, nearest-N)

See `seed/SEED_DATA.md` for dataset details and regeneration instructions.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vite + React + TypeScript + Tailwind CSS v4 |
| Backend | FastAPI + SQLAlchemy + Alembic |
| Database | PostgreSQL + PostGIS + pgvector (Supabase) |
| Cache | Redis (Upstash) |
| Task Queue | Celery + Redis |
| LLM | Groq (llama-4-scout) + OpenRouter fallback |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Auth | Clerk |
| Maps | Google Maps JS API |
| Storage | Cloudflare R2 |

## Compliance

PlotIQ is positioned as a classifieds-tech platform (not a broker/agent). All AI outputs include mandatory disclaimers. See `/legal` in the app and `COMPLIANCE.md` for full details.
