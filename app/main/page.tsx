import ChatContainer from "@/app/ui/chat-container";
import { loadConfig, getDefaultProgram } from "@/app/utils/config";
import styles from "../../styles/background.module.css";

export default async function MainPage() {
  // Load configuration
  const config = loadConfig();
  const defaultProgram = getDefaultProgram();

  return (
    <main className={styles.background}>
      <div className={styles.overlay}></div>
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>

      {/* Content above overlay */}
      <div className="relative z-10 mx-auto my-4 sm:my-8 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-white">
        {/* Header with back button */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">
            CMBAgent Info
          </h1>
          <a 
            href="/landing" 
            className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
          >
            ← Back to Landing
          </a>
        </div>

        {/* Description */}
        <p className="text-center text-lg mb-8 max-w-2xl mx-auto italic font-semibold">
          A <strong>next-generation chatbot</strong> fluent in the language of the <strong>100 most-starred GitHub libraries</strong> in finance and astronomy. From <strong>portfolio optimization</strong> to <em>cosmic microwave background</em> analysis, it instantly bridges <strong>code and insight</strong> — no setup required, just <em>smart execution.</em>
        </p>

        <ChatContainer
          programs={config.programs}
          defaultProgramId={defaultProgram.id}
        />
      </div>
    </main>
  );
} 