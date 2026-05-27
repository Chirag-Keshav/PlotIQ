# Implementation Tasks: PlotIQ POC (Phases 0–3)

## Task Overview

Tasks are ordered by dependency. Each task maps to a coherent unit of work. Property-based tests (PBT) are embedded as sub-tasks within the relevant parent tasks.

---

## Phase 0 — Foundation

### 1. Monorepo Restructure and Video Fix

- [x] 1.1 Create top-level `/frontend`, `/backend`, `/ai`, `/seed` directories
- [x] 1.2 Move all existing `src/`, `index.html`, `vite.config.ts`, `tsconfig.json`, `package.json` into `/frontend/`
- [x] 1.3 Move `ce_f_f_c_be_d_b_d_ef_a_mp_.mp4` from repo root to `frontend/public/`
- [x] 1.4 Update `Hero.tsx` video `<source src>` from CDN URL to `/ce_f_f_c_be_d_b_d_ef_a_mp_.mp4`
- [x] 1.5 Update `frontend/vite.config.ts` paths if needed after move; verify `npm run dev` still works
- [x] 1.6 Create root-level `README.md` with local setup steps, env vars list, and seeding instructions
- [x] 1.7 Create root-level `.env.example` with all required key names (no values)
- [x] 1.8 Create `docker-compose.yml` at repo root for local Postgres + Redis dev services

---

### 2. Backend Scaffold (FastAPI)

- [x] 2.1 Create `backend/` directory with `app/`, `alembic/`, `tests/` subdirectories per design
- [x] 2.2 Create `backend/requirements.txt` with pinned versions: fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, pgvector, pydantic[email], python-multipart, celery, redis, httpx, python-jose, svix, boto3, ruff
- [x] 2.3 Create `backend/app/core/config.py` — Pydantic Settings class loading all env vars (DATABASE_URL, REDIS_URL, CLERK_SECRET_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, R2_BUCKET, R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, GOOGLE_MAPS_API_KEY)
- [x] 2.4 Create `backend/app/core/database.py` — SQLAlchemy async engine, session factory, startup connectivity check with PostGIS/pgvector extension validation
- [x] 2.5 Create `backend/app/main.py` — FastAPI app factory, CORS middleware, router registration, lifespan startup/shutdown
- [x] 2.6 Implement `GET /health` endpoint returning `{status, version, dependencies}` with 200/503 based on DB+Redis reachability
- [x] 2.7 Create `backend/app/core/auth.py` — Clerk JWT verification middleware using JWKS endpoint; `get_current_user` and `require_admin` dependency functions
- [x] 2.8 Create `backend/app/workers/celery_app.py` — Celery app configured with Upstash Redis broker and result backend

---

### 3. Database Schema and Migrations

- [x] 3.1 Create SQLAlchemy ORM models for all 7 tables: `listings`, `listing_documents`, `growth_signals`, `fraud_signals`, `comparables`, `users`, `audit_log` (files in `backend/app/models/`)
- [x] 3.2 Configure Alembic (`alembic.ini`, `alembic/env.py`) to use async SQLAlchemy engine and auto-detect model changes
- [x] 3.3 Generate and run initial Alembic migration creating all 7 tables with correct column types (GEOGRAPHY, VECTOR(384), JSONB, UUID PKs)
- [x] 3.4 Add PostGIS spatial index on `listings.location` and B-tree indexes on `listings.locality`, `listings.confidence_score`, `listings.price_lakhs`
- [x] 3.5 Add pgvector IVFFlat index on `listings.embedding` (lists=50 for seed dataset size)
- [x] 3.6 Create `backend/app/schemas/listing.py` — Pydantic v2 schemas: `ListingCreate`, `ListingSummary`, `ListingDetail`, `RiskFlag`, `GrowthSignalSummary`
- [x] 3.7 Create `backend/app/schemas/search.py` — `SearchFilters`, `BoundingBox`, `SearchRequest`, `SearchResponse`
- [x] 3.8 Create `backend/app/schemas/document.py` — `DocumentAnalysis` (all 5 doc types), `DocumentUploadResponse`
- [x] 3.9 Create `backend/app/schemas/admin.py` — `AdminQueueItem`, `AdminAction`, `AdminMetrics`
- [ ] 3.10 Write PBT: `test_listing_create_roundtrip` — Property 1: deserialize → serialize → deserialize produces equivalent model (Hypothesis, 100 examples)
- [ ] 3.11 Write PBT: `test_document_analysis_roundtrip` — Property 2: serialize → deserialize produces equivalent DocumentAnalysis (Hypothesis, 100 examples)
- [ ] 3.12 Write PBT: `test_search_filters_roundtrip` — Property 3: serialize to query string → deserialize produces equivalent SearchFilters (Hypothesis, 100 examples)
- [ ] 3.13 Write PBT: `test_validation_error_identifies_field` — Property 4: invalid ListingCreate payload raises ValidationError naming the bad field (Hypothesis, 100 examples)

