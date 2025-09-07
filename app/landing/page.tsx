'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAllDomains } from '../utils/domain-loader';

export default function LandingPage() {
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const router = useRouter();
  const domains = getAllDomains();

  const handleDomainSelect = async (domainId: string) => {
    setSelectedDomain(domainId);
    setIsAnimating(true);
    
    // Navigate to domain leaderboard
    setTimeout(() => {
      router.push(`/leaderboard/${domainId}`);
    }, 800);
  };

  return (
    <main 
      className="min-h-screen bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('/earth.png')" }}
    >
      {/* Dark overlay */}
              <div className="absolute inset-0 bg-black opacity-60"></div>

      {/* Content above overlay */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 text-white page-fade-in">
        {/* Hero section */}
        <div className="text-center max-w-none mx-auto content-fade-in mb-8 sm:mb-12">
          <h1 className="text-4xl sm:text-6xl md:text-7xl lg:text-9xl font-bold mb-4 sm:mb-6 text-white font-jersey text-center uppercase">
            Synapses
          </h1>
          
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-jersey mb-6 sm:mb-8 md:mb-10 text-white">
            Choose Your Domain
          </h2>
        </div>

        {/* Domain Cards */}
        <div className="max-w-6xl w-full content-fade-in px-2">
          {/* Tous les domaines sur la même ligne */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 max-w-5xl mx-auto">
            {domains.map((domain, index) => {
              const isFinance = domain.id === 'finance';
              const isMachineLearning = domain.id === 'machinelearning';
              const isBiochemistry = domain.id === 'biochemistry';
              const isAstronomy = domain.id === 'astronomy';
              const isDisabled = false; // Tous les domaines sont maintenant activés
              
              return (
                <div
                  key={domain.id}
                  className={`relative group bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl transition-all duration-300 transform ${
                    isDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer hover:scale-105 hover:bg-white/20 hover:border-white/30 shadow-lg hover:shadow-xl'
                  } ${selectedDomain === domain.id ? 'bg-white/20 border-white/40' : ''} ${
                    isMachineLearning || isBiochemistry ? 'sm:col-span-2 lg:col-span-1' : ''
                  }`}
                  onClick={() => !isDisabled && handleDomainSelect(domain.id)}
                >
                  {/* Card Content */}
                  <div className="relative p-4 sm:p-6 md:p-8 flex items-center justify-center min-h-[100px] sm:min-h-[120px] md:min-h-[140px]">
                    <div className="text-center">
                      {/* Domain Title */}
                      <h3 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-jersey text-white">
                        {domain.name}
                      </h3>
                    </div>

                    {/* Selection Indicator */}
                    <div className="absolute top-2 sm:top-3 right-2 sm:right-3 w-4 sm:w-5 h-4 sm:h-5 rounded-full border-2 border-white/60">
                      {selectedDomain === domain.id && (
                        <div className="absolute inset-1 bg-white rounded-full"></div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Loading Animation */}
        {isAnimating && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="animate-spin rounded-full h-12 w-12 border-2 border-white/30 border-t-white"></div>
          </div>
        )}
      </div>

    </main>
  );
}