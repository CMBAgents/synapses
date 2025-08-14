import FadeIn from "../../ui/fadein";
import LeaderboardTable from "../../ui/leaderboardtable";
import { loadFinanceData } from "../../utils/domain-loader";

import styles from "../../styles/background.module.css";

export default function FinanceLeaderboard() {
  const financeData = loadFinanceData();

  return (
    <main 
      className="min-h-screen bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('/pexels-slendyalex-3745234.jpg')" }}
    >
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-start px-2 sm:px-4 pt-8 sm:pt-12 md:pt-16">
        {/* Title outside the frame */}
        <div className="text-center mb-6 sm:mb-8 md:mb-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-jersey text-white">
            Finance & Trading
          </h1>
        </div>

        {/* Translucent frame starts here */}
        <div className="w-full max-w-6xl bg-white/10 backdrop-blur-sm rounded-lg p-3 sm:p-4 md:p-6 shadow-lg border border-white/20">
          <FadeIn>
            {/* Header */}
            <div className="flex items-center justify-between mb-4 sm:mb-6 md:mb-8">
              <a 
                href="/chat/finance" 
                className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-3 sm:py-3 sm:px-4 md:px-6 rounded-full text-sm sm:text-base md:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
              >
                Chat
              </a>
              
              <div className="text-center flex-1 mx-2 sm:mx-4">
                <h2 className="text-xl sm:text-2xl md:text-3xl font-inter text-white">
                  Leaderboard
                </h2>
              </div>
              
              <a 
                href="/landing" 
                className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-3 sm:py-3 sm:px-4 md:px-6 rounded-full text-sm sm:text-base md:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter flex items-center"
              >
                <svg width="20" height="20" className="sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
                </svg>
              </a>
            </div>

            {/* Description */}
            <div className="text-center mb-4 sm:mb-6 md:mb-8">
              <p className="text-sm sm:text-base md:text-lg mb-2 sm:mb-4 max-w-2xl mx-auto italic font-semibold text-muted font-inter">
                Top 100 starred library in finance and trading
              </p>
              <p className="text-muted max-w-3xl mx-auto font-inter text-xs sm:text-sm md:text-base">
                Libraries with the same number of stars get attributed the same rank.
              </p>
            </div>

            {/* Leaderboard */}
            <div className="flex justify-center">
              <LeaderboardTable
                title="Leaderboard"
                libraries={financeData.libraries}
              />
            </div>
          </FadeIn>
        </div>
      </div>
    </main>
  );
}
