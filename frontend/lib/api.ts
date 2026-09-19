import {
  Country,
  Decade,
  FeaturedDiscovery,
  Genre,
  Industry,
  Language,
  PaginatedResponse,
  SitemapEntry,
  TitleDetail,
  TitleFilterParams,
  TitleSummary,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const fetchOptions: RequestInit = {
      headers: {
        Accept: "application/json",
        ...options?.headers,
      },
      ...options,
    };
    if (!fetchOptions.cache && !(fetchOptions as any).next) {
      (fetchOptions as any).next = { revalidate: 30 };
    }
    const res = await fetch(url, fetchOptions);

    if (!res.ok) {
      let errorMessage = `API Error ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData?.detail) {
          errorMessage = typeof errorData.detail === "string" 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // use default error message
      }
      throw new Error(errorMessage);
    }

    return await res.json();
  } catch (error: any) {
    console.error(`[API] Failed to fetch ${url}:`, error.message);
    throw error;
  }
}

export async function fetchTitles(
  params: TitleFilterParams = {}
): Promise<PaginatedResponse<TitleSummary>> {
  const query = new URLSearchParams();

  if (params.type) query.append("type", params.type);
  if (params.category) query.append("category", params.category);
  if (params.is_anime !== undefined) query.append("is_anime", String(params.is_anime));
  if (params.language) query.append("language", params.language);
  if (params.industry) query.append("industry", params.industry);
  if (params.genre) query.append("genre", params.genre);
  if (params.year) query.append("year", String(params.year));
  if (params.decade) query.append("decade", String(params.decade));
  if (params.min_rating) query.append("min_rating", String(params.min_rating));
  if (params.min_vote_count) query.append("min_vote_count", String(params.min_vote_count));
  const searchKeyword = params.q || params.query;
  if (searchKeyword) query.append("q", searchKeyword);
  if (params.section) query.append("section", params.section);
  const sortOption = params.sort || params.sort_by;
  if (sortOption) query.append("sort", sortOption);
  if (params.page) query.append("page", String(params.page));
  if (params.page_size) query.append("page_size", String(params.page_size));

  const queryString = query.toString();
  return fetchJson<PaginatedResponse<TitleSummary>>(
    `/api/v1/titles${queryString ? `?${queryString}` : ""}`,
    { cache: "no-store" } // Ensure dynamic filter queries are not stale
  );
}

export async function fetchTitleDetail(id: number): Promise<TitleDetail> {
  return fetchJson<TitleDetail>(`/api/v1/titles/${id}`);
}

export async function fetchTitleByTmdb(
  tmdbId: number,
  type?: string
): Promise<TitleDetail> {
  const query = type ? `?type=${encodeURIComponent(type)}` : "";
  return fetchJson<TitleDetail>(`/api/v1/titles/tmdb/${tmdbId}${query}`);
}

export async function fetchLanguages(): Promise<Language[]> {
  return fetchJson<Language[]>("/api/v1/taxonomies/languages");
}

export async function fetchGenres(): Promise<Genre[]> {
  return fetchJson<Genre[]>("/api/v1/taxonomies/genres");
}

export async function fetchIndustries(): Promise<Industry[]> {
  return fetchJson<Industry[]>("/api/v1/taxonomies/industries");
}

export async function fetchCountries(): Promise<Country[]> {
  return fetchJson<Country[]>("/api/v1/taxonomies/countries");
}

export async function fetchDecades(): Promise<Decade[]> {
  return fetchJson<Decade[]>("/api/v1/taxonomies/decades");
}

export async function fetchFeaturedDiscovery(): Promise<FeaturedDiscovery> {
  return fetchJson<FeaturedDiscovery>("/api/v1/discovery/featured");
}

export async function fetchSitemapEntries(): Promise<SitemapEntry[]> {
  return fetchJson<SitemapEntry[]>("/api/v1/titles/sitemap-entries", {
    next: { revalidate: 3600 },
  });
}


