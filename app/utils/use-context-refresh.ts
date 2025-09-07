'use client';

import { useState, useEffect } from 'react';

export function useContextRefresh(domain: string) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    const updateContextStatus = async () => {
    setIsUpdating(true);
    try {
      const response = await fetch(`/api/context?domain=${domain}&action=updateLibrariesWithContextStatus`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store'
      });
      
      if (response.ok) {
        setLastUpdate(new Date());
      }
    } catch (error) {
      // Silent error handling
    } finally {
      setIsUpdating(false);
    }
  };

  // Auto-update when component mounts
  useEffect(() => {
    updateContextStatus();
  }, [domain]);

  return {
    isUpdating,
    lastUpdate,
    updateContextStatus
  };
} 