---

### 4. AI Layer Scaffold

- [x] 4.1 Create `ai/` directory with `scorers/`, `chains/`, `embeddings/`, `price_model/` subdirectories
- [x] 4.2 Create `ai/embeddings/embedding_service.py` — `EmbeddingService` wrapping `sentence-transformers/all-MiniLM-L6-v2`; `embed(text) -> list[float]` and `embed_listing(listing) -> list[float]`
- [ ] 4.3 Write PBT: `test_embedding_dimension` — Property 9: any non-empty string produces exactly 384 floats (Hypothesis, 100 examples)
- [x] 4.4 Create `ai/scorers/confidence_engine.py` — `compute_confidence_score(listing_state) -> tuple[int, ConfidenceBreakdown]` with weighted aggregation
- [x] 4.5 Create `ai/scorers/document_completeness.py` — scorer returning 0–100 based on which doc types are present
- [x] 4.6 Create `ai/scorers/kyc_scorer.py` — 100/50/0 based on KYC status
- [x] 4.7 Create `ai/scorers/geo_consistency.py` — validates lat/lng within Hyderabad bounding box, cross-checks locality
- [x] 4.8 Create `ai/scorers/duplicate_detector.py` — perceptual hash comparison (imagehash library) + phone reuse check
- [x] 4.9 Create `ai/scorers/pricing_anomaly.py` — Z-score vs locality median price/sqyd
- [x] 4.10 Create `ai/scorers/freshness_scorer.py` — linear decay from 100 at 0 days to 0 at 90 days
- [ ] 4.11 Write PBT: `test_confidence_score_in_range` — Property 5: any listing state produces score in [0, 100] (Hypothesis, 100 examples)
- [ ] 4.12 Write PBT: `test_pricing_anomaly_matches_zscore` — Property 6: flagged iff Z-score > 2.0 (Hypothesis, 100 examples)
- [ ] 4.13 Write PBT: `test_listing_status_from_score` — Property 11: status assignment matches score thresholds and fraud signal override (Hypothesis, 100 examples)

---

### 5. Seed Dataset

- [x] 5.1 Create `seed/listings_data.py` with 60 Hyderabad plot records across 8 localities (Kokapet, Shadnagar, Adibatla, Patancheru, Ibrahimpatnam, Shamshabad, Ghatkesar, Sangareddy) — at least 10 per confidence tier (high/medium/low)
- [x] 5.2 Create `seed/growth_signals_data.py` with 15+ curated Hyderabad infrastructure projects (HMDA layouts, NHAI NH-44/NH-65/ORR Phase II, HMRL metro extensions, Fab City, Genome Valley, Adibatla aerospace park)
- [x] 5.3 Create `seed/seed.py` — main script: runs migrations, inserts listings, generates embeddings via EmbeddingService, inserts growth signals, validates PostGIS radius/bounding-box/nearest-N queries before exit
- [x] 5.4 Create `seed/SEED_DATA.md` documenting how to regenerate the dataset
- [x] 5.5 Train and serialize price model: `ai/price_model/train.py` runs Ridge regression on seed listings, saves `model.joblib`; integrate into backend startup (load if exists, train if not)

