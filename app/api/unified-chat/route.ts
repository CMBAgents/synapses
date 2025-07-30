import { NextRequest } from 'next/server';
import { loadContext, getSystemPromptWithContext } from '@/app/utils/context';
import { getProgramById, loadConfig } from '@/app/utils/config';
import { createChatCompletion, createStreamingChatCompletion, logTokenUsage } from '@/app/utils/unified-client';

// This enables Edge Functions in Vercel
export const runtime = "edge";

export async function POST(request: NextRequest) {
  try {
    // Parse message from post
    const { programId, messages, modelId, stream = false } = await request.json();

    // Get program configuration
    const program = getProgramById(programId);
    if (!program) {
      return new Response(
        JSON.stringify({ error: `Program ${programId} not found` }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Load context for the program directly using the programId
    // This will handle URL-based context files automatically
    const context = await loadContext([], programId);

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

    // Log the request for debugging
    console.log('Unified API Request:', {
      programId,
      modelId: modelId || 'default',
      messageCount: messages.length,
      systemMessageLength: systemMessage.content.length,
      streaming: stream
    });

    // Load config to check for fallback model
    const config = loadConfig();
    const fallbackModelId = config.fallbackModelId;

    try {
      if (stream) {
        // Handle streaming request
        try {
          // Try with the primary model first
          const streamingResponse = await createStreamingChatCompletion(modelId, allMessages);

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
                  const cancelText = JSON.stringify({
                    choices: [{
                      delta: { content: '\n\n*Response cancelled by user*' }
                    }]
                  });
                  controller.enqueue(encoder.encode(`data: ${cancelText}\n\n`));
                  controller.enqueue(encoder.encode('data: [DONE]\n\n'));
                } catch (finalError) {
                  // Ignore errors when trying to send the final message
                }
              } else {
                console.error('Error processing stream:', error);
                try {
                  controller.error(error);
                } catch (controllerError) {
                  // Controller might already be closed
                  console.log('Could not send error to controller');
                }
              }
            } finally {
              try {
                controller.close();
              } catch (closeError) {
                // Controller might already be closed
                console.log('Controller already closed');
              }
            }
          }
        });

        // Return the streaming response
        return new Response(readable, {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
          }
        });
        } catch (primaryError) {
          // If there's a fallback model configured and the primary model failed, try the fallback
          if (fallbackModelId) {
            console.log(`Primary model failed, trying fallback model: ${fallbackModelId}`);

            // Try with the fallback model
            const fallbackStreamingResponse = await createStreamingChatCompletion(fallbackModelId, allMessages);

            // Check if the fallback streaming response is valid
            if (!fallbackStreamingResponse) {
              throw new Error('Fallback model returned an invalid streaming response');
            }

            // For streaming responses, we need to convert the OpenAI stream to a ReadableStream
            const encoder = new TextEncoder();
            const readable = new ReadableStream({
              async start(controller) {
                try {
                  // Send a notice that we're using the fallback model (unless in simpleMode)
                  if (config.simpleMode !== true) {
                    const fallbackNotice = JSON.stringify({
                      choices: [{
                        delta: { content: `*Using fallback model due to error with primary model*\n\n` }
                      }]
                    });
                    controller.enqueue(encoder.encode(`data: ${fallbackNotice}\n\n`));
                  }

                  // Handle each chunk from the OpenAI stream
                  for await (const chunk of fallbackStreamingResponse as any) {
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
                  // Handle errors in the fallback stream
                  console.error('Error processing fallback stream:', error);
                  try {
                    controller.error(error);
                  } catch (controllerError) {
                    // Controller might already be closed
                    console.log('Could not send error to controller');
                  }
                } finally {
                  try {
                    controller.close();
                  } catch (closeError) {
                    // Controller might already be closed
                    console.log('Controller already closed');
                  }
                }
              }
            });

            // Return the fallback streaming response
            return new Response(readable, {
              headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
              }
            });
          } else {
            // No fallback model, re-throw the error
            throw primaryError;
          }
        }
      } else {
        // Handle non-streaming request
        try {
          // Try with the primary model first
          const completion = await createChatCompletion(modelId, allMessages);

          // Log token usage
          if (completion.usage) {
            logTokenUsage(modelId, programId, completion.usage);
          }

          // Extract the content from the response
          const content = completion.choices[0]?.message?.content || '';

          // Return the response
          return new Response(
            JSON.stringify({ content }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          );
        } catch (primaryError) {
          // If there's a fallback model configured and the primary model failed, try the fallback
          if (fallbackModelId) {
            console.log(`Primary model failed, trying fallback model: ${fallbackModelId}`);

            try {
              // Try with the fallback model
              const fallbackCompletion = await createChatCompletion(fallbackModelId, allMessages);

              // Log token usage for the fallback model
              if (fallbackCompletion.usage) {
                logTokenUsage(fallbackModelId, programId, fallbackCompletion.usage);
              }

              // Check if the fallback completion has a valid structure
              if (!fallbackCompletion || !fallbackCompletion.choices || !fallbackCompletion.choices[0]) {
                throw new Error('Fallback model returned an invalid response structure');
              }

              // Extract the content from the fallback response
              let content = fallbackCompletion.choices[0]?.message?.content || '';

              // Add a notice that we're using the fallback model (unless in simpleMode)
              if (config.simpleMode !== true) {
                content = `*Using fallback model due to error with primary model*\n\n${content}`;
              }

              // Return the fallback response
              return new Response(
                JSON.stringify({ content }),
                { status: 200, headers: { 'Content-Type': 'application/json' } }
              );
            } catch (fallbackError) {
              // Both primary and fallback models failed
              console.error('Both primary and fallback models failed:', { primaryError, fallbackError });
              throw fallbackError; // Throw the fallback error for the error handler
            }
          } else {
            // No fallback model, re-throw the error
            throw primaryError;
          }
        }
      }
    } catch (error) {
      // Handle errors
      console.error('Error in unified chat API:', error);

      // Create a more detailed error message
      const errorMessage = error instanceof Error ? error.message : String(error);

      // Check for specific error types
      if (errorMessage.includes('API key')) {
        return new Response(
          JSON.stringify({
            error: 'API key error',
            details: 'Please check your API key configuration.',
            message: errorMessage
          }),
          { status: 401, headers: { 'Content-Type': 'application/json' } }
        );
      } else if (errorMessage.includes('model')) {
        return new Response(
          JSON.stringify({
            error: 'Model configuration error',
            details: `The specified model may not be available or properly configured.`,
            message: errorMessage
          }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
      }

      // Re-throw for general error handling
      throw error;
    }
  } catch (error) {
    console.error('Error in unified chat API:', error);

    // Create a more detailed error message
    const errorMessage = error instanceof Error
      ? `Error: ${error.message}`
      : 'An unknown error occurred';

    // Return a more informative error response
    return new Response(
      JSON.stringify({
        error: 'An error occurred processing your request',
        details: errorMessage,
        timestamp: new Date().toISOString()
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
}
