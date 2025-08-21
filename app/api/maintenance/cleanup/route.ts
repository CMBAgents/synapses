import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { type = 'pycache' } = await request.json();
    
    // Vérifier que le type est valide
    if (!['pycache', 'contexts', 'all'].includes(type)) {
      return NextResponse.json({ error: 'Invalid cleanup type' }, { status: 400 });
    }

    // Chemin vers le script unifié
    const scriptPath = path.join(process.cwd(), 'scripts', 'maintenance', 'context-manager-unified.py');
    
    // Construire la commande selon le type
    let command: string;
    switch (type) {
      case 'pycache':
        command = `python3 "${scriptPath}" --cleanup-pycache`;
        break;
      case 'contexts':
        command = `python3 "${scriptPath}" --cleanup`;
        break;
      case 'all':
        command = `python3 "${scriptPath}" --cleanup && python3 "${scriptPath}" --cleanup-pycache`;
        break;
      default:
        command = `python3 "${scriptPath}" --cleanup-pycache`;
    }
    
    // Exécuter le nettoyage en arrière-plan
    execAsync(command, { cwd: process.cwd() })
      .then(({ stdout, stderr }) => {
        console.log('Cleanup completed successfully:', stdout);
        if (stderr) {
          console.warn('Cleanup warnings:', stderr);
        }
      })
      .catch((error) => {
        console.error('Cleanup failed:', error);
      });

    return NextResponse.json({ 
      success: true, 
      message: `Cleanup ${type} started successfully`,
      type
    });
    
  } catch (error) {
    console.error('Error starting cleanup:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    // Retourner les types de nettoyage disponibles
    return NextResponse.json({ 
      status: 'available',
      types: ['pycache', 'contexts', 'all'],
      descriptions: {
        pycache: 'Clean Python cache files (__pycache__ and .pyc)',
        contexts: 'Clean duplicate context files',
        all: 'Clean both Python caches and duplicate contexts'
      },
      description: 'Cleanup API for CMB Agent Info'
    });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
