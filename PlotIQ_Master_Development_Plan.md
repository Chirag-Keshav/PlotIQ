# PlotIQ — AI-Powered Land Discovery & Verification Platform
## Master Development Plan (POC → Production)

> **Positioning:** "AI-assisted land due diligence and discovery" — not another property portal.
> **Target V1 Geography:** Hyderabad, Telangana (ORR belt, Kokapet, Shadnagar, Adibatla, Patancheru, Ibrahimpatnam, Sangareddy corridor)

---

## 1. PRODUCT OVERVIEW & STRUCTURAL HIERARCHY

```
PlotIQ
├── Core Problem Being Solved
│   ├── Fake listings & fraud
│   ├── Pricing opacity
│   ├── Legal confusion (EC, sale deed, approvals)
│   ├── Poor location decision-making
│   ├── Broker dependency
│   └── Low transparency in land transactions
│
├── Product Layers
│   ├── DISCOVERY LAYER      → Find the right plot (map, semantic search, filters)
│   ├── INTELLIGENCE LAYER   → Understand the plot (scores, comps, growth signals)
│   ├── VERIFICATION LAYER   → Trust the plot (fraud, docs, legal, KYC)
│   └── DECISION LAYER       → Act on the plot (negotiation, agent, comparison)
│
└── User Roles
    ├── Buyer / Investor        → Primary user
    ├── Seller / Owner          → Lists plots, uploads docs
    ├── Admin / Ops             → Verifies, moderates, manages trust queue
    └── AI Agent (internal)     → Scores, analyzes, flags, recommends
```

---

## 2. COMPLETE USER FLOWS (Start → End)

### 2A. BUYER FLOW

```
[ENTRY]
  → Land on homepage / app
  → Optional: sign up / login (email, Google, phone OTP)

[DISCOVERY]
  → Type natural language query OR use filters
     e.g. "Plots near Hyderabad ORR under 40 lakhs for warehouse"
  → AI parses intent: budget, location, use-case, size range, road access
  → Map loads with pins + split listing-card panel (Zillow-style)
  → Pins color-coded by confidence score (green / yellow / red)
  → Cards show: Price, Size, Confidence Score, 2–3 risk badges, "Analyze" CTA

[SHORTLISTING]
  → Click a card → Side drawer opens (progressive reveal)
  → Drawer shows: thumbnail map, price, score, top 3 risk/verification signals
  → User clicks "Full Analysis" → navigates to Listing Detail Page

[LISTING DETAIL PAGE — the core product]
  ├── Tab 1: Overview
  │   └── Plot summary, owner info (verified/unverified), listing age, location
  ├── Tab 2: AI Confidence Score
  │   └── Breakdown: doc completeness, owner KYC, geo consistency, duplicate check
  │   └── Score out of 100, each sub-score with explanation
  │   └── Disclaimer: "Model estimate — not a legal certification"
  ├── Tab 3: Legal & Documents
  │   └── Upload status: EC, Sale Deed, Layout Approval, Mutation, Encumbrance
  │   └── AI summary of each doc: entities, risks, missing approvals, red flags
  │   └── Disclaimer: "This is AI-generated — consult a lawyer for title certainty"
  ├── Tab 4: Price Intelligence
  │   └── Estimated fair value range (ML model)
  │   └── Comparable plots sold nearby (last 6–12 months)
  │   └── Price trend chart for the micro-market
  │   └── Overpriced / underpriced flag with explanation
  │   └── Negotiation range suggestion
  ├── Tab 5: Location Intelligence
  │   └── Satellite map overlay: water bodies, highways, flood zones
  │   └── Distances: ORR, NH, metro, airport, hospitals, schools
  │   └── Road access score
  │   └── Land use classification (residential / agricultural / commercial)
  ├── Tab 6: Future Growth
  │   └── Nearby approved/under-construction projects (government sources)
  │   └── Infrastructure announcements (HMDA, NHAI, TSRTC, HMRL)
  │   └── Growth tier: High / Medium / Speculative (with source + date)
  └── Tab 7: Risk Summary
      └── Top 3 risks with severity + explanation
      └── Missing document checklist
      └── Fraud signal report (if any)

[ACTION]
  → Save to watchlist
  → Request seller contact (gated post-verification)
  → Chat with AI agent: "Should I buy this plot?"
  → Download due-diligence summary PDF (optional premium)
  → Compare with up to 3 other plots side-by-side

[POST-DECISION]
  → User can mark plot as "Under Negotiation" / "Purchased"
  → Rate and review seller after transaction
```

### 2B. SELLER / OWNER FLOW

