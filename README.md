# Cinema Explorer

> Explore movies and series through time, language, and culture.

Cinema Explorer is an exploratory cinema and television discovery platform engineered to transcend algorithmic echo chambers. Instead of generic collaborative filtering or opaque recommendation models, Cinema Explorer structures global audiovisual media across historical eras, linguistic traditions, and cultural production movements.

---

## The Core Product Concept

The platform's discovery architecture follows an intuitive, deterministic progression:

```
TIME ──▶ DECADE ──▶ YEAR ──▶ LANGUAGE / REGION ──▶ INDUSTRY / GENRE ──▶ DISCOVER
```

1. **Time & Era**: Select historical epochs from classic golden ages (1950s–1980s) to contemporary releases (2020s).
2. **Year Drilldown**: Narrow down to specific release years within any chosen decade.
3. **Language & Region**: Explore across 8 primary cultural discovery traditions—Telugu, Hindi, Tamil, Malayalam, Kannada, English, Japanese, and Korean—as well as global world languages.
4. **Industry & Genre**: Filter through film industries (Tollywood, Bollywood, Kollywood, Mollywood, Sandalwood, Hollywood, Anime Industry, Korean Cinema) and cinematic genres.
5. **Discover**: Browse deterministic, mathematically explainable catalog results.

---

## V1 Feature Highlights

- **Movies + TV Series Discovery**: Seamless browsing across feature films and serialized television with unified taxonomy filtering.
- **Chronological Time Exploration**: Decade pills and exact-year drilldowns with live title distribution counts.
- **Cultural Language & Industry Taxonomies**: Multi-industry classification mapping titles to regional cinematic ecosystems (South Asian regional cinema, East Asian cinema, Western cinema).
- **Anime as a First-Class Discovery Category**: Japanese animation is integrated as an organic discovery dimension and spotlight hub—free of binary "Yes/No" labeling.
- **8-Tier Deterministic Search Relevance**: Keyword searches rank via a multi-level SQL precedence hierarchy (Exact title → Prefix match → Word boundary match → Alternate title exact match → Alternate title prefix match → Case-insensitive title substring → Alternate title substring → Tie-breaker).
- **Bayesian Weighted Rating**: Eliminates false extremes from raw averages using an empirical catalog formula:
  $$\text{WR} = \left(\frac{v}{v + 250}\right) \cdot R + \left(\frac{250}{v + 250}\right) \cdot 6.86$$
  Critically acclaimed cinematic masterworks (*Breaking Bad*, *Chernobyl*, *Interstellar*, *Spirited Away*, *RRR*) naturally lead top-rated rankings.
- **Deterministic Sort Modes**: Popularity, Bayesian Weighted Rating, Most Voted, Newest Releases, Oldest Releases, and Alphabetical (Title A–Z) with secondary tie-breakers (`Title.id.asc()`) ensuring reproducible pagination.
- **Featured Discovery Hubs**: Curated collections for *Trending Worldwide*, *Indian Regional Cinema*, *Anime Spotlight*, *Critically Acclaimed Masterpieces*, and *Global Highlights*.
- **Where to Watch in India (OTT)**: Verified streaming availability categorized into Streaming, Rent, and Buy with official platform badges.
- **Smart Google Fallback**: When streaming provider records are unavailable for a title, a pre-composed Google search fallback link (`[Title] [Year] [Type] where to watch`) provides immediate access to updated web availability.
- **Responsive Multi-Device UI**: Handcrafted dark theme tested across mobile (375px, 390px), tablet (768px), and desktop (1280px, 1440px) with zero horizontal overflow.
- **Production SEO**: Native Next.js 15 metadata routes generating `robots.txt` and a complete `sitemap.xml` indexing all 5,138 canonical URLs, complete with OpenGraph and Twitter cards.
- **Accessibility (WCAG 2.1 AA)**: Accessible forms with `role="search"`, form control associations, `<nav aria-label="Catalog pagination">`, screen-reader disclosures on external links (`opens in a new tab`), and high-contrast focus rings.

---

## Current Catalog Dataset

The Cinema Explorer database contains a verified, deduplicated media catalog:

| Metric | Count | Details |
| :--- | :---: | :--- |
| **Total Titles** | **5,135** | Fully normalized and classified |
| **Feature Films (Movies)** | **3,470** | Historical and contemporary global cinema |
| **Television Series** | **1,665** | Multi-season series with season metadata |
| **Anime Titles** | **855** | Feature films and serialized anime |
| **India OTT Watch Offers** | **11,444** | Streaming, rent, and buy options across 60 platforms |
| **Classified Industries** | **100%** | All 5,135 titles mapped to regional/cultural industries |
| **Orphan Records** | **0** | Perfect foreign key and relational referential integrity |

