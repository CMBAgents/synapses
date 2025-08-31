import { notFound } from 'next/navigation';
import ChatTemplate from '@/app/ui/chat-template';
import { domainExists } from '@/app/utils/domain-loader';

interface ChatDomainPageProps {
  params: {
    domain: string;
  };
}

export default function ChatDomainPage({ params }: ChatDomainPageProps) {
  const { domain } = params;

  // Check if the domain exists
  if (!domainExists(domain)) {
    notFound();
  }

  return <ChatTemplate domain={domain} />;
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
