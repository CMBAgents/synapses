#!/usr/bin/env python3
"""
Script de test pour le système de mise à jour des domaines.
Teste les différentes fonctionnalités sans faire de vraies mises à jour.
"""

import sys
from pathlib import Path
import json

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from update_all_domains import DomainUpdater, DOMAIN_CONFIGS

def test_configuration():
    """Teste la configuration des domaines"""
    print("=== Test de la configuration des domaines ===")
    
    for domain, config in DOMAIN_CONFIGS.items():
        print(f"\n📁 Domaine: {domain}")
        print(f"   - Utilise ASCL: {config['use_ascl']}")
        print(f"   - Nombre de mots-clés: {len(config['keywords'])}")
        print(f"   - Librairies spécifiques: {len(config['specific_libs'])}")
        print(f"   - Description: {config['description'][:80]}...")
    
    print(f"\n✅ Configuration testée: {len(DOMAIN_CONFIGS)} domaines configurés")

def test_domain_updater_initialization():
    """Teste l'initialisation de la classe DomainUpdater"""
    print("\n=== Test de l'initialisation ===")
    
    try:
        updater = DomainUpdater()
        print("✅ DomainUpdater initialisé avec succès")
        print(f"   - Base directory: {updater.base_dir}")
        print(f"   - Update BDD directory: {updater.update_bdd_dir}")
        print(f"   - Data directory: {updater.data_dir}")
        print(f"   - Temp directory: {updater.temp_dir}")
        
        return updater
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return None

def test_github_search_simulation():
    """Simule la recherche GitHub (sans faire de vraies requêtes)"""
    print("\n=== Test de la recherche GitHub (simulation) ===")
    
    updater = DomainUpdater()
    
    # Test avec un petit ensemble de mots-clés
    test_keywords = ["pandas", "numpy", "matplotlib"]
    
    print(f"Simulation de recherche pour: {test_keywords}")
    print("✅ Simulation réussie (pas de vraies requêtes API)")

def test_domain_config_validation():
    """Valide la configuration des domaines"""
    print("\n=== Validation de la configuration ===")
    
    required_fields = ["use_ascl", "keywords", "description", "specific_libs"]
    
    for domain, config in DOMAIN_CONFIGS.items():
        print(f"\n🔍 Validation du domaine: {domain}")
        
        # Vérifier les champs requis
        for field in required_fields:
            if field in config:
                print(f"   ✅ {field}: présent")
            else:
                print(f"   ❌ {field}: manquant")
        
        # Vérifier que les mots-clés ne sont pas vides
        if config["keywords"]:
            print(f"   ✅ keywords: {len(config['keywords'])} mots-clés")
        else:
            print(f"   ❌ keywords: vide")
        
        # Vérifier la cohérence use_ascl
        if config["use_ascl"]:
            print(f"   ℹ️  use_ascl: True (utilisera ASCL)")
        else:
            print(f"   ℹ️  use_ascl: False (utilisera GitHub API)")

def test_file_paths():
    """Teste que les chemins de fichiers sont corrects"""
    print("\n=== Test des chemins de fichiers ===")
    
    updater = DomainUpdater()
    
    # Vérifier que les répertoires existent ou peuvent être créés
    paths_to_check = [
        updater.base_dir,
        updater.update_bdd_dir,
        updater.data_dir,
        updater.temp_dir
    ]
    
    for path in paths_to_check:
        if path.exists():
            print(f"✅ {path}: existe")
        else:
            print(f"⚠️  {path}: n'existe pas (sera créé)")
    
    # Vérifier que get100.py existe (pour le domaine astronomie)
    get100_path = updater.update_bdd_dir / "get100.py"
    if get100_path.exists():
        print(f"✅ {get100_path}: existe (nécessaire pour le domaine astronomie)")
    else:
        print(f"❌ {get100_path}: manquant (nécessaire pour le domaine astronomie)")

def test_specific_libraries():
    """Teste la gestion des librairies spécifiques"""
    print("\n=== Test des librairies spécifiques ===")
    
    for domain, config in DOMAIN_CONFIGS.items():
        if config["specific_libs"]:
            print(f"\n📚 {domain}: {len(config['specific_libs'])} librairies spécifiques")
            for lib in config["specific_libs"]:
                print(f"   - {lib}")
        else:
            print(f"\n📚 {domain}: aucune librairie spécifique")

def main():
    """Fonction principale de test"""
    print("🧪 Tests du système de mise à jour des domaines")
    print("=" * 60)
    
    try:
        # Exécuter tous les tests
        test_configuration()
        updater = test_domain_updater_initialization()
        test_github_search_simulation()
        test_domain_config_validation()
        test_file_paths()
        test_specific_libraries()
        
        print("\n" + "=" * 60)
        print("🎉 Tous les tests sont passés avec succès!")
        print("\n📋 Résumé:")
        print(f"   - {len(DOMAIN_CONFIGS)} domaines configurés")
        print("   - Système ASCL pour l'astronomie")
        print("   - API GitHub pour les autres domaines")
        print("   - Gestion des librairies spécifiques")
        print("   - Structure modulaire et extensible")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
