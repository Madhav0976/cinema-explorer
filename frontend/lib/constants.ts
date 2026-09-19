export const DISCOVERY_LANGUAGES = [
  { code: "te", name: "Telugu", native: "తెలుగు" },
  { code: "hi", name: "Hindi", native: "हिन्दी" },
  { code: "ta", name: "Tamil", native: "தமிழ்" },
  { code: "ml", name: "Malayalam", native: "മലയാളം" },
  { code: "kn", name: "Kannada", native: "ಕನ್ನಡ" },
  { code: "en", name: "English", native: "English" },
  { code: "ja", name: "Japanese", native: "日本語" },
  { code: "ko", name: "Korean", native: "한국어" },
] as const;

export const SORT_OPTIONS = [
  { value: "popularity.desc", label: "Popular" },
  { value: "rating.desc", label: "Top Rated" },
  { value: "release_date.desc", label: "Newest" },
  { value: "release_date.asc", label: "Oldest" },
  { value: "votes.desc", label: "Most Voted" },
  { value: "title.asc", label: "Title (A - Z)" },
] as const;

export const CONTENT_TYPE_TABS = [
  { id: "all", label: "All Content" },
  { id: "movie", label: "Movies" },
  { id: "tv", label: "TV Series" },
  { id: "anime", label: "Anime" },
] as const;

export const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p";

export function getTmdbImageUrl(
  path?: string | null,
  size: "w92" | "w154" | "w185" | "w342" | "w500" | "w780" | "original" = "w500"
): string | null {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  return `${TMDB_IMAGE_BASE}/${size}${path.startsWith("/") ? "" : "/"}${path}`;
}

const LEGACY_PROVIDER_LOGOS: Record<string, string> = {
  "/netflix.jpg": "/rK1KljqmbvO9HQa1PBFLILWah72.png",
  "/prime.jpg": "/gMZdpavHmxFNnLpMHwVxfqeux2g.png",
  "/gplay.jpg": "/aZRENwYILujqs0RVOZutTh0BVGV.png",
};

export function getProviderLogoUrl(
  path?: string | null,
  size: "w92" | "w154" | "w185" | "original" = "w92"
): string | null {
  if (!path) return null;
  const resolvedPath = LEGACY_PROVIDER_LOGOS[path] || path;
  return getTmdbImageUrl(resolvedPath, size);
}

