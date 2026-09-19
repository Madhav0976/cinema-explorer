export default function Footer() {
  return (
    <footer className="border-t border-neutral-800/80 bg-neutral-950 py-10 text-center text-neutral-400">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 space-y-3">
        {/* Brand Name */}
        <h2 className="text-base font-semibold tracking-tight text-white">
          Cinema Explorer
        </h2>

        {/* Product Tagline */}
        <p className="text-sm text-neutral-400">
          Explore movies and series through time, language, and culture.
        </p>

        {/* Engineering Credit */}
        <p className="pt-2 text-xs text-neutral-500">
          Cinema Explorer V1 · Built with Next.js, FastAPI &amp; PostgreSQL · Metadata via TMDB
        </p>
      </div>
    </footer>
  );
}
