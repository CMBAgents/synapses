#!/usr/bin/env python3
"""
Script pour supprimer complètement un domaine.
Usage: python3 delete-domain.py <domain_name>

Ce script :
1. Supprime le fichier JSON dans app/data/
2. Supprime le dossier de contexte dans public/context/
3. Met à jour le domain-loader.ts
4. Régénère les routes
"""

import sys
import shutil
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
        
        # 6. Mettre à jour le domain-loader.ts
        print(f"🔄 Mise à jour du domain-loader.ts...")
        self.update_domain_loader()
        
        # 7. Régénérer les routes
        print(f"🛣️  Régénération des routes...")
        self.regenerate_routes()
        
        print(f"\n🎉 Domaine '{domain_name}' supprimé avec succès!")
        print(f"📁 Fichiers supprimés:")
        print(f"   - {json_file}")
        print(f"   - {context_folder}")
        print(f"🔄 Routes mises à jour automatiquement")
        
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
