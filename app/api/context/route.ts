import { NextRequest } from 'next/server';
import { getEmbeddedContext } from '@/app/utils/context';
import { getProgramById } from '@/app/utils/config';

export async function GET(_request: NextRequest) {
  try {
    // Get information about the embedded context
    const programs = getProgramById() as Record<string, any>;
    const contextInfo = Object.entries(programs).map(([id, program]) => {
      const context = getEmbeddedContext(id);
      return {
        id,
        name: program.name,
        available: !!context,
        size: context ? context.length : 0
      };
    });

    return new Response(
      JSON.stringify({
        success: true,
        message: 'Context is embedded in the application',
        contextInfo
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  } catch (error) {
    console.error('Error accessing embedded context:', error);

    return new Response(
      JSON.stringify({
        error: 'An error occurred accessing embedded context',
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