```
[ONBOARDING]
  → Register with phone OTP + Aadhaar/PAN (KYC)
  → Agree to listing terms and data usage policy

[LISTING CREATION]
  → Enter basic details: location (pin on map), size, price, use type
  → Upload documents: EC, sale deed, layout approval, photos
  → AI instantly runs:
      - Duplicate image check
      - Phone number cross-reference
      - Document entity extraction
      - Price anomaly check
  → Receives preliminary confidence score
  → Prompted to fix any issues before publishing

[VERIFICATION PIPELINE]
  → Tier 1: Self-serve auto-check (AI)
  → Tier 2: Human review flag (if AI confidence < threshold or fraud signals)
  → Tier 3: Full manual verification for "Fully Verified" badge

[LIVE LISTING]
  → Listing goes live with verified/partial badge
  → Seller notified when inquiries arrive
  → Periodic re-confirmation prompts (60-day freshness cycle)
```

### 2C. ADMIN / OPS FLOW

```
[TRUST DASHBOARD]
  → Queue: flagged listings (fraud signals, duplicate images, strange pricing)
  → Actions: approve, request more docs, reject, mark as scam
  → Metrics: verification rate, fraud catch rate, stale listing count

[MODERATION]
  → Takedown requests from buyers
  → False-listing reports
  → Dispute resolution interface
```

---

## 3. FEATURES — ORDERED BY POC IMPLEMENTATION PRIORITY

| Priority | Feature | Why First | POC Scope |
|----------|---------|-----------|-----------|
| 1 | **Curated Hyderabad listing dataset** (50–100 plots) | Nothing works without data | Seed 50 demo plots with realistic fields |
| 2 | **Map-first UI (Zillow split-view)** | Core UX; everything else builds on it | Map + cards + pins colored by score |
| 3 | **Natural language / semantic search** | Primary differentiator vs. 99acres | LLM parses query → filters → semantic ranking |
| 4 | **AI Confidence Score** | The trust anchor of the product | Rule-based + ML scoring over demo data fields |
| 5 | **Listing detail page with tabs** | Where the intelligence lives | 7-tab detail page with mock + real AI outputs |
| 6 | **Legal Document Analyzer** | Strongest differentiator, hackathon wow factor | Upload PDF → LLM extracts entities, risk flags |
| 7 | **Price Estimation** | Zillow-equivalent for land | Regression over demo comps + location features |
| 8 | **Location Intelligence (map overlay)** | High visual impact, clearly differentiated | Google Maps + Overpass API for nearby POIs |
| 9 | **Future Growth Signals** | Investors love this | Curated HMDA/NHAI project list + news tags |
| 10 | **Fraud Detection** | Critical for trust narrative | Duplicate image hash, phone reuse, price anomaly |
| 11 | **Seller onboarding mock flow** | Answers "how do listings get in?" | Simplified form + doc upload + instant AI check |
| 12 | **Admin trust dashboard (demo)** | Shows operational maturity | Static + partially live verification queue |
| 13 | **Conversational AI agent ("Should I buy?")** | High wow-factor, clear differentiator | RAG over listing data + Claude API |
| 14 | **Negotiation assistant** | Unique feature | Simple comparable-based offer range |
| 15 | **Compare plots side-by-side** | Buyer utility | Up to 3 plots, tabular comparison |
| 16 | **Watchlist / Save** | Retention feature | User profile + saved listings |
| 17 | **Due diligence PDF export** | Premium/monetization signal | PDF render of detail page tabs |
| 18 | **Recommendation engine** | Personalized discovery | Embeddings-based similarity + user profile |

---

## 4. TECH STACK

### 4A. FRONTEND

| Component | Technology | Reason |
|-----------|-----------|--------|
| Framework | **Next.js 14 (App Router)** | SSR for SEO, fast navigation, great DX |
| UI Library | **shadcn/ui + Tailwind CSS** | Composable, accessible, unstyled-to-styled |
| Map | **Mapbox GL JS** or **Google Maps JS API** | Mapbox preferred for custom pin styling and split-view; Google Maps if budget is tight and familiarity helps |
| Map overlays | **deck.gl** or **Mapbox Layers** | Satellite heatmaps, flood zone overlays, growth corridors |
| State management | **Zustand** | Lightweight, good for map + search state |
| Data fetching | **TanStack Query (React Query)** | Caching, background refetch for listings |
| Charts/graphs | **Recharts** | Price trend charts, score breakdowns |
| Document upload | **react-dropzone** | Drag-and-drop doc upload for seller flow |
| Forms | **React Hook Form + Zod** | Type-safe forms with validation |
| Auth UI | **Clerk** or **NextAuth.js** | Phone OTP + Google sign-in |

### 4B. BACKEND

