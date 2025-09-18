import { getProgramById } from './config';
import { Program } from './types';
import { Domain, getSupportedDomains } from '@/app/config/domains';

// Cache for storing loaded context to avoid repeated lookups
const combinedContextCache: Record<string, string> = {};

// Cache for storing URL-based context to avoid repeated fetches
const urlContextCache: Record<string, string> = {};

// Cache for storing loaded context files - ONLY ONE AT A TIME
let fileContextCache: { programId: string; content: string } | null = null;

// Memory management - no size limits, but only one context at a time
const MAX_CACHE_ENTRIES = 1; // Only 1 context file in cache

// Track cache usage (for monitoring only)
let currentCacheSize = 0;

// Cleanup interval
let cleanupInterval: NodeJS.Timeout | null = null;

/**
 * Clear all caches to free memory
 */
export function clearAllCaches(): void {
  // Clear single context cache
  if (fileContextCache) {
    const size = Buffer.byteLength(fileContextCache.content, 'utf8');
    currentCacheSize -= size;
    fileContextCache = null;
  }
  
  Object.keys(urlContextCache).forEach(key => {
    const size = Buffer.byteLength(urlContextCache[key], 'utf8');
    currentCacheSize -= size;
    delete urlContextCache[key];
  });
  
  Object.keys(combinedContextCache).forEach(key => {
    const size = Buffer.byteLength(combinedContextCache[key], 'utf8');
    currentCacheSize -= size;
    delete combinedContextCache[key];
  });
  
  console.log('All caches cleared to free memory');
}

/**
 * Start periodic cache cleanup (disabled since we have no size limits)
 */
function startCacheCleanup(): void {
  // Disabled - no size limits, only one context at a time
  console.log('Cache cleanup disabled - using single context cache without size limits');
}

// Track pending fetches to avoid duplicate requests
// Using any type to avoid TypeScript issues with Promise types
const pendingFetches: Record<string, any> = {};

/**
 * Manage cache size by removing oldest entries when limit is reached
 * NOTE: This is now simplified since we only cache one context at a time
 */
function manageCacheSize(cache: Record<string, string>, key: string, content: string) {
  const contentSize = Buffer.byteLength(content, 'utf8');
  
  // If adding this content would exceed entry limit, clean up
  if (Object.keys(cache).length >= MAX_CACHE_ENTRIES) {
    
    // Remove oldest entries (simple FIFO)
    const keys = Object.keys(cache);
    const entriesToRemove = Math.max(1, Math.floor(keys.length / 2)); // Remove half
    
    for (let i = 0; i < entriesToRemove; i++) {
      const oldestKey = keys[i];
      const removedSize = Buffer.byteLength(cache[oldestKey], 'utf8');
      currentCacheSize -= removedSize;
      delete cache[oldestKey];
    }
  }
  
  // Add new content
  cache[key] = content;
  currentCacheSize += contentSize;
}

