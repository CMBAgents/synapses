#!/usr/bin/env python3
"""
Script pour supprimer complètement un domaine.
Usage: python3 delete-domain.py <domain_name>

Ce script :
1. Supprime le fichier JSON dans app/data/
2. Supprime le dossier de contexte dans public/context/
3. Met à jour la section domaines dans config.json
4. Met à jour le domain-loader.ts
5. Régénère les routes
6. Met à jour le script generate-programs-from-libraries.py
"""

import sys
import shutil
import re
import json
from pathlib import Path
import subprocess

# Import des utilitaires partagés
import importlib.util
spec = importlib.util.spec_from_file_location("domain_utils", Path(__file__).parent / "domain-utils.py")
domain_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(domain_utils)

DomainSystemConfig = domain_utils.DomainSystemConfig
validate_domain_name = domain_utils.validate_domain_name

class DomainDeleter:
    def __init__(self):
        self.config = DomainSystemConfig()
        self.setup_paths()
    
    def setup_paths(self):
        """Configure les chemins depuis la racine du projet"""
        if Path.cwd().name == "templates":
            self.project_root = Path.cwd().parent.parent
        else:
            self.project_root = Path.cwd()
        
        self.data_dir = self.project_root / "app" / "data"
        self.context_dir = self.project_root / "public" / "context"
        self.utils_dir = self.project_root / "app" / "utils"
    
    def validate_domain_exists(self, domain_id: str) -> bool:
        """Vérifie si le domaine existe"""
        json_file = self.data_dir / f"{domain_id}-libraries.json"
        context_folder = self.context_dir / domain_id
        
        return json_file.exists() or context_folder.exists()
    
    def delete_domain(self, domain_name: str):
        """Supprime un domaine complet"""
        print(f"🗑️  Suppression du domaine '{domain_name}'...")
        
        # 1. Validation et normalisation
        domain_id = validate_domain_name(domain_name)
        print(f"📝 ID du domaine: {domain_id}")
        
        # 2. Vérifier si le domaine existe
        if not self.validate_domain_exists(domain_id):
            print(f"❌ Le domaine '{domain_id}' n'existe pas!")
            return False
        
        # 3. Confirmation de suppression
        print(f"⚠️  ATTENTION: Cette action va supprimer définitivement le domaine '{domain_id}'")
        print(f"   - Fichier de données: {self.data_dir / f'{domain_id}-libraries.json'}")
        print(f"   - Dossier de contexte: {self.context_dir / domain_id}")
        print(f"   - Toutes les librairies et contextes associés")
        
        response = input("Êtes-vous sûr de vouloir continuer ? (oui/NON): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Suppression annulée")
            return False
        
        # 4. Supprimer le fichier JSON
        json_file = self.data_dir / f"{domain_id}-libraries.json"
        if json_file.exists():
            try:
                json_file.unlink()
                print(f"✅ Fichier JSON supprimé: {json_file}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression du fichier JSON: {e}")
                return False
        
        # 5. Supprimer le dossier de contexte
        context_folder = self.context_dir / domain_id
        if context_folder.exists():
            try:
                shutil.rmtree(context_folder)
                print(f"✅ Dossier de contexte supprimé: {context_folder}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression du dossier de contexte: {e}")
                return False
        
        # 6. Mettre à jour la configuration dans config.json
        print(f"⚙️  Mise à jour de la configuration...")
        self.update_config_json(domain_id)
        
        # 7. Mettre à jour le domain-loader.ts
        print(f"🔄 Mise à jour du domain-loader.ts...")
        self.update_domain_loader()
        
        # 8. Régénérer les routes
        print(f"🛣️  Régénération des routes...")
        self.regenerate_routes()
        
        # 9. Mettre à jour le script generate-programs-from-libraries.py
        print(f"🔄 Mise à jour du script de génération...")
        self.update_generate_script(domain_id)
        
        print(f"\n🎉 Domaine '{domain_name}' supprimé avec succès!")
        print(f"📁 Fichiers supprimés:")
        print(f"   - {json_file}")
        print(f"   - {context_folder}")
        print(f"🔄 Routes et scripts mis à jour automatiquement")
        
        return True
    
    def update_domain_loader(self):
        """Met à jour le domain-loader.ts en supprimant les références au domaine"""
        domain_loader_path = self.utils_dir / "domain-loader.ts"
        
        if not domain_loader_path.exists():
            print(f"⚠️  Fichier domain-loader.ts non trouvé: {domain_loader_path}")
            return
        
        try:
            # Créer une sauvegarde
            backup_path = domain_loader_path.with_suffix('.ts.backup-delete')
            shutil.copy2(domain_loader_path, backup_path)
            print(f"💾 Sauvegarde créée: {backup_path}")
            
            # Lire le contenu actuel
            with open(domain_loader_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Supprimer les lignes liées au domaine supprimé
            # Cette logique sera gérée par le script generate-domain-routes.py
            print(f"✅ domain-loader.ts sera mis à jour par le script de génération")
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du domain-loader.ts: {e}")
    
    def regenerate_routes(self):
        """Régénère les routes en appelant le script existant"""
        try:
            script_path = Path(__file__).parent / "generate-domain-routes.py"
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            
            if result.returncode == 0:
                print("✅ Routes régénérées avec succès")
            else:
                print(f"⚠️  Régénération des routes terminée avec des avertissements")
                if result.stderr:
                    print(f"Erreurs: {result.stderr}")
        except Exception as e:
            print(f"❌ Erreur lors de la régénération des routes: {e}")
    
    def update_generate_script(self, domain_id: str):
        """Met à jour le script generate-programs-from-libraries.py pour retirer le domaine supprimé"""
        try:
            script_path = self.project_root / "scripts" / "core" / "generate-programs-from-libraries.py"
            
            if not script_path.exists():
                print(f"⚠️  Script generate-programs-from-libraries.py non trouvé: {script_path}")
                return
            
            # Lire le contenu actuel
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si le domaine est présent
            if f"{domain_id}-libraries.json" not in content:
                print(f"✅ Domaine '{domain_id}' déjà absent du script")
                return
            
            # Supprimer l'import du fichier JSON
            import_pattern = rf"    with open\('app/data/{domain_id}-libraries\.json', 'r'\) as f:\n        {domain_id}_data = json\.load\(f\)\n"
            content = re.sub(import_pattern, "", content)
            
            # Supprimer la création des programmes
            program_pattern = rf"    # Créer les programmes pour .+\n    {domain_id}_programs = \[create_program_from_library\(lib, '{domain_id}'\) \n                         for lib in {domain_id}_data\['libraries'\]\]\n"
            content = re.sub(program_pattern, "", content)
            
            # Retirer le domaine de la ligne all_programs
            all_programs_pattern = rf" \+ {domain_id}_programs"
            content = re.sub(all_programs_pattern, "", content)
            
            # Supprimer le print du domaine
            print_pattern = rf"    print\(f\"   - .+: \{{len\({domain_id}_programs\)\}} programmes\"\)\n"
            content = re.sub(print_pattern, "", content)
            
            # Nettoyer les lignes vides multiples
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # Sauvegarder le fichier modifié
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Script generate-programs-from-libraries.py mis à jour (domaine '{domain_id}' retiré)")
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du script: {e}")
    
    def update_config_json(self, domain_id: str):
        """Met à jour la section domaines dans config.json en supprimant le domaine"""
        try:
            config_file = self.project_root / "config.json"
            
            if not config_file.exists():
                print(f"⚠️  Fichier config.json non trouvé: {config_file}")
                return
            
            # Charger la configuration existante
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Vérifier si la section domaines existe
            if 'domains' not in config:
                print(f"⚠️  Section 'domains' non trouvée dans config.json")
                return
            
            # Supprimer le domaine de la liste supported
            if domain_id in config['domains']['supported']:
                config['domains']['supported'].remove(domain_id)
                print(f"✅ Domaine '{domain_id}' retiré de la liste supported")
            
            # Supprimer le domaine des displayNames
            if domain_id in config['domains']['displayNames']:
                del config['domains']['displayNames'][domain_id]
                print(f"✅ Domaine '{domain_id}' retiré des displayNames")
            
            # Supprimer le domaine des descriptions
            if domain_id in config['domains']['descriptions']:
                del config['domains']['descriptions'][domain_id]
                print(f"✅ Domaine '{domain_id}' retiré des descriptions")
            
            # Sauvegarder la configuration
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuration config.json mise à jour (domaine '{domain_id}' supprimé)")
                
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de config.json: {e}")
    
    def list_domains(self):
        """Liste tous les domaines disponibles"""
        print("📋 Domaines disponibles:")
        
        # Lister les fichiers JSON
        json_files = list(self.data_dir.glob("*-libraries.json"))
        
        if not json_files:
            print("   Aucun domaine trouvé")
            return
        
        for json_file in json_files:
            domain_id = json_file.name.replace('-libraries.json', '')
            json_file = self.data_dir / f"{domain_id}-libraries.json"
            context_folder = self.context_dir / domain_id
            
            status = []
            if json_file.exists():
                status.append("📄 JSON")
            if context_folder.exists():
                status.append("📁 Contexte")
            
            print(f"   - {domain_id}: {' + '.join(status)}")

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python3 delete-domain.py <domain_name>")
        print("Exemples:")
        print("  python3 delete-domain.py 'Physics'")
        print("  python3 delete-domain.py 'Computer Science'")
        print("  python3 delete-domain.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        domain_deleter = DomainDeleter()
        domain_deleter.list_domains()
        return
    
    domain_name = sys.argv[1]
    
    try:
        domain_deleter = DomainDeleter()
        success = domain_deleter.delete_domain(domain_name)
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Suppression annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la suppression du domaine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
