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
      <div className="w-full max-w-4xl bg-white/80 dark:bg-gray-900/80 rounded-lg p-6 shadow-lg">
        <FadeIn>
          <div className="w-full max-w-3xl mb-8">
            <h1 className="text-3xl text-center font-bold text-gray-900 dark:text-gray-100 text-left mb-2">
              Python Libraries Leaderboard
            </h1>
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