| Component | Technology | Reason |
|-----------|-----------|--------|
| API Framework | **FastAPI (Python)** | Best for ML/AI-heavy backends; async support |
| ORM | **SQLAlchemy + Alembic** | Migrations, relation modeling |
| Primary DB | **PostgreSQL + PostGIS** | Relational data + geospatial queries (radius search, polygon overlays) |
| Vector DB | **Pinecone** or **pgvector** (Postgres extension) | Semantic search embeddings; pgvector avoids extra infra for POC |
| File Storage | **AWS S3** or **Cloudflare R2** | Document uploads, listing images |
| Cache | **Redis** | Search result caching, session tokens |
| Task Queue | **Celery + Redis** | Async document analysis, fraud checks, score generation |
| Auth Backend | **Clerk** (preferred) or custom JWT | Phone OTP + Google, session management |
| Search | **pgvector** (POC) → **Elasticsearch** (scale) | Vector similarity for semantic search; Elasticsearch for full-text at scale |

### 4C. AI / ML LAYER

| Component | Technology | Reason |
|-----------|-----------|--------|
| Primary LLM | **Claude API (claude-sonnet-4-6)** | Document analysis, conversational agent, NL query parsing |
| Embeddings | **OpenAI text-embedding-3-small** or **Cohere embed-v3** | Semantic search over listings |
| Orchestration | **LangChain** (simple chains) or **LangGraph** (agent loops) | Multi-step document analysis pipeline, conversational agent with memory |
| Document OCR | **AWS Textract** or **Google Document AI** | Extract text from scanned EC/sale-deed PDFs |
| Image hashing (fraud) | **ImageHash** (Python library) | Perceptual hash for duplicate image detection |
| Price prediction | **scikit-learn (Ridge/XGBoost)** → **LightGBM** at scale | Regression over location features, size, comparable sales |
| MCP Server (internal) | **Custom FastMCP server** | Expose tools: `search_listings`, `analyze_document`, `score_listing`, `get_area_signals`, `find_comparables` — so AI agent can call them |
| Satellite/geo analysis | **Google Earth Engine API** (free tier) or **Sentinel Hub** | Urbanization growth, NDVI, land classification |

### 4D. GEOSPATIAL & DATA

| Component | Technology | Reason |
|-----------|-----------|--------|
| Map tiles | **Mapbox** or **Google Maps Platform** | Base map + satellite hybrid |
| Geocoding | **Google Geocoding API** | Address → lat/lng conversion |
| POI data | **Overpass API (OpenStreetMap)** | Schools, hospitals, highways near any plot — free |
| Government data | **HMDA portal, RERA Telangana, NHAI tender portal** | Approved projects, planning notifications |
| Infrastructure news | **NewsAPI** or **Google News RSS** | Curated news parsing for growth signal tagging |
| Land records | **Dharani portal (Telangana)** | Public land registry data (manual integration for POC) |
| Flood/risk data | **NDMA flood hazard maps** | Risk zone overlays |

### 4E. INFRASTRUCTURE & DEVOPS

| Component | Technology | Reason |
|-----------|-----------|--------|
| Hosting (backend) | **Railway** or **Render** (POC) → **AWS ECS** (prod) | Easy deploy for POC, scalable path to prod |
| Hosting (frontend) | **Vercel** | Native Next.js support, free tier for POC |
| CI/CD | **GitHub Actions** | Automated tests, lint, deploy |
| Monitoring | **Sentry** (errors) + **PostHog** (analytics) | Error tracking + user behavior |
| Secret management | **doppler** or **AWS Secrets Manager** | API keys, DB creds |
| Database hosting | **Supabase** (POC) → **AWS RDS** (prod) | Postgres + PostGIS with GUI, free tier |

### 4F. COMPLIANCE TOOLING

| Component | Technology | Reason |
|-----------|-----------|--------|
| Privacy / consent | Custom consent banner + DPDPA checklist | Indian Digital Personal Data Protection Act compliance |
| Terms / disclaimers | Legal disclaimer system in UI | Required for AI score, price estimate, doc analysis outputs |
| Audit logs | Postgres audit log table | Track who accessed/modified listings and docs |
| Rate limiting | **Upstash Rate Limit** (Redis-based) | Prevent abuse of document upload / AI endpoints |

---

## 5. PHASE-WISE DEVELOPMENT PLAN

---

### PHASE 0 — FOUNDATION (Week 1)
**Goal:** Repo, data, and infrastructure ready. Zero visible product.

#### 0.1 — Project Setup
- [ ] Initialize monorepo: `/frontend` (Next.js), `/backend` (FastAPI), `/ai` (LangChain/MCP tools)
- [ ] Set up GitHub repo with branch protection + PR templates
- [ ] Configure GitHub Actions CI: lint (ESLint, Ruff), type-check (mypy, tsc), test (pytest, vitest)
- [ ] Set up Vercel (frontend) + Railway/Render (backend) with auto-deploy from `main`
- [ ] Configure Supabase (Postgres + PostGIS extension enabled)
- [ ] Configure Redis (Upstash free tier for POC)
- [ ] Set up S3/R2 bucket for document and image uploads
- [ ] Add secret management (doppler or .env.local + GitHub secrets)