---

## Phase 1 — Core Discovery

### 6. Search Backend (NL Parser + Semantic Search)

- [x] 6.1 Create `ai/chains/nl_query_parser.py` — async `parse_nl_query(query: str) -> SearchFilters` using Groq `llama-4-scout-17b-16e-instruct` with JSON mode; fallback returns empty `SearchFilters()` on any error
- [x] 6.2 Create `backend/app/services/search_service.py` — `SearchService.search()`: NL parse → embed query → SQL WHERE from filters + PostGIS bounds → pgvector cosine re-rank → return `SearchResponse`
- [x] 6.3 Create `backend/app/api/search.py` — `POST /search` route handler; wire to `SearchService`; target <500ms response
- [x] 6.4 Create `backend/app/api/listings.py` — `GET /listings` (paginated), `GET /listings/{id}` endpoints
- [x] 6.5 Write unit tests: NL parser with 10 representative queries mapped to expected structured filters
- [x] 6.6 Write integration test: `POST /search` against seed data returns results in <500ms

---

### 7. Authentication (Clerk)

- [x] 7.1 Install and configure Clerk in `frontend/` — add `@clerk/clerk-react`, wrap app in `<ClerkProvider>`, set `VITE_CLERK_PUBLISHABLE_KEY` env var
- [x] 7.2 Update `frontend/src/components/Navbar.tsx` — show `<UserButton>` when signed in, show "Sign In" button when signed out; preserve existing glassmorphism styling
- [x] 7.3 Create `frontend/src/components/ui/AuthModal.tsx` — Clerk `<SignIn>` modal overlay triggered from Navbar
- [x] 7.4 Create `frontend/src/stores/authStore.ts` — Zustand store syncing Clerk user state; `isAdmin` derived from user's public metadata role
- [x] 7.5 Create `frontend/src/lib/RequireAuth.tsx` and `RequireAdmin.tsx` — route guard components that redirect to sign-in if unauthenticated/unauthorized
- [x] 7.6 Implement `POST /webhooks/clerk` in `backend/app/api/webhooks.py` — SVIX signature verification, upsert user record in `users` table on `user.created` / `user.updated` events
- [x] 7.7 Wire Clerk JWT auth middleware to all protected backend routes (listing create, document upload, admin routes)
- [x] 7.8 Write integration tests: protected routes return 401 without token, 403 for wrong role

---

### 8. Map Discovery UI (Frontend)

