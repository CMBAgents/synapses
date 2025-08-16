import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { domain, libraryName } = await request.json();
    
    if (!domain || !['astronomy', 'finance'].includes(domain)) {
      return NextResponse.json({ error: 'Invalid domain' }, { status: 400 });
    }

    if (!libraryName) {
      return NextResponse.json({ error: 'Library name is required' }, { status: 400 });
    }

    // Get library info from JSON
    const jsonPath = path.join(process.cwd(), 'app', 'data', `${domain}-libraries.json`);
    const contextDirName = domain;
    const contextDir = path.join(process.cwd(), 'public', 'context', contextDirName);
    
    if (!fs.existsSync(jsonPath)) {
      return NextResponse.json({ error: 'JSON file not found' }, { status: 404 });
    }

    const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
    const library = jsonData.libraries.find((lib: any) => lib.name === libraryName);
    
    if (!library) {
      return NextResponse.json({ error: 'Library not found' }, { status: 404 });
    }

    // Check if context file already exists
    const contextFileName = `${libraryName.split('/').pop()}-context.txt`;
    const contextFilePath = path.join(contextDir, contextFileName);
    
    if (fs.existsSync(contextFilePath)) {
      return NextResponse.json({ 
        success: true, 
        message: 'Context file already exists',
        contextFileName 
      });
    }

    // Create context directory if it doesn't exist
    if (!fs.existsSync(contextDir)) {
      fs.mkdirSync(contextDir, { recursive: true });
    }

    // Generate context using contextmaker with Git cloning
    try {
      console.log(`🔄 Generating context for ${libraryName}...`);
      
      // Extract the package name from the library name (e.g., "simonsobs/pixell" -> "pixell")
      const packageName = libraryName.split('/').pop();
      const githubUrl = library.github_url;
      
      // Create temporary directory for cloning
      const tempDir = await fs.promises.mkdtemp(path.join(os.tmpdir(), 'context-'));
      
      try {
        // Clone the repository
        console.log(`🔄 Cloning ${githubUrl}...`);
        const cloneResult = await execAsync(`git clone --depth 1 ${githubUrl} ${tempDir}`, {
          timeout: 300000 // 5 minutes timeout
        });
        
        if (cloneResult.stderr) {
          console.warn(`Git clone stderr: ${cloneResult.stderr}`);
        }
        
        // Run contextmaker using command line with --output
        const outputPath = path.join(contextDir, `${packageName}-context.txt`);
        
        console.log(`Running contextmaker for ${packageName} from ${tempDir}`);
        
        const { stdout, stderr } = await execAsync(`contextmaker ${packageName} --output "${outputPath}" --input-path "${tempDir}"`, {
          timeout: 300000 // 5 minutes timeout
        });
        
        if (stderr) {
          console.warn(`contextmaker stderr: ${stderr}`);
        }
        
        // Check if file was created
        if (fs.existsSync(outputPath)) {
          console.log(`✅ Context file generated: ${outputPath}`);
          
          // Update the library entry
          library.hasContextFile = true;
          library.contextFileName = `${packageName}-context.txt`;
          
          fs.writeFileSync(jsonPath, JSON.stringify(jsonData, null, 2));
          
          return NextResponse.json({ 
            success: true, 
            message: `Context file generated for ${libraryName}`,
            contextFileName: `${packageName}-context.txt`,
            outputPath: outputPath
          });
        } else {
          throw new Error('Context file was not created');
        }
        
      } finally {
        // Clean up temporary directory
        try {
          await fs.promises.rm(tempDir, { recursive: true, force: true });
        } catch (cleanupError) {
          console.warn(`Failed to clean up temp directory: ${cleanupError}`);
        }
      }
      
    } catch (error) {
      console.error(`Error generating context for ${libraryName}:`, error);
      return NextResponse.json({ 
        error: `Failed to generate context: ${error}` 
      }, { status: 500 });
    }
    
  } catch (error) {
    console.error('Error in generate-context API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 