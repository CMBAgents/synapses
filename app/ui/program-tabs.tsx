'use client'

import { useState, useEffect } from 'react';
import { Program } from '@/app/utils/types';
import { preloadContext } from '@/app/utils/context';

interface ProgramTabsProps {
  programs: Program[];
  activeProgram: string;
  onProgramChange: (programId: string) => void;
}

export default function ProgramTabs({
  programs,
  activeProgram,
  onProgramChange
}: ProgramTabsProps) {
  // Preload context for the active program when it changes
  useEffect(() => {
    // Preload context for the active program
    if (activeProgram) {
      preloadContext(activeProgram).catch(error => {
        console.error(`Error preloading context for ${activeProgram}:`, error);
      });
    }
  }, [activeProgram]);

  // Handle tab change
  const handleTabChange = (programId: string) => {
    // Call the parent's onProgramChange handler
    onProgramChange(programId);

    // No need to preload here as the useEffect will handle it when activeProgram changes
  };

  return (
    <div className="border-b border-gray-300 dark:border-gray-700 bg-gray-100 dark:bg-gray-900">
      <ul className="flex px-2 pt-2">
        {programs.map((program) => (
          <li key={program.id} className="mr-1">
            <button
              className={`px-5 py-2 rounded-t-md transition-colors ${activeProgram === program.id
                ? 'bg-white dark:bg-gray-900 text-blue-700 dark:text-blue-400 font-semibold border-2 border-gray-300 dark:border-gray-700 border-b-0'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-700'
              }`}
              onClick={() => handleTabChange(program.id)}
            >
              {program.name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
