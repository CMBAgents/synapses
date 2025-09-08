/**
 * Configuration centralisée des domaines
 * Ce fichier lit la configuration depuis config.json
 * Pour ajouter un nouveau domaine, ajoutez-le à la section "domains" de config.json
 */

import config from '../../config.json';

// Types basés sur la configuration
export type Domain = typeof config.domains.supported[number];

/**
 * Vérifie si un domaine est supporté
 */
export function isDomainSupported(domain: string): domain is Domain {
  return config.domains.supported.includes(domain as Domain);
}

/**
 * Obtient tous les domaines supportés
 */
export function getSupportedDomains(): readonly Domain[] {
  return config.domains.supported;
}

/**
 * Obtient le nom d'affichage d'un domaine
 */
export function getDomainDisplayName(domain: Domain): string {
  return config.domains.displayNames[domain as keyof typeof config.domains.displayNames] || domain;
}

/**
 * Obtient la description d'un domaine
 */
export function getDomainDescription(domain: Domain): string {
  return config.domains.descriptions[domain as keyof typeof config.domains.descriptions] || `Top libraries in ${domain}`;
}

/**
 * Obtient le programme par défaut pour un domaine
 */
export function getDomainDefaultProgram(domain: Domain): string {
  return config.domains.defaultPrograms[domain as keyof typeof config.domains.defaultPrograms] || '';
}

/**
 * Obtient la description spécialisée pour l'IA d'un domaine
 */
export function getDomainSpecializedDescription(domain: Domain): string {
  const descriptions: Record<string, string> = {
    'astronomy': 'astrophysics and cosmology',
    'finance': 'finance and trading',
    'biochemistry': 'biochemistry and bioinformatics',
    'machinelearning': 'machine learning and artificial intelligence'
  };
  return descriptions[domain] || domain;
}

/**
 * Obtient le nom court du domaine pour l'IA
 */
export function getDomainShortName(domain: Domain): string {
  const shortNames: Record<string, string> = {
    'astronomy': 'astrophysics',
    'finance': 'finance',
    'biochemistry': 'biochemistry',
    'machinelearning': 'machine learning'
  };
  return shortNames[domain] || domain;
}
