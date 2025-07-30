export interface ModelConfig {
  id: string; // Unique identifier for the model (in litellm format: provider/model-name)
  name: string; // Display name for the model
  description?: string; // Optional description of the model
  options?: {
    temperature?: number; // Model temperature (0-1)
    max_completion_tokens?: number; // Maximum number of tokens to generate
    [key: string]: any; // Allow for additional model-specific options
  };
}

export interface Program {
  id: string;
  name: string;
  description: string;
  contextFiles: string[]; // Can be empty if combinedContextFile is a URL
  contextFile?: string; // For backward compatibility
  combinedContextFile?: string; // Name of the combined context file for download or a URL to fetch context from
  docsUrl: string;
  extraSystemPrompt?: string; // Additional program-specific system prompt instructions
}

export interface Config {
  programs: Program[];
  defaultProgram: string;
  showContextLink?: boolean;
  simpleMode?: boolean; // Flag to hide top panels when only one code and model
  greeting?: string; // Global greeting message to display in chat
  additionalContext?: string; // Additional context string to add to the system prompt
  apiKeys?: {
    openai?: string;
    gemini?: string;
  };
  availableModels: ModelConfig[]; // List of available models
  defaultModelId: string; // Default model ID to use
  fallbackModelId?: string; // Fallback model ID to use if the default model fails
  useDirectOpenAIKey?: boolean; // Flag to use direct OpenAI key if available
  useDirectGeminiKey?: boolean; // Flag to use direct Gemini key if available
  systemPrompt?: string; // Common system prompt template with placeholders
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | string;
  content: string;
  createdAt: Date;
}

export interface ChatState {
  messages: Message[];
  threadId?: string;
  selectedModelId?: string; // The ID of the selected model
}
