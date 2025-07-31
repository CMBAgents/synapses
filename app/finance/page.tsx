import ChatContainer from "@/app/ui/chat-container";
import { loadFinanceData } from "@/app/utils/domain-loader";
import styles from "../../styles/background.module.css";

export default async function FinancePage() {
  const financeData = loadFinanceData();

  return (
    <main className={styles.background}>
      <div className={styles.overlay}></div>
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      {/* Content above overlay */}
      <div className="relative z-10 mx-auto my-4 sm:my-8 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-main">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="text-4xl">📈</div>
            <div>
              <h1 className="text-3xl font-heading">Finance & Trading</h1>
              <p className="text-muted text-base">AI Assistant for portfolio optimization and algorithmic trading</p>
            </div>
          </div>
          <div className="flex gap-4">
            <a 
              href="/finance/leaderboard" 
              className="btn-accent px-4 py-2 text-sm"
            >
              View Leaderboard
            </a>
            <a 
              href="/domain-selector" 
              className="btn-accent px-4 py-2 text-sm"
            >
              ← Change Domain
            </a>
          </div>
        </div>

        {/* Description */}
        <p className="text-center text-lg mb-8 max-w-2xl mx-auto italic font-semibold text-muted">
          Master the <strong>top finance and trading libraries</strong> with our AI assistant. 
          From <strong>portfolio optimization</strong> to <em>algorithmic trading strategies</em>, 
          get instant insights and code execution for financial analysis.
        </p>

        {/* Domain Info */}
        <div className="bg-card rounded-lg p-6 mb-8 border border-main card-shadow">
          <h3 className="text-xl font-heading mb-3">Domain Overview</h3>
          <p className="text-muted mb-4">{financeData.description}</p>
          <div className="flex flex-wrap gap-2">
            {financeData.keywords.map((keyword, index) => (
              <span 
                key={index}
                className="bg-beige-light/30 text-beige-dark px-3 py-1 rounded-full text-sm border border-beige-dark/40"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>

        <ChatContainer
          programs={[{ 
            id: 'finance', 
            name: 'Finance & Trading', 
            description: financeData.description,
            contextFiles: [],
            docsUrl: '',
            extraSystemPrompt: `You are an AI assistant specialized in finance and trading. You have access to information about ${financeData.libraries.length} top finance libraries including: ${financeData.libraries.slice(0, 5).map(lib => lib.name).join(', ')} and more.`
          }]}
          defaultProgramId="finance"
        />
      </div>
    </main>
  );
} 