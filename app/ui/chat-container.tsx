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
  showModelSelectorOnly?: boolean;
}

export default function ChatContainer({
  programs,
  defaultProgramId,
  preselectedLibrary,
  showModelSelectorOnly = false
}: ChatContainerProps) {
  const [config, setConfig] = useState<any>(null);
  const [activeProgram, setActiveProgram] = useState(defaultProgramId);
  const [selectedModelId, setSelectedModelId] = useState<string>('');

  // Load config safely
  useEffect(() => {
    try {
      const loadedConfig = loadConfig();
      setConfig(loadedConfig);
      setSelectedModelId(loadedConfig.defaultModelId || 'gemini/gemini-2.5-flash-preview-04-17');
    } catch (error) {
      console.error('Error loading config:', error);
      // Set fallback values
      setConfig({
        availableModels: [],
        defaultModelId: 'gemini/gemini-2.5-flash-preview-04-17',
        greeting: "How can I help you?"
      });
      setSelectedModelId('gemini/gemini-2.5-flash-preview-04-17');
    }
  }, []);

  // Preload context for the default program when the component mounts
  useEffect(() => {
    if (defaultProgramId) {
      preloadContext(defaultProgramId).catch(error => {
        console.error(`Error preloading context for default program ${defaultProgramId}:`, error);
      });
    }
  }, [defaultProgramId]);

  // Handle program change
  const handleProgramChange = (programId: string) => {
    setActiveProgram(programId);
  };

  // Handle model change
  const handleModelChange = (modelId: string) => {
    setSelectedModelId(modelId);
  };

  // Get the active program
  const getActiveProgram = () => {
    return programs.find(p => p.id === activeProgram) || programs[0];
  };

  const currentProgram = getActiveProgram();
  const showTabs = programs.length > 1;
  const showContextLink = config?.showContextLink !== false; // Default to true if not specified

  // Check if we should use simple mode (hide top panels when simpleMode is enabled and only one program)
  const useSimpleMode = config?.simpleMode === true && programs.length === 1;

  // Load libraries based on the active program
  const getLibraries = () => {
    if (activeProgram === 'astronomy') {
      return loadAstronomyData().libraries;
    } else if (activeProgram === 'finance') {
      return loadFinanceData().libraries;
    }
    return [];
  };

  // Don't render until config is loaded
  if (!config) {
    return <div className="flex flex-col w-full h-full p-4 text-white">Loading...</div>;
  }

  // If showModelSelectorOnly is true, only show the model selector
  if (showModelSelectorOnly) {
    return (
      <ModelSelector
        models={config.availableModels || []}
        selectedModelId={selectedModelId}
        onModelChange={handleModelChange}
      />
    );
  }

  return (
    <div className="flex flex-col w-full h-full">
      {/* Chat area */}
      <div className="flex-1">
        <ChatSimple
          programId={activeProgram}
          greeting={config.greeting || "How can I help you?"}
          selectedModelId={selectedModelId}
          libraries={getLibraries()}
          preselectedLibrary={preselectedLibrary}
        />
      </div>
    </div>
  );
}
