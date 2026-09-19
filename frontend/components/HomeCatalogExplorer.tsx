"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import ExplorerStepper from "./ExplorerStepper";
import { ChevronLeftIcon, ChevronRightIcon, FilmIcon } from "./icons";
import { EmptyState, ErrorState, GridSkeleton } from "./StateViews";
import TitleCard from "./TitleCard";
import {
  fetchCountries,
  fetchDecades,
  fetchGenres,
  fetchIndustries,
  fetchLanguages,
  fetchTitles,
} from "../lib/api";
import { SORT_OPTIONS } from "../lib/constants";
import {
  Country,
  Decade,
  Genre,
  Industry,
  Language,
  TitleFilterParams,
  TitleSummary,
} from "../lib/types";

export default function HomeCatalogExplorer() {
  // Catalog State
  const [titles, setTitles] = useState<TitleSummary[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Taxonomy State
  const [decades, setDecades] = useState<Decade[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);

  // Active Filter Params
  const [filters, setFilters] = useState<TitleFilterParams>({
    sort_by: "popularity.desc",
    page: 1,
    page_size: 20,
  });

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

  // Fetch Catalog Titles whenever filters change
  const loadTitles = (currentFilters: TitleFilterParams) => {
    setLoading(true);
    setError(null);
    fetchTitles(currentFilters)
      .then((res) => {
        setTitles(res.items);
        setTotalItems(res.total);
        setTotalPages(res.total_pages ?? res.pages ?? 1);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load titles from catalog.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadTitles(filters);
  }, [filters]);

  const handleFilterChange = (newFilters: TitleFilterParams) => {
    setFilters(newFilters);
  };

  const handleResetFilters = () => {
    setFilters({
      sort_by: "popularity.desc",
      page: 1,
      page_size: 20,
    });
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setFilters((prev) => ({ ...prev, page: newPage }));
      const catalogEl = document.getElementById("catalog");
      if (catalogEl) {
        catalogEl.scrollIntoView({ behavior: "smooth" });
      }
    }
  };

  const handleSortChange = (newSort: string) => {
    setFilters((prev) => ({ ...prev, sort_by: newSort, page: 1 }));
  };

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

  const startIndex = totalItems > 0 ? ((filters.page || 1) - 1) * 20 + 1 : 0;
  const endIndex = Math.min((filters.page || 1) * 20, totalItems);

  return (
    <section id="catalog" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-8 pt-6">
      <div className="border-b border-neutral-800/80 pb-4">
        <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
          <FilmIcon className="h-6 w-6 text-amber-500" />
          Cinema Catalog & Time Explorer
        </h2>
        <p className="text-xs text-neutral-400 mt-1">
          Filter through time, language, and culture using the guided explorer below.
        </p>
      </div>

      {/* Established Cinema Explorer UX Funnel */}
      <ExplorerStepper
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleResetFilters}
        decades={decades}
        languages={languages}
        industries={industries}
        genres={genres}
      />

      {/* Results Bar & Sorting */}
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

        <div className="flex items-center gap-4">
          <Link
            href="/catalog"
            className="text-xs font-semibold text-amber-400 hover:text-amber-300 transition-colors hidden md:inline-flex items-center gap-1"
          >
            Open Full Catalog View →
          </Link>

          {/* Sorting Controls */}
          <div className="flex items-center gap-2 self-end sm:self-auto">
            <label className="text-xs text-neutral-400 whitespace-nowrap">Sort by:</label>
            <select
              value={filters.sort_by || "popularity.desc"}
              onChange={(e) => handleSortChange(e.target.value)}
              className="rounded-lg bg-neutral-900 border border-neutral-800 py-1.5 px-3 text-xs text-neutral-200 focus:border-amber-500 focus:outline-none"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Catalog Grid State Machine */}
      {loading ? (
        <GridSkeleton count={filters.page_size || 20} />
      ) : error ? (
        <ErrorState message={error} onRetry={() => loadTitles(filters)} />
      ) : titles.length === 0 ? (
        <EmptyState
          title="No cinema titles matched your criteria"
          message="No movies or series match your current time, language, or culture filters. Try clearing or expanding your criteria."
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

      {/* Numbered Pagination Bar */}
      {!loading && totalPages > 1 && (
        <div className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2 pt-6 border-t border-neutral-800/80">
          <button
            onClick={() => handlePageChange((filters.page || 1) - 1)}
            disabled={(filters.page || 1) <= 1}
            className="flex items-center gap-1 px-3 sm:px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-xs font-semibold text-neutral-300 hover:text-white hover:bg-neutral-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors mr-1"
          >
            <ChevronLeftIcon className="h-4 w-4" />
            <span className="hidden sm:inline">Previous</span>
          </button>

          {getPaginationPages(filters.page || 1, totalPages).map((p, idx) => {
            if (p === "...") {
              return (
                <span
                  key={`ellipsis-${idx}`}
                  className="px-2 py-1 text-xs text-neutral-600 select-none"
                >
                  ...
                </span>
              );
            }

            const pageNum = Number(p);
            const isActive = pageNum === (filters.page || 1);

            return (
              <button
                key={`page-${pageNum}`}
                onClick={() => handlePageChange(pageNum)}
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

          <button
            onClick={() => handlePageChange((filters.page || 1) + 1)}
            disabled={(filters.page || 1) >= totalPages}
            className="flex items-center gap-1 px-3 sm:px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-xs font-semibold text-neutral-300 hover:text-white hover:bg-neutral-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors ml-1"
          >
            <span className="hidden sm:inline">Next</span>
            <ChevronRightIcon className="h-4 w-4" />
          </button>
        </div>
      )}
    </section>
  );
}

