"use client";

import FadeIn from "../ui/fadein";
import LeaderboardTable from "../ui/leaderboardtable";

import { astronomyLibs, financeLibs } from "../data/loadLibs";

export default function Page2() {
  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center bg-cover bg-center bg-no-repeat bg-fadein"
      style={{ backgroundImage: "url('image_page2.png')" }}
    >
      <div className="w-full max-w-6xl bg-white/80 dark:bg-gray-900/80 rounded-lg p-6 shadow-lg">
        <FadeIn>
          <div className="w-full max-w-3xl mb-8">
            <h1 className="text-3xl text-center font-bold text-gray-900 dark:text-gray-100 text-right mb-2">
              Python Libraries Leaderboard
            </h1>
            <p className="text-center text-lg mb-8 max-w-2xl text-gray-900 dark:text-gray-100 italic text-right font-semibold">
          Criteria for the leaderboard: Number of stars on GitHub, Key words : astronomy & cosmology for astronomy libraries, finance & trading for finance libraries.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-6">
            <LeaderboardTable
              title="Astronomy"
              libraries={astronomyLibs}
            />
            <LeaderboardTable
              title="Finance"
              libraries={financeLibs}
            />
          </div>
        </FadeIn>
      </div>
    </div>
  );
}
