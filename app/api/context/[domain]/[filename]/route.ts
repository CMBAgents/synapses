import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: { domain: string; filename: string } }
) {
  try {
    const { domain, filename } = params;
    
    // Vérifier que les paramètres sont sécurisés
    if (!domain || !filename || 
        domain.includes('..') || domain.includes('/') ||
        filename.includes('..') || filename.includes('/')) {
      return new Response('Invalid parameters', { status: 400 });
    }

    // Construire le chemin vers le fichier
    const filePath = path.join(process.cwd(), 'public', 'context', domain, filename);

    // Vérifier si le fichier existe
    if (!fs.existsSync(filePath)) {
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