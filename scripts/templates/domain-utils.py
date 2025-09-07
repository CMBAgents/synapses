#!/usr/bin/env python3
"""
Utilitaires partagés pour la création et la gestion des domaines.
Ce fichier contient les classes et fonctions communes utilisées par les scripts de domaines.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any
import subprocess

class DomainSystemConfig:
    def __init__(self, config_path: str = "domain-config.json"):
        self.config = self.load_config(config_path)
        self.paths = self.config["paths"]
        self.templates = self.config["templates"]
        self.maintenance = self.config["maintenance"]
        self.domain_mappings = self.config["domain_mappings"]
        self.special_domains = self.config["special_domains"]
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_path(self, key: str) -> Path:
        """Retourne le chemin configuré"""
        return Path(self.paths[key])
    
    def get_template_setting(self, key: str):
        """Retourne le paramètre de template configuré"""
        return self.templates[key]
    
    def get_domain_display_name(self, domain_id: str) -> str:
        """Retourne le nom d'affichage d'un domaine"""
        return self.domain_mappings.get(domain_id, domain_id.title())
    
    def get_domain_description(self, domain_id: str) -> str:
        """Retourne la description d'un domaine"""
        # Vérifier d'abord les domaines spéciaux
        if domain_id == 'astronomy':
            return 'Celestial observations, gravitational waves, and cosmic microwave background analysis'
        elif domain_id == 'biochemistry':
            return 'Molecular dynamics, drug discovery, and computational biology'
        elif domain_id == 'finance':
            return 'Portfolio optimization, algorithmic trading, and financial analysis'
        elif domain_id == 'machinelearning':
            return 'Deep learning, neural networks, and AI model development'
        
        # Pour les nouveaux domaines, utiliser une description générique
        return f'Top libraries in {domain_id} with cutting-edge research and development'
    
    def is_special_domain(self, domain_id: str) -> bool:
        """Vérifie si un domaine a des règles spéciales"""
        return domain_id in self.special_domains

class DomainDescriptionGenerator:
    def __init__(self):
        self.domain_patterns = {
            'physics': ['particle', 'quantum', 'mechanics', 'relativity', 'nuclear'],
            'chemistry': ['molecular', 'chemical', 'reaction', 'catalyst', 'organic'],
            'biology': ['genomic', 'cellular', 'evolutionary', 'ecological', 'molecular'],
            'mathematics': ['numerical', 'analytical', 'statistical', 'optimization', 'algebraic'],
            'engineering': ['structural', 'mechanical', 'electrical', 'civil', 'aerospace'],
            'computer_science': ['algorithmic', 'computational', 'software', 'database', 'network'],
            'medicine': ['clinical', 'pharmaceutical', 'diagnostic', 'therapeutic', 'biomedical'],
            'geology': ['geophysical', 'seismic', 'mineralogical', 'stratigraphic', 'tectonic']
        }
    
    def generate_description(self, domain_id: str, domain_name: str) -> str:
        """Génère une description intelligente basée sur le domaine"""
        # Vérifier d'abord les domaines spéciaux
        if domain_id == 'astronomy':
            return 'Celestial observations, gravitational waves, and cosmic microwave background analysis'
        elif domain_id == 'biochemistry':
            return 'Molecular dynamics, drug discovery, and computational biology'
        elif domain_id == 'finance':
            return 'Portfolio optimization, algorithmic trading, and financial analysis'
        elif domain_id == 'machinelearning':
            return 'Deep learning, neural networks, and AI model development'
        
        # Pour les nouveaux domaines, utiliser les patterns
        for pattern_id, keywords in self.domain_patterns.items():
            if any(keyword in domain_id.lower() for keyword in keywords):
                return f'Advanced {domain_name.lower()} with focus on {", ".join(keywords[:3])}'
        
        # Fallback générique
        return f'Top libraries in {domain_name.lower()} with cutting-edge research and development'
    
    def generate_keywords(self, domain_id: str, domain_name: str) -> List[str]:
        """Génère des mots-clés pertinents pour le domaine"""
        base_keywords = [domain_id.lower(), domain_name.lower().replace(' & ', ' ').replace(' ', '-')]
        
        # Ajouter des mots-clés spécifiques au domaine
        if domain_id == 'astronomy':
            base_keywords.extend(['astrophysics', 'cosmology', 'gravitational-waves', 'cmb'])
        elif domain_id == 'biochemistry':
            base_keywords.extend(['molecular-dynamics', 'drug-discovery', 'bioinformatics'])
        elif domain_id == 'finance':
            base_keywords.extend(['trading', 'portfolio-optimization', 'risk-management'])
        elif domain_id == 'machinelearning':
            base_keywords.extend(['deep-learning', 'neural-networks', 'artificial-intelligence'])
        
        return base_keywords

class LibraryGenerator:
    def __init__(self, config: DomainSystemConfig):
        self.config = config
    
    def generate_sample_libraries(self, domain_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Génère des librairies d'exemple pour un nouveau domaine"""
        libraries = []
        
        for i in range(1, count + 1):
            library = {
                "rank": i,
                "name": f"example-org/{domain_id}-library-{i}",
                "github_url": f"https://github.com/example-org/{domain_id}-library-{i}",
                "stars": random.randint(100, 10000),
                "hasContextFile": False,
                "contextFileName": None
            }
            libraries.append(library)
        
        return libraries
    
    def create_domain_json(self, domain_id: str, domain_name: str, libraries: List[Dict]) -> Dict[str, Any]:
        """Crée la structure JSON complète pour un domaine"""
        description_gen = DomainDescriptionGenerator()
        
        return {
            "libraries": libraries,
            "domain": domain_name,
            "description": description_gen.generate_description(domain_id, domain_name),
            "keywords": description_gen.generate_keywords(domain_id, domain_name)
        }

class MaintenanceIntegrator:
    def __init__(self, config: DomainSystemConfig):
        self.config = config
    
    def call_maintenance_system(self, domain_id: str):
        """Appelle le système de maintenance existant"""
        try:
            # Construire le chemin correct vers le script de génération de contextes
            context_script = Path.cwd().parent / "maintenance" / "context-manager-unified.py"
            
            if not context_script.exists():
                print(f"⚠️  Script de génération de contextes non trouvé: {context_script}")
                return False
            
            print(f"🔧 Appel du système de génération de contextes pour le domaine '{domain_id}'...")
            
            # Exécuter le script de génération de contextes
            result = subprocess.run(
                ["python3", str(context_script), "--full"],
                capture_output=True,
                text=True,
                cwd=Path.cwd().parent.parent  # Remonter à la racine du projet
            )
            
            if result.returncode == 0:
                print(f"✅ Génération de contextes terminée avec succès pour '{domain_id}'")
                return True
            else:
                print(f"⚠️  Génération de contextes terminée avec des avertissements pour '{domain_id}'")
                print(f"Sortie: {result.stdout}")
                if result.stderr:
                    print(f"Erreurs: {result.stderr}")
                return True  # On continue même avec des avertissements
                
        except Exception as e:
            print(f"❌ Erreur lors de l'appel de la génération de contextes: {e}")
            return False

def validate_domain_name(domain_name: str) -> str:
    """Valide et normalise le nom du domaine"""
    # Convertir en minuscules et remplacer les espaces par des tirets
    domain_id = domain_name.lower().replace(' ', '-').replace('&', 'and')
    
    # Supprimer les caractères non autorisés
    domain_id = ''.join(c for c in domain_id if c.isalnum() or c == '-')
    
    # Éviter les doubles tirets
    domain_id = '-'.join(filter(None, domain_id.split('-')))
    
    return domain_id
