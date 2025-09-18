'use client';

import { useState, useEffect } from 'react';

interface CreditsProps {
  className?: string;
  variant?: 'default' | 'minimal' | 'inline';
}

export default function Credits({ className = '', variant = 'default' }: CreditsProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Show credits after a short delay
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (variant === 'inline') {
    return (
      <div className={`text-xs text-gray-500 ${className}`}>
        <div className="flex flex-col items-center space-y-1">
          <div>
            <span>Created by </span>
            <a 
              href="https://github.com/polariscongroo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-blue-400 transition-colors duration-200"
            >
              Chadi Ait Ekioui
            </a>
          </div>
          <div>
            <span>Powered by </span>
            <a 
              href="https://github.com/CMBAgents" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-blue-400 transition-colors duration-200"
            >
              CMBAgents
            </a>
            <span> • </span>
            <a 
              href="https://discord.gg/pAbnFJrkgZ" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-purple-400 transition-colors duration-200"
            >
              Discord
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'minimal') {
    return (
      <div 
        className={`fixed bottom-2 right-2 z-50 transition-all duration-500 ${
          isVisible ? 'opacity-60 hover:opacity-100' : 'opacity-0'
        } ${className}`}
      >
        <div className="text-xs text-white/60 hover:text-white/90 transition-colors duration-200">
          <div>
            <a 
              href="https://github.com/polariscongroo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-white/90 transition-colors duration-200"
            >
              by Chadi Ait Ekioui
            </a>
          </div>
          <div className="text-xs">
            <a 
              href="https://github.com/CMBAgents" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-white/90 transition-colors duration-200"
            >
              CMBAgents
            </a>
            <span> • </span>
            <a 
              href="https://discord.gg/pAbnFJrkgZ" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-purple-300 transition-colors duration-200"
            >
              Discord
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`fixed bottom-4 right-4 z-50 transition-all duration-500 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      } ${className}`}
    >
      <div className="bg-black/80 backdrop-blur-sm border border-white/20 rounded-lg px-3 py-2 text-white text-sm">
        <div className="flex flex-col space-y-1">
          <div className="flex items-center space-x-2">
            <span className="text-white/80">Created by</span>
            <a 
              href="https://github.com/polariscongroo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-white hover:text-blue-300 transition-colors duration-200 font-medium"
            >
              Chadi Ait Ekioui
            </a>
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-white/60">Powered by</span>
            <a 
              href="https://github.com/CMBAgents" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-white/80 hover:text-blue-300 transition-colors duration-200"
            >
              CMBAgents
            </a>
            <span className="text-white/60">•</span>
            <a 
              href="https://discord.gg/pAbnFJrkgZ" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-white/80 hover:text-purple-300 transition-colors duration-200"
            >
              Discord
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
