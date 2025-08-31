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
        
        print(f"📝 ID du domaine: {domain_id}")
        print(f"📝 Nom d'affichage: {display_name}")
        
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
        
        # 6. Appeler le système de maintenance
        if self.config.maintenance.get("auto_call", True):
            self.maintenance_integrator.call_maintenance_system(domain_id)
        
        # 6. Générer les routes
        print(f"🛣️  Génération des routes...")
        self.generate_routes()
        
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
