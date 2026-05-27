# Requirements Document

## Introduction

PlotIQ is an AI-powered land discovery and verification platform targeting Hyderabad, Telangana. It is **not** a classifieds portal — the core differentiator is intelligence layered on top of listings: fraud detection, legal document analysis, price estimation, location intelligence, and a conversational AI agent.

This document covers the POC scope: **Phases 0 through 3** — Foundation, Core Discovery, Intelligence Layer, and Location & Geospatial Intelligence. The POC targets three user roles: Buyer/Investor (primary), Seller/Owner, and Admin/Ops.

**Tech stack confirmed for POC:**
- Frontend: Vite + React (existing mock, preserve design language)
- Backend: FastAPI (Python), starting from scratch
- Database: PostgreSQL + PostGIS + pgvector via Supabase
- Map: Google Maps JS API
- LLMs: OpenRouter and Groq (not Claude/OpenAI directly)
- File storage: Cloudflare R2 or AWS S3
- Auth: Clerk or NextAuth (phone OTP + Google OAuth)
- Task queue: Celery + Redis (Upstash free tier)

---

## Glossary

- **System**: The PlotIQ platform as a whole (frontend + backend + AI layer)
- **Frontend**: The Vite + React web application served to users
- **Backend**: The FastAPI Python service exposing REST endpoints
- **AI_Layer**: The LangChain/MCP-based AI pipeline in `/ai`
- **Confidence_Score_Engine**: The backend module that computes a 0–100 trust score for each listing
- **Document_Analyzer**: The AI pipeline that performs OCR and LLM-based extraction on uploaded legal documents
- **Search_Engine**: The backend module combining NL query parsing, structured filters, and pgvector semantic search
- **Map_View**: The Google Maps JS API integration rendered in the Frontend
- **Listing**: A single land plot record stored in PostgreSQL with all associated metadata, scores, and documents
- **Seed_Dataset**: The curated set of 50–80 Hyderabad plot records used to populate the POC database
- **PostGIS**: The PostgreSQL geospatial extension enabling radius search, bounding box queries, and spatial joins
- **pgvector**: The PostgreSQL extension storing and querying high-dimensional embedding vectors
- **Confidence_Score**: A 0–100 numeric score computed by the Confidence_Score_Engine representing listing trustworthiness
- **Risk_Flag**: A structured signal attached to a Listing indicating a specific fraud or quality concern
- **Growth_Signal**: A structured record linking a government infrastructure project to a geographic area
- **POI**: Point of Interest — a named location (school, hospital, metro station, highway) retrieved from OpenStreetMap via the Overpass API
- **EC**: Encumbrance Certificate — a legal document certifying a property is free of monetary and legal liabilities
- **Sale_Deed**: The primary legal document transferring ownership of land from seller to buyer
- **Layout_Approval**: Government approval (typically HMDA or DTCP) for a residential or commercial layout
- **Mutation_Register**: A revenue department record updating land ownership after a transaction
- **Patta**: A land ownership document issued by the revenue department (also called ROR — Record of Rights)
- **HMDA**: Hyderabad Metropolitan Development Authority
- **NHAI**: National Highways Authority of India
- **ORR**: Outer Ring Road — the primary arterial highway encircling Hyderabad
- **Buyer**: A user role representing a person searching for land to purchase or invest in
- **Seller**: A user role representing a person listing land for sale
- **Admin**: A user role with elevated privileges to review, approve, reject, or flag listings
- **KYC**: Know Your Customer — identity verification using Aadhaar and/or PAN
- **Disclaimer**: A mandatory UI element informing users that AI outputs are not legal or financial certifications
- **Monorepo**: The single Git repository containing `/frontend`, `/backend`, and `/ai` directories
- **Celery_Worker**: An asynchronous task processor consuming jobs from the Redis queue
- **Embedding**: A fixed-length numeric vector representation of a listing's text fields, stored in pgvector
- **Overpass_API**: The OpenStreetMap query API used to retrieve POI data within a geographic radius
- **GeoJSON**: A standard format for encoding geographic data structures used for flood risk and land use overlays

---

## Requirements

### Requirement 1: Monorepo and Project Structure

**User Story:** As a developer, I want a well-structured monorepo, so that frontend, backend, and AI components are independently deployable yet co-located for easy development.

#### Acceptance Criteria

