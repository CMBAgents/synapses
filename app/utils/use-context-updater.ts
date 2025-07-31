'use client';

import { useEffect } from 'react';

export function useContextUpdater(domain: 'astronomy' | 'finance') {
  useEffect(() => {
    const updateContextStatus = async () => {
      try {
        const response = await fetch('/api/context', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          cache: 'no-store'
        });
        
        if (response.ok) {
          console.log(`Context status updated for ${domain}`);
        }
      } catch (error) {
        console.warn(`Could not update context status for ${domain}:`, error);
      }
    };

    // Update context status when component mounts
    updateContextStatus();
  }, [domain]);
}

export function useGlobalContextUpdater() {
  useEffect(() => {
    const updateAllContextStatus = async () => {
      try {
        const domains = ['astronomy', 'finance'];
        
        for (const domain of domains) {
          const response = await fetch(`/api/context?domain=${domain}&action=updateLibrariesWithContextStatus`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            cache: 'no-store'
          });
          
          if (response.ok) {
            console.log(`Context status updated for ${domain}`);
          }
        }
      } catch (error) {
        console.warn('Could not update context status:', error);
      }
    };

    // Update context status when component mounts
    updateAllContextStatus();
  }, []);
} 