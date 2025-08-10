'use client'

import { useState, useRef, useEffect } from 'react';
import { AiOutlineUser, AiOutlineRobot, AiOutlineSend, AiOutlineStop } from 'react-icons/ai';
import Markdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
// We'll handle syntax highlighting styles in globals.css
import { Message, ModelConfig } from '@/app/utils/types';
import ModelSelector from './model-selector';
import CopyButton from './copy-button';

export default function ChatSimple({
  programId,
  greeting,
  selectedModelId = '',
  libraries = []
}: {
  programId: string;
  greeting: string;
  selectedModelId?: string;
  libraries?: Array<{ 
    name: string; 
    description?: string;
    hasContextFile?: boolean;
    contextFileName?: string;
    github_url?: string;
    stars?: number;
    rank?: number;
  }>;
}) {
  // Use a ref to store messages for each program ID
  const messagesMapRef = useRef<Record<string, Message[]>>({});
  const [currentMessages, setCurrentMessages] = useState<Message[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedLibrary, setSelectedLibrary] = useState<string>("");
  const messageId = useRef(0);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Store the selected model ID for reference
  const selectedModelIdRef = useRef<string>(selectedModelId);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Create a ref for the greeting message to avoid hydration mismatches
  const greetingMessageRef = useRef<Message>({
    id: "greeting",
    role: "assistant",
    content: greeting,
    createdAt: new Date(0), // Use a consistent date initially
  });

  // Update the greeting message and load messages for the current program
  useEffect(() => {
    // Update greeting message
    greetingMessageRef.current = {
      id: "greeting",
      role: "assistant",
      content: greeting,
      createdAt: new Date()
    };

    // Load messages for the current program
    const programMessages = messagesMapRef.current[programId] || [];
    setCurrentMessages(programMessages);

    // Update the selected model ID reference
    selectedModelIdRef.current = selectedModelId;
  }, [programId, greeting, selectedModelId]);

  // Auto-resize the textarea when the component mounts or when prompt changes
  useEffect(() => {
    if (textareaRef.current) {
      // Reset height to auto to get the correct scrollHeight
      textareaRef.current.style.height = 'auto';
      // Set the height to scrollHeight to fit the content
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [prompt]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    // Add busy indicator
    setIsLoading(true);

    // Add user message to list of messages
    messageId.current++;
    // Create a timestamp once for this message
    const messageTimestamp = new Date();

    const userMessage = {
      id: messageId.current.toString(),
      role: "user",
      content: prompt,
      createdAt: messageTimestamp,
    };

    // Update current messages and store in the map
    const updatedMessages = [...currentMessages, userMessage];
    setCurrentMessages(updatedMessages);
    messagesMapRef.current[programId] = updatedMessages;
    setPrompt("");

    // Prepare messages for API
    const apiMessages = [
      ...currentMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      {
        role: userMessage.role,
        content: userMessage.content
      }
    ];

    try {
      // Use the unified API endpoint for all providers
      const apiEndpoint = '/api/unified-chat';

      console.log(`Using API endpoint: ${apiEndpoint} with model ID: ${selectedModelId || 'default'}`);

      // Get model options to check if streaming is enabled
      const configModule = await import('@/app/utils/config');
      const configData = configModule.loadConfig();
      const modelConfig = configData.availableModels.find(model => model.id === selectedModelId);
      const useStreaming = modelConfig?.options?.stream === true;

      // Create a new AbortController for this request
      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;

      // If streaming is enabled, set the streaming state
      if (useStreaming) {
        setIsStreaming(true);
      }

      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          programId,
          messages: apiMessages,
          modelId: selectedModelId, // Pass the selected model ID
          stream: useStreaming, // Pass streaming flag
        }),
        signal, // Pass the abort signal
      });

      // Check if the response is ok
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorDetails = errorData.details || '';
        const errorMessage = errorData.error || response.statusText;

        // Provide more specific error messages based on the error type
        if (errorMessage.includes('API key')) {
          throw new Error(`OpenAI API key error: ${errorDetails}`);
        } else if (errorMessage.includes('model')) {
          throw new Error(`Model configuration error: ${errorDetails}`);
        } else {
          throw new Error(`API responded with status ${response.status}: ${errorMessage}`);
        }
      }

      // Check if the response is a streaming response
      if (response.headers.get('Content-Type')?.includes('text/event-stream')) {
        // Handle streaming response
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('Failed to get reader from response');
        }

        // Create a new message for streaming content
        messageId.current++;
        const streamingMessageId = messageId.current.toString();
        let streamingContent = '';

        // Add an empty assistant message that will be updated
        setCurrentMessages(prevMessages => {
          const streamingMessage = {
            id: streamingMessageId,
            role: "assistant",
            content: "",
            createdAt: messageTimestamp,
          };
          const updatedMessages = [...prevMessages, streamingMessage];
          messagesMapRef.current[programId] = updatedMessages;
          return updatedMessages;
        });

        try {
          while (true) {
            let done = false;
            let value: Uint8Array | undefined;

            try {
              // This read operation might throw if the request is aborted
              const result = await reader.read();
              done = result.done;
              value = result.value;
            } catch (readError) {
              // If the error is due to abortion, we'll handle it gracefully
              if (signal.aborted) {
                console.log('Stream reading aborted by user');
                break;
              }
              // For other errors, rethrow
              throw readError;
            }

            if (done) break;

            // Check if the request has been aborted after a successful read
            if (signal.aborted) {
              console.log('Stream processing aborted by user after successful read');
              break;
            }

            // Decode the chunk and process it
            const chunk = decoder.decode(value, { stream: true });

            // Process the chunk (format: data: {...}\n\n)
            const lines = chunk.split('\n\n').filter(line => line.trim() !== '');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.substring(6);
                if (data === '[DONE]') continue;

                try {
                  const parsed = JSON.parse(data);
                  const content = parsed.choices?.[0]?.delta?.content || '';
                  if (content) {
                    streamingContent += content;

                    // Update the message with the new content
                    setCurrentMessages(prevMessages => {
                      const updatedMessages = prevMessages.map(msg =>
                        msg.id === streamingMessageId
                          ? { ...msg, content: streamingContent }
                          : msg
                      );
                      messagesMapRef.current[programId] = updatedMessages;
                      return updatedMessages;
                    });
                  }
                } catch (e) {
                  console.error('Error parsing stream chunk:', e);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      } else {
        // For non-streaming API, parse the JSON response
        const responseData = await response.json();

        // Extract the content from the response
        const finalContent = responseData.content || "No content received from API";

        // Add assistant message to list of messages
        messageId.current++;

        // Use the same timestamp for consistency
        const assistantMessage = {
          id: messageId.current.toString(),
          role: "assistant",
          content: finalContent,
          createdAt: messageTimestamp, // Reuse the same timestamp
        };

        // Update current messages and store in the map
        setCurrentMessages(prevMessages => {
          const updatedMessages = [...prevMessages, assistantMessage];
          messagesMapRef.current[programId] = updatedMessages;
          return updatedMessages;
        });
      }
    } catch (error) {
      console.error('Error in chat:', error);

      // Display error message to the user
      messageId.current++;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      // Create a timestamp for the error message
      const errorTimestamp = new Date();
      const errorAssistantMessage = {
        id: messageId.current.toString(),
        role: "assistant",
        content: `I'm sorry, there was an error processing your request: ${errorMessage}. Please try again later.`,
        createdAt: errorTimestamp,
      };

      // Update current messages and store in the map
      setCurrentMessages(prevMessages => {
        const updatedMessages = [...prevMessages, errorAssistantMessage];
        messagesMapRef.current[programId] = updatedMessages;
        return updatedMessages;
      });
    } finally {
      // Remove busy indicator and streaming state
      setIsLoading(false);
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }

  // Handles changes to the prompt input field
  function handlePromptChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setPrompt(e.target.value);

    // Auto-resize the textarea
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
  }

  // Handle key down events for the textarea
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    // If Enter is pressed without Shift, submit the form
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (prompt.trim().length > 0 && !isLoading) {
        const form = e.currentTarget.form;
        if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    }
  }

  // Handle cancellation of streaming response
  function handleCancelStream() {
    if (abortControllerRef.current) {
      // Add a message to the current streaming message indicating cancellation
      // This is done before aborting to ensure it's captured
      const streamingMessageId = messageId.current.toString();
      setCurrentMessages(prevMessages => {
        const updatedMessages = prevMessages.map(msg =>
          msg.id === streamingMessageId
            ? { ...msg, content: msg.content + "\n\n*Response cancelled by user*" }
            : msg
        );
        messagesMapRef.current[programId] = updatedMessages;
        return updatedMessages;
      });

      // Now abort the request
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
      // Keep isLoading true until the finally block in handleSubmit sets it to false
    }
  }

  // No longer need handleModelChange as the model selector is moved to the container

  return (
    <div className="flex flex-col h-full">
      {/* Chat messages area - scrollable */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {/* Library selector takes full space */}
        <div className="bg-gradient-to-br from-white/15 to-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/30 shadow-lg">
          <div className="flex items-center justify-between">
            {/* Library selector */}
            <div className="flex-1 mr-6">
              <label htmlFor="library-select" className="block text-sm font-semibold text-gray-800 dark:text-gray-100 mb-3 tracking-wide">
                Choose Library
              </label>
              <div className="relative">
                <select
                  id="library-select"
                  value={selectedLibrary}
                  onChange={(e) => setSelectedLibrary(e.target.value)}
                  className="w-full px-4 py-3 bg-white/40 backdrop-blur-sm border border-white/50 rounded-xl text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-white/60 focus:border-white/70 transition-all duration-300 hover:bg-white/50 hover:border-white/60 appearance-none cursor-pointer"
                >
                  <option value="">Select a library...</option>
                  {libraries.map((library, index) => (
                    <option key={index} value={library.name} className="py-2">
                      {library.name}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>
            
            {/* Selected library display */}
            {selectedLibrary && (
              <div className="bg-gradient-to-r from-white/25 to-white/15 backdrop-blur-sm rounded-xl p-4 border border-white/30 shadow-inner min-w-[250px]">
                <div className="flex items-center mb-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                  <div className="font-semibold text-gray-800 dark:text-gray-100 text-sm">
                    {selectedLibrary}
                  </div>
                </div>
                
                {/* GitHub Link */}
                <div className="flex items-center mb-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                  <a 
                    href={libraries.find(lib => lib.name === selectedLibrary)?.github_url || '#'}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-400 hover:text-blue-300 transition-colors cursor-pointer flex items-center"
                  >
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    GitHub
                  </a>
                </div>
                
                {/* Context File Link */}
                {libraries.find(lib => lib.name === selectedLibrary)?.hasContextFile && (
                  <div className="flex items-center mb-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    <a 
                      href={`/api/context/${programId === 'astronomy' ? 'astronomy' : 'finance'}/${libraries.find(lib => lib.name === selectedLibrary)?.contextFileName}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-green-400 hover:text-green-300 transition-colors cursor-pointer flex items-center"
                    >
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                        <path d="M14 2v6h6"/>
                        <path d="M16 13H8"/>
                        <path d="M16 17H8"/>
                        <path d="M10 9H8"/>
                      </svg>
                      View Context
                    </a>
                  </div>
                )}
                {!libraries.find(lib => lib.name === selectedLibrary)?.hasContextFile && (
                  <div className="flex items-center mb-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                    <span className="text-xs text-gray-300">No context available</span>
                  </div>
                )}
                
                {/* Description */}
                {libraries.find(lib => lib.name === selectedLibrary)?.description && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed mt-2">
                    {libraries.find(lib => lib.name === selectedLibrary)?.description}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
        
        {currentMessages.map(m =>
          <ChatMessage
            key={m.id}
            message={m}
          />
        )}
      </div>

      {/* Input panel - fixed at bottom */}
      <div className="bg-almond-beige/80 backdrop-blur-sm border-t border-white/20 p-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 z-10">
                <AiOutlineRobot className="w-5 h-5" />
              </div>
              <textarea
                ref={textareaRef}
                disabled={isLoading}
                autoFocus
                rows={1}
                className="w-full pl-10 pr-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-black dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none overflow-hidden min-h-[38px] focus:outline-none focus:ring-2 focus:ring-white/50"
                onChange={handlePromptChange}
                onKeyDown={handleKeyDown}
                value={prompt}
                placeholder={isLoading ? "Thinking..." : "How can I help you?"} />
            </div>
            {isLoading ? (
              isStreaming ? (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    handleCancelStream();
                  }}
                  className="px-6 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-black dark:text-white hover:bg-white/30 transition-colors duration-200"
                >
                  <ChatSpinner color="currentColor" />
                </button>
              ) : (
                <button
                  disabled
                  className="px-6 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-black dark:text-white"
                >
                  <ChatSpinner color="currentColor" />
                </button>
              )
            ) : (
              <button
                disabled={prompt.length === 0}
                className="px-6 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-black dark:text-white hover:bg-white/30 transition-colors duration-200 disabled:opacity-50"
              >
                <AiOutlineSend />
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}

function ChatMessage({ message }: { message: Message }) {
  function displayRole(roleName: string) {
    switch (roleName) {
      case "user":
        return <AiOutlineUser className="text-gray-600 dark:text-gray-300" />;
      case "assistant":
        return <AiOutlineRobot className="text-gray-600 dark:text-gray-300" />;
      default:
        return null;
    }
  }

  const isUser = message.role === "user";

  // Process content to preserve line breaks in user messages
  // For user messages, ensure single line breaks are preserved by adding two spaces at the end of each line
  const processedContent = isUser
    ? message.content.split('\n').join('  \n')
    : message.content;

  return (
    <div className={`flex rounded-lg text-gray-700 dark:text-gray-200 px-3 sm:px-4 py-3 my-2 shadow-sm border ${isUser ? 'bg-blue-50 border-blue-100 dark:bg-blue-900 dark:border-blue-800' : 'bg-white/20 backdrop-blur-sm border-white/30 dark:bg-gray-800/20 dark:border-gray-700'}`}>
      <div className="text-2xl sm:text-3xl flex-shrink-0 flex items-start pt-1">
        {displayRole(message.role)}
      </div>
      <div className="ml-2 sm:mx-3 text-left w-full overflow-hidden prose dark:prose-invert max-w-none">
        <Markdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeRaw, rehypeHighlight, rehypeKatex]}
            components={{
              code(props) {
                const { node, inline, className, children } = props as {
                  node?: any;
                  inline?: boolean;
                  className?: string;
                  children: React.ReactNode;
                };
                // We're not using the language match but keeping it for future reference
                // const match = /language-(\w+)/.exec(className || '');

                // Extract text for copy button
                const extractText = (node: any): string => {
                  if (typeof node === 'string') return node;
                  if (Array.isArray(node)) return node.map(extractText).join('');
                  if (node && typeof node === 'object' && 'props' in node) {
                    return extractText(node.props?.children || '');
                  }
                  return '';
                };

                // For inline code, keep it simple
                if (inline) {
                  return <code className={`${className} inline-code`} {...props}>{children}</code>;
                }

                // For code blocks, check if it's inside a pre tag
                // This is the most reliable way to identify actual code blocks vs standalone code tags
                const isInPreTag = node &&
                  'parentNode' in node &&
                  node.parentNode &&
                  'tagName' in node.parentNode &&
                  node.parentNode.tagName &&
                  node.parentNode.tagName.toLowerCase() === 'pre';

                if (isInPreTag) {
                  // For actual code blocks (inside pre tags), add copy button
                  return (
                    <>
                      <code className={className} {...props}>{children}</code>
                      <CopyButton text={extractText(children)} />
                    </>
                  );
                } else {
                  // For standalone code tags that aren't inline (rare case), just render the code
                  return <code className={className} {...props}>{children}</code>;
                }
              }
            }}
          >
            {processedContent}
        </Markdown>
      </div>
    </div>
  );
}

function ChatSpinner({ color = "currentColor" }: { color?: string }) {
  return (
    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke={color} strokeWidth="4"></circle>
      <path className="opacity-75" fill={color} d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  );
}
