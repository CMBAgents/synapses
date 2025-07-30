import { getProgramById } from './config';
import { Program } from './types';
import { getEmbeddedContext as getEmbeddedContextFromModule } from './embedded-context';

// Cache for storing loaded context to avoid repeated lookups
const combinedContextCache: Record<string, string> = {};

// Cache for storing URL-based context to avoid repeated fetches
const urlContextCache: Record<string, string> = {};

// Track pending fetches to avoid duplicate requests
// Using any type to avoid TypeScript issues with Promise types
const pendingFetches: Record<string, any> = {};

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

      // Cache the content
      urlContextCache[url] = content;
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

    // Use embedded context as fallback or if no URL is provided
    const contextContent = getEmbeddedContextFromModule(programId);

    if (!contextContent) {
      console.error(`No embedded context found for program: ${programId}`);
      return `Context could not be loaded. No embedded context found for program: ${programId}.`;
    }

    console.log(`Using embedded context for ${programId} (${contextContent.length} bytes)`);
    return contextContent;
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

  console.log(`Loading embedded context for program: ${program.id}`);

  // Get the embedded context for this program
  const contextContent = getEmbeddedContextFromModule(program.id);

  if (!contextContent) {
    console.error(`No embedded context found for program: ${program.id}`);
    return `Context could not be loaded. No embedded context found for program: ${program.id}.`;
  }

  console.log(`Successfully loaded embedded context for ${program.id} (${contextContent.length} bytes)`);

  // Cache the content
  combinedContextCache[cacheKey] = contextContent;
  return contextContent;
}

/**
 * Get the embedded context for a program directly
 * This is a convenience function that wraps the imported getEmbeddedContext
 * @param programId The ID of the program
 * @returns The embedded context content or undefined if not found
 */
export function getEmbeddedContext(programId: string): string | undefined {
  // Re-export from embedded-context.ts
  return getEmbeddedContextFromModule(programId);
}

/**
 * Preload context for a program
 * This is useful for preloading context when a tab becomes active
 * @param programId The ID of the program
 * @returns A promise that resolves when the context is loaded
 */
export async function preloadContext(programId: string): Promise<void> {
  try {
    const program = getProgramById(programId) as Program;

    if (!program) {
      console.error(`Program not found for preloading: ${programId}`);
      return;
    }

    // If the program has a combinedContextFile that is a URL, preload it
    if (program.combinedContextFile && isUrl(program.combinedContextFile)) {
      // Fetch the context, but only log if it was actually fetched (not cached)
      const { wasFetched } = await fetchContextFromUrl(program.combinedContextFile);
      if (wasFetched) {
        console.log(`Preloaded context for program: ${programId}`);
      }
    }
  } catch (error) {
    console.error(`Error preloading context for program ${programId}:`, error);
  }
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
