'use client';

import { useState, useEffect, useMemo } from 'react';
import { LibraryEntry } from '../utils/domain-loader';

interface LibrarySearchProps {
  libraries: LibraryEntry[];
  onLibrarySelect: (library: LibraryEntry) => void;
  placeholder?: string;
}

export default function LibrarySearch({ libraries, onLibrarySelect, placeholder = "Search libraries..." }: LibrarySearchProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  // Fonction de similarité simple (distance de Levenshtein simplifiée)
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

  // Filtrer et trier les librairies par pertinence
  const filteredLibraries = useMemo(() => {
    if (!searchTerm.trim()) return [];
    
    const searchLower = searchTerm.toLowerCase();
    
    return libraries
      .map(library => ({
        ...library,
        similarity: calculateSimilarity(searchTerm, library.name)
      }))
      .filter(library => 
        library.name.toLowerCase().includes(searchLower) || 
        library.similarity > 0.6 // Seuil de similarité
      )
      .sort((a, b) => {
        // Priorité aux correspondances exactes au début
        const aStartsWith = a.name.toLowerCase().startsWith(searchLower);
        const bStartsWith = b.name.toLowerCase().startsWith(searchLower);
        
        if (aStartsWith && !bStartsWith) return -1;
        if (!aStartsWith && bStartsWith) return 1;
        
        // Puis par similarité
        return b.similarity - a.similarity;
      })
      .slice(0, 8); // Limiter à 8 résultats
  }, [searchTerm, libraries]);

  // Gestion des touches clavier
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || filteredLibraries.length === 0) return;
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < filteredLibraries.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : filteredLibraries.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredLibraries.length) {
          handleLibrarySelect(filteredLibraries[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleLibrarySelect = (library: LibraryEntry) => {
    onLibrarySelect(library);
    setSearchTerm(library.name);
    setIsOpen(false);
    setSelectedIndex(-1);
  };

  // Effet pour ouvrir/fermer la liste
  useEffect(() => {
    setIsOpen(searchTerm.length > 0 && filteredLibraries.length > 0);
    setSelectedIndex(-1);
  }, [searchTerm, filteredLibraries]);

  return (
    <div className="relative w-full max-w-md">
      {/* Input de recherche */}
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="w-full px-4 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-lg text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-white/50 transition-all duration-200"
      />
      
      {/* Liste des suggestions */}
      {isOpen && (
        <div className="absolute top-full mt-1 w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
          {filteredLibraries.map((library, index) => (
            <div
              key={library.name}
              onClick={() => handleLibrarySelect(library)}
              className={`px-4 py-3 cursor-pointer transition-all duration-150 ${
                index === selectedIndex
                  ? 'bg-white/20 text-white'
                  : 'text-white/90 hover:bg-white/15'
              } ${index === 0 ? 'rounded-t-lg' : ''} ${
                index === filteredLibraries.length - 1 ? 'rounded-b-lg' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{library.name}</div>
                  <div className="text-sm text-white/70">
                    ⭐ {library.stars.toLocaleString()} stars
                  </div>
                </div>
                {library.similarity && library.similarity < 1 && (
                  <div className="text-xs text-white/60 bg-white/10 px-2 py-1 rounded">
                    {Math.round(library.similarity * 100)}% match
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Message quand aucun résultat */}
      {searchTerm.length > 0 && filteredLibraries.length === 0 && (
        <div className="absolute top-full mt-1 w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg shadow-lg z-50 px-4 py-3 text-white/70 text-center">
          No libraries found for "{searchTerm}"
        </div>
      )}
    </div>
  );
}
