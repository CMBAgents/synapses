const fs = require('fs');
const path = require('path');

// Read programs from config.json
const configPath = path.join(__dirname, '..', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const programs = config.programs;

console.log('Using programs:', programs);

// Ensure public/context directory exists
const publicContextDir = path.join(__dirname, '..', 'public', 'context');
if (!fs.existsSync(publicContextDir)) {
  fs.mkdirSync(publicContextDir, { recursive: true });
}

// Copy individual context files to public/context
const contextDir = path.join(__dirname, '..', 'context');
const contextFiles = fs.readdirSync(contextDir);

for (const file of contextFiles) {
  const sourcePath = path.join(contextDir, file);
  const destPath = path.join(publicContextDir, file);

  if (fs.statSync(sourcePath).isFile()) {
    fs.copyFileSync(sourcePath, destPath);
    console.log(`Copied ${file} to public/context`);
  }
}

// Function to check if a string is a URL
function isUrl(str) {
  try {
    new URL(str);
    return true;
  } catch (e) {
    return false;
  }
}

// Generate combined context files
for (const program of programs) {
  try {
    // Skip if combinedContextFile is a URL
    if (program.combinedContextFile && isUrl(program.combinedContextFile)) {
      console.log(`Skipping combined context generation for ${program.id} - using URL: ${program.combinedContextFile}`);
      continue;
    }

    // Skip if contextFiles is empty or not an array
    if (!program.contextFiles || !Array.isArray(program.contextFiles) || program.contextFiles.length === 0) {
      console.log(`Skipping combined context generation for ${program.id} - no context files defined`);
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

    // Skip if no combinedContextFile is defined
    if (!program.combinedContextFile) {
      console.log(`Skipping combined context file output for ${program.id} - no combinedContextFile defined`);
      continue;
    }

    const outputPath = path.join(publicContextDir, program.combinedContextFile);

    fs.writeFileSync(outputPath, combinedContent, 'utf8');
    console.log(`Generated combined context file for ${program.id}: ${program.combinedContextFile}`);
  } catch (error) {
    console.error(`Error generating combined context for ${program.id}:`, error);
  }
}

console.log('Context files built successfully');
