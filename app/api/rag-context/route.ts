import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

// This enables Node.js runtime for Python integration
export const runtime = "nodejs";

/**
 * API route to get RAG context for a library
 * Uses Python script to query ChromaDB and return relevant chunks
 */
export async function POST(request: NextRequest) {
  try {
    const { library, query, topK = 5, maxTokens = 8000 } = await request.json();

    if (!library || !query) {
      return NextResponse.json(
        { error: 'Missing required parameters: library and query' },
        { status: 400 }
      );
    }

    // Call Python script to get context
    const context = await getRAGContext(library, query, topK, maxTokens);

    return NextResponse.json({
      library,
      query,
      context,
      contextLength: context.length,
      estimatedTokens: Math.floor(context.length / 4)
    });

  } catch (error) {
    console.error('Error in RAG context API:', error);
    return NextResponse.json(
      { 
        error: 'Failed to retrieve context',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

/**
 * Call Python script to get RAG context
 */
function getRAGContext(
  library: string,
  query: string,
  topK: number,
  maxTokens: number
): Promise<string> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(process.cwd(), 'scripts', 'rag_retriever.py');
    
    const python = spawn('python3', [
      scriptPath,
      '--library', library,
      '--query', query,
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
        reject(new Error(`Python script failed: ${stderr}`));
      } else {
        resolve(stdout.trim());
      }
    });

    python.on('error', (error) => {
      reject(new Error(`Failed to spawn Python process: ${error.message}`));
    });
  });
}

