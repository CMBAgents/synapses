"use client";

import FadeIn from "../ui/fadein";
import LeaderboardTable from "../ui/leaderboardtable";

import { astronomyLibs, financeLibs } from "../data/loadLibs";

export default function Page2() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
      <FadeIn>
        <div className="w-full max-w-3xl mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 text-left mb-2">
            Python Libraries Leaderboard
          </h1>
          <p className="text-lg text-justify text-gray-700 dark:text-gray-300">
            A next-gen chatbot that speaks the language of the top 100 GitHub
            libraries in finance and astronomy. From portfolio optimization to cosmic
            microwave background analysis, it instantly bridges code and insight.
            No setup, just smart execution.
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-6">
          <LeaderboardTable
            title="Python Libraries Leaderboard - Astronomy"
            libraries={astronomyLibs}
          />
          <LeaderboardTable
            title="Python Libraries Leaderboard - Finance"
            libraries={financeLibs}
          />
        </div>
      </FadeIn>
    </div>
  );
}
