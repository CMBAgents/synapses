import { notFound } from 'next/navigation';
import LeaderboardTemplate from '@/app/ui/leaderboard-template';
import { domainExists } from '@/app/utils/domain-loader';

interface LeaderboardDomainPageProps {
  params: {
    domain: string;
  };
}

export default function LeaderboardDomainPage({ params }: LeaderboardDomainPageProps) {
  const { domain } = params;

  // Check if the domain exists
  if (!domainExists(domain)) {
    notFound();
  }

  return <LeaderboardTemplate domain={domain} />;
}

// Generate static params for all available domains
export async function generateStaticParams() {
  // This would be generated at build time
  // For now, we'll return the known domains
  return [
    { domain: 'astronomy' },
    { domain: 'finance' },
    { domain: 'biochemistry' },
    { domain: 'machinelearning' },
  ];
}
