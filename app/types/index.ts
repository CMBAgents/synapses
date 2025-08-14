// Core configuration types
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
  fallbackModelId?: string | null; // Fallback model ID to use if the default model fails
  useDirectOpenAIKey?: boolean; // Flag to use direct OpenAI key if available
  useDirectGeminiKey?: boolean; // Flag to use direct Gemini key if available
  systemPrompt?: string; // Common system prompt template with placeholders
}

// Chat and messaging types
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

// Domain and library types
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

export type Domain = 'astronomy' | 'finance';

export interface ContextFile {
  name: string;
  content: string;
  domain: Domain;
}

// UI Component Props types
export interface BaseChatPageProps {
  domain: Domain;
  title: string;
  description: string;
  libraries: LibraryEntry[];
}

export interface BaseLeaderboardPageProps {
  domain: Domain;
  title: string;
  description: string;
  libraries: LibraryEntry[];
}

export interface ChatContainerProps {
  domain: Domain;
  title: string;
  description: string;
  libraries: LibraryEntry[];
  children?: React.ReactNode;
}

export interface ModelSelectorProps {
  selectedModelId: string;
  onModelChange: (modelId: string) => void;
  availableModels: ModelConfig[];
  className?: string;
}

export interface LibrarySelectorProps {
  libraries: LibraryEntry[];
  selectedLibrary: string | null;
  onLibrarySelect: (library: string) => void;
  className?: string;
}

export interface LibrarySearchProps {
  libraries: LibraryEntry[];
  onSearch: (query: string) => void;
  placeholder?: string;
  className?: string;
}

export interface LeaderboardTableProps {
  libraries: LibraryEntry[];
  domain: Domain;
  className?: string;
}

export interface ProgramTabsProps {
  programs: Program[];
  selectedProgram: string;
  onProgramSelect: (programId: string) => void;
  className?: string;
}

export interface ContextUpdaterProps {
  domain: Domain;
  onUpdate?: () => void;
  className?: string;
}

export interface CopyButtonProps {
  text: string;
  label?: string;
  className?: string;
  onCopy?: () => void;
}

export interface WelcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  content: React.ReactNode;
}

export interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
}

// API and utility types
export interface ProviderConfig {
  baseUrl: string;
  apiKey?: string;
  headers?: Record<string, string>;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// Domain configuration
export interface DomainConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
}
