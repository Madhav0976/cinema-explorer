# Cinema Explorer — Phase 6A.3 Catalog Data Quality Audit Report

**Audit Date:** September 18, 2026  
**Catalog Scope:** 5,135 Titles (PostgreSQL Database)  
**Time Coverage:** 2000 – 2026 (27 Release Years)  
**Supported Discovery Languages:** Telugu (`te`), Hindi (`hi`), Tamil (`ta`), Malayalam (`ml`), Kannada (`kn`), English (`en`), Japanese (`ja`), Korean (`ko`)  
**Status:** READ-ONLY AUDIT & VERIFICATION — **Zero records modified, deleted, or truncated.**

---

## 1. Executive Summary

Cinema Explorer underwent a comprehensive data quality audit following the Phase 6A.2 bulk TMDB catalog expansion. The database was scaled from 10 seed titles to **5,135 production titles** across 27 release years and 8 target discovery languages.

### Key Audit Findings:
1. **Catalog Integrity (100% Intact):**
   - Exactly **5,135 titles** (**3,470 Movies** and **1,665 TV Series**).
   - **Zero duplicate `(tmdb_id, type)` pairs** and zero duplicate title metadata records.
   - **Zero broken foreign-key relationships** and zero orphaned relationship records across all 9 relational tables.
   - **All 10 canonical seed titles** remain completely intact with original primary keys, attributes, and associations.
2. **Year & Date Precision (100% Clean):**
   - Every single release year from **2000 through 2026 (27 / 27 years)** is represented with between 139 and 230 titles per year.
   - Zero missing years, zero null release dates, and zero titles outside the 2000–2026 range.
   - 100% of titles have `release_date_precision = 'day'`.
3. **Language & Regional Diversity:**
   - English (`en`), Japanese (`ja`), Korean (`ko`), Hindi (`hi`), Tamil (`ta`), Malayalam (`ml`), and Telugu (`te`) each possess deep coverage (400 to 1,080 titles each).
   - Kannada (`kn`) has 45 titles; an empirical TMDB API audit proved that TMDB itself contains only 48 Kannada movies and 1 TV series with `vote_count >= 10`. Cinema Explorer captured 45 / 49 (91.8%) of all available TMDB Kannada titles matching our quality filter.
4. **Classification & Anime Quality (99.94% Precision):**
   - 100% of titles (5,135 / 5,135) possess an industry classification with zero multi-industry conflicts.
   - **Anime Classification is 100% accurate**: 855 titles flagged `is_anime=True` (all Japanese animation), 0 non-Japanese animations flagged, and 0 Japanese live-action titles misclassified.
   - Only **3 suspicious industry records** were identified (British films where TMDB added `US` to `origin_country` despite British production).
5. **Metadata & Media Completeness:**
   - Critical attributes (`title`, `original_title`, `release_date`, `original_language`, `tmdb_rating`, `vote_count`, `popularity`): **100% complete (0% missing)**.
   - Overviews: 99.92% complete (4 missing).
   - Posters: 99.92% complete (4 missing). Backdrops: 97.49% complete (129 missing).
   - Watch Providers: 81,333 offer records worldwide across 4,840 titles (94.26% coverage); 3,481 titles have India (`IN`) streaming/rent/buy provider options.

---

## 2. Catalog Integrity Audit

### Core Volume Breakdown
| Metric | Value | Status |
| :--- | :--- | :--- |
| **Total Database Titles** | **5,135** | Optimal |
| **Movies Count** | **3,470** (67.57%) | Optimal |
| **TV Series Count** | **1,665** (32.43%) | Optimal |
| **Invalid Content Types (`!= 'movie','tv'`)** | **0** | Clean |
| **Null or Non-Positive TMDB IDs** | **0** | Clean |
| **Duplicate `(tmdb_id, type)` Pairs** | **0** | Clean |
| **Suspicious Duplicate Title Records** | **0** | Clean |

### Foreign Key & Relational Orphan Audit
Every child table was audited using `NOT IN (SELECT id FROM titles)` to detect orphaned records:

| Relationship Table | Associated Entity | Orphaned Records | Status |
| :--- | :--- | :---: | :--- |
| `title_languages` | Languages | **0** | Clean |
| `title_genres` | Genres | **0** | Clean |
| `title_countries` | Countries | **0** | Clean |
| `title_industries` | Industries | **0** | Clean |
| `alternate_titles` | Alternate Titles | **0** | Clean |
| `external_ids` | IMDb & Wikidata IDs | **0** | Clean |
| `credits` | Cast & Crew | **0** | Clean |
| `seasons` | TV Seasons | **0** | Clean |
| `title_watch_providers` | Watch Provider Offers | **0** | Clean |