1. THE System SHALL organize source code into three top-level directories: `/frontend` (Vite + React), `/backend` (FastAPI), and `/ai` (LangChain/MCP tools).
2. THE System SHALL preserve the existing Vite + React frontend codebase including all current components (Navbar, Hero, GlassCard) and the dark glassmorphism design language.
3. WHEN the Hero component renders, THE Frontend SHALL load the background video from the local file `public/ce_f_f_c_be_d_b_d_ef_a_mp_.mp4` rather than any external CDN URL.
4. THE System SHALL include a root-level `README.md` documenting local setup steps, required environment variables, and database seeding instructions.
5. THE Backend SHALL expose a health-check endpoint at `GET /health` returning HTTP 200 with a JSON status payload.
6. THE System SHALL include a `.env.example` file listing all required environment variable keys without values.

---

### Requirement 2: Database and Infrastructure Setup

**User Story:** As a developer, I want PostgreSQL with PostGIS and pgvector configured on Supabase, so that geospatial queries and semantic vector search work from day one.

#### Acceptance Criteria

1. THE Backend SHALL connect to a PostgreSQL database with the PostGIS extension enabled, supporting `GEOGRAPHY(POINT, 4326)` column types.
2. THE Backend SHALL connect to a PostgreSQL database with the pgvector extension enabled, supporting `VECTOR(1536)` column types for listing embeddings.
3. THE Backend SHALL use SQLAlchemy with Alembic for all schema migrations, with migration files committed to the repository.
4. THE System SHALL provision a Redis instance (Upstash free tier) and configure Celery to use it as the task broker and result backend.
5. THE System SHALL provision a file storage bucket (Cloudflare R2 or AWS S3) and configure the Backend to upload documents and images to it.
6. WHEN the Backend starts, THE Backend SHALL verify database connectivity and log an error with a descriptive message if the connection fails.
7. IF the PostGIS or pgvector extension is not enabled on the connected database, THEN THE Backend SHALL log a startup error identifying the missing extension by name.

---

### Requirement 3: Seed Dataset

**User Story:** As a developer, I want a realistic seed dataset of Hyderabad plots, so that all POC features have meaningful data to demonstrate.

#### Acceptance Criteria

1. THE System SHALL include a seed script that inserts between 50 and 80 plot listings into the `listings` table.
2. THE Seed_Dataset SHALL distribute listings across 6 to 8 distinct Hyderabad localities (e.g., Kokapet, Shadnagar, Adibatla, Patancheru, Ibrahimpatnam, Sangareddy corridor, Shamshabad, Ghatkesar).
3. EACH seeded Listing SHALL include the following fields with realistic values: `lat`, `lng`, `price_lakhs`, `area_sqyd`, `owner_type`, `road_access`, `listing_age`, `doc_status`, `mock_confidence_score`, `risk_flags`, and `growth_signals`.
4. THE Seed_Dataset SHALL include listings with `mock_confidence_score` values distributed across all three tiers: high (80–100), medium (50–79), and low (0–49), with at least 10 listings in each tier.
5. WHEN the seed script runs, THE Backend SHALL generate and store a pgvector embedding for each seeded Listing using the configured embedding model.
6. THE System SHALL validate PostGIS spatial queries against the seed data, including radius search (5 km), bounding box, and nearest-N queries, before the seed script exits.
7. THE System SHALL include a `SEED_DATA.md` file documenting how to regenerate the Hyderabad demo dataset.

---

### Requirement 4: Compliance Baseline

**User Story:** As a product owner, I want mandatory legal disclaimers and a privacy policy structure in place from the start, so that the platform is legally defensible before any user-facing feature ships.

#### Acceptance Criteria

1. THE Frontend SHALL display a non-skippable Disclaimer on every page or component that renders a Confidence_Score, stating: "AI confidence score is a model estimate and does not constitute legal title certification."
2. THE Frontend SHALL display a non-skippable Disclaimer on every page or component that renders a price estimate, stating: "Price estimates are model outputs and are not a valuation or guarantee."
3. THE Frontend SHALL display a non-skippable Disclaimer on every page or component that renders Document_Analyzer output, stating: "This is an AI-generated summary only. Consult a licensed lawyer for legal advice and title verification."
4. THE Frontend SHALL display a non-skippable Disclaimer on every page or component that renders Growth_Signal data, stating: "Growth signals are based on announced or approved projects. Outcomes depend on execution. This is not investment advice."
5. THE System SHALL include a `/legal` route rendering a page with Terms of Service, Privacy Policy, Disclaimer inventory, and a Grievance contact.
6. THE Backend SHALL maintain an audit log table recording every access to or modification of a Listing's documents, including the user ID, action type, and timestamp.
7. THE Backend SHALL never transmit KYC data (Aadhaar number, PAN number) to any LLM API endpoint.
8. THE System SHALL include a "Report a listing" mechanism allowing any authenticated user to submit a takedown or grievance report for any Listing.

