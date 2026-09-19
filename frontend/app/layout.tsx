import type { Metadata } from "next";
import { Suspense } from "react";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Cinema Explorer — Explore Movies & Series Through Time, Language & Culture",
  description:
    "Explore movies and series across decades, languages, industries, and cultures—from South Asian regional cinema and Japanese anime to Korean cinema and Hollywood classics.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "Cinema Explorer — Explore Movies & Series Through Time, Language & Culture",
    description:
      "Explore movies and series across decades, languages, industries, and cultures—from South Asian regional cinema and Japanese anime to Korean cinema and Hollywood classics.",
    url: siteUrl,
    siteName: "Cinema Explorer",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Cinema Explorer — Explore Movies & Series Through Time, Language & Culture",
    description:
      "Explore movies and series across decades, languages, industries, and cultures—from South Asian regional cinema and Japanese anime to Korean cinema and Hollywood classics.",
  },
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png",
  },
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-950 text-neutral-100 antialiased font-sans flex flex-col justify-between">
        <div>
          <Suspense fallback={<header className="sticky top-0 z-50 w-full border-b border-neutral-800/80 bg-neutral-950/90 backdrop-blur-md h-16" />}>
            <Navbar />
          </Suspense>
          <main>{children}</main>
        </div>
        <Footer />
      </body>
    </html>
  );
}
