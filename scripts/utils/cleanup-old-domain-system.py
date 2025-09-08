#!/usr/bin/env python3
"""
Script de nettoyage pour supprimer l'ancien système de gestion des domaines.
Ce script supprime les fichiers obsolètes maintenant que nous avons le système unifié.
"""

import os
import shutil
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_old_files():
    """Supprime les anciens fichiers du système de domaines"""
    
    # Fichiers à supprimer (ancien système)
    files_to_remove = [
        # Anciens scripts de mise à jour
        "app/update_bdd/get100.py",
        "scripts/utils/update-domain-data.py",
        
        # Anciens scripts de création de domaine (remplacés par le système unifié)
        "scripts/templates/create-domain.py",
        "scripts/templates/delete-domain.py",
        "scripts/templates/domain-utils.py",
        "scripts/templates/domain-config.json",
        
        # Anciens scripts de maintenance obsolètes
        "scripts/maintenance/daily_maintenance.py",
        "scripts/maintenance/optimized-auto-update.py",
        "scripts/maintenance/monitor-updater.py",
        
        # Fichiers CSV temporaires (garder seulement les derniers)
        "app/update_bdd/top_astronomy_cosmology_repos.csv",
        "app/update_bdd/avantdernier.csv",
        
        # Anciens scripts de test
        "scripts/utils/test_maintenance.py",
        "scripts/utils/test-unified-scripts.py",
    ]
    
    # Dossiers à nettoyer (mais pas supprimer complètement)
    dirs_to_clean = [
        "app/update_bdd/__pycache__",
        "scripts/templates/__pycache__",
        "scripts/maintenance/__pycache__",
        "scripts/utils/__pycache__",
        "temp/repos",
        "temp/contexts",
    ]
    
    logger.info("🧹 Nettoyage de l'ancien système de domaines...")
    
    # Supprimer les fichiers obsolètes
    removed_files = 0
    for file_path in files_to_remove:
        path = Path(file_path)
        if path.exists():
            try:
                if path.is_file():
                    path.unlink()
                    logger.info(f"✅ Fichier supprimé: {file_path}")
                    removed_files += 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    logger.info(f"✅ Dossier supprimé: {file_path}")
                    removed_files += 1
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer {file_path}: {e}")
        else:
            logger.debug(f"📄 Fichier non trouvé (déjà supprimé): {file_path}")
    
    # Nettoyer les dossiers (supprimer le contenu mais garder le dossier)
    cleaned_dirs = 0
    for dir_path in dirs_to_clean:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            try:
                # Supprimer le contenu du dossier
                for item in path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                logger.info(f"✅ Dossier nettoyé: {dir_path}")
                cleaned_dirs += 1
            except Exception as e:
                logger.warning(f"⚠️ Impossible de nettoyer {dir_path}: {e}")
    
    logger.info(f"🎉 Nettoyage terminé:")
    logger.info(f"   - {removed_files} fichiers/dossiers supprimés")
    logger.info(f"   - {cleaned_dirs} dossiers nettoyés")

def backup_important_files():
    """Sauvegarde les fichiers importants avant nettoyage"""
    
    backup_dir = Path("backup_old_system")
    backup_dir.mkdir(exist_ok=True)
    
    # Fichiers importants à sauvegarder
    important_files = [
        "app/update_bdd/ascl_repos_with_stars.csv",
        "app/update_bdd/last.csv",
        "app/data/astronomy-libraries.json",
        "app/data/biochemistry-libraries.json", 
        "app/data/finance-libraries.json",
        "app/data/machinelearning-libraries.json",
    ]
    
    logger.info("💾 Sauvegarde des fichiers importants...")
    
    for file_path in important_files:
        source = Path(file_path)
        if source.exists():
            dest = backup_dir / source.name
            try:
                shutil.copy2(source, dest)
                logger.info(f"✅ Sauvegardé: {file_path}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de sauvegarder {file_path}: {e}")

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nettoyage de l'ancien système de domaines")
    parser.add_argument("--backup", action="store_true", help="Sauvegarder les fichiers importants avant nettoyage")
    parser.add_argument("--dry-run", action="store_true", help="Simuler le nettoyage sans supprimer")
    
    args = parser.parse_args()
    
    if args.backup:
        backup_important_files()
    
    if args.dry_run:
        logger.info("🔍 Mode simulation - aucun fichier ne sera supprimé")
        # Afficher ce qui serait supprimé
        files_to_remove = [
            "app/update_bdd/get100.py",
            "scripts/utils/update-domain-data.py",
            "scripts/templates/create-domain.py",
            "scripts/templates/delete-domain.py",
            "scripts/templates/domain-utils.py",
            "scripts/templates/domain-config.json",
        ]
        
        for file_path in files_to_remove:
            path = Path(file_path)
            if path.exists():
                logger.info(f"📄 Serait supprimé: {file_path}")
            else:
                logger.info(f"📄 Non trouvé: {file_path}")
    else:
        cleanup_old_files()

if __name__ == "__main__":
    main()
