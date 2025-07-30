import { Config, Program } from './types';

// Import the config directly
import rawConfigJson from '../../config.json';

/**
 * Type definition for the raw config.json file structure
 * This helps TypeScript understand what properties are available in the imported JSON
 */
interface RawConfigJson {
  systemPrompt?: string;
  programs: Array<{
    id: string;
    name: string;
    description: string;
    contextFiles: string[]; // Can be empty if combinedContextFile is a URL
    combinedContextFile?: string; // Can be a URL to fetch context from
    docsUrl: string;
    extraSystemPrompt?: string;
  }>;
  defaultProgram: string;
  showContextLink?: boolean;
  simpleMode?: boolean;
  greeting?: string;
  additionalContext?: string;
  defaultModelId: string;
  fallbackModelId?: string;
  useDirectOpenAIKey?: boolean;
  useDirectGeminiKey?: boolean;
  availableModels: Array<{
    id: string;
    name: string;
    description?: string;
    options?: {
      temperature?: number;
      max_completion_tokens?: number;
      stream?: boolean;
      [key: string]: any;
    };
  }>;
}

// Add type assertion to include all properties
const configJson = rawConfigJson as RawConfigJson;

// Default configuration for non-program settings
const defaultConfig: Partial<Config> = {
  showContextLink: true, // Set to false to hide the context link
  simpleMode: false, // Set to true to hide top panels when only one code and model
  greeting: "How can I help you?", // Default greeting message
  additionalContext: "", // Default empty additional context
  apiKeys: {
    // These are just placeholders, actual keys should be set in environment variables
    openai: process.env.OPENAI_API_KEY,
    gemini: process.env.GEMINI_API_KEY
  }
  // availableModels and defaultModelId are now loaded from config.json
};

/**
 * Get URL parameters in a server-safe way
 * @returns An object with URL parameters
 */
export function getUrlParams(): Record<string, string> {
  // This function is safe to call on both client and server
  if (typeof window === 'undefined') {
    // Server-side: no URL parameters available
    return {};
  }

  // Client-side: get URL parameters
  const params: Record<string, string> = {};
  const urlParams = new URLSearchParams(window.location.search);

  // Convert URLSearchParams to a simple object
  urlParams.forEach((value, key) => {
    params[key] = value;
  });

  return params;
}

/**
 * Load the configuration
 * @returns The configuration object
 */
export function loadConfig(): Config {
  // Get URL parameters
  const urlParams = getUrlParams();

  // Check for URL parameters that override config settings
  const urlGreeting = urlParams.greeting;
  const urlAdditionalContext = urlParams.context;

  // Merge with default config to ensure all fields are present
  return {
    ...defaultConfig,
    programs: configJson.programs,
    defaultProgram: configJson.defaultProgram,
    showContextLink: configJson.showContextLink !== undefined ? configJson.showContextLink : defaultConfig.showContextLink,
    simpleMode: configJson.simpleMode !== undefined ? configJson.simpleMode : defaultConfig.simpleMode,
    // Use URL parameter for greeting if available, otherwise use config or default
    greeting: urlGreeting || (configJson.greeting !== undefined ? configJson.greeting : defaultConfig.greeting),
    // Use URL parameter for additional context if available, otherwise use config or default
    additionalContext: urlAdditionalContext || (configJson.additionalContext !== undefined ? configJson.additionalContext : defaultConfig.additionalContext),
    defaultModelId: configJson.defaultModelId || 'gemini/gemini-2.0-flash',
    fallbackModelId: configJson.fallbackModelId, // Optional fallback model ID
    availableModels: configJson.availableModels || [],
    // Load the new flags, defaulting to true if not present in config.json
    useDirectOpenAIKey: configJson.useDirectOpenAIKey ?? true,
    useDirectGeminiKey: configJson.useDirectGeminiKey ?? true,
    apiKeys: defaultConfig.apiKeys || {}
  } as Config;
}

/**
 * Get a program by its ID or all programs if no ID is provided
 * @param programId The ID of the program (optional)
 * @returns The program object, all programs as a record, or undefined if not found
 */
export function getProgramById(programId?: string): Program | Record<string, Program> | undefined {
  const config = loadConfig();

  // If no programId is provided, return all programs as a record
  if (!programId) {
    const programsRecord: Record<string, Program> = {};
    config.programs.forEach(program => {
      programsRecord[program.id] = program;
    });
    return programsRecord;
  }

  // Otherwise, return the specific program
  return config.programs.find(program => program.id === programId);
}

/**
 * Get the default program
 * @returns The default program object
 */
export function getDefaultProgram(): Program {
  const config = loadConfig();
  const defaultProgram = config.programs.find(program => program.id === config.defaultProgram);
  return defaultProgram || config.programs[0];
}

/**
 * Parse a model ID in the format 'provider/model-name'
 * @param modelId The model ID to parse
 * @returns An object with provider and modelName properties
 */
export function parseModelId(modelId: string): { provider: string; modelName: string } {
  const parts = modelId.split('/');
  if (parts.length !== 2) {
    throw new Error(`Invalid model ID format: ${modelId}. Expected format: 'provider/model-name'`);
  }
  return {
    provider: parts[0],
    modelName: parts[1]
  };
}


