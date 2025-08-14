#!/usr/bin/env python3
"""
Script principal pour mettre à jour tous les domaines.
Utilise deux approches différentes selon le domaine :
- Astronomie/Cosmologie : Système actuel avec ASCL (get100.py)
- Autres domaines : API GitHub directe avec filtrage par mots-clés
"""

import os
import sys
import json
import csv
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Configuration des domaines et leurs mots-clés
DOMAIN_CONFIGS = {
    "astrophysics_cosmology": {
        "use_ascl": True,
        "keywords": [
            "astro", "astropy", "healpy", "photutils", "sky", "gal", "cosmo", "cmb",
            "planck", "tardis", "lightkurve", "astroquery", "pypeit", "poppy", "stellar",
            "galsim", "ultranest", "pymultinest", "zeus", "radis", "astronn", "presto", 
            "astroplan", "sep", "specutils", "s2fft", "stingray",
            "spacepy", "pycbc", "gwpy", "einsteinpy", "simonsobs", "cmbant", "lesgourg/class_public",
        ],
        "description": "Top astrophysics and cosmology libraries for celestial observations, gravitational waves, and cosmic microwave background analysis",
        "specific_libs": [
            "CMBAgents/cmbagent",
            "cmbant/camb", 
            "cmbant/getdist",
            "CobayaSampler/cobaya"
        ]
    },
    "finance_trading": {
        "use_ascl": False,
        "keywords": [
            "finance", "trading", "portfolio", "quant", "zipline", "yfinance", "pyfolio",
            "empyrical", "alphalens", "mlfinlab", "ffn", "finquant", "backtrader",
            "vnpy", "tushare", "akshare", "ccxt", "pandas-ta", "ta-lib", "finrl",
            "qlib", "finrl", "gplearn", "pykalman", "arch", "statsmodels"
        ],
        "description": "Top finance and trading libraries for portfolio optimization, algorithmic trading, and financial analysis",
        "specific_libs": []
    },
    "machine_learning": {
        "use_ascl": False,
        "keywords": [
            "ml", "machine-learning", "deep-learning", "neural", "tensorflow", "pytorch",
            "scikit-learn", "keras", "xgboost", "lightgbm", "catboost", "transformers",
            "huggingface", "opencv", "nltk", "spacy", "gensim", "fastai", "jax"
        ],
        "description": "Top machine learning and deep learning libraries for AI development and research",
        "specific_libs": []
    }
}

