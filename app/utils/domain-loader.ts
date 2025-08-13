import astronomyData from '../data/astronomy-libraries.json';
import financeData from '../data/finance-libraries.json';

export type LibraryEntry = {
  rank: number;
  name: string;
  github_url: string;
  stars: number;
  hasContextFile?: boolean;
  contextFileName?: string;
  programId?: string; // Derived field for the program ID
};

export type DomainData = {
  libraries: LibraryEntry[];
  domain: string;
  description: string;
  keywords: string[];
};

export function loadAstronomyData(): DomainData {
  const data = astronomyData as DomainData;
  
  // Add programId field to each library entry
  data.libraries = data.libraries.map(lib => ({
    ...lib,
    programId: lib.contextFileName ? lib.contextFileName.replace('-context.txt', '') : undefined
  }));
  
  return data;
}

export function loadFinanceData(): DomainData {
  return financeData as DomainData;
}

export function getDomainData(domain: 'astronomy' | 'finance'): DomainData {
  switch (domain) {
    case 'astronomy':
      return loadAstronomyData();
    case 'finance':
      return loadFinanceData();
    default:
      throw new Error(`Unknown domain: ${domain}`);
  }
}

export function getAllDomains(): Array<{id: string, name: string, description: string, icon: string}> {
  return [
    {
      id: 'astronomy',
      name: 'Astrophysics & Cosmology',
      description: 'Celestial observations, gravitational waves, and cosmic microwave background analysis',
      icon: ''
    },
    {
      id: 'machine-learning',
      name: 'Machine Learning',
      description: 'Deep learning, neural networks, and AI model development',
      icon: ''
    },
    {
      id: 'finance',
      name: 'Finance & Trading',
      description: 'Portfolio optimization, algorithmic trading, and financial analysis',
      icon: ''
    }
  ];
} 