---

### Requirement 5: Map-First Discovery UI

**User Story:** As a Buyer, I want a Zillow-style split-view map interface, so that I can visually explore available plots and immediately see their trust signals.

#### Acceptance Criteria

1. THE Frontend SHALL render a split-view layout with the Map_View occupying 60% of the viewport width on the left and a listing card panel occupying 40% on the right, on screens wider than 768px.
2. WHEN the viewport width is 768px or less, THE Frontend SHALL stack the Map_View above the listing card panel in a single-column layout with the listing panel rendered as a bottom sheet.
3. THE Map_View SHALL render custom pin markers for each Listing, color-coded by Confidence_Score tier: green for scores 80 and above, yellow for scores 50 through 79, red for scores below 50, and grey for listings with no score.
4. WHEN the user pans or zooms the Map_View, THE Frontend SHALL update the listing card panel to show only Listings whose coordinates fall within the current map viewport bounds.
5. THE Frontend SHALL display a "Search this area" button that becomes visible after the user pans the Map_View, and WHEN clicked, THE Frontend SHALL trigger a new search using the current viewport bounding box as the geographic constraint.
6. EACH listing card in the panel SHALL display: price in lakhs, area in square yards, locality name, Confidence_Score badge, up to two Risk_Flag pills, and an "Analyze" call-to-action button.
7. THE Frontend SHALL render loading skeleton states for listing cards and map pins while search results are being fetched.
8. THE Frontend SHALL maintain the dark glassmorphism design language (black background, white/10 glass cards, frosted navigation) established in the existing mock across all new pages and components.

---

### Requirement 6: Natural Language and Semantic Search

**User Story:** As a Buyer, I want to search for plots using plain English, so that I don't need to know exact filter values to find relevant listings.

#### Acceptance Criteria

1. THE Search_Engine SHALL accept a natural language query string and parse it into a structured filter object containing zero or more of: `budget_max`, `budget_min`, `location_hint`, `use_type`, `road_access`, `area_min`, `area_max`.
2. WHEN a natural language query is parsed, THE AI_Layer SHALL use an LLM via OpenRouter or Groq to perform the extraction, and THE Backend SHALL return the structured filter object alongside the ranked results.
3. THE Search_Engine SHALL generate an embedding for the query string and perform cosine similarity search over the pgvector listing embeddings to produce a semantic relevance ranking.
4. THE Search_Engine SHALL combine structured filter constraints (hard constraints applied via SQL WHERE clauses) with semantic ranking (soft relevance applied as a re-ranking step) to produce the final result list.
5. THE Backend SHALL expose a `POST /search` endpoint accepting a JSON body with `query` (string) and optional `filters` (object), and returning a ranked array of Listing summaries with scores.
6. WHEN the `POST /search` endpoint receives a request, THE Backend SHALL return a response within 500ms for queries against the seed dataset under normal load.
7. THE Frontend SHALL render a search bar accepting natural language input and a collapsible filter panel with controls for: price range (min/max in lakhs), area range (min/max in square yards), locality (multi-select), use type (single-select), and Confidence_Score threshold (slider).
8. IF the natural language parser cannot extract any structured filters from a query, THEN THE Search_Engine SHALL fall back to pure semantic search over all listings without applying any hard constraints.

---

### Requirement 7: Authentication

**User Story:** As a user, I want to sign in with Google or my phone number, so that I can access protected features like saving listings and contacting sellers.

#### Acceptance Criteria