#### 0.2 — Seed Dataset
- [ ] Design listing schema (see below)
- [ ] Create 50–80 seeded Hyderabad plots across 6–8 localities
- [ ] Each listing must have: `lat, lng, price_lakhs, area_sqyd, owner_type, road_access, listing_age, doc_status (EC/deed/approval), mock_confidence_score, risk_flags[], growth_signals[]`
- [ ] Import into Postgres + generate embeddings for each listing (store in pgvector)
- [ ] Validate PostGIS queries: radius search, bounding box, nearest-N

#### 0.3 — Compliance Baseline (start here, not later)
- [ ] Draft Terms of Service with these mandatory disclaimers:
  - AI confidence score ≠ legal title certification
  - Price estimates are model outputs, not guarantees
  - Document analysis ≠ lawyer opinion
  - Growth signals marked by source type + date + confidence
- [ ] Privacy policy covering: personal data collected, document uploads, third-party APIs used
- [ ] Decide: are you a classifieds-tech platform (safer) or a broker/agent (triggers RERA)?
- [ ] Add "Report a listing" and "Grievance" contact infrastructure (required for IT platform liability)
- [ ] Review Mapbox/Google Maps licensing terms for data caching and display rules

---

### PHASE 1 — CORE DISCOVERY (Weeks 2–3)
**Goal:** Map + search working. Users can find plots. First visible product.

#### 1.1 — Map UI (Frontend)
- [ ] Build split-view layout: map left (60%), listing cards right (40%), mobile-responsive stacked
- [ ] Integrate Mapbox GL JS with custom pin markers
- [ ] Pin colors: green (score 80+), yellow (50–79), red (<50), grey (unscored)
- [ ] Map bounds control: listing cards update as user pans/zooms
- [ ] "Search this area" button when map is moved
- [ ] Listing card component: price, area, locality, confidence score badge, 2 risk pills, "Analyze" button
- [ ] Loading skeleton states for cards and map pins
- [ ] Mobile: bottom sheet replaces right panel

#### 1.2 — Search & Filtering (Backend + Frontend)
- [ ] Build natural language query parser (LangChain + Claude):
  - Input: "Plots near Hyderabad ORR under 40 lakhs for warehouse"
  - Output: `{budget_max: 40, location_hint: "ORR", use_type: "commercial", road_access: "highway"}`
- [ ] Build filter-to-SQL converter (structured filters → PostGIS query)
- [ ] Semantic search: embed query → cosine similarity over pgvector listing embeddings
- [ ] Combine: structured filter (hard constraints) + semantic ranking (soft relevance)
- [ ] API: `POST /search` → returns ranked listings with scores
- [ ] Frontend: search bar with NL input + collapsible filter panel (price range, size, locality, use type, score threshold)

#### 1.3 — Authentication
- [ ] Implement Clerk or NextAuth with:
  - Google OAuth
  - Phone OTP (required for seller flow)
- [ ] Protected routes: seller onboarding, watchlist, contact requests
- [ ] User profile table in Postgres

**Compliance checkpoint:**
- Ensure search does not expose PII (phone, Aadhaar) in listing cards
- All API endpoints rate-limited
- HTTPS enforced everywhere

---

### PHASE 2 — INTELLIGENCE LAYER (Weeks 4–5)
**Goal:** The AI confidence score and listing detail page are live. This is the product's core differentiator.

#### 2.1 — Confidence Score Engine (Backend)
- [ ] Define scoring dimensions and weights:
  ```
  Document completeness:   25%
  Owner KYC status:        20%
  Geo-location consistency: 15%
  Duplicate detection:     20%
  Pricing anomaly check:   10%
  Listing freshness:       10%
  ```
- [ ] Implement each sub-scorer as a Python function in `/ai/scorers/`
- [ ] Duplicate image detection: perceptual hash (ImageHash) comparison against all listing images in DB
- [ ] Phone number reuse: check same phone used in >N listings
- [ ] Price anomaly: Z-score vs. median price per locality/sqyd
- [ ] Celery task: run scoring pipeline on listing creation and on doc upload
- [ ] Store scores in Postgres with per-dimension breakdown (JSON field)

#### 2.2 — Legal Document Analyzer (Backend + AI)
- [ ] Build document upload endpoint: `POST /listings/{id}/documents`
  - Accept PDF, JPG, PNG
  - Store in S3/R2, reference in DB
- [ ] OCR pipeline: if scanned → AWS Textract → extracted text
- [ ] LangChain document analysis chain:
  - Prompt: extract entities (parties, survey numbers, dates, amounts), identify risk clauses, list missing approvals, flag suspicious language
  - Structured output schema (Pydantic)
