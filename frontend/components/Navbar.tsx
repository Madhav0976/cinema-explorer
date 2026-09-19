"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { SearchIcon, XMarkIcon } from "./icons";

interface NavbarProps {
  onSearchSubmit?: (query: string) => void;
  searchQuery?: string;
}

export default function Navbar({ onSearchSubmit, searchQuery }: NavbarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Read search query from URL params if available, otherwise fallback to prop or empty
  const urlQuery = searchParams ? searchParams.get("q") || searchParams.get("query") || "" : "";
  const [localQuery, setLocalQuery] = useState(searchQuery !== undefined ? searchQuery : urlQuery);

  // Keep localQuery synced whenever the URL search param or searchQuery prop changes
  useEffect(() => {
    if (searchQuery !== undefined) {
      setLocalQuery(searchQuery);
    } else if (searchParams) {
      const q = searchParams.get("q") || searchParams.get("query") || "";
      setLocalQuery(q);
    }
  }, [searchParams, searchQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = localQuery.trim();
    if (onSearchSubmit) {
      onSearchSubmit(trimmed);
    } else {
      if (trimmed) {
        if (pathname === "/catalog" && searchParams) {
          const newParams = new URLSearchParams(searchParams.toString());
          newParams.set("q", trimmed);
          newParams.delete("page"); // Reset page to 1 on new search
          router.push(`/catalog?${newParams.toString()}`);
        } else {
          router.push(`/catalog?q=${encodeURIComponent(trimmed)}`);
        }
      } else {
        router.push("/catalog");
      }
    }
  };

  const handleClear = () => {
    setLocalQuery("");
    if (onSearchSubmit) {
      onSearchSubmit("");
    } else {
      // When on /catalog, clear query parameters (q, query) and page, but preserve any other active filters
      if (pathname === "/catalog" && searchParams) {
        const newParams = new URLSearchParams(searchParams.toString());
        newParams.delete("q");
        newParams.delete("query");
        newParams.delete("page");
        const qs = newParams.toString();
        router.push(`/catalog${qs ? `?${qs}` : ""}`);
      } else {
        // From any other page, navigate directly to /catalog, NEVER to /
        router.push("/catalog");
      }
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-neutral-800/80 bg-neutral-950/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo & Tagline */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative flex h-9 w-9 items-center justify-center overflow-hidden rounded-lg bg-neutral-900/80 border border-neutral-800/90 shadow-md shadow-amber-950/30 group-hover:scale-105 transition-transform duration-200">
              <Image
                src="/logo.png"
                alt="Cinema Explorer Symbol"
                width={36}
                height={36}
                className="object-contain"
                priority
              />
            </div>
            <div>
              <span className="text-xl font-black tracking-tight text-white group-hover:text-amber-400 transition-colors">
                Cinema Explorer
              </span>
              <span className="hidden sm:block text-xs font-medium tracking-wider text-neutral-400 uppercase">
                Time • Language • Culture
              </span>
            </div>
          </Link>
        </div>

        {/* Global Search Bar */}
        <div className="flex-1 max-w-md mx-4 hidden md:block">
          <form onSubmit={handleSubmit} className="relative" role="search">
            <input
              type="text"
              aria-label="Search by title, original title, or alternate name"
              placeholder="Search by title, original title, or alternate name..."
              value={localQuery}
              onChange={(e) => setLocalQuery(e.target.value)}
              className="w-full rounded-full bg-neutral-900 border border-neutral-800 py-2 pl-10 pr-9 text-sm text-neutral-100 placeholder-neutral-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition-all"
            />
            <SearchIcon className="absolute left-3.5 top-2.5 h-4 w-4 text-neutral-500" aria-hidden="true" />
            {localQuery && (
              <button
                type="button"
                onClick={handleClear}
                aria-label="Clear search query"
                className="absolute right-3 top-2.5 text-neutral-400 hover:text-white"
                title="Clear search"
              >
                <XMarkIcon className="h-4 w-4" aria-hidden="true" />
              </button>
            )}
          </form>
        </div>

        {/* Navigation Links */}
        <nav className="flex items-center gap-2 sm:gap-4" aria-label="Main Navigation">
          <Link
            href="/catalog"
            className="px-3 py-1.5 text-sm font-medium text-neutral-300 hover:text-white hover:bg-neutral-900/60 rounded-lg transition-colors"
          >
            Catalog
          </Link>
          <Link
            href="/featured"
            className="px-3 py-1.5 text-sm font-medium text-neutral-300 hover:text-white hover:bg-neutral-900/60 rounded-lg transition-colors"
          >
            Featured Hubs
          </Link>
        </nav>
      </div>

      {/* Mobile Search Bar */}
      <div className="md:hidden border-t border-neutral-800/60 px-4 py-2 bg-neutral-950">
        <form onSubmit={handleSubmit} className="relative" role="search">
          <input
            type="text"
            aria-label="Search titles"
            placeholder="Search titles..."
            value={localQuery}
            onChange={(e) => setLocalQuery(e.target.value)}
            className="w-full rounded-full bg-neutral-900 border border-neutral-800 py-2 pl-10 pr-9 text-sm text-neutral-100 placeholder-neutral-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />
          <SearchIcon className="absolute left-3.5 top-2.5 h-4 w-4 text-neutral-500" aria-hidden="true" />
          {localQuery && (
            <button
              type="button"
              onClick={handleClear}
              aria-label="Clear search query"
              className="absolute right-3 top-2.5 text-neutral-400 hover:text-white"
              title="Clear search"
            >
              <XMarkIcon className="h-4 w-4" aria-hidden="true" />
            </button>
          )}
        </form>
      </div>
    </header>
  );
}
