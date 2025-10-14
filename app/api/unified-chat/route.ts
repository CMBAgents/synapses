import { NextRequest } from 'next/server';
import { loadContext, getSystemPromptWithContext } from '@/app/utils/context';
import { getProgramById, loadConfig } from '@/app/utils/config';
import { createChatCompletion, createStreamingChatCompletion, logTokenUsage } from '@/app/utils/unified-client';
import { credentialRateLimiter, sanitizeLogData } from '@/app/utils/security';
import { initializeProviderHealth } from '@/app/utils/provider-health';
import { spawn } from 'child_process';
import path from 'path';

// This enables Node.js runtime for Google Cloud compatibility
export const runtime = "nodejs";

// Initialize provider health monitoring on first load
let healthInitialized = false;
if (!healthInitialized) {
  initializeProviderHealth();
  healthInitialized = true;
}

/**
 * Get RAG context using Python script
 * Falls back to full context if RAG unavailable
 */
async function getRAGContext(
  programId: string,
  userQuery: string,
  topK: number = 5,
  maxTokens: number = 8000
): Promise<string> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(process.cwd(), 'chunking', 'rag_retriever.py');
    
    const python = spawn('python3', [
      scriptPath,
      '--library', programId,
      '--query', userQuery,
      '--top-k', topK.toString(),
      '--max-tokens', maxTokens.toString()
    ]);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        console.warn(`RAG script failed (code ${code}), falling back to full context`);
        console.warn(`Error: ${stderr}`);
        reject(new Error('RAG_UNAVAILABLE'));
      } else {
        resolve(stdout.trim());
      }
    });

    python.on('error', (error) => {
      console.warn(`RAG script error, falling back to full context:`, error.message);
      reject(new Error('RAG_UNAVAILABLE'));
    });
  });
}

