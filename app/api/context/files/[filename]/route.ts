import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const { filename } = await params;
    
    // Vérifier que le nom de fichier est sécurisé
    if (!filename || filename.includes('..') || filename.includes('/')) {
      return new Response('Invalid filename', { status: 400 });
    }

    // Chercher le fichier dans les sous-dossiers astronomy et finance
    const possiblePaths = [
      path.join(process.cwd(), 'public', 'context', 'astronomy', filename),
      path.join(process.cwd(), 'public', 'context', 'finance', filename)
    ];

    let filePath = null;
    for (const possiblePath of possiblePaths) {
      if (fs.existsSync(possiblePath)) {
        filePath = possiblePath;
        break;
      }
    }

    if (!filePath) {
      return new Response('Context file not found', { status: 404 });
    }

    // Lire le contenu du fichier
    const content = fs.readFileSync(filePath, 'utf-8');

    // Retourner le contenu avec les bons headers
    return new Response(content, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'public, max-age=3600', // Cache pendant 1 heure
      },
    });

  } catch (error) {
    console.error('Error serving context file:', error);
    return new Response('Internal server error', { status: 500 });
  }
} 