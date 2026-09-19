import type { Metadata } from "next";
import HomeCuratedHubs from "../../components/HomeCuratedHubs";
import { SparklesIcon } from "../../components/icons";
import { fetchFeaturedDiscovery } from "../../lib/api";
import { FeaturedDiscovery } from "../../lib/types";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  title: "Featured Hubs — Curated Cinema Movements & Spotlights | Cinema Explorer",
  description:
    "Explore curated collections across cultural cinema movements: Trending Worldwide, Indian Regional Cinema, Japanese Anime Spotlight, Critically Acclaimed Masterpieces, and Global Cinema Highlights.",
  alternates: {
    canonical: `${siteUrl}/featured`,
  },
  openGraph: {
    title: "Featured Hubs — Curated Cinema Movements & Spotlights | Cinema Explorer",
    description:
      "Explore curated collections across cultural cinema movements: Trending Worldwide, Indian Regional Cinema, Japanese Anime Spotlight, Critically Acclaimed Masterpieces, and Global Cinema Highlights.",
    url: `${siteUrl}/featured`,
    siteName: "Cinema Explorer",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Featured Hubs — Curated Cinema Movements & Spotlights | Cinema Explorer",
    description:
      "Explore curated collections across cultural cinema movements: Trending Worldwide, Indian Regional Cinema, Japanese Anime Spotlight, Critically Acclaimed Masterpieces, and Global Cinema Highlights.",
  },
};


export const dynamic = "force-dynamic";

export default async function FeaturedHubsPage() {
  let featured: FeaturedDiscovery | null = null;
  try {
    featured = await fetchFeaturedDiscovery();
  } catch (err: any) {
    console.error("Server fetch for featured discovery failed:", err?.message);
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Featured Hubs Header Banner */}
      <div className="border-b border-neutral-800/80 pb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <SparklesIcon className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-500">
                Curated Selections
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              Curated Discovery Hubs
            </h1>
            <p className="text-xs sm:text-sm text-neutral-400 mt-1 max-w-2xl">
              Hand-picked collections highlighting cultural cinema movements, top-rated masterpieces, and trending stories from around the globe.
            </p>
          </div>
        </div>
      </div>

      {/* Exclusively Curated Rows (Trending, Indian Regional, Anime, Top Rated, Global Highlights) */}
      <HomeCuratedHubs initialFeatured={featured} showHeader={false} padded={false} />
    </div>
  );
}

