import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { getSupportedDomains } from '@/app/config/domains';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const resolvedParams = await params;
    const filename = resolvedParams.filename;
    
    // Vérifier que le fichier se termine par .txt
    if (!filename.endsWith('.txt')) {
      return NextResponse.json({ error: 'Invalid file type' }, { status: 400 });
    }

    // Chercher le fichier dans les domaines disponibles
    const domains = getSupportedDomains();
    let filePath = null;
    let foundDomain = null;

    for (const domain of domains) {
      const contextPath = path.join(process.cwd(), 'public', 'context', domain, filename);
      if (fs.existsSync(contextPath)) {
        filePath = contextPath;
        foundDomain = domain;
        break;
      }
    }

    if (!filePath) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }

    // Lire le contenu du fichier
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Retourner le contenu pour affichage dans le navigateur
    return new NextResponse(content, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'public, max-age=3600', // Cache pour 1 heure
      },
    });

  } catch (error) {
    console.error('Error serving context file:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 