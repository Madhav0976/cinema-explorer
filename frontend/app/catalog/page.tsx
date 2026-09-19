"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import ExplorerStepper from "../../components/ExplorerStepper";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  FilmIcon,
  SparklesIcon,
  StarIcon,
  GlobeIcon,
} from "../../components/icons";
import { EmptyState, ErrorState, GridSkeleton } from "../../components/StateViews";
import TitleCard from "../../components/TitleCard";
import {
  fetchCountries,
  fetchDecades,
  fetchGenres,
  fetchIndustries,
  fetchLanguages,
  fetchTitles,
} from "../../lib/api";
import { SORT_OPTIONS } from "../../lib/constants";
import {
  Country,
  Decade,
  Genre,
  Industry,
  Language,
  TitleFilterParams,
  TitleSummary,
} from "../../lib/types";

function resolveSortValue(sort: string, section?: string): string {
  const s = sort.toLowerCase().trim();
  if (s === "top-rated" || s === "top_rated" || s === "rating" || (s === "popularity.desc" && section === "top-rated")) {
    return "rating.desc";
  }
  if (s === "popular" || s === "popularity" || s === "popularity.desc") {
    return "popularity.desc";
  }
  if (s === "most-voted" || s === "most_voted" || s === "votes" || s === "votes.desc") {
    return "votes.desc";
  }
  if (s === "newest" || s === "release_date" || s === "release_date.desc") {
    return "release_date.desc";
  }
  if (s === "oldest" || s === "release_date.asc") {
    return "release_date.asc";
  }
  if (s === "title" || s === "title.asc") {
    return "title.asc";
  }
  return "popularity.desc";
}

function CatalogContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Extract query parameters from URL
  const queryParam = searchParams.get("q") || searchParams.get("query") || "";
  const pageParam = parseInt(searchParams.get("page") || "1", 10) || 1;
  const sortParam = searchParams.get("sort") || searchParams.get("sort_by") || "popularity.desc";
  const typeParam = searchParams.get("type") as "movie" | "tv" | null;
  const categoryParam = searchParams.get("category");
  const isAnimeParam = searchParams.get("is_anime") === "true" ? true : undefined;
  const languageParam = searchParams.get("language") || undefined;
  const industryParam = searchParams.get("industry") || undefined;
  const genreParam = searchParams.get("genre") || undefined;
  const yearParam = searchParams.get("year") ? parseInt(searchParams.get("year")!, 10) : undefined;
  const decadeParam = searchParams.get("decade") ? parseInt(searchParams.get("decade")!, 10) : undefined;
  const sectionParam = searchParams.get("section") || undefined;

  // Catalog State
  const [titles, setTitles] = useState<TitleSummary[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSearchFilters, setShowSearchFilters] = useState(false);

  // Taxonomy State
  const [decades, setDecades] = useState<Decade[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);

  // Load Taxonomies on mount
  useEffect(() => {
    Promise.allSettled([
      fetchDecades(),
      fetchLanguages(),
      fetchIndustries(),
      fetchGenres(),
      fetchCountries(),
    ]).then(([decadesRes, langsRes, indsRes, genresRes, countriesRes]) => {
      if (decadesRes.status === "fulfilled") setDecades(decadesRes.value);
      if (langsRes.status === "fulfilled") setLanguages(langsRes.value);
      if (indsRes.status === "fulfilled") setIndustries(indsRes.value);
      if (genresRes.status === "fulfilled") setGenres(genresRes.value);
      if (countriesRes.status === "fulfilled") setCountries(countriesRes.value);
    });
  }, []);

  // Construct active filters object
  const activeFilters: TitleFilterParams = {
    q: queryParam || undefined,
    query: queryParam || undefined,
    type: typeParam || undefined,
    category: categoryParam || undefined,
    is_anime: isAnimeParam,
    language: languageParam,
    industry: industryParam,
    genre: genreParam,
    year: yearParam,
    decade: decadeParam,
    section: sectionParam,
    sort_by: sortParam,
    sort: sortParam,
    page: pageParam,
    page_size: 20,
  };

  // Fetch titles whenever URL search parameters change
  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchTitles(activeFilters)
      .then((res) => {
        setTitles(res.items);
        setTotalItems(res.total);
        setTotalPages(res.total_pages ?? res.pages ?? 1);
        setHasNext(res.has_next ?? (res.page < (res.total_pages ?? res.pages ?? 1)));
        setHasPrevious(res.has_previous ?? (res.page > 1));
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load catalog titles.");
        setLoading(false);
      });
  }, [
    queryParam,
    pageParam,
    sortParam,
    typeParam,
    categoryParam,
    isAnimeParam,
    languageParam,
    industryParam,
    genreParam,
    yearParam,
    decadeParam,
    sectionParam,
  ]);

  // URL state update helper
  const updateUrlParams = (newParams: Record<string, string | number | undefined | null>, resetPage = true) => {
    const params = new URLSearchParams();

    // Carry forward existing non-empty values
    if (queryParam) params.set("q", queryParam);
    if (typeParam) params.set("type", typeParam);
    if (categoryParam) params.set("category", categoryParam);
    if (isAnimeParam !== undefined) params.set("is_anime", String(isAnimeParam));
    if (languageParam) params.set("language", languageParam);
    if (industryParam) params.set("industry", industryParam);
    if (genreParam) params.set("genre", genreParam);
    if (yearParam) params.set("year", String(yearParam));
    if (decadeParam) params.set("decade", String(decadeParam));
    if (sectionParam) params.set("section", sectionParam);
    if (sortParam && sortParam !== "popularity.desc") params.set("sort", sortParam);

    // Apply updates
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") {
        params.delete(key);
      } else {
        params.set(key, String(value));
      }
    });

    // Page reset handling
    if (resetPage) {
      params.delete("page");
    } else if (newParams.page && Number(newParams.page) > 1) {
      params.set("page", String(newParams.page));
    } else {
      params.delete("page");
    }

    const qs = params.toString();
    router.push(`/catalog${qs ? `?${qs}` : ""}`);
  };

  const handleFilterChange = (filters: TitleFilterParams) => {
    updateUrlParams(
      {
        type: filters.type,
        category: filters.category,
        is_anime: filters.is_anime !== undefined ? String(filters.is_anime) : undefined,
        language: filters.language,
        industry: filters.industry,
        genre: filters.genre,
        year: filters.year,
        decade: filters.decade,
        q: filters.q || filters.query,
      },
      true // Reset page to 1
    );
  };

  const hasActiveNonSearchFilters = Boolean(
    typeParam ||
    categoryParam ||
    isAnimeParam !== undefined ||
    languageParam ||
    industryParam ||
    genreParam ||
    yearParam ||
    decadeParam ||
    sectionParam
  );

  const handleClearSearch = () => {
    updateUrlParams({ q: undefined, query: undefined }, true);
  };

  const handleResetFilters = () => {
    router.push("/catalog");
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      updateUrlParams({ page: newPage }, false);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleSortChange = (newSort: string) => {
    updateUrlParams({ sort: newSort }, true); // Reset page to 1 on sort change
  };

  // Smart pagination windowing helper (1, 2, 3 ... 438)
  const getPaginationPages = (current: number, total: number): (number | string)[] => {
    if (total <= 7) {
      return Array.from({ length: total }, (_, i) => i + 1);
    }
    if (current <= 4) {
      return [1, 2, 3, 4, 5, "...", total];
    }
    if (current >= total - 3) {
      return [1, "...", total - 4, total - 3, total - 2, total - 1, total];
    }
    return [1, "...", current - 1, current, current + 1, "...", total];
  };

  // Result range computation
  const startIndex = totalItems > 0 ? (pageParam - 1) * 20 + 1 : 0;
  const endIndex = Math.min(pageParam * 20, totalItems);

  // Determine section heading
  let sectionTitle = "Cinema Catalog & Time Explorer";
  let sectionSubtitle = "Explore movies and series through time, language, and culture.";
  let sectionIcon = <FilmIcon className="h-6 w-6 text-amber-500" />;

  if (queryParam) {
    sectionTitle = `Search Results for "${queryParam}"`;
    sectionSubtitle = `${totalItems.toLocaleString()} title${totalItems === 1 ? "" : "s"} found`;
  } else if (sectionParam === "trending") {
    sectionTitle = "Trending Worldwide";
    sectionSubtitle = "Most popular movies and series across global audiences";
    sectionIcon = <FilmIcon className="h-6 w-6 text-amber-500" />;
  } else if (sectionParam === "top-rated") {
    sectionTitle = "Critically Acclaimed Masterpieces";
    sectionSubtitle = "Highest-rated cinema across global audiences";
    sectionIcon = <StarIcon className="h-6 w-6 fill-amber-500 text-amber-500" />;
  } else if (sectionParam === "indian-regional") {
    sectionTitle = "Indian Regional Cinema";
    sectionSubtitle = "Tollywood, Bollywood, Kollywood, Mollywood & Sandalwood";
    sectionIcon = <GlobeIcon className="h-6 w-6 text-amber-500" />;
  } else if (sectionParam === "global-highlights") {
    sectionTitle = "Global Cinema Highlights";
    sectionSubtitle = "International cinema gems and acclaimed productions";
    sectionIcon = <GlobeIcon className="h-6 w-6 text-amber-500" />;
  } else if (categoryParam === "anime" || isAnimeParam) {
    sectionTitle = "Anime Spotlight";
    sectionSubtitle = "Japanese animated masterpieces and series";
    sectionIcon = <SparklesIcon className="h-6 w-6 text-amber-500" />;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header Banner */}
      <div className="border-b border-neutral-800/80 pb-5">
        <div className="flex items-center gap-3">
          {sectionIcon}
          <div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              {sectionTitle}
            </h1>
            <p className="text-xs sm:text-sm text-neutral-400 mt-1">
              {sectionSubtitle}
            </p>
          </div>
        </div>
      </div>

      {/* Search Header or Discovery Stepper Filter */}
      {queryParam ? (
        <div className="rounded-2xl border border-neutral-800/80 bg-neutral-900/40 p-4 sm:p-5 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-neutral-400 font-medium">Search query:</span>
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
                <span>&ldquo;{queryParam}&rdquo;</span>
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="hover:text-white transition-colors p-0.5 rounded focus:outline-none cursor-pointer"
                  aria-label="Clear search"
                >
                  <span className="text-sm font-bold leading-none">&times;</span>
                </button>
              </span>

              {hasActiveNonSearchFilters && (
                <button
                  type="button"
                  onClick={handleResetFilters}
                  className="text-xs text-neutral-400 hover:text-white transition-colors underline ml-2 cursor-pointer"
                >
                  Reset All Filters
                </button>
              )}
            </div>

            {/* Compact Filter Results Toggle */}
            <button
              type="button"
              onClick={() => setShowSearchFilters(!showSearchFilters)}
              className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg border text-xs font-semibold transition-all cursor-pointer ${
                showSearchFilters || hasActiveNonSearchFilters
                  ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                  : "bg-neutral-900 border-neutral-800 text-neutral-300 hover:text-white hover:border-neutral-700"
              }`}
            >
              <SparklesIcon className="h-3.5 w-3.5" />
              <span>{showSearchFilters ? "Hide Discovery Filters" : "Filter Results"}</span>
              {hasActiveNonSearchFilters && (
                <span className="flex h-2 w-2 rounded-full bg-amber-400" />
              )}
            </button>
          </div>

          {/* Collapsible Stepper when requested or active filters present */}
          {showSearchFilters && (
            <div className="pt-3 border-t border-neutral-800/60">
              <ExplorerStepper
                filters={activeFilters}
                onFilterChange={handleFilterChange}
                onReset={handleResetFilters}
                decades={decades}
                languages={languages}
                industries={industries}
                genres={genres}
              />
            </div>
          )}
        </div>
      ) : (
        /* Full Guided Discovery Stepper Filter (Default for catalog browsing) */
        <ExplorerStepper
          filters={activeFilters}
          onFilterChange={handleFilterChange}
          onReset={handleResetFilters}
          decades={decades}
          languages={languages}
          industries={industries}
          genres={genres}
        />
      )}

      {/* Results Header & Sort Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2 border-b border-neutral-800/60 pb-4">
        <div className="text-sm text-neutral-400">
          {loading ? (
            <span>Updating catalog results...</span>
          ) : (
            <span className="font-medium">
              <strong className="text-white">{totalItems.toLocaleString()}</strong> title{totalItems === 1 ? "" : "s"} found
              {totalItems > 0 && (
                <span className="text-neutral-500 text-xs ml-2">
                  (Showing {startIndex}–{endIndex} of {totalItems.toLocaleString()})
                </span>
              )}
            </span>
          )}
        </div>

        {/* Sorting Dropdown */}
        <div className="flex items-center gap-2 self-end sm:self-auto">
          <label htmlFor="catalog-sort-select" className="text-xs text-neutral-400 whitespace-nowrap">
            Sort by:
          </label>
          <select
            id="catalog-sort-select"
            aria-label="Sort catalog titles"
            value={resolveSortValue(sortParam, sectionParam)}
            onChange={(e) => handleSortChange(e.target.value)}
            className="rounded-lg bg-neutral-900 border border-neutral-800 py-1.5 px-3 text-xs text-neutral-200 focus:border-amber-500 focus:outline-none transition-colors"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Catalog Grid State Machine */}
      {loading ? (
        <GridSkeleton count={20} />
      ) : error ? (
        <ErrorState
          message={error}
          onRetry={() => {
            setLoading(true);
            fetchTitles(activeFilters)
              .then((res) => {
                setTitles(res.items);
                setTotalItems(res.total);
                setTotalPages(res.total_pages ?? res.pages ?? 1);
                setLoading(false);
              })
              .catch((err) => {
                setError(err.message || "Failed to load titles.");
                setLoading(false);
              });
          }}
        />
      ) : titles.length === 0 ? (
        <EmptyState
          title="No titles found"
          message={
            queryParam
              ? `No movies or series matched "${queryParam}". Try a different title, spelling, or adjust your filters.`
              : "No movies or series match your current time, language, or culture filters. Try clearing or expanding your criteria."
          }
          onReset={handleResetFilters}
        />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5 gap-4 sm:gap-6">
            {titles.map((title) => (
              <TitleCard key={title.id} title={title} />
            ))}
          </div>

          {/* Sub-grid Range Indicator */}
          <div className="text-center text-xs text-neutral-500 pt-2">
            Showing {startIndex}–{endIndex} of {totalItems.toLocaleString()}
          </div>
        </div>
      )}

      {/* Server-Side Pagination Bar */}
      {!loading && totalPages > 1 && (
        <nav aria-label="Catalog pagination" className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2 pt-6 border-t border-neutral-800/80">
          {/* Previous Button */}
          <button
            onClick={() => handlePageChange(pageParam - 1)}
            disabled={!hasPrevious || pageParam <= 1}
            aria-label="Previous page"
            className="flex items-center gap-1 px-3 sm:px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-xs font-semibold text-neutral-300 hover:text-white hover:bg-neutral-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors mr-1"
          >
            <ChevronLeftIcon className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">Previous</span>
          </button>

          {/* Numbered Page Window */}
          {getPaginationPages(pageParam, totalPages).map((p, idx) => {
            if (p === "...") {
              return (
                <span
                  key={`ellipsis-${idx}`}
                  className="px-2 py-1 text-xs text-neutral-600 select-none"
                  aria-hidden="true"
                >
                  ...
                </span>
              );
            }

            const pageNum = Number(p);
            const isActive = pageNum === pageParam;

            return (
              <button
                key={`page-${pageNum}`}
                onClick={() => handlePageChange(pageNum)}
                aria-label={`Page ${pageNum}`}
                aria-current={isActive ? "page" : undefined}
                className={`min-w-[36px] h-9 px-2 rounded-lg text-xs font-bold border transition-all ${
                  isActive
                    ? "bg-amber-500 text-neutral-950 border-amber-500 shadow-md shadow-amber-500/20"
                    : "bg-neutral-900/80 border-neutral-800 text-neutral-300 hover:text-white hover:bg-neutral-800"
                }`}
              >
                {pageNum}
              </button>
            );
          })}

          {/* Next Button */}
          <button
            onClick={() => handlePageChange(pageParam + 1)}
            disabled={!hasNext || pageParam >= totalPages}
            aria-label="Next page"
            className="flex items-center gap-1 px-3 sm:px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-xs font-semibold text-neutral-300 hover:text-white hover:bg-neutral-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors ml-1"
          >
            <span className="hidden sm:inline">Next</span>
            <ChevronRightIcon className="h-4 w-4" aria-hidden="true" />
          </button>
        </nav>
      )}
    </div>
  );
}

export default function CatalogPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 space-y-8">
          <div className="h-10 w-64 bg-neutral-900 rounded-lg animate-pulse" />
          <GridSkeleton count={20} />
        </div>
      }
    >
      <CatalogContent />
    </Suspense>
  );
}

