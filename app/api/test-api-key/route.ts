import { NextRequest } from 'next/server';
import { createClient } from '@/app/utils/unified-client';

// This enables Node.js runtime for Google Cloud compatibility
export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  try {
    // Parse the request
    const { modelId, credentials } = await request.json();

    if (!modelId) {
      return new Response(
        JSON.stringify({ error: 'Model ID is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    console.log('Testing API key for model:', modelId);
    console.log('Credentials provided:', credentials ? 'Yes' : 'No');

    // Create a test message
    const testMessages = [
      {
        role: 'user',
        content: 'Hello! This is a test message to verify the API key is working. Please respond with a simple greeting.'
      }
    ];

    try {
      // Test the API key by making a simple call
      const { client, modelName, isVertexAI, provider } = createClient(modelId, credentials);
      
      console.log('Client created successfully:', {
        provider,
        modelName,
        isVertexAI,
        hasClient: !!client
      });

      if (isVertexAI) {
        // For Vertex AI, we'll just check if the client was created successfully
        // since the actual API call requires more complex setup
        return new Response(
          JSON.stringify({ 
            success: true, 
            message: 'Vertex AI client created successfully',
            provider,
            modelName,
            credentials: {
              projectId: credentials?.[modelId]?.projectId ? 'Set' : 'Missing',
              location: credentials?.[modelId]?.location ? 'Set' : 'Missing',
              serviceAccountKey: credentials?.[modelId]?.serviceAccountKey ? 'Set' : 'Missing'
            }
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        );
      } else {
        // For other providers, make a simple test call
        if (!client) {
          throw new Error('Client not available for this model');
        }

        // Make a minimal test call with model-specific parameters
        let testOptions: any = {
          model: modelName,
          messages: testMessages as any,
          stream: false
        };

        // GPT-5 specific parameters
        if (modelName.includes('gpt-5')) {
          testOptions.max_completion_tokens = 50;
          // GPT-5 doesn't support temperature, so we omit it
        } else {
          // For other models, use standard parameters
          testOptions.max_tokens = 50;
          testOptions.temperature = 0.1;
        }

        console.log('Making test API call with options:', testOptions);

        const response = await client.chat.completions.create(testOptions);
        
        // Type assertion to handle the response properly
        const completionResponse = response as any;
        
        console.log('API test successful:', {
          model: completionResponse.model,
          usage: completionResponse.usage,
          responseLength: completionResponse.choices?.[0]?.message?.content?.length || 0
        });

        return new Response(
          JSON.stringify({ 
            success: true, 
            message: 'API key is valid and working',
            provider,
            modelName,
            response: {
              content: completionResponse.choices?.[0]?.message?.content || '',
              model: completionResponse.model || modelName,
              usage: completionResponse.usage || {}
            }
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        );
      }

    } catch (apiError) {
      console.error('API test failed:', apiError);
      
      // Provide detailed error information
      const errorMessage = apiError instanceof Error ? apiError.message : String(apiError);
      
      if (errorMessage.includes('API key') || errorMessage.includes('authentication')) {
        return new Response(
          JSON.stringify({ 
            success: false, 
            error: 'API key validation failed',
            details: errorMessage,
            provider: modelId.split('/')[0],
            modelName: modelId.split('/')[1]
          }),
          { status: 401, headers: { 'Content-Type': 'application/json' } }
        );
      } else if (errorMessage.includes('model') || errorMessage.includes('not found')) {
        return new Response(
          JSON.stringify({ 
            success: false, 
            error: 'Model not available',
            details: errorMessage,
            provider: modelId.split('/')[0],
            modelName: modelId.split('/')[1]
          }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
      } else {
        return new Response(
          JSON.stringify({ 
            success: false, 
            error: 'API test failed',
            details: errorMessage,
            provider: modelId.split('/')[0],
            modelName: modelId.split('/')[1]
          }),
          { status: 500, headers: { 'Content-Type': 'application/json' } }
        );
      }
    }

  } catch (error) {
    console.error('Error in API key test endpoint:', error);
    
    return new Response(
      JSON.stringify({
        error: 'Failed to process API key test request',
        details: error instanceof Error ? error.message : String(error)
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
