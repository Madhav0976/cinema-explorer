# Cinema Explorer Backend

Production-grade FastAPI backend service powering Cinema Explorer's catalog exploration, deterministic search relevance, and taxonomy aggregations.

---

## Responsibilities

- **Catalog & Exploration Service**: Dynamic query builder supporting simultaneous filtering by content type, anime category, language, industry, genre, year, decade, rating, and vote counts.
- **Deterministic Search Relevance**: 8-tier SQL relevance hierarchy prioritizing exact titles, prefix matches, word boundaries, and alternate names without external search engines.
- **Query-Time Bayesian Ranking**: Computes mathematically explainable weighted ratings ($WR = \frac{v}{v+250} \cdot R + \frac{250}{v+250} \cdot 6.86$) on the fly in PostgreSQL.
- **Relational Data Modeling**: SQLAlchemy 2.0 mapped models with eager joinedload strategies eliminating N+1 queries.
- **Sanitized Logging & Resiliency**: Active `SensitiveDataFilter` redacting API keys and Bearer tokens, with global exception handling preventing internal traceback leakage.

---

## Setup & Running

From the project root or `backend/` directory:

### 1. Initialize Virtual Environment & Install Dependencies
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Database Migrations
Apply all schema definitions and performance secondary indexes:
```bash
alembic upgrade head
```

### 3. Start Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API is available at `http://localhost:8000`. OpenAPI Swagger documentation is at `http://localhost:8000/docs`.

---

## Environment Variables

Configured in `.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer` | PostgreSQL connection string using psycopg3 |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated allowed origins for CORS |

---

## Major API Route Groups

All endpoints are versioned under `/api/v1`:

### 1. Titles & Catalog (`/api/v1/titles`)
- `GET /api/v1/titles`: Multi-parameter title discovery with pagination and sorting.
- `GET /api/v1/titles/{id}`: Detailed title metadata, cast/crew, seasons, alternate titles, external IDs, and India watch providers.
- `GET /api/v1/titles/tmdb/{tmdb_id}`: Title metadata lookup by TMDB ID.
- `GET /api/v1/titles/sitemap-entries`: High-performance, lightweight ID and timestamp stream for SEO sitemap generation.

### 2. Taxonomies (`/api/v1/taxonomies`)
- `GET /api/v1/taxonomies/languages`: Language codes and names with live catalog counts.
- `GET /api/v1/taxonomies/genres`: Film and television genres with live catalog counts.
- `GET /api/v1/taxonomies/industries`: Regional cinema industries with live catalog counts.
- `GET /api/v1/taxonomies/countries`: Production countries with live catalog counts.
- `GET /api/v1/taxonomies/decades`: Release decades with live catalog counts.

### 3. Discovery Hubs (`/api/v1/discovery`)
- `GET /api/v1/discovery/featured`: Pre-curated collections for Trending Worldwide, Top Rated (Bayesian), Indian Regional Cinema, Anime Spotlight, and Global Highlights.

### 4. Health Check
- `GET /health` and `GET /api/v1/health`: Sanitized database connectivity check returning `{"status": "healthy", "database": "connected", "version": "1.0.0"}`.

---

## Running Automated Backend Tests

Run the full pytest suite (53 tests):
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/
```
Verifies endpoint responses, validation constraints, Bayesian rating behavior, search relevance, pagination determinism, and error handling.
