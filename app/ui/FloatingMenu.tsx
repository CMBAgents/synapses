"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";

export default function FloatingMenu() {
  const [hovered, setHovered] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // On change la destination selon la page actuelle
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
          relative rounded-full bg-blue-600 text-white w-14 h-14 flex items-center justify-center
          shadow-md transition-colors duration-300 focus:outline-none focus:ring-4 focus:ring-blue-400
          ${hovered ? "bg-blue-700" : "bg-blue-600"}
        `}
        aria-label="Ouvrir le menu"
        onClick={() => router.push(destination)}
      >
        {/* Cercle fin au centre */}
        <span
          className="absolute w-10 h-10 rounded-full border-2 border-white pointer-events-none"
          aria-hidden="true"
        ></span>

        {/* Icône ☰ qui disparaît au survol */}
        <span
          className={`relative text-2xl select-none transition-opacity duration-300 ${
            hovered ? "opacity-0" : "opacity-100"
          }`}
        >
          ☰
        </span>
      </button>

      {/* Boîte texte centrée au-dessus */}
      {hovered && (
        <div
          className="absolute bottom-full mb-3 left-1/2 transform -translate-x-1/2
                     bg-white dark:bg-gray-900 shadow-lg rounded-lg px-5 py-2
                     text-gray-800 dark:text-gray-200 whitespace-nowrap
                     text-center text-lg font-semibold z-60"
        >
          Leaderboard
        </div>
      )}
    </div>
  );
}
