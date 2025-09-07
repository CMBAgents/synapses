import { notFound } from 'next/navigation';
import ChatTemplate from '@/app/ui/chat-template';
import { domainExists } from '@/app/utils/domain-loader';
import { getSupportedDomains } from '@/app/config/domains';

interface ChatDomainPageProps {
  params: Promise<{
    domain: string;
  }>;
}

export default async function ChatDomainPage({ params }: ChatDomainPageProps) {
  const { domain } = await params;

  // Check if the domain exists
  if (!domainExists(domain)) {
    notFound();
  }

  return <ChatTemplate domain={domain} />;
}

// Generate static params for all available domains
export async function generateStaticParams() {
  // Get domains from centralized configuration
  const supportedDomains = getSupportedDomains();
  return supportedDomains.map(domain => ({ domain }));
}