1. THE Frontend SHALL support Google OAuth sign-in via Clerk or NextAuth, completing the OAuth flow without leaving the application.
2. THE Frontend SHALL support phone number sign-in via OTP (one-time password) sent by SMS, completing verification within the application.
3. WHEN a user successfully authenticates, THE Backend SHALL create or update a user record in the `users` table with the user's provider ID, display name, and authentication method.
4. THE Backend SHALL protect the following route categories with authentication middleware, returning HTTP 401 for unauthenticated requests: seller listing creation, document upload, watchlist operations, and contact request submission.
5. WHILE a user is authenticated as an Admin, THE Backend SHALL permit access to the `/admin` route and all admin API endpoints.
6. THE Frontend SHALL display the user's display name and a sign-out option in the Navbar when the user is authenticated.
7. IF a user attempts to access a protected route while unauthenticated, THEN THE Frontend SHALL redirect the user to the sign-in page and return the user to the originally requested route after successful authentication.

---

### Requirement 8: AI Confidence Score Engine

**User Story:** As a Buyer, I want each listing to have a transparent AI-generated trust score, so that I can quickly assess listing quality without reading every document.

#### Acceptance Criteria

1. THE Confidence_Score_Engine SHALL compute a Confidence_Score between 0 and 100 for each Listing using six weighted dimensions: document completeness (25%), owner KYC status (20%), geo-location consistency (15%), duplicate detection (20%), pricing anomaly check (10%), and listing freshness (10%).
2. THE Confidence_Score_Engine SHALL store the per-dimension score breakdown as a JSONB field on the Listing record alongside the aggregate Confidence_Score.
3. WHEN a new Listing is created, THE Backend SHALL enqueue a Celery task to compute the Confidence_Score asynchronously within 30 seconds of listing creation.
4. WHEN a document is uploaded to a Listing, THE Backend SHALL enqueue a Celery task to recompute the Confidence_Score reflecting the updated document completeness dimension.
5. THE Confidence_Score_Engine SHALL detect duplicate images by computing a perceptual hash for each uploaded listing image and comparing it against all previously indexed image hashes in the database.
6. THE Confidence_Score_Engine SHALL detect phone number reuse by flagging any Listing whose seller phone number appears in more than 3 other Listings in different localities.
7. THE Confidence_Score_Engine SHALL detect pricing anomalies by computing the Z-score of the Listing's price per square yard against the median price per square yard for its locality, and flagging listings with a Z-score greater than 2.
8. THE Frontend SHALL display the Confidence_Score as a radial chart with per-dimension breakdown on the AI Score tab of the Listing Detail Page.
9. THE Frontend SHALL display the mandatory Disclaimer for Confidence_Score on the AI Score tab in a visually prominent position that cannot be collapsed or dismissed.

---

### Requirement 9: Legal Document Analyzer

**User Story:** As a Buyer, I want the platform to analyze uploaded legal documents and extract key entities and risks, so that I can understand a document's contents without reading dense legal text.

#### Acceptance Criteria

1. THE Backend SHALL expose a `POST /listings/{id}/documents` endpoint accepting PDF, JPG, and PNG file uploads up to 20MB, storing the file in the configured object storage bucket and recording the reference in the database.
2. WHEN a document is uploaded, THE Document_Analyzer SHALL extract text from the document using OCR if the document is a scanned image or a non-text-layer PDF.
3. WHEN text is available from a document, THE Document_Analyzer SHALL use an LLM via OpenRouter or Groq to extract: named parties, survey numbers, dates, transaction amounts, identified risk clauses, missing approvals, and suspicious language patterns.
4. THE Document_Analyzer SHALL produce structured output conforming to a defined Pydantic schema for each of the following document types: EC, Sale_Deed, Layout_Approval, Mutation_Register, and Patta.
5. THE Backend SHALL store the Document_Analyzer output as a JSONB field on the document record in the database.
6. THE Frontend SHALL display the document upload status tracker and the AI summary for each uploaded document on the Legal & Docs tab of the Listing Detail Page.
7. THE Frontend SHALL display the mandatory Document_Analyzer Disclaimer on the Legal & Docs tab in a visually prominent position that cannot be collapsed or dismissed.
8. THE Backend SHALL never include raw KYC data fields (Aadhaar number, PAN number) in any prompt sent to an LLM API.
9. IF the Document_Analyzer encounters an unreadable or corrupted file, THEN THE Backend SHALL return a structured error response identifying the document ID and the failure reason, without crashing the analysis pipeline.

---

### Requirement 10: Listing Detail Page

**User Story:** As a Buyer, I want a comprehensive 7-tab detail page for each listing, so that I can access all intelligence about a plot in one place.