- [ ] Document types to handle: EC (Encumbrance Certificate), Sale Deed, Layout Approval, Mutation Register, Patta
- [ ] Store analysis output in Postgres (JSON)
- [ ] **Critical disclaimer on every output:** "AI-generated summary only. Consult a licensed lawyer for legal advice and title verification."

#### 2.3 — Listing Detail Page (Frontend)
- [ ] 7-tab detail page (see Section 2A for full tab spec)
- [ ] Confidence score visualization: radial chart with sub-dimension breakdown
- [ ] Document section: upload status tracker, AI summary per document
- [ ] Risk badges: colored pills with severity (high/medium/low)
- [ ] "Analyze Plot" primary CTA
- [ ] Side drawer (progressive reveal on card click) → Full page navigation
- [ ] Breadcrumb and back-to-map navigation

#### 2.4 — Price Intelligence (Backend + ML)
- [ ] Build price estimation model:
  - Features: locality, size (sqyd), road access type, distance to ORR, distance to highway, land use, doc completeness score, listing age
  - Model: scikit-learn Ridge regression trained on seed data (expand with synthetic comparables)
  - Output: estimated fair value range (P10–P90 confidence interval)
- [ ] Comparable plots query: nearest 5–10 sold/listed plots by geo + size
- [ ] Price trend: aggregate by locality + month (even if seeded) → line chart
- [ ] Negotiation range: P25–P50 of comparables as suggested offer
- [ ] **Required disclaimer on all price outputs:** "Estimated range based on model. Not a valuation."

**Compliance checkpoint:**
- No document content sent to LLM without user consent checkbox
- AI outputs labelled as "AI-generated" in UI
- Price/score disclaimers visible and non-skippable on first view

---

### PHASE 3 — LOCATION & GEOSPATIAL INTELLIGENCE (Week 6)
**Goal:** Map overlays and future growth signals distinguish PlotIQ visually and analytically.

#### 3.1 — Location Intelligence Layer (Frontend + Backend)
- [ ] Satellite/hybrid map toggle on listing detail page
- [ ] POI overlay using Overpass API (OpenStreetMap):
  - Schools, hospitals, malls, metro stations, highways, bus depots
  - Show within 5km radius, filterable by type
- [ ] Distance calculator: plot lat/lng → great-circle distance to key infrastructure
- [ ] Road access score: based on OSM road classification within 500m
- [ ] Flood risk: NDMA hazard zone layer overlay (static GeoJSON for Hyderabad)
- [ ] Land use classification: color overlay from Telangana master plan GeoJSON (if available publicly)

#### 3.2 — Future Growth Signals (Backend + AI)
- [ ] Build a growth signal database table: `{signal_type, title, source_url, source_type, date_announced, status (announced/approved/under-construction/operational), location_polygon, confidence}`
- [ ] Populate with curated Hyderabad infrastructure projects:
  - HMDA approved layouts near ORR corridors
  - NHAI highway projects (NH-44, NH-65, ORR Phase II)
  - TSRTC/HMRL metro extensions
  - Industrial parks (Fab City, Genome Valley, Adibatla aerospace)
- [ ] NewsAPI integration (optional for POC): fetch infrastructure news → Claude tags status type + location
- [ ] Plot-level growth signal matching: spatial join of signal polygons to listing location
- [ ] Growth tier labels: "High growth corridor" / "Emerging zone" / "Speculative" — each with source + date
- [ ] **Required disclaimer:** "Growth signals are based on announced/approved projects. Outcomes depend on execution. Not investment advice."

---

### PHASE 4 — VERIFICATION & TRUST LAYER (Week 7)
**Goal:** Seller onboarding and admin trust dashboard demonstrate the operational backbone.

#### 4.1 — Seller Onboarding Flow (Frontend + Backend)
- [ ] Multi-step form:
  - Step 1: Phone OTP login
  - Step 2: Owner KYC (Aadhaar number + PAN — masked and hashed, not stored in plain text)
  - Step 3: Plot details (lat/lng pin drop, size, price, use type, ownership type)
  - Step 4: Document upload (EC, sale deed, photos)
  - Step 5: AI pre-check results shown with fix prompts
  - Step 6: Listing preview before submission
- [ ] Instantly run confidence score and fraud checks on submission
- [ ] If score > 70: auto-publish with "AI Verified" badge
- [ ] If score 40–70: publish with "Partial Verification" badge + flag for human review
- [ ] If score < 40 or fraud signals: hold for manual review

#### 4.2 — Admin / Trust Dashboard (Frontend + Backend)
- [ ] Admin-only route (`/admin`) with role-based access
- [ ] Verification queue: listings pending human review, sorted by fraud signal severity
- [ ] Per-listing admin view:
  - All submitted docs
  - AI score breakdown
  - Fraud signals raised
  - Actions: Approve / Request more docs / Reject / Mark as scam
