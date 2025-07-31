import ChatContainer from "@/app/ui/chat-container";
import { loadAstronomyData } from "@/app/utils/domain-loader";
import styles from "../../styles/background.module.css";

export default async function AstronomyPage() {
  const astronomyData = loadAstronomyData();

  return (
    <main 
      className="min-h-screen bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('/pexels-slendyalex-3745234.jpg')" }}
    >
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      {/* Content above overlay */}
      <div className="relative z-10 mx-auto my-4 sm:my-8 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-main">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="text-4xl">🔭</div>
            <div>
              <h1 className="text-3xl font-heading">Astronomy & Cosmology</h1>
              <p className="text-muted text-base">AI Assistant for celestial observations and cosmic analysis</p>
            </div>
          </div>
          <div className="flex gap-4">
            <a 
              href="/astronomy/leaderboard" 
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
          Explore the <strong>top astronomy and cosmology libraries</strong> with our AI assistant. 
          From <strong>gravitational wave detection</strong> to <em>cosmic microwave background</em> analysis, 
          get instant insights and code execution for celestial research.
        </p>

        {/* Domain Info */}
        <div className="bg-card rounded-lg p-6 mb-8 border border-main card-shadow">
          <h3 className="text-xl font-heading mb-3">Domain Overview</h3>
          <p className="text-muted mb-4">{astronomyData.description}</p>
          <div className="flex flex-wrap gap-2">
            {astronomyData.keywords.map((keyword, index) => (
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
            id: 'astronomy', 
            name: 'Astronomy & Cosmology', 
            description: astronomyData.description,
            contextFiles: [],
            docsUrl: '',
            extraSystemPrompt: `You are an AI assistant specialized in astronomy and cosmology. You have access to information about ${astronomyData.libraries.length} top astronomy libraries including: ${astronomyData.libraries.slice(0, 5).map(lib => lib.name).join(', ')} and more.`
          }]}
          defaultProgramId="astronomy"
        />
      </div>
    </main>
  );
} 