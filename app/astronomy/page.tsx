'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import ChatContainer from "@/app/ui/chat-container";
import { loadAstronomyData } from "@/app/utils/domain-loader";
import ContextUpdater from "@/app/ui/context-updater";

function AstronomyContent() {
  const astronomyData = loadAstronomyData();
  const searchParams = useSearchParams();
  const preselectedLibrary = searchParams.get('library') || undefined;

  return (
    <ContextUpdater domain="astronomy">
      <main 
        className="min-h-screen bg-cover bg-center bg-no-repeat flex flex-col relative"
        style={{ backgroundImage: "url('/earth.png')" }}
      >
        {/* Dark overlay for better text readability */}
        <div className="absolute inset-0 bg-black/40"></div>
        
        {/* Content */}
        <div className="relative z-10 mx-auto pt-4 pb-4 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 sm:mb-6 pt-4 sm:pt-6 md:pt-8">
          <a 
            href="/astronomy/leaderboard" 
            className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-2 sm:py-3 sm:px-3 md:px-4 lg:px-6 rounded-full text-xs sm:text-sm md:text-base lg:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
          >
            <span className="hidden sm:inline">Leaderboard</span>
            <span className="sm:hidden">List</span>
          </a>
          
          <div className="text-center flex-1 mx-2 sm:mx-4">
            <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-jersey text-white">
              <span className="hidden sm:inline">Astronomy & Cosmology</span>
              <span className="sm:hidden">Astronomy</span>
            </h1>
          </div>
          
          <a 
            href="/landing" 
            className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-2 px-3 sm:py-3 sm:px-4 md:px-6 rounded-full text-xs sm:text-sm md:text-base lg:text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
          >
            HOME
          </a>
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
            preselectedLibrary={preselectedLibrary}
          />
        </div>
      </div>
    </main>
    </ContextUpdater>
  );
}

export default function AstronomyPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AstronomyContent />
    </Suspense>
  );
} 