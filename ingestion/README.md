# Cinema Explorer Ingestion Pipeline

The ingestion pipeline handles the fetching, normalization, classification, validation, and idempotent persistence of movie and TV metadata from The Movie Database (TMDB) API into PostgreSQL.

---

## 1. Setup & Environment Variables

The pipeline reads configuration from `.env` or system environment variables:

```env
DATABASE_URL=postgresql+psycopg://cinema_user:cinema_password@localhost:5432/cinema_explorer
TMDB_API_KEY=your_tmdb_v3_api_key
# Or use TMDB v4 read access token:
# TMDB_ACCESS_TOKEN=your_v4_bearer_token
TMDB_BASE_URL=https://api.themoviedb.org/3
TMDB_IMAGE_BASE_URL=https://image.tmdb.org/t/p
```

> [!IMPORTANT]
> A valid TMDB API key or read access token is required to fetch real metadata from TMDB. Secrets are automatically redacted in logs and must never be committed to source control.

---

## 2. CLI Commands

From the project root:

### Ingest a Movie
```bash
PYTHONPATH=.:backend backend/.venv/bin/python -m ingestion.cli movie <tmdb_id>
```
Example:
```bash
PYTHONPATH=.:backend backend/.venv/bin/python -m ingestion.cli movie 579974
```

### Ingest a TV / Web Series
```bash
PYTHONPATH=.:backend backend/.venv/bin/python -m ingestion.cli tv <tmdb_id>
```
Example:
```bash
PYTHONPATH=.:backend backend/.venv/bin/python -m ingestion.cli tv 1396
```

### Ingest the Seed Dataset
```bash
PYTHONPATH=.:backend backend/.venv/bin/python -m ingestion.cli seed
```

Add `--verbose` / `-v` for debug-level HTTP and pipeline logs:
```bash
PYTHONPATH=.:backend backend/.venv/bin/python -m ingestion.cli -v movie 27205
```

---

## 3. Seed Dataset Scope

The seed list in `ingestion/seeds.py` includes canonical TMDB IDs representing:

| Content Type | Title | TMDB ID | Language | Expected Industry | Anime? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Movie | *RRR* | `579974` | Telugu (`te`) | Tollywood | No |
| Movie | *3 Idiots* | `20453` | Hindi (`hi`) | Bollywood | No |
| Movie | *Vikram* | `743563` | Tamil (`ta`) | Kollywood | No |
| Movie | *Manjummel Boys* | `1069945` | Malayalam (`ml`) | Mollywood | No |
| Movie | *Kantara* | `858485` | Kannada (`kn`) | Sandalwood | No |
| Movie | *Inception* | `27205` | English (`en`) | Hollywood | No |
| Movie | *Spirited Away* | `129` | Japanese (`ja`) | Anime Industry | **Yes** |
| Movie | *Parasite* | `496243` | Korean (`ko`) | Korean Cinema | No |
| TV Series | *Breaking Bad* | `1396` | English (`en`) | Hollywood | No |
| TV Series | *Attack on Titan* | `1429` | Japanese (`ja`) | Anime Industry | **Yes** |

---

## 4. Pipeline Architecture

```text
TMDB API v3
     │
     ▼
TMDBClient (auth, timeouts, rate-limits, retries)
     │
     ▼
Normalizers (movie.py / tv.py / date_precision.py)
     │
     ├── Classifiers (anime.py / industry.py)
     │
     ▼
Validation (NormalizedTitlePayload via Pydantic)
     │
     ▼
TitleRepository (atomic transactions, idempotent upsert)
     │
     ▼
PostgreSQL Database
```

### Classification Approach

1. **Anime (`titles.is_anime`)**:
   - Multi-signal conservative rule engine.
   - Non-negotiable requirement: Must belong to Animation genre (`id: 16`). Live-action Japanese cinema (*Seven Samurai*, *Godzilla*) is strictly rejected.
   - Combines signals: Japanese language (`ja`), Japanese production (`JP`), anime studio names, and manga keywords.
   - Non-Japanese animation (*Toy Story*) is strictly rejected.
   - Fallback: `is_anime = False`.

2. **Industry (`title_industries`)**:
   - Rule-based mapping combining original language, production countries, and anime status.
   - Tollywood (`te` + `IN`), Bollywood (`hi` + `IN`), Kollywood (`ta` + `IN`), Mollywood (`ml` + `IN`), Sandalwood (`kn` + `IN`), Hollywood (`en` + `US`), British Cinema (`en` + `GB`), Korean Cinema (`ko` + `KR`), Japanese Cinema (`ja` + `JP`), Anime Industry (`is_anime = True`).
   - Produces `confidence` (0.0 to 1.0) and `source`.
   - **Manual Override Protection**: If `title_industries.is_manual_override` is `True`, re-ingestion will never overwrite the record.

### Idempotency & Upsert Strategy

- Keyed on `(tmdb_id, type)` for `titles`.
- Repeated ingestion updates mutable fields (`overview`, `poster_path`, `rating`, `popularity`, etc.) rather than inserting duplicates.
- All taxonomies (`languages`, `genres`, `countries`, `industries`, `people`, `watch_providers`) use get-or-create logic with natural external identifiers.
- Relations and child entities (`credits`, `seasons`, `alternate_titles`, `external_ids`, `title_watch_providers`) reconcile without duplicating rows.

### Supported Markets (OTT)

- Primary market: India (`IN`).
- Offer types mapped: `flatrate`, `rent`, `buy`, `free`, `ads`.

---

## 5. Testing

Run the ingestion test suite:

```bash
PYTHONPATH=.:backend backend/.venv/bin/pytest ingestion/tests/ -v
```

Tests cover:
- TMDB configuration and validation
- Movie and TV normalization
- Date precision parsing (`day`, `month`, `year`)
- Anime multi-signal classifier and industry rules
- Idempotency and duplicate prevention against PostgreSQL
- Manual override protection
- Season and OTT provider ingestion
- Client timeouts, rate limits (429), retries, and key redaction
- CLI commands and argument handling

---

## 6. Common Errors

- `TMDBAuthenticationError`: TMDB API credentials are missing or invalid. Set `TMDB_API_KEY` in `.env`.
- `TMDBNotFoundError`: The requested TMDB ID does not exist on TMDB (HTTP 404).
- `OperationalError: connection to server at 127.0.0.1:5432 failed`: Ensure PostgreSQL is running (`docker compose up -d`).

---

## 7. Licensing & Attribution

This product uses the TMDB API but is not endorsed or certified by TMDB. All metadata and artwork belong to their respective copyright holders.
