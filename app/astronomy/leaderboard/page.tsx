import FadeIn from "../../ui/fadein";
import LeaderboardTable from "../../ui/leaderboardtable";
import { loadAstronomyData } from "../../utils/domain-loader";

import styles from "../../styles/background.module.css";

export default function AstronomyLeaderboard() {
  const astronomyData = loadAstronomyData();

  return (
    <main 
      className="min-h-screen bg-black relative"
    >
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-2 sm:px-4">
        <div className="w-full max-w-6xl bg-white/10 backdrop-blur-sm rounded-lg p-3 sm:p-4 md:p-6 shadow-lg border border-white/20">
          <FadeIn>
            {/* Header */}
            <div className="flex items-center justify-between mb-4 sm:mb-6 md:mb-8">
              <a 
                href="/astronomy" 
                className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-3 sm:py-3 sm:px-4 md:px-6 rounded-full text-sm sm:text-base md:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
              >
                Chat
              </a>
              
              <div className="text-center flex-1 mx-2 sm:mx-4">
                <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-jersey text-white">
                  <span className="hidden sm:inline">Astrophysics & Cosmology</span>
                  <span className="sm:hidden">Astrophysics Libraries</span>
                </h1>
              </div>
              
              <a 
                href="/landing" 
                className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-3 sm:py-3 sm:px-4 md:px-6 rounded-full text-sm sm:text-base md:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
              >
                HOME
              </a>
            </div>

            {/* Description */}
            <div className="text-center mb-4 sm:mb-6 md:mb-8">
              <p className="text-sm sm:text-base md:text-lg mb-2 sm:mb-4 max-w-2xl mx-auto italic font-semibold text-muted font-inter">
                <span className="hidden sm:inline">Criteria: Number of stars on GitHub, Keywords: astrophysics & cosmology</span>
                <span className="sm:hidden">Top astrophysics libraries by GitHub stars</span>
              </p>
              <p className="text-muted max-w-3xl mx-auto font-inter text-xs sm:text-sm md:text-base hidden sm:block">
                {astronomyData.description}
              </p>
            </div>

            {/* Leaderboard */}
            <div className="flex justify-center">
              <LeaderboardTable
                title="Astrophysics & Cosmology"
                libraries={astronomyData.libraries}
              />
            </div>
          </FadeIn>
        </div>
      </div>
    </main>
  );
} 