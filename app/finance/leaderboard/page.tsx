import FadeIn from "../../ui/fadein";
import LeaderboardTable from "../../ui/leaderboardtable";
import { loadFinanceData } from "../../utils/domain-loader";
import FloatingMenu from "../../ui/FloatingMenu";
import ThemeToggle from "../../ui/theme-toggle";
import styles from "../../styles/background.module.css";

export default function FinanceLeaderboard() {
  const financeData = loadFinanceData();

  return (
    <main className={styles.background}>
      <div className={styles.overlay}></div>
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-6xl bg-white/10 backdrop-blur-sm rounded-lg p-6 shadow-lg border border-white/20">
          <FadeIn>
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-4">
                <div className="text-4xl">📈</div>
                <div>
                  <h1 className="text-3xl font-heading text-white">Finance & Trading Libraries</h1>
                  <p className="text-white/80 font-inter">Top GitHub repositories for financial analysis</p>
                </div>
              </div>
              <div className="flex gap-48">
                <FloatingMenu />
                <ThemeToggle />
              </div>
            </div>

            {/* Description */}
            <div className="text-center mb-8">
              <p className="text-lg mb-4 max-w-2xl mx-auto italic font-semibold text-muted font-inter">
                Criteria: Number of stars on GitHub, Keywords: finance & trading
              </p>
              <p className="text-muted max-w-3xl mx-auto font-inter">
                {financeData.description}
              </p>
            </div>

            {/* Leaderboard */}
            <div className="flex justify-center">
              <LeaderboardTable
                title="Finance & Trading"
                libraries={financeData.libraries}
              />
            </div>
          </FadeIn>
        </div>
      </div>
    </main>
  );
} 