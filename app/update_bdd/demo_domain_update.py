#!/usr/bin/env python3
"""
Script de démonstration du système de mise à jour des domaines.
Montre comment le système fonctionne avec des exemples concrets.
"""

import sys
from pathlib import Path
import json

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from update_all_domains import DomainUpdater, DOMAIN_CONFIGS

def demo_configuration():
    """Démonstration de la configuration des domaines"""
    print("🔧 CONFIGURATION DES DOMAINES")
    print("=" * 60)
    
    for domain, config in DOMAIN_CONFIGS.items():
        approach = "ASCL (système existant)" if config["use_ascl"] else "GitHub API (nouveau)"
        print(f"\n📁 {domain.upper()}")
        print(f"   Approche: {approach}")
        print(f"   Mots-clés: {', '.join(config['keywords'][:5])}...")
        print(f"   Description: {config['description'][:80]}...")
        
        if config["specific_libs"]:
            print(f"   Librairies spécifiques: {len(config['specific_libs'])}")
            for lib in config["specific_libs"][:2]:  # Montrer seulement les 2 premières
                print(f"     - {lib}")
            if len(config["specific_libs"]) > 2:
                print(f"     ... et {len(config['specific_libs']) - 2} autres")

def demo_github_search_logic():
    """Démonstration de la logique de recherche GitHub"""
    print("\n🔍 LOGIQUE DE RECHERCHE GITHUB")
    print("=" * 60)
    
    # Exemple avec le domaine finance
    finance_config = DOMAIN_CONFIGS["finance"]
    
    print(f"Domaine: finance")
    print(f"Approche: GitHub API directe")
    print(f"Mots-clés: {', '.join(finance_config['keywords'][:8])}...")
    
    print("\nProcessus de recherche:")
    print("1. Pour chaque mot-clé, recherche GitHub avec:")
    print("   - language:python")
    print("   - stars:>100")
    print("   - tri par nombre d'étoiles (décroissant)")
    
    print("\n2. Exemple de requête:")
    example_query = "finance language:python stars:>100"
    print(f"   Query: {example_query}")
    
    print("\n3. Résultats:")
    print("   - Dépôts uniques (éviter les doublons)")
    print("   - Tri par popularité")
    print("   - Top 100 librairies")
    print("   - Gestion des ex-aequo")

def demo_ascl_logic():
    """Démonstration de la logique ASCL"""
    print("\n📚 LOGIQUE ASCL (ASTRONOMIE)")
    print("=" * 60)
    
    astronomy_config = DOMAIN_CONFIGS["astronomy"]
    
    print(f"Domaine: astronomy")
    print(f"Approche: ASCL (Astrophysics Source Code Library)")
    print(f"Mots-clés: {', '.join(astronomy_config['keywords'][:8])}...")
    
    print("\nProcessus ASCL:")
    print("1. Téléchargement des données ASCL")
    print("2. Filtrage par mots-clés astronomie/cosmologie")
    print("3. Récupération du nombre d'étoiles GitHub")
    print("4. Ajout de librairies spécifiques importantes:")
    
    for lib in astronomy_config["specific_libs"]:
        print(f"   - {lib}")
    
    print("\n5. Tri et classement final")

def demo_usage_examples():
    """Exemples d'utilisation du système"""
    print("\n💻 EXEMPLES D'UTILISATION")
    print("=" * 60)
    
    print("1. Mettre à jour tous les domaines:")
    print("   python3 update_all_domains.py")
    
    print("\n2. Mettre à jour un domaine spécifique:")
    print("   python3 update_all_domains.py --domain finance")
    print("   python3 update_all_domains.py --domain machine_learning")
    
    print("\n3. Mettre à jour explicitement tous les domaines:")
    print("   python3 update_all_domains.py --all")
    
    print("\n4. Mise à jour programmatique:")
    print("   from update_all_domains import DomainUpdater")
    print("   updater = DomainUpdater()")
    print("   updater.update_specific_domain('finance')")

def demo_output_structure():
    """Démonstration de la structure de sortie"""
    print("\n📊 STRUCTURE DE SORTIE")
    print("=" * 60)
    
    print("Chaque domaine génère un fichier JSON:")
    print("app/data/{domain}-libraries.json")
    
    print("\nStructure du JSON:")
    example_json = {
        "libraries": [
            {
                "name": "owner/repo",
                "github_url": "https://github.com/owner/repo",
                "stars": 1500,
                "rank": 1,
                "description": "Description du repo",
                "language": "Python"
            }
        ],
        "domain": "finance",
        "description": "Description du domaine",
        "keywords": ["finance", "trading", "portfolio"]
    }
    
    print(json.dumps(example_json, indent=2, ensure_ascii=False))
    
    print("\nFichiers générés:")
    for domain in DOMAIN_CONFIGS.keys():
        print(f"   - {domain}-libraries.json")

def demo_extensibility():
    """Démonstration de l'extensibilité"""
    print("\n🚀 EXTENSIBILITÉ")
    print("=" * 60)
    
    print("Pour ajouter un nouveau domaine:")
    
    new_domain_example = {
        "web_development": {
            "use_ascl": False,
            "keywords": ["web", "django", "flask", "fastapi", "react", "vue"],
            "description": "Top web development frameworks and libraries",
            "specific_libs": []
        }
    }
    
    print("1. Ajouter dans DOMAIN_CONFIGS:")
    print(json.dumps(new_domain_example, indent=2, ensure_ascii=False))
    
    print("\n2. Le système détecte automatiquement:")
    print("   - use_ascl: False → Utilise GitHub API")
    print("   - use_ascl: True → Utilise ASCL")
    
    print("\n3. Mise à jour immédiate:")
    print("   python3 update_all_domains.py --domain web_development")

def main():
    """Fonction principale de démonstration"""
    print("🎯 DÉMONSTRATION DU SYSTÈME DE MISE À JOUR DES DOMAINES")
    print("=" * 80)
    
    try:
        # Exécuter toutes les démonstrations
        demo_configuration()
        demo_github_search_logic()
        demo_ascl_logic()
        demo_usage_examples()
        demo_output_structure()
        demo_extensibility()
        
        print("\n" + "=" * 80)
        print("🎉 DÉMONSTRATION TERMINÉE!")
        print("\n📋 RÉSUMÉ:")
        print("   ✅ Système hybride ASCL + GitHub API")
        print("   ✅ Configuration centralisée et extensible")
        print("   ✅ Gestion automatique des approches")
        print("   ✅ Structure modulaire et maintenable")
        print("   ✅ Facile d'ajouter de nouveaux domaines")
        
        print("\n🚀 Prêt à utiliser!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