- [x] 8.1 Install frontend dependencies: `@react-google-maps/api`, `zustand`, `@tanstack/react-query`, `react-router-dom`, `recharts`
- [x] 8.2 Create `frontend/src/stores/mapStore.ts` — Zustand store with bounds, center, zoom, activeFilters, searchQuery, selectedListingId, comparisonTray
- [x] 8.3 Create `frontend/src/lib/api.ts` — axios/fetch API client with base URL from env, JWT header injection from Clerk session
- [x] 8.4 Create `frontend/src/hooks/useSearch.ts` — TanStack Query hook wrapping `POST /search`
- [x] 8.5 Create `frontend/src/hooks/useListing.ts` — TanStack Query hook wrapping `GET /listings/{id}`
- [x] 8.6 Create `frontend/src/pages/DiscoverPage.tsx` — split-view layout: 60% map / 40% card panel on desktop; stacked + bottom sheet on mobile
- [x] 8.7 Create `frontend/src/components/map/MapView.tsx` — Google Maps wrapper with `@react-google-maps/api`; renders custom color-coded `ListingPin` markers; fires `setBounds` on pan/zoom
- [x] 8.8 Create `frontend/src/components/map/ListingPin.tsx` — custom marker: green (≥80), yellow (50–79), red (<50), grey (no score)
- [x] 8.9 Create `frontend/src/components/map/SearchAreaButton.tsx` — appears after map pan; triggers new search with current bounds
- [x] 8.10 Create `frontend/src/components/listing/ListingCard.tsx` — glass card: price, area, locality, ConfidenceScoreBadge, up to 2 RiskFlagPills, Analyze button
- [x] 8.11 Create `frontend/src/components/listing/SkeletonCard.tsx` — loading skeleton matching ListingCard dimensions
- [x] 8.12 Create `frontend/src/components/search/SearchBar.tsx` — NL text input with submit; updates `mapStore.searchQuery`
- [x] 8.13 Create `frontend/src/components/search/FilterPanel.tsx` — collapsible panel: price range, area range, locality multi-select, use type, confidence threshold slider
- [x] 8.14 Create `frontend/src/components/ui/DisclaimerBanner.tsx` — non-dismissible banner with 4 variants (score/price/document/growth); uses design system tokens
- [x] 8.15 Add `DisclaimerBanner variant="score"` to `DiscoverPage` below the search bar
- [x] 8.16 Update `frontend/src/App.tsx` — add React Router `<BrowserRouter>` with routes: `/`, `/discover`, `/listings/:id`, `/sell`, `/admin`, `/legal`
- [x] 8.17 Write component tests: ListingCard renders all fields; SkeletonCard renders during loading; DisclaimerBanner shows correct text per variant

---

## Phase 2 — Intelligence Layer

### 9. Confidence Score Engine (Backend + Celery)

- [x] 9.1 Create `backend/app/workers/score_tasks.py` — Celery task `compute_confidence_score_task(listing_id)`: loads listing state, calls `confidence_engine.compute_confidence_score()`, updates `listings.confidence_score` and `listings.confidence_breakdown`, sets `listing_status` per threshold rules
- [x] 9.2 Create `backend/app/workers/embedding_tasks.py` — Celery task `generate_embedding_task(listing_id)`: generates embedding via `EmbeddingService`, stores in `listings.embedding`
- [x] 9.3 Wire listing creation (`POST /listings`) to enqueue both `generate_embedding_task` and `compute_confidence_score_task` after DB insert
- [x] 9.4 Wire document upload to enqueue `compute_confidence_score_task` after analysis completes (recompute doc completeness dimension)
- [x] 9.5 Implement stale listing detection: Celery beat task running daily, sets `stale` RiskFlag on listings with `last_confirmed_at` > 60 days
- [x] 9.6 Create `backend/app/api/listings.py` — add `GET /listings/{id}/score` endpoint returning `ConfidenceBreakdown`
- [x] 9.7 Write unit tests: each scorer with boundary inputs (0 docs, all docs, KYC verified/none, duplicate hash match, price at Z=2.0 boundary, freshness at 0/30/60/90 days)

---

### 10. Legal Document Analyzer (Backend + AI)

- [x] 10.1 Create `ai/chains/document_analyzer.py` — orchestrates pdfplumber/pytesseract OCR + Groq LLM extraction against `DocumentAnalysis` schema
- [x] 10.2 Create `backend/app/services/document_service.py` — handles file upload to R2, invokes `document_analyzer`, stores result in `listing_documents`
- [x] 10.3 Create `backend/app/api/documents.py` — `POST /listings/{id}/documents` route handler accepting `UploadFile` (authenticated sellers only)
- [x] 10.4 Write tests: verify `sanitize_for_llm` function successfully strips all mocked KYC fields (Aadhaar, PAN) from JSON inputs before LLM serialization
- [x] 10.5 Write component tests for Legal Tab UI verifying JSON data mapping

---

### 11. Listing Detail Page (Frontend — 7 Tabs)

