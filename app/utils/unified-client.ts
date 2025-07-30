/**
 * Unified client for different LLM providers using the OpenAI API format
 */
import OpenAI from 'openai';
import { parseModelId, loadConfig } from './config';

// Provider configuration interface
interface ProviderConfig {
  baseURL?: string;
  apiKeyEnvVar: string;
  defaultModel: string;
  defaultHeaders?: Record<string, string>;
}

// Map of provider types to their configurations
const PROVIDER_CONFIGS: Record<string, ProviderConfig> = {
  openai: {
    apiKeyEnvVar: 'OPENAI_API_KEY',
    defaultModel: 'gpt-4.1-mini-2025-04-14'
  },
  gemini: {
    baseURL: 'https://generativelanguage.googleapis.com/v1beta/openai/',
    apiKeyEnvVar: 'GEMINI_API_KEY',
    defaultModel: 'gemini-2.0-flash'
  },
  // We'll keep SambaNova support but not add it to the default config due to context limitations
  sambanova: {
    baseURL: 'https://api.sambanova.ai/v1/',
    apiKeyEnvVar: 'SAMBA_NOVA_API_KEY',
    defaultModel: 'DeepSeek-V3-0324'
  },
  openrouter: {
    baseURL: 'https://openrouter.ai/api/v1',
    apiKeyEnvVar: 'OPEN_ROUTER_KEY',
    defaultModel: 'deepseek/deepseek-chat-v3-0324'
  }
  // Default fallback for unknown providers will be OpenRouter
};

/**
 * Create an OpenAI client configured for the specified model ID
 * @param modelId The model ID in the format "provider/model-name"
 * @returns An OpenAI client configured for the specified provider
 */
export function createClient(modelId?: string) {
  const config = loadConfig();

  // Default to the configuration's default model if no model ID is provided
  const modelIdToUse = modelId || config.defaultModelId;

  // Parse the model ID to get the provider and model name
  const { provider, modelName } = parseModelId(modelIdToUse);

  // Determine the target provider configuration based on flags and availability
  let targetProviderKey: keyof typeof PROVIDER_CONFIGS = 'openrouter'; // Default to OpenRouter

  if (provider === 'openai' && config.useDirectOpenAIKey) {
    targetProviderKey = 'openai';
  } else if (provider === 'gemini' && config.useDirectGeminiKey) {
    targetProviderKey = 'gemini';
  } else if (provider === 'sambanova') {
    targetProviderKey = 'sambanova';
  } else if (PROVIDER_CONFIGS[provider]) {
    // Handle cases where a known provider (like 'openrouter') is explicitly requested
    // or when direct keys for openai/gemini are disabled/missing.
    targetProviderKey = provider as keyof typeof PROVIDER_CONFIGS;
    // If the provider isn't in PROVIDER_CONFIGS, targetProviderKey remains 'openrouter'
    if (!PROVIDER_CONFIGS[targetProviderKey]) {
        targetProviderKey = 'openrouter';
    }
  }
  // For unknown providers, targetProviderKey remains 'openrouter'

  const providerConfig = PROVIDER_CONFIGS[targetProviderKey];
  const apiKeyEnvVar = providerConfig.apiKeyEnvVar;
  const apiKey = process.env[apiKeyEnvVar];

  // Determine actual provider and model name for the API call
  const actualProvider = targetProviderKey;
  // Use the original modelId for OpenRouter, otherwise just the modelName
  const actualModelName = (targetProviderKey === 'openrouter') ? modelIdToUse : modelName;

  // Log the decision
  if (targetProviderKey !== 'openrouter' && (provider === targetProviderKey)) {
      console.log(`Attempting to use direct ${targetProviderKey} key for model: ${actualModelName}`);
  } else {
      console.log(`Using OpenRouter for model: ${actualModelName}`);
  }

  // Check API key
  if (!apiKey) {
    throw new Error(`API key not configured for the selected provider (${actualProvider}). Please set the ${apiKeyEnvVar} environment variable.`);
  }

  // Create the OpenAI client with the provider-specific configuration
  const clientConfig: any = {
    apiKey,
    baseURL: providerConfig.baseURL,
    dangerouslyAllowBrowser: true // Required for edge runtime
  };

  // Add default headers if specified
  if (providerConfig.defaultHeaders) {
    clientConfig.defaultHeaders = providerConfig.defaultHeaders;
  }

  const client = new OpenAI(clientConfig);

  return {
    client,
    provider: actualProvider,
    modelName: actualModelName,
    modelId: modelIdToUse
  };
}

/**
 * Get the model options for a specific model ID
 * @param modelId The model ID in the format "provider/model-name"
 * @returns The model options from the configuration
 */
export function getModelOptions(modelId?: string) {
  const config = loadConfig();

  // Default to the configuration's default model if no model ID is provided
  const modelIdToUse = modelId || config.defaultModelId;

  // Find the model in the configuration
  const modelConfig = config.availableModels.find(model => model.id === modelIdToUse);
  if (!modelConfig) {
    console.warn(`Model ${modelIdToUse} not found in configuration. Using default options.`);
    return {};
  }

  return modelConfig.options || {};
}

/**
 * Create a chat completion with the specified model
 * @param modelId The model ID in the format "provider/model-name"
 * @param messages The chat messages
 * @param options Additional options for the completion
 * @returns The completion response
 */
export async function createChatCompletion(
  modelId: string | undefined,
  messages: Array<{ role: string; content: string }>,
  options: Record<string, any> = {}
) {
  // Create the client for the specified model
  const { client, modelName } = createClient(modelId);

  // Get the model options from the configuration
  const modelOptions = getModelOptions(modelId);

  // Merge the model options with the provided options
  const completionOptions: any = {
    model: modelName,
    messages,
    ...modelOptions,
    ...options
  };

  // Create the completion
  return client.chat.completions.create(completionOptions);
}

/**
 * Create a streaming chat completion with the specified model
 * @param modelId The model ID in the format "provider/model-name"
 * @param messages The chat messages
 * @param options Additional options for the completion
 * @returns A ReadableStream of the completion response
 */
export async function createStreamingChatCompletion(
  modelId: string | undefined,
  messages: Array<{ role: string; content: string }>,
  options: Record<string, any> = {}
) {
  // Create the client for the specified model
  const { client, modelName, provider } = createClient(modelId);

  // Get the model options from the configuration
  const modelOptions = getModelOptions(modelId);

  // Merge the model options with the provided options and ensure streaming is enabled
  const completionOptions: any = {
    model: modelName,
    messages,
    ...modelOptions,
    ...options,
    stream: true
  };

  // Log the streaming request
  console.log(`Creating streaming completion for ${provider}/${modelName}`);

  try {
    // Create the streaming completion
    const stream = await client.chat.completions.create(completionOptions);
    console.log('Stream created successfully');
    return stream;
  } catch (error) {
    console.error('Error creating streaming completion:', error);
    throw error;
  }
}

/**
 * Log token usage for a completion
 * @param modelId The model ID
 * @param programId The program ID
 * @param usage The token usage information
 */
export function logTokenUsage(
  modelId: string | undefined,
  programId: string | undefined,
  usage: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number }
) {
  if (!usage) return;

  const { provider, modelName } = modelId ? parseModelId(modelId) : { provider: 'unknown', modelName: 'unknown' };

  console.log(`Token usage for ${provider}/${modelName} (${programId || 'unknown'}):`, {
    promptTokens: usage.prompt_tokens || 0,
    completionTokens: usage.completion_tokens || 0,
    totalTokens: usage.total_tokens || 0
  });
}
