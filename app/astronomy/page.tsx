import ChatContainer from "@/app/ui/chat-container";
import { loadAstronomyData } from "@/app/utils/domain-loader";
import FloatingMenu from "@/app/ui/floatingmenu";
import ThemeToggle from "@/app/ui/theme-toggle";

export default async function AstronomyPage() {
  const astronomyData = loadAstronomyData();

  return (
    <main className="min-h-screen bg-almond-beige flex flex-col">
      {/* Content */}
      <div className="mx-auto pt-4 pb-4 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-black dark:text-white">
        {/* Header */}
        <div className="flex items-center mb-6 pt-8">
          <div className="flex items-center gap-4 flex-1">
            <div className="text-4xl">🔭</div>
            <div>
              <h1 className="text-3xl font-heading">Astronomy & Cosmology</h1>
              <p className="text-gray-700 dark:text-gray-200 text-base font-inter">AI Assistant for celestial observations and cosmic analysis</p>
            </div>
          </div>
          <div className="flex gap-48">
            <FloatingMenu />
            <ThemeToggle />
          </div>
        </div>





        <div className="flex-1 mt-8">
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
      </div>
    </main>
  );
} 