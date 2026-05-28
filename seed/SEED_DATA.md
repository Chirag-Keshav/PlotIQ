# PlotIQ Seed Dataset

## Overview

The seed dataset populates the database with realistic Hyderabad land plot listings and infrastructure growth signals for the POC demo.

- **Listings**: 60 plots across 8 localities, with confidence scores across all three tiers
- **Growth Signals**: 16 curated Hyderabad infrastructure projects

## How to Run

```bash
# From the repo root
cd backend
pip install -r requirements.txt

# Ensure DATABASE_URL and REDIS_URL are set in .env
python -m seed.seed
```

Or from the `seed/` directory:

```bash
python seed.py
```

## Localities Covered

| Locality | Count | Notes |
|---|---|---|
| Kokapet | ~8 | Financial District edge, ORR access |
| Shadnagar | ~8 | NH-44 corridor, industrial growth |
| Adibatla | ~8 | Aerospace & defence park proximity |
| Patancheru | ~8 | Fab City, industrial estates |
| Ibrahimpatnam | ~7 | Eastern ORR, logistics zone |
| Shamshabad | ~7 | Airport zone, metro Phase 2 |
| Ghatkesar | ~7 | Metro Phase 3 corridor |
| Sangareddy | ~7 | Auto manufacturing, NH-65 |

## Confidence Score Distribution

| Tier | Score Range | Count |
|---|---|---|
| High | 80–100 | ≥ 10 |
| Medium | 50–79 | ≥ 10 |
| Low | 0–49 | ≥ 10 |

## Growth Signals Dataset

Sourced from `growth_signals_data.py`. Covers:

- HMDA layout approvals (Kokapet, Adibatla, Pharma City)
- NHAI highway projects (NH-44, NH-65, ORR Phase II, RRR)
- HMRL metro extensions (Phase 2 airport, Phase 3 Ghatkesar, Kokapet node)
- Industrial parks (Pharma City, Aerospace Park, Genome Valley, Fab City, Sangareddy Auto, Ibrahimpatnam Hub)

## Regenerating the Dataset

To wipe and reseed:

```bash
# Drop and recreate via Alembic
alembic downgrade base
alembic upgrade head
python -m seed.seed
```

To regenerate only listings (keep growth signals):

```bash
python -c "from seed.seed import seed_listings; import asyncio; asyncio.run(seed_listings())"
```

## Validation

The seed script validates before exiting:

1. **Radius search**: listings within 5km of Kokapet center
2. **Bounding box**: listings within Hyderabad metro extent
3. **Nearest-N**: 10 nearest listings to a fixed coordinate
4. **Embedding check**: all listings have non-null embeddings of dimension 384
