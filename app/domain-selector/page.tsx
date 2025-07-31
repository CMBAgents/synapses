'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAllDomains } from '../utils/domain-loader';
import styles from "../../styles/background.module.css";

export default function DomainSelector() {
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const router = useRouter();
  const domains = getAllDomains();

  const handleDomainSelect = (domainId: string) => {
    setSelectedDomain(domainId);
    setIsAnimating(true);
    setTimeout(() => {
      router.push(`/${domainId}`);
    }, 800);
  };

  return (
    <main className="bg-main">
      <div className="sober-overlay fixed inset-0 z-0"></div>
      {/* Content above overlay */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 text-main">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-heading mb-6 text-main">
            Choose Your Domain
          </h1>
          <p className="text-xl md:text-2xl text-muted max-w-3xl mx-auto">
            Select the domain you want to explore with our AI assistant
          </p>
        </div>

        {/* Domain Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl w-full">
          {domains.map((domain, index) => (
            <div
              key={domain.id}
              className={`
                relative group cursor-pointer transform transition-all duration-500 ease-out card-shadow
                bg-card border border-main
                ${isAnimating && selectedDomain === domain.id 
                  ? 'scale-110 rotate-3' 
                  : 'hover:scale-105 hover:-rotate-1'
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
              <div className="relative rounded-2xl p-8 transition-all duration-500">
                {/* Domain Icon */}
                <div className={`
                  text-6xl mb-6 transition-all duration-500
                  ${selectedDomain === domain.id 
                    ? 'scale-125' 
                    : 'group-hover:scale-110'
                  }
                `}>
                  {domain.icon}
                </div>

                {/* Domain Title */}
                <h2 className="text-2xl md:text-3xl font-heading mb-4 text-main">
                  {domain.name}
                </h2>

                {/* Domain Description */}
                <p className="text-muted text-lg leading-relaxed mb-6">
                  {domain.description}
                </p>

                {/* Selection Indicator */}
                <div className={`
                  absolute top-4 right-4 w-6 h-6 rounded-full border-2 transition-all duration-300
                  ${selectedDomain === domain.id 
                    ? 'border-blue-400 bg-blue-400' 
                    : 'border-main group-hover:border-blue-400/60'
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
            className="btn-accent px-6 py-3 text-lg font-semibold"
          >
            ← Back to Landing
          </button>
        </div>

        {/* Loading Animation */}
        {isAnimating && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-400 mx-auto mb-4"></div>
                              <p className="text-main text-xl font-heading">
                Loading {selectedDomain === 'astronomy' ? 'Astronomy' : 'Finance'} domain...
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
} 