import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import BackButton from "../../../components/BackButton";
import {
  ExternalLinkIcon,
  SearchIcon,
  StarIcon,
} from "../../../components/icons";
import PosterImage from "../../../components/PosterImage";
import ProviderBadge from "../../../components/ProviderBadge";
import { fetchTitleDetail } from "../../../lib/api";
import { getTmdbImageUrl } from "../../../lib/constants";
import { TitleDetail } from "../../../lib/types";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
  try {
    const title = await fetchTitleDetail(Number(id));
    const releaseYear = title.release_date
      ? new Date(title.release_date).getFullYear()
      : null;
    const pageTitle = releaseYear
      ? `${title.title} (${releaseYear}) — Cinema Explorer`
      : `${title.title} — Cinema Explorer`;
    const description =
      title.overview ||
      `Explore metadata, cast, streaming platforms, and details for ${title.title} on Cinema Explorer.`;
    const canonicalUrl = `${siteUrl}/title/${id}`;
    const ogImage = title.backdrop_path
      ? getTmdbImageUrl(title.backdrop_path, "original")
      : title.poster_path
      ? getTmdbImageUrl(title.poster_path, "w500")
      : undefined;

    return {
      title: pageTitle,
      description,
      alternates: {
        canonical: canonicalUrl,
      },
      openGraph: {
        title: pageTitle,
        description,
        url: canonicalUrl,
        type: "video.movie",
        siteName: "Cinema Explorer",
        images: ogImage ? [{ url: ogImage, alt: title.title }] : [],
      },
      twitter: {
        card: "summary_large_image",
        title: pageTitle,
        description,
        images: ogImage ? [ogImage] : [],
      },
    };
  } catch {
    return {
      title: "Title Details — Cinema Explorer",
      description: "Explore movies and series through time, language and culture.",
    };
  }
}