- [ ] Metrics panel: total listings, verification rate (%), fraud catch rate, stale listing count (>60 days)
- [ ] Stale listing alerts: auto-flag listings older than 60 days with no seller confirmation

#### 4.3 — Fraud Detection Pipeline (Backend + AI)
- [ ] Duplicate image detection: on every image upload, compute perceptual hash → compare with all indexed hashes
- [ ] Phone number cross-reference: flag if same phone used for >3 listings in different localities
- [ ] Pricing anomaly: flag if price > 2 std deviations above locality median
- [ ] Metadata inconsistency: flag if uploaded doc location doesn't match listing location (entity extraction)
- [ ] Fraud signal storage: `{listing_id, signal_type, severity, detail, status (open/resolved)}`

**Compliance checkpoint:**
- KYC data (Aadhaar, PAN) hashed + encrypted at rest; never sent to LLM
- Takedown/grievance flow functional
- Seller terms of service accepted before listing creation
- Admin action audit log (who approved/rejected, when)

---

### PHASE 5 — CONVERSATIONAL AI AGENT & ADVANCED FEATURES (Week 8)
**Goal:** The "Should I buy?" agent and comparison features complete the decision-support layer.

#### 5.1 — Custom MCP Server (Backend)
- [ ] Build FastMCP server exposing these tools:
  ```
  search_listings(query, filters) → ranked listings
  get_listing_details(listing_id) → full listing + scores + docs
  analyze_document(listing_id, doc_type) → AI analysis result
  score_listing(listing_id) → confidence score + breakdown
  get_area_growth_signals(lat, lng, radius_km) → growth signals
  find_comparables(listing_id, n=5) → similar listings by location+size
  get_price_estimate(listing_id) → price range + explanation
  ```
- [ ] MCP server backed entirely by your own Postgres + scoring functions (no competitor data)
- [ ] Claude API uses MCP tools to answer user questions with real listing data

#### 5.2 — Conversational AI Agent (Frontend + Backend)
- [ ] Chat widget on listing detail page: "Ask about this plot"
- [ ] System prompt: agent knows the current listing, uses MCP tools to pull context
- [ ] Example interactions:
  - "Is this plot a good investment?" → Agent checks growth signals, price estimate, risk score
  - "Are there similar plots cheaper in this area?" → Calls `find_comparables`
  - "What are the legal risks?" → Calls `analyze_document`
  - "Should I offer less?" → Calls `get_price_estimate` + negotiation logic
- [ ] LangGraph for multi-turn conversation state (maintains context across turns)
- [ ] **Required framing:** Agent responses always end with: "This is AI-assisted analysis, not financial or legal advice."

#### 5.3 — Plot Comparison (Frontend)
- [ ] "Compare" button on listing cards → adds to comparison tray
- [ ] Comparison page: side-by-side table of up to 3 plots
- [ ] Rows: price, area, confidence score, legal status, road access, flood risk, growth tier, price/sqyd
- [ ] Visual: radar chart overlaying scores for each plot
- [ ] "Best match" highlight based on user's stated intent (if captured from search)

#### 5.4 — Watchlist & Notifications (Frontend + Backend)
- [ ] Save listing to watchlist (authenticated users only)
- [ ] Watchlist page: saved plots with last-checked score and freshness
- [ ] Email/SMS notification if a watched plot's score changes significantly or if seller re-confirms

---

### PHASE 6 — POLISH, COMPLIANCE FINALIZATION & POC HANDOFF (Week 9)
**Goal:** POC is demo-ready, legally defensible, and handoff-ready for a real engineering team.

#### 6.1 — UI Polish
- [ ] Consistent design system: color tokens, typography scale, spacing system
- [ ] Loading states, empty states, error states for every screen
- [ ] Accessibility audit: WCAG 2.1 AA (keyboard nav, screen reader labels, color contrast)
- [ ] Mobile responsiveness: bottom sheets, touch-friendly pins, swipeable cards
- [ ] Onboarding tour for new users (react-joyride)
- [ ] Dark mode support (optional but impressive)

#### 6.2 — Performance
- [ ] API response time targets: search <300ms, listing detail <500ms, AI analysis <3s
- [ ] Next.js image optimization for listing photos
- [ ] Map clustering for >50 pins (Supercluster library)
- [ ] CDN for static assets (Vercel edge)
- [ ] Postgres query optimization: indexes on `lat, lng, price, locality, confidence_score`
- [ ] PostGIS spatial index on listing coordinates

