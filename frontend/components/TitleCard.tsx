"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { getTmdbImageUrl } from "../lib/constants";
import { TitleSummary } from "../lib/types";
import { FilmIcon, StarIcon, TvIcon } from "./icons";

interface TitleCardProps {
  title: TitleSummary;
}

export default function TitleCard({ title }: TitleCardProps) {
  const [imageError, setImageError] = useState(false);

  const posterUrl = getTmdbImageUrl(title.poster_path, "w500");
  const releaseYear = title.release_date ? new Date(title.release_date).getFullYear() : null;
  const isMovie = title.type === "movie";

  // Primary culture/industry badge: first industry if available, otherwise original language
  const primaryIndustry = title.industries && title.industries.length > 0 ? title.industries[0] : null;

  return (
    <Link
      href={`/title/${title.id}`}
      className="group relative flex flex-col h-full rounded-xl overflow-hidden bg-neutral-900/60 border border-neutral-800/80 hover:border-amber-500/80 hover:bg-neutral-900/90 transition-colors duration-200 hover:shadow-lg hover:shadow-black/50"
    >
      {/* Poster Image Container */}
      <div className="relative aspect-[2/3] w-full flex-shrink-0 overflow-hidden bg-neutral-950">
        {posterUrl && !imageError ? (
          <Image
            src={posterUrl}
            alt={title.title}
            fill
            unoptimized
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
            className="object-cover group-hover:brightness-105 transition-[filter] duration-200"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center p-4 text-center bg-gradient-to-b from-neutral-900 to-neutral-950 text-neutral-600">
            {isMovie ? <FilmIcon className="h-12 w-12 mb-2" /> : <TvIcon className="h-12 w-12 mb-2" />}
            <span className="text-xs font-medium text-neutral-400 line-clamp-2">{title.title}</span>
          </div>
        )}

        {/* Content Type Badge (Movie / TV) */}
        <div className="absolute top-2 left-2">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold tracking-wide uppercase shadow-md ${
              isMovie
                ? "bg-amber-500/90 text-neutral-950 backdrop-blur-sm"
                : "bg-sky-500/90 text-neutral-950 backdrop-blur-sm"
            }`}
          >
            {isMovie ? "Movie" : "TV Series"}
          </span>
        </div>

        {/* TMDB Rating Badge */}
        {title.tmdb_rating !== null && title.tmdb_rating !== undefined && title.tmdb_rating > 0 && (
          <div className="absolute top-2 right-2">
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-xs font-bold bg-neutral-950/80 backdrop-blur-md text-amber-400 border border-neutral-800 shadow-md">
              <StarIcon className="h-3 w-3 fill-amber-400" />
              {title.tmdb_rating.toFixed(1)}
            </span>
          </div>
        )}

        {/* Bottom Poster Gradient */}
        <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-neutral-950/90 via-neutral-950/40 to-transparent" />
      </div>

      {/* Title Card Details with deterministic structural height */}
      <div className="p-3.5 flex flex-col flex-1 justify-between gap-2.5 bg-neutral-900/40">
        <div className="min-h-[38px] flex flex-col justify-start">
          <h4 className="font-semibold text-sm text-neutral-100 group-hover:text-amber-400 line-clamp-1 transition-colors">
            {title.title}
          </h4>

          {/* Secondary Subtitle / Original Title with consistent slot */}
          {title.original_title && title.original_title !== title.title ? (
            <p className="text-[11px] text-neutral-400 line-clamp-1 italic mt-0.5">
              {title.original_title}
            </p>
          ) : (
            <div className="h-4 mt-0.5" aria-hidden="true" />
          )}
        </div>

        <div className="space-y-1.5 pt-1.5 border-t border-neutral-800/60 mt-auto">
          {/* Metadata Row: Year & Industry/Language */}
          <div className="flex items-center justify-between text-xs text-neutral-300">
            <span>{releaseYear || "TBA"}</span>
            {primaryIndustry ? (
              <span className="text-[11px] font-medium text-amber-400 truncate max-w-[110px]" title={primaryIndustry}>
                {primaryIndustry}
              </span>
            ) : title.original_language ? (
              <span className="text-[11px] font-medium uppercase text-neutral-300">
                {title.original_language}
              </span>
            ) : null}
          </div>

          {/* Genres Line with consistent height */}
          <p className="text-[11px] text-neutral-300 truncate h-4">
            {title.genres && title.genres.length > 0
              ? title.genres.slice(0, 2).join(" • ")
              : "\u00A0"}
          </p>
        </div>
      </div>
    </Link>
  );
}

