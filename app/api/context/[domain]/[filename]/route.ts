import { NextRequest } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ domain: string; filename: string }> }
) {
  try {
    const { domain, filename } = await context.params;

    // Validate domain
    if (!['astronomy', 'finance'].includes(domain)) {
      return new Response(
        JSON.stringify({ error: 'Invalid domain' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Construct the file path
    const contextPath = path.join(process.cwd(), 'public', 'context', domain, filename);

    // Check if file exists
    if (!fs.existsSync(contextPath)) {
      return new Response(
        JSON.stringify({ 
          error: `Context file not found: ${filename}`,
          path: contextPath,
          timestamp: new Date().toISOString()
        }),
        {
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Read and return the file content
    const content = fs.readFileSync(contextPath, 'utf-8');
    
    return new Response(content, {
      status: 200,
      headers: {
        'Content-Type': 'text/markdown',
        'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
      }
    });

  } catch (error) {
    console.error(`Error accessing context file:`, error);

    return new Response(
      JSON.stringify({
        error: 'An error occurred accessing context file',
        details: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString()
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}
