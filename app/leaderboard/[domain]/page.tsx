import { notFound } from 'next/navigation';
import LeaderboardTemplate from '@/app/ui/leaderboard-template';
import { domainExists } from '@/app/utils/domain-loader';
import { getSupportedDomains } from '@/app/config/domains';

interface LeaderboardDomainPageProps {
  params: Promise<{
    domain: string;
  }>;
}

export default async function LeaderboardDomainPage({ params }: LeaderboardDomainPageProps) {
  const { domain } = await params;

  // Check if the domain exists
  if (!domainExists(domain)) {
    notFound();
  }

  return <LeaderboardTemplate domain={domain} />;
}

// Generate static params for all available domains
export async function generateStaticParams() {
  // Get domains from centralized configuration
  const supportedDomains = getSupportedDomains();
  return supportedDomains.map(domain => ({ domain }));
}
