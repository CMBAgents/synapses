'use client';

import { useEffect, useRef } from 'react';

interface MaintenanceOptions {
  type?: 'quick' | 'full';
  onStart?: () => void;
  onComplete?: () => void;
  onError?: (error: string) => void;
  autoRun?: boolean;
}

export function useMaintenance(options: MaintenanceOptions = {}) {
  const {
    type = 'quick',
    onStart,
    onComplete,
    onError,
    autoRun = true
  } = options;
  
  const hasRunRef = useRef(false);

  const runMaintenance = async () => {
    if (hasRunRef.current) return;
    
    try {
      onStart?.();
      
      const response = await fetch('/api/maintenance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log(`Maintenance ${type} started:`, result.message);
        onComplete?.();
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to start maintenance');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Maintenance error:', errorMessage);
      onError?.(errorMessage);
    }
  };

  // Exécuter la maintenance automatiquement lors du premier chargement
  useEffect(() => {
    if (autoRun && !hasRunRef.current) {
      hasRunRef.current = true;
      runMaintenance();
    }
  }, [autoRun]);

  // Exécuter la maintenance lors du refresh de la page
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Marquer que la maintenance peut être relancée au prochain chargement
      hasRunRef.current = false;
    };

    const handleLoad = () => {
      if (autoRun && !hasRunRef.current) {
        hasRunRef.current = true;
        runMaintenance();
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('load', handleLoad);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('load', handleLoad);
    };
  }, [autoRun]);

  return {
    runMaintenance,
    isRunning: hasRunRef.current
  };
}

// Hook pour la maintenance globale de l'application
export function useGlobalMaintenance() {
  return useMaintenance({
    type: 'quick',
    autoRun: true,
    onStart: () => console.log('Starting global maintenance...'),
    onComplete: () => console.log('Global maintenance started successfully'),
    onError: (error) => console.error('Global maintenance failed:', error)
  });
}
