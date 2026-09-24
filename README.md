# Cinema Explorer

> **Explore movies and series through time, language, and culture.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.1-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-122%20passed-brightgreen?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Madhav0976/cinema-explorer/blob/main/LICENSE)

Cinema Explorer is an open-source cinema and television discovery platform engineered to transcend algorithmic echo chambers. Rather than relying on opaque recommendation engines or personal data tracking, Cinema Explorer organizes global audiovisual media along historical epochs, linguistic traditions, and cultural production movements.

From South Asian regional masterworks (Tollywood, Bollywood, Kollywood, Mollywood, Sandalwood) and East Asian cinema (Japanese anime, Korean cinema) to Hollywood classics and international cinema highlights, Cinema Explorer provides a deterministic, structured pathway to explore world cinema.

---

## Table of Contents

- [Core Discovery Philosophy](#core-discovery-philosophy)
- [Key Features](#key-features)
- [Product & UX Flow](#product--ux-flow)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Verified Catalog Dataset](#verified-catalog-dataset)
- [Search & Ranking Engine](#search--ranking-engine)
- [Where to Watch (India OTT)](#where-to-watch-india-ott)
- [API Overview](#api-overview)
- [Repository Structure](#repository-structure)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Security & Credential Protection](#security--credential-protection)
- [SEO & Accessibility](#seo--accessibility)
- [Production Deployment](#production-deployment)
- [Contributing](#contributing)
- [Attributions & Legal Disclaimers](#attributions--legal-disclaimers)
- [License](#license)

---

## Core Discovery Philosophy

Most streaming discovery systems rely on opaque user profiles and engagement-maximizing recommendation algorithms. Cinema Explorer adopts a deterministic exploration model that puts the audience in control:

```
TIME ──▶ DECADE ──▶ YEAR ──▶ LANGUAGE / REGION ──▶ INDUSTRY / GENRE ──▶ DISCOVER
```

1. **Time**: Select historical eras ranging from vintage golden ages (1950s–1980s) to contemporary releases (2020s).
2. **Year**: Drill down into exact release years with real-time title distribution counts.
3. **Language & Region**: Filter across 8 primary cultural traditions (Telugu, Hindi, Tamil, Malayalam, Kannada, English, Japanese, Korean) as well as global world languages.
4. **Industry & Genre**: Focus on regional film industries (Tollywood, Bollywood, Kollywood, Mollywood, Sandalwood, Hollywood, Anime Industry, Korean Cinema) combined with thematic genres.
5. **Discover**: Browse mathematically explainable, reproducible catalog results with zero hidden biases.

---

## Key Features

- **Unified Movies & Television Catalog**: Explore both feature films and serialized multi-season television under a synchronized taxonomy system.
- **Anime as a First-Class Category**: Japanese animation is integrated organically as a cultural discovery dimension and dedicated spotlight hub—never reduced to a binary flag.
- **8-Tier Deterministic Search Relevance**: Full-text catalog search driven by a multi-level SQL precedence hierarchy (exact title match, prefix match, word-boundary regex, alternate titles, and popularity tie-breakers).
- **Bayesian Weighted Ratings**: Eliminates small-sample rating distortion ($C = 6.86$, $m = 250$), ensuring critically acclaimed masterworks naturally lead quality-sorted results without arbitrary curation.
- **Deterministic Multi-Mode Sorting**: Sort by Popularity, Bayesian Weighted Rating, Most Voted, Release Date (Newest/Oldest), and Title (A–Z), backed by strict secondary tie-breakers (`Title.id.asc()`) for consistent pagination.
- **Curated Discovery Hubs**: Instant access to curated movements: *Trending Worldwide*, *Indian Regional Cinema*, *Anime Spotlight*, *Critically Acclaimed Masterpieces*, and *Global Highlights*.
- **India OTT Availability (Where to Watch)**: Up-to-date streaming platform listings categorized into Streaming, Rent, and Buy, with direct watch provider links.
- **Smart Google Fallback**: Dynamic web fallback (`[Title] [Year] [Type] where to watch`) provides immediate access to updated streaming data when regional catalog records are unlisted.
- **Production-Grade Next.js 15 Frontend**: Built with React 19, Tailwind CSS, custom dark mode, and zero layout shift. Title cards maintain strict physical dimensions on hover with no intrusive scale transforms.
- **Full WCAG 2.1 AA Accessibility**: Semantic HTML landmarks, accessible modal controls, high-contrast focus indicators, keyboard-traversable stepper filters, and screen-reader disclosures.
- **Native Next.js SEO**: Dynamic `sitemap.xml` indexing all 5,138 canonical routes, structured OpenGraph / Twitter metadata cards, and clean canonical URL alternates.
- **Hardened Security Architecture**: Credential-sanitized logging filters, strict server-side TMDB credential isolation, exact-origin CORS validation, and zero credentials in client-side code.

---

## Product & UX Flow

```mermaid
flowchart LR
    A["Homepage\n(Hero & CTAs)"] --> B["Curated Hubs\n(Trending, Regional, Anime)"]
    A --> C["Guided Explorer\n(Interactive Stepper)"]
    B --> D["Catalog Grid\n(Faceted Filters & Sort)"]
    C --> D
    D --> E["Title Detail Page\n(/title/:id)"]
    E --> F["Where to Watch\n(Streaming, Rent, Buy)"]
    E --> G["Google Fallback\n(External Search)"]
```

---

## Architecture

Cinema Explorer enforces a strict separation of concerns across three distinct tiers:

```mermaid
flowchart TB
    subgraph DataPipeline ["Data Ingestion Pipeline (Offline CLI)"]
        TMDB["The Movie Database\n(TMDB API v3/v4)"] --> Client["TMDBClient\n(Rate-Limited, Retries, Bearer Auth)"]
        Client --> Norm["Normalizers & Classifiers\n(Anime & Industry Detection)"]
        Norm --> Repo["TitleRepository\n(Idempotent Upserts)"]
    end

    subgraph DatabaseTier ["Storage Layer"]
        Repo --> PG[("PostgreSQL 16 Database\n(17 Tables, 51 Indexes, Alembic)")]
    end

    subgraph BackendTier ["FastAPI Application (Render)"]
        PG --> Engine["SQLAlchemy 2.0 Engine\n(psycopg3, Connection Pool)"]
        Engine --> Services["Catalog & Discovery Services\n(Bayesian Ranking, 8-Tier Search)"]
        Services --> API["FastAPI REST Routes\n(/api/v1/*, CORS, Health Check)"]
    end

    subgraph FrontendTier ["Next.js Application (Vercel)"]
        API --> ClientFetch["Next.js 15 App Router\n(React 19, Server & Client Components)"]
        ClientFetch --> Browser["End-User Browser\n(Responsive UI, WCAG AA, SEO)"]
    end

    classDef primary fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef secondary fill:#0f172a,stroke:#64748b,stroke-width:1px,color:#cbd5e1;
    class TMDB,PG,API,Browser primary;
    class Client,Norm,Repo,Engine,Services,ClientFetch secondary;
```

> [!NOTE]
> The runtime web application queries the PostgreSQL database exclusively. Zero external TMDB requests are dispatched during end-user browsing, guaranteeing deterministic response times under 100ms.

---

## Technology Stack

### Frontend
- **Framework**: [Next.js 15.1](https://nextjs.org/) (App Router, Server-Side Rendering & Client Components)
- **UI Library**: [React 19.0](https://react.dev/)
- **Styling**: [Tailwind CSS 3.4](https://tailwindcss.com/) with PostCSS & Autoprefixer
- **Type Safety**: [TypeScript 5](https://www.typescriptlang.org/)

### Backend
- **Framework**: [FastAPI 0.115](https://fastapi.tiangolo.com/) (ASGI)
- **Server**: [Uvicorn 0.30](https://www.uvicorn.org/) (Standard async runtime)
- **ORM & Query Builder**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Mapped declarative models, joinedload strategies)
- **Database Driver**: [psycopg 3.2](https://www.psycopg.org/psycopg3/) (Binary async/sync PostgreSQL driver)
- **Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) & [pydantic-settings](https://github.com/pydantic/pydantic-settings)
- **Logging**: Custom `SensitiveDataFilter` redacting API keys and Bearer tokens

### Database
- **Engine**: [PostgreSQL 16](https://www.postgresql.org/) (Alpine-based container locally, managed PostgreSQL in production)
- **Migrations**: [Alembic 1.13](https://alembic.sqlalchemy.org/) (Linear migration history)
- **Indexing**: 51 indexes covering primary keys, foreign keys, compound search, and sorting columns

### Data & Ingestion
- **Runtime**: Python 3.12
- **HTTP Client**: [HTTPX 0.27](https://www.python-httpx.org/) (Connection pooling, exponential backoff retries)
- **Classifiers**: Rule-based taxonomy engines for Indian regional film industries and Japanese anime

---

## Verified Catalog Dataset

The Cinema Explorer database contains an audited, normalized catalog:

| Metric | Verified Count | Notes |
| :--- | :---: | :--- |
| **Total Titles** | **5,135** | Fully deduplicated `(tmdb_id, type)` entries |
| **Feature Films (Movies)** | **3,470** | Classical and modern global cinema |
| **Television Series** | **1,665** | Multi-season web series and broadcast television |
| **Anime Titles** | **855** | Feature anime films and serialized anime |
| **India OTT Watch Offers** | **11,444** | Streaming, rent, and buy options across 60+ platforms |
| **Classified Industries** | **100%** | Every title mapped to regional/cultural ecosystems |
| **Cast & Crew Credits** | **110,158** | Actors, directors, writers, and key creators |
| **Alternate Titles** | **36,656** | Regional, translated, and transliterated titles |
| **People Records** | **42,087** | Normalized actors and filmmakers |
| **Seasons** | **7,331** | TV season records with episode counts and air dates |
| **Orphan Foreign Keys** | **0** | Verified referential integrity across all 15 relations |

---

## Search & Ranking Engine

### 8-Tier SQL Search Relevance Hierarchy
Search keywords are evaluated deterministically using PostgreSQL expressions without third-party search engines:

1. **Tier 1 — Exact Title Match**: Full case-insensitive string equality (`lower(title) = :q`).
2. **Tier 2 — Title Prefix Match**: Title begins with search term (`lower(title) LIKE :q || '%'`).
3. **Tier 3 — Word Boundary Match**: Regex match on word starts (`lower(title) ~ ('(^|[^a-z0-9])' || :regex_q)`).
4. **Tier 4 — Alternate Title Exact Match**: Exact match on localized or transliterated names.
5. **Tier 5 — Alternate Title Prefix Match**: Alternate title begins with search term.
6. **Tier 6 — Case-Insensitive Substring Match**: Title contains query substring.
7. **Tier 7 — Alternate Title Substring Match**: Alternate title contains query substring.
8. **Tier 8 — Deterministic Tie-Breaker**: Secondary sort on `tmdb_popularity DESC`, `id ASC`.

### Bayesian Weighted Rating
Raw average ratings often produce skewed rankings for titles with very few votes. Cinema Explorer applies an empirical Bayesian weighted rating formula calculated at query time:

$$\text{WR} = \left(\frac{v}{v + m}\right) \cdot R + \left(\frac{m}{v + m}\right) \cdot C$$

- $v$: Title vote count (`Title.tmdb_vote_count`)
- $R$: Title average rating (`Title.tmdb_rating`)
- $m$: Minimum vote threshold (**250 votes**)
- $C$: Global catalog mean score (**6.86**)

Titles with few votes shrink toward the catalog average ($6.86$), while titles with substantial vote counts converge toward their true public rating.

---

## Where to Watch (India OTT)

Cinema Explorer maps streaming, rental, and purchasing availability tailored to the Indian media ecosystem:

- **Streaming (Flatrate / Free / Ads)**: Netflix, Amazon Prime Video, Disney+ Hotstar, JioCinema, Zee5, SonyLIV, Apple TV+, Sun NXT, aha, and more.
- **Rent & Buy**: Google Play Movies, Apple iTunes, YouTube Movies, Amazon Video.
- **Smart Google Fallback**: For titles without listed India OTT records, an automated query button (`[Title] [Year] [Type] where to watch`) launches an external Google search, ensuring users always find up-to-date availability.

---

## API Overview

The FastAPI backend exposes versioned REST endpoints under `/api/v1`:

```
GET /api/v1/health                       Database connectivity and service health check
GET /api/v1/titles                       Paginated catalog exploration (filtering, search, sort)
GET /api/v1/titles/{id}                  Comprehensive metadata, cast/crew, seasons, OTT offers
GET /api/v1/titles/tmdb/{tmdb_id}        Metadata lookup by TMDB ID
GET /api/v1/titles/sitemap-entries       Lightweight id/timestamp pairs for SEO sitemap generation
GET /api/v1/discovery/featured           Curated discovery rows (Trending, Regional, Anime, Top Rated)
GET /api/v1/taxonomies/languages         Supported languages with catalog title counts
GET /api/v1/taxonomies/genres            Available genres with catalog title counts
GET /api/v1/taxonomies/industries        Film industries with catalog title counts
GET /api/v1/taxonomies/countries         Production countries with catalog title counts
GET /api/v1/taxonomies/decades           Release decades with catalog title counts
```

Interactive OpenAPI documentation is available locally at `http://localhost:8000/docs` or `http://localhost:8000/redoc`.

---

## Repository Structure

```text
cinema-explorer/
├── backend/                  # FastAPI Application
│   ├── alembic/              # Linear database migrations (3 versions)
│   ├── app/
│   │   ├── api/              # Route controllers (/api/v1)
│   │   ├── core/             # Configuration, CORS parsing, sanitized logging
│   │   ├── db/               # SQLAlchemy engine & session factory
│   │   ├── models/           # Declarative mapped relational models
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   └── services/         # Catalog query builder, Bayesian ranker, search service
│   ├── tests/                # Pytest test suite (59 tests)
│   ├── alembic.ini
│   ├── requirements.txt
│   └── README.md
├── frontend/                 # Next.js 15 Web Application
│   ├── app/                  # App Router: layout, catalog, featured, title detail, sitemap
│   ├── components/           # UI: Stepper, TitleCard, Navbar, Footer, Badges, Icons
│   ├── lib/                  # Fetch client, TypeScript interfaces, constants
│   ├── public/               # Brand logos and icons
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── README.md
├── ingestion/                # Data Pipeline & Ingestion CLI
│   ├── classifiers/          # Industry and anime classification logic
│   ├── normalizers/          # Metadata and date precision normalizers
│   ├── services/             # TMDB discovery and title ingestion workflows
│   ├── tmdb/                 # Rate-limited HTTPX client with bearer authentication
│   ├── tests/                # Ingestion test suite (63 tests)
│   ├── cli.py                # Command-line entrypoint for seed/title imports
│   └── README.md
├── docs/                     # Architecture, API specifications, and operations guides
├── docker-compose.yml        # PostgreSQL 16 Alpine local database service
├── .env.example              # Sanitized configuration template
├── .gitignore                # Git exclusions (secrets, scratch artifacts, virtual environments)
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

---

## Local Development Setup

### Prerequisites
- **Python**: 3.10+ (Python 3.12 recommended)
- **Node.js**: 18+ and `npm`
- **Docker**: Docker Engine and Docker Compose
- *(Optional)* TMDB API Key / Access Token (only needed for running ingestion CLI)

### 1. Clone the Repository
```bash
git clone https://github.com/Madhav0976/cinema-explorer.git
cd cinema-explorer
```

### 2. Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```

Ensure `.env` matches your local environment:
```env
DATABASE_URL=postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
TMDB_BASE_URL=https://api.themoviedb.org/3
TMDB_IMAGE_BASE_URL=https://image.tmdb.org/t/p
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

Configure frontend variables:
```bash
cp frontend/.env.example frontend/.env
```

### 3. Start PostgreSQL Database
```bash
docker compose up -d
```

Verify that the PostgreSQL container is running:
```bash
docker compose ps
```

### 4. Apply Database Migrations
Create a virtual environment and apply Alembic migrations:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
cd ..
```

### 5. Start the FastAPI Backend
From the repository root:
```bash
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify backend health:
```bash
curl http://localhost:8000/api/v1/health
# Response: {"status":"healthy","database":"connected","version":"1.0.0"}
```

### 6. Start the Next.js Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```

The frontend application will be running at [http://localhost:3000](http://localhost:3000).

---

## Environment Variables

| Variable | Scope | Default / Placeholder | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Backend / Ingestion | `postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer` | PostgreSQL connection URI |
| `CORS_ORIGINS` | Backend | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated allowed origins for CORS |
| `NEXT_PUBLIC_API_URL` | Frontend | `http://localhost:8000` | Base URL of the FastAPI backend service |
| `NEXT_PUBLIC_SITE_URL` | Frontend | `http://localhost:3000` | Canonical site origin for SEO metadata & sitemaps |
| `TMDB_BASE_URL` | Ingestion | `https://api.themoviedb.org/3` | TMDB API v3 base endpoint |
| `TMDB_IMAGE_BASE_URL` | Ingestion / Frontend | `https://image.tmdb.org/t/p` | TMDB media CDN origin |
| `TMDB_API_KEY` | Ingestion *(Optional)* | *(empty)* | TMDB v3 API key (only for running ETL CLI) |
| `TMDB_ACCESS_TOKEN` | Ingestion *(Optional)* | *(empty)* | TMDB v4 read access token |

---

## Testing & Quality Assurance

Cinema Explorer maintains **122 automated Python tests** across backend and ingestion pipelines:

### Backend Test Suite (59 Tests)
Verifies catalog filtering, 8-tier search relevance, Bayesian ranking calculations, pagination windowing, configurable CORS origins, and health endpoints:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/
```

### Ingestion Test Suite (63 Tests)
Verifies TMDB client rate-limiting, exponential backoff retries, sensitive data redaction, anime classifiers, industry normalizers, and idempotent database repositories:
```bash
PYTHONPATH=.:backend backend/.venv/bin/pytest ingestion/tests/
```

### Frontend Build Verification
Verifies strict TypeScript type-checking, CSS bundle optimization, and sitemap generation:
```bash
cd frontend
npm run build
```

---

## Security & Credential Protection

- **Server-Side Isolation**: TMDB keys and database credentials are never bundled into client-side code. The browser interacts exclusively with public API endpoints.
- **Sensitive Data Logging Redaction**: Both the FastAPI application (`app.core.logging`) and ingestion pipeline implement an active `SensitiveDataFilter` that scrubs `api_key`, `token`, `password`, and `Bearer` headers from all logs.
- **Exact-Origin CORS Validation**: Starlette `CORSMiddleware` validates exact comma-separated origins. Wildcard `*` origins are strictly blocked when credentials are enabled.
- **Git Hygiene**: Environment files (`.env`, `frontend/.env`) and temporary operational artifacts (`scratch/`) are strictly excluded by `.gitignore`.
- **Sanitized Exception Handling**: Global exception handlers suppress internal Python tracebacks and SQL errors, returning uniform JSON error responses to clients.

---

## SEO & Accessibility

- **Canonical URL Indexing**: Built-in Next.js 15 App Router metadata routes generate a dynamic `sitemap.xml` covering all 5,138 canonical pages (`/`, `/catalog`, `/featured`, and all `/title/:id` routes).
- **Search Engine Directives**: Clean `robots.txt` allowing primary indexable content while disallowing dynamic search queries (`/catalog?*`) to prevent duplicate indexing.
- **Social Sharing**: Automated OpenGraph and Twitter Summary Cards with localized posters, titles, and release years.
- **WCAG 2.1 AA Compliance**:
  - Semantic landmark regions (`<header>`, `<main>`, `<footer>`, `<nav aria-label="Catalog pagination">`).
  - Search inputs associated with explicit labels and `role="search"`.
  - External links clearly labeled for assistive devices (`opens in a new tab`).
  - Strict focus indicators and contrast ratios on all interactive buttons and dropdowns.

---

## Production Deployment

Cinema Explorer V1 is engineered for cloud deployment across decoupled platforms:

- **Frontend**: [Vercel](https://vercel.com/) (Next.js serverless and edge runtime, Root Directory: `frontend`).
- **Backend**: [Render](https://render.com/) (Python 3.12 Web Service, Root Directory: `backend`, Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
- **Database**: [Render PostgreSQL](https://render.com/docs/databases) (Managed PostgreSQL 16 with internal private network connectivity).

The runtime web service queries PostgreSQL directly. It requires no TMDB credentials, external caches, or third-party search engines, ensuring reliable, low-cost operations.

---

## Contributing

Contributions to Cinema Explorer are welcome! Please follow these guidelines:

1. **Fork the Repository**: Create a personal fork on GitHub.
2. **Create a Feature Branch**: `git checkout -b feature/your-feature-name`
3. **Commit Cleanly**: Follow conventional commit guidelines (`feat: ...`, `fix: ...`, `docs: ...`).
4. **Run the Test Suites**: Ensure all 122 tests pass before submitting changes:
   ```bash
   PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/
   PYTHONPATH=.:backend backend/.venv/bin/pytest ingestion/tests/
   cd frontend && npm run build
   ```
5. **Open a Pull Request**: Submit your PR with a clear summary of modifications and test verification.

---

## Attributions & Legal Disclaimers

### The Movie Database (TMDB)
> **"This product uses the TMDB API but is not endorsed or certified by TMDB."**

Cinema Explorer utilizes TMDB metadata, cast/crew credits, poster images, and backdrops under the TMDB API Terms of Use. Cinema Explorer does not claim ownership of TMDB metadata or copyrighted imagery.

### JustWatch
Streaming availability and provider information ("Streaming", "Rent", "Buy") are powered by **JustWatch** via TMDB's watch-provider integration. All provider names and logos are trademarks of their respective owners.

---

## License

This project is open-source software licensed under the **MIT License**.  
See the full license terms in the [LICENSE](https://github.com/Madhav0976/cinema-explorer/blob/main/LICENSE) file.
