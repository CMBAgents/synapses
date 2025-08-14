import FadeIn from "../../ui/fadein";
import LeaderboardTable from "../../ui/leaderboardtable";
import { loadFinanceData } from "../../utils/domain-loader";

import styles from "../../styles/background.module.css";

export default function FinanceLeaderboard() {
  const financeData = loadFinanceData();

  return (
    <main 
      className="h-screen bg-cover bg-center bg-no-repeat relative overflow-hidden"
      style={{ backgroundImage: "url('/pexels-slendyalex-3745234.jpg')" }}
    >
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      <div className="relative z-10 h-screen flex flex-col items-center justify-start px-2 sm:px-4 pt-8 sm:pt-12 md:pt-16">
        {/* Title outside the frame */}
        <div className="text-center mb-6 sm:mb-8 md:mb-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-jersey text-white">
            Finance & Trading
          </h1>
        </div>

        {/* Translucent frame starts here */}
        <div className="w-full max-w-6xl bg-white/10 backdrop-blur-sm rounded-lg p-3 sm:p-4 md:p-6 shadow-lg border border-white/20 flex-1 flex flex-col">
          <FadeIn>
            {/* Header with description */}
            <div className="flex items-center justify-between mb-4">
              <a 
                href="/chat/finance" 
                className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-3 sm:py-3 sm:px-4 md:px-6 rounded-full text-sm sm:text-base md:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
              >
                Chat
              </a>
              
              <div className="text-center flex-1 mx-2 sm:mx-4">
                <p className="text-sm sm:text-base md:text-lg italic font-semibold text-white font-inter">
                  Top 100 starred library in finance and trading
                </p>
                <p className="text-white/70 max-w-3xl mx-auto font-inter text-xs sm:text-sm md:text-base">
                  Libraries with the same number of stars get attributed the same rank.
                </p>
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

            {/* Leaderboard */}
            <div className="flex-1 flex flex-col">
              <h2 className="text-lg sm:text-xl font-inter text-white text-center mb-2">
                Leaderboard
              </h2>
              <div className="flex-1 flex justify-center">
                <LeaderboardTable
                  title=""
                  libraries={financeData.libraries}
                />
              </div>
            </div>
          </FadeIn>
        </div>
      </div>
    </main>
  );
}
