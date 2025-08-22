'use client'

import { useState, useEffect } from 'react';
import ChatSimple from './chat-simple';
import ModelSelector from './model-selector';
import { Program } from '@/app/utils/types';
import { loadConfig } from '@/app/utils/config';
import { preloadContext } from '@/app/utils/context';
import { loadAstronomyData, loadFinanceData, loadBiochemistryData, loadMachineLearningData } from '@/app/utils/domain-loader';
import { useProgramContext } from '../contexts/ProgramContext';

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
  const { activeProgramId } = useProgramContext();
  const [config, setConfig] = useState<any>(null);
  const [selectedModelId, setSelectedModelId] = useState<string>('');
  const [credentials, setCredentials] = useState<Record<string, Record<string, string>>>({});

  // Load config safely
  useEffect(() => {
    try {
      const loadedConfig = loadConfig();
      setConfig(loadedConfig);
      setSelectedModelId(loadedConfig.defaultModelId || 'deepseek/deepseek-chat-v3-0324');
    } catch (error) {
      console.error('Error loading config:', error);
      // Set fallback values
      setConfig({
        availableModels: [],
        defaultModelId: 'deepseek/deepseek-chat-v3-0324',
        greeting: "How can I help you?"
      });
      setSelectedModelId('deepseek/deepseek-chat-v3-0324');
    }
  }, []);

  // Preload context for the active program when the component mounts
  useEffect(() => {
    if (activeProgramId && activeProgramId !== '') {
      preloadContext(activeProgramId).catch(error => {
        console.error(`Error preloading context for active program ${activeProgramId}:`, error);
      });
    }
  }, [activeProgramId]);

  // Handle model change
  const handleModelChange = (modelId: string) => {
    setSelectedModelId(modelId);
  };

  // Handle credentials change
  const handleCredentialsChange = (newCredentials: Record<string, Record<string, string>>) => {
    setCredentials(newCredentials);
  };

  // Get the active program - use the global activeProgramId
  const getActiveProgram = () => {
    if (activeProgramId && activeProgramId !== '') {
      return programs.find(p => p.id === activeProgramId) || programs[0];
    }
    // If no specific program is selected, return the first available program
    return programs[0];
  };

  const currentProgram = getActiveProgram();
  const showTabs = programs.length > 1;
  const showContextLink = config?.showContextLink !== false; // Default to true if not specified

  // Check if we should use simple mode (hide top panels when simpleMode is enabled and only one program)
  const useSimpleMode = config?.simpleMode === true && programs.length === 1;

  // Load libraries based on the active program
  const getLibraries = () => {
    if (activeProgramId === 'astronomy') {
      return loadAstronomyData().libraries;
    } else if (activeProgramId === 'finance') {
      return loadFinanceData().libraries;
    } else if (activeProgramId === 'biochemistry') {
      return loadBiochemistryData().libraries;
    } else if (activeProgramId === 'machinelearning') {
      return loadMachineLearningData().libraries;
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
        onCredentialsChange={handleCredentialsChange}
      />
    );
  }

  return (
    <div className="flex flex-col w-full h-full">
      {/* Chat area */}
      <div className="flex-1 h-full">
        <ChatSimple
          programId={activeProgramId || 'general'}
          greeting={config.greeting || "How can I help you?"}
          selectedModelId={selectedModelId}
          libraries={getLibraries()}
          preselectedLibrary={preselectedLibrary}
          credentials={credentials}
        />
      </div>
    </div>
  );
}
