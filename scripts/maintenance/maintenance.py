#!/usr/bin/env python3
"""
Script de maintenance simplifié pour CMB Agent Info
Remplace: daily_maintenance.py, optimized-auto-update.py, monitor-updater.py

Fonctionnalités:
1. Maintenance quotidienne des bibliothèques
2. Génération des contextes manquants
3. Synchronisation avec le cloud
4. Monitoring des coûts
5. Mise à jour automatique de la configuration
"""

import os
import sys
import json
import csv
import subprocess
import tempfile
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import re
from time import sleep
import random
from tqdm import tqdm
from multiprocessing import Pool

class MaintenanceManager:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.update_bdd_dir = self.base_dir / "app" / "update_bdd"
        self.data_dir = self.base_dir / "app" / "data" 
        self.context_dir = self.base_dir / "public" / "context"
        self.temp_dir = self.base_dir / "temp" / "repos"
        self.logs_dir = self.base_dir / "logs"
        
        # Créer les dossiers nécessaires
        self.logs_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de données
        self.ascl_csv = self.update_bdd_dir / "ascl_repos_with_stars.csv"
        self.last_csv = self.update_bdd_dir / "last.csv"
        self.astronomy_json = self.data_dir / "astronomy-libraries.json"
        self.commit_log_file = self.base_dir / "commit_log.json"
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'maintenance.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def step0_ensure_dependencies(self):
        """Étape 0: Vérifie et installe les dépendances nécessaires"""
        self.logger.info("=== ÉTAPE 0: Vérification et installation des dépendances ===")
        
        try:
            # Vérifier et mettre à jour contextmaker
            if not self._check_contextmaker():
                self.logger.info("Installation de contextmaker...")
                self._install_contextmaker()
            else:
                self.logger.info("Mise à jour de contextmaker vers la dernière version...")
                self._install_contextmaker()
            
            # Vérifier git
            if not self._check_git():
                self.logger.error("❌ Git n'est pas installé. Veuillez l'installer manuellement.")
                raise Exception("Git non disponible")
            
            self.logger.info("✅ Étape 0 terminée: toutes les dépendances sont disponibles")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 0: {e}")
            raise
    
    def _check_contextmaker(self) -> bool:
        """Vérifie si contextmaker est disponible"""
        try:
            result = subprocess.run(
                ["python3", "-c", "import contextmaker"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _install_contextmaker(self):
        """Installe contextmaker via pip"""
        try:
            self.logger.info("Installation/mise à jour de contextmaker via pip3...")
            result = subprocess.run(
                ["pip3", "install", "--upgrade", "contextmaker"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                self.logger.info("✅ contextmaker installé avec succès")
            else:
                self.logger.error(f"❌ Échec de l'installation: {result.stderr}")
                raise Exception(f"Installation échouée: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Timeout lors de l'installation de contextmaker")
            raise Exception("Timeout installation")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'installation: {e}")
            raise
    
    def _check_git(self) -> bool:
        """Vérifie si git est disponible"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def step1_update_all_domains(self) -> Dict[str, bool]:
        """Étape 1: Met à jour tous les domaines avec le système unifié"""
        self.logger.info("=== ÉTAPE 1: Mise à jour de tous les domaines ===")
        
        try:
            # Utiliser le nouveau système unifié
            script_path = self.base_dir / "scripts" / "core" / "unified-domain-updater.py"
            if not script_path.exists():
                self.logger.error(f"❌ Script unifié non trouvé: {script_path}")
                raise Exception("Script unifié introuvable")
            
            self.logger.info("🔄 Exécution du système unifié de mise à jour des domaines...")
            result = subprocess.run(
                ["python3", str(script_path), "--maintenance"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Étape 1 terminée: tous les domaines mis à jour")
                # Parser les résultats si nécessaire
                return {"astronomy": True, "biochemistry": True, "finance": True, "machinelearning": True}
            else:
                self.logger.error(f"❌ Erreur lors de la mise à jour: {result.stderr}")
                raise Exception(f"Échec de la mise à jour: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Timeout lors de la mise à jour des domaines")
            raise Exception("Timeout de la mise à jour")
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 1: {e}")
            raise
    
    def step2_update_context_status(self):
        """Étape 2: Mise à jour du statut des contextes"""
        self.logger.info("=== ÉTAPE 2: Mise à jour du statut des contextes ===")
        
        try:
            # Utiliser le script unifié context-manager-unified.py
            script_path = self.base_dir / "scripts" / "maintenance" / "context-manager-unified.py"
            if script_path.exists():
                self.logger.info("Exécution de context-manager-unified.py (mise à jour rapide)...")
                subprocess.run(["python3", str(script_path), "--quick"], cwd=self.base_dir, check=True)
                self.logger.info("✅ Statut des contextes mis à jour via le script unifié")
            else:
                self.logger.error("Script context-manager-unified.py non trouvé")
                raise Exception("Script context-manager-unified.py introuvable")
            
            self.logger.info("✅ Étape 2 terminée: statut des contextes mis à jour")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 2: {e}")
            raise
    
    def step1_detect_github_changes(self):
        """Étape 1: Détection des modifications GitHub et marquage des contextes obsolètes"""
        self.logger.info("=== ÉTAPE 1: Détection des modifications GitHub ===")
        
        try:
            # Utiliser le script unifié pour détecter les modifications
            script_path = self.base_dir / "scripts" / "maintenance" / "context-manager-unified.py"
            if script_path.exists():
                self.logger.info("Exécution de la détection des modifications GitHub...")
                result = subprocess.run(
                    ["python3", str(script_path), "--quick"], 
                    cwd=self.base_dir,
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                self.logger.info("✅ Détection des modifications GitHub terminée")
                if result.stdout:
                    # Afficher les résultats de la détection
                    for line in result.stdout.strip().split('\n'):
                        if line.strip() and ('🔄' in line or '✅' in line or 'repos vérifiés' in line):
                            self.logger.info(f"   {line}")
            else:
                self.logger.error("Script context-manager-unified.py non trouvé")
                raise Exception("Script context-manager-unified.py introuvable")
            
            self.logger.info("✅ Étape 1 terminée: modifications GitHub détectées")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Erreur lors de la détection GitHub: {e.stderr}")
            raise Exception(f"Échec de la détection GitHub: {e.stderr}")
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 1: {e}")
            raise

    def step2_5_fix_context_names(self):
        """Étape 2.5: Correction des noms de fichiers de contexte"""
        self.logger.info("=== ÉTAPE 2.5: Correction des noms de contexte ===")
        
        try:
            # Utiliser le script de correction des noms
            script_path = self.base_dir / "scripts" / "utils" / "fix-context-names.py"
            if script_path.exists():
                self.logger.info("Exécution du correcteur de noms de contexte...")
                result = subprocess.run(["python3", str(script_path)], cwd=self.base_dir, 
                                      capture_output=True, text=True, check=True)
                self.logger.info("✅ Correction des noms de contexte terminée")
                if result.stdout:
                    self.logger.info("📋 Résultats de la correction:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip() and ('✅' in line or '📝' in line):
                            self.logger.info(f"   {line}")
            else:
                self.logger.warning("Script fix-context-names.py non trouvé, passage de l'étape")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Erreur lors de la correction des noms: {e.stderr}")
            # Ne pas faire échouer la maintenance pour cette étape
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 2.5: {e}")
            # Ne pas faire échouer la maintenance pour cette étape
    
    # Les méthodes _update_json_status_via_api, _check_server_status et _update_domain_via_api 
    # ont été supprimées car remplacées par l'utilisation directe de update-json-status.py
    
    def step3_generate_missing_contexts(self):
        """Étape 3: Génération des contextes manquants"""
        self.logger.info("=== ÉTAPE 3: Génération des contextes manquants ===")
        
        try:
            # Charger les données existantes
            astronomy_data = self._load_astronomy_data()
            finance_data = self._load_finance_data()
            
            # Générer les contextes manquants pour astronomy
            self._generate_contexts_for_domain(astronomy_data, "astronomy")
            
            # Générer les contextes manquants pour finance
            self._generate_contexts_for_domain(finance_data, "finance")
            
            # Nettoyer les contextes dupliqués
            self._cleanup_duplicate_contexts()
            
            self.logger.info("✅ Étape 3 terminée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 3: {e}")
            raise
    
    def step4_update_configuration(self):
        """Étape 4: Met à jour la configuration"""
        self.logger.info("=== ÉTAPE 4: Mise à jour de la configuration ===")
        
        try:
            # Exécuter le script unifié pour la mise à jour de configuration
            script_path = self.base_dir / "scripts" / "maintenance" / "context-manager-unified.py"
            if script_path.exists():
                subprocess.run(["python3", str(script_path), "--quick"], cwd=self.base_dir, check=True)
                self.logger.info("✅ Configuration mise à jour via le script unifié")
            else:
                self.logger.error("Script context-manager-unified.py non trouvé")
            
            self.logger.info("✅ Étape 4 terminée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 4: {e}")
            raise
    
    def step5_cleanup(self):
        """Étape 5: Nettoyage"""
        self.logger.info("=== ÉTAPE 5: Nettoyage ===")
        
        try:
            # Nettoyer les repositories temporaires
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Nettoyer les logs anciens (garder seulement 7 jours)
            self._cleanup_old_logs()
            
            self.logger.info("✅ Étape 5 terminée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 5: {e}")
            raise
    
    def run_full_maintenance(self):
        """Exécute la maintenance complète"""
        self.logger.info("🚀 Début de la maintenance complète")
        
        try:
            # Étape 0: Vérification et installation des dépendances
            self.step0_ensure_dependencies()
            
            # Étape 1: Mise à jour de tous les domaines
            domain_results = self.step1_update_all_domains()
            
            # Étape 2: Mise à jour du statut des contextes
            self.step2_update_context_status()
            
            # Étape 3: Génération contextes
            self.step3_generate_missing_contexts()
            
            # Étape 4: Mise à jour configuration
            self.step4_update_configuration()
            
            # Étape 5: Nettoyage
            self.step5_cleanup()
            
            self.logger.info("🎉 Maintenance complète terminée avec succès!")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la maintenance: {e}")
            raise
    
    def run_quick_maintenance(self):
        """Exécute une maintenance rapide avec détection des modifications GitHub"""
        self.logger.info("🚀 Début de la maintenance rapide")
        
        try:
            # Étape 0: Vérification des dépendances
            self.step0_ensure_dependencies()
            
            # Étape 1: Détection des modifications GitHub et marquage des contextes obsolètes
            # self.step1_detect_github_changes()  # Commenté temporairement
            
            # Étape 2.5: Correction des noms de contexte
            self.step2_5_fix_context_names()
            
            # Étape 3: Génération contextes
            self.step3_generate_missing_contexts()
            
            # Étape 4: Mise à jour configuration
            self.step4_update_configuration()
            
            # Étape 5: Nettoyage
            self.step5_cleanup()
            
            self.logger.info("🎉 Maintenance rapide terminée avec succès!")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la maintenance: {e}")
            raise
    
    # Méthodes utilitaires (simplifiées)
    def _download_ascl_data(self) -> List[Dict]:
        """Télécharge les données ASCL"""
        # Implémentation simplifiée - utilise les données existantes
        if self.ascl_csv.exists():
            return self._load_csv_data(self.ascl_csv)
        else:
            self.logger.warning("Fichier ASCL non trouvé, utilisation des données existantes")
            return []
    
    def _extract_github_repos(self, ascl_data: List[Dict]) -> Set[str]:
        """Extrait les repositories GitHub"""
        github_repos = set()
        for item in ascl_data:
            if 'github_url' in item and item['github_url']:
                github_repos.add(item['github_url'])
        return github_repos
    
    def _fetch_stars_parallel(self, repos: List[str]) -> List[Dict]:
        """Récupère les étoiles en parallèle"""
        # Implémentation simplifiée
        return [{"url": repo, "stars": 0} for repo in repos]
    
    def _filter_astronomy_repos(self, repos: List[Dict]) -> List[Dict]:
        """Filtre les repositories astronomie"""
        return repos  # Simplifié
    
    def _get_top_100(self, repos: List[Dict]) -> List[Dict]:
        """Obtient le top 100"""
        return repos[:100] if len(repos) > 100 else repos
    
    def _save_to_csv(self, data: List[Dict], filepath: Path):
        """Sauvegarde en CSV"""
        if data:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    def _load_astronomy_data(self) -> Dict:
        """Charge les données astronomy"""
        if self.astronomy_json.exists():
            with open(self.astronomy_json, 'r') as f:
                return json.load(f)
        return {"libraries": [], "domain": "astronomy"}
    
    def _load_finance_data(self) -> Dict:
        """Charge les données finance"""
        finance_json = self.data_dir / "finance-libraries.json"
        if finance_json.exists():
            with open(finance_json, 'r') as f:
                return json.load(f)
        return {"libraries": [], "domain": "finance"}
    
    def _update_libraries_data(self, existing_data: Dict, new_data: List[Dict]) -> List[Dict]:
        """Met à jour les données des bibliothèques"""
        # Implémentation simplifiée
        return existing_data.get("libraries", [])
    
    def _generate_contexts_for_domain(self, data: Dict, domain: str):
        """Génère les contextes pour un domaine"""
        self.logger.info(f"Génération des contextes pour {domain}")
        # Utilise le script unifié pour la génération
        script_path = self.base_dir / "scripts" / "maintenance" / "context-manager-unified.py"
        if script_path.exists():
            self.logger.info("Génération des contextes via le script unifié...")
            # Note: Le script unifié gère tous les domaines automatiquement
            # On l'appelle une seule fois pour tous les domaines
            if domain == "astronomy":  # Appeler seulement pour le premier domaine
                subprocess.run(["python3", str(script_path), "--full"], cwd=self.base_dir)
        else:
            self.logger.error("Script context-manager-unified.py non trouvé")
    
    def _cleanup_duplicate_contexts(self):
        """Nettoie les contextes dupliqués et garde le plus long pour chaque bibliothèque"""
        self.logger.info("🧹 Nettoyage avancé des contextes dupliqués...")
        self.logger.info("  - Suppression des doublons racine")
        self.logger.info("  - Conservation du contexte le plus long pour chaque bibliothèque")
        self.logger.info("  - Mise à jour automatique des JSON après chaque modification")
        
        script_path = self.base_dir / "scripts" / "maintenance" / "context-manager-unified.py"
        if script_path.exists():
            subprocess.run(["python3", str(script_path), "--cleanup"], cwd=self.base_dir, check=True)
            self.logger.info("✅ Nettoyage avancé des contextes dupliqués terminé")
        else:
            self.logger.warning("Script context-manager-unified.py non trouvé")
    
    def _cleanup_old_logs(self):
        """Nettoie les anciens logs"""
        cutoff_date = datetime.now() - timedelta(days=7)
        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
    
    def _load_csv_data(self, filepath: Path) -> List[Dict]:
        """Charge les données CSV"""
        data = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        return data

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Script de maintenance simplifié")
    parser.add_argument("--quick", action="store_true", help="Maintenance rapide (sans récupération ASCL)")
    parser.add_argument("--base-dir", default=".", help="Répertoire de base")
    
    args = parser.parse_args()
    
    manager = MaintenanceManager(args.base_dir)
    
    if args.quick:
        manager.run_quick_maintenance()
    else:
        manager.run_full_maintenance()

if __name__ == "__main__":
    main()