class DomainUpdater:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.update_bdd_dir = self.base_dir / "app" / "update_bdd"
        self.data_dir = self.base_dir / "app" / "data"
        self.temp_dir = self.base_dir / "temp" / "repos"
        
        # Créer les dossiers nécessaires
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def update_astrophysics_cosmology_domain(self):
        """Met à jour le domaine astrophysics & cosmology en utilisant le système ASCL existant"""
        self.logger.info("=== Mise à jour du domaine ASTROPHYSICS & COSMOLOGY (système ASCL) ===")
        
        try:
            # Importer et exécuter le script get100.py existant
            sys.path.append(str(self.update_bdd_dir))
            from get100 import main as get100_main
            
            # Exécuter la mise à jour
            get100_main()
            self.logger.info("✅ Domaine astrophysics & cosmology mis à jour avec succès")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la mise à jour du domaine astrophysics & cosmology: {e}")
            raise
    
    def search_github_repos(self, keywords: List[str], min_stars: int = 100) -> List[Dict]:
        """Recherche des dépôts GitHub basés sur des mots-clés"""
        self.logger.info(f"Recherche GitHub pour les mots-clés: {keywords[:5]}...")
        
        repos = []
        seen_repos = set()
        
        for keyword in keywords:
            try:
                # Recherche GitHub API
                query = f"{keyword} language:python stars:>={min_stars}"
                url = "https://api.github.com/search/repositories"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 100
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                for repo in data.get("items", []):
                    repo_name = repo["full_name"]
                    if repo_name not in seen_repos:
                        seen_repos.add(repo_name)
                        repos.append({
                            "name": repo_name,
                            "github_url": repo["html_url"],
                            "stars": repo["stargazers_count"],
                            "description": repo["description"] or "",
                            "language": repo["language"] or "Python"
                        })
                
                # Respecter les limites de l'API GitHub
                time.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"Erreur lors de la recherche pour '{keyword}': {e}")
                continue
        
        # Trier par nombre d'étoiles
        repos.sort(key=lambda x: x["stars"], reverse=True)
        
        self.logger.info(f"Trouvé {len(repos)} dépôts uniques")
        return repos
    
    def update_github_domain(self, domain: str, config: Dict):
        """Met à jour un domaine en utilisant l'API GitHub directe"""
        self.logger.info(f"=== Mise à jour du domaine {domain.upper()} (API GitHub) ===")
        
        try:
            # Rechercher les dépôts
            repos = self.search_github_repos(config["keywords"])
            
            # Ajouter les librairies spécifiques si définies
            if config["specific_libs"]:
                self.logger.info(f"Ajout de {len(config['specific_libs'])} librairies spécifiques...")
                specific_repos = self.get_specific_libraries_info(config["specific_libs"])
                
                # Ajouter seulement si pas déjà présents
                existing_names = {repo["name"] for repo in repos}
                for lib in specific_repos:
                    if lib["name"] not in existing_names:
                        repos.append(lib)
                        self.logger.info(f"➕ Ajouté: {lib['name']} avec {lib['stars']} étoiles")
            
            # Prendre le top 100
            top_repos = repos[:100]
            
            # Ajouter les rangs avec gestion des ex-aequo
            current_rank = 1
            for i, repo in enumerate(top_repos):
                if i > 0 and top_repos[i]["stars"] < top_repos[i-1]["stars"]:
                    current_rank = i + 1
                repo["rank"] = current_rank
            
            # Créer le fichier JSON du domaine
            domain_data = {
                "libraries": top_repos,
                "domain": domain,
                "description": config["description"],
                "keywords": config["keywords"]
            }
            
            # Sauvegarder
            output_path = self.data_dir / f"{domain}-libraries.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(domain_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Domaine {domain} mis à jour: {len(top_repos)} librairies")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la mise à jour du domaine {domain}: {e}")
            raise
    
    def get_specific_libraries_info(self, specific_libs: List[str]) -> List[Dict]:
        """Récupère les informations des librairies spécifiques via GitHub API"""
        libs_info = []
        
        for lib in specific_libs:
            try:
                url = f"https://api.github.com/repos/{lib}"
                response = requests.get(url)
                response.raise_for_status()
                
                data = response.json()
                libs_info.append({
                    "name": lib,
                    "github_url": data["html_url"],
                    "stars": data["stargazers_count"],
                    "description": data["description"] or f"Bibliothèque {lib}",
                    "language": data["language"] or "Python"
                })
                
                self.logger.info(f"✅ {lib}: {data['stargazers_count']} étoiles")
                
                # Respecter les limites de l'API
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.warning(f"Erreur pour {lib}: {e}")
                continue
        
        return libs_info
    
    def update_all_domains(self):
        """Met à jour tous les domaines configurés"""
        self.logger.info("🚀 Début de la mise à jour de tous les domaines")
        
        for domain, config in DOMAIN_CONFIGS.items():
            try:
                if config["use_ascl"]:
                    # Utiliser le système ASCL existant
                    self.update_astrophysics_cosmology_domain()
                else:
                    # Utiliser l'API GitHub directe
                    self.update_github_domain(domain, config)
                    
            except Exception as e:
                self.logger.error(f"❌ Échec de la mise à jour du domaine {domain}: {e}")
                # Continuer avec les autres domaines
                continue
        
        self.logger.info("🎉 Mise à jour de tous les domaines terminée")
    
    def update_specific_domain(self, domain: str):
        """Met à jour un domaine spécifique"""
        if domain not in DOMAIN_CONFIGS:
            self.logger.error(f"❌ Domaine '{domain}' non configuré")
            return
        
        config = DOMAIN_CONFIGS[domain]
        
        try:
            if config["use_ascl"]:
                self.update_astrophysics_cosmology_domain()
            else:
                self.update_github_domain(domain, config)
                
        except Exception as e:
            self.logger.error(f"❌ Échec de la mise à jour du domaine {domain}: {e}")
            raise

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mise à jour des domaines")
    parser.add_argument("--domain", help="Domaine spécifique à mettre à jour")
    parser.add_argument("--all", action="store_true", help="Mettre à jour tous les domaines")
    
    args = parser.parse_args()
    
    updater = DomainUpdater()
    
    if args.domain:
        updater.update_specific_domain(args.domain)
    elif args.all:
        updater.update_all_domains()
    else:
        # Par défaut, mettre à jour tous les domaines
        updater.update_all_domains()

if __name__ == "__main__":
    main()
