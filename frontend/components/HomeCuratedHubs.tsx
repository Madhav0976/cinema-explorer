"use client";

import { useEffect, useState } from "react";
import CuratedRow from "./CuratedRow";
import { FilmIcon, GlobeIcon, SparklesIcon, StarIcon } from "./icons";
import { GridSkeleton } from "./StateViews";
import { fetchFeaturedDiscovery } from "../lib/api";
import { FeaturedDiscovery } from "../lib/types";

interface HomeCuratedHubsProps {
  initialFeatured?: FeaturedDiscovery | null;
  showHeader?: boolean;
  padded?: boolean;
}

export default function HomeCuratedHubs({
  initialFeatured = null,
  showHeader = false,
  padded = true,
}: HomeCuratedHubsProps) {
  const [featured, setFeatured] = useState<FeaturedDiscovery | null>(initialFeatured);
  const [loading, setLoading] = useState<boolean>(!initialFeatured);

  useEffect(() => {
    // If not pre-rendered by server, fetch client-side
    if (!featured) {
      fetchFeaturedDiscovery()
        .then((data) => {
          setFeatured(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Client fetch for curated hubs failed:", err);
          setLoading(false);
        });
    }
  }, [featured]);

  return (
    <section
      id="featured"
      className={`${padded ? "mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" : ""} space-y-12`}
    >
      {showHeader && (
        <div className="border-b border-neutral-800/80 pb-4">
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            <SparklesIcon className="h-6 w-6 text-amber-500" />
            Curated Discovery Hubs
          </h2>
          <p className="text-xs text-neutral-400 mt-1">
            Hand-picked selections highlighting cultural cinema movements, top-rated masterpieces, and trending stories.
          </p>
        </div>
      )}

      {loading ? (
        <div className="space-y-8">
          <GridSkeleton count={5} />
        </div>
      ) : featured ? (
        <div className="space-y-12">
          {/* 1. Trending Worldwide */}
          {featured.trending && featured.trending.length > 0 && (
            <CuratedRow
              title="Trending Worldwide"
              subtitle="Most popular movies and series right now"
              icon={<FilmIcon className="h-5 w-5" />}
              titles={featured.trending}
              exploreHref="/catalog?section=trending"
            />
          )}

          {/* 2. Indian Regional Showcase */}
          {featured.indian_regional && featured.indian_regional.length > 0 && (
            <CuratedRow
              title="Indian Regional Cinema"
              subtitle="Tollywood, Bollywood, Kollywood, Mollywood & Sandalwood"
              icon={<GlobeIcon className="h-5 w-5" />}
              titles={featured.indian_regional}
              exploreHref="/catalog?section=indian-regional"
            />
          )}

          {/* 3. Anime Spotlight */}
          {featured.anime_spotlight && featured.anime_spotlight.length > 0 && (
            <CuratedRow
              title="Anime Spotlight"
              subtitle="Japanese animated masterpieces and series"
              icon={<SparklesIcon className="h-5 w-5" />}
              titles={featured.anime_spotlight}
              exploreHref="/catalog?category=anime"
            />
          )}

          {/* 4. Top Rated Masterpieces */}
          {featured.top_rated && featured.top_rated.length > 0 && (
            <CuratedRow
              title="Critically Acclaimed Masterpieces"
              subtitle="Highest-rated cinema across global audiences"
              icon={<StarIcon className="h-5 w-5 fill-amber-500" />}
              titles={featured.top_rated}
              exploreHref="/catalog?section=top-rated"
            />
          )}

          {/* 5. Global Highlights */}
          {featured.global_highlights && featured.global_highlights.length > 0 && (
            <CuratedRow
              title="Global Cinema Highlights"
              subtitle="International highlights and acclaimed productions"
              icon={<GlobeIcon className="h-5 w-5" />}
              titles={featured.global_highlights}
              exploreHref="/catalog?section=global-highlights"
            />
          )}
        </div>
      ) : null}
    </section>
  );
}

