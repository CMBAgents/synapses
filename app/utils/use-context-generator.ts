'use client';

import { useState } from 'react';

export function useContextGenerator() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState<string | null>(null);

  const generateContextForLibrary = async (domain: 'astronomy' | 'finance', libraryName: string) => {
    setIsGenerating(true);
    setGenerationStatus(`Generating context for ${libraryName}...`);
    
    try {
      const response = await fetch('/api/generate-context', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain, libraryName }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setGenerationStatus(`✅ Context generated for ${libraryName}`);
        return { success: true, data };
      } else {
        setGenerationStatus(`❌ Failed to generate context: ${data.error}`);
        return { success: false, error: data.error };
      }
    } catch (error) {
      setGenerationStatus(`❌ Error: ${error}`);
      return { success: false, error };
    } finally {
      setIsGenerating(false);
    }
  };

  const generateAllMissingContexts = async (domain: 'astronomy' | 'finance') => {
    setIsGenerating(true);
    setGenerationStatus(`Generating all missing contexts for ${domain}...`);
    
    try {
      const response = await fetch('/api/generate-all-contexts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        const { results } = data;
        setGenerationStatus(`✅ Generated ${results.generated} contexts for ${domain} (${results.failed} failed)`);
        return { success: true, data };
      } else {
        setGenerationStatus(`❌ Failed to generate contexts: ${data.error}`);
        return { success: false, error: data.error };
      }
    } catch (error) {
      setGenerationStatus(`❌ Error generating contexts: ${error}`);
      return { success: false, error };
    } finally {
      setIsGenerating(false);
    }
  };

  return {
    isGenerating,
    generationStatus,
    generateContextForLibrary,
    generateAllMissingContexts,
  };
} 