// Function to check if a string is a URL
function isUrl(str: string): boolean {
  try {
    new URL(str);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Load context directly from .txt file via API (more efficient than embedded contexts)
 * @param programId The program ID
 * @param domain The domain for the program
 * @returns The context content or null if file not found
 */
async function loadContextFromFile(programId: string, domain: Domain): Promise<string | null> {
  // Check cache first - only if it's the same program
  if (fileContextCache && fileContextCache.programId === programId) {
    return fileContextCache.content;
  }

  try {
    // Get the program to find the context file name
    const program = getProgramById(programId) as Program;
    if (!program) {
      console.error(`Program not found: ${programId}`);
      return null;
    }

    // Try to get context file name from program configuration
    let contextFileName: string | null = null;
    
    if (program.contextFiles && program.contextFiles.length > 0) {
      // Use the first context file
      contextFileName = program.contextFiles[0];
    } else {
      // Fallback: construct filename from program ID
      contextFileName = `${programId}-context.txt`;
    }

    // Make API request to load the context file using the optimized endpoint
    // Use absolute URL to avoid relative path issues
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const response = await fetch(`${baseUrl}/api/context/${encodeURIComponent(contextFileName)}?domain=${domain}`);
    
    if (!response.ok) {
      console.log(`Context file not found: ${contextFileName} (${response.status})`);
      return null;
    }

    const contextContent = await response.text();
    if (!contextContent) {
      console.log(`No content in context file: ${contextFileName}`);
      return null;
    }

    // Cache the result - REPLACE previous context (only one at a time)
    if (fileContextCache) {
      const oldSize = Buffer.byteLength(fileContextCache.content, 'utf8');
      currentCacheSize -= oldSize;
    }
    
    fileContextCache = {
      programId: programId,
      content: contextContent
    };
    currentCacheSize += Buffer.byteLength(contextContent, 'utf8');
    
    console.log(`Loaded context from file: ${contextFileName} (${contextContent.length} bytes)`);
    return contextContent;

  } catch (error) {
    console.error(`Error loading context file for ${programId}:`, error);
    return null;
  }
}

/**
 * Get domain from program ID by checking the program configuration
 * @param programId The program ID
 * @returns The domain for the program
 */
function getDomainFromProgramId(programId: string): Domain {
  const program = getProgramById(programId) as Program;
  if (!program) {
    console.error(`Program not found: ${programId}`);
    return 'astronomy'; // Default fallback
  }
  
  // Try to find the domain by checking which domain's context files contain this program
  // This is more robust than hardcoded heuristics
  const supportedDomains = getSupportedDomains();
  
  for (const domain of supportedDomains) {
    // Check if the program ID matches patterns for this domain
    // This could be improved by adding domain metadata to the program configuration
    if (isProgramInDomain(programId, domain)) {
      return domain;
    }
  }
  
  // Default fallback
  return 'astronomy';
}

/**
 * Check if a program belongs to a specific domain based on heuristics
 * @param programId The program ID
 * @param domain The domain to check
 * @returns True if the program likely belongs to this domain
 */
function isProgramInDomain(programId: string, domain: Domain): boolean {
  // Define domain-specific patterns
  const domainPatterns: Record<Domain, string[]> = {
    'astronomy': ['skyfield', 'astropy', 'astrometry', 'einsteinpy', 'lightkurve', 'gwpy', 'pycbc', 'castro', 'healpy', 'photutils', 'class', 'spacepy', 'presto', 'galsim', 'galpy', 'radis', 'poppy', 'zeus', 'camb', 'tardis', 'astroplan', 'pymultinest', 'astronn', 'sep', 's2fft', 'stingray', 'ultranest', 'specutils', 'pypeit', 'pyastronomy', 'getdist', 'astroalign', 'cobaya', 'astroclip', 'gala', 'cmbagent', 'deepsphere', 'skypy', 'reproject', 'halotools', 'agama', 'petar', 'astronomaly', 'spectral-cube', 'astrophot', 'pyuvdata', 'ccdproc', 'gatspy', 'astrocv', 'astronify', 'sourcextractorplusplus', 'pyvo', 'astroscrappy', 'sncosmo', 'cosmopower', 'harmonic', 'spisea', 'turbustat', 'pynucastro', 'artpop', 'galstreams', 'astroddpm', 'smili', 'pybdsf', 'octotiger', 'pixell', 'quokka', 'galight', 'astromodels', 'skymapper', 'astro-accelerate', 'cosmolopy', 'extinction', 'gwfast', 'megalib', 'cosmolattice', 'astrodendro', 'toast', 'numcosmo', 'slicerastro', 'astrocats', 'swarp', 'visiomatic', 'astroabc', 'nmma', 'cosmotransitions', 'galacticus', 'astronet-triage', 'exosims', 'maestro', 'weirdestgalaxies', 'galario', 'pycorr', 'rmextract', 'frbpoppy'],
    'biochemistry': ['biopython', 'scikit-bio', 'mdanalysis', 'openmm', 'openmmtools', 'rdkit', 'pymol', 'openbabel', 'gromacs', 'chimerax'],
    'finance': ['quantopian', 'yfinance', 'ffn', 'pyfolio', 'finquant', 'empyrical', 'alphalens', 'qgrid'],
    'machinelearning': ['pytorch', 'tensorflow', 'scikit-learn', 'keras', 'transformers', 'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn']
  };
  
  const patterns = domainPatterns[domain] || [];
  return patterns.some(pattern => programId.toLowerCase().includes(pattern.toLowerCase()));
}

/**
 * Fetch context from a URL
 * @param url The URL to fetch context from
 * @returns The content of the context and whether it was freshly fetched
 */
async function fetchContextFromUrl(url: string): Promise<{ content: string; wasFetched: boolean }> {
  // Check if the URL context is already cached
  if (urlContextCache[url]) {
    // Return cached content without logging
    return { content: urlContextCache[url], wasFetched: false };
  }

  // Check if there's already a pending fetch for this URL
  if (pendingFetches[url]) {
    // Return the existing promise to avoid duplicate fetches
    return pendingFetches[url];
  }

  // Only log when actually fetching
  console.log(`Fetching context from URL: ${url}`);

  // Create a new fetch promise
  const fetchPromise = new Promise<{ content: string; wasFetched: boolean }>(async (resolve) => {
    try {
      const response = await fetch(url, {
        headers: {
          'Accept': 'text/plain, text/markdown, application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch context from URL: ${url}, status: ${response.status}`);
      }

      // Try to get the content type
      const contentType = response.headers.get('Content-Type') || '';

      let content: string;

      // Handle different content types
      if (contentType.includes('application/json')) {
        // If it's JSON, stringify it
        const json = await response.json();
        content = JSON.stringify(json, null, 2);
      } else {
        // Otherwise treat as text
        content = await response.text();
      }

      // Cache the content with memory management
      manageCacheSize(urlContextCache, url, content);
      console.log(`Successfully fetched context from URL: ${url} (${content.length} bytes)`);

      // Remove from pending fetches
      delete pendingFetches[url];

      resolve({ content, wasFetched: true });
    } catch (error) {
      // Remove from pending fetches on error
      delete pendingFetches[url];
      console.error(`Error fetching context from URL: ${url}`, error);

      // Instead of re-throwing the error, resolve with a fallback response
      // This prevents unhandled promise rejections
      resolve({
        content: `Error fetching context from URL: ${url}. ${error instanceof Error ? error.message : String(error)}`,
        wasFetched: true
      });
    }
  });

  // Store the promise in pendingFetches
  pendingFetches[url] = fetchPromise;

  // Return the promise
  return fetchPromise;
}

/**
 * Load context for a program using either embedded context content or a URL
 * @param contextFiles Array of context file paths or a single context file path
 * @param programId Optional program ID to directly load context for a specific program
 * @returns The content of the combined context
 */
export async function loadContext(contextFiles: string[] | string, programId?: string): Promise<string> {
  // If programId is provided, use it directly
  if (programId) {
    const program = getProgramById(programId) as Program;

    if (!program) {
      console.error(`Program not found: ${programId}`);
      return `Context could not be loaded. Program ${programId} not found.`;
    }

    // Check if the program has a combinedContextFile that is a URL
    if (program.combinedContextFile && isUrl(program.combinedContextFile)) {
      // Fetch the context from the URL - errors are handled inside fetchContextFromUrl
      const { content } = await fetchContextFromUrl(program.combinedContextFile);

      // If the content starts with "Error fetching context", it means there was an error
      // In that case, fall back to embedded context
      if (content.startsWith("Error fetching context")) {
        console.log(`Falling back to embedded context for program: ${programId}`);
      } else {
        return content;
      }
    }

    // Try to load context directly from .txt file first (more efficient)
    const domain = getDomainFromProgramId(programId);
    const contextContent = await loadContextFromFile(programId, domain);

    if (contextContent) {
      console.log(`Using direct file context for ${programId} (${contextContent.length} bytes)`);
      return contextContent;
    }

    // No fallback - context files are required

    console.error(`No context found for program: ${programId}`);
    return `Context could not be loaded. No context found for program: ${programId}.`;
  }

  // Convert single file to array for consistent handling
  const filesArray = typeof contextFiles === 'string' ? [contextFiles] : contextFiles;

  // Generate a cache key based on the context files
  const cacheKey = filesArray.join('|');

  // Check if the combined context is already cached
  if (combinedContextCache[cacheKey]) {
    return combinedContextCache[cacheKey];
  }

  // Find the program that matches these context files
  const program = Object.values(getProgramById() as Record<string, Program>)
    .find(p => p.contextFiles &&
      JSON.stringify(p.contextFiles.sort()) === JSON.stringify(filesArray.sort()));

  if (!program) {
    console.error(`No program found for context files: ${filesArray.join(', ')}`);
    return `Context could not be loaded. No matching program found for the specified context files.`;
  }

  // Check if the program has a combinedContextFile that is a URL
  if (program.combinedContextFile && isUrl(program.combinedContextFile)) {
    // Fetch the context from the URL - errors are handled inside fetchContextFromUrl
    const { content } = await fetchContextFromUrl(program.combinedContextFile);

    // If the content starts with "Error fetching context", it means there was an error
    // In that case, fall back to embedded context
    if (content.startsWith("Error fetching context")) {
      console.log(`Falling back to embedded context for program: ${program.id}`);
    } else {
      // Cache the content
      combinedContextCache[cacheKey] = content;
      return content;
    }
  }

  console.log(`Loading context from file for program: ${program.id}`);

  // Get the context from file for this program
  const domain = getDomainFromProgramId(program.id);
  const contextContent = await loadContextFromFile(program.id, domain);

  if (!contextContent) {
    console.error(`No context file found for program: ${program.id}`);
    return `Context could not be loaded. No context file found for program: ${program.id}.`;
  }

  console.log(`Successfully loaded embedded context for ${program.id} (${contextContent.length} bytes)`);

  // Cache the content with memory management
  manageCacheSize(combinedContextCache, cacheKey, contextContent);
  return contextContent;
}

/**
 * Get the embedded context for a program directly
 * This is a convenience function that wraps the imported getEmbeddedContext
 * @param programId The ID of the program
 * @returns The embedded context content or undefined if not found
 */
export async function getEmbeddedContext(programId: string): Promise<string | undefined> {
  const domain = getDomainFromProgramId(programId);
  const result = await loadContextFromFile(programId, domain);
  return result || undefined;
}

/**
 * Get current cache info for debugging
 */
export function getCacheInfo() {
  return {
    hasContext: !!fileContextCache,
    currentProgram: fileContextCache?.programId || null,
    contextSize: fileContextCache ? Buffer.byteLength(fileContextCache.content, 'utf8') : 0,
    totalCacheSize: currentCacheSize,
    maxCacheSize: 'unlimited', // No size limits
    maxEntries: MAX_CACHE_ENTRIES
  };
}

/**
 * Preload context for a program (DISABLED to save memory)
 * This is useful for preloading context when a tab becomes active
 * @param programId The ID of the program
 * @returns A promise that resolves when the context is loaded
 */
export async function preloadContext(programId: string): Promise<void> {
  // Disabled to save memory - contexts will be loaded on-demand
  console.log(`Preloading disabled for memory optimization: ${programId}`);
  return;
}

/**
 * Get the system prompt with context for a specific program
 * @param programId The ID of the program
 * @param context The context content
 * @returns The system prompt with context
 */
export function getSystemPromptWithContext(programId: string, context: string): string {
  // Get the program configuration and global config
  const program = getProgramById(programId) as Program;
  const { loadConfig } = require('./config');
  const config = loadConfig();

  // Get program name and uppercase ID
  const programName = program?.name || programId.toUpperCase();
  const programIdUpper = programId.toUpperCase();

  // Get the system prompt template and replace placeholders
  // Load the system prompt from config.json if it's not available in the config object
  const rawConfig = require('../../config.json');
  let systemPromptTemplate = (config.systemPrompt || rawConfig.systemPrompt || '')
    .replace(/\{PROGRAM_ID\}/g, programIdUpper)
    .replace(/\{PROGRAM_NAME\}/g, programName);

  // Add program-specific extra system prompt if available
  if (program?.extraSystemPrompt) {
    systemPromptTemplate += `\n\n${program.extraSystemPrompt}`;
  }

  // Add additional context if available
  if (config.additionalContext) {
    systemPromptTemplate += `\n\nUSER CONTEXT:\n${config.additionalContext}`;
  }

  // Append the documentation to the system prompt
  return `${systemPromptTemplate}\n\nDOCUMENTATION:\n${context}`;
}