- [x] 11.1 Create `frontend/src/pages/ListingDetailPage.tsx` — fetches listing detail, score, documents, price estimate, POIs, growth signals via TanStack Query hooks; renders `BreadcrumbNav` + `ListingHeader` + `TabNav`
- [x] 11.2 Create `frontend/src/components/listing/BreadcrumbNav.tsx` — "← Back to map" link navigating to `/discover` without resetting Zustand mapStore
- [x] 11.3 Create `frontend/src/components/listing/ListingHeader.tsx` — title, locality, price, area, verification badge (Full/Partial/Unverified)
- [x] 11.4 Create `frontend/src/components/listing/tabs/OverviewTab.tsx` — plot summary, OwnerInfoCard (verified/unverified badge), listing age in days, ThumbnailMap (static Google Maps embed)
- [x] 11.5 Create `frontend/src/components/listing/tabs/AIScoreTab.tsx` — `ConfidenceRadialChart` (Recharts RadialBarChart), 6 `DimensionBreakdown` rows, `DisclaimerBanner variant="score"`
- [x] 11.6 Create `frontend/src/components/listing/tabs/LegalDocsTab.tsx` — `DocumentUploadTracker` (status per doc type), `DocumentSummaryCard` per uploaded doc, `DisclaimerBanner variant="document"`
- [x] 11.7 Create `frontend/src/components/listing/tabs/PriceIntelligenceTab.tsx` — `PriceRangeCard` (P10–P90), `ComparablesList`, `PriceTrendChart` (Recharts LineChart), `PricingFlagBadge`, `NegotiationRangeCard`, `DisclaimerBanner variant="price"`
- [x] 11.8 Create `frontend/src/components/listing/tabs/LocationIntelligenceTab.tsx` — satellite/hybrid toggle, `POIOverlayControls` checkboxes, `POIMarkers`, `DistanceSummaryTable`, `FloodRiskOverlay` (static GeoJSON)
- [x] 11.9 Create `frontend/src/components/listing/tabs/FutureGrowthTab.tsx` — `GrowthTierBadge`, `GrowthSignalCard` per signal, `DisclaimerBanner variant="growth"`
- [x] 11.10 Create `frontend/src/components/listing/tabs/RiskSummaryTab.tsx` — top 3 `RiskFlagCard` with severity, `MissingDocChecklist`, `FraudSignalReport`
- [x] 11.11 Write component tests: each tab renders DisclaimerBanner; BreadcrumbNav preserves mapStore state on navigation

---

### 12. Price Intelligence (Backend)

- [x] 12.1 Create `backend/app/services/price_service.py` — `PriceService`: `estimate(listing_id)` returns P10/P50/P90 via bootstrap resampling (100 samples) on Ridge model; `get_comparables(listing_id)` PostGIS radius + 20% area tolerance; `get_price_trend(locality)` median price/sqyd by month; `classify_price()` P25/P75 thresholds; `compute_negotiation_range()` P25–P50 × area
- [x] 12.2 Create `backend/app/api/listings.py` — add `GET /listings/{id}/price-estimate` endpoint returning full `PriceEstimate` response shape
- [x] 12.3 Write PBT: `test_price_classification_matches_percentiles` — Property 7: overpriced/underpriced/fair matches P25/P75 (Hypothesis, 100 examples)
- [x] 12.4 Write PBT: `test_negotiation_range_formula` — Property 8: range equals [P25×area, P50×area] in lakhs (Hypothesis, 100 examples)
- [x] 12.5 Write unit tests: price model predictions are within expected range on seed data; comparables query returns 5–10 results within 20% area tolerance

---

### 13. Seller Listing Creation (Frontend + Backend)

