'use client';

import { useProgramContext } from '../contexts/ProgramContext';

export default function DebugPanel() {
  const { activeProgramId, selectedLibrary } = useProgramContext();

  return (
    <div className="fixed top-4 left-4 bg-black/80 text-white p-3 rounded-lg text-sm z-50 max-w-xs">
      <div className="font-bold mb-2 text-green-400">DEBUG: Nouveau Système</div>
      
      <div className="mb-2">
        <div className="font-semibold">Active Program ID:</div>
        <div className="font-mono text-green-400 break-all">{activeProgramId || 'None'}</div>
      </div>

      <div className="mb-2">
        <div className="font-semibold">Selected Library:</div>
        <div className="text-blue-400">{selectedLibrary?.name || 'None'}</div>
      </div>

      <div className="text-xs text-gray-400 mt-2">
        ✅ Ancien système supprimé<br/>
        ✅ Contexte global actif<br/>
        ✅ programId dynamique
      </div>
    </div>
  );
}
