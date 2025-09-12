#!/usr/bin/env python3
"""
Système unifié de mise à jour des domaines avec API GitHub.
Gère tous les domaines : astronomy, biochemistry, finance, machinelearning, etc.

Usage:
    python3 unified-domain-updater.py --domain astronomy
    python3 unified-domain-updater.py --all
    python3 unified-domain-updater.py --maintenance
"""

import requests
import json
import sys
import time
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DomainConfig:
    """Configuration pour un domaine"""
    name: str
    display_name: str
    description: str
    keywords: List[str]
    specific_libs: List[str]
    use_ascl: bool
    max_libraries: int = 100

class GitHubAPIClient:
    """Client pour l'API GitHub avec gestion des limites de taux"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        else:
            self.session.headers.update({
                'Accept': 'application/vnd.github.v3+json'
            })
    
    def search_repositories(self, query: str, sort: str = 'stars', order: str = 'desc', per_page: int = 100) -> List[Dict]:
        """Recherche des dépôts GitHub avec l'API officielle"""
        url = f"{self.base_url}/search/repositories"
        params = {
            'q': query,
            'sort': sort,
            'order': order,
            'per_page': per_page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API GitHub: {e}")
            return []
    
    def get_rate_limit(self) -> Dict:
        """Vérifie les limites de taux de l'API"""
        url = f"{self.base_url}/rate_limit"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {'rate': {'remaining': 0, 'limit': 60}}

class ASCLScraper:
    """Scraper pour l'Astrophysics Source Code Library (pour le domaine astronomy)"""
    
    def __init__(self):
        self.ascl_url = "https://ascl.net/code/json"
    
    def download_ascl_data(self) -> Dict:
        """Télécharge les données ASCL"""
        try:
            response = requests.get(self.ascl_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur téléchargement ASCL: {e}")
            return {}
    
    def extract_github_repos(self, data: Dict) -> Set[str]:
        """Extrait les URLs GitHub des données ASCL"""
        import re
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
    
    def get_github_stars_scraping(self, repo_path: str) -> int:
        """Récupère les étoiles en scrapant la page GitHub (méthode existante)"""
        import re
        import random
        import time
        
        time.sleep(random.uniform(0.1, 0.5))  # Éviter le rate limiting
        
        url = f"https://github.com/{repo_path}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Pattern: "Star this repository (NUMBER)"
                star_pattern = r'Star this repository \((\d+)\)'
                match = re.search(star_pattern, response.text)
                if match:
                    return int(match.group(1))
                
                # Pattern alternatif
                alt_pattern = r'aria-label="(\d+) users? starred this repository"'
                match = re.search(alt_pattern, response.text)
                if match:
                    return int(match.group(1))
            
            return 0
        except Exception:
            return 0

class UnifiedDomainUpdater:
    """Mise à jour unifiée pour tous les domaines"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_client = GitHubAPIClient(github_token)
        self.ascl_scraper = ASCLScraper()
        self.data_dir = Path("app/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration des domaines
        self.domains = {
            'astronomy': DomainConfig(
                name='astronomy',
                display_name='Astrophysics & Cosmology',
                description='Top astronomy and cosmology libraries for celestial observations, gravitational waves, and cosmic microwave background analysis',
                keywords=['astronomy', 'cosmology', 'astrophysics', 'gravitational waves', 'CMB', 'healpy', 'astropy', 'pixell', 'galaxy', 'stellar', 'exoplanet', 'radio astronomy', 'solar', 'planetary', 'stellar evolution', 'black hole', 'neutron star', 'supernova', 'dark matter', 'dark energy'],
                specific_libs=[
                    'CMBAgents/cmbagent',
                    'cmbant/camb', 
                    'cmbant/getdist',
                    'CobayaSampler/cobaya',
                    'simonsobs/pixell',
                    'astropy/astropy',
                    'astropy/photutils',
                    'astropy/astroquery',
                    'dstndstn/astrometry.net',
                    'einsteinpy/einsteinpy',
                    'lightkurve/lightkurve',
                    'gwpy/gwpy',
                    'healpy/healpy'
                ],
                use_ascl=False,
                max_libraries=100
            ),
            'biochemistry': DomainConfig(
                name='biochemistry',
                display_name='Biochemistry & Bioinformatics',
                description='Top biochemistry and bioinformatics libraries for molecular dynamics, drug discovery, and computational biology',
                keywords=['biochemistry', 'bioinformatics', 'molecular dynamics', 'drug discovery', 'computational biology', 'biopython', 'mdanalysis', 'openmm', 'rdkit', 'gromacs'],
                specific_libs=[
                    'biopython/biopython',
                    'scikit-bio/scikit-bio',
                    'mdanalysis/mdanalysis',
                    'openmm/openmm',
                    'rdkit/rdkit',
                    'openbabel/openbabel',
                    'gromacs/gromacs'
                ],
                use_ascl=False,
                max_libraries=10
            ),
            'finance': DomainConfig(
                name='finance',
                display_name='Finance & Trading',
                description='Top finance and trading libraries for portfolio optimization, algorithmic trading, and financial analysis',
                keywords=['finance', 'trading', 'portfolio', 'quantitative', 'zipline', 'yfinance', 'pyfolio', 'empyrical', 'alphalens', 'mlfinlab'],
                specific_libs=[
                    'quantopian/zipline',
                    'ranaroussi/yfinance',
                    'quantopian/pyfolio',
                    'quantopian/empyrical',
                    'quantopian/alphalens',
                    'mlfinlab/mlfinlab'
                ],
                use_ascl=False,
                max_libraries=10
            ),
            'machinelearning': DomainConfig(
                name='machinelearning',
                display_name='Machine Learning & AI',
                description='Top machine learning and deep learning libraries for AI, neural networks, and data science',
                keywords=['machine learning', 'deep learning', 'artificial intelligence', 'neural networks', 'data science', 'pytorch', 'tensorflow', 'scikit-learn', 'keras', 'transformers'],
                specific_libs=[
                    'pytorch/pytorch',
                    'tensorflow/tensorflow',
                    'scikit-learn/scikit-learn',
                    'keras-team/keras',
                    'huggingface/transformers',
                    'pandas-dev/pandas',
                    'numpy/numpy',
                    'scipy/scipy',
                    'matplotlib/matplotlib'
                ],
                use_ascl=False,
                max_libraries=10
            )
        }
    
    def add_domain_automatically(self, domain_name: str, display_name: str, description: str, 
                                keywords: List[str], specific_libs: List[str], use_ascl: bool = False):
        """
        Automatise complètement l'ajout d'un nouveau domaine.
        Met à jour tous les fichiers de configuration et génère les données.
        """
        logger.info(f"🚀 Ajout automatique du domaine '{domain_name}'...")
        
        try:
            # 1. AUTOMATISER : Mise à jour du script unifié
            self._update_unified_script(domain_name, display_name, description, keywords, specific_libs, use_ascl)
            
            # 2. AUTOMATISER : Mise à jour de config.json
            self._update_config_json(domain_name, display_name, description)
            
            # 3. AUTOMATISER : Mise à jour de domains.ts
            self._update_domains_ts(domain_name, display_name, description)
            
            # 4. AUTOMATISER : Génération des données
            logger.info(f"📊 Génération des données pour le domaine '{domain_name}'...")
            self._add_domain_to_config(domain_name, display_name, description, keywords, specific_libs, use_ascl)
            self.update_domain(domain_name)
            
            # 5. AUTOMATISER : Génération des routes
            logger.info("🛣️ Génération des routes...")
            self._generate_domain_routes()
            
            # 6. AUTOMATISER : Génération des contextes
            logger.info("📚 Génération des contextes...")
            self._generate_contexts(domain_name)
            
            logger.info(f"✅ Domaine '{domain_name}' ajouté avec succès !")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout du domaine '{domain_name}': {e}")
            raise
    
    def _update_unified_script(self, domain_name: str, display_name: str, description: str, 
                              keywords: List[str], specific_libs: List[str], use_ascl: bool):
        """Met à jour le script unifié avec la nouvelle configuration de domaine"""
        script_path = Path(__file__)
        content = script_path.read_text()
        
        # Créer la nouvelle configuration de domaine
        domain_config = f"""            '{domain_name}': DomainConfig(
                name='{domain_name}',
                display_name='{display_name}',
                description='{description}',
                keywords={keywords},
                specific_libs={specific_libs},
                use_ascl={use_ascl},
                max_libraries=10
            ),"""
        
        # Trouver la fin de la section domains et insérer la nouvelle configuration
        pattern = r"(\s+)\}\s*$"
        replacement = f"\\1{domain_config}\n\\1}}"
        
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if new_content != content:
            script_path.write_text(new_content)
            logger.info(f"✅ Script unifié mis à jour avec le domaine '{domain_name}'")
        else:
            logger.warning(f"⚠️ Impossible de mettre à jour le script unifié pour '{domain_name}'")
    
    def _update_config_json(self, domain_name: str, display_name: str, description: str):
        """Met à jour config.json avec le nouveau domaine"""
        config_path = Path("config.json")
        
        if not config_path.exists():
            logger.error("❌ Fichier config.json introuvable")
            return
        
        config = json.loads(config_path.read_text())
        
        # Ajouter le domaine dans supported
        if 'domains' not in config:
            config['domains'] = {}
        if 'supported' not in config['domains']:
            config['domains']['supported'] = []
        
        if domain_name not in config['domains']['supported']:
            config['domains']['supported'].append(domain_name)
        
        # Ajouter les mappings
        if 'displayNames' not in config['domains']:
            config['domains']['displayNames'] = {}
        config['domains']['displayNames'][domain_name] = display_name
        
        if 'descriptions' not in config['domains']:
            config['domains']['descriptions'] = {}
        config['domains']['descriptions'][domain_name] = description
        
        if 'defaultPrograms' not in config['domains']:
            config['domains']['defaultPrograms'] = {}
        config['domains']['defaultPrograms'][domain_name] = []
        
        # Sauvegarder
        config_path.write_text(json.dumps(config, indent=2))
        logger.info(f"✅ config.json mis à jour avec le domaine '{domain_name}'")
    
    def _update_domains_ts(self, domain_name: str, display_name: str, description: str):
        """Met à jour domains.ts avec le nouveau domaine"""
        domains_ts_path = Path("app/config/domains.ts")
        
        if not domains_ts_path.exists():
            logger.error("❌ Fichier domains.ts introuvable")
            return
        
        content = domains_ts_path.read_text()
        
        # Ajouter dans domain_mappings
        mapping_entry = f"  '{domain_name}': '{display_name}',"
        if f"'{domain_name}':" not in content:
            # Trouver la fin de domain_mappings et ajouter
            pattern = r"(export const domain_mappings = \{[^}]+)(\s+\};)"
            replacement = f"\\1{mapping_entry}\n\\2"
            content = re.sub(pattern, replacement, content)
        
        # Ajouter dans descriptions
        desc_entry = f"  '{domain_name}': '{description}',"
        if f"'{domain_name}':" not in content or "descriptions" not in content:
            # Trouver la fin de descriptions et ajouter
            pattern = r"(export const descriptions = \{[^}]+)(\s+\};)"
            replacement = f"\\1{desc_entry}\n\\2"
            content = re.sub(pattern, replacement, content)
        
        domains_ts_path.write_text(content)
        logger.info(f"✅ domains.ts mis à jour avec le domaine '{domain_name}'")
    
    def _add_domain_to_config(self, domain_name: str, display_name: str, description: str, 
                             keywords: List[str], specific_libs: List[str], use_ascl: bool):
        """Ajoute le domaine à la configuration interne"""
        self.domains[domain_name] = DomainConfig(
            name=domain_name,
            display_name=display_name,
            description=description,
            keywords=keywords,
            specific_libs=specific_libs,
            use_ascl=use_ascl,
            max_libraries=10
        )
    
    def _generate_domain_routes(self):
        """Génère les routes pour les domaines"""
        try:
            import subprocess
            result = subprocess.run([
                "python3", "scripts/templates/generate-domain-routes.py"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                logger.info("✅ Routes générées avec succès")
            else:
                logger.error(f"❌ Erreur génération routes: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération des routes: {e}")
    
    def _generate_contexts(self, domain_name: str):
        """Génère les contextes pour le nouveau domaine"""
        try:
            import subprocess
            result = subprocess.run([
                "python3", "-c", 
                f"import requests; requests.post('http://localhost:3000/api/generate-all-contexts', json={{'domain': '{domain_name}'}})"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                logger.info(f"✅ Contextes générés pour le domaine '{domain_name}'")
            else:
                logger.warning(f"⚠️ Génération contextes échouée: {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ Erreur génération contextes: {e}")
    
    def update_astronomy_domain(self) -> List[Dict]:
        """Met à jour le domaine astronomy en utilisant ASCL (méthode existante)"""
        logger.info("🔄 Mise à jour du domaine astronomy via ASCL...")
        
        # Télécharger les données ASCL
        ascl_data = self.ascl_scraper.download_ascl_data()
        if not ascl_data:
            logger.error("❌ Impossible de télécharger les données ASCL")
            return []
        
        # Extraire les repos GitHub
        repos = self.ascl_scraper.extract_github_repos(ascl_data)
        logger.info(f"📚 Trouvé {len(repos)} dépôts GitHub dans ASCL")
        
        # Récupérer les étoiles
        libraries = []
        for i, repo_path in enumerate(repos):
            if i >= self.domains['astronomy'].max_libraries:
                break
                
            stars = self.ascl_scraper.get_github_stars_scraping(repo_path)
            if stars >= 0:
                libraries.append({
                    'name': repo_path,
                    'github_url': f'https://github.com/{repo_path}',
                    'stars': stars,
                    'rank': 0,  # Sera mis à jour après tri
                    'hasContextFile': False,
                    'contextFileName': None
                })
        
        # Ajouter les bibliothèques spécifiques
        for lib_name in self.domains['astronomy'].specific_libs:
            if not any(lib['name'] == lib_name for lib in libraries):
                # Récupérer les étoiles en temps réel via scraping
                stars = self.ascl_scraper.get_github_stars_scraping(lib_name)
                if stars >= 0:
                    libraries.append({
                        'name': lib_name,
                        'github_url': f'https://github.com/{lib_name}',
                        'stars': stars,
                        'rank': 0,
                        'hasContextFile': False,
                        'contextFileName': None
                    })
                else:
                    logger.warning(f"⚠️ Impossible de récupérer les étoiles pour {lib_name}")
        
        # Trier par étoiles et assigner les rangs
        libraries.sort(key=lambda x: x['stars'], reverse=True)
        current_rank = 1
        for i, lib in enumerate(libraries):
            if i > 0 and libraries[i]['stars'] < libraries[i-1]['stars']:
                current_rank = i + 1
            lib['rank'] = current_rank
        
        logger.info(f"✅ Domaine astronomy mis à jour: {len(libraries)} bibliothèques")
        return libraries
    
    def update_domain_with_github_api(self, domain_name: str) -> List[Dict]:
        """Met à jour un domaine en utilisant l'API GitHub avec mots-clés"""
        if domain_name not in self.domains:
            logger.error(f"❌ Domaine inconnu: {domain_name}")
            return []
        
        domain_config = self.domains[domain_name]
        logger.info(f"🔄 Mise à jour du domaine {domain_name} via API GitHub...")
        
        # Vérifier les limites de taux
        rate_limit = self.github_client.get_rate_limit()
        remaining = rate_limit.get('rate', {}).get('remaining', 0)
        if remaining < 10:
            logger.warning(f"⚠️ Limite de taux API faible: {remaining} requêtes restantes")
        
        libraries = []
        
        # Rechercher avec les mots-clés du domaine
        for keyword in domain_config.keywords[:10]:  # Augmenter à 10 mots-clés
            query = f"{keyword} language:python stars:>20"  # Réduire le seuil d'étoiles
            logger.info(f"🔍 Recherche: {query}")
            
            repos = self.github_client.search_repositories(query, per_page=30)
            
            for repo in repos:
                if len(libraries) >= domain_config.max_libraries:
                    break
                
                # Éviter les doublons
                repo_name = repo['full_name']
                if not any(lib['name'] == repo_name for lib in libraries):
                    libraries.append({
                        'name': repo_name,
                        'github_url': repo['html_url'],
                        'stars': repo['stargazers_count'],
                        'rank': 0,
                        'hasContextFile': False,
                        'contextFileName': None
                    })
            
            # Pause pour respecter les limites de taux
            time.sleep(1)
        
        # Ajouter les bibliothèques spécifiques
        for lib_name in domain_config.specific_libs:
            if not any(lib['name'] == lib_name for lib in libraries):
                # Rechercher la bibliothèque spécifique
                query = f"repo:{lib_name}"
                repos = self.github_client.search_repositories(query, per_page=1)
                
                if repos:
                    repo = repos[0]
                    libraries.append({
                        'name': repo['full_name'],
                        'github_url': repo['html_url'],
                        'stars': repo['stargazers_count'],
                        'rank': 0,
                        'hasContextFile': False,
                        'contextFileName': None
                    })
        
        # Trier par étoiles et assigner les rangs
        libraries.sort(key=lambda x: x['stars'], reverse=True)
        
        # Limiter au nombre maximum configuré
        libraries = libraries[:domain_config.max_libraries]
        
        current_rank = 1
        for i, lib in enumerate(libraries):
            if i > 0 and libraries[i]['stars'] < libraries[i-1]['stars']:
                current_rank = i + 1
            lib['rank'] = current_rank
        
        logger.info(f"✅ Domaine {domain_name} mis à jour: {len(libraries)} bibliothèques")
        return libraries
    
    def save_domain_json(self, domain_name: str, libraries: List[Dict]):
        """Sauvegarde les bibliothèques dans le fichier JSON du domaine en préservant les informations existantes"""
        if domain_name not in self.domains:
            return
        
        domain_config = self.domains[domain_name]
        json_path = self.data_dir / f"{domain_name}-libraries.json"
        
        # Charger les données existantes si le fichier existe
        existing_libraries = {}
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    # Créer un dictionnaire des bibliothèques existantes
                    for lib in existing_data.get('libraries', []):
                        existing_libraries[lib['name']] = lib
                logger.info(f"📚 Chargé {len(existing_libraries)} bibliothèques existantes")
            except Exception as e:
                logger.warning(f"⚠️ Erreur lors du chargement des données existantes: {e}")
        
        # Fusionner les nouvelles données avec les données existantes
        merged_libraries = []
        for lib in libraries:
            lib_name = lib['name']
            
            # Normaliser le nom pour la comparaison (insensible à la casse)
            lib_name_normalized = lib_name.lower()
            
            # Chercher une correspondance dans les bibliothèques existantes (insensible à la casse)
            matching_existing = None
            for existing_name, existing_lib in existing_libraries.items():
                if existing_name.lower() == lib_name_normalized:
                    matching_existing = (existing_name, existing_lib)
                    break
            
            if matching_existing:
                # Préserver les informations existantes (hasContextFile, contextFileName, etc.)
                existing_name, existing_lib = matching_existing
                merged_lib = {
                    'name': lib['name'],
                    'github_url': lib['github_url'],
                    'stars': lib['stars'],  # Mettre à jour le nombre d'étoiles
                    'rank': lib['rank'],    # Mettre à jour le rang
                    'hasContextFile': existing_lib.get('hasContextFile', False),  # Préserver
                    'contextFileName': existing_lib.get('contextFileName', None),  # Préserver
                }
                
                # Préserver d'autres champs existants si présents
                for key in ['description', 'lastUpdated', 'tags']:
                    if key in existing_lib:
                        merged_lib[key] = existing_lib[key]
                
                logger.info(f"🔄 Mis à jour: {lib_name} (était {existing_name}) - {lib['stars']} ⭐ (rang {lib['rank']}) - Context préservé: {existing_lib.get('hasContextFile', False)}")
            else:
                # Nouvelle bibliothèque
                merged_lib = {
                    'name': lib['name'],
                    'github_url': lib['github_url'],
                    'stars': lib['stars'],
                    'rank': lib['rank'],
                    'hasContextFile': False,
                    'contextFileName': None
                }
                logger.info(f"🆕 Nouvelle: {lib_name} - {lib['stars']} ⭐ (rang {lib['rank']})")
            
            merged_libraries.append(merged_lib)
        
        # Créer les données finales
        domain_data = {
            'libraries': merged_libraries,
            'domain': domain_name,
            'description': domain_config.description,
            'keywords': domain_config.keywords
        }
        
        # Sauvegarder
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(domain_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Fichier sauvegardé: {json_path}")
        logger.info(f"📊 Résumé: {len(merged_libraries)} bibliothèques total")
    
    def update_domain(self, domain_name: str):
        """Met à jour un domaine spécifique"""
        if domain_name not in self.domains:
            logger.error(f"❌ Domaine inconnu: {domain_name}")
            return False
        
        domain_config = self.domains[domain_name]
        
        if domain_config.use_ascl and domain_name == 'astronomy':
            # Utiliser la méthode ASCL pour l'astronomie
            libraries = self.update_astronomy_domain()
        else:
            # Utiliser l'API GitHub pour les autres domaines
            libraries = self.update_domain_with_github_api(domain_name)
        
        if libraries:
            self.save_domain_json(domain_name, libraries)
            return True
        
        return False
    
    def update_all_domains(self):
        """Met à jour tous les domaines"""
        logger.info("🚀 Mise à jour de tous les domaines...")
        
        results = {}
        for domain_name in self.domains.keys():
            logger.info(f"\n{'='*50}")
            logger.info(f"🔄 Mise à jour du domaine: {domain_name}")
            logger.info(f"{'='*50}")
            
            success = self.update_domain(domain_name)
            results[domain_name] = success
            
            if success:
                logger.info(f"✅ {domain_name}: Succès")
            else:
                logger.error(f"❌ {domain_name}: Échec")
        
        # Résumé
        logger.info(f"\n{'='*50}")
        logger.info("📊 RÉSUMÉ DE LA MISE À JOUR")
        logger.info(f"{'='*50}")
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        for domain, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"{status} {domain}")
        
        logger.info(f"\nRésultat: {successful}/{total} domaines mis à jour avec succès")
        
        return results

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Système unifié de mise à jour des domaines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 unified-domain-updater.py --domain astronomy
  python3 unified-domain-updater.py --domain finance
  python3 unified-domain-updater.py --all
  python3 unified-domain-updater.py --maintenance
  
  # Ajouter un nouveau domaine automatiquement:
  python3 unified-domain-updater.py --add-domain physics --display-name "Physics & Quantum" --description "Top physics and quantum computing libraries" --keywords "physics,quantum,quantum computing,quantum mechanics" --specific-libs "qiskit/qiskit,rigetti/pyquil,quantumlib/Cirq,google/quantum"
        """
    )
    
    parser.add_argument('--domain', help='Domaine à mettre à jour')
    parser.add_argument('--all', action='store_true', help='Mettre à jour tous les domaines')
    parser.add_argument('--maintenance', action='store_true', help='Mode maintenance (mise à jour complète)')
    parser.add_argument('--add-domain', help='Ajouter un nouveau domaine automatiquement')
    parser.add_argument('--display-name', help='Nom d\'affichage du nouveau domaine')
    parser.add_argument('--description', help='Description du nouveau domaine')
    parser.add_argument('--keywords', help='Mots-clés séparés par des virgules')
    parser.add_argument('--specific-libs', help='Bibliothèques spécifiques séparées par des virgules')
    parser.add_argument('--use-ascl', action='store_true', help='Utiliser ASCL pour ce domaine')
    parser.add_argument('--token', help='Token GitHub pour l\'API (optionnel)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialiser le système
    updater = UnifiedDomainUpdater(args.token)
    
    if args.add_domain:
        # Ajouter un nouveau domaine automatiquement
        if not args.display_name or not args.description or not args.keywords or not args.specific_libs:
            logger.error("❌ Pour ajouter un domaine, vous devez fournir: --display-name, --description, --keywords, --specific-libs")
            sys.exit(1)
        
        keywords = [k.strip() for k in args.keywords.split(',')]
        specific_libs = [lib.strip() for lib in args.specific_libs.split(',')]
        
        try:
            updater.add_domain_automatically(
                domain_name=args.add_domain,
                display_name=args.display_name,
                description=args.description,
                keywords=keywords,
                specific_libs=specific_libs,
                use_ascl=args.use_ascl
            )
            logger.info(f"✅ Domaine '{args.add_domain}' ajouté avec succès !")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout du domaine: {e}")
            sys.exit(1)
    elif args.maintenance or args.all:
        # Mise à jour complète
        updater.update_all_domains()
    elif args.domain:
        # Mise à jour d'un domaine spécifique
        success = updater.update_domain(args.domain)
        if success:
            logger.info(f"✅ Domaine {args.domain} mis à jour avec succès")
        else:
            logger.error(f"❌ Échec de la mise à jour du domaine {args.domain}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
