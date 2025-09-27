import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import { isDomainSupported } from '@/app/config/domains';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { domain } = await request.json();
    
    if (!domain || !isDomainSupported(domain)) {
      return NextResponse.json({ error: 'Invalid domain' }, { status: 400 });
    }

    // Get library info from JSON
    const jsonPath = path.join(process.cwd(), 'app', 'data', `${domain}-libraries.json`);
    const contextDirName = domain;
    const contextDir = path.join(process.cwd(), 'public', 'context', contextDirName);
    
    if (!fs.existsSync(jsonPath)) {
      return NextResponse.json({ error: 'JSON file not found' }, { status: 404 });
    }

    const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
    
    // Create context directory if it doesn't exist
    if (!fs.existsSync(contextDir)) {
      fs.mkdirSync(contextDir, { recursive: true });
    }

    // Get existing context files
    const existingContextFiles: string[] = [];
    if (fs.existsSync(contextDir)) {
      const files = fs.readdirSync(contextDir);
      files.forEach(file => {
        if (file.endsWith('.txt')) {
          existingContextFiles.push(file);
        }
      });
    }

    const results = {
      total: 0,
      generated: 0,
      failed: 0,
      alreadyExists: 0,
      errors: [] as string[]
    };

    console.log(`🔄 Generating missing contexts for ${domain}...`);
    console.log(`Found ${existingContextFiles.length} existing context files`);

    for (const library of jsonData.libraries) {
      results.total++;
      const libraryName = library.name;
      const packageName = libraryName.split('/').pop();
      const contextFileName = `${packageName}-context.txt`;
      const finalOutputPath = path.join(contextDir, contextFileName);
      const tempContextsDir = path.join(process.cwd(), 'temp', 'contexts');

      // Skip if context file already exists
      if (existingContextFiles.includes(contextFileName)) {
        results.alreadyExists++;
        console.log(`✅ ${libraryName}: Context file already exists`);
        continue;
      }

      try {
        console.log(`🔄 Generating context for ${libraryName}...`);
        
        // Create temporary directory for cloning
        const tempDir = await fs.promises.mkdtemp(path.join(os.tmpdir(), 'context-'));
        
        try {
          // Clone the repository
          console.log(`🔄 Cloning ${library.github_url}...`);
          const cloneResult = await execAsync(`git clone --depth 1 ${library.github_url} ${tempDir}`, {
            timeout: 300000 // 5 minutes timeout
          });
          
          if (cloneResult.stderr) {
            console.warn(`Git clone stderr for ${libraryName}: ${cloneResult.stderr}`);
          }
          
          // Run contextmaker using command line with --output
          const tempOutputDir = path.join(tempContextsDir, `${packageName}-temp`);
          
          // Ensure the temp contexts directory exists
          if (!fs.existsSync(tempContextsDir)) {
            fs.mkdirSync(tempContextsDir, { recursive: true });
          }
          
          console.log(`Running contextmaker for ${packageName} from ${tempDir}`);
          console.log(`Temporary output dir: ${tempOutputDir}`);
          console.log(`Final output: ${finalOutputPath}`);
          
          const { stdout, stderr } = await execAsync(`PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH" contextmaker ${packageName} --output "${tempOutputDir}" --input-path "${tempDir}" --rough`, {
            timeout: 300000 // 5 minutes timeout
          });
          
          if (stderr) {
            console.warn(`contextmaker stderr for ${libraryName}: ${stderr}`);
          }
          
          // Check if file was created and move it to final location
          const generatedFile = path.join(tempOutputDir, `${packageName}.txt`);
          if (fs.existsSync(generatedFile)) {
            // Move the file to the final location
            fs.copyFileSync(generatedFile, finalOutputPath);
            console.log(`✅ ${libraryName}: Context file generated successfully`);
            
            // Clean up temporary directory
            fs.rmSync(tempOutputDir, { recursive: true, force: true });
            
            results.generated++;
            
            // Update the library entry
            library.hasContextFile = true;
            library.contextFileName = contextFileName;
          } else {
            console.log(`❌ ${libraryName}: Context file not created`);
            results.failed++;
            results.errors.push(`${libraryName}: File not created`);
          }
          
        } finally {
          // Clean up temporary directory
          try {
            await fs.promises.rm(tempDir, { recursive: true, force: true });
          } catch (cleanupError) {
            console.warn(`Failed to clean up temp directory for ${libraryName}: ${cleanupError}`);
          }
        }
        
      } catch (error) {
        console.error(`❌ ${libraryName}: Error generating context - ${error}`);
        results.failed++;
        results.errors.push(`${libraryName}: ${error}`);
      }
    }

    // Save updated JSON
    fs.writeFileSync(jsonPath, JSON.stringify(jsonData, null, 2));
    
    console.log(`📊 ${domain} Summary:`);
    console.log(`   Total libraries: ${results.total}`);
    console.log(`   Already have context: ${results.alreadyExists}`);
    console.log(`   Successfully generated: ${results.generated}`);
    console.log(`   Failed: ${results.failed}`);

    return NextResponse.json({ 
      success: true, 
      message: `Context generation completed for ${domain}`,
      results
    });
    
  } catch (error) {
    console.error('Error in generate-all-contexts API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 