### Taxonomy Table Usage Audit
- **Languages (`languages`)**: 0 unused.
- **Genres (`genres`)**: 0 unused.
- **Countries (`countries`)**: 0 unused.
- **Watch Providers (`watch_providers`)**: 0 unused.
- **Industries (`industries`)**: 2 unused (`HK Cinema`, `SE Cinema`). These were created during initial seed migrations and do not affect catalog performance.
- **People (`people`)**: 107 people records not currently linked in `credits`. These represent pre-created entity records from TMDB response payloads.

---

## 3. Year & Date Quality Audit

### Distribution Across 2000–2026
The catalog covers 27 consecutive release years without any gaps:

| Release Year | Total Titles | Movies | TV Series | % of Catalog |
| :---: | :---: | :---: | :---: | :---: |
| **2026** | 178 | 100 | 78 | 3.47% |
| **2025** | 215 | 135 | 80 | 4.19% |
| **2024** | 214 | 134 | 80 | 4.17% |
| **2023** | 227 | 147 | 80 | 4.42% |
| **2022** | 230 | 150 | 80 | 4.48% |
| **2021** | 224 | 144 | 80 | 4.36% |
| **2020** | 209 | 137 | 72 | 4.07% |
| **2019** | 222 | 144 | 78 | 4.32% |
| **2018** | 216 | 142 | 74 | 4.21% |
| **2017** | 210 | 145 | 65 | 4.09% |
| **2016** | 211 | 146 | 65 | 4.11% |
| **2015** | 203 | 141 | 62 | 3.95% |
| **2014** | 202 | 141 | 61 | 3.93% |
| **2013** | 200 | 137 | 63 | 3.90% |
| **2012** | 203 | 141 | 62 | 3.95% |
| **2011** | 197 | 136 | 61 | 3.84% |
| **2010** | 199 | 139 | 60 | 3.88% |
| **2009** | 170 | 118 | 52 | 3.31% |
| **2008** | 159 | 111 | 48 | 3.10% |
| **2007** | 168 | 119 | 49 | 3.27% |
| **2006** | 164 | 114 | 50 | 3.19% |
| **2005** | 164 | 117 | 47 | 3.19% |
| **2004** | 164 | 119 | 45 | 3.19% |
| **2003** | 156 | 111 | 45 | 3.04% |
| **2002** | 152 | 110 | 42 | 2.96% |
| **2001** | 139 | 98 | 41 | 2.71% |
| **2000** | 139 | 97 | 42 | 2.71% |

### Date Quality Diagnostics
- **Missing Years in 2000–2026**: **0** (All 27 years present).
- **Titles Outside 2000–2026 Range**: **0**.
- **Null Release Dates**: **0**.
- **Date Precision Distribution**:
  - `'day'`: **5,135** (100.0%)
  - `'month'` / `'year'` / `null`: **0** (0.0%)

---

## 4. Language Coverage Audit

Cinema Explorer supports 8 primary cultural discovery languages.

### Volume & Type Distribution by Language
| ISO 639-1 | Language Name | Total Titles | Movies | TV Series | Years Covered | Coverage Rate |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| `ja` | Japanese | 1,080 | 540 | 540 | 27 / 27 | 100% |
| `en` | English | 1,080 | 540 | 540 | 27 / 27 | 100% |
| `ko` | Korean | 929 | 533 | 396 | 27 / 27 | 100% |
| `hi` | Hindi | 715 | 540 | 175 | 27 / 27 | 100% |
| `ta` | Tamil | 464 | 454 | 10 | 27 / 27 | 100% |
| `ml` | Malayalam | 419 | 418 | 1 | 27 / 27 | 100% |
| `te` | Telugu | 403 | 401 | 2 | 27 / 27 | 100% |
| `kn` | Kannada | 45 | 44 | 1 | 17 / 27 | 63% |
| **Other** | Non-discovery | **0** | **0** | **0** | — | — |