export default async function TitleDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const titleId = Number(id);

  if (!titleId || isNaN(titleId)) {
    notFound();
  }

  let title: TitleDetail;
  try {
    title = await fetchTitleDetail(titleId);
  } catch {
    notFound();
  }

  const backdropUrl = getTmdbImageUrl(title.backdrop_path, "original");
  const posterUrl = getTmdbImageUrl(title.poster_path, "w500");
  const releaseYear = title.release_date
    ? new Date(title.release_date).getFullYear()
    : null;
  const isMovie = title.type === "movie";

  // Separate credits into cast and crew
  const topCast = title.credits
    ? title.credits
        .filter((c) => c.category === "cast")
        .sort((a, b) => (a.cast_order ?? 999) - (b.cast_order ?? 999))
        .slice(0, 10)
    : [];

  const directors = title.credits
    ? title.credits.filter((c) => c.category === "crew" && c.job === "Director")
    : [];

  const writers = title.credits
    ? title.credits.filter(
        (c) =>
          c.category === "crew" &&
          (c.job === "Writer" || c.job === "Screenplay" || c.job === "Story")
      )
    : [];

  // Group watch providers strictly for India (IN)
  const inOffers = (title.watch_providers || []).filter(
    (p) => (p.country_code || "").toUpperCase() === "IN"
  );

  // Streaming offers: flatrate, free, ads
  const streamingOffers = inOffers.filter((p) => {
    const t = (p.offer_type || p.type || "").toLowerCase();
    return t === "flatrate" || t === "free" || t === "ads";
  });
  const uniqueStreaming: typeof streamingOffers = [];
  const seenStreaming = new Set<string>();
  for (const o of streamingOffers) {
    const key = o.provider.name.toLowerCase();
    if (!seenStreaming.has(key)) {
      seenStreaming.add(key);
      uniqueStreaming.push(o);
    }
  }

  // Rent offers
  const rentOffers = inOffers.filter((p) => {
    const t = (p.offer_type || p.type || "").toLowerCase();
    return t === "rent";
  });
  const uniqueRent: typeof rentOffers = [];
  const seenRent = new Set<string>();
  for (const o of rentOffers) {
    const key = o.provider.name.toLowerCase();
    if (!seenRent.has(key)) {
      seenRent.add(key);
      uniqueRent.push(o);
    }
  }

  // Buy offers
  const buyOffers = inOffers.filter((p) => {
    const t = (p.offer_type || p.type || "").toLowerCase();
    return t === "buy";
  });
  const uniqueBuy: typeof buyOffers = [];
  const seenBuy = new Set<string>();
  for (const o of buyOffers) {
    const key = o.provider.name.toLowerCase();
    if (!seenBuy.has(key)) {
      seenBuy.add(key);
      uniqueBuy.push(o);
    }
  }

  const hasAnyInOffers =
    uniqueStreaming.length > 0 || uniqueRent.length > 0 || uniqueBuy.length > 0;

  // Dynamic Google search query fallback when no India provider records exist
  const contentTerm = title.is_anime
    ? "anime"
    : title.type === "tv"
    ? "TV series"
    : "movie";
  const googleQuery = [title.title, releaseYear, contentTerm, "where to watch"]
    .filter(Boolean)
    .join(" ");
  const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(
    googleQuery
  )}`;

  return (
    <div className="min-h-screen pb-16">
      {/* Hero Banner with Backdrop Image */}
      <div className="relative w-full h-[360px] md:h-[480px] bg-neutral-950 overflow-hidden">
        {backdropUrl && (
          <Image
            src={backdropUrl}
            alt={title.title}
            fill
            unoptimized
            priority
            sizes="100vw"
            className="object-cover opacity-30 object-top"
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-neutral-950/60 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-neutral-950/90 via-neutral-950/40 to-transparent" />

        {/* Back Button (History-aware) */}
        <div className="absolute top-6 left-4 sm:left-8 z-10">
          <BackButton fallbackHref="/catalog" label="Back to Explorer" />
        </div>
      </div>

      {/* Main Content Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-44 md:-mt-64 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8">
          {/* Left Column: Poster & Quick Facts */}
          <div className="space-y-6">
            <div className="relative aspect-[2/3] w-full rounded-2xl overflow-hidden bg-neutral-900 border border-neutral-800 shadow-2xl shadow-black/80">
              <PosterImage
                src={posterUrl}
                alt={title.title}
                type={title.type}
                priority
              />
            </div>

            {/* Quick Metadata Card */}
            <div className="rounded-xl border border-neutral-800/80 bg-neutral-900/40 p-4 space-y-3 text-xs">
              <h4 className="font-bold text-neutral-300 uppercase tracking-wider text-[10px]">
                Taxonomy & Culture
              </h4>

              {/* Type */}
              <div className="flex justify-between py-1 border-b border-neutral-800/60">
                <span className="text-neutral-400">Content Type</span>
                <span className="font-semibold text-white uppercase">{title.type}</span>
              </div>

              {/* Release Date */}
              {title.release_date && (
                <div className="flex justify-between py-1 border-b border-neutral-800/60">
                  <span className="text-neutral-400">Release Date</span>
                  <span className="font-semibold text-white">{title.release_date}</span>
                </div>
              )}

              {/* Primary Language */}
              {title.original_language && (
                <div className="flex justify-between py-1 border-b border-neutral-800/60">
                  <span className="text-neutral-400">Original Language</span>
                  <span className="font-semibold uppercase text-amber-400">
                    {title.original_language}
                  </span>
                </div>
              )}

              {/* Industries */}
              {title.industries && title.industries.length > 0 && (
                <div className="flex justify-between py-1 border-b border-neutral-800/60">
                  <span className="text-neutral-400">Industry</span>
                  <span className="font-semibold text-white text-right">
                    {title.industries.map((ind) => ind.name).join(", ")}
                  </span>
                </div>
              )}

              {/* Production Countries */}
              {title.countries && title.countries.length > 0 && (
                <div className="flex justify-between py-1 border-b border-neutral-800/60">
                  <span className="text-neutral-400">Country</span>
                  <span className="font-semibold text-white text-right">
                    {title.countries.map((c) => c.name).join(", ")}
                  </span>
                </div>
              )}

              {/* External IDs */}
              {title.external_ids &&
                (title.external_ids.imdb_id || title.external_ids.wikidata_id) && (
                  <div className="pt-2 flex items-center gap-3">
                    {title.external_ids.imdb_id && (
                      <a
                        href={`https://www.imdb.com/title/${title.external_ids.imdb_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label={`View ${title.title} on IMDb (opens in a new tab)`}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-400 hover:text-amber-300"
                      >
                        IMDb <ExternalLinkIcon className="h-3 w-3" aria-hidden="true" />
                      </a>
                    )}
                    {title.external_ids.wikidata_id && (
                      <a
                        href={`https://www.wikidata.org/wiki/${title.external_ids.wikidata_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label={`View ${title.title} on Wikidata (opens in a new tab)`}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-sky-400 hover:text-sky-300"
                      >
                        Wikidata <ExternalLinkIcon className="h-3 w-3" aria-hidden="true" />
                      </a>
                    )}
                  </div>
                )}
            </div>
          </div>

          {/* Right Column: Title Header, Overview, Cast, Seasons, Where to Watch */}
          <div className="md:col-span-2 lg:col-span-3 space-y-8">
            {/* Header Block */}
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`px-2.5 py-0.5 rounded-md text-xs font-bold uppercase tracking-wider ${
                    isMovie ? "bg-amber-500 text-neutral-950" : "bg-sky-500 text-neutral-950"
                  }`}
                >
                  {isMovie ? "Movie" : "TV Series"}
                </span>

                {title.industries && title.industries.length > 0 && (
                  <span className="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-neutral-800 text-amber-300 border border-neutral-700">
                    {title.industries[0].name}
                  </span>
                )}

                {releaseYear && (
                  <span className="px-2 py-0.5 rounded text-xs text-neutral-400">
                    {releaseYear}
                  </span>
                )}
              </div>

              <h1 className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight text-white">
                {title.title}
              </h1>

              {title.original_title && title.original_title !== title.title && (
                <p className="text-lg text-neutral-400 italic">
                  Original Title: {title.original_title}
                </p>
              )}

              {/* Rating & Stats Bar */}
              <div className="flex items-center gap-4 pt-2">
                {title.tmdb_rating !== null && title.tmdb_rating !== undefined && (
                  <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-neutral-900 border border-neutral-800 text-amber-400">
                    <StarIcon className="h-4 w-4 fill-amber-400" />
                    <span className="font-bold text-sm">
                      {title.tmdb_rating.toFixed(1)}
                    </span>
                    <span className="text-neutral-400 text-xs">/ 10</span>
                  </div>
                )}
                {title.tmdb_vote_count !== null && title.tmdb_vote_count !== undefined && (
                  <span className="text-xs text-neutral-400">
                    ({title.tmdb_vote_count.toLocaleString()} votes)
                  </span>
                )}
              </div>

              {/* Genres Pills */}
              {title.genres && title.genres.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-2">
                  {title.genres.map((genre) => (
                    <span
                      key={genre.id}
                      className="px-2.5 py-1 rounded-full text-xs font-medium bg-neutral-900 text-neutral-300 border border-neutral-800"
                    >
                      {genre.name}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Overview / Synopsis */}
            {title.overview && (
              <div className="space-y-2">
                <h3 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Synopsis
                </h3>
                <p className="text-neutral-300 text-sm sm:text-base leading-relaxed">
                  {title.overview}
                </p>
              </div>
            )}

            {/* Key Creators (Directors & Writers) */}
            {(directors.length > 0 || writers.length > 0) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-neutral-800/80">
                {directors.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                      Director{directors.length > 1 ? "s" : ""}
                    </h4>
                    <p className="text-sm font-semibold text-white mt-1">
                      {directors.map((d) => d.person.name).join(", ")}
                    </p>
                  </div>
                )}
                {writers.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                      Writer{writers.length > 1 ? "s" : ""} / Creators
                    </h4>
                    <p className="text-sm font-semibold text-white mt-1">
                      {writers.map((w) => w.person.name).join(", ")}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Cast Section */}
            {topCast.length > 0 && (
              <div className="space-y-3 pt-4 border-t border-neutral-800/80">
                <h3 className="text-base font-bold text-white">Top Cast</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                  {topCast.map((credit) => (
                    <div
                      key={credit.id}
                      className="rounded-xl bg-neutral-900/50 border border-neutral-800/80 p-2.5 flex flex-col justify-between"
                    >
                      <div>
                        <p className="font-semibold text-xs text-white line-clamp-1">
                          {credit.person.name}
                        </p>
                        {credit.role && (
                          <p className="text-[11px] text-neutral-400 line-clamp-1 mt-0.5">
                            {credit.role}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TV Seasons Breakdown (For TV series) */}
            {!isMovie && title.seasons && title.seasons.length > 0 && (
              <div className="space-y-4 pt-4 border-t border-neutral-800/80">
                <h3 className="text-base font-bold text-white">Seasons & Episodes</h3>
                <div className="space-y-3">
                  {title.seasons.map((season) => (
                    <div
                      key={season.id}
                      className="rounded-xl bg-neutral-900/40 border border-neutral-800/80 p-4 flex flex-col sm:flex-row justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-white">
                            {season.name || `Season ${season.season_number}`}
                          </span>
                          {season.air_date && (
                            <span className="text-xs text-neutral-400">
                              ({new Date(season.air_date).getFullYear()})
                            </span>
                          )}
                        </div>
                        {season.overview && (
                          <p className="text-xs text-neutral-300 line-clamp-2 max-w-2xl">
                            {season.overview}
                          </p>
                        )}
                      </div>
                      <div className="sm:text-right flex-shrink-0">
                        <span className="inline-flex items-center px-2.5 py-1 rounded bg-neutral-800 text-xs font-semibold text-amber-300">
                          {season.episode_count || 0} Episodes
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Where to Watch (OTT Providers for India) */}
            <div className="space-y-4 pt-4 border-t border-neutral-800/80">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  Where to Watch in India
                </h3>
                {hasAnyInOffers && (
                  <span className="text-[11px] font-semibold text-amber-400/90 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                    India (IN)
                  </span>
                )}
              </div>

              {!hasAnyInOffers ? (
                <div className="rounded-xl border border-neutral-800/80 bg-neutral-900/40 p-5 text-center space-y-3">
                  <p className="text-xs text-neutral-400">
                    Streaming availability isn&apos;t currently listed for this title.
                  </p>
                  <div>
                    <a
                      href={googleSearchUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="Check where to watch on Google (opens in a new tab)"
                      className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700/80 border border-neutral-700/80 hover:border-amber-500/50 text-xs font-medium text-neutral-200 hover:text-white transition-all shadow-sm group"
                    >
                      <SearchIcon className="w-3.5 h-3.5 text-neutral-400 group-hover:text-amber-400 transition-colors" aria-hidden="true" />
                      <span>Check where to watch on Google</span>
                      <ExternalLinkIcon className="w-3 h-3 text-neutral-500 group-hover:text-neutral-300 transition-colors ml-0.5" aria-hidden="true" />
                    </a>
                  </div>
                  <p className="text-[11px] text-neutral-500">
                    Google may have newer availability information.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Streaming */}
                  {uniqueStreaming.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                          Streaming
                        </h4>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {uniqueStreaming.map((wp, idx) => (
                          <ProviderBadge
                            key={`stream-${wp.provider.id || idx}-${wp.provider.name}`}
                            name={wp.provider.name}
                            logoPath={wp.provider.logo_path}
                            link={wp.link}
                            offerType={wp.offer_type || wp.type}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Rent */}
                  {uniqueRent.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                          Rent
                        </h4>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {uniqueRent.map((wp, idx) => (
                          <ProviderBadge
                            key={`rent-${wp.provider.id || idx}-${wp.provider.name}`}
                            name={wp.provider.name}
                            logoPath={wp.provider.logo_path}
                            link={wp.link}
                            offerType={wp.offer_type || wp.type}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Buy */}
                  {uniqueBuy.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                          Buy
                        </h4>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {uniqueBuy.map((wp, idx) => (
                          <ProviderBadge
                            key={`buy-${wp.provider.id || idx}-${wp.provider.name}`}
                            name={wp.provider.name}
                            logoPath={wp.provider.logo_path}
                            link={wp.link}
                            offerType={wp.offer_type || wp.type}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* JustWatch / TMDB Attribution */}
                  <div className="pt-2 border-t border-neutral-800/40">
                    <p className="text-[11px] text-neutral-500 flex items-center gap-1.5">
                      <span>Streaming data powered by</span>
                      <a
                        href="https://www.justwatch.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label="Visit JustWatch (opens in a new tab)"
                        className="font-medium text-neutral-400 hover:text-amber-400 transition-colors underline decoration-neutral-700 underline-offset-2"
                      >
                        JustWatch
                      </a>
                      <span>via TMDB</span>
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Alternate Titles */}
            {title.alternate_titles && title.alternate_titles.length > 0 && (
              <div className="space-y-2 pt-4 border-t border-neutral-800/80">
                <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                  Alternate Titles
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {title.alternate_titles.slice(0, 8).map((alt, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded text-xs bg-neutral-900/60 text-neutral-400 border border-neutral-800"
                    >
                      {alt.title} {alt.country_code ? `(${alt.country_code})` : ""}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
