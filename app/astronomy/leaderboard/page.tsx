import FadeIn from "../../ui/fadein";
import LeaderboardTable from "../../ui/leaderboardtable";
import { loadAstronomyData } from "../../utils/domain-loader";
import styles from "../../../styles/background.module.css";

export default function AstronomyLeaderboard() {
  const astronomyData = loadAstronomyData();

  return (
    <main 
      className="min-h-screen bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('/pexels-slendyalex-3745234.jpg')" }}
    >
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-6xl bg-card rounded-lg p-6 shadow-lg border border-main card-shadow">
          <FadeIn>
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-4">
                <div className="text-4xl">🔭</div>
                <div>
                  <h1 className="text-3xl font-heading text-main">Astronomy & Cosmology Libraries</h1>
                  <p className="text-muted">Top GitHub repositories for celestial research</p>
                </div>
              </div>
              <div className="flex gap-4">
                <a 
                  href="/astronomy" 
                  className="btn-accent px-4 py-2 text-sm"
                >
                  ← Back to Chat
                </a>
                <a 
                  href="/domain-selector" 
                  className="btn-accent px-4 py-2 text-sm"
                >
                  Change Domain
                </a>
              </div>
            </div>

            {/* Description */}
            <div className="text-center mb-8">
              <p className="text-lg mb-4 max-w-2xl mx-auto italic font-semibold text-muted">
                Criteria: Number of stars on GitHub, Keywords: astronomy & cosmology
              </p>
              <p className="text-muted max-w-3xl mx-auto">
                {astronomyData.description}
              </p>
            </div>

            {/* Leaderboard */}
            <div className="flex justify-center">
              <LeaderboardTable
                title="Astronomy & Cosmology"
                libraries={astronomyData.libraries}
              />
            </div>
          </FadeIn>
        </div>
      </div>
    </main>
  );
} 