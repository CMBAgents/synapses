#!/usr/bin/env python3
"""
Script de maintenance quotidienne du site CMB Agent Info

Ce script automatise les tâches de maintenance suivantes :
1. Récupération des données des librairies depuis ASCL
2. Comparaison avec les données existantes et mise à jour du JSON
3. Génération/mise à jour des contextes pour les nouvelles librairies ou celles avec nouveaux commits
4. Nettoyage des repositories clonés temporairement

Utilisation : python scripts/daily_maintenance.py
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

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_maintenance.log'),
        logging.StreamHandler()
    ]
)

class DailyMaintenanceManager:
    """Gestionnaire principal pour la maintenance quotidienne"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.update_bdd_dir = self.base_dir / "app" / "update_bdd"
        self.data_dir = self.base_dir / "app" / "data" 
        self.context_dir = self.base_dir / "app" / "context"
        self.public_context_dir = self.base_dir / "public" / "context"
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
        
    def step1_fetch_libraries_data(self) -> List[Dict]:
        """
        Étape 1: Récupère les librairies depuis ASCL et retourne les 100 meilleures
        """
        logging.info("=== ÉTAPE 1: Récupération des données des librairies ===")
        
        try:
            # 1. Télécharger les données ASCL
            logging.info("Téléchargement des données ASCL...")
            ascl_data = self._download_ascl_data()
            
            # 2. Extraire les repos GitHub
            logging.info("Extraction des repositories GitHub...")
            github_repos = self._extract_github_repos(ascl_data)
            logging.info(f"Trouvé {len(github_repos)} repositories uniques")
            
            # 3. Récupérer le nombre d'étoiles (en parallèle)
            logging.info("Récupération du nombre d'étoiles...")
            repos_with_stars = self._fetch_stars_parallel(list(github_repos))
            
            # 4. Filtrer les repos astro/cosmo
            logging.info("Filtrage des repositories astronomie/cosmologie...")
            filtered_repos = self._filter_astronomy_repos(repos_with_stars)
            
            # 5. Obtenir le top 100
            logging.info("Sélection du top 100...")
            top_100 = self._get_top_100(filtered_repos)
            
            # 6. Sauvegarder en CSV
            self._save_to_csv(top_100, self.last_csv)
            
            logging.info(f"✅ Étape 1 terminée: {len(top_100)} librairies récupérées")
            return top_100
            
        except Exception as e:
            logging.error(f"❌ Erreur dans l'étape 1: {e}")
            raise
    
    def step2_compare_and_update_json(self, new_libraries: List[Dict]) -> Tuple[List[str], List[str]]:
        """
        Étape 2: Compare les nouvelles librairies avec l'ancien JSON et met à jour
        Retourne: (nouvelles_librairies, librairies_supprimées)
        """
        logging.info("=== ÉTAPE 2: Comparaison et mise à jour du JSON ===")
        
        try:
            # Charger l'ancien JSON s'il existe
            old_libraries = []
            if self.astronomy_json.exists():
                with open(self.astronomy_json, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    old_libraries = old_data.get('libraries', [])
            
            # Extraire les noms pour comparaison
            old_names = {lib['name'] for lib in old_libraries}
            new_names = {lib['name'] for lib in new_libraries}
            
            # Identifier les changements
            nouvelles = list(new_names - old_names)
            supprimees = list(old_names - new_names)
            
            logging.info(f"Nouvelles librairies: {len(nouvelles)}")
            logging.info(f"Librairies supprimées: {len(supprimees)}")
            
            if nouvelles:
                logging.info(f"Nouvelles: {nouvelles[:5]}{'...' if len(nouvelles) > 5 else ''}")
            if supprimees:
                logging.info(f"Supprimées: {supprimees[:5]}{'...' if len(supprimees) > 5 else ''}")
            
            # Créer le nouveau JSON avec preservation des statuts de contexte existants
            updated_libraries = []
            for lib in new_libraries:
                # Chercher si cette librairie existait déjà
                existing_lib = next((old_lib for old_lib in old_libraries if old_lib['name'] == lib['name']), None)
                
                if existing_lib:
                    # Préserver les informations de contexte existantes
                    lib['hasContextFile'] = existing_lib.get('hasContextFile', False)
                    lib['contextFileName'] = existing_lib.get('contextFileName', '')
                else:
                    # Nouvelle librairie - pas de contexte encore
                    lib['hasContextFile'] = False
                    lib['contextFileName'] = ''
                
                updated_libraries.append(lib)
            
            # Créer le nouveau fichier JSON
            new_json_data = {
                "libraries": updated_libraries,
                "domain": "astronomy", 
                "description": "Top astronomy and cosmology libraries for celestial observations, gravitational waves, and cosmic microwave background analysis",
                "keywords": ["astronomy", "cosmology", "astrophysics", "gravitational waves", "CMB", "healpy", "astropy"],
                "last_updated": datetime.now().isoformat()
            }
            
            # Sauvegarder le nouveau JSON
            with open(self.astronomy_json, 'w', encoding='utf-8') as f:
                json.dump(new_json_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"✅ Étape 2 terminée: JSON mis à jour avec {len(updated_libraries)} librairies")
            return nouvelles, supprimees
            
        except Exception as e:
            logging.error(f"❌ Erreur dans l'étape 2: {e}")
            raise
    
    def step3_update_contexts(self, new_libraries: List[str]) -> Dict:
        """
        Étape 3: Met à jour les fichiers de contexte
        - Génère des contextes pour les nouvelles librairies
        - Met à jour les contextes des librairies avec nouveaux commits (dernière mois)
        """
        logging.info("=== ÉTAPE 3: Mise à jour des contextes ===")
        
        results = {
            'new_contexts_generated': 0,
            'contexts_updated': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Charger les données des librairies
            with open(self.astronomy_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                libraries = data['libraries']
            
            # Charger le log des commits
            commit_log = self._load_commit_log()
            
            # Traiter chaque librairie
            for lib in libraries:
                lib_name = lib['name']
                github_url = lib['github_url']
                package_name = lib_name.split('/')[-1]
                
                try:
                    # Cas 1: Nouvelle librairie sans contexte
                    if not lib.get('hasContextFile', False):
                        logging.info(f"🆕 Génération contexte pour nouvelle librairie: {lib_name}")
                        if self._generate_context_for_library(lib, package_name, github_url):
                            results['new_contexts_generated'] += 1
                            # Mettre à jour le JSON
                            lib['hasContextFile'] = True
                            lib['contextFileName'] = f"{package_name}-context.txt"
                        else:
                            results['failed'] += 1
                            results['errors'].append(f"Échec génération contexte: {lib_name}")
                    
                    # Cas 2: Librairie existante - vérifier nouveaux commits du dernier mois
                    else:
                        logging.info(f"🔍 Vérification commits récents pour: {lib_name}")
                        if self._has_recent_commits(github_url, commit_log):
                            logging.info(f"🔄 Nouveaux commits détectés, mise à jour contexte: {lib_name}")
                            if self._generate_context_for_library(lib, package_name, github_url):
                                results['contexts_updated'] += 1
                                # Mettre à jour le log des commits
                                latest_commit = self._get_latest_commit_sha(github_url)
                                if latest_commit:
                                    commit_log[github_url] = latest_commit
                            else:
                                results['failed'] += 1
                                results['errors'].append(f"Échec mise à jour contexte: {lib_name}")
                        else:
                            logging.info(f"✅ Pas de nouveaux commits pour: {lib_name}")
                
                except Exception as e:
                    logging.error(f"❌ Erreur traitement {lib_name}: {e}")
                    results['failed'] += 1
                    results['errors'].append(f"{lib_name}: {str(e)}")
            
            # Sauvegarder le JSON mis à jour et le log des commits
            with open(self.astronomy_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self._save_commit_log(commit_log)
            
            logging.info(f"✅ Étape 3 terminée:")
            logging.info(f"  - Nouveaux contextes générés: {results['new_contexts_generated']}")
            logging.info(f"  - Contextes mis à jour: {results['contexts_updated']}")
            logging.info(f"  - Échecs: {results['failed']}")
            
            return results
            
        except Exception as e:
            logging.error(f"❌ Erreur dans l'étape 3: {e}")
            raise
    
    def step4_cleanup_repositories(self):
        """
        Étape 4: Nettoie tous les repositories clonés temporairement
        """
        logging.info("=== ÉTAPE 4: Nettoyage des repositories ===")
        
        try:
            if self.temp_dir.exists():
                # Supprimer tout le contenu du dossier temp
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(parents=True, exist_ok=True)
                logging.info("✅ Repositories temporaires nettoyés")
            else:
                logging.info("✅ Aucun repository temporaire à nettoyer")
                
        except Exception as e:
            logging.error(f"❌ Erreur lors du nettoyage: {e}")
            raise
    
    # === MÉTHODES UTILITAIRES ===
    
    def _download_ascl_data(self) -> dict:
        """Télécharge les données depuis ASCL"""
        url = "https://ascl.net/code/json"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def _extract_github_repos(self, data: dict) -> Set[str]:
        """Extrait les repositories GitHub uniques depuis les données ASCL"""
        github_pattern = r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
        repos = set()
        
        data_str = json.dumps(data)
        matches = re.findall(github_pattern, data_str, re.IGNORECASE)
        
        for match in matches:
            repo_path = match.strip()
            repo_path = re.sub(r'["\],\s]+$', '', repo_path)
            if repo_path.endswith('.git'):
                repo_path = repo_path[:-4]
            repos.add(repo_path.lower())
        
        return repos
    
    def _fetch_stars_parallel(self, repos: List[str]) -> List[Tuple[str, int]]:
        """Récupère le nombre d'étoiles en parallèle"""
        repos_with_indices = list(enumerate(repos))
        results = []
        
        with tqdm(total=len(repos_with_indices), desc="Récupération étoiles") as pbar:
            with Pool(processes=4) as pool:
                for result in pool.imap_unordered(self._get_github_stars_with_delay, repos_with_indices):
                    results.append(result)
                    pbar.update(1)
        
        return results
    
    def _get_github_stars_with_delay(self, repo_with_index: Tuple[int, str]) -> Tuple[str, int]:
        """Récupère le nombre d'étoiles pour un repository avec délai"""
        index, repo_path = repo_with_index
        sleep(random.uniform(0.1, 0.5))
        
        url = f"https://github.com/{repo_path}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                star_pattern = r'Star this repository \((\d+)\)'
                match = re.search(star_pattern, response.text)
                if match:
                    return (f"github.com/{repo_path}", int(match.group(1)))
                
                alt_pattern = r'aria-label="(\d+) users? starred this repository"'
                match = re.search(alt_pattern, response.text)
                if match:
                    return (f"github.com/{repo_path}", int(match.group(1)))
                return (f"github.com/{repo_path}", 0)
            else:
                return (f"github.com/{repo_path}", -1)
        except Exception:
            return (f"github.com/{repo_path}", -1)
    
    def _filter_astronomy_repos(self, repos_with_stars: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """Filtre les repositories astronomie/cosmologie"""
        keywords = [
            "astro", "astropy", "healpy", "photutils", "sky", "gal", "cosmo", "cmb",
            "planck", "tardis", "lightkurve", "astroquery", "pypeit", "poppy", "stellar",
            "galsim", "ultranest", "pymultinest", "zeus", "radis", "astronn", "presto", 
            "astroplan", "sep", "specutils", "s2fft", "stingray",
            "spacepy", "pycbc", "gwpy", "einsteinpy", "simonsobs", "cmbant", "lesgourg/class_public",
        ]
        
        filtered = []
        for url, stars in repos_with_stars:
            if stars >= 0 and any(keyword in url.lower() for keyword in keywords):
                filtered.append((url, stars))
        
        return filtered
    
    def _get_top_100(self, repos_with_stars: List[Tuple[str, int]]) -> List[Dict]:
        """Retourne le top 100 des repositories triés par étoiles"""
        # Trier par nombre d'étoiles (décroissant)
        sorted_repos = sorted(repos_with_stars, key=lambda x: x[1], reverse=True)
        top_100 = sorted_repos[:100]
        
        # Convertir en format attendu
        libraries = []
        for i, (url, stars) in enumerate(top_100, 1):
            repo_name = url.replace("github.com/", "")
            libraries.append({
                "name": repo_name,
                "github_url": f"https://{url}",
                "stars": stars,
                "rank": i
            })
        
        return libraries
    
    def _save_to_csv(self, libraries: List[Dict], csv_path: Path):
        """Sauvegarde les librairies en CSV"""
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['library_name', 'github_url', 'stars'])
            for lib in libraries:
                writer.writerow([lib['name'], lib['github_url'], lib['stars']])
    
    def _load_commit_log(self) -> Dict:
        """Charge le log des commits"""
        if self.commit_log_file.exists():
            with open(self.commit_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_commit_log(self, commit_log: Dict):
        """Sauvegarde le log des commits"""
        with open(self.commit_log_file, 'w', encoding='utf-8') as f:
            json.dump(commit_log, f, indent=2, ensure_ascii=False)
    
    def _has_recent_commits(self, github_url: str, commit_log: Dict) -> bool:
        """Vérifie s'il y a eu des commits dans le dernier mois"""
        try:
            # Obtenir le dernier commit actuel
            latest_commit = self._get_latest_commit_sha(github_url)
            if not latest_commit:
                return False
            
            # Vérifier si différent du log
            last_logged = commit_log.get(github_url)
            if last_logged != latest_commit:
                # Vérifier si le commit est récent (dernier mois)
                return self._is_commit_recent(github_url, latest_commit)
            
            return False
            
        except Exception as e:
            logging.warning(f"Erreur vérification commits pour {github_url}: {e}")
            return False
    
    def _get_latest_commit_sha(self, github_url: str) -> Optional[str]:
        """Récupère le SHA du dernier commit"""
        try:
            repo_path = github_url.replace("https://github.com/", "").replace(".git", "")
            api_url = f"https://api.github.com/repos/{repo_path}/commits"
            
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    return commits[0]["sha"]
            return None
            
        except Exception as e:
            logging.warning(f"Erreur récupération commit pour {github_url}: {e}")
            return None
    
    def _is_commit_recent(self, github_url: str, commit_sha: str) -> bool:
        """Vérifie si un commit est récent (dernier mois)"""
        try:
            repo_path = github_url.replace("https://github.com/", "").replace(".git", "")
            api_url = f"https://api.github.com/repos/{repo_path}/commits/{commit_sha}"
            
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                commit_data = response.json()
                commit_date_str = commit_data["commit"]["author"]["date"]
                commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                
                # Vérifier si c'est dans le dernier mois
                one_month_ago = datetime.now() - timedelta(days=30)
                return commit_date.replace(tzinfo=None) > one_month_ago
            
            return False
            
        except Exception as e:
            logging.warning(f"Erreur vérification date commit pour {github_url}: {e}")
            return False
    
    def _generate_context_for_library(self, lib: Dict, package_name: str, github_url: str) -> bool:
        """Génère le contexte pour une librairie"""
        try:
            # Créer dossier de contexte s'il n'existe pas
            context_domain_dir = self.public_context_dir / "astronomy"
            context_domain_dir.mkdir(parents=True, exist_ok=True)
            
            # Chemin de sortie du contexte
            output_path = context_domain_dir / f"{package_name}-context.txt"
            
            # Créer dossier temporaire pour clonage
            temp_repo_dir = tempfile.mkdtemp(dir=self.temp_dir)
            
            try:
                # Cloner le repository
                logging.info(f"  Clonage de {github_url}...")
                clone_cmd = ["git", "clone", "--depth", "1", github_url, temp_repo_dir]
                result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    logging.error(f"  Erreur clonage: {result.stderr}")
                    return False
                
                # Générer le contexte avec contextmaker Python API
                logging.info(f"  Génération contexte avec contextmaker...")
                
                import contextmaker
                
                try:
                    # Utiliser l'API Python de contextmaker
                    result_path = contextmaker.make(
                        library_name=package_name,
                        output_path=str(output_path),
                        input_path=temp_repo_dir,
                        extension='txt'
                    )
                    
                    if result_path and output_path.exists():
                        logging.info(f"  ✅ Contexte généré: {output_path}")
                        return True
                    else:
                        logging.error(f"  ❌ Échec génération contexte: pas de fichier créé")
                        return False
                        
                except Exception as e:
                    logging.error(f"  ❌ Erreur contextmaker: {e}")
                    return False
                    
            finally:
                # Nettoyer le dossier temporaire
                if os.path.exists(temp_repo_dir):
                    shutil.rmtree(temp_repo_dir, ignore_errors=True)
                    
        except Exception as e:
            logging.error(f"  ❌ Exception génération contexte pour {package_name}: {e}")
            return False
    
    def run_daily_maintenance(self):
        """Exécute la maintenance quotidienne complète"""
        start_time = datetime.now()
        logging.info(f"🚀 DÉBUT DE LA MAINTENANCE QUOTIDIENNE - {start_time}")
        
        try:
            # Étape 1: Récupération des données
            new_libraries = self.step1_fetch_libraries_data()
            
            # Étape 2: Comparaison et mise à jour JSON
            nouvelles, supprimees = self.step2_compare_and_update_json(new_libraries)
            
            # Étape 3: Mise à jour des contextes
            context_results = self.step3_update_contexts(nouvelles)
            
            # Étape 4: Nettoyage
            self.step4_cleanup_repositories()
            
            # Résumé final
            end_time = datetime.now()
            duration = end_time - start_time
            
            logging.info("🎉 MAINTENANCE QUOTIDIENNE TERMINÉE !")
            logging.info(f"⏱️  Durée totale: {duration}")
            logging.info(f"📊 Résumé:")
            logging.info(f"  - Librairies traitées: {len(new_libraries)}")
            logging.info(f"  - Nouvelles librairies: {len(nouvelles)}")
            logging.info(f"  - Librairies supprimées: {len(supprimees)}")
            logging.info(f"  - Nouveaux contextes générés: {context_results['new_contexts_generated']}")
            logging.info(f"  - Contextes mis à jour: {context_results['contexts_updated']}")
            logging.info(f"  - Échecs: {context_results['failed']}")
            
            # Log des erreurs s'il y en a
            if context_results['errors']:
                logging.warning("⚠️  ERREURS RENCONTRÉES:")
                for error in context_results['errors']:
                    logging.warning(f"  - {error}")
            
            return True
            
        except Exception as e:
            logging.error(f"💥 ERREUR CRITIQUE DANS LA MAINTENANCE: {e}")
            return False


def main():
    """Point d'entrée principal"""
    # Vérifier qu'on est dans le bon répertoire
    if not Path("package.json").exists():
        print("❌ Erreur: Veuillez exécuter ce script depuis la racine du projet")
        sys.exit(1)
    
    # Vérifier que contextmaker est installé
    try:
        import contextmaker
        # Tester que la fonction make est disponible
        if not hasattr(contextmaker, 'make'):
            print("❌ Erreur: contextmaker.make() non disponible")
            print("   Veuillez installer contextmaker: pip install contextmaker")
            sys.exit(1)
        print("✅ contextmaker disponible")
    except ImportError:
        print("❌ Erreur: contextmaker n'est pas installé")
        print("   Veuillez installer contextmaker: pip install contextmaker")
        sys.exit(1)
    
    # Créer et exécuter le gestionnaire de maintenance
    maintenance_manager = DailyMaintenanceManager()
    success = maintenance_manager.run_daily_maintenance()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