#### 6.3 — Compliance Final Pass
- [ ] Legal review checklist:
  - [ ] AI output disclaimers on every AI-generated field
  - [ ] RERA positioning confirmed: classifieds-tech, not broker
  - [ ] Privacy policy covers DPDPA requirements
  - [ ] IT Intermediary rules: grievance officer contact, 24-hour takedown acknowledgment
  - [ ] Map/satellite licensing: Mapbox or Google Maps terms confirmed for display caching
  - [ ] No AI output claims "clear title," "verified investment," or "guaranteed appreciation"
  - [ ] Document analysis output cannot be downloaded without disclaimer acceptance
  - [ ] Price estimate confidence interval shown, never a point prediction
  - [ ] Growth signals labeled with: source type, announcement date, project status
  - [ ] KYC data handling: encrypted, access-logged, not exported to AI
  - [ ] Seller terms: false listing consequences, document ownership confirmation
- [ ] Add `/legal` page with ToS, Privacy Policy, Disclaimer, Grievance contact

#### 6.4 — Testing
- [ ] Unit tests: scoring functions, document parser, NL search parser (pytest)
- [ ] Integration tests: full listing creation flow, document upload + analysis pipeline
- [ ] Frontend E2E: Playwright — search → find plot → view detail → analyze document (happy path)
- [ ] Load test: 50 concurrent users on search endpoint (k6 or Locust)
- [ ] Fraud detection tests: known duplicate images, same phone listings, price outliers

#### 6.5 — Documentation (for AI agent / dev team handoff)
- [ ] `README.md`: project overview, local setup, env vars, seeding instructions
- [ ] `ARCHITECTURE.md`: system diagram, data flow, AI pipeline, MCP server spec
- [ ] `API.md`: all FastAPI endpoints with request/response schemas (auto-generated via FastAPI docs)
- [ ] `SCORING.md`: confidence score dimensions, weights, rationale
- [ ] `COMPLIANCE.md`: legal positioning, disclaimer inventory, data handling rules
- [ ] `SEED_DATA.md`: how to regenerate the Hyderabad demo dataset
- [ ] ADRs (Architecture Decision Records): Why Mapbox over Google Maps, why pgvector over Pinecone, why FastAPI over Node

---

## 6. DATA SCHEMA (Core Tables)

```sql
-- Listings
CREATE TABLE listings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  seller_id UUID REFERENCES users(id),
  title TEXT,
  description TEXT,
  lat DOUBLE PRECISION NOT NULL,
  lng DOUBLE PRECISION NOT NULL,
  location GEOGRAPHY(POINT, 4326),  -- PostGIS
  locality TEXT,
  price_lakhs NUMERIC(10,2),
  area_sqyd NUMERIC(10,2),
  price_per_sqyd NUMERIC(10,2) GENERATED ALWAYS AS (price_lakhs * 100000 / area_sqyd) STORED,
  use_type TEXT,  -- residential/agricultural/commercial/industrial
  road_access TEXT,  -- highway/main-road/lane/no-road
  ownership_type TEXT,  -- freehold/leasehold/agricultural-patta
  listing_status TEXT DEFAULT 'pending',  -- pending/live/flagged/removed
  verification_tier INTEGER DEFAULT 0,  -- 0=unverified, 1=AI-verified, 2=fully-verified
  confidence_score NUMERIC(5,2),
  confidence_breakdown JSONB,
  risk_flags JSONB,
  growth_signals JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_confirmed_at TIMESTAMPTZ,
  embedding VECTOR(1536)  -- pgvector for semantic search
);

-- Documents
CREATE TABLE listing_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  listing_id UUID REFERENCES listings(id),
  doc_type TEXT,  -- EC/sale-deed/layout-approval/mutation/patta/photo
  storage_url TEXT,
  ocr_text TEXT,
  ai_analysis JSONB,  -- entities, risks, missing_approvals, red_flags
  analysis_status TEXT DEFAULT 'pending',
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Growth Signals
CREATE TABLE growth_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_type TEXT,  -- metro/highway/industrial-park/hospital/school/mall
  title TEXT,
  source_url TEXT,
  source_type TEXT,  -- government/developer/news
  status TEXT,  -- announced/approved/under-construction/operational
  announced_date DATE,
  location GEOGRAPHY(POLYGON, 4326),
  confidence TEXT,  -- high/medium/speculative
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fraud Signals
CREATE TABLE fraud_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  listing_id UUID REFERENCES listings(id),
  signal_type TEXT,  -- duplicate-image/phone-reuse/price-anomaly/doc-mismatch
  severity TEXT,  -- high/medium/low
  detail TEXT,
  status TEXT DEFAULT 'open',  -- open/resolved/false-positive
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comparable Sales (price model training data)
CREATE TABLE comparables (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lat DOUBLE PRECISION,
  lng DOUBLE PRECISION,
  locality TEXT,
  area_sqyd NUMERIC,
  price_lakhs NUMERIC,
  transaction_date DATE,
  source TEXT  -- dharani/manual/estimated
);

-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT UNIQUE,
  email TEXT UNIQUE,
  role TEXT DEFAULT 'buyer',  -- buyer/seller/admin
  kyc_status TEXT DEFAULT 'unverified',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. MCP SERVER TOOL SPECIFICATION

```python
# /ai/mcp_server.py — FastMCP tool registry

