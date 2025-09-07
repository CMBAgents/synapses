'use client';

import { Suspense, useState, useEffect } from 'react';
import { useSearchParams, useParams } from 'next/navigation';
import ChatContainer from "./chat-container";
import { loadAstronomyData, loadFinanceData, loadBiochemistryData, loadMachineLearningData } from "../utils/domain-loader";
import ContextUpdater from "./context-updater";
import LibrarySelector from "./library-selector";
import { useProgramContext } from "../contexts/ProgramContext";
import { getDomainDisplayName, getDomainDescription } from "../config/domains";


interface BaseChatPageProps {
  domain: 'astronomy' | 'finance' | 'biochemistry' | 'machinelearning';
}

function BaseChatContent({ domain }: BaseChatPageProps) {
  const { activeProgramId, setActiveProgramId, selectedLibrary, setSelectedLibrary } = useProgramContext();
  const searchParams = useSearchParams();
  const params = useParams();
  const preselectedLibrary = searchParams.get('library') || undefined;

  // Get programId from URL params if available
  const urlProgramId = params.programId as string;

  const getDomainData = () => {
    if (domain === 'astronomy') {
      return loadAstronomyData();
    } else if (domain === 'finance') {
      return loadFinanceData();
    } else if (domain === 'biochemistry') {
      return loadBiochemistryData();
    } else if (domain === 'machinelearning') {
      return loadMachineLearningData();
    }
    return loadAstronomyData(); // fallback
  };

  const getDomainTitle = () => {
    return getDomainDisplayName(domain);
  };

  const getLeaderboardUrl = () => {
    return `/leaderboard/${domain}`;
  };

  // Function to get default program ID for the domain
  const getDefaultProgramIdForDomain = () => {
    if (domain === 'astronomy') {
      return 'skyfielders-python-skyfield';
    } else if (domain === 'finance') {
      return 'quantopian-zipline';
    } else if (domain === 'biochemistry') {
      return 'biopython-biopython';
    } else if (domain === 'machinelearning') {
      return 'pytorch-pytorch';
    }
    return 'skyfielders-python-skyfield'; // fallback
  };

  // Function to map library name to program ID
  const getProgramIdFromLibraryName = (libraryName: string): string => {
    // Convert library name format to program ID format
    // e.g., "skyfielders/python-skyfield" -> "skyfielders-python-skyfield"
    return libraryName.replace(/\//g, '-');
  };

  // Initialize activeProgramId based on priority:
  // 1. URL programId (highest priority)
  // 2. Preselected library from URL params
  // 3. Use a real existing program as fallback
  useEffect(() => {
    let programId = '';
    
    if (urlProgramId) {
      // Highest priority: programId from URL
      programId = urlProgramId;
    } else if (preselectedLibrary) {
      // Second priority: preselected library from URL params
      programId = getProgramIdFromLibraryName(preselectedLibrary);
    } else {
      // Fallback: use the first available program from the domain
      const domainData = getDomainData();
      if (domainData.libraries.length > 0) {
        // Use the first library as fallback
        programId = getProgramIdFromLibraryName(domainData.libraries[0].name);
      }
    }
    
    setActiveProgramId(programId);
  }, [urlProgramId, preselectedLibrary, domain, setActiveProgramId]);

  // Handle library selection
  const handleLibrarySelect = (library: any) => {
    setSelectedLibrary(library);
    if (library && library.name) {
      const programId = getProgramIdFromLibraryName(library.name);
      setActiveProgramId(programId);
    } else {
      // Fallback: use the first available program from the domain
      const domainData = getDomainData();
      if (domainData.libraries.length > 0) {
        const fallbackProgramId = getProgramIdFromLibraryName(domainData.libraries[0].name);
        setActiveProgramId(fallbackProgramId);
      } else {
        setActiveProgramId('');
      }
    }
  };

  const domainData = getDomainData();

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
                  id: activeProgramId || getDefaultProgramIdForDomain(), 
                  name: selectedLibrary ? selectedLibrary.name : getDomainTitle(), 
                  description: selectedLibrary ? `Expert on ${selectedLibrary.name}` : domainData.description,
                  contextFiles: [],
                  docsUrl: selectedLibrary ? selectedLibrary.github_url : '',
                  extraSystemPrompt: selectedLibrary ? `You are an expert on ${selectedLibrary.name}. Use the provided documentation to help users with this library.` : `You are an AI assistant specialized in ${domain === 'astronomy' ? 'astrophysics and cosmology' : domain === 'finance' ? 'finance and trading' : domain === 'biochemistry' ? 'biochemistry and bioinformatics' : 'machine learning and artificial intelligence'}. You have access to information about ${domainData.libraries.length} top ${domain === 'astronomy' ? 'astrophysics' : domain === 'finance' ? 'finance' : domain === 'biochemistry' ? 'biochemistry' : 'machine learning'} libraries including: ${domainData.libraries.slice(0, 5).map(lib => lib.name).join(', ')} and more.`
                }]}
                defaultProgramId={activeProgramId || getDefaultProgramIdForDomain()}
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
                onLibrarySelect={handleLibrarySelect}
              />
            </div>
          </div>

          {/* Chat area - full width below selectors with fixed height */}
          <div className="w-full h-[calc(100vh-300px)] min-h-[500px]">
            <ChatContainer
              programs={[{ 
                id: activeProgramId || getDefaultProgramIdForDomain(), 
                name: selectedLibrary ? selectedLibrary.name : getDomainTitle(), 
                description: selectedLibrary ? `Expert on ${selectedLibrary.name}` : domainData.description,
                contextFiles: [],
                docsUrl: selectedLibrary ? selectedLibrary.github_url : '',
                extraSystemPrompt: selectedLibrary ? `You are an expert on ${selectedLibrary.name}. Use the provided documentation to help users with this library.` : `You are an AI assistant specialized in ${domain === 'astronomy' ? 'astrophysics and cosmology' : domain === 'finance' ? 'finance and trading' : domain === 'biochemistry' ? 'biochemistry and bioinformatics' : 'machine learning and artificial intelligence'}. You have access to information about ${domainData.libraries.length} top ${domain === 'astronomy' ? 'astrophysics' : domain === 'finance' ? 'finance' : domain === 'biochemistry' ? 'biochemistry' : 'machine learning'} libraries including: ${domainData.libraries.slice(0, 5).map(lib => lib.name).join(', ')} and more.`
              }]}
              defaultProgramId={activeProgramId || getDefaultProgramIdForDomain()}
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
