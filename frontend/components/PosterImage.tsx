"use client";

import Image from "next/image";
import { useState } from "react";
import { FilmIcon, TvIcon } from "./icons";

interface PosterImageProps {
  src: string | null;
  alt: string;
  type: "movie" | "tv";
  priority?: boolean;
  className?: string;
  sizes?: string;
}

export default function PosterImage({
  src,
  alt,
  type,
  priority = false,
  className = "object-cover",
  sizes = "(max-width: 768px) 100vw, 33vw",
}: PosterImageProps) {
  const [error, setError] = useState(false);

  if (!src || error) {
    return (
      <div className="flex h-full w-full flex-col items-center justify-center p-6 text-center bg-gradient-to-b from-neutral-900 to-neutral-950 text-neutral-600">
        {type === "movie" ? <FilmIcon className="h-16 w-16 mb-2" /> : <TvIcon className="h-16 w-16 mb-2" />}
        <span className="text-xs font-medium text-neutral-400 line-clamp-2">{alt}</span>
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      fill
      unoptimized
      priority={priority}
      sizes={sizes}
      className={className}
      onError={() => setError(true)}
    />
  );
}