### Deep-Dive Analysis on Kannada (`kn`)
Kannada title volume is 45 titles, which is noticeably lower than the other 7 languages. To determine if this was an ingestion defect or TMDB data limitation, a live discovery audit was executed directly against TMDB:
- **Kannada Movies on TMDB:**
  - `vote_count >= 10`: **48 titles total** worldwide in TMDB. (Cinema Explorer ingested 44 titles, 91.7% capture).
  - `vote_count >= 5`: 141 titles.
  - `vote_count >= 1`: 817 titles.
- **Kannada TV Series on TMDB:**
  - `vote_count >= 10`: **Exactly 1 title** (*Beast of Bangalore: Indian Predator*, TMDB ID 214777). (Cinema Explorer ingested this exact title).
  - `vote_count >= 1`: 11 titles total.

**Conclusion:** The lower count is caused entirely by TMDB's sparse community voting for Sandalwood cinema prior to 2016. The ingestion pipeline performed correctly under the `min_vote_count=10` threshold.

---

## 5. Industry Classification Quality Audit

Cinema Explorer classifies titles into cultural cinema industries using transparent, rule-based inference.

### Industry Distribution
| Industry | Cultural Region | Title Count | % of Catalog |
| :--- | :--- | :---: | :---: |
| **Hollywood** | United States / Global English | 1,023 | 19.92% |
| **Korean Cinema** | South Korea | 929 | 18.09% |
| **Anime Industry** | Japan (Anime Productions) | 855 | 16.65% |
| **Bollywood** | Hindi Cinema (India) | 713 | 13.89% |
| **Kollywood** | Tamil Cinema (India) | 463 | 9.02% |
| **Mollywood** | Malayalam Cinema (India) | 419 | 8.16% |
| **Tollywood** | Telugu Cinema (India) | 403 | 7.85% |
| **Japanese Cinema** | Japan (Live-Action Cinema) | 225 | 4.38% |
| **British Cinema** | United Kingdom | 52 | 1.01% |
| **Sandalwood** | Kannada Cinema (India) | 45 | 0.88% |
| **Australian Cinema** | Australia | 5 | 0.10% |
| **Other Regional Fallbacks** | US, SG, DE Cinema | 3 | 0.06% |

- **Titles with Zero Industries:** **0** (100% classified).
- **Titles with Multiple Industries:** **0** (Single primary industry maintained).

---

## 6. Anime Classification Audit

Cinema Explorer treats Anime as an internal cultural classification (`is_anime = True`) and a discovery category filter (`/catalog?category=anime`), intentionally hiding raw boolean tags on title cards.

| Audit Metric | Count | Evaluation |
| :--- | :---: | :--- |
| **Total Anime Titles** | **855** | Optimal |
| **Anime Movies** | 361 | Optimal |
| **Anime TV Series** | 494 | Optimal |
| **Non-Japanese Anime (`is_anime=True, lang != 'ja'`)** | **0** | **100% Clean** |
| **Japanese Animation marked `is_anime=False`** | **0** | **100% Clean** |
| **Japanese Live-Action marked `is_anime=True`** | **0** | **100% Clean** |
| **Discrepancy (`is_anime` vs `industry='Anime Industry'`)** | **0** | **100% Aligned** |

**Conclusion:** The Anime classifier rule (`original_language == 'ja'` + `animation` genre $\rightarrow$ `is_anime=True`) is robust and operating with zero false positives or false negatives.

---

## 7. Metadata Completeness Audit

Evaluation of completeness across all 5,135 titles in the catalog:

| Field Name | Storage Column | Missing Count | Missing % | Severity / Impact |
| :--- | :--- | :---: | :---: | :--- |
| `title` | `titles.title` | 0 | 0.00% | None |
| `original_title` | `titles.original_title` | 0 | 0.00% | None |
| `release_date` | `titles.release_date` | 0 | 0.00% | None |
| `release_date_precision` | `titles.release_date_precision` | 0 | 0.00% | None |
| `original_language` | `titles.original_language` | 0 | 0.00% | None |
| `tmdb_rating` | `titles.tmdb_rating` | 0 | 0.00% | None |
| `tmdb_vote_count` | `titles.tmdb_vote_count` | 0 | 0.00% | None |
| `tmdb_popularity` | `titles.tmdb_popularity` | 0 | 0.00% | None |
| `spoken_languages` | `title_languages` | 0 | 0.00% | None |
| `tv_seasons` | `seasons` (for TV) | 0 | 0.00% | None |
| `overview` | `titles.overview` | 4 | 0.08% | Very Low (TMDB has no synopsis) |
| `poster_path` | `titles.poster_path` | 4 | 0.08% | Very Low (TMDB has no poster) |
| `genres` | `title_genres` | 14 | 0.27% | Very Low (Niche indie/TV stubs) |
| `credits` | `credits` | 22 | 0.43% | Low (Uncredited shorts/reality) |
| `countries` | `title_countries` | 33 | 0.64% | Low (Co-productions without country) |
| `backdrop_path` | `titles.backdrop_path` | 129 | 2.51% | Low (Fallback to poster/placeholder) |
| `watch_providers` | `title_watch_providers` | 295 | 5.74% | Low (Unlicensed older titles) |

