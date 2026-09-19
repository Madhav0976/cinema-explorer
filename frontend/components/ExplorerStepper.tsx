"use client";

import { useState } from "react";
import { CONTENT_TYPE_TABS, DISCOVERY_LANGUAGES } from "../lib/constants";
import { Decade, Genre, Industry, Language, TitleFilterParams } from "../lib/types";
import {
  CalendarIcon,
  ChevronDownIcon,
  ClockIcon,
  FilmIcon,
  GlobeIcon,
  SparklesIcon,
  TagIcon,
  TvIcon,
  XMarkIcon,
} from "./icons";

interface ExplorerStepperProps {
  filters: TitleFilterParams;
  onFilterChange: (filters: TitleFilterParams) => void;
  onReset: () => void;
  decades: Decade[];
  languages: Language[];
  industries: Industry[];
  genres: Genre[];
}

export default function ExplorerStepper({
  filters,
  onFilterChange,
  onReset,
  decades,
  languages,
  industries,
  genres,
}: ExplorerStepperProps) {
  const [expandedSection, setExpandedSection] = useState<"time" | "language" | "culture" | null>(null);

  // Content type / category handling
  const activeContentType = filters.category === "anime" ? "anime" : (filters.type || "all");

  const handleContentTypeChange = (tabId: string) => {
    if (tabId === "all") {
      onFilterChange({ ...filters, type: undefined, category: undefined, is_anime: undefined, page: 1 });
    } else if (tabId === "anime") {
      onFilterChange({ ...filters, type: undefined, category: "anime", is_anime: true, page: 1 });
    } else {
      onFilterChange({ ...filters, type: tabId as "movie" | "tv", category: undefined, is_anime: undefined, page: 1 });
    }
  };

  const handleDecadeSelect = (decadeNum?: number) => {
    onFilterChange({
      ...filters,
      decade: decadeNum,
      year: undefined, // Reset specific year when decade changes
      page: 1,
    });
  };

  const handleYearSelect = (yearNum?: number) => {
    onFilterChange({
      ...filters,
      year: yearNum,
      page: 1,
    });
  };

  const handleLanguageSelect = (langCode?: string) => {
    onFilterChange({
      ...filters,
      language: langCode,
      page: 1,
    });
  };

  const handleIndustrySelect = (industryName?: string) => {
    onFilterChange({
      ...filters,
      industry: industryName,
      page: 1,
    });
  };

  const handleGenreSelect = (genreName?: string) => {
    onFilterChange({
      ...filters,
      genre: genreName,
      page: 1,
    });
  };

  // Generate years list for the selected decade
  const yearsInSelectedDecade = filters.decade
    ? Array.from({ length: 10 }, (_, i) => filters.decade! + i).filter(
        (y) => y <= new Date().getFullYear() + 1
      )
    : [];

  const hasActiveFilters = Boolean(
    filters.type ||
    filters.category ||
    filters.language ||
    filters.industry ||
    filters.genre ||
    filters.year ||
    filters.decade ||
    filters.query ||
    filters.min_rating
  );

  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900/50 backdrop-blur-md p-4 sm:p-6 shadow-xl space-y-6">
      {/* Top Bar: Primary Content Type Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800/80">
        <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-neutral-950 border border-neutral-800/90 w-fit max-w-full">
          {CONTENT_TYPE_TABS.map((tab) => {
            const isActive = activeContentType === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => handleContentTypeChange(tab.id)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                  isActive
                    ? "bg-amber-500 text-neutral-950 shadow-md shadow-amber-950/40"
                    : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900"
                }`}
              >
                {tab.id === "movie" && <FilmIcon className="h-3.5 w-3.5" />}
                {tab.id === "tv" && <TvIcon className="h-3.5 w-3.5" />}
                {tab.id === "anime" && <SparklesIcon className="h-3.5 w-3.5" />}
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Discovery Funnel Breadcrumbs / Progress */}
        <div className="hidden lg:flex items-center gap-2 text-xs text-neutral-400">
          <span className="font-semibold text-neutral-400 uppercase tracking-wider">Discovery Funnel:</span>
          <span className={filters.decade ? "text-amber-400 font-semibold" : ""}>TIME</span>
          <span>→</span>
          <span className={filters.decade ? "text-amber-400 font-semibold" : ""}>DECADE</span>
          <span>→</span>
          <span className={filters.year ? "text-amber-400 font-semibold" : ""}>YEAR</span>
          <span>→</span>
          <span className={filters.language ? "text-amber-400 font-semibold" : ""}>LANGUAGE/REGION</span>
          <span>→</span>
          <span className={filters.industry || filters.genre ? "text-amber-400 font-semibold" : ""}>GENRE/INDUSTRY</span>
          <span>→</span>
          <span className="text-amber-500 font-bold">DISCOVER</span>
        </div>
      </div>

      {/* Guided Explorer Dimensions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* STEP 1: TIME → DECADE & YEAR */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <ClockIcon className="h-4 w-4 text-amber-500" />
              <span>1. Time & Era</span>
            </div>
            {filters.decade && (
              <button
                onClick={() => handleDecadeSelect(undefined)}
                className="text-[11px] text-amber-400/80 hover:text-amber-300"
              >
                Clear Era
              </button>
            )}
          </div>

          {/* Decade Pills */}
          <div className="flex flex-wrap gap-1.5">
            <button
              onClick={() => handleDecadeSelect(undefined)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-colors ${
                !filters.decade
                  ? "bg-amber-500/20 border-amber-500/80 text-amber-300"
                  : "bg-neutral-950 border-neutral-800 text-neutral-400 hover:border-neutral-700 hover:text-neutral-300"
              }`}
            >
              All Eras
            </button>
            {decades.map((d) => {
              const isSelected = filters.decade === d.decade;
              return (
                <button
                  key={d.decade}
                  onClick={() => handleDecadeSelect(d.decade)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-colors flex items-center gap-1.5 ${
                    isSelected
                      ? "bg-amber-500/20 border-amber-500/80 text-amber-300"
                      : "bg-neutral-950 border-neutral-800 text-neutral-400 hover:border-neutral-700 hover:text-neutral-300"
                  }`}
                >
                  <span>{d.label}</span>
                  <span className="text-[10px] text-neutral-400">({d.title_count})</span>
                </button>
              );
            })}
          </div>

          {/* Year Drilldown (When decade is chosen) */}
          {filters.decade && yearsInSelectedDecade.length > 0 && (
            <div className="pt-2 border-t border-neutral-800/60 space-y-1.5">
              <div className="flex items-center justify-between text-xs text-neutral-400">
                <span className="flex items-center gap-1">
                  <CalendarIcon className="h-3 w-3 text-amber-400" />
                  Exact Year in {filters.decade}s:
                </span>
                {filters.year && (
                  <button
                    onClick={() => handleYearSelect(undefined)}
                    className="text-[10px] text-neutral-400 hover:text-neutral-200"
                  >
                    Any Year
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-1">
                {yearsInSelectedDecade.map((yr) => {
                  const isYearSelected = filters.year === yr;
                  return (
                    <button
                      key={yr}
                      onClick={() => handleYearSelect(isYearSelected ? undefined : yr)}
                      className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                        isYearSelected
                          ? "bg-amber-500 text-neutral-950 font-bold"
                          : "bg-neutral-950 text-neutral-400 hover:text-white hover:bg-neutral-800"
                      }`}
                    >
                      {yr}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* STEP 2: LANGUAGE & REGION (8 Primary Discovery Languages) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <GlobeIcon className="h-4 w-4 text-amber-500" />
              <span>2. Language & Culture</span>
            </div>
            {filters.language && (
              <button
                onClick={() => handleLanguageSelect(undefined)}
                className="text-[11px] text-amber-400/80 hover:text-amber-300"
              >
                Clear Language
              </button>
            )}
          </div>

          {/* 8 Discovery Languages Pills */}
          <div className="grid grid-cols-2 gap-1.5">
            {DISCOVERY_LANGUAGES.map((lang) => {
              const isSelected = filters.language === lang.code;
              return (
                <button
                  key={lang.code}
                  onClick={() => handleLanguageSelect(isSelected ? undefined : lang.code)}
                  className={`px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center justify-between transition-all ${
                    isSelected
                      ? "bg-amber-500/20 border-amber-500/80 text-amber-300 shadow-sm"
                      : "bg-neutral-950 border-neutral-800 text-neutral-400 hover:border-neutral-700 hover:text-neutral-300"
                  }`}
                >
                  <span className="font-semibold">{lang.name}</span>
                  <span className="text-[10px] text-neutral-400">{lang.native}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* STEP 3: INDUSTRY & GENRE */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <TagIcon className="h-4 w-4 text-amber-500" />
              <span>3. Industry & Genre</span>
            </div>
            {(filters.industry || filters.genre) && (
              <button
                onClick={() => onFilterChange({ ...filters, industry: undefined, genre: undefined, page: 1 })}
                className="text-[11px] text-amber-400/80 hover:text-amber-300"
              >
                Clear All
              </button>
            )}
          </div>

          {/* Industry Select Dropdown */}
          <div className="space-y-1">
            <label className="text-xs text-neutral-400">Cinema Industry:</label>
            <select
              value={filters.industry || ""}
              onChange={(e) => handleIndustrySelect(e.target.value || undefined)}
              className="w-full rounded-lg bg-neutral-950 border border-neutral-800 py-1.5 px-2.5 text-xs text-neutral-200 focus:border-amber-500 focus:outline-none"
            >
              <option value="">All Industries</option>
              {industries.map((ind) => (
                <option key={ind.id} value={ind.name}>
                  {ind.name} {ind.title_count !== null ? `(${ind.title_count})` : ""}
                </option>
              ))}
            </select>
          </div>

          {/* Genre Select Dropdown */}
          <div className="space-y-1">
            <label className="text-xs text-neutral-400">Genre:</label>
            <select
              value={filters.genre || ""}
              onChange={(e) => handleGenreSelect(e.target.value || undefined)}
              className="w-full rounded-lg bg-neutral-950 border border-neutral-800 py-1.5 px-2.5 text-xs text-neutral-200 focus:border-amber-500 focus:outline-none"
            >
              <option value="">All Genres</option>
              {genres.map((g) => (
                <option key={g.id} value={g.name}>
                  {g.name} {g.title_count !== null ? `(${g.title_count})` : ""}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Active Filter Chips & Reset Bar */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-neutral-800/80">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-semibold text-neutral-400 mr-1">Active:</span>

            {/* Type Chip */}
            {filters.type && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-neutral-800 text-neutral-200 border border-neutral-700">
                Type: {filters.type === "movie" ? "Movie" : "TV Series"}
                <button onClick={() => onFilterChange({ ...filters, type: undefined, page: 1 })}>
                  <XMarkIcon className="h-3 w-3 text-neutral-400 hover:text-white" />
                </button>
              </span>
            )}

            {/* Anime Category Chip */}
            {filters.category === "anime" && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40">
                Category: Anime
                <button onClick={() => onFilterChange({ ...filters, category: undefined, is_anime: undefined, page: 1 })}>
                  <XMarkIcon className="h-3 w-3 text-amber-400 hover:text-white" />
                </button>
              </span>
            )}

            {/* Decade Chip */}
            {filters.decade && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-neutral-800 text-neutral-200 border border-neutral-700">
                Decade: {filters.decade}s
                <button onClick={() => handleDecadeSelect(undefined)}>
                  <XMarkIcon className="h-3 w-3 text-neutral-400 hover:text-white" />
                </button>
              </span>
            )}

            {/* Year Chip */}
            {filters.year && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-neutral-800 text-neutral-200 border border-neutral-700">
                Year: {filters.year}
                <button onClick={() => handleYearSelect(undefined)}>
                  <XMarkIcon className="h-3 w-3 text-neutral-400 hover:text-white" />
                </button>
              </span>
            )}

            {/* Language Chip */}
            {filters.language && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-neutral-800 text-neutral-200 border border-neutral-700">
                Language: {DISCOVERY_LANGUAGES.find((l) => l.code === filters.language)?.name || filters.language}
                <button onClick={() => handleLanguageSelect(undefined)}>
                  <XMarkIcon className="h-3 w-3 text-neutral-400 hover:text-white" />
                </button>
              </span>
            )}

            {/* Industry Chip */}
            {filters.industry && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-neutral-800 text-neutral-200 border border-neutral-700">
                Industry: {filters.industry}
                <button onClick={() => handleIndustrySelect(undefined)}>
                  <XMarkIcon className="h-3 w-3 text-neutral-400 hover:text-white" />
                </button>
              </span>
            )}

            {/* Genre Chip */}
            {filters.genre && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-neutral-800 text-neutral-200 border border-neutral-700">
                Genre: {filters.genre}
                <button onClick={() => handleGenreSelect(undefined)}>
                  <XMarkIcon className="h-3 w-3 text-neutral-400 hover:text-white" />
                </button>
              </span>
            )}

            {/* Search Query Chip */}
            {filters.query && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-neutral-800 text-neutral-200 border border-neutral-700">
                Search: &ldquo;{filters.query}&rdquo;
                <button onClick={() => onFilterChange({ ...filters, query: undefined, page: 1 })}>
                  <XMarkIcon className="h-3 w-3 text-neutral-400 hover:text-white" />
                </button>
              </span>
            )}
          </div>

          <button
            onClick={onReset}
            className="text-xs font-semibold text-rose-400 hover:text-rose-300 transition-colors"
          >
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
}

