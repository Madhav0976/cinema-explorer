# Cinema Explorer Frontend

The Next.js 15 frontend application for Cinema Explorer, built with the App Router, React 19, TypeScript, and Tailwind CSS.

---

## Responsibilities

- **Exploration UI**: Interactive 3-step Guided Explorer (`ExplorerStepper`) supporting time, era, language, and industry filtering.
- **Dynamic Catalog**: Infinite/paginated browsing with URL parameter synchronization, instant query-time sorting, and active filter pill tags.
- **Curated Discovery Hubs**: Multi-carousel presentation for global cinematic movements (Trending, Indian Regional, Anime Spotlight, Bayesian Top Rated, Global Highlights).
- **Title Detail Experience**: Rich metadata presentation, season breakdowns for TV series, and Where-to-Watch in India OTT offers with smart Google search fallback.
- **Search Engine Optimization (SEO)**: Server-side metadata generation, dynamic OpenGraph/Twitter cards, `robots.txt` directives, and full 5,138-URL `sitemap.xml`.
- **Accessibility**: WCAG 2.1 AA compliant semantic HTML, keyboard-navigable controls, `role="search"` forms, and screen-reader disclosures for external links.

---

## Environment Variables

Copy `frontend/.env.example` to `frontend/.env`:

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend FastAPI service endpoint |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` | Canonical site origin for SEO sitemaps and social cards |

---

## Development & Production Commands

From the `frontend/` directory:

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```
The application will be accessible at [http://localhost:3000](http://localhost:3000).

### Build for Production
```bash
npm run build
```
Compiles TypeScript, processes Tailwind CSS, and verifies static and metadata routes (`robots.txt`, `sitemap.xml`).

### Start Production Server
```bash
npm run start
```
Runs the optimized Next.js production server on port 3000.
