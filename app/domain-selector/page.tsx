'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAllDomains } from '../utils/domain-loader';
import styles from "../styles/background.module.css";

export default function DomainSelector() {
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const router = useRouter();
  const domains = getAllDomains();

  const handleDomainSelect = async (domainId: string) => {
    setSelectedDomain(domainId);
    setIsAnimating(true);
    
    // Navigate immediately - context update will happen on page load
    setTimeout(() => {
      router.push(`/${domainId}`);
    }, 800);
  };

  return (
    <main 
      className="min-h-screen bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('/pexels-jean-luc-benazet-753072919-19025281.jpg')" }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>
      {/* Content above overlay */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 text-white page-fade-in">
        {/* Header */}
        <div className="text-center mb-12 content-fade-in">
          <h1 className="text-5xl md:text-7xl font-jersey mb-6 text-white">
            Choose Your Domain
          </h1>
          <p className="text-xl md:text-2xl text-white max-w-3xl mx-auto font-inter">
            Select the domain you want to explore with our AI assistant
          </p>
        </div>

        {/* Domain Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl w-full content-fade-in">
          {domains.map((domain, index) => (
            <div
              key={domain.id}
              className={`
                relative group cursor-pointer transform transition-all duration-500 ease-out
                bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl
                ${isAnimating && selectedDomain === domain.id 
                  ? 'scale-110 rotate-3' 
                  : ''
                }
                ${isAnimating && selectedDomain !== domain.id 
                  ? 'scale-95 opacity-50' 
                  : ''
                }
              `}
              style={{
                animationDelay: `${index * 200}ms`
              }}
              onClick={() => handleDomainSelect(domain.id)}
            >
              {/* Card Content */}
              <div className="relative p-8 transition-all duration-500">
                {/* Domain Icon */}
                <div className={`
                  text-6xl mb-6 transition-all duration-500
                  ${selectedDomain === domain.id 
                    ? 'scale-125' 
                    : ''
                  }
                `}>
                  {/* Icon removed */}
                </div>

                {/* Domain Title */}
                <h2 className="text-2xl md:text-3xl font-heading mb-4 text-white">
                  {domain.name}
                </h2>

                {/* Domain Description */}
                <p className="text-white text-lg leading-relaxed mb-6 font-inter">
                  {domain.description}
                </p>

                {/* Selection Indicator */}
                <div className={`
                  absolute top-4 right-4 w-6 h-6 rounded-full border-2 transition-all duration-300
                  ${selectedDomain === domain.id 
                    ? 'border-black bg-black' 
                    : 'border-white/60 group-hover:border-black/60'
                  }
                `}>
                  {selectedDomain === domain.id && (
                    <div className="absolute inset-1 bg-white rounded-full animate-pulse"></div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Back Button */}
        <div className="mt-12">
          <button
            onClick={() => router.push('/landing')}
            className="bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-4 px-8 rounded-full text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl font-inter nav-transition"
          >
            ← Back to Landing
          </button>
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