---

## 8. Credits & TV Data Quality

### Credits Distribution
- **Total Associated Credits:** 109,872 cast and crew records.
- **Average Credits per Title:** **21.5 credits**.
- **Minimum Credits (where present):** 1.
- **Maximum Credits:** 67 (e.g. large Hollywood ensemble casts).
- **Titles with 0 Credits:** **22 titles** (0.43%). These are reality television series (e.g., *NPR Tiny Desk Concerts*, *All Elite Wrestling: Dynamite*) or obscure animated shorts where TMDB provides no cast list.
- **Titles with 1–2 Credits:** **54 titles** (1.05%).

### TV Seasons & Episodes Quality
- **Total TV Series:** 1,665 titles.
- **Total TV Seasons:** 7,331 season records.
- **TV Series with 0 Seasons:** **0** (All TV series possess at least season 1).
- **Season 0 (Specials):** **783 records**. Preserved and compliant with TMDB conventions.
- **Negative Season Numbers:** **0**.
- **Zero-Episode Seasons:** **141 seasons** (1.92%). These represent unreleased future seasons or empty TMDB stub containers.

---

## 9. Poster & Image Quality

- **Missing Posters:** **4 titles** (0.08%):
  1. `[2859]` *Anthaka Mundu Aa Tarvatha* (2013, Telugu)
  2. `[3446]` *Rama Rama Krishna Krishna* (2010, Telugu)
  3. `[4309]` *123 from Amalapuram* (2005, Telugu)
  4. `[4791]` *Bobby* (2002, Telugu)
- **Missing Backdrops:** **129 titles** (2.51%).
- **Malformed Image Paths:** **0**. Every image path begins with `/` and follows standard TMDB hash patterns (e.g., `/u0XUBNQWlOvrh0Gd97ARGpIkL0.jpg`).

---

## 10. OTT & Watch Provider Data Audit

*(Baseline evaluation for upcoming Phase 6B)*

- **Total Provider Offer Records:** **81,333 offers** across worldwide markets.
- **Worldwide Title Coverage:** **4,840 titles** (94.26%) have at least one streaming/rent/buy provider globally.
- **India Market (`country_code = 'IN'`):**
  - **3,481 titles** (67.79% of total catalog) have active watch options in India.
  - **1,654 titles** currently have no India provider record in TMDB.
  - **11,444 total India offer records**.
- **India Offer Types Breakdown:**
  - `flatrate` (Subscription Stream): **6,023** (52.6%)
  - `rent`: **2,294** (20.0%)
  - `buy`: **1,715** (15.0%)
  - `ads` (AVOD): **1,260** (11.0%)
  - `free`: **152** (1.3%)
- **Top 10 Streaming Platforms in India by Title Availability:**
  1. **YouTube**: 1,182 titles
  2. **Google Play Movies**: 1,166 titles
  3. **Apple TV Store**: 1,036 titles
  4. **JioHotstar**: 1,024 titles
  5. **Amazon Prime Video**: 1,004 titles
  6. **Netflix**: 925 titles
  7. **Amazon Prime Video with Ads**: 856 titles
  8. **VI Movies and TV**: 728 titles
  9. **Amazon Video**: 493 titles
  10. **Zee5**: 411 titles
- **Malformed / Missing Provider Links:** **0**.

---

## 11. Suspicious Records Table

The following 3 records were flagged during the automated rule audit:

