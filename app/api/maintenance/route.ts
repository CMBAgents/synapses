import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { type = 'quick' } = await request.json();
    
    // Vérifier que le type est valide
    if (!['quick', 'full'].includes(type)) {
      return NextResponse.json({ error: 'Invalid maintenance type' }, { status: 400 });
    }

    // Chemin vers le script de maintenance modulaire
    const scriptPath = path.join(process.cwd(), 'maintenance', 'maintenance_modular.py');
    
    // Exécuter la maintenance en arrière-plan
    const command = `python3 "${scriptPath}" --mode ${type}`;
    
    // Exécuter la maintenance de manière asynchrone
    execAsync(command, { cwd: process.cwd() })
      .then(({ stdout, stderr }) => {
        console.log('Maintenance completed successfully:', stdout);
        if (stderr) {
          console.warn('Maintenance warnings:', stderr);
        }
      })
      .catch((error) => {
        console.error('Maintenance failed:', error);
      });

    return NextResponse.json({ 
      success: true, 
      message: `Maintenance ${type} started successfully`,
      type
    });
    
  } catch (error) {
    console.error('Error starting maintenance:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    // Retourner le statut de la maintenance
    return NextResponse.json({ 
      status: 'available',
      types: ['quick', 'full'],
      description: 'Maintenance API for CMB Agent Info'
    });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
