export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
  pages?: number;
}

export interface TitleSummary {
  id: number;
  tmdb_id: number;
  type: "movie" | "tv";
  title: string;
  original_title?: string | null;
  release_date?: string | null;
  release_date_precision?: string | null;
  poster_path?: string | null;
  backdrop_path?: string | null;
  original_language?: string | null;
  tmdb_rating?: number | null;
  tmdb_vote_count?: number | null;
  tmdb_popularity?: number | null;
  is_anime: boolean;
  industries: string[];
  genres: string[];
}

export interface TitleIndustrySummary {
  name: string;
  confidence: number;
  source: string;
  is_manual_override: boolean;
}

export interface PersonSummary {
  id: number;
  tmdb_person_id: number;
  name: string;
  original_name?: string | null;
  profile_path?: string | null;
}

export interface CreditSummary {
  id: number;
  category: "cast" | "crew";
  role?: string | null;
  job?: string | null;
  department?: string | null;
  cast_order?: number | null;
  person: PersonSummary;
}

export interface SeasonSummary {
  id: number;
  tmdb_season_id: number;
  season_number: number;
  name?: string | null;
  overview?: string | null;
  poster_path?: string | null;
  air_date?: string | null;
  episode_count?: number | null;
}

export interface AlternateTitleSummary {
  title: string;
  country_code?: string | null;
}

export interface ExternalIdsSummary {
  imdb_id?: string | null;
  wikidata_id?: string | null;
}

export interface WatchProviderSummary {
  id: number;
  tmdb_provider_id: number;
  name: string;
  logo_path?: string | null;
  display_priority?: number | null;
}

export interface TitleWatchProvider {
  country_code: string;
  offer_type: "flatrate" | "rent" | "buy" | "free" | "ads" | string;
  type?: "flatrate" | "rent" | "buy" | "free" | "ads" | string;
  link?: string | null;
  provider: WatchProviderSummary;
}

export interface Language {
  id: number;
  code: string;
  name: string;
  title_count?: number | null;
}

export interface Genre {
  id: number;
  tmdb_id: number;
  name: string;
  title_count?: number | null;
}

export interface Industry {
  id: number;
  name: string;
  title_count?: number | null;
}

export interface Country {
  id: number;
  code: string;
  name: string;
  title_count?: number | null;
}

export interface Decade {
  decade: number;
  label: string;
  title_count: number;
}

export interface TitleDetail {
  id: number;
  tmdb_id: number;
  type: "movie" | "tv";
  title: string;
  original_title?: string | null;
  overview?: string | null;
  release_date?: string | null;
  release_date_precision?: string | null;
  poster_path?: string | null;
  backdrop_path?: string | null;
  original_language?: string | null;
  tmdb_rating?: number | null;
  tmdb_vote_count?: number | null;
  tmdb_popularity?: number | null;
  is_anime: boolean;

  genres: Genre[];
  languages: Language[];
  countries: Country[];
  industries: TitleIndustrySummary[];
  credits: CreditSummary[];
  seasons: SeasonSummary[];
  alternate_titles: AlternateTitleSummary[];
  external_ids?: ExternalIdsSummary | null;
  watch_providers: TitleWatchProvider[];
}

export interface FeaturedDiscovery {
  trending: TitleSummary[];
  top_rated: TitleSummary[];
  indian_regional: TitleSummary[];
  anime_spotlight: TitleSummary[];
  global_highlights: TitleSummary[];
}

export interface TitleFilterParams {
  type?: "movie" | "tv";
  category?: "anime" | string;
  is_anime?: boolean;
  language?: string;
  industry?: string;
  genre?: string;
  year?: number;
  decade?: number;
  min_rating?: number;
  min_vote_count?: number;
  query?: string;
  q?: string;
  section?: string;
  sort?: string;
  sort_by?: string;
  page?: number;
  page_size?: number;
}

export interface SitemapEntry {
  id: number;
  last_modified: string | null;
}


