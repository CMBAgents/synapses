'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import ChatContainer from "@/app/ui/chat-container";
import { loadAstronomyData } from "@/app/utils/domain-loader";
import FloatingMenu from "@/app/ui/FloatingMenu";
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
        <div className="flex items-center mb-6 pt-8">
          <div className="flex items-center gap-4 flex-1">
            <div>
              <h1 className="text-5xl font-jersey text-white">Astronomy & Cosmology</h1>
            </div>
          </div>
          <div className="flex gap-48">
            <FloatingMenu />
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