- [ ] 13.1 Create `backend/app/api/listings.py` — `POST /listings`: requires auth, validates `tos_accepted=true` (HTTP 400 if missing), rate-limits 5/seller/24h (HTTP 429), inserts listing, enqueues embedding + score tasks
- [ ] 13.2 Create `frontend/src/pages/SellerPage.tsx` — multi-step form wrapped in `<RequireAuth>`
- [ ] 13.3 Create `frontend/src/components/seller/Step1LocationPicker.tsx` — Google Maps pin drop, captures lat/lng
- [ ] 13.4 Create `frontend/src/components/seller/Step2PlotDetails.tsx` — size, price, use type, ownership type fields with validation
- [ ] 13.5 Create `frontend/src/components/seller/Step3DocumentUpload.tsx` — file upload for EC, Sale Deed, photos; shows upload progress
- [ ] 13.6 Create `frontend/src/components/seller/SubmissionResult.tsx` — shows preliminary confidence score and fix prompts after submission
- [ ] 13.7 Write integration tests: TOS not accepted returns 400; 6th listing in 24h returns 429; successful submission enqueues Celery tasks
- [x] 13.1 Create `frontend/src/pages/SellerDashboard.tsx` — basic form mapping to `ListingCreate` schema, triggers `POST /listings`, handles success/error states
- [x] 13.2 Create `frontend/src/components/seller/Step1LocationPicker.tsx` — Google Maps pin drop, captures lat/lng
- [x] 13.3 Create `frontend/src/components/seller/Step2PlotDetails.tsx` — size, price, use type, ownership type fields with validation
- [x] 13.4 Create `frontend/src/components/seller/Step3DocumentUpload.tsx` — file upload for EC, Sale Deed, photos; shows upload progress
- [x] 13.5 Create `frontend/src/components/seller/SubmissionResult.tsx` — shows preliminary confidence score and fix prompts after submission
- [x] 13.6 Write integration tests: TOS not accepted returns 400; 6th listing in 24h returns 429; successful submission enqueues Celery tasks

---

### 14. Admin Trust Dashboard (Frontend + Backend)

- [x] 14.1 Create `frontend/src/pages/AdminDashboard.tsx` — table of pending/live listings, requires Clerk admin role
- [x] 14.2 Create `backend/app/api/admin.py` — `GET /admin/queue` (returns pending listings), `POST /admin/action` (approve/reject/takedown)
- [x] 14.3 Create `backend/app/services/admin_service.py` — `AdminService`: handles manual status overrides, updates `listings.listing_status`, logs action to `audit_log`
- [x] 14.4 Write PBT: `test_audit_log_capture` — Property 10: any admin status change produces exactly one AuditLog entry (Hypothesis, 100 examples)
- [x] 14.5 Write integration test: non-admin user receives 403 Forbidden on `/admin/*` routes; admin action creates audit_log entry

---

## Phase 3 — Location & Geospatial Intelligence

### 15. POI Overlay and Location Intelligence (Backend)

- [ ] 15.1 Create `backend/app/services/poi_service.py` — `POIService.get_pois(lat, lng)`: Overpass API query (5km radius, 6 categories), great-circle distance calculation per POI, 10s timeout with cached/empty fallback (no 5xx)
- [ ] 15.2 Create `backend/app/api/listings.py` — add `GET /listings/{id}/pois` endpoint; cache results in Redis (TTL 1 hour)
- [ ] 15.3 Add static `frontend/public/hyderabad_flood_zones.geojson` — Hyderabad NDMA flood hazard zone data
- [ ] 15.4 Update `LocationIntelligenceTab` — wire `useListingPOIs` TanStack Query hook; render POI markers with category icons; render flood GeoJSON layer; implement satellite/hybrid map toggle
- [ ] 15.5 Create `frontend/src/hooks/useListingPOIs.ts` — TanStack Query hook wrapping `GET /listings/{id}/pois`
- [ ] 15.6 Write unit tests: Overpass timeout returns `{pois: {}, error: "overpass_unavailable"}` without 5xx; distance calculation correct for known lat/lng pairs

---

### 16. Future Growth Signals (Backend + Frontend)

