const fs = require('fs');
const path = require('path');

function updateLibrariesWithContextStatus(domain) {
  try {
    const jsonPath = path.join(process.cwd(), 'app', 'data', `${domain}-libraries.json`);
    const contextDir = path.join(process.cwd(), 'app', 'context', domain);
    
    if (!fs.existsSync(jsonPath)) {
      console.log(`JSON file not found for domain: ${domain}`);
      return;
    }
    
    // Read the JSON file
    const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
    
    // Get existing context files
    const contextFiles = [];
    if (fs.existsSync(contextDir)) {
      const files = fs.readdirSync(contextDir);
      files.forEach(file => {
        if (file.endsWith('.txt')) {
          contextFiles.push(file);
        }
      });
    }
    
    console.log(`Found ${contextFiles.length} context files for ${domain}:`, contextFiles);
    
    // Update each library entry
    jsonData.libraries.forEach((library) => {
      // Create the expected context file name based on library name
      // Handle different naming patterns
      let contextFileName = '';
      
      // Try different naming patterns
      const patterns = [
        `${library.name.replace(/[\/\-\.]/g, '-')}-context.txt`,
        `${library.name.split('/').pop()}-context.txt`,
        `${library.name.split('/').pop().replace(/[\/\-\.]/g, '-')}-context.txt`
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
        console.log(`✓ ${library.name} has context file: ${contextFileName}`);
      } else {
        delete library.contextFileName;
        console.log(`✗ ${library.name} has no context file`);
      }
    });
    
    // Write back to the JSON file
    fs.writeFileSync(jsonPath, JSON.stringify(jsonData, null, 2));
    console.log(`\nUpdated context status for ${domain}: ${jsonData.libraries.length} libraries processed\n`);
    
    return jsonData;
  } catch (error) {
    console.error(`Error updating context status for domain ${domain}:`, error);
    return null;
  }
}

function updateAllLibrariesWithContextStatus() {
  const domains = ['astronomy', 'finance'];
  console.log('🔄 Updating context status for all domains...\n');
  
  domains.forEach(domain => {
    console.log(`📁 Processing ${domain} domain:`);
    updateLibrariesWithContextStatus(domain);
  });
  
  console.log('✅ Context status update completed!');
}

// Run the update
updateAllLibrariesWithContextStatus(); 