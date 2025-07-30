import ChatContainer from "@/app/ui/chat-container";
import { loadConfig, getDefaultProgram } from "@/app/utils/config";

export default async function Home() {
  // Load configuration
  const config = loadConfig();
  const defaultProgram = getDefaultProgram();

  return (
    <main className="min-h-screen bg-white dark:bg-gray-900">
      <div className="mx-auto my-4 sm:my-8 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl">
        {/* Titre centré */}
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4 text-center">
          CMBAgent Info
        </h1>

        {/* Texte descriptif centré, italique avec gras, largeur plus large */}
        <p className="text-center text-lg text-gray-700 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
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