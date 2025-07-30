import { NextRequest } from 'next/server';
import { getEmbeddedContext, loadContext } from '@/app/utils/context';
import { getProgramById } from '@/app/utils/config';
import { Program } from '@/app/utils/types';

export async function GET(_request: NextRequest, context: { params: Promise<{ programId: string }> }) {
  try {
    // Get the programId from params
    const { programId } = await context.params;

    // Get the program configuration
    const program = getProgramById(programId) as Program;

    if (!program) {
      return new Response(
        JSON.stringify({
          error: `Program not found: ${programId}`,
          timestamp: new Date().toISOString()
        }),
        {
          status: 404,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
    }

    // Check if the program has a combinedContextFile that is a URL
    if (program.combinedContextFile && program.combinedContextFile.startsWith('http')) {
      try {
        // Load context using the loadContext function which handles URLs
        const contextContent = await loadContext([], programId);

        // Return the context as plain text
        return new Response(contextContent, {
          status: 200,
          headers: {
            'Content-Type': 'text/markdown'
          }
        });
      } catch (error) {
        console.error(`Error loading context from URL for program ${programId}:`, error);
        // Fall through to try embedded context
      }
    }

    // Get the embedded context for the specified program
    const contextContent = getEmbeddedContext(programId);

    if (!contextContent) {
      return new Response(
        JSON.stringify({
          error: `No context found for program: ${programId}`,
          timestamp: new Date().toISOString()
        }),
        {
          status: 404,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
    }

    // Return the context as plain text
    return new Response(contextContent, {
      status: 200,
      headers: {
        'Content-Type': 'text/markdown'
      }
    });
  } catch (error) {
    console.error(`Error accessing context:`, error);

    return new Response(
      JSON.stringify({
        error: 'An error occurred accessing context',
        details: error instanceof Error ? error.message : String(error),
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
