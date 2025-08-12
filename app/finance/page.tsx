'use client';

import ChatContainer from "@/app/ui/chat-container";
import { loadFinanceData } from "@/app/utils/domain-loader";
import LibrarySearch from "@/app/ui/library-search";
import ContextUpdater from "@/app/ui/context-updater";

export default function FinancePage() {
  const financeData = loadFinanceData();

  return (
    <ContextUpdater domain="finance">
      <main className="min-h-screen bg-almond-beige flex flex-col">
        {/* Content */}
        <div className="mx-auto pt-4 pb-4 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-black dark:text-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 sm:mb-6 pt-4 sm:pt-6 md:pt-8">
          <a 
            href="/finance/leaderboard" 
            className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-2 sm:py-3 sm:px-3 md:px-4 lg:px-6 rounded-full text-xs sm:text-sm md:text-base lg:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
          >
            <span className="hidden sm:inline">Leaderboard</span>
            <span className="sm:hidden">List</span>
          </a>
          
          <div className="text-center flex-1 mx-2 sm:mx-4">
            <h1 className="text-xl sm:text-2xl md:text-3xl font-heading">
              <span className="hidden sm:inline">Finance & Trading</span>
              <span className="sm:hidden">Finance</span>
            </h1>
            <p className="text-gray-700 dark:text-gray-200 text-xs sm:text-sm md:text-base font-inter hidden sm:block">AI Assistant for portfolio optimization and algorithmic trading</p>
            <p className="text-gray-700 dark:text-gray-200 text-xs font-inter sm:hidden">AI Trading Assistant</p>
          </div>
          
          <a 
            href="/landing" 
            className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-3 sm:py-3 sm:px-4 md:px-6 rounded-full text-xs sm:text-sm md:text-base lg:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
          >
            HOME
          </a>
        </div>



        {/* Library Search */}
        <div className="mb-8">
          <LibrarySearch
            libraries={financeData.libraries}
            onLibrarySelect={(library) => {
              // Ouvrir le lien GitHub de la librairie sélectionnée
              window.open(library.github_url, '_blank');
            }}
            placeholder="Search finance libraries..."
          />
        </div>

        <div className="flex-1 mt-8">
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
      </div>
    </main>
    </ContextUpdater>
  );
} 