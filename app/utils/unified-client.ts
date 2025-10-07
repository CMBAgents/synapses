/**
 * Unified client for different LLM providers using the OpenAI API format
 */
import OpenAI from 'openai';
import { parseModelId, loadConfig } from './config';
import { writeFileSync, unlinkSync } from 'fs';
import { join } from 'path';
import { randomBytes } from 'crypto';
import { tmpdir } from 'os';
import { getBestProvider, recordProviderResult, initializeProviderHealth } from './provider-health';

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
    defaultModel: 'gemini-2.5-flash',
    isVertexAI: true
  },
  deepseek: {
    baseURL: 'https://api.deepseek.com/v1',
    apiKeyEnvVar: 'DEEPSEEK_API_KEY',
    defaultModel: 'deepseek-chat'
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

// Utility function to decrypt sensitive data (server-side)
async function decryptData(encryptedData: string, key: string): Promise<string> {
  try {
    const crypto = require('crypto');
    
    // Convert from base64
    const combined = Buffer.from(encryptedData, 'base64');
    
    // Extract IV and encrypted data
    const iv = combined.slice(0, 12);
    const encryptedBuffer = combined.slice(12);
    
    // Create decipher
    const decipher = crypto.createDecipher('aes-256-gcm', key);
    decipher.setAuthTag(encryptedBuffer.slice(-16));
    
    // Decrypt
    let decrypted = decipher.update(encryptedBuffer.slice(0, -16), null, 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Failed to decrypt credentials');
  }
}

// Utility function to detect if data is encrypted
function isEncrypted(data: string): boolean {
  try {
    // Check if it's base64 encoded and has the right structure
    const buffer = Buffer.from(data, 'base64');
    return buffer.length > 28; // IV (12) + minimum encrypted data (16)
  } catch {
    return false;
  }
}

// Secure credential processing
async function processCredentials(credentials: Record<string, Record<string, string>>, modelId: string): Promise<Record<string, string>> {
  const processedCredentials: Record<string, string> = {};
  
  if (!credentials || !credentials[modelId]) {
    return processedCredentials;
  }
  
  const modelCredentials = credentials[modelId];
  
  // Process each credential field
  for (const [key, value] of Object.entries(modelCredentials)) {
    if (value) {
      // Check if the value is encrypted
      if (isEncrypted(value)) {
        try {
          // For now, we'll use a simple approach - in production, you'd want to pass the encryption key securely
          // This is a simplified version - in a real implementation, you'd need to securely pass the encryption key
          const decryptedValue = await decryptData(value, process.env.ENCRYPTION_KEY || 'fallback-key');
          processedCredentials[key] = decryptedValue;
        } catch (error) {
          console.error(`Failed to decrypt ${key}:`, error);
          // Fall back to treating it as unencrypted
          processedCredentials[key] = value;
        }
      } else {
        processedCredentials[key] = value;
      }
    }
  }
  
  return processedCredentials;
}

/**
 * Create an OpenAI client configured for the specified model ID
 * @param modelId The model ID in the format "provider/model-name"
 * @returns An OpenAI client configured for the specified provider
 */
export async function createClient(modelId?: string, credentials?: Record<string, Record<string, string>>) {
  const config = loadConfig();

  // Default to the configuration's default model if no model ID is provided
  const modelIdToUse = modelId || config.defaultModelId;

  // Parse the model ID to get the provider and model name
  const { provider, modelName } = parseModelId(modelIdToUse);

  // Find the model configuration to get the credentialType
  const modelConfig = config.availableModels.find(m => m.id === modelIdToUse);
  const credentialType = modelConfig?.credentialType;

  // Determine target provider based on credentialType (takes precedence) or routing strategy
  // The credentialType in config.json explicitly tells us which provider to use
  let targetProviderKey: string;
  
  if (credentialType) {
    // If credentialType is specified in config.json, use it to determine the provider
    // This ensures models like "deepseek/deepseek-chat-v3-0324" with credentialType="openrouter"
    // will use OpenRouter and OPEN_ROUTER_KEY, not the direct DeepSeek API
    targetProviderKey = credentialType;
    console.log(`Using provider from credentialType: ${credentialType} for model ${modelIdToUse}`);
  } else if (provider === 'openrouter') {
    // For OpenRouter models without explicit credentialType, use adaptive routing
    targetProviderKey = getBestProvider(provider);
    console.log(`Adaptive routing for ${provider}: selected=${targetProviderKey}`);
  } else {
    // For specific providers (vertexai, openai, gemini, etc.), use the requested provider directly
    // Check if the provider exists in our config
    if (PROVIDER_CONFIGS[provider]) {
      targetProviderKey = provider;
      console.log(`Using requested provider: ${provider}`);
    } else {
      // Unknown provider, fallback to openrouter
      console.warn(`Unknown provider: ${provider}, falling back to openrouter`);
      targetProviderKey = 'openrouter';
    }
  }

  const providerConfig = PROVIDER_CONFIGS[targetProviderKey as keyof typeof PROVIDER_CONFIGS];
  if (!providerConfig) {
    throw new Error(`Provider configuration not found for: ${targetProviderKey}`);
  }
  const apiKeyEnvVar = providerConfig.apiKeyEnvVar;
  
  // Process credentials securely
  const processedCredentials = await processCredentials(credentials || {}, modelIdToUse);
  
  // For Vertex AI, we need to check for Google Cloud credentials
  let apiKey: string | undefined;
  
  // First check if credentials were provided for this specific model
  if (processedCredentials && Object.keys(processedCredentials).length > 0) {
    if (targetProviderKey === 'vertexai') {
      // For Vertex AI, check if we have the required credentials
      if (processedCredentials.projectId && processedCredentials.location && processedCredentials.serviceAccountKey) {
        // Create a temporary file for the service account key
        const tempFile = join(tmpdir(), `service-account-${randomBytes(8).toString('hex')}.json`);
        
        try {
          // Write the service account key to a temporary file
          writeFileSync(tempFile, processedCredentials.serviceAccountKey);
          
          // Store credentials in environment for this request
          process.env.GOOGLE_CLOUD_PROJECT = processedCredentials.projectId;
          process.env.VERTEX_AI_LOCATION = processedCredentials.location;
          process.env.GOOGLE_APPLICATION_CREDENTIALS = tempFile;
          apiKey = processedCredentials.projectId; // Use project ID as the key identifier
          
          // Schedule cleanup of the temporary file
          setTimeout(() => {
            try {
              unlinkSync(tempFile);
            } catch (error) {
              console.error('Failed to cleanup temporary service account file:', error);
            }
          }, 60000); // Clean up after 1 minute
          
        } catch (error) {
          console.error('Failed to create temporary service account file:', error);
          throw new Error('Failed to process Google Cloud credentials');
        }
      }
    } else if (targetProviderKey === 'openai' || targetProviderKey === 'deepseek') {
      // For OpenAI/DeepSeek, use the API key
      if (processedCredentials.apiKey) {
        apiKey = processedCredentials.apiKey;
      }
    }
  }
  
  // Fallback to environment variables if no credentials provided
  if (!apiKey) {
    if (targetProviderKey === 'vertexai') {
      // Check for Google Cloud credentials
      apiKey = process.env.GOOGLE_APPLICATION_CREDENTIALS || 
                process.env.GOOGLE_CLOUD_PROJECT || 
                process.env.GOOGLE_ACCESS_TOKEN;
    } else {
      apiKey = process.env[apiKeyEnvVar];
    }
  }

  // Determine actual provider and model name for the API call
  const actualProvider = targetProviderKey;
  
  // Determine the model name to use based on the target provider
  let actualModelName: string;
  if (targetProviderKey === 'openrouter') {
    // OpenRouter needs the full modelId (e.g., "deepseek/deepseek-chat-v3-0324")
    actualModelName = modelIdToUse;
  } else if (targetProviderKey === provider) {
    // Using the requested provider directly, use just the model name
    actualModelName = modelName;
  } else {
    // Provider switched (e.g., from deepseek to openrouter), use the full modelId
    // This handles fallback cases where we route to a different provider
    actualModelName = modelIdToUse;
  }

  // Log the decision (without sensitive data)
  console.log(`Provider routing: requested=${provider}, target=${targetProviderKey}, model=${actualModelName}`);

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
  options: Record<string, any> = {},
  credentials?: Record<string, Record<string, string>>,
  modelId?: string
) {
  try {
    // Import Vertex AI Generative AI client
    const { VertexAI } = await import('@google-cloud/vertexai');
    
    // Get credentials for this specific model using the full modelId
    const modelCredentials = modelId ? credentials?.[modelId] : credentials?.[`vertexai/${modelName}`];
    
    console.log('Vertex AI credentials debug:', {
      modelName,
      modelId,
      hasCredentials: !!credentials,
      credentialKeys: credentials ? Object.keys(credentials) : [],
      modelCredentials,
      serviceAccountKey: modelCredentials?.serviceAccountKey ? 'Present' : 'Missing',
      envProjectId: process.env.GOOGLE_CLOUD_PROJECT,
      envLocation: process.env.VERTEX_AI_LOCATION,
      envCredentials: process.env.GOOGLE_APPLICATION_CREDENTIALS ? 'Present' : 'Missing'
    });
    
    // Check if we have complete user credentials
    const hasCompleteUserCredentials = modelCredentials?.projectId && 
                                    modelCredentials?.location && 
                                    modelCredentials?.serviceAccountKey;
    
    if (!hasCompleteUserCredentials) {
      console.log('Incomplete user credentials, falling back to environment variables');
      
      // Check if environment variables are available
      if (!process.env.GOOGLE_CLOUD_PROJECT || !process.env.GOOGLE_APPLICATION_CREDENTIALS) {
        throw new Error('Vertex AI credentials not provided and environment variables are not configured. Please provide credentials or set GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS.');
      }
      
      // Use environment variables
      const vertexAI = new VertexAI({
        project: process.env.GOOGLE_CLOUD_PROJECT,
        location: process.env.VERTEX_AI_LOCATION || 'us-central1',
      });
      
      // Get the generative model
      const model = vertexAI.preview.getGenerativeModel({
        model: modelName,
      });
      
      // Convert messages to the format expected by Gemini
      const geminiMessages = messages.map(msg => ({
        role: msg.role === 'system' ? 'user' : msg.role, // Gemini doesn't support system role
        parts: [{ text: msg.content }]
      }));
      
      // Generate content
      const result = await model.generateContent({
        contents: geminiMessages,
      });
      
      const response = result.response;
      const content = response.candidates?.[0]?.content?.parts?.[0]?.text || '';
      
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
    }
    
    // Use user-provided credentials
    console.log('Using user-provided credentials');
    
    // Parse the service account key
    const serviceAccountKey = JSON.parse(modelCredentials.serviceAccountKey);
    
    // Create a temporary file for the service account key
    const tempFileName = `temp-credentials-${randomBytes(8).toString('hex')}.json`;
    const tempFilePath = join(tmpdir(), tempFileName);
    
    console.log('Creating temporary credentials file:', tempFilePath);
    
    // Write the service account key to the temporary file
    writeFileSync(tempFilePath, modelCredentials.serviceAccountKey);
    
    // Set the credentials in the environment temporarily for this request
    const originalCredentials = process.env.GOOGLE_APPLICATION_CREDENTIALS;
    const originalProject = process.env.GOOGLE_CLOUD_PROJECT;
    const originalLocation = process.env.VERTEX_AI_LOCATION;
    
    try {
      // Set environment variables for this request
      process.env.GOOGLE_APPLICATION_CREDENTIALS = tempFilePath;
      process.env.GOOGLE_CLOUD_PROJECT = modelCredentials.projectId;
      process.env.VERTEX_AI_LOCATION = modelCredentials.location;
      
      // Re-initialize the client with the updated environment
      const vertexAIWithCredentials = new VertexAI({
        project: modelCredentials.projectId,
        location: modelCredentials.location,
      });
      
      // Get the generative model
      const model = vertexAIWithCredentials.preview.getGenerativeModel({
        model: modelName,
      });
      
      // Convert messages to the format expected by Gemini
      const geminiMessages = messages.map(msg => ({
        role: msg.role === 'system' ? 'user' : msg.role, // Gemini doesn't support system role
        parts: [{ text: msg.content }]
      }));
      
      // Generate content
      const result = await model.generateContent({
        contents: geminiMessages,
      });
      
      const response = result.response;
      const content = response.candidates?.[0]?.content?.parts?.[0]?.text || '';
      
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
    } finally {
      // Restore original environment variables
      process.env.GOOGLE_APPLICATION_CREDENTIALS = originalCredentials;
      process.env.GOOGLE_CLOUD_PROJECT = originalProject;
      process.env.VERTEX_AI_LOCATION = originalLocation;
      
      // Clean up the temporary file
      try {
        unlinkSync(tempFilePath);
        console.log('Temporary credentials file cleaned up:', tempFilePath);
      } catch (cleanupError) {
        console.warn('Failed to clean up temporary credentials file:', cleanupError);
      }
    }
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
  options: Record<string, any> = {},
  credentials?: Record<string, Record<string, string>>
) {
  const startTime = Date.now();
  const { provider } = modelId ? parseModelId(modelId) : { provider: 'unknown' };
  
  try {
    // Create the client for the specified model
    const { client, modelName, isVertexAI } = await createClient(modelId, credentials);

    // Handle Vertex AI separately
    if (isVertexAI) {
      const result = await createVertexAIChatCompletion(modelName, messages, options, credentials, modelId);
      const responseTime = Date.now() - startTime;
      recordProviderResult(provider, true, responseTime);
      return result;
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

    // Log the final options for debugging
    console.log(`Creating chat completion for ${modelName} with options:`, completionOptions);

    // Ensure client exists before using it
    if (!client) {
      throw new Error('Client not available for chat completion');
    }

    // Create the completion
    const result = await client.chat.completions.create(completionOptions);
    const responseTime = Date.now() - startTime;
    recordProviderResult(provider, true, responseTime);
    return result;
    
  } catch (error) {
    const responseTime = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    recordProviderResult(provider, false, responseTime, errorMessage);
    throw error;
  }
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
  options: Record<string, any> = {},
  credentials?: Record<string, Record<string, string>>
) {
  const startTime = Date.now();
  const { provider } = modelId ? parseModelId(modelId) : { provider: 'unknown' };
  
  try {
    // Create the client for the specified model
    const { client, modelName, isVertexAI } = await createClient(modelId, credentials);

    // Handle Vertex AI separately (note: Vertex AI streaming is more complex)
    if (isVertexAI) {
      // For now, return a non-streaming response wrapped in a stream-like format
      const response = await createVertexAIChatCompletion(modelName, messages, options, credentials, modelId);
      const responseTime = Date.now() - startTime;
      recordProviderResult(provider, true, responseTime);
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

    // Log the streaming request and options
    console.log(`Creating streaming completion for ${provider}/${modelName}`);
    console.log(`Streaming options:`, completionOptions);

    // Ensure client exists before using it
    if (!client) {
      throw new Error('Client not available for streaming completion');
    }
    
    // Create the streaming completion
    const stream = await client.chat.completions.create(completionOptions);
    console.log('Stream created successfully');
    
    // Record successful stream creation
    const responseTime = Date.now() - startTime;
    recordProviderResult(provider, true, responseTime);
    
    return stream;
  } catch (error) {
    const responseTime = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    recordProviderResult(provider, false, responseTime, errorMessage);
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
