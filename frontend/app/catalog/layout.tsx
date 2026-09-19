import type { Metadata } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  title: "Browse Catalog — Cinema Explorer",
  description:
    "Explore and filter cinema across decades, languages, industries, and genres. Discover movies and series from South Asian regional cinema, Japanese anime, Korean cinema, and Hollywood classics.",
  alternates: {
    canonical: `${siteUrl}/catalog`,
  },
  openGraph: {
    title: "Browse Catalog — Cinema Explorer",
    description:
      "Explore and filter cinema across decades, languages, industries, and genres.",
    url: `${siteUrl}/catalog`,
    siteName: "Cinema Explorer",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Browse Catalog — Cinema Explorer",
    description:
      "Explore and filter cinema across decades, languages, industries, and genres.",
  },
};

export default function CatalogLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

