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
  selectedModelId = ''
}: {
  programId: string;
  greeting: string;
  selectedModelId?: string;
}) {
  // Use a ref to store messages for each program ID
  const messagesMapRef = useRef<Record<string, Message[]>>({});
  const [currentMessages, setCurrentMessages] = useState<Message[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
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
    <div className="flex flex-col bg-white dark:bg-gray-800">
      <div className="p-2">
        <ChatMessage
          message={greetingMessageRef.current}
        />
        {currentMessages.map(m =>
          <ChatMessage
            key={m.id}
            message={m}
          />
        )}
      </div>
      <div className="p-2 border-t border-gray-300 dark:border-gray-700">
        {/* Chat input form */}
        <form onSubmit={handleSubmit} className="flex">
          <textarea
            ref={textareaRef}
            disabled={isLoading}
            autoFocus
            rows={1}
            className="border border-gray-300 dark:border-gray-700 rounded w-full py-2 px-3 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 resize-none overflow-hidden min-h-[38px]"
            onChange={handlePromptChange}
            onKeyDown={handleKeyDown}
            value={prompt}
            placeholder={isLoading ? "Thinking..." : "Ask a question..."} />
          {isLoading ? (
            isStreaming ? (
              <button
                onClick={(e) => {
                  e.preventDefault();
                  handleCancelStream();
                }}
                className="ml-2 bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded focus:outline-none"
              >
                <ChatSpinner color="white" />
              </button>
            ) : (
              <button
                disabled
                className="ml-2 bg-blue-500 text-white font-bold py-2 px-4 rounded focus:outline-none"
              >
                <ChatSpinner color="white" />
              </button>
            )
          ) : (
            <button
              disabled={prompt.length === 0}
              className="ml-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none"
            >
              <AiOutlineSend />
            </button>
          )}
        </form>
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
    <div className={`flex rounded-lg text-gray-700 dark:text-gray-200 px-3 sm:px-4 py-3 my-2 shadow-sm border ${isUser ? 'bg-blue-50 border-blue-100 dark:bg-blue-900 dark:border-blue-800' : 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'}`}>
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
