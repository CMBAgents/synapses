'use client'

import { useState, useEffect } from 'react';
import ProgramTabs from './program-tabs';
import ChatSimple from './chat-simple';
import ModelSelector from './model-selector';
import ThemeWrapper from './theme-wrapper';
import { Program } from '@/app/utils/types';
import { loadConfig } from '@/app/utils/config';
import { preloadContext } from '@/app/utils/context';

interface ChatContainerProps {
  programs: Program[];
  defaultProgramId: string;
}

export default function ChatContainer({
  programs,
  defaultProgramId
}: ChatContainerProps) {
  const config = loadConfig();
  const [activeProgram, setActiveProgram] = useState(defaultProgramId);
  // Chat state is managed internally by ChatSimple component
  const [selectedModelId, setSelectedModelId] = useState<string>(config.defaultModelId);

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
    setSelectedModelId(modelId);
    // The selected model is passed to ChatSimple component
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

  return (
    <div className="flex flex-col w-full mx-auto border border-gray-300 dark:border-gray-700 shadow-lg rounded-md overflow-hidden text-sm sm:text-base bg-white dark:bg-gray-900">
      {!useSimpleMode && (
        <div className="flex flex-col bg-white dark:bg-gray-900">
          <div className="flex justify-between items-center">
            <div className="flex-grow">
              {showTabs && (
                <ProgramTabs
                  programs={programs}
                  activeProgram={activeProgram}
                  onProgramChange={handleProgramChange}
                />
              )}
            </div>
            {config.availableModels.length > 1 && (
              <div className="p-2 relative w-56">
                <ModelSelector
                  models={config.availableModels}
                  selectedModelId={selectedModelId}
                  onModelChange={handleModelChange}
                />
              </div>
            )}
          </div>

          <div className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 border-b border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div className="flex justify-between items-center">
              <div>
                {currentProgram.description}
              </div>
              <div className="flex space-x-4 items-center">
                {showContextLink && (
                  <a
                    href={`/api/context/${currentProgram.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline whitespace-nowrap"
                    title="View and download the LLM document context file"
                  >
                    <span className="hidden sm:inline">Context</span>
                    <span className="sm:hidden">📄</span>
                  </a>
                )}
                <a
                  href={currentProgram.docsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline whitespace-nowrap"
                  title="View official documentation"
                >
                  <span className="hidden sm:inline">Docs</span>
                  <span className="sm:hidden">📖</span>
                </a>
                <ThemeWrapper />
              </div>
            </div>
          </div>
        </div>
      )}

      <ChatSimple
        /* Remove key to prevent re-render when program changes */
        programId={activeProgram}
        greeting={config.greeting || "How can I help you?"}
        selectedModelId={selectedModelId}
      />
    </div>
  );
}
