import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const { domain } = await request.json();
    
    if (!domain || !['astronomy', 'finance'].includes(domain)) {
      return NextResponse.json({ error: 'Invalid domain' }, { status: 400 });
    }

    const jsonPath = path.join(process.cwd(), 'app', 'data', `${domain}-libraries.json`);
    // Handle the special case where astronomy context files are in 'astro' directory
    const contextDirName = domain === 'astronomy' ? 'astro' : domain;
    const contextDir = path.join(process.cwd(), 'public', 'context', contextDirName);
    
    if (!fs.existsSync(jsonPath)) {
      return NextResponse.json({ error: 'JSON file not found' }, { status: 404 });
    }
    
    // Read the JSON file
    const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
    
    // Get existing context files
    const contextFiles: string[] = [];
    if (fs.existsSync(contextDir)) {
      const files = fs.readdirSync(contextDir);
      files.forEach(file => {
        if (file.endsWith('.txt')) {
          contextFiles.push(file);
        }
      });
    }
    
    // Update each library entry
    jsonData.libraries.forEach((library: any) => {
      // Create the expected context file name based on library name
      const contextFileName = `${library.name.replace(/[\/\-\.]/g, '-')}-context.txt`;
      const hasContextFile = contextFiles.includes(contextFileName);
      
      // Update the library entry
      library.hasContextFile = hasContextFile;
      if (hasContextFile) {
        library.contextFileName = contextFileName;
      } else {
        delete library.contextFileName;
      }
    });
    
    // Write back to the JSON file
    fs.writeFileSync(jsonPath, JSON.stringify(jsonData, null, 2));
    
    return NextResponse.json({ 
      success: true, 
      message: `Updated context status for ${domain}: ${jsonData.libraries.length} libraries processed`,
      contextFiles,
      updatedLibraries: jsonData.libraries.length
    });
    
  } catch (error) {
    console.error('Error updating context status:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 