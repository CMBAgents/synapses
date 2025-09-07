#!/usr/bin/env python3
"""
Script unifié pour créer un nouveau domaine complet.
Usage: python3 create-domain.py <domain_name>

Ce script :
1. Crée le fichier JSON avec 10 librairies d'exemple
2. Appelle le système de maintenance
3. Génère les routes nécessaires
4. Met à jour le domain-loader.ts
"""

import sys
import subprocess
import re
import json
from pathlib import Path
import logging

# Import des utilitaires partagés
import importlib.util
spec = importlib.util.spec_from_file_location("domain_utils", Path(__file__).parent / "domain-utils.py")
domain_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(domain_utils)

DomainSystemConfig = domain_utils.DomainSystemConfig
LibraryGenerator = domain_utils.LibraryGenerator
MaintenanceIntegrator = domain_utils.MaintenanceIntegrator
validate_domain_name = domain_utils.validate_domain_name

class DomainCreator:
    def __init__(self):
        self.config = DomainSystemConfig()
        self.library_generator = LibraryGenerator(self.config)
        self.maintenance_integrator = MaintenanceIntegrator(self.config)
        self.setup_logging()
    
    def setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_domain(self, domain_name: str):
        """Crée un nouveau domaine complet"""
        print(f"🚀 Création du domaine '{domain_name}'...")
        
        # 1. Validation et normalisation
        domain_id = validate_domain_name(domain_name)
        display_name = self.config.get_domain_display_name(domain_id)
        description = self.config.get_domain_description(domain_id)
        
        print(f"📝 ID du domaine: {domain_id}")
        print(f"📝 Nom d'affichage: {display_name}")
        print(f"📝 Description: {description}")
        
        # 2. Vérifier si le domaine existe déjà
        data_dir = self.config.get_path("data_dir")
        json_file = data_dir / f"{domain_id}-libraries.json"
        
        if json_file.exists():
            print(f"⚠️  Le domaine '{domain_id}' existe déjà!")
            response = input("Voulez-vous le remplacer ? (y/N): ")
            if response.lower() != 'y':
                print("❌ Création annulée")
                return
        
        # 3. Générer les librairies
        library_count = self.config.get_template_setting("library_count")
        if self.config.is_special_domain(domain_id):
            special_config = self.config.special_domains[domain_id]
            if special_config.get("preserve_libraries", False):
                print(f"🔒 Domaine spécial '{domain_id}' - préservation des librairies existantes")
                # Charger les librairies existantes si le fichier existe
                if json_file.exists():
                    with open(json_file, 'r', encoding='utf-8') as f:
                        import json
                        existing_data = json.load(f)
                        libraries = existing_data.get("libraries", [])
                        print(f"📚 {len(libraries)} librairies existantes préservées")
                else:
                    libraries = self.library_generator.generate_sample_libraries(domain_id, library_count)
            else:
                libraries = self.library_generator.generate_sample_libraries(domain_id, library_count)
        else:
            libraries = self.library_generator.generate_sample_libraries(domain_id, library_count)
        
        print(f"📚 Génération de {len(libraries)} librairies...")
        
        # 4. Créer le fichier JSON
        domain_data = self.library_generator.create_domain_json(domain_id, display_name, libraries)
        
        # Créer le dossier data s'il n'existe pas
        data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(domain_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fichier JSON créé: {json_file}")
        
        # 5. Créer le dossier de contexte
        print(f"📁 Création du dossier de contexte...")
        context_dir = Path.cwd().parent.parent / "public" / "context" / domain_id
        context_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Dossier de contexte créé: {context_dir}")
        
        # 6. Mettre à jour la configuration dans config.json
        print(f"⚙️  Mise à jour de la configuration...")
        self.update_config_json(domain_id, display_name, description)
        
        # 7. Appeler le système de maintenance
        if self.config.maintenance.get("auto_call", True):
            self.maintenance_integrator.call_maintenance_system(domain_id)
        
        # 6. Générer les routes
        print(f"🛣️  Génération des routes...")
        self.generate_routes()
        
        # 7. Mettre à jour le script generate-programs-from-libraries.py
        print(f"🔄 Mise à jour du script de génération...")
        self.update_generate_script(domain_id)
        
        print(f"\n🎉 Domaine '{domain_name}' créé avec succès!")
        print(f"📁 Fichier de données: {json_file}")
        print(f"🌐 Routes disponibles: /chat/{domain_id} et /leaderboard/{domain_id}")
        print(f"🔧 Maintenance: {'✅ Automatique' if self.config.maintenance.get('auto_call') else '❌ Manuel'}")
    
    def generate_routes(self):
        """Génère les routes en appelant le script existant"""
        try:
            script_path = Path(__file__).parent / "generate-domain-routes.py"
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            
            if result.returncode == 0:
                print("✅ Routes générées avec succès")
            else:
                print(f"⚠️  Génération des routes terminée avec des avertissements")
                if result.stderr:
                    print(f"Erreurs: {result.stderr}")
        except Exception as e:
            print(f"❌ Erreur lors de la génération des routes: {e}")
    
    def update_generate_script(self, domain_id: str):
        """Met à jour le script generate-programs-from-libraries.py pour inclure le nouveau domaine"""
        try:
            script_path = self.project_root / "scripts" / "core" / "generate-programs-from-libraries.py"
            
            if not script_path.exists():
                print(f"⚠️  Script generate-programs-from-libraries.py non trouvé: {script_path}")
                return
            
            # Lire le contenu actuel
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si le domaine est déjà présent
            if f"{domain_id}-libraries.json" in content:
                print(f"✅ Domaine '{domain_id}' déjà présent dans le script")
                return
            
            # Créer les lignes à ajouter
            domain_display_name = self.config.get_domain_display_name(domain_id)
            
            # Ajouter l'import du fichier JSON
            import_line = f"    with open('app/data/{domain_id}-libraries.json', 'r') as f:\n"
            import_line += f"        {domain_id}_data = json.load(f)\n"
            
            # Ajouter la création des programmes
            program_line = f"    # Créer les programmes pour {domain_display_name}\n"
            program_line += f"    {domain_id}_programs = [create_program_from_library(lib, '{domain_id}') \n"
            program_line += f"                         for lib in {domain_id}_data['libraries']]\n"
            
            # Trouver l'endroit pour insérer les imports (après le dernier with open)
            import_pattern = r"(    with open\('app/data/[^']+\.json', 'r'\) as f:\n        \w+_data = json\.load\(f\)\n)"
            import_match = list(re.finditer(import_pattern, content))
            
            if import_match:
                last_import = import_match[-1]
                insert_pos = last_import.end()
                content = content[:insert_pos] + "\n" + import_line + content[insert_pos:]
            
            # Trouver l'endroit pour insérer la création des programmes (après le dernier programme)
            program_pattern = r"(    \w+_programs = \[create_program_from_library\(lib, '[^']+'\) \n                         for lib in \w+_data\['libraries'\]\]\n)"
            program_match = list(re.finditer(program_pattern, content))
            
            if program_match:
                last_program = program_match[-1]
                insert_pos = last_program.end()
                content = content[:insert_pos] + "\n" + program_line + content[insert_pos:]
            
            # Mettre à jour la ligne all_programs
            all_programs_pattern = r"(all_programs = [^+]+ \+ [^+]+ \+ [^+]+ \+ [^+]+)"
            all_programs_replacement = f"all_programs = astronomy_programs + finance_programs + biochemistry_programs + machinelearning_programs + {domain_id}_programs"
            content = re.sub(all_programs_pattern, all_programs_replacement, content)
            
            # Mettre à jour les prints
            print_pattern = r"(    print\(f\"   - Machine Learning: \{len\(machinelearning_programs\)\} programmes\"\)\n)"
            print_replacement = f"    print(f\"   - Machine Learning: {{len(machinelearning_programs)}} programmes\")\n    print(f\"   - {domain_display_name}: {{len({domain_id}_programs)}} programmes\")\n"
            content = re.sub(print_pattern, print_replacement, content)
            
            # Sauvegarder le fichier modifié
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Script generate-programs-from-libraries.py mis à jour avec le domaine '{domain_id}'")
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du script: {e}")
    
    def update_config_json(self, domain_id: str, display_name: str, description: str):
        """Met à jour la section domaines dans config.json"""
        try:
            config_file = Path.cwd().parent.parent / "config.json"
            
            if not config_file.exists():
                print(f"⚠️  Fichier config.json non trouvé: {config_file}")
                return
            
            # Charger la configuration existante
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Initialiser la section domaines si elle n'existe pas
            if 'domains' not in config:
                config['domains'] = {
                    'supported': [],
                    'displayNames': {},
                    'descriptions': {}
                }
            
            # Ajouter le nouveau domaine s'il n'existe pas déjà
            if domain_id not in config['domains']['supported']:
                config['domains']['supported'].append(domain_id)
                config['domains']['displayNames'][domain_id] = display_name
                config['domains']['descriptions'][domain_id] = description
                
                # Sauvegarder la configuration
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Domaine '{domain_id}' ajouté à config.json")
            else:
                print(f"✅ Domaine '{domain_id}' déjà présent dans config.json")
                
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de config.json: {e}")

def main():
    """Fonction principale"""
    if len(sys.argv) != 2:
        print("Usage: python3 create-domain.py <domain_name>")
        print("Exemples:")
        print("  python3 create-domain.py 'Physics'")
        print("  python3 create-domain.py 'Computer Science'")
        print("  python3 create-domain.py 'Medicine & Healthcare'")
        sys.exit(1)
    
    domain_name = sys.argv[1]
    
    try:
        domain_creator = DomainCreator()
        domain_creator.create_domain(domain_name)
    except KeyboardInterrupt:
        print("\n❌ Création annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la création du domaine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