#### Acceptance Criteria

1. THE Frontend SHALL render a Listing Detail Page with seven tabs: Overview, AI Score, Legal & Docs, Price Intelligence, Location Intelligence, Future Growth, and Risk Summary.
2. THE Overview tab SHALL display: plot summary, owner information with verified/unverified badge, listing age in days, locality name, and a thumbnail map showing the plot's location.
3. THE AI Score tab SHALL display the Confidence_Score radial chart, per-dimension sub-scores with explanations, and the mandatory Confidence_Score Disclaimer.
4. THE Legal & Docs tab SHALL display the upload status for each expected document type (EC, Sale_Deed, Layout_Approval, Mutation_Register, Patta), the AI summary for each uploaded document, and the mandatory Document_Analyzer Disclaimer.
5. THE Price Intelligence tab SHALL display the estimated fair value range, a list of comparable plots, a price trend chart for the micro-market, an overpriced/underpriced flag with explanation, a negotiation range suggestion, and the mandatory price estimate Disclaimer.
6. THE Location Intelligence tab SHALL display a satellite/hybrid map toggle, POI overlay controls, distances to key infrastructure, road access score, and flood risk overlay.
7. THE Future Growth tab SHALL display nearby infrastructure projects with source, announcement date, project status, and growth tier label, along with the mandatory Growth_Signal Disclaimer.
8. THE Risk Summary tab SHALL display the top 3 Risk_Flags with severity level (high/medium/low) and explanation, a missing document checklist, and any fraud signal report.
9. WHEN a user navigates to the Listing Detail Page from a listing card, THE Frontend SHALL preserve the map state (center, zoom, active filters) so that the user can return to the same map view via breadcrumb navigation.

---

### Requirement 11: Price Intelligence

**User Story:** As a Buyer, I want an AI-generated price estimate with comparable plots, so that I can assess whether a listing is fairly priced before negotiating.

#### Acceptance Criteria

1. THE Backend SHALL expose a price estimation model trained on the seed dataset using scikit-learn Ridge regression, with features including: locality, area in square yards, road access type, distance to ORR in kilometers, distance to nearest highway in kilometers, land use type, document completeness score, and listing age in days.
2. THE Backend SHALL return a price estimate as a confidence interval (P10 to P90 range in lakhs) rather than a single point value.
3. THE Backend SHALL identify 5 to 10 comparable Listings by performing a PostGIS radius query centered on the subject Listing's coordinates, filtered to listings within a 20% size range of the subject Listing's area.
4. THE Backend SHALL compute a price trend by aggregating the median price per square yard by locality and calendar month across the seed dataset.
5. THE Backend SHALL classify a Listing as overpriced if its price per square yard exceeds the P75 of comparable listings, and as underpriced if it falls below the P25 of comparable listings.
6. THE Backend SHALL compute a negotiation range as the P25 to P50 price per square yard of comparable listings multiplied by the subject Listing's area.
7. THE Frontend SHALL render the price trend as a line chart using Recharts on the Price Intelligence tab.
8. THE Frontend SHALL display the mandatory price estimate Disclaimer on the Price Intelligence tab in a visually prominent position that cannot be collapsed or dismissed.

---

### Requirement 12: Location Intelligence and POI Overlay

**User Story:** As a Buyer, I want to see nearby points of interest and infrastructure distances on the listing map, so that I can evaluate the plot's connectivity and livability.

#### Acceptance Criteria

1. THE Frontend SHALL provide a satellite/hybrid map toggle on the Location Intelligence tab of the Listing Detail Page, switching the Map_View base layer between roadmap and satellite imagery.
2. THE Backend SHALL expose a `GET /listings/{id}/pois` endpoint that queries the Overpass API for POIs within a 5km radius of the Listing's coordinates, returning results categorized by type: schools, hospitals, malls, metro stations, highways, and bus depots.
3. THE Frontend SHALL render POI markers as a toggleable overlay on the map, with distinct icons per POI category, filterable by category using a checkbox panel.
4. THE Backend SHALL compute the great-circle distance from the Listing's coordinates to each returned POI and include the distance in kilometers in the API response.
5. THE Frontend SHALL display a distance summary table on the Location Intelligence tab listing the nearest POI of each category with its name and distance in kilometers.
6. THE Frontend SHALL render a flood risk overlay on the Location Intelligence tab map using a static GeoJSON file representing Hyderabad flood hazard zones.
7. IF the Overpass API request fails or times out after 10 seconds, THEN THE Backend SHALL return a cached or empty POI result with an error flag, without returning an HTTP 5xx response to the Frontend.

