'use client';

import { useGlobalMaintenance } from '../utils/use-maintenance';

export default function MaintenanceProvider() {
  // Utilise le hook de maintenance globale
  useGlobalMaintenance();
  
  // Ce composant ne rend rien visuellement, il gère juste la maintenance
  return null;
}
