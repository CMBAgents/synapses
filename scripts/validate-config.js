/**
 * This script validates that the config.json file matches the expected structure.
 * It helps catch errors before they cause build failures.
 */

const fs = require('fs');
const path = require('path');

// Function to validate that config.json has the required structure
function validateConfig() {
  console.log('Validating config.json structure...');

  try {
    // Load the config.json file
    const configPath = path.join(__dirname, '..', 'config.json');
    const configJson = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    // Check for required properties
    const requiredProps = [
      'programs',
      'defaultProgram',
      'availableModels',
      'defaultModelId'
    ];

    for (const prop of requiredProps) {
      if (!(prop in configJson)) {
        throw new Error(`Required property '${prop}' is missing in config.json`);
      }
    }

    // Validate programs array
    if (!Array.isArray(configJson.programs)) {
      throw new Error('Property "programs" must be an array');
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

    // Validate each program
    for (const program of configJson.programs) {
      if (!program.id) throw new Error(`Program is missing required 'id' property`);
      if (!program.name) throw new Error(`Program '${program.id}' is missing required 'name' property`);
      if (!program.description) throw new Error(`Program '${program.id}' is missing required 'description' property`);

      // contextFiles can be empty if combinedContextFile is a URL
      if (!program.contextFiles) {
        if (!program.combinedContextFile || !isUrl(program.combinedContextFile)) {
          throw new Error(`Program '${program.id}' is missing required 'contextFiles' property and does not have a URL-based 'combinedContextFile'`);
        }
      }

      if (!program.docsUrl) throw new Error(`Program '${program.id}' is missing required 'docsUrl' property`);
    }

    // Validate availableModels array
    if (!Array.isArray(configJson.availableModels)) {
      throw new Error('Property "availableModels" must be an array');
    }

    // Validate each model
    for (const model of configJson.availableModels) {
      if (!model.id) throw new Error(`Model is missing required 'id' property`);
      if (!model.name) throw new Error(`Model '${model.id}' is missing required 'name' property`);
    }

    // Validate defaultProgram exists in programs
    const programIds = configJson.programs.map(p => p.id);
    if (!programIds.includes(configJson.defaultProgram)) {
      throw new Error(`defaultProgram '${configJson.defaultProgram}' does not exist in the programs list`);
    }

    // Validate defaultModelId exists in availableModels
    const modelIds = configJson.availableModels.map(m => m.id);
    if (!modelIds.includes(configJson.defaultModelId)) {
      throw new Error(`defaultModelId '${configJson.defaultModelId}' does not exist in the availableModels list`);
    }

    console.log('✅ config.json is valid!');
    process.exit(0);
  } catch (error) {
    console.error('❌ Config validation failed:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

// Run the validation
validateConfig();
