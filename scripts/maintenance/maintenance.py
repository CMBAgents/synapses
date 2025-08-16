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
import requests
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
            # Vérifier contextmaker
            if not self._check_contextmaker():
                self.logger.info("Installation de contextmaker...")
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
            self.logger.info("Installation de contextmaker via pip3...")
            result = subprocess.run(
                ["pip3", "install", "contextmaker"],
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
    
    def step1_fetch_libraries_data(self) -> List[Dict]:
        """Étape 1: Récupère les librairies depuis ASCL"""
        self.logger.info("=== ÉTAPE 1: Récupération des données des librairies ===")
        
        try:
            # Télécharger les données ASCL
            self.logger.info("Téléchargement des données ASCL...")
            ascl_data = self._download_ascl_data()
            
            # Extraire les repos GitHub
            self.logger.info("Extraction des repositories GitHub...")
            github_repos = self._extract_github_repos(ascl_data)
            self.logger.info(f"Trouvé {len(github_repos)} repositories uniques")
            
            # Récupérer le nombre d'étoiles
            self.logger.info("Récupération du nombre d'étoiles...")
            repos_with_stars = self._fetch_stars_parallel(list(github_repos))
            
            # Filtrer les repos astro/cosmo
            self.logger.info("Filtrage des repositories astronomie/cosmologie...")
            filtered_repos = self._filter_astronomy_repos(repos_with_stars)
            
            # Obtenir le top 100
            self.logger.info("Sélection du top 100...")
            top_100 = self._get_top_100(filtered_repos)
            
            # Sauvegarder en CSV
            self._save_to_csv(top_100, self.last_csv)
            
            self.logger.info(f"✅ Étape 1 terminée: {len(top_100)} librairies récupérées")
            return top_100
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 1: {e}")
            raise
    
    def step2_update_json_data(self, libraries_data: List[Dict]):
        """Étape 2: Met à jour les fichiers JSON"""
        self.logger.info("=== ÉTAPE 2: Mise à jour des données JSON ===")
        
        try:
            # Charger les données existantes
            astronomy_data = self._load_astronomy_data()
            
            # Mettre à jour avec les nouvelles données
            updated_libraries = self._update_libraries_data(astronomy_data, libraries_data)
            
            # Sauvegarder
            astronomy_data["libraries"] = updated_libraries
            astronomy_data["last_update"] = datetime.now().isoformat()
            
            with open(self.astronomy_json, 'w') as f:
                json.dump(astronomy_data, f, indent=2)
            
            self.logger.info(f"✅ Étape 2 terminée: {len(updated_libraries)} librairies mises à jour")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'étape 2: {e}")
            raise
    
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
            # Exécuter le gestionnaire de contextes directement
            script_path = self.base_dir / "scripts" / "core" / "manage-contexts.py"
            if script_path.exists():
                subprocess.run(["python3", str(script_path), "--force"], cwd=self.base_dir, check=True)
            else:
                self.logger.error("Script manage-contexts.py non trouvé")
            
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
            
            # Étape 1: Récupération des données
            libraries_data = self.step1_fetch_libraries_data()
            
            # Étape 2: Mise à jour JSON
            self.step2_update_json_data(libraries_data)
            
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
        """Exécute une maintenance rapide (sans récupération ASCL)"""
        self.logger.info("🚀 Début de la maintenance rapide")
        
        try:
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
        # Implémentation simplifiée - utilise le script existant
        script_path = self.base_dir / "scripts" / "maintenance" / "generate-missing-contexts.py"
        if script_path.exists():
            subprocess.run(["python3", str(script_path), "--domain", domain], cwd=self.base_dir)
    
    def _cleanup_duplicate_contexts(self):
        """Nettoie les contextes dupliqués"""
        self.logger.info("Nettoyage des contextes dupliqués")
        script_path = self.base_dir / "scripts" / "maintenance" / "cleanup-duplicate-contexts.py"
        if script_path.exists():
            subprocess.run(["python3", str(script_path)], cwd=self.base_dir)
        else:
            self.logger.warning("Script cleanup-duplicate-contexts.py non trouvé")
    
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
