#!/usr/bin/env python3
"""
Planificateur de maintenance quotidienne pour CMB Agent Info

Ce script tourne en continu et lance automatiquement la maintenance quotidienne
à une heure spécifiée (par défaut 2h00 du matin).

Fonctionnalités:
- Planification automatique de la maintenance
- Logs détaillés de toutes les opérations
- Redémarrage automatique en cas d'erreur
- Configuration flexible de l'heure de maintenance

Utilisation:
    python3 schedule_daily_maintenance.py [--hour HOUR] [--minute MINUTE]

Exemple:
    python3 schedule_daily_maintenance.py --hour 2 --minute 0  # Maintenance à 2h00
    python3 schedule_daily_maintenance.py --hour 3 --minute 30 # Maintenance à 3h30
"""

import os
import sys
import time
import logging
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import signal
import atexit

class MaintenanceScheduler:
    def __init__(self, hour: int = 2, minute: int = 0, base_dir: str = "."):
        self.hour = hour
        self.minute = minute
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / "logs"
        self.maintenance_script = self.base_dir / "scripts" / "maintenance" / "maintenance.py"
        
        # Créer le dossier de logs
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configuration du logging
        self.setup_logging()
        
        # Flag pour arrêt propre
        self.running = True
        
        # Enregistrer les handlers de signal pour arrêt propre
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self._cleanup)
        
        self.logger.info(f"🚀 Planificateur de maintenance initialisé")
        self.logger.info(f"⏰ Maintenance programmée à {hour:02d}:{minute:02d}")
        self.logger.info(f"📁 Répertoire de base: {self.base_dir}")
        self.logger.info(f"📝 Logs: {self.logs_dir / 'scheduler.log'}")
    
    def setup_logging(self):
        """Configure le système de logging"""
        log_file = self.logs_dir / "scheduler.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Log de démarrage
        self.logger.info("=" * 60)
        self.logger.info("🔄 Démarrage du planificateur de maintenance")
        self.logger.info("=" * 60)
    
    def _signal_handler(self, signum, frame):
        """Gère les signaux d'arrêt"""
        self.logger.info(f"📡 Signal reçu ({signum}), arrêt en cours...")
        self.running = False
    
    def _cleanup(self):
        """Nettoyage à la sortie"""
        self.logger.info("🧹 Nettoyage du planificateur...")
        self.logger.info("=" * 60)
        self.logger.info("🛑 Planificateur de maintenance arrêté")
        self.logger.info("=" * 60)
    
    def should_run_maintenance(self) -> bool:
        """Vérifie si c'est l'heure de lancer la maintenance"""
        now = datetime.now()
        return now.hour == self.hour and now.minute == self.minute
    
    def run_maintenance(self):
        """Lance la maintenance quotidienne"""
        self.logger.info("🔧 Lancement de la maintenance quotidienne...")
        
        try:
            # Vérifier que le script existe
            if not self.maintenance_script.exists():
                self.logger.error(f"❌ Script de maintenance non trouvé: {self.maintenance_script}")
                return False
            
            # Lancer la maintenance rapide (--quick)
            self.logger.info("⚡ Exécution de la maintenance rapide (--quick)")
            
            start_time = datetime.now()
            result = subprocess.run(
                ["python3", str(self.maintenance_script), "--quick"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=3600  # Timeout de 1 heure
            )
            end_time = datetime.now()
            duration = end_time - start_time
            
            if result.returncode == 0:
                self.logger.info(f"✅ Maintenance terminée avec succès en {duration}")
                if result.stdout:
                    self.logger.info("📋 Sortie de la maintenance:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self.logger.info(f"   {line}")
            else:
                self.logger.error(f"❌ Maintenance échouée (code: {result.returncode})")
                if result.stderr:
                    self.logger.error("📋 Erreurs de la maintenance:")
                    for line in result.stderr.strip().split('\n'):
                        if line.strip():
                            self.logger.error(f"   {line}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Timeout: la maintenance a pris plus d'1 heure")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la maintenance: {e}")
            return False
        
        return True
    
    def run(self):
        """Boucle principale du planificateur"""
        self.logger.info("🔄 Démarrage de la boucle de planification...")
        
        last_maintenance_date = None
        
        while self.running:
            try:
                now = datetime.now()
                
                # Vérifier si c'est l'heure de la maintenance
                if self.should_run_maintenance():
                    # Éviter de lancer plusieurs fois la même maintenance
                    if last_maintenance_date is None or last_maintenance_date.date() < now.date():
                        self.logger.info(f"⏰ {now.strftime('%H:%M:%S')} - Heure de maintenance atteinte")
                        
                        success = self.run_maintenance()
                        if success:
                            last_maintenance_date = now
                            self.logger.info("✅ Maintenance planifiée terminée avec succès")
                        else:
                            self.logger.error("❌ Maintenance planifiée échouée")
                    else:
                        # Éviter les exécutions multiples dans la même minute
                        time.sleep(60)
                        continue
                
                # Attendre 1 minute avant la prochaine vérification
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle principale: {e}")
                time.sleep(60)  # Attendre avant de réessayer

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Planificateur de maintenance quotidienne",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 schedule_daily_maintenance.py                    # Maintenance à 2h00 (défaut)
  python3 schedule_daily_maintenance.py --hour 3           # Maintenance à 3h00
  python3 schedule_daily_maintenance.py --hour 1 --minute 30  # Maintenance à 1h30
        """
    )
    
    parser.add_argument(
        "--hour", 
        type=int, 
        default=2, 
        help="Heure de maintenance (0-23, défaut: 2)"
    )
    parser.add_argument(
        "--minute", 
        type=int, 
        default=0, 
        help="Minute de maintenance (0-59, défaut: 0)"
    )
    parser.add_argument(
        "--base-dir", 
        default=".", 
        help="Répertoire de base du projet (défaut: .)"
    )
    
    args = parser.parse_args()
    
    # Validation des arguments
    if not (0 <= args.hour <= 23):
        print("❌ Erreur: l'heure doit être entre 0 et 23")
        sys.exit(1)
    
    if not (0 <= args.minute <= 59):
        print("❌ Erreur: la minute doit être entre 0 et 59")
        sys.exit(1)
    
    # Vérifier qu'on est dans le bon répertoire
    base_path = Path(args.base_dir)
    if not (base_path / "package.json").exists():
        print("❌ Erreur: package.json non trouvé. Assurez-vous d'être dans le bon répertoire.")
        sys.exit(1)
    
    # Créer et lancer le planificateur
    scheduler = MaintenanceScheduler(
        hour=args.hour,
        minute=args.minute,
        base_dir=args.base_dir
    )
    
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du planificateur...")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
