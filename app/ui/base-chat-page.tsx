'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import ChatContainer from "./chat-container";
import { loadAstronomyData, loadFinanceData } from "../utils/domain-loader";
import ContextUpdater from "./context-updater";
import LibrarySelector from "./library-selector";

interface BaseChatPageProps {
  domain: 'astronomy' | 'finance';
}

function BaseChatContent({ domain }: BaseChatPageProps) {
  const getDomainData = () => {
    if (domain === 'astronomy') {
      return loadAstronomyData();
    } else if (domain === 'finance') {
      return loadFinanceData();
    }
    return loadAstronomyData(); // fallback
  };

  const getDomainTitle = () => {
    if (domain === 'astronomy') {
      return 'Astrophysics & Cosmology';
    } else if (domain === 'finance') {
      return 'Finance & Trading';
    }
    return 'Domain';
  };

  const getLeaderboardUrl = () => {
    return `/leaderboard/${domain}`;
  };

  const domainData = getDomainData();
  const searchParams = useSearchParams();
  const preselectedLibrary = searchParams.get('library') || undefined;

  return (
    <ContextUpdater domain={domain}>
      <main 
        className="min-h-screen bg-cover bg-center bg-no-repeat flex flex-col relative"
        style={{ backgroundImage: "url('/earth.png')" }}
      >
        {/* Dark overlay for better text readability */}
        <div className="absolute inset-0 bg-black/40"></div>
        
        {/* Content */}
        <div className="relative z-10 mx-auto pt-8 sm:pt-12 md:pt-16 pb-4 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-white">
          {/* Title with buttons - more spaced */}
          <div className="text-center mb-8 sm:mb-12">
            <div className="flex items-center justify-between mb-6">
              <a 
                href={getLeaderboardUrl()}
                className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-1 px-2 sm:py-2 sm:px-3 rounded-full text-xs sm:text-sm transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter"
              >
                <span className="hidden sm:inline">Leaderboard</span>
                <span className="sm:hidden">List</span>
              </a>
              
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-jersey text-white flex-1 mx-8">
                {getDomainTitle()}
              </h1>
              
              <a 
                href="/landing" 
                className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-1 px-2 sm:py-2 sm:px-3 rounded-full text-xs sm:text-sm transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter flex items-center"
              >
                <svg width="16" height="16" className="sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Selectors row - centered and aligned */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-4">
            {/* Model selector */}
            <div className="w-full sm:w-80">
              <ChatContainer
                programs={[{ 
                  id: domain, 
                  name: getDomainTitle(), 
                  description: domainData.description,
                  contextFiles: [],
                  docsUrl: '',
                  extraSystemPrompt: `You are an AI assistant specialized in ${domain === 'astronomy' ? 'astrophysics and cosmology' : 'finance and trading'}. You have access to information about ${domainData.libraries.length} top ${domain === 'astronomy' ? 'astrophysics' : 'finance'} libraries including: ${domainData.libraries.slice(0, 5).map(lib => lib.name).join(', ')} and more.`
                }]}
                defaultProgramId={domain}
                preselectedLibrary={preselectedLibrary}
                showModelSelectorOnly={true}
              />
            </div>

            {/* Library selector - more space */}
            <div className="w-full sm:w-96">
              <LibrarySelector 
                libraries={domainData.libraries}
                preselectedLibrary={preselectedLibrary}
                simplified={true}
              />
            </div>
          </div>

          {/* Chat area - full width below selectors with fixed height */}
          <div className="w-full h-[calc(100vh-300px)] min-h-[500px]">
            <ChatContainer
              programs={[{ 
                id: domain, 
                name: getDomainTitle(), 
                description: domainData.description,
                contextFiles: [],
                docsUrl: '',
                extraSystemPrompt: `You are an AI assistant specialized in ${domain === 'astronomy' ? 'astrophysics and cosmology' : 'finance and trading'}. You have access to information about ${domainData.libraries.length} top ${domain === 'astronomy' ? 'astrophysics' : 'finance'} libraries including: ${domainData.libraries.slice(0, 5).map(lib => lib.name).join(', ')} and more.`
              }]}
              defaultProgramId={domain}
              preselectedLibrary={preselectedLibrary}
              showModelSelectorOnly={false}
            />
          </div>
        </div>
      </main>
    </ContextUpdater>
  );
}

export default function BaseChatPage({ domain }: BaseChatPageProps) {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <BaseChatContent domain={domain} />
    </Suspense>
  );
}
