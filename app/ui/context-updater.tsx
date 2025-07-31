'use client';

import { useContextRefresh } from '../utils/use-context-refresh';

interface ContextUpdaterProps {
  domain: 'astronomy' | 'finance';
  children: React.ReactNode;
}

export default function ContextUpdater({ domain, children }: ContextUpdaterProps) {
  const { isUpdating, lastUpdate } = useContextRefresh(domain);

  return <>{children}</>;
} 