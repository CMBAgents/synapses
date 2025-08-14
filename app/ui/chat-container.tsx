'use client'

import { useState, useEffect } from 'react';
import ProgramTabs from './program-tabs';
import ChatSimple from './chat-simple';
import ModelSelector from './model-selector';
import ThemeWrapper from './theme-wrapper';
import { Program } from '@/app/utils/types';
import { loadConfig } from '@/app/utils/config';
import { preloadContext } from '@/app/utils/context';
import { loadAstronomyData, loadFinanceData } from '@/app/utils/domain-loader';

interface ChatContainerProps {
  programs: Program[];
  defaultProgramId: string;
  preselectedLibrary?: string;
  selectedModelId?: string;
  onModelChange?: (modelId: string) => void;
  credentials?: Record<string, Record<string, string>>;
}

export default function ChatContainer({
  programs,
  defaultProgramId,
  preselectedLibrary,
  selectedModelId: externalSelectedModelId,
  onModelChange: externalOnModelChange,
  credentials
}: ChatContainerProps) {
  const config = loadConfig();
  const [activeProgram, setActiveProgram] = useState(defaultProgramId);
  // Chat state is managed internally by ChatSimple component
  // Always use the external model ID if provided, otherwise fall back to default
  const effectiveModelId = externalSelectedModelId || config.defaultModelId;
  
  // No need for local state - just use the external one directly
  const selectedModelId = effectiveModelId;

  // Preload context for the default program when the component mounts
  useEffect(() => {
    if (defaultProgramId) {
      preloadContext(defaultProgramId).catch(error => {
        console.error(`Error preloading context for default program ${defaultProgramId}:`, error);
      });
    }
  }, [defaultProgramId]);

  // No need to initialize chat states as they're managed internally by ChatSimple

  // Handle program change
  const handleProgramChange = (programId: string) => {
    setActiveProgram(programId);
  };

  // Handle model change
  const handleModelChange = (modelId: string) => {
    // Call external handler if provided
    if (externalOnModelChange) {
      externalOnModelChange(modelId);
    }
  };

  // Get the active program
  const getActiveProgram = () => {
    return programs.find(p => p.id === activeProgram) || programs[0];
  };

  const currentProgram = getActiveProgram();
  const showTabs = programs.length > 1;
  const showContextLink = config.showContextLink !== false; // Default to true if not specified

  // Check if we should use simple mode (hide top panels when simpleMode is enabled and only one program)
  // Note: We no longer check the number of available models to allow for fallback models
  const useSimpleMode = config.simpleMode === true && programs.length === 1;

  // Load libraries based on the active program
  const getLibraries = () => {
    if (activeProgram === 'astronomy') {
      return loadAstronomyData().libraries;
    } else if (activeProgram === 'finance') {
      return loadFinanceData().libraries;
    }
    return [];
  };

  return (
    <div className="flex flex-col w-full mx-auto h-full">
      <ChatSimple
        programId={activeProgram}
        greeting={config.greeting || "How can I help you?"}
        selectedModelId={selectedModelId}
        libraries={getLibraries()}
        preselectedLibrary={preselectedLibrary}
        credentials={credentials}
      />
    </div>
  );
}
