import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const domain = searchParams.get('domain');
    const action = searchParams.get('action');
    const fileName = searchParams.get('fileName');

    if (!domain || !['astronomy', 'finance'].includes(domain)) {
      return NextResponse.json({ error: 'Invalid domain' }, { status: 400 });
    }

    switch (action) {
      case 'loadContextFile':
        if (!fileName) {
          return NextResponse.json({ error: 'fileName is required' }, { status: 400 });
        }
        return handleLoadContextFile(domain, fileName);

      case 'getContextFiles':
        return handleGetContextFiles(domain);

      case 'hasContextFile':
        if (!fileName) {
          return NextResponse.json({ error: 'fileName is required' }, { status: 400 });
        }
        return handleHasContextFile(domain, fileName);

      case 'updateLibrariesWithContextStatus':
        return handleUpdateLibrariesWithContextStatus(domain);

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Error in context API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

function handleLoadContextFile(domain: string, fileName: string) {
  try {
    const contextDirName = domain;
    const contextPath = path.join(process.cwd(), 'public', 'context', contextDirName, fileName);
    if (fs.existsSync(contextPath)) {
      const content = fs.readFileSync(contextPath, 'utf-8');
      return NextResponse.json({ content });
    }
    return NextResponse.json({ content: null });
  } catch (error) {
    console.error(`Error loading context file ${fileName} for domain ${domain}:`, error);
    return NextResponse.json({ content: null });
  }
}

function handleGetContextFiles(domain: string) {
  try {
    const contextDirName = domain;
    const contextDir = path.join(process.cwd(), 'public', 'context', contextDirName);
    if (!fs.existsSync(contextDir)) {
      return NextResponse.json([]);
    }

    const files = fs.readdirSync(contextDir);
    const contextFiles = [];

    for (const file of files) {
      if (file.endsWith('.txt')) {
        const content = fs.readFileSync(path.join(contextDir, file), 'utf-8');
        contextFiles.push({
          name: file.replace('.txt', ''),
          content,
          domain
        });
      }
    }

    return NextResponse.json(contextFiles);
  } catch (error) {
    console.error(`Error loading context files for domain ${domain}:`, error);
    return NextResponse.json([]);
  }
}

function handleHasContextFile(domain: string, fileName: string) {
  try {
    const contextDirName = domain;
    const contextPath = path.join(process.cwd(), 'public', 'context', contextDirName, fileName);
    const hasFile = fs.existsSync(contextPath);
    return NextResponse.json({ hasFile });
  } catch (error) {
    return NextResponse.json({ hasFile: false });
  }
}

function handleUpdateLibrariesWithContextStatus(domain: string) {
  try {
    const jsonPath = path.join(process.cwd(), 'app', 'data', `${domain}-libraries.json`);
    const contextDirName = domain;
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
      // Handle different naming patterns
      let contextFileName = '';
      
      // Try different naming patterns
      const patterns = [
        `${library.name.replace(/[\/\-\.]/g, '-')}-context.txt`,
        `${library.name.split('/').pop()}-context.txt`,
        `${library.name.split('/').pop().replace(/[\/\-\.]/g, '-')}-context.txt`,
        // Handle cases like "skyfielders/python-skyfield" -> "skyfield-context.txt"
        `${library.name.split('/').pop().split('-').pop()}-context.txt`,
        // Handle cases like "python-skyfield" -> "skyfield-context.txt"
        `${library.name.split('/').pop().split('-').slice(-1)[0]}-context.txt`
      ];
      
      let hasContextFile = false;
      for (const pattern of patterns) {
        if (contextFiles.includes(pattern)) {
          contextFileName = pattern;
          hasContextFile = true;
          break;
        }
      }
      
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
      data: jsonData
    });
    
  } catch (error) {
    console.error(`Error updating context status for domain ${domain}:`, error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
