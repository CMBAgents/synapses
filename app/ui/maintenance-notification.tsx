'use client';

import { useState, useEffect } from 'react';
import { useMaintenance } from '../utils/use-maintenance';

export default function MaintenanceNotification() {
  const [showNotification, setShowNotification] = useState(false);
  const [maintenanceStatus, setMaintenanceStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');
  
  const { runMaintenance, isRunning } = useMaintenance({
    type: 'quick',
    autoRun: false, // Ne pas exécuter automatiquement
    onStart: () => {
      setMaintenanceStatus('running');
      setShowNotification(true);
    },
    onComplete: () => {
      setMaintenanceStatus('completed');
      setTimeout(() => setShowNotification(false), 3000);
    },
    onError: () => {
      setMaintenanceStatus('error');
      setTimeout(() => setShowNotification(false), 5000);
    }
  });

  // Masquer la notification après un délai
  useEffect(() => {
    if (maintenanceStatus === 'completed' || maintenanceStatus === 'error') {
      const timer = setTimeout(() => {
        setShowNotification(false);
        setMaintenanceStatus('idle');
      }, maintenanceStatus === 'completed' ? 3000 : 5000);
      
      return () => clearTimeout(timer);
    }
  }, [maintenanceStatus]);

  if (!showNotification) return null;

  const getStatusColor = () => {
    switch (maintenanceStatus) {
      case 'running':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = () => {
    switch (maintenanceStatus) {
      case 'running':
        return 'Maintenance en cours...';
      case 'completed':
        return 'Maintenance terminée avec succès';
      case 'error':
        return 'Erreur lors de la maintenance';
      default:
        return 'Maintenance';
    }
  };

  const getStatusIcon = () => {
    switch (maintenanceStatus) {
      case 'running':
        return '🔄';
      case 'completed':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '⚙️';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className={`${getStatusColor()} text-white px-4 py-3 rounded-lg shadow-lg flex items-center space-x-3 min-w-64`}>
        <span className="text-xl">{getStatusIcon()}</span>
        <div className="flex-1">
          <p className="font-medium">{getStatusText()}</p>
          {maintenanceStatus === 'running' && (
            <div className="mt-2">
              <div className="w-full bg-white bg-opacity-30 rounded-full h-2">
                <div className="bg-white h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
              </div>
            </div>
          )}
        </div>
        <button
          onClick={() => setShowNotification(false)}
          className="text-white hover:text-gray-200 transition-colors"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
