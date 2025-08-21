import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { action = 'quick' } = await request.json();
    
    // Vérifier que l'action est valide
    if (!['quick', 'full', 'verify', 'cleanup'].includes(action)) {
      return NextResponse.json({ error: 'Invalid context action' }, { status: 400 });
    }

    // Chemin vers le script unifié
    const scriptPath = path.join(process.cwd(), 'scripts', 'maintenance', 'context-manager-unified.py');
    
    // Construire la commande selon l'action
    let command: string;
    switch (action) {
      case 'quick':
        command = `python3 "${scriptPath}" --quick`;
        break;
      case 'full':
        command = `python3 "${scriptPath}" --full`;
        break;
      case 'verify':
        command = `python3 "${scriptPath}" --verify`;
        break;
      case 'cleanup':
        command = `python3 "${scriptPath}" --cleanup`;
        break;
      default:
        command = `python3 "${scriptPath}" --quick`;
    }
    
    // Exécuter l'action en arrière-plan
    execAsync(command, { cwd: process.cwd() })
      .then(({ stdout, stderr }) => {
        console.log(`Context action ${action} completed successfully:`, stdout);
        if (stderr) {
          console.warn(`Context action ${action} warnings:`, stderr);
        }
      })
      .catch((error) => {
        console.error(`Context action ${action} failed:`, error);
      });

    return NextResponse.json({ 
      success: true, 
      message: `Context action ${action} started successfully`,
      action
    });
    
  } catch (error) {
    console.error('Error starting context action:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    // Retourner les actions de contexte disponibles
    return NextResponse.json({ 
      status: 'available',
      actions: ['quick', 'full', 'verify', 'cleanup'],
      descriptions: {
        quick: 'Quick context update without generation',
        full: 'Full context update with generation of missing contexts',
        verify: 'Verify context file structure',
        cleanup: 'Clean duplicate context files'
      },
      description: 'Context Management API for CMB Agent Info'
    });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
