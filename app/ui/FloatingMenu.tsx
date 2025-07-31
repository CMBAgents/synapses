"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";

export default function FloatingMenu() {
  const [hovered, setHovered] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // Check if we're on a domain page
  const isOnAstronomyPage = pathname === "/astronomy";
  const isOnFinancePage = pathname === "/finance";
  const isOnAstronomyLeaderboard = pathname === "/astronomy/leaderboard";
  const isOnFinanceLeaderboard = pathname === "/finance/leaderboard";
  
  // Determine destination based on current page
  let destination;
  if (isOnAstronomyPage) {
    destination = "/astronomy/leaderboard"; // Go to astronomy leaderboard
  } else if (isOnFinancePage) {
    destination = "/finance/leaderboard"; // Go to finance leaderboard
  } else if (isOnAstronomyLeaderboard) {
    destination = "/astronomy"; // Go back to astronomy chat
  } else if (isOnFinanceLeaderboard) {
    destination = "/finance"; // Go back to finance chat
  } else {
    destination = "/domain-selector"; // Default fallback
  }

  // Don't show the floating menu on landing page or domain selector
  if (pathname === "/landing" || pathname === "/domain-selector") {
    return null;
  }

  return (
    <div
      className="relative z-50"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <button
        className={`
          relative rounded-full w-12 h-12 flex items-center justify-center
          transition-all duration-300 shadow-lg focus:outline-none focus:ring-2
          bg-white/20 backdrop-blur-md border border-white/30
          text-white hover:bg-white/30 hover:border-white/50 hover:scale-110
          focus:ring-white/50
        `}
        aria-label="Menu de navigation"
      >
        {/* Icône ☰ */}
        <span className="text-lg select-none">
          ☰
        </span>
      </button>

      {/* Menu au survol avec animation */}
      <div className="absolute top-1/2 -translate-y-1/2 left-full ml-3 flex flex-col gap-2">
        {/* Premier bouton - Chat/Leaderboard */}
        <button
          onClick={() => router.push(isOnAstronomyLeaderboard || isOnFinanceLeaderboard ? 
            (isOnAstronomyLeaderboard ? "/astronomy" : "/finance") : 
            (isOnAstronomyPage ? "/astronomy/leaderboard" : "/finance/leaderboard"))}
          className={`w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg shadow-lg transition-all duration-200 px-4 py-3 text-white hover:bg-white/20 text-left font-inter whitespace-nowrap ${
            hovered 
              ? 'opacity-100 transform translate-x-0 scale-100' 
              : 'opacity-0 transform translate-x-2 scale-95 pointer-events-none'
          }`}
        >
          {isOnAstronomyLeaderboard || isOnFinanceLeaderboard ? "Chat" : "Leaderboard"}
        </button>
        
        {/* Deuxième bouton - Change Domain */}
        <button
          onClick={() => router.push("/domain-selector")}
          className={`w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg shadow-lg transition-all duration-200 px-4 py-3 text-white hover:bg-white/20 text-left font-inter whitespace-nowrap ${
            hovered 
              ? 'opacity-100 transform translate-x-0 scale-100' 
              : 'opacity-0 transform translate-x-2 scale-95 pointer-events-none'
          }`}
        >
          Change Domain
        </button>
      </div>
    </div>
  );
}
