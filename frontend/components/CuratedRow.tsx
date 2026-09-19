"use client";

import Link from "next/link";
import { useRef } from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "./icons";
import TitleCard from "./TitleCard";
import { TitleSummary } from "../lib/types";

interface CuratedRowProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  titles: TitleSummary[];
  onExploreMore?: () => void;
  exploreHref?: string;
  exploreLabel?: string;
}

export default function CuratedRow({
  title,
  subtitle,
  icon,
  titles,
  onExploreMore,
  exploreHref,
  exploreLabel = "Explore All",
}: CuratedRowProps) {
  const rowRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: "left" | "right") => {
    if (rowRef.current) {
      const scrollAmount = rowRef.current.clientWidth * 0.75;
      rowRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  if (!titles || titles.length === 0) return null;

  return (
    <section className="space-y-4">
      {/* Header Row */}
      <div className="flex items-end justify-between px-1">
        <div className="flex items-center gap-3">
          {icon && <div className="text-amber-500">{icon}</div>}
          <div>
            <h3 className="text-xl font-bold tracking-tight text-white">{title}</h3>
            {subtitle && <p className="text-xs text-neutral-400 mt-0.5">{subtitle}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {exploreHref ? (
            <Link
              href={exploreHref}
              className="text-xs font-semibold text-amber-400 hover:text-amber-300 transition-colors px-2 py-1"
            >
              {exploreLabel} →
            </Link>
          ) : onExploreMore ? (
            <button
              onClick={onExploreMore}
              className="text-xs font-semibold text-amber-400 hover:text-amber-300 transition-colors px-2 py-1"
            >
              {exploreLabel} →
            </button>
          ) : null}
          <div className="hidden sm:flex items-center gap-1">
            <button
              onClick={() => scroll("left")}
              className="p-1.5 rounded-full bg-neutral-900 border border-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
              aria-label="Scroll left"
            >
              <ChevronLeftIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => scroll("right")}
              className="p-1.5 rounded-full bg-neutral-900 border border-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
              aria-label="Scroll right"
            >
              <ChevronRightIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Horizontal Carousel Row */}
      <div
        ref={rowRef}
        className="flex gap-4 sm:gap-5 overflow-x-auto pb-3 pt-1 scrollbar-none scroll-smooth -mx-4 px-4 sm:mx-0 sm:px-0"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
      >
        {titles.map((item) => (
          <div key={item.id} className="min-w-[160px] sm:min-w-[180px] md:min-w-[200px] flex-shrink-0 flex flex-col h-full">
            <TitleCard title={item} />
          </div>
        ))}
      </div>
    </section>
  );
}

