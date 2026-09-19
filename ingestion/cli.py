import argparse
import logging
import sys
from pathlib import Path

from ingestion.services.checkpoint_service import CheckpointService
from ingestion.services.discovery_service import DiscoveryService, DiscoverySummary
from ingestion.services.ingestion_service import IngestionResult, IngestionService
from ingestion.tmdb.client import SensitiveDataFilter, install_sensitive_data_filter

DEFAULT_DISCOVERY_LANGUAGES = ["te", "hi", "ta", "ml", "kn", "en", "ja", "ko"]


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=level, format=format_str)
    install_sensitive_data_filter()
    for handler in logging.root.handlers:
        if not any(isinstance(f, SensitiveDataFilter) for f in handler.filters):
            handler.addFilter(SensitiveDataFilter())


def print_result(result: IngestionResult) -> None:
    print("-" * 60)
    print(f"Content Type : {result.content_type.upper()}")
    print(f"TMDB ID      : {result.tmdb_id}")
    print(f"Title        : {result.title}")
    print(f"Status       : {result.status.upper()}")
    print(f"Duration     : {result.duration_ms:.1f}ms")
    if result.status != "failed":
        print(f"Is Anime     : {'YES' if result.is_anime else 'NO'}")
        print(f"Industry     : {result.industry or 'N/A'}")
    else:
        print(f"Error        : {result.error}")
    print("-" * 60)


def print_seed_summary(results: list[IngestionResult]) -> None:
    print("\n" + "=" * 80)
    print("CINEMA EXPLORER SEED INGESTION SUMMARY")
    print("=" * 80)
    print(f"{'STATUS':<10} {'TYPE':<7} {'TMDB ID':<10} {'ANIME':<7} {'INDUSTRY':<18} {'TITLE':<24}")
    print("-" * 80)

    success_count = 0
    failure_count = 0

    for r in results:
        status_str = r.status.upper()
        anime_str = "YES" if r.is_anime else "NO"
        ind_str = (r.industry or "N/A")[:16]
        title_str = r.title[:22]
        if r.status in ("created", "updated"):
            success_count += 1
        else:
            failure_count += 1
        print(f"{status_str:<10} {r.content_type:<7} {r.tmdb_id:<10} {anime_str:<7} {ind_str:<18} {title_str:<24}")

    print("-" * 80)
    print(f"Total: {len(results)} | Success: {success_count} | Failed: {failure_count}")
    print("=" * 80 + "\n")


def print_discovery_summary(summary: DiscoverySummary) -> None:
    print("\n" + "=" * 60)
    print("CINEMA EXPLORER DISCOVERY SUMMARY")
    print("=" * 60)
    print(f"Summary:")
    print(f"  discovered={summary.discovered}")
    print(f"  new={summary.new}")
    print(f"  updated={summary.updated}")
    print(f"  skipped={summary.skipped}")
    print(f"  failed={summary.failed}")
    print(f"  duration={summary.duration_seconds:.1f}s")
    print("=" * 60 + "\n")


