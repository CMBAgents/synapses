"use client";

import FadeIn from "../ui/fadein";
import LeaderboardTable from "../ui/leaderboardtable";

import { loadAstronomyData, loadFinanceData } from "../utils/domain-loader";

export default function Page2() {
  const astronomyData = loadAstronomyData();
  const financeData = loadFinanceData();

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center bg-cover bg-center bg-no-repeat bg-fadein"
      style={{ backgroundImage: "url('image_page2.png')" }}
    >
      <div className="relative z-10 w-full max-w-6xl bg-white/80 dark:bg-gray-900/80 rounded-lg p-6 shadow-lg">
        <FadeIn>
          <div className="w-full max-w-3xl mb-8">
            <h1 className="text-3xl text-center font-bold text-gray-900 dark:text-gray-100 text-right mb-2">
              Python Libraries Leaderboard
            </h1>
            <p className="text-center text-lg mb-8 max-w-2xl text-gray-900 dark:text-gray-100 italic text-right font-semibold">
          Criteria for the leaderboard: Number of stars on GitHub, Key words : astrophysics & cosmology for astrophysics libraries, finance & trading for finance libraries.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-6">
            <LeaderboardTable
              title="Astrophysics"
              libraries={astronomyData.libraries}
            />
            <LeaderboardTable
              title="Finance"
              libraries={financeData.libraries}
            />
          </div>
        </FadeIn>
      </div>
    </div>
  );
}
