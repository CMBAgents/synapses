const fs = require('fs');
const path = require('path');

// Read programs from config.json
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const programs = config.programs;

console.log('Generating embedded context module...');

// Source directory for context files
const contextDir = path.join(__dirname, '..', 'context');

// Function to check if a string is a URL
function isUrl(str) {
  try {
    new URL(str);
    return true;
  } catch (e) {
    return false;
  }
}

// Generate combined context content
const combinedContexts = {};

for (const program of programs) {
  try {
    // Skip if combinedContextFile is a URL - we'll fetch it at runtime
    if (program.combinedContextFile && isUrl(program.combinedContextFile)) {
      console.log(`Skipping embedded context generation for ${program.id} - using URL: ${program.combinedContextFile}`);
      // Add a placeholder to indicate this is a URL-based context
      combinedContexts[program.id] = `This context is loaded from URL: ${program.combinedContextFile}`;
      continue;
    }

    // Skip if contextFiles is empty or not an array
    if (!program.contextFiles || !Array.isArray(program.contextFiles) || program.contextFiles.length === 0) {
      console.log(`Skipping embedded context generation for ${program.id} - no context files defined`);
      combinedContexts[program.id] = `No context files defined for ${program.id}`;
      continue;
    }

    const contents = program.contextFiles.map(file => {
      const filePath = path.join(contextDir, file);
      if (!fs.existsSync(filePath)) {
        console.error(`Context file not found: ${filePath}`);
        return `Context file ${file} not found.`;
      }
      return fs.readFileSync(filePath, 'utf8');
    });

    const combinedContent = contents.join('\n\n---\n\n');
    combinedContexts[program.id] = combinedContent;

    console.log(`Generated embedded context for ${program.id} (${combinedContent.length} bytes)`);
  } catch (error) {
    console.error(`Error generating embedded context for ${program.id}:`, error);
    // Add an error message as the context
    combinedContexts[program.id] = `Error generating context for ${program.id}: ${error.message}`;
  }
}

// Generate TypeScript module with embedded context
const tsContent = `// This file is auto-generated. Do not edit directly.
// Generated on ${new Date().toISOString()}

/**
 * Embedded context content for each program
 * This avoids having to load context files at runtime
 */
export const embeddedContexts: Record<string, string> = {
${Object.entries(combinedContexts).map(([id, content]) => {
  // Use JSON.stringify to properly escape all special characters
  return `  '${id}': ${JSON.stringify(content)},`;
}).join('\n')}
};

/**
 * Get the embedded context for a program
 * @param programId The ID of the program
 * @returns The embedded context content or undefined if not found
 */
export function getEmbeddedContext(programId: string): string | undefined {
  return embeddedContexts[programId];
}
`;

// Write the TypeScript file
const outputPath = path.join(__dirname, '..', 'app', 'utils', 'embedded-context.ts');
fs.writeFileSync(outputPath, tsContent, 'utf8');

console.log(`Generated embedded context module at ${outputPath}`);