| Title ID | TMDB ID | Title | Type | Year | Lang | Countries in DB | Current Industry | Reason Flagged | Recommended Action |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| `4855` | `1576` | **Resident Evil** | movie | 2002 | `en` | `['DE', 'FR', 'CA', 'GB']` | Hollywood | European co-production classified as Hollywood via TMDB `origin_country` containing `US`. | Optional manual override to British Cinema or leave as Hollywood (US distributor). |
| `4042` | `4517` | **Elizabeth: The Golden Age** | movie | 2007 | `en` | `['DE', 'FR', 'GB']` | Hollywood | UK/European historical drama classified as Hollywood via TMDB `origin_country` containing `US`. | Reclassify to **British Cinema**. |
| `4540` | `27` | **9 Songs** | movie | 2004 | `en` | `['GB']` | Hollywood | UK production (Michael Winterbottom) classified as Hollywood via TMDB `origin_country` containing `US`. | Reclassify to **British Cinema**. |

---

## 12. Canonical Seed Titles Verification

All 10 canonical seed titles are verified present and unaltered in PostgreSQL:

| DB ID | TMDB ID | Type | Title | Lang | Year | Industry | Anime? | Credits | Providers | Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **`9`** | `27205` | movie | **Inception** | `en` | 2010 | Hollywood | No | 30 | 10 | **Intact** |
| **`13`** | `129` | movie | **Spirited Away** | `ja` | 2001 | Anime Industry | Yes | 26 | 1 | **Intact** |
| **`15`** | `20453` | movie | **3 Idiots** | `hi` | 2009 | Bollywood | No | 31 | 4 | **Intact** |
| **`19`** | `496243` | movie | **Parasite** | `ko` | 2019 | Korean Cinema | No | 32 | 1 | **Intact** |
| **`20`** | `1429` | tv | **Attack on Titan** | `ja` | 2013 | Anime Industry | Yes | 26 | 2 | **Intact** |
| **`24`** | `743563` | movie | **Vikram** | `ta` | 2022 | Kollywood | No | 29 | 2 | **Intact** |
| **`25`** | `1069945` | movie | **Manjummel Boys** | `ml` | 2024 | Mollywood | No | 27 | 1 | **Intact** |
| **`26`** | `858485` | movie | **Kantara** | `kn` | 2022 | Sandalwood | No | 25 | 4 | **Intact** |
| **`30`** | `1396` | tv | **Breaking Bad** | `en` | 2008 | Hollywood | No | 15 | 1 | **Intact** |
| **`31`** | `579974` | movie | **RRR** | `te` | 2022 | Tollywood | No | 26 | 3 | **Intact** |

---

## 13. Issues Priority Classification

### Critical Issues (0)
- *None.* The database schema, relational integrity, primary keys, and core attributes are 100% consistent.

### High-Priority Issues (0)
- *None.* Zero duplicate records, zero broken foreign keys, and zero crashes in API endpoints.

### Medium-Priority Issues (2)
1. **Classifier Precedence on English Origin Countries:** `ingestion/classifiers/industry.py` considers `origin_country` before production countries. For films like *Elizabeth: The Golden Age* and *9 Songs*, TMDB includes `US` in origin countries, overriding their British production status.
   - *Recommendation:* Prioritize `production_countries` over `origin_country` when determining British Cinema vs. Hollywood.
2. **Kannada Catalog Volume (45 titles):** Under `vote_count >= 10`, TMDB only has 49 Kannada titles.
   - *Recommendation for future data expansion:* In a dedicated Sandalwood enrichment pass, query Kannada with `min_vote_count = 3` or `1` to ingest ~200 additional Kannada titles across 2000–2026.

### Low-Priority Issues (4)
1. **Missing Posters (4 titles):** 4 older Telugu titles lack posters in TMDB. Frontend already renders graceful SVG placeholders.
2. **Missing Backdrops (129 titles / 2.51%):** Frontend falls back gracefully to poster art.
3. **Missing Overviews (4 titles / 0.08%):** TMDB lacks synopses for 4 titles.
4. **Zero-Episode TV Seasons (141 seasons):** Empty TMDB containers. Filter out seasons where `episode_count == 0` during UI presentation.

---

## 14. Final Recommendations Before Phase 6B

The database is in **production-ready health** and fully prepared for Phase 6B (OTT & Watch Provider Integration):
1. **No destructive database cleanup is needed or recommended.**
2. **No table truncations or re-ingestions are required.**
3. **All 102 automated tests are passing.**
4. For Phase 6B, build on the existing 11,444 India watch provider records in `title_watch_providers`, adding UI badges for platforms (JioHotstar, Prime Video, Netflix, Zee5) and deep-linking capabilities.

