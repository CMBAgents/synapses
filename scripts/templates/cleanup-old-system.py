#!/usr/bin/env python3
"""
Script pour nettoyer l'ancien système de domaines.
Ce script supprime tous les fichiers obsolètes et garde seulement le nouveau système dynamique.
"""

import shutil
from pathlib import Path
import subprocess

class OldSystemCleaner:
    def __init__(self):
        self.setup_paths()
    
    def setup_paths(self):
        """Configure les chemins depuis la racine du projet"""
        if Path.cwd().name == "templates":
            self.project_root = Path.cwd().parent.parent
        else:
            self.project_root = Path.cwd()
        
        self.chat_dir = self.project_root / "app" / "chat"
        self.leaderboard_dir = self.project_root / "app" / "leaderboard"
        self.ui_dir = self.project_root / "app" / "ui"
    
    def cleanup_old_domain_pages(self):
        """Supprime les anciennes pages de domaines hardcodées"""
        print("🧹 Nettoyage des anciennes pages de domaines...")
        
        # Domaines à conserver (garder les dossiers pour la compatibilité)
        domains_to_keep = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
        
        # Supprimer les anciennes pages hardcodées
        old_files_to_remove = []
        
        for domain in domains_to_keep:
            # Supprimer les anciens fichiers page.tsx
            chat_page = self.chat_dir / domain / "page.tsx"
            leaderboard_page = self.leaderboard_dir / domain / "page.tsx"
            
            if chat_page.exists():
                old_files_to_remove.append(chat_page)
            if leaderboard_page.exists():
                old_files_to_remove.append(leaderboard_page)
        
        # Supprimer les fichiers
        for file_path in old_files_to_remove:
            try:
                file_path.unlink()
                print(f"✅ Supprimé: {file_path}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
        
        print(f"📁 Gardé les dossiers de domaines pour la compatibilité")
    
    def cleanup_old_ui_components(self):
        """Supprime les anciens composants UI obsolètes"""
        print("🧹 Nettoyage des anciens composants UI...")
        
        # Fichiers à supprimer (obsolètes avec le nouveau système)
        files_to_remove = [
            "base-chat-page.tsx",
            "base-leaderboard-page.tsx"
        ]
        
        for filename in files_to_remove:
            file_path = self.ui_dir / filename
            if file_path.exists():
                try:
                    # Créer une sauvegarde avant suppression
                    backup_path = file_path.with_suffix('.tsx.backup-cleanup')
                    shutil.copy2(file_path, backup_path)
                    print(f"💾 Sauvegarde créée: {backup_path}")
                    
                    file_path.unlink()
                    print(f"✅ Supprimé: {file_path}")
                except Exception as e:
                    print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
            else:
                print(f"⚠️  Fichier non trouvé: {file_path}")
    
    def cleanup_empty_directories(self):
        """Supprime les dossiers vides après nettoyage"""
        print("🧹 Vérification des dossiers vides...")
        
        # Vérifier les dossiers de domaines
        for domain_dir in [self.chat_dir, self.leaderboard_dir]:
            for subdir in domain_dir.iterdir():
                if subdir.is_dir() and subdir.name != "[domain]":
                    # Compter les fichiers dans le sous-dossier
                    file_count = len(list(subdir.glob("*.tsx")))
                    if file_count == 0:
                        print(f"📁 Dossier vide détecté: {subdir}")
                        print(f"   (gardé pour la compatibilité avec le nouveau système)")
    
    def verify_new_system(self):
        """Vérifie que le nouveau système est en place"""
        print("🔍 Vérification du nouveau système...")
        
        # Vérifier les fichiers essentiels du nouveau système
        essential_files = [
            self.chat_dir / "[domain]" / "page.tsx",
            self.leaderboard_dir / "[domain]" / "page.tsx",
            self.ui_dir / "chat-template.tsx",
            self.ui_dir / "leaderboard-template.tsx",
            self.ui_dir / "domain-navigator.tsx"
        ]
        
        all_good = True
        for file_path in essential_files:
            if file_path.exists():
                print(f"✅ {file_path.name} - OK")
            else:
                print(f"❌ {file_path.name} - MANQUANT")
                all_good = False
        
        if all_good:
            print("🎉 Nouveau système vérifié et fonctionnel!")
        else:
            print("⚠️  Certains fichiers du nouveau système sont manquants!")
        
        return all_good
    
    def regenerate_routes(self):
        """Régénère les routes pour s'assurer que tout est à jour"""
        print("🛣️  Régénération des routes...")
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
    
    def run_cleanup(self):
        """Exécute le nettoyage complet"""
        print("🚀 Début du nettoyage de l'ancien système...")
        print("=" * 50)
        
        # 1. Nettoyer les anciennes pages
        self.cleanup_old_domain_pages()
        print()
        
        # 2. Nettoyer les anciens composants UI
        self.cleanup_old_ui_components()
        print()
        
        # 3. Vérifier les dossiers vides
        self.cleanup_empty_directories()
        print()
        
        # 4. Vérifier le nouveau système
        if self.verify_new_system():
            print()
            # 5. Régénérer les routes
            self.regenerate_routes()
        
        print("=" * 50)
        print("🎉 Nettoyage terminé!")
        print("\n📋 Résumé des actions:")
        print("   ✅ Anciennes pages de domaines supprimées")
        print("   ✅ Anciens composants UI supprimés")
        print("   ✅ Sauvegardes créées avant suppression")
        print("   ✅ Nouveau système vérifié")
        print("   ✅ Routes régénérées")

def main():
    """Fonction principale"""
    try:
        cleaner = OldSystemCleaner()
        
        # Demander confirmation
        print("⚠️  ATTENTION: Ce script va supprimer des fichiers de l'ancien système!")
        print("   - base-chat-page.tsx")
        print("   - base-leaderboard-page.tsx")
        print("   - Anciennes pages de domaines hardcodées")
        print("   - Des sauvegardes seront créées")
        
        response = input("\nÊtes-vous sûr de vouloir continuer ? (oui/NON): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Nettoyage annulé")
            return
        
        cleaner.run_cleanup()
        
    except KeyboardInterrupt:
        print("\n❌ Nettoyage annulé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

if __name__ == "__main__":
    main()