- [ ] 16.1 Create `backend/app/services/growth_service.py` — `GrowthService.get_signals(listing_id)`: PostGIS spatial join (listing point within 10km of signal polygon), growth tier label assignment (High/Emerging/Speculative)
- [ ] 16.2 Create `backend/app/api/listings.py` — add `GET /listings/{id}/growth-signals` endpoint
- [ ] 16.3 Add validation in `GrowthSignal` model: reject insert if `status="announced"` and `source_url` is null
- [ ] 16.4 Create `frontend/src/hooks/useGrowthSignals.ts` — TanStack Query hook wrapping `GET /listings/{id}/growth-signals`
- [ ] 16.5 Wire `FutureGrowthTab` to `useGrowthSignals` hook; render `GrowthTierBadge` and `GrowthSignalCard` list
- [ ] 16.6 Write PBT: `test_growth_tier_label` — Property 10: tier label matches approved/under_construction signal count rules (Hypothesis, 100 examples)
- [ ] 16.7 Write unit tests: spatial join returns correct signals for known listing coordinates; "announced" signal without source_url is rejected

---

### 17. Legal Page and Report Listing

- [ ] 17.1 Create `frontend/src/pages/LegalPage.tsx` — Terms of Service, Privacy Policy, Disclaimer inventory (all 4 variants), Grievance contact
- [ ] 17.2 Create `backend/app/api/listings.py` — add `POST /listings/{id}/report` endpoint (auth required); inserts grievance record; returns `{report_id, status: "received"}`
- [ ] 17.3 Add "Report this listing" button to `ListingDetailPage` (visible to authenticated users)

---

### 18. Error Handling, Logging, and Rate Limiting

- [ ] 18.1 Add global FastAPI exception handler returning consistent `{error: {code, message, details}}` JSON envelope for all error types
- [ ] 18.2 Add structured JSON request logging middleware (method, path, status, response_time_ms) to `backend/app/main.py`
- [ ] 18.3 Implement per-IP rate limiting (60 req/min) using Redis sliding window; return HTTP 429 with `Retry-After` header
- [ ] 18.4 Add `GET /health` dependency status check for Postgres, Redis, and R2; return 503 with named unavailable dependency
- [ ] 18.5 Add Celery task retry logic: `autoretry_for=(Exception,)`, `max_retries=3`, exponential backoff on all worker tasks
- [ ] 18.6 Write integration tests: 503 response when DB is unreachable; 429 after rate limit exceeded; error envelope shape is consistent across all error types

---

## Cross-Cutting

### 19. Design System Consistency Audit

- [ ] 19.1 Audit all new page components — verify `glass-card`, `btn-primary`, `btn-secondary` CSS classes are used consistently; no inline styles override design tokens
- [ ] 19.2 Verify all new pages use Inter font, correct weight scale, and WCAG 2.1 AA contrast ratios on dark background
- [ ] 19.3 Verify all entrance animations use Framer Motion `motion` package following stagger-in pattern from existing components
- [ ] 19.4 Verify `DisclaimerBanner` is present and non-dismissible on every tab/page that renders AI output (score, price, document, growth)

---

### 20. End-to-End Smoke Test

- [ ] 20.1 Manual walkthrough: homepage → `/discover` → type NL query → map loads with pins → click listing card → listing detail page opens → all 7 tabs render without errors
- [ ] 20.2 Manual walkthrough: sign in with Google → navigate to `/sell` → complete 3-step form → submit → see confidence score result
- [ ] 20.3 Manual walkthrough: sign in as admin → navigate to `/admin` → see metrics panel and verification queue → perform approve action → verify audit log entry created
- [ ] 20.4 Verify video plays on landing page Hero from local file (not CDN)
- [ ] 20.5 Verify all DisclaimerBanners are visible and non-dismissible across all AI-output pages

---

*Tasks version: 1.0 — PlotIQ POC Phases 0–3*
*Total tasks: 20 parent tasks, ~100 sub-tasks*
*Ordering: dependency-safe (each task only depends on earlier tasks)*
*PBT coverage: Properties 1–11 embedded in tasks 3, 4, 9, 12, 16*