def main(argv: list[str] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ingestion.cli",
        description="Cinema Explorer TMDB Ingestion & Catalog Discovery CLI",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed debug logging",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Movie command
    movie_parser = subparsers.add_parser("movie", help="Ingest a single movie by TMDB ID")
    movie_parser.add_argument("tmdb_id", type=int, help="Numeric TMDB Movie ID")

    # 2. TV command
    tv_parser = subparsers.add_parser("tv", help="Ingest a single TV show by TMDB ID")
    tv_parser.add_argument("tmdb_id", type=int, help="Numeric TMDB TV Series ID")

    # 3. Seed command
    subparsers.add_parser("seed", help="Ingest the controlled discovery seed dataset")

    # 4. Discover command (Single slice across pages)
    discover_parser = subparsers.add_parser("discover", help="Discover and ingest titles for a specific slice")
    discover_parser.add_argument("content_type", choices=["movie", "tv"], help="Content type: movie or tv")
    discover_parser.add_argument("-l", "--language", type=str, default=None, help="Original language code (e.g. te, hi, ja)")
    discover_parser.add_argument("-y", "--year", type=int, default=None, help="Release / air year (e.g. 2022)")
    discover_parser.add_argument("-d", "--decade", type=int, default=None, help="Decade start year (e.g. 2020 for 2020-2029)")
    discover_parser.add_argument("--start-year", type=int, default=None, help="Start year of date range")
    discover_parser.add_argument("--end-year", type=int, default=None, help="End year of date range")
    discover_parser.add_argument("-p", "--pages", type=int, default=1, help="Number of pages to discover (default: 1)")
    discover_parser.add_argument("--min-vote-count", type=int, default=5, help="Minimum TMDB vote count threshold (default: 5)")
    discover_parser.add_argument("--sort-by", type=str, default="popularity.desc", help="TMDB sort order (default: popularity.desc)")
    discover_parser.add_argument("--dry-run", action="store_true", help="Preview discovery candidates without saving")
    discover_parser.add_argument("--no-resume", action="store_true", help="Disable checkpoint resume")
    discover_parser.add_argument("--checkpoint-file", type=str, default=None, help="Custom checkpoint JSON file path")
    discover_parser.add_argument("--update-existing", action="store_true", help="Re-fetch and update titles that already exist in database")
    discover_parser.add_argument("--delay", type=float, default=0.2, help="Delay in seconds between detail calls (default: 0.2)")

    # 5. Bulk command (Distributed cross-product catalog expansion)
    bulk_parser = subparsers.add_parser("bulk", help="Run distributed catalog expansion across languages and years")
    bulk_parser.add_argument(
        "--types",
        type=str,
        default="movie,tv",
        help="Comma-separated content types (default: movie,tv)",
    )
    bulk_parser.add_argument(
        "--languages",
        type=str,
        default=",".join(DEFAULT_DISCOVERY_LANGUAGES),
        help="Comma-separated language codes (default: te,hi,ta,ml,kn,en,ja,ko)",
    )
    bulk_parser.add_argument("--start-year", type=int, default=1990, help="Earliest release year (default: 1990)")
    bulk_parser.add_argument("--end-year", type=int, default=2025, help="Latest release year (default: 2025)")
    bulk_parser.add_argument("--pages-per-slice", type=int, default=1, help="Pages per language-year slice (default: 1)")
    bulk_parser.add_argument("--max-titles", type=int, default=5000, help="Maximum total titles to ingest (default: 5000)")
    bulk_parser.add_argument("--min-vote-count", type=int, default=5, help="Minimum TMDB vote count threshold (default: 5)")
    bulk_parser.add_argument("--sort-by", type=str, default="popularity.desc", help="TMDB sort order (default: popularity.desc)")
    bulk_parser.add_argument("--dry-run", action="store_true", help="Preview slices and candidates without saving")
    bulk_parser.add_argument("--no-resume", action="store_true", help="Disable checkpoint resume")
    bulk_parser.add_argument("--checkpoint-file", type=str, default=None, help="Custom checkpoint JSON file path")
    bulk_parser.add_argument("--update-existing", action="store_true", help="Re-fetch and update existing titles")
    bulk_parser.add_argument("--delay", type=float, default=0.2, help="Delay in seconds between detail calls (default: 0.2)")

    args = parser.parse_args(argv)
    setup_logging(args.verbose)

    service = IngestionService()

    if args.command == "movie":
        res = service.ingest_movie(args.tmdb_id)
        print_result(res)
        return 0 if res.status != "failed" else 1

    elif args.command == "tv":
        res = service.ingest_tv(args.tmdb_id)
        print_result(res)
        return 0 if res.status != "failed" else 1

    elif args.command == "seed":
        results = service.ingest_seed()
        print_seed_summary(results)
        any_failed = any(r.status == "failed" for r in results)
        return 1 if any_failed else 0

    elif args.command == "discover":
        ckpt = CheckpointService(
            filepath=args.checkpoint_file,
            enabled=not args.no_resume,
        )
        discovery = DiscoveryService(
            tmdb_client=service.client,
            ingestion_service=service,
            checkpoint_service=ckpt,
        )
        summary = discovery.discover(
            content_type=args.content_type,
            language=args.language,
            year=args.year,
            start_year=args.start_year,
            end_year=args.end_year,
            decade=args.decade,
            pages=args.pages,
            min_vote_count=args.min_vote_count,
            sort_by=args.sort_by,
            skip_existing=not args.update_existing,
            dry_run=args.dry_run,
            delay_seconds=args.delay,
        )
        print_discovery_summary(summary)
        return 0 if summary.failed == 0 else 1

    elif args.command == "bulk":
        types_list = [t.strip() for t in args.types.split(",") if t.strip()]
        langs_list = [l.strip() for l in args.languages.split(",") if l.strip()]

        ckpt = CheckpointService(
            filepath=args.checkpoint_file,
            enabled=not args.no_resume,
        )
        discovery = DiscoveryService(
            tmdb_client=service.client,
            ingestion_service=service,
            checkpoint_service=ckpt,
        )
        summary = discovery.bulk_ingest(
            types=types_list,
            languages=langs_list,
            start_year=args.start_year,
            end_year=args.end_year,
            pages_per_slice=args.pages_per_slice,
            max_titles=args.max_titles,
            min_vote_count=args.min_vote_count,
            sort_by=args.sort_by,
            skip_existing=not args.update_existing,
            dry_run=args.dry_run,
            delay_seconds=args.delay,
        )
        print_discovery_summary(summary)
        return 0 if summary.failed == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
