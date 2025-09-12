#!/usr/bin/env python3
"""
Étape 6: Nettoyage
"""

import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_temp_repos():
    """Nettoie les repositories temporaires"""
    temp_dir = Path(__file__).parent.parent.parent.parent / "temp" / "repos"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Repositories temporaires nettoyés")

def cleanup_old_logs():
    """Nettoie les anciens logs (garder seulement 7 jours)"""
    logs_dir = Path(__file__).parent.parent.parent.parent / "logs"
    if not logs_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=7)
    cleaned_count = 0
    
    for log_file in logs_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_date.timestamp():
            try:
                log_file.unlink()
                cleaned_count += 1
            except Exception as e:
                print(f"⚠️ Erreur suppression {log_file.name}: {e}")
    
    if cleaned_count > 0:
        print(f"✅ {cleaned_count} anciens logs supprimés")
    else:
        print("✅ Aucun ancien log à nettoyer")

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 6: Nettoyage ===")
    
    try:
        # Nettoyer les repositories temporaires
        cleanup_temp_repos()
        
        # Nettoyer les logs anciens
        cleanup_old_logs()
        
        print("✅ Étape 6 terminée")
        
    except Exception as e:
        print(f"❌ Erreur dans l'étape 6: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
