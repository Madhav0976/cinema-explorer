"use client";

import { useRouter } from "next/navigation";
import { ChevronLeftIcon } from "./icons";

interface BackButtonProps {
  fallbackHref?: string;
  label?: string;
}

export default function BackButton({
  fallbackHref = "/catalog",
  label = "Back to Explorer",
}: BackButtonProps) {
  const router = useRouter();

  const handleBack = () => {
    // If the browser has history entries, router.back() preserves exact search/filters/page state
    if (typeof window !== "undefined" && window.history.length > 1) {
      router.back();
    } else {
      router.push(fallbackHref);
    }
  };

  return (
    <button
      type="button"
      onClick={handleBack}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-neutral-900/80 backdrop-blur-md border border-neutral-800 text-neutral-300 hover:text-white hover:bg-neutral-800 transition-colors text-xs font-semibold shadow-lg cursor-pointer"
    >
      <ChevronLeftIcon className="h-4 w-4" />
      {label}
    </button>
  );
}

