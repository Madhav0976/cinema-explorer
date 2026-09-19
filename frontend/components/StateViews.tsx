import React from "react";
import { FilmIcon, RefreshIcon, SearchIcon } from "./icons";

export function CardSkeleton() {
  return (
    <div className="flex flex-col rounded-xl overflow-hidden bg-neutral-900/60 border border-neutral-800/60 animate-pulse">
      <div className="aspect-[2/3] w-full bg-neutral-800/70" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-neutral-800 rounded w-3/4" />
        <div className="flex items-center justify-between">
          <div className="h-3 bg-neutral-800 rounded w-1/4" />
          <div className="h-3 bg-neutral-800 rounded w-1/4" />
        </div>
        <div className="h-3 bg-neutral-800/60 rounded w-1/2" />
      </div>
    </div>
  );
}

export function GridSkeleton({ count = 10 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5 gap-4 sm:gap-6">
      {Array.from({ length: count }).map((_, idx) => (
        <CardSkeleton key={idx} />
      ))}
    </div>
  );
}

export function DetailSkeleton() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-pulse space-y-8">
      <div className="h-80 md:h-96 w-full bg-neutral-900 rounded-2xl border border-neutral-800" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="h-96 bg-neutral-900 rounded-xl" />
        <div className="md:col-span-2 space-y-4">
          <div className="h-8 bg-neutral-800 rounded w-1/2" />
          <div className="h-4 bg-neutral-800 rounded w-full" />
          <div className="h-4 bg-neutral-800 rounded w-5/6" />
          <div className="h-24 bg-neutral-900 rounded-xl mt-6" />
        </div>
      </div>
    </div>
  );
}

export function EmptyState({
  title = "No titles found",
  message = "No movies or series match the selected discovery criteria. Try expanding your decade, language, or industry filters.",
  onReset,
}: {
  title?: string;
  message?: string;
  onReset?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center rounded-2xl border border-neutral-800/80 bg-neutral-900/30">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-neutral-900 border border-neutral-800 text-neutral-400 mb-4 shadow-inner">
        <SearchIcon className="h-8 w-8 text-neutral-400" />
      </div>
      <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
      <p className="text-sm text-neutral-400 max-w-md mb-6">{message}</p>
      {onReset && (
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-neutral-950 font-semibold text-sm transition-colors shadow-lg shadow-amber-950/30"
        >
          <RefreshIcon className="h-4 w-4" />
          Reset All Filters
        </button>
      )}
    </div>
  );
}

export function ErrorState({
  message = "Failed to load titles from the catalog. Please ensure the backend service is running.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center rounded-2xl border border-rose-900/50 bg-rose-950/20">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-rose-950/50 border border-rose-800 text-rose-400 mb-4">
        <FilmIcon className="h-8 w-8 text-rose-400" />
      </div>
      <h3 className="text-lg font-bold text-white mb-2">Unable to Connect to Cinema Catalog</h3>
      <p className="text-sm text-rose-300/80 max-w-md mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm transition-colors shadow-lg shadow-rose-950/50"
        >
          <RefreshIcon className="h-4 w-4" />
          Retry Connection
        </button>
      )}
    </div>
  );
}