---

### Requirement 13: Future Growth Signals

**User Story:** As a Buyer or Investor, I want to see nearby government infrastructure projects linked to a listing's location, so that I can assess the area's long-term appreciation potential.

#### Acceptance Criteria

1. THE Backend SHALL maintain a `growth_signals` database table with fields: `signal_type`, `title`, `source_url`, `source_type`, `date_announced`, `status` (one of: announced, approved, under-construction, operational), `location_polygon` (PostGIS geometry), and `confidence`.
2. THE Seed_Dataset SHALL populate the `growth_signals` table with at least 15 curated Hyderabad infrastructure projects covering HMDA approved layouts, NHAI highway projects, HMRL metro extensions, and industrial parks.
3. THE Backend SHALL expose a `GET /listings/{id}/growth-signals` endpoint that performs a PostGIS spatial join between the Listing's coordinates and the `growth_signals` table, returning all signals whose `location_polygon` contains or is within 10km of the Listing's location.
4. THE Backend SHALL assign a growth tier label to each Listing based on the count and status of nearby Growth_Signals: "High Growth Corridor" for listings with 3 or more approved or under-construction signals within 10km, "Emerging Zone" for listings with 1 to 2 such signals, and "Speculative" for listings with only announced signals or no signals.
5. THE Frontend SHALL display each Growth_Signal on the Future Growth tab with: title, source type, announcement date, current status, and growth tier label.
6. THE Frontend SHALL display the mandatory Growth_Signal Disclaimer on the Future Growth tab in a visually prominent position that cannot be collapsed or dismissed.
7. IF a Growth_Signal record has a `status` of "announced" with no `source_url`, THEN THE Backend SHALL reject the record insertion with a validation error identifying the missing field.

---

### Requirement 14: Seller Listing Creation (POC Scope)

**User Story:** As a Seller, I want to create a listing by entering plot details and uploading documents, so that my property is discoverable by buyers with an AI-generated trust score.

#### Acceptance Criteria

1. THE Frontend SHALL provide a multi-step listing creation form accessible only to authenticated users, with steps for: plot location (pin drop on map), plot details (size, price, use type, ownership type), and document upload (EC, Sale_Deed, photos).
2. WHEN a Seller submits a new Listing, THE Backend SHALL immediately enqueue a Celery task to run the Confidence_Score_Engine and Document_Analyzer pipelines on the submitted data.
3. WHEN the Confidence_Score_Engine completes for a new Listing, THE Backend SHALL set the Listing's `listing_status` to "live" if the score is 70 or above, "live" with a "Partial Verification" badge if the score is between 40 and 69, or "pending_review" if the score is below 40 or any fraud signal is raised.
4. THE Frontend SHALL display the preliminary Confidence_Score and any identified issues to the Seller after submission, with prompts to upload missing documents or correct flagged fields.
5. THE Backend SHALL require Seller acceptance of the Terms of Service before the listing creation endpoint processes the request, returning HTTP 400 if the acceptance flag is not present.
6. THE Backend SHALL enforce a rate limit of 5 listing creation requests per Seller per 24-hour period, returning HTTP 429 with a descriptive message when the limit is exceeded.

---

### Requirement 15: Admin Trust Dashboard (POC Demo Quality)

**User Story:** As an Admin, I want a dashboard showing the verification queue and key trust metrics, so that I can review flagged listings and demonstrate operational maturity.

#### Acceptance Criteria

1. THE Frontend SHALL render an `/admin` route accessible only to users with the Admin role, returning HTTP 403 for all other authenticated users.
2. THE Admin dashboard SHALL display a verification queue listing all Listings with `listing_status` of "pending_review", sorted by fraud signal severity in descending order.
3. THE Admin dashboard SHALL provide per-listing actions: Approve (sets status to "live"), Request More Docs (sends a notification to the Seller), Reject (sets status to "removed"), and Mark as Scam (sets status to "removed" and creates a fraud record).
4. THE Admin dashboard SHALL display a metrics panel showing: total listing count, verification rate as a percentage of live listings, fraud catch rate as a percentage of reviewed listings, and stale listing count (listings with `last_confirmed_at` older than 60 days).
5. WHEN an Admin performs any action on a Listing, THE Backend SHALL record the action in the audit log table with the Admin's user ID, the action type, the target Listing ID, and the timestamp.
6. THE Backend SHALL automatically flag Listings whose `last_confirmed_at` timestamp is more than 60 days in the past by setting a `stale` Risk_Flag on the Listing record.