---

## Architecture

Cinema Explorer follows a clean, decoupled architecture:

```text
┌────────────────────────────────────────────────────────┐
│                   The Movie Database                   │
│                       (TMDB API)                       │
└───────────────────────────┬────────────────────────────┘
                            │  Ingestion CLI & Pipelines
                            ▼
┌────────────────────────────────────────────────────────┐
│           Python Ingestion & Classification            │
│  (Data Normalization, Industry Mappings, Validation)   │
└───────────────────────────┬────────────────────────────┘
                            │  Idempotent Upserts
                            ▼
┌────────────────────────────────────────────────────────┐
│                 PostgreSQL 16 Database                 │
│   (Relational Schema, 6 Secondary Indexes, Alembic)    │
└───────────────────────────┬────────────────────────────┘
                            │  SQLAlchemy 2.0 / Joinedload
                            ▼
┌────────────────────────────────────────────────────────┐
│                    FastAPI Backend                     │
│    (REST API, Bayesian Ranking, Sanitized Logging)     │
└───────────────────────────┬────────────────────────────┘
                            │  HTTP / JSON (<100ms Latency)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Next.js 15 Frontend                  │
│       (App Router, React 19, Tailwind CSS, SEO)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
                       User Browser
```

---

## Technology Stack

- **Frontend**: [Next.js 15](https://nextjs.org/) (App Router), [React 19](https://react.dev/), [Tailwind CSS](https://tailwindcss.com/), [TypeScript](https://www.typescriptlang.org/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/), [Pydantic v2](https://docs.pydantic.dev/), [Uvicorn](https://www.uvicorn.org/)
- **Database & Migrations**: [PostgreSQL 16](https://www.postgresql.org/), [Alembic](https://alembic.sqlalchemy.org/)
- **Data Ingestion**: Python 3.12, HTTPX, Backoff retries, Checkpointing
- **Containerization**: [Docker Compose](https://docs.docker.com/compose/)

---

## Repository Structure

```text
cinema-explorer/
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database migration versions
│   ├── app/
│   │   ├── api/              # REST route controllers (/api/v1)
│   │   ├── core/             # Configuration & SensitiveDataFilter logging
│   │   ├── db/               # Engine & session factories
│   │   ├── models/           # SQLAlchemy 2.0 mapped models
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   └── services/         # Catalog, taxonomy & discovery services
│   ├── tests/                # Pytest test suite (53 tests)
│   ├── requirements.txt
│   └── README.md
├── frontend/                 # Next.js 15 Web Application
│   ├── app/                  # App Router pages, layouts, robots.ts, sitemap.ts
│   ├── components/           # UI components (Stepper, Cards, Nav, Badges)
│   ├── lib/                  # API client, types, constants
│   ├── public/               # Logos and static assets
│   ├── package.json
│   └── README.md
├── ingestion/                # Data Ingestion & Normalization Pipeline
│   ├── classifiers/          # Rule-based anime and industry classifiers
│   ├── normalizers/          # Movie/TV and date precision normalizers
│   ├── services/             # TMDB discovery & ingestion services
│   ├── tmdb/                 # Rate-limited HTTPX TMDB API client
│   ├── tests/                # Ingestion test suite (63 tests)
│   └── README.md
├── docker-compose.yml        # PostgreSQL 16 local database container
├── .env.example              # Root environment variable template
├── .gitignore                # Git ignore rules (includes scratch/ and secrets)
└── README.md                 # Project documentation
```

---

## Getting Started

### Prerequisites

- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** and `npm`
- **Docker** and **Docker Compose**
- *(Optional)* TMDB API Key / Access Token (only required if running fresh ingestion)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/cinema-explorer.git
cd cinema-explorer
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Review `.env`:
```env
DATABASE_URL=postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer
TMDB_BASE_URL=https://api.themoviedb.org/3
TMDB_IMAGE_BASE_URL=https://image.tmdb.org/t/p
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Optional: Required only when running the ingestion CLI to fetch fresh TMDB data
# TMDB_API_KEY=your_api_key_here
# TMDB_ACCESS_TOKEN=your_v4_bearer_token_here
```

Configure frontend environment:
```bash
cp frontend/.env.example frontend/.env
```

### 3. Start PostgreSQL Database

Launch the database container via Docker Compose:

```bash
docker compose up -d
```

Verify that PostgreSQL is healthy:
```bash
docker compose ps
```

### 4. Run Database Migrations

Initialize a Python virtual environment and run Alembic migrations:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
cd ..
```

### 5. Start the FastAPI Backend

Run Uvicorn from the project root:

```bash
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify backend health:
```bash
curl http://localhost:8000/api/v1/health
# Returns: {"status":"healthy","database":"connected","version":"1.0.0"}
```

API documentation will be accessible at: `http://localhost:8000/docs`.

### 6. Start the Next.js Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The web application is now running at `http://localhost:3000`.

To build and run in production mode:
```bash
cd frontend
npm run build
npm run start
```

---

## API Overview

All endpoints are versioned under `/api/v1`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service and database connectivity health check |
| `GET` | `/api/v1/titles` | Paginated catalog discovery with multi-faceted filtering, search, and sorting |
| `GET` | `/api/v1/titles/{id}` | Complete title metadata, cast/crew, seasons, and India watch providers |
| `GET` | `/api/v1/titles/tmdb/{tmdb_id}` | Title lookup by TMDB ID |
| `GET` | `/api/v1/titles/sitemap-entries` | Lightweight `id` and `updated_at` tuples for sitemap generation |
| `GET` | `/api/v1/discovery/featured` | Curated discovery rows (Trending, Top Rated, Regional, Anime, Global) |
| `GET` | `/api/v1/taxonomies/languages` | Supported discovery languages with catalog counts |
| `GET` | `/api/v1/taxonomies/genres` | Available genres with catalog counts |
| `GET` | `/api/v1/taxonomies/industries` | Regional cinema industries with catalog counts |
| `GET` | `/api/v1/taxonomies/countries` | Production countries with catalog counts |
| `GET` | `/api/v1/taxonomies/decades` | Release decades with catalog counts |

---

## Running Automated Tests

Cinema Explorer includes comprehensive test suites across backend and ingestion pipelines:

### Backend Pytest Suite (53 Tests)
Verifies API routes, parameter validations, Bayesian ranking, search relevance, pagination tie-breakers, and sanitized error handlers:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/
```

### Ingestion Pytest Suite (63 Tests)
Verifies rate-limiting, retry exponential backoff, credential redaction filters, anime classifiers, and idempotent database repositories:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest ingestion/tests/
```

### Frontend Production Build
Verifies TypeScript compilation, Tailwind CSS bundling, and static metadata route generation:
```bash
cd frontend && npm run build
```

---

## Performance & Indexing

Cinema Explorer V1 achieves sub-100ms average response times natively through PostgreSQL secondary indexes without external caching layers:

- `ix_titles_lower_title`: Index on `lower(title)` for case-insensitive search and alphabetical sorting.
- `ix_titles_tmdb_vote_count`: Index on `tmdb_vote_count DESC NULLS LAST` for the Most Voted sort mode.
- `ix_title_genres_genre_id`, `ix_title_industries_industry_id`, `ix_title_languages_language_id`, `ix_title_countries_country_id`: Secondary indexes on junction table foreign keys to eliminate sequential scans during faceted filtering.
- **Relevance Hierarchy SubPlan Optimization**: Alternate title relevance scoring avoids redundant table scans.
- **Eager Loading**: Singular taxonomy and provider relationships use SQLAlchemy `joinedload`, eliminating N+1 query overhead on title detail lookups.

Native benchmark performance:
- Keyword search: **~69ms**
- Faceted catalog filtering: **~15–28ms**
- Title detail lookup: **~23ms**
- Next.js page generation: **~4–36ms**

---

## Security & Credential Protection

- **Server-Side Isolation**: TMDB credentials and database connection strings are strictly consumed server-side. The frontend environment is limited to public API and site URLs (`NEXT_PUBLIC_*`).
- **Sensitive Data Logging Filter**: Both the FastAPI application (`app.core.logging`) and ingestion pipeline (`ingestion.tmdb.client`) implement an active `SensitiveDataFilter` that automatically redacts API keys, bearer tokens, and credentials from all logs.
- **Bearer Authentication**: Outgoing TMDB requests prioritize HTTP `Authorization: Bearer <token>` headers to keep secrets out of query strings.
- **Sanitized Error Responses**: Global exception handlers prevent Python tracebacks or database connection exceptions from leaking to client responses.
- **Git Hygiene**: Environment files (`.env`, `.env.local`, `frontend/.env`) and temporary benchmark artifacts (`scratch/`) are gitignored.

---

## Attribution & Data Disclaimers

### The Movie Database (TMDB)
This product uses the TMDB API but is not endorsed or certified by TMDB.

Cinema Explorer sources metadata, cast and crew credits, posters, and backdrops from TMDB under the TMDB API terms of use. Cinema Explorer does not claim ownership of TMDB metadata or images.

### JustWatch
Streaming availability and Where-to-Watch provider data ("Streaming", "Rent", "Buy") are powered by **JustWatch** through TMDB's watch-provider integration. All provider logos and platform names are trademarks of their respective owners.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
