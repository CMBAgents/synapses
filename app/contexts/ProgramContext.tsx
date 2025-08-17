'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ProgramContextType {
  activeProgramId: string;
  setActiveProgramId: (programId: string) => void;
  selectedLibrary: any;
  setSelectedLibrary: (library: any) => void;
}

const ProgramContext = createContext<ProgramContextType | undefined>(undefined);

export function useProgramContext() {
  const context = useContext(ProgramContext);
  if (context === undefined) {
    throw new Error('useProgramContext must be used within a ProgramProvider');
  }
  return context;
}

interface ProgramProviderProps {
  children: ReactNode;
  initialProgramId?: string;
}

export function ProgramProvider({ children, initialProgramId = '' }: ProgramProviderProps) {
  const [activeProgramId, setActiveProgramId] = useState<string>(initialProgramId);
  const [selectedLibrary, setSelectedLibrary] = useState<any>(null);

  const value = {
    activeProgramId,
    setActiveProgramId,
    selectedLibrary,
    setSelectedLibrary,
  };

  return (
    <ProgramContext.Provider value={value}>
      {children}
    </ProgramContext.Provider>
  );
}
