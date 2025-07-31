const fs = require('fs');
const path = require('path');

function updateContextStatus() {
  const domains = ['astronomy', 'finance'];
  
  domains.forEach(domain => {
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
    
    // Update each library entry
    jsonData.libraries.forEach(library => {
      // Check if there's a context file for this library
      const contextFileName = `${library.name.replace(/[\/\-\.]/g, '-')}-context.txt`;
      const hasContextFile = contextFiles.includes(contextFileName);
      
      // Update the library entry
      library.hasContextFile = hasContextFile;
      if (hasContextFile) {
        library.contextFileName = contextFileName;
      }
    });
    
    // Write back to the JSON file
    fs.writeFileSync(jsonPath, JSON.stringify(jsonData, null, 2));
    console.log(`Updated context status for ${domain}: ${jsonData.libraries.length} libraries processed`);
  });
}

// Run the update
updateContextStatus(); 