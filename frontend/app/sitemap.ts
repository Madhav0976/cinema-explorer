import type { MetadataRoute } from "next";
import { fetchSitemapEntries } from "../lib/api";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: `${siteUrl}`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1.0,
    },
    {
      url: `${siteUrl}/catalog`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
    {
      url: `${siteUrl}/featured`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
  ];

  try {
    const titles = await fetchSitemapEntries();
    const titleRoutes: MetadataRoute.Sitemap = titles.map((title) => ({
      url: `${siteUrl}/title/${title.id}`,
      lastModified: title.last_modified ? new Date(title.last_modified) : new Date(),
      changeFrequency: "weekly",
      priority: 0.8,
    }));

    return [...staticRoutes, ...titleRoutes];
  } catch (error) {
    console.error("[Sitemap] Failed to fetch sitemap title entries:", error);
    return staticRoutes;
  }
}

