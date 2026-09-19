import Link from "next/link";
import HomeCatalogExplorer from "../components/HomeCatalogExplorer";
import HomeCuratedHubs from "../components/HomeCuratedHubs";
import { SparklesIcon } from "../components/icons";
import { fetchFeaturedDiscovery } from "../lib/api";
import { FeaturedDiscovery } from "../lib/types";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  // Fetch curated collections on the server for instant SSR pre-rendering
  let featured: FeaturedDiscovery | null = null;
  try {
    featured = await fetchFeaturedDiscovery();
  } catch (err: any) {
    console.error("Server-side fetch for featured discovery failed:", err?.message);
  }

  return (
    <div className="space-y-16 pb-20">
      {/* Cinematic Hero Section */}
      <section className="relative overflow-hidden border-b border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 via-neutral-950 to-neutral-950 pt-16 pb-20 sm:pt-24 sm:pb-28">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(245,158,11,0.15),rgba(255,255,255,0))]" />

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold tracking-wide uppercase shadow-inner">
            <SparklesIcon className="h-3.5 w-3.5" />
            Time • Language • Culture Discovery
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white max-w-4xl mx-auto">
            Discover Cinema Beyond <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-rose-400 to-amber-200">Borders &amp; Eras</span>
          </h1>

          <p className="text-base sm:text-xl text-neutral-300 max-w-2xl mx-auto font-light leading-relaxed">
            Explore movies and series across decades, languages, industries, and cultures—from South Asian regional cinema and Japanese anime to Korean cinema and Hollywood classics.
          </p>

          {/* Quick Filter CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
            <Link
              href="/catalog"
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-neutral-950 font-bold text-sm shadow-xl shadow-rose-950/40 transition-all hover:scale-105"
            >
              Start Exploring
            </Link>
            <Link
              href="/catalog?category=anime"
              className="px-5 py-3 rounded-xl bg-neutral-900/80 hover:bg-neutral-800 border border-neutral-800 text-neutral-200 font-semibold text-sm transition-all hover:border-neutral-700"
            >
              Anime Spotlight
            </Link>
            <Link
              href="/catalog?industry=Tollywood"
              className="px-5 py-3 rounded-xl bg-neutral-900/80 hover:bg-neutral-800 border border-neutral-800 text-neutral-200 font-semibold text-sm transition-all hover:border-neutral-700"
            >
              Tollywood Showcase
            </Link>
            <Link
              href="/catalog?language=ko"
              className="px-5 py-3 rounded-xl bg-neutral-900/80 hover:bg-neutral-800 border border-neutral-800 text-neutral-200 font-semibold text-sm transition-all hover:border-neutral-700"
            >
              Korean Cinema
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Discovery Hubs Section (Restored Curated Rows) */}
      <HomeCuratedHubs initialFeatured={featured} />

      {/* Main Guided Discovery Catalog Section */}
      <HomeCatalogExplorer />
    </div>
  );
}