export async function POST(request: NextRequest) {
  try {
    // Get client IP for rate limiting
    const clientIP = request.headers.get('x-forwarded-for') || 
                    request.headers.get('x-real-ip') || 
                    'unknown';
    
    // Rate limiting for credential attempts
    if (!credentialRateLimiter.isAllowed(clientIP)) {
      return new Response(
        JSON.stringify({ 
          error: 'Too many credential attempts. Please try again later.',
          details: 'Rate limit exceeded for credential validation'
        }),
        { 
          status: 429, 
          headers: { 
            'Content-Type': 'application/json',
            'Retry-After': '900' // 15 minutes
          } 
        }
      );
    }

    // Parse message from post
    const { programId, messages, modelId, stream = false, credentials = {} } = await request.json();

    // Sanitize logs to prevent credential exposure
    const sanitizedCredentials = sanitizeLogData(credentials);

    // Get program configuration
    const program = getProgramById(programId);
    if (!program) {
      return new Response(
        JSON.stringify({ error: `Program ${programId} not found` }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Extract user query from the last message for RAG
    const lastUserMessage = messages.filter((msg: any) => msg.role === 'user').pop();
    const userQuery = lastUserMessage?.content || '';

     // Try to load RAG context first, fall back to full context if unavailable
     let context = '';
     let usingRAG = false;
     
     // Check if we're on Cloud Run (production) - disable RAG there
     const isCloudRun = process.env.K_SERVICE !== undefined;
     
     if (!isCloudRun && userQuery) {
       // RAG available only in local development
       try {
         console.log('Attempting RAG context retrieval (LOCAL):', {
           programId,
           queryLength: userQuery.length,
           queryPreview: userQuery.substring(0, 100)
         });
         
         context = await getRAGContext(programId, userQuery, 5, 8000);
         usingRAG = true;
         
         console.log('RAG context loaded successfully:', {
           contextLength: context.length,
           estimatedTokens: Math.floor(context.length / 4)
         });
       } catch (error) {
         console.warn('RAG unavailable, falling back to full context:', error);
         // Fall back to full context
         context = await loadContext([], programId);
         usingRAG = false;
       }
     } else {
       // On Cloud Run or no query: load full context
       if (isCloudRun) {
         console.log('Cloud Run environment detected - using full context (ChromaDB not available)');
       }
       context = await loadContext([], programId);
     }

    // Create system message with context
    const systemMessage = {
      role: "system",
      content: getSystemPromptWithContext(programId, context)
    };

    // Prepare the messages array with the system message
    const allMessages = [
      systemMessage,
      ...messages.map((msg: any) => ({
        role: msg.role,
        content: msg.content
      }))
    ];

    // Log the request for debugging (with sanitized data)
    console.log('Unified API Request:', {
      programId,
      modelId: modelId || 'default',
      messageCount: messages.length,
      systemMessageLength: systemMessage.content.length,
      streaming: stream,
      hasCredentials: !!credentials,
      credentialKeys: Object.keys(sanitizedCredentials),
      clientIP: sanitizeLogData(clientIP),
      usingRAG: usingRAG,
      contextSource: usingRAG ? 'RAG (ChromaDB)' : 'Full Context'
    });

    // Load config to check for fallback model
    const config = loadConfig();
    const fallbackModelId = config.fallbackModelId;

    try {
      if (stream) {
        // Handle streaming request
        try {
          // Try with the primary model first
          const streamingResponse = await createStreamingChatCompletion(modelId, allMessages, {}, credentials);

          // For streaming responses, we need to convert the OpenAI stream to a ReadableStream
          const encoder = new TextEncoder();
          const readable = new ReadableStream({
          async start(controller) {
            try {
              // Handle each chunk from the OpenAI stream
              for await (const chunk of streamingResponse as any) {
                // Check if the controller is still active before enqueueing
                try {
                  // Format the chunk as an SSE message
                  const text = JSON.stringify({
                    choices: [{
                      delta: { content: chunk.choices[0]?.delta?.content || '' }
                    }]
                  });
                  // Send the chunk as an SSE message
                  controller.enqueue(encoder.encode(`data: ${text}\n\n`));
                } catch (enqueueError) {
                  // If we can't enqueue, the client probably disconnected
                  console.log('Client disconnected or controller closed');
                  break;
                }
              }

              try {
                // Signal the end of the stream
                controller.enqueue(encoder.encode('data: [DONE]\n\n'));
              } catch (finalEnqueueError) {
                // Ignore errors when trying to send the final message
                console.log('Could not send final message, controller may be closed');
              }
            } catch (error) {
              // Check if this is an abort error
              if (error instanceof Error && error.name === 'AbortError') {
                console.log('Stream aborted by client');
                // Try to send a final message indicating cancellation
                try {
                  controller.enqueue(encoder.encode('data: [CANCELLED]\n\n'));
                } catch (cancelError) {
                  // Ignore errors when trying to send cancellation message
                }
                return;
              }
              
              // Log other errors
              console.error('Error in streaming response:', error);
              
              // Try to send an error message to the client
              try {
                const errorMessage = JSON.stringify({
                  error: 'Streaming error occurred',
                  details: error instanceof Error ? error.message : 'Unknown error'
                });
                controller.enqueue(encoder.encode(`data: ${errorMessage}\n\n`));
              } catch (errorEnqueueError) {
                // Ignore errors when trying to send error message
              }
            }
          }
          });

          // Reset rate limiter on successful request
          credentialRateLimiter.reset(clientIP);

          return new Response(readable, {
            headers: {
              'Content-Type': 'text/event-stream',
              'Cache-Control': 'no-cache',
              'Connection': 'keep-alive',
            },
          });
        } catch (streamingError) {
          console.error('Streaming error with primary model:', streamingError);
          
          // If fallback model is configured and different from primary, try fallback
          if (fallbackModelId && fallbackModelId !== modelId) {
            console.log(`Trying fallback model: ${fallbackModelId}`);
            try {
              const fallbackStreamingResponse = await createStreamingChatCompletion(fallbackModelId, allMessages, {}, credentials);
              
              const encoder = new TextEncoder();
              const readable = new ReadableStream({
                async start(controller) {
                  try {
                    for await (const chunk of fallbackStreamingResponse as any) {
                      try {
                        const text = JSON.stringify({
                          choices: [{
                            delta: { content: chunk.choices[0]?.delta?.content || '' }
                          }]
                        });
                        controller.enqueue(encoder.encode(`data: ${text}\n\n`));
                      } catch (enqueueError) {
                        console.log('Client disconnected during fallback streaming');
                        break;
                      }
                    }
                    
                    try {
                      controller.enqueue(encoder.encode('data: [DONE]\n\n'));
                    } catch (finalEnqueueError) {
                      console.log('Could not send final fallback message');
                    }
                  } catch (error) {
                    console.error('Error in fallback streaming response:', error);
                    try {
                      const errorMessage = JSON.stringify({
                        error: 'Fallback streaming error occurred',
                        details: error instanceof Error ? error.message : 'Unknown error'
                      });
                      controller.enqueue(encoder.encode(`data: ${errorMessage}\n\n`));
                    } catch (errorEnqueueError) {
                      // Ignore errors when trying to send error message
                    }
                  }
                }
              });

              // Reset rate limiter on successful fallback request
              credentialRateLimiter.reset(clientIP);

              return new Response(readable, {
                headers: {
                  'Content-Type': 'text/event-stream',
                  'Cache-Control': 'no-cache',
                  'Connection': 'keep-alive',
                },
              });
            } catch (fallbackError) {
              console.error('Fallback streaming also failed:', fallbackError);
              throw fallbackError;
            }
          } else {
            throw streamingError;
          }
        }
      } else {
        // For non-streaming API, parse the JSON response
        try {
          const responseData = await createChatCompletion(modelId, allMessages, {}, credentials);
          
          // Reset rate limiter on successful request
          credentialRateLimiter.reset(clientIP);
          
          return new Response(JSON.stringify(responseData), {
            headers: { 'Content-Type': 'application/json' },
          });
        } catch (completionError) {
          console.error('Completion error with primary model:', completionError);
          
          // If fallback model is configured and different from primary, try fallback
          if (fallbackModelId && fallbackModelId !== modelId) {
            console.log(`Trying fallback model: ${fallbackModelId}`);
            try {
              const fallbackResponseData = await createChatCompletion(fallbackModelId, allMessages, {}, credentials);
              
              // Reset rate limiter on successful fallback request
              credentialRateLimiter.reset(clientIP);
              
              return new Response(JSON.stringify(fallbackResponseData), {
                headers: { 'Content-Type': 'application/json' },
              });
            } catch (fallbackError) {
              console.error('Fallback completion also failed:', fallbackError);
              throw fallbackError;
            }
          } else {
            throw completionError;
          }
        }
      }
    } catch (error) {
      console.error('Error in chat completion:', error);
      
      // Log error details (sanitized)
      const errorDetails = error instanceof Error ? error.message : 'Unknown error';
      console.error('Chat completion error details:', sanitizeLogData(errorDetails));

      // Provide more specific error messages based on the error type
      let errorMessage = 'An error occurred while processing your request';
      let statusCode = 500;
      
      if (errorDetails.includes('API key') || errorDetails.includes('authentication')) {
        errorMessage = 'Authentication failed. Please check your API credentials.';
        statusCode = 401;
      } else if (errorDetails.includes('model') || errorDetails.includes('configuration')) {
        errorMessage = 'Model configuration error. Please try a different model.';
        statusCode = 400;
      } else if (errorDetails.includes('rate limit') || errorDetails.includes('quota')) {
        errorMessage = 'Rate limit exceeded. Please try again later.';
        statusCode = 429;
      } else if (errorDetails.includes('context') || errorDetails.includes('token')) {
        errorMessage = 'Request too large. Please try a shorter message.';
        statusCode = 413;
      }

      return new Response(
        JSON.stringify({ 
          error: errorMessage,
          details: sanitizeLogData(errorDetails)
        }),
        { 
          status: statusCode, 
          headers: { 'Content-Type': 'application/json' } 
        }
      );
    }
  } catch (error) {
    console.error('Unexpected error in unified chat API:', error);
    
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        details: 'An unexpected error occurred'
      }),
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }
}
