"use client";

import Image from "next/image";
import { useState } from "react";
import { getProviderLogoUrl } from "../lib/constants";
import { ExternalLinkIcon } from "./icons";

interface ProviderBadgeProps {
  name: string;
  logoPath?: string | null;
  link?: string | null;
  offerType?: string | null;
}

export default function ProviderBadge({
  name,
  logoPath,
  link,
  offerType,
}: ProviderBadgeProps) {
  const [imgError, setImgError] = useState(false);
  const logoUrl = getProviderLogoUrl(logoPath);

  const getTag = () => {
    if (!offerType) return null;
    const norm = offerType.toLowerCase();
    if (norm === "free") return "Free";
    if (norm === "ads") return "Ads";
    return null;
  };

  const tag = getTag();

  const content = (
    <>
      {logoUrl && !imgError ? (
        <div className="relative w-6 h-6 rounded-md overflow-hidden bg-neutral-800 flex-shrink-0 border border-neutral-700/40">
          <Image
            src={logoUrl}
            alt={name}
            fill
            unoptimized
            sizes="24px"
            className="object-cover"
            onError={() => setImgError(true)}
          />
        </div>
      ) : (
        <div className="w-6 h-6 rounded-md bg-neutral-800 border border-neutral-700/60 flex items-center justify-center text-[10px] font-bold text-neutral-300 flex-shrink-0">
          {name.slice(0, 2).toUpperCase()}
        </div>
      )}

      <span className="text-xs font-medium text-neutral-200 group-hover:text-white transition-colors truncate max-w-[160px]">
        {name}
      </span>

      {tag && (
        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-400/10 text-amber-300 border border-amber-400/20">
          {tag}
        </span>
      )}

      {link && (
        <ExternalLinkIcon className="w-3 h-3 text-neutral-500 group-hover:text-amber-400 transition-colors ml-0.5 flex-shrink-0" />
      )}
    </>
  );

  const containerClasses =
    "inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-neutral-900/90 border border-neutral-800 hover:border-neutral-700 hover:bg-neutral-800/80 transition-all text-xs group shadow-sm";

  if (link) {
    return (
      <a
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        title={`Watch on ${name} (via TMDB)`}
        className={containerClasses}
      >
        {content}
      </a>
    );
  }

  return <div className={containerClasses}>{content}</div>;
}

