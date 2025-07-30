"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";

export default function FloatingMenu() {
  const [hovered, setHovered] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const isOnHomePage = pathname === "/";
  const destination = isOnHomePage ? "/page2" : "/";

  return (
    <div
      className="fixed bottom-10 left-1/2 transform -translate-x-1/2 z-50"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <button
        className={`
          relative rounded-full w-14 h-14 flex items-center justify-center
          transition-colors duration-300 shadow-md focus:outline-none focus:ring-4
          ${hovered
            ? "bg-white dark:bg-neutral-800"
            : "bg-white dark:bg-black"}
          text-black dark:text-white
          focus:ring-neutral-400 dark:focus:ring-white
        `}
        aria-label="Ouvrir le menu"
        onClick={() => router.push(destination)}
      >
        {/* Cercle au centre */}
        <span
          className="absolute w-10 h-10 rounded-full border-2 border-current pointer-events-none"
          aria-hidden="true"
        ></span>

        {/* Icône ☰ */}
        <span
          className={`relative text-2xl select-none transition-opacity duration-300 ${
            hovered ? "opacity-0" : "opacity-100"
          }`}
        >
          ☰
        </span>
      </button>

      {/* Texte au survol */}
      {hovered && (
        <div
          className="absolute bottom-full mb-3 left-1/2 transform -translate-x-1/2
                     bg-white dark:bg-black shadow-lg rounded-lg px-5 py-2
                     text-black dark:text-white whitespace-nowrap
                     text-center text-lg font-semibold z-60"
        >
          {isOnHomePage ? "Leaderboard" : "Select a Library"}
        </div>
      )}
    </div>
  );
}
