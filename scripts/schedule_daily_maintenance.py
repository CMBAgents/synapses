#!/usr/bin/env python3
"""
Script de planification pour la maintenance quotidienne

Ce script planifie l'exécution automatique de la maintenance quotidienne
à une heure définie chaque jour.

Utilisation :
    python scripts/schedule_daily_maintenance.py

Configuration :
    - Modifiez MAINTENANCE_TIME pour changer l'heure d'exécution
    - Le script tourne en boucle et vérifie toutes les minutes
"""

import schedule
import time
import subprocess
import logging
import sys
from pathlib import Path
from datetime import datetime

# Configuration
MAINTENANCE_TIME = "02:00"  # Heure de maintenance (format HH:MM)
MAINTENANCE_SCRIPT = "scripts/daily_maintenance.py"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_daily_maintenance():
    """Exécute le script de maintenance quotidienne"""
    logging.info("🕒 Démarrage de la maintenance quotidienne planifiée")
    
    try:
        # Exécuter le script de maintenance
        result = subprocess.run(
            [sys.executable, MAINTENANCE_SCRIPT],
            capture_output=True,
            text=True,
            timeout=3600  # Timeout de 1 heure
        )
        
        if result.returncode == 0:
            logging.info("✅ Maintenance quotidienne terminée avec succès")
        else:
            logging.error(f"❌ Maintenance quotidienne échouée (code {result.returncode})")
            if result.stderr:
                logging.error(f"Erreur: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        logging.error("❌ Maintenance quotidienne échouée: timeout")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'exécution de la maintenance: {e}")

def main():
    """Point d'entrée principal du planificateur"""
    # Vérifier qu'on est dans le bon répertoire
    if not Path("package.json").exists():
        print("❌ Erreur: Veuillez exécuter ce script depuis la racine du projet")
        sys.exit(1)
    
    # Vérifier que le script de maintenance existe
    if not Path(MAINTENANCE_SCRIPT).exists():
        print(f"❌ Erreur: Script de maintenance introuvable: {MAINTENANCE_SCRIPT}")
        sys.exit(1)
    
    # Créer le dossier logs s'il n'existe pas
    Path("logs").mkdir(exist_ok=True)
    
    # Planifier la maintenance quotidienne
    schedule.every().day.at(MAINTENANCE_TIME).do(run_daily_maintenance)
    
    logging.info(f"📅 Planificateur démarré - maintenance prévue chaque jour à {MAINTENANCE_TIME}")
    logging.info("Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
            
    except KeyboardInterrupt:
        logging.info("👋 Planificateur arrêté par l'utilisateur")
    except Exception as e:
        logging.error(f"💥 Erreur dans le planificateur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