@mcp.tool()
async def search_listings(
    query: str,
    budget_max_lakhs: float | None,
    locality: str | None,
    use_type: str | None,
    min_confidence: float = 0,
    limit: int = 20
) -> list[ListingSummary]:
    """Natural language + filter hybrid search over Hyderabad listings."""

@mcp.tool()
async def get_listing_details(listing_id: str) -> ListingDetail:
    """Full listing data including scores, documents, risk flags."""

@mcp.tool()
async def analyze_document(listing_id: str, doc_id: str) -> DocumentAnalysis:
    """Get AI analysis of a specific document: risks, entities, missing items."""

@mcp.tool()
async def score_listing(listing_id: str) -> ConfidenceScore:
    """Run/refresh the confidence scoring pipeline for a listing."""

@mcp.tool()
async def get_area_growth_signals(
    lat: float, lng: float, radius_km: float = 10
) -> list[GrowthSignal]:
    """Return nearby infrastructure and development signals."""

@mcp.tool()
async def find_comparables(
    listing_id: str, n: int = 5
) -> list[ComparableListing]:
    """Find N most similar listings by location, size, and use type."""

@mcp.tool()
async def get_price_estimate(
    listing_id: str
) -> PriceEstimate:
    """Return model-based price range with P10/P50/P90 and explanation."""
```

---

## 8. COMPLIANCE QUICK-REFERENCE FOR DEVELOPERS

Every developer working on this project must internalize these rules:

| Rule | Where It Applies | Implementation |
|------|-----------------|----------------|
| Never certify title | Legal doc analyzer output | Mandatory disclaimer component in UI |
| Never guarantee returns | Price estimation, investment score | Confidence intervals only; "model estimate" label always visible |
| Growth signals must show source + status | Growth tab | Source type, date, status fields required in DB and UI |
| AI outputs are advisory only | All AI features | "AI-assisted" label on every AI-generated field |
| KYC data never goes to LLM | Seller onboarding | Hash/encrypt before store; extract only doc-type features for analysis |
| Verify map data licensing | Map overlays | Google Maps: no caching beyond policy; Mapbox: check tile usage limits |
| RERA safe harbor | All marketing copy | Platform = classifieds tech, not broker. No "verified agent" language |
| Grievance officer required | /legal page | Named contact, 24-hour acknowledgment SLA |
| Data minimization | All forms | Don't collect what you don't need; no full Aadhaar storage |
| False listing liability | Seller ToS | Seller affirms ownership; platform is not liable for false claims |

---

## 9. HACKATHON POC DEMO SCRIPT (5-minute walkthrough)

```
[0:00] Show homepage → type: "Plots near Kokapet ORR under 50 lakhs"
[0:30] Map loads → pins appear → cards slide in → explain confidence score color coding
[1:00] Click a plot → side drawer opens → show score + 3 risk badges
[1:30] Navigate to full detail page → walk through tabs:
         Legal & Docs: upload EC → AI analysis runs → shows entities + risk flags
         Price Intel: show estimated range + comparables map
         Location: satellite overlay + POIs + flood zone
         Growth: HMDA/metro project tagged "approved"
[3:00] Open chat widget → ask "Should I offer less than asking price?"
         Agent calls get_price_estimate + find_comparables → returns reasoned answer
[3:45] Switch to admin dashboard → show fraud queue → one duplicate image flagged
[4:15] Show seller onboarding form → doc upload → instant AI pre-check
[4:45] Close: "This is AI-assisted due diligence for land — not another classifieds app"
```

---

## 10. RISK REGISTER & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Thin listing supply (cold start) | High | High | Seed 80 curated demo listings; manual owner outreach for V1 real data |
| Map API costs blow up | Medium | Medium | Implement aggressive tile caching; switch to Mapbox if Google costs spike |
| LLM hallucination in doc analysis | High | High | Structured output schema (Pydantic); human-review flag for low-confidence outputs; mandatory disclaimer |
| RERA classification risk | Medium | High | Legal review before launch; position as tech platform, not broker |
| Competitor scraping enforcement | Low | High | Do not use scraped data; use seed dataset + direct seller onboarding |
| Price model underfit | High | Medium | Use wide confidence intervals; frame as range not point; label clearly |
| KYC data breach | Low | Very High | Encrypt at rest, hash Aadhaar, access logs, no LLM exposure |
| Stale listings killing trust | High | High | 60-day re-confirmation cycle; auto-expire after 90 days |
| Growth signals turning out wrong | Medium | Medium | Status tracking (announced vs. operational); date stamps; "speculative" label for news-only signals |
```
