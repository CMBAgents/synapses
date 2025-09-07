import financeData from '../data/finance-libraries.json';
import astronomyData from '../data/astronomy-libraries.json';
import machinelearningData from '../data/machinelearning-libraries.json';
import biochemistryData from '../data/biochemistry-libraries.json';

export type LibraryEntry = {
  rank: number;
  name: string;
  github_url: string;
  stars: number;
  hasContextFile?: boolean;
  contextFileName?: string;
};

export type DomainData = {
  libraries: LibraryEntry[];
  domain: string;
  description: string;
  keywords: string[];
};

// Map of domain IDs to their data
const domainDataMap: Record<string, DomainData> = {
  'finance': financeData as DomainData,
  'astronomy': astronomyData as DomainData,
  'machinelearning': machinelearningData as DomainData,
  'biochemistry': biochemistryData as DomainData,
};

// Individual loader functions for backward compatibility
export function loadFinanceData(): DomainData { return financeData as DomainData; }
export function loadAstronomyData(): DomainData { return astronomyData as DomainData; }
export function loadMachineLearningData(): DomainData { return machinelearningData as DomainData; }
export function loadBiochemistryData(): DomainData { return biochemistryData as DomainData; }

export function getDomainData(domain: string): DomainData {
  const domainData = domainDataMap[domain];
  if (!domainData) {
    throw new Error(`Unknown domain: ${domain}`);
  }
  return domainData;
}

export function getAllDomains(): Array<{id: string, name: string, description: string, icon: string}> {
  return [
  {
    "id": "finance",
    "name": "Finance & Trading",
    "description": "Portfolio optimization, algorithmic trading, and financial analysis",
    "icon": ""
  },
  {
    "id": "astronomy",
    "name": "Astrophysics & Cosmology",
    "description": "Celestial observations, gravitational waves, and cosmic microwave background analysis",
    "icon": ""
  },
  {
    "id": "machinelearning",
    "name": "Machine Learning & AI",
    "description": "Deep learning, neural networks, and AI model development",
    "icon": ""
  },
  {
    "id": "biochemistry",
    "name": "Biochemistry & Bioinformatics",
    "description": "Molecular dynamics, drug discovery, and computational biology",
    "icon": ""
  }
];
}

// Function to check if a domain exists
export function domainExists(domain: string): boolean {
  return domain in domainDataMap;
}

// Function to get all available domain IDs
export function getAvailableDomainIds(): string[] {
  return Object.keys(domainDataMap);
}
