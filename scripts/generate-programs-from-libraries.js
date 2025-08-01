const fs = require('fs');
const path = require('path');

// Charger les données des bibliothèques
const astronomyData = JSON.parse(fs.readFileSync(path.join(__dirname, '../app/data/astronomy-libraries.json'), 'utf8'));
const financeData = JSON.parse(fs.readFileSync(path.join(__dirname, '../app/data/finance-libraries.json'), 'utf8'));

// Fonction pour créer un ID de programme à partir du nom
function createProgramId(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

// Fonction pour créer un programme à partir d'une bibliothèque
function createProgramFromLibrary(library, domain) {
  const programId = createProgramId(library.name);
  
  return {
    id: programId,
    name: library.name.split('/').pop(), // Prendre seulement la dernière partie du nom
    description: `${library.name} - ${domain === 'astronomy' ? 'Astronomy' : 'Finance'} library with ${library.stars} stars`,
    contextFiles: [],
    combinedContextFile: library.hasContextFile ? 
      `/context/${domain}/${library.contextFileName}` : 
      undefined,
    docsUrl: library.github_url,
    extraSystemPrompt: `You are an expert on ${library.name}. Use the provided documentation to help users with this ${domain} library.`
  };
}

// Créer les programmes pour l'astronomie
const astronomyPrograms = astronomyData.libraries.map(lib => 
  createProgramFromLibrary(lib, 'astronomy')
);

// Créer les programmes pour la finance
const financePrograms = financeData.libraries.map(lib => 
  createProgramFromLibrary(lib, 'finance')
);

// Combiner tous les programmes
const allPrograms = [...astronomyPrograms, ...financePrograms];

// Charger la configuration existante
const configPath = path.join(__dirname, '../config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Remplacer les programmes existants
config.programs = allPrograms;

// Changer le programme par défaut vers la première bibliothèque d'astronomie
config.defaultProgram = astronomyPrograms[0].id;

// Sauvegarder la nouvelle configuration
fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

console.log(`✅ Généré ${allPrograms.length} programmes:`);
console.log(`   - Astronomy: ${astronomyPrograms.length} programmes`);
console.log(`   - Finance: ${financePrograms.length} programmes`);
console.log(`   - Programme par défaut: ${config.defaultProgram}`);
console.log(`\n📁 Configuration sauvegardée dans: ${configPath}`); 