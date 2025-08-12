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
  isVertexAI?: boolean; // Flag to identify Vertex AI provider
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
  vertexai: {
    apiKeyEnvVar: 'GOOGLE_APPLICATION_CREDENTIALS',
    defaultModel: 'gemini-1.5-flash',
    isVertexAI: true
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
  } else if (provider === 'vertexai') {
    targetProviderKey = 'vertexai';
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
  
  // For Vertex AI, we need to check for Google Cloud credentials
  let apiKey: string | undefined;
  if (targetProviderKey === 'vertexai') {
    // Check for Google Cloud credentials
    apiKey = process.env.GOOGLE_APPLICATION_CREDENTIALS || 
              process.env.GOOGLE_CLOUD_PROJECT || 
              process.env.GOOGLE_ACCESS_TOKEN;
  } else {
    apiKey = process.env[apiKeyEnvVar];
  }

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
    if (targetProviderKey === 'vertexai') {
      throw new Error(`Google Cloud credentials not configured for Vertex AI. Please set one of: GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT, or GOOGLE_ACCESS_TOKEN environment variable.`);
    } else {
      throw new Error(`API key not configured for the selected provider (${actualProvider}). Please set the ${apiKeyEnvVar} environment variable.`);
    }
  }

  // For Vertex AI, we need to use a different approach since it doesn't use OpenAI API format
  if (targetProviderKey === 'vertexai') {
    // Return a special client object for Vertex AI
    return {
      client: null, // Will be handled specially in the completion functions
      provider: actualProvider,
      modelName: actualModelName,
      modelId: modelIdToUse,
      isVertexAI: true
    };
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
 * Create a chat completion with Vertex AI
 * @param modelName The Vertex AI model name
 * @param messages The chat messages
 * @param options Additional options for the completion
 * @returns The completion response
 */
async function createVertexAIChatCompletion(
  modelName: string,
  messages: Array<{ role: string; content: string }>,
  options: Record<string, any> = {}
) {
  try {
    // Import Vertex AI client dynamically to avoid issues in edge runtime
    const { PredictionServiceClient } = await import('@google-cloud/aiplatform');
    
    // Initialize the client
    const client = new PredictionServiceClient({
      apiEndpoint: process.env.VERTEX_AI_ENDPOINT || 'us-central1-aiplatform.googleapis.com',
      projectId: process.env.GOOGLE_CLOUD_PROJECT,
    });

    // Convert messages to Vertex AI format
    const vertexMessages = messages.map(msg => ({
      role: msg.role === 'system' ? 'user' : msg.role, // Vertex AI doesn't support system role
      content: msg.content
    }));

    // Create the request
    const request = {
      endpoint: `projects/${process.env.GOOGLE_CLOUD_PROJECT}/locations/${process.env.VERTEX_AI_LOCATION || 'us-central1'}/publishers/google/models/${modelName}`,
      instances: [{
        messages: vertexMessages
      }],
      parameters: {
        temperature: options.temperature || 0.7,
        maxOutputTokens: options.max_completion_tokens || 4096,
        topP: options.top_p || 0.8,
        topK: options.top_k || 40
      }
    };

    // Make the prediction
    const [response] = await client.predict(request);
    
    // Extract the response content
    const prediction = response.predictions?.[0];
    if (!prediction) {
      throw new Error('No prediction received from Vertex AI');
    }

    // Convert Vertex AI response to OpenAI format
    const content = prediction.structValue?.fields?.candidates?.listValue?.values?.[0]?.structValue?.fields?.content?.stringValue || '';
    
    return {
      choices: [{
        message: {
          role: 'assistant',
          content: content
        },
        finish_reason: 'stop'
      }],
      usage: {
        prompt_tokens: 0, // Vertex AI doesn't provide token usage in this format
        completion_tokens: 0,
        total_tokens: 0
      }
    };
  } catch (error) {
    console.error('Error creating Vertex AI completion:', error);
    throw error;
  }
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
  const { client, modelName, isVertexAI } = createClient(modelId);

  // Handle Vertex AI separately
  if (isVertexAI) {
    return createVertexAIChatCompletion(modelName, messages, options);
  }

  // Get the model options from the configuration
  const modelOptions = getModelOptions(modelId);

  // Merge the model options with the provided options
  const completionOptions: any = {
    model: modelName,
    messages,
    ...modelOptions,
    ...options
  };

  // Ensure client exists before using it
  if (!client) {
    throw new Error('Client not available for chat completion');
  }

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
  const { client, modelName, provider, isVertexAI } = createClient(modelId);

  // Handle Vertex AI separately (note: Vertex AI streaming is more complex)
  if (isVertexAI) {
    // For now, return a non-streaming response wrapped in a stream-like format
    const response = await createVertexAIChatCompletion(modelName, messages, options);
    return {
      ...response,
      // Create a simple stream-like interface
      [Symbol.asyncIterator]: async function* () {
        yield response;
      }
    };
  }

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
    // Ensure client exists before using it
    if (!client) {
      throw new Error('Client not available for streaming completion');
    }
    
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