---

### Requirement 16: Parser and Serializer Round-Trip Integrity

**User Story:** As a developer, I want all data parsers and serializers to be verifiably correct, so that data is never silently corrupted when moving between formats.

#### Acceptance Criteria

1. THE Backend SHALL implement a Listing serializer that converts a Listing database record to a JSON API response object.
2. THE Backend SHALL implement a Listing deserializer that converts a JSON API request body to a validated Listing creation payload using Pydantic.
3. FOR ALL valid Listing creation payloads, deserializing then serializing then deserializing SHALL produce an equivalent object (round-trip property).
4. THE Document_Analyzer SHALL implement a structured output serializer that converts LLM extraction results to the defined Pydantic schema for each document type.
5. FOR ALL valid Document_Analyzer outputs, serializing to JSON then deserializing from JSON SHALL produce an equivalent Pydantic model instance (round-trip property).
6. THE Search_Engine SHALL implement a query filter serializer that converts a structured filter object to a URL-safe query string and a deserializer that reconstructs the filter object from the query string.
7. FOR ALL valid structured filter objects, serializing to query string then deserializing SHALL produce an equivalent filter object (round-trip property).
8. IF a Listing serializer receives a field value that does not conform to the expected type, THEN THE Backend SHALL return a structured validation error identifying the field name and the received type.

---

### Requirement 17: API Performance and Reliability

**User Story:** As a Buyer, I want search and listing detail responses to be fast and reliable, so that the discovery experience feels responsive.

#### Acceptance Criteria

1. WHEN the `POST /search` endpoint receives a request against the seed dataset under normal load (fewer than 10 concurrent requests), THE Backend SHALL return a complete response within 500ms.
2. WHEN the `GET /listings/{id}` endpoint receives a request, THE Backend SHALL return a complete response within 300ms.
3. WHEN the Document_Analyzer pipeline is triggered for a newly uploaded document, THE Backend SHALL complete the analysis and store the result within 30 seconds for documents up to 5MB.
4. THE Backend SHALL return HTTP 429 with a `Retry-After` header when any endpoint receives more than 60 requests per minute from a single IP address.
5. IF any backend dependency (database, Redis, object storage) is unavailable, THEN THE Backend SHALL return HTTP 503 with a JSON body identifying the unavailable dependency, rather than returning HTTP 500 or timing out silently.
6. THE Backend SHALL log all requests with method, path, response status code, and response time in milliseconds to standard output in a structured JSON format.

---

### Requirement 18: Design System Consistency

**User Story:** As a product owner, I want all new pages to match the existing dark glassmorphism design language, so that the POC presents a cohesive visual identity.

#### Acceptance Criteria

1. THE Frontend SHALL apply the dark glassmorphism design system to all new pages and components, using: black (`#000000`) as the base background, `bg-white/5` to `bg-white/10` for glass card surfaces, `border-white/10` to `border-white/20` for card borders, and `backdrop-blur-[20px]` for frosted glass effects.
2. THE Frontend SHALL use the Inter font family at the defined weight scale (400, 500, 600, 700) for all text elements across new pages.
3. THE Frontend SHALL use the `glass-card` CSS class defined in `src/index.css` as the base style for all card components across new pages.
4. THE Frontend SHALL use the `btn-primary` and `btn-secondary` CSS classes defined in `src/index.css` for all primary and secondary action buttons across new pages.
5. THE Frontend SHALL use Framer Motion (the `motion` package) for all entrance animations on new pages, following the stagger-in pattern established in the existing components.
6. THE Frontend SHALL maintain WCAG 2.1 AA color contrast ratios for all text elements rendered on the dark background.

---

*Document version: 1.0 — PlotIQ POC Phases 0–3*
*Scope: Foundation, Core Discovery, Intelligence Layer, Location & Geospatial Intelligence*
*Roles in scope: Buyer/Investor, Seller/Owner, Admin/Ops*
