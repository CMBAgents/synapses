'use client';

import { useState, useEffect, useRef } from 'react';
import { LibraryEntry } from '../utils/domain-loader';

interface LibrarySelectorProps {
  libraries: LibraryEntry[];
  onLibrarySelect?: (library: LibraryEntry | null) => void;
  preselectedLibrary?: string;
  className?: string;
}

export default function LibrarySelector({ 
  libraries, 
  onLibrarySelect, 
  preselectedLibrary,
  className = ""
}: LibrarySelectorProps) {
  const [libraryInput, setLibraryInput] = useState(preselectedLibrary || "");
  const [selectedLibrary, setSelectedLibrary] = useState<string>(preselectedLibrary || "");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fonction de similarité simple
  const calculateSimilarity = (str1: string, str2: string): number => {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const editDistance = levenshteinDistance(longer.toLowerCase(), shorter.toLowerCase());
    return (longer.length - editDistance) / longer.length;
  };

  const levenshteinDistance = (str1: string, str2: string): number => {
    const matrix: number[][] = [];
    
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    
    return matrix[str2.length][str1.length];
  };

  // Trouver la meilleure correspondance
  const findBestMatch = (input: string) => {
    if (!input.trim()) return null;
    
    const searchLower = input.toLowerCase();
    const matches = libraries
      .map(library => ({
        library,
        similarity: calculateSimilarity(input, library.name)
      }))
      .filter(match => 
        match.library.name.toLowerCase().includes(searchLower) || 
        match.similarity > 0.6
      )
      .sort((a, b) => {
        const aStartsWith = a.library.name.toLowerCase().startsWith(searchLower);
        const bStartsWith = b.library.name.toLowerCase().startsWith(searchLower);
        
        if (aStartsWith && !bStartsWith) return -1;
        if (!aStartsWith && bStartsWith) return 1;
        
        return b.similarity - a.similarity;
      });
    
    return matches.length > 0 ? matches[0] : null;
  };

  // Obtenir les suggestions
  const getSuggestions = (input: string) => {
    if (!input.trim()) return [];
    
    const searchLower = input.toLowerCase();
    return libraries
      .map(library => ({
        ...library,
        similarity: calculateSimilarity(input, library.name)
      }))
      .filter(library => 
        library.name.toLowerCase().includes(searchLower) || 
        library.similarity > 0.6
      )
      .sort((a, b) => {
        const aStartsWith = a.name.toLowerCase().startsWith(searchLower);
        const bStartsWith = b.name.toLowerCase().startsWith(searchLower);
        
        if (aStartsWith && !bStartsWith) return -1;
        if (!aStartsWith && bStartsWith) return 1;
        
        return b.similarity - a.similarity;
      })
      .slice(0, 8);
  };

  // Gérer la sélection de librairie
  const handleLibrarySelect = (library: LibraryEntry) => {
    setLibraryInput(library.name);
    setSelectedLibrary(library.name);
    setShowSuggestions(false);
    onLibrarySelect?.(library);
  };

  // Effet pour mettre à jour la sélection quand preselectedLibrary change
  useEffect(() => {
    if (preselectedLibrary) {
      setLibraryInput(preselectedLibrary);
      setSelectedLibrary(preselectedLibrary);
    }
  }, [preselectedLibrary]);

  const matchedLibrary = libraries.find(lib => lib.name === selectedLibrary);
  const isRecognized = !!matchedLibrary;

  return (
    <div className={`relative ${className}`}>
      <div className="flex items-center justify-center space-x-4">
        {/* Input de sélection */}
        <div className="w-64 relative">
          <input
            ref={inputRef}
            id="library-input"
            type="text"
            value={libraryInput}
            onChange={(e) => {
              const value = e.target.value;
              setLibraryInput(value);
              setShowSuggestions(value.length > 0);
              
              const match = findBestMatch(value);
              setSelectedLibrary(match ? match.library.name : value);
              onLibrarySelect?.(match ? match.library : null);
            }}
            onFocus={() => setShowSuggestions(libraryInput.length > 0)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Type library name..."
            className="w-full px-3 py-2 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-white/50 transition-all duration-200 text-sm"
          />
          
          {/* Suggestions dropdown - en bas */}
          {showSuggestions && (
            <div className="absolute top-full mt-1 w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto">
              {getSuggestions(libraryInput).map((suggestion, index) => (
                <div
                  key={suggestion.name}
                  onClick={() => handleLibrarySelect(suggestion)}
                  className={`px-4 py-3 cursor-pointer transition-all duration-150 text-white/90 hover:bg-white/15 ${
                    index === 0 ? 'rounded-t-lg' : ''
                  } ${index === getSuggestions(libraryInput).length - 1 ? 'rounded-b-lg' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="font-medium">{suggestion.name}</div>
                    {suggestion.similarity && suggestion.similarity < 1 && (
                      <div className="text-xs text-white/60 bg-white/10 px-2 py-1 rounded">
                        {Math.round(suggestion.similarity * 100)}% match
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {getSuggestions(libraryInput).length === 0 && (
                <div className="px-4 py-3 text-white/70 text-center">
                  No matching libraries found
                </div>
              )}
            </div>
          )}
        </div>

        {/* Affichage des informations de la librairie sélectionnée - à droite */}
        <div className="bg-gradient-to-r from-white/25 to-white/15 backdrop-blur-sm rounded-xl p-4 border border-white/30 shadow-inner min-w-[250px] min-h-[120px]">
          {selectedLibrary ? (
            <>
              <div className="flex items-center mb-3">
                <div className={`w-2 h-2 rounded-full mr-2 ${isRecognized ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
                <div className="font-semibold text-white text-sm">
                  {selectedLibrary}
                </div>
              </div>
              
              {isRecognized ? (
                <>
                  {/* GitHub Link */}
                  <div className="flex items-center mb-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                    <a 
                      href={matchedLibrary.github_url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:text-blue-300 transition-colors cursor-pointer flex items-center"
                    >
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                      </svg>
                      GitHub
                    </a>
                  </div>
                  
                  {/* Context File Link */}
                  {matchedLibrary.hasContextFile ? (
                    <div className="flex items-center mb-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      <a 
                        href={`/api/context/${matchedLibrary.contextFileName}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-green-400 hover:text-green-300 transition-colors cursor-pointer flex items-center"
                      >
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                          <path d="M14 2v6h6"/>
                          <path d="M16 13H8"/>
                          <path d="M16 17H8"/>
                          <path d="M10 9H8"/>
                        </svg>
                        View Context
                      </a>
                    </div>
                  ) : (
                    <div className="flex items-center mb-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                      <span className="text-xs text-gray-400">No context documentation available</span>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex items-center mb-2">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></div>
                  <span className="text-xs text-yellow-400">
                    Library not recognized - no documentation available
                  </span>
                </div>
              )}
              
              {/* Description */}
              {matchedLibrary?.description && (
                <p className="text-xs text-gray-300 leading-relaxed mt-2">
                  {matchedLibrary.description}
                </p>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <span className="text-xs text-white/50">Select a library to see details</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
