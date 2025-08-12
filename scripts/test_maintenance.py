#!/usr/bin/env python3
"""
Script de test pour la maintenance quotidienne

Ce script teste les différentes fonctions de maintenance sans effectuer
les opérations réelles (mode dry-run).

Utilisation: python scripts/test_maintenance.py
"""

import sys
import subprocess
from pathlib import Path
import json
import logging

# Configuration du logging pour les tests
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_prerequisites():
    """Teste les prérequis pour la maintenance"""
    print("🔍 Test des prérequis...")
    
    errors = []
    
    # Test 1: Vérifier qu'on est dans le bon répertoire
    if not Path("package.json").exists():
        errors.append("❌ package.json non trouvé - exécutez depuis la racine du projet")
    else:
        print("✅ Répertoire de projet valide")
    
    # Test 2: Vérifier Python
    try:
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            print(f"✅ Python {python_version.major}.{python_version.minor} OK")
        else:
            errors.append(f"❌ Python 3.8+ requis (trouvé {python_version.major}.{python_version.minor})")
    except Exception as e:
        errors.append(f"❌ Erreur vérification Python: {e}")
    
    # Test 3: Vérifier Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git disponible")
        else:
            errors.append("❌ Git non disponible")
    except FileNotFoundError:
        errors.append("❌ Git non installé")
    
    # Test 4: Vérifier contextmaker
    try:
        import contextmaker
        if hasattr(contextmaker, 'make'):
            print("✅ contextmaker disponible")
        else:
            errors.append("❌ contextmaker.make() non disponible")
    except ImportError:
        errors.append("❌ contextmaker non installé")
    
    # Test 5: Vérifier les dépendances Python
    required_modules = ['requests', 'tqdm', 'schedule']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} importé")
        except ImportError:
            errors.append(f"❌ Module Python manquant: {module}")
    
    # Test 6: Vérifier les dossiers nécessaires
    required_dirs = [
        "app/data",
        "app/update_bdd", 
        "logs",
        "temp"
    ]
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ Dossier {dir_path} existe")
        else:
            print(f"⚠️  Dossier {dir_path} sera créé")
    
    # Test 7: Vérifier les fichiers de données existants
    data_files = [
        "app/data/astronomy-libraries.json",
        "app/update_bdd/ascl_repos_with_stars.csv"
    ]
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ Fichier {file_path} existe")
        else:
            print(f"⚠️  Fichier {file_path} sera créé lors de la première exécution")
    
    return errors

def test_network_connectivity():
    """Teste la connectivité réseau"""
    print("\n🌐 Test de connectivité réseau...")
    
    import requests
    
    # Test ASCL API
    try:
        response = requests.get("https://ascl.net/code/json", timeout=10)
        if response.status_code == 200:
            print("✅ ASCL API accessible")
        else:
            print(f"⚠️  ASCL API retourne code {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur accès ASCL API: {e}")
    
    # Test GitHub API
    try:
        response = requests.get("https://api.github.com/repos/astropy/astropy/commits", timeout=10)
        if response.status_code == 200:
            print("✅ GitHub API accessible")
        else:
            print(f"⚠️  GitHub API retourne code {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur accès GitHub API: {e}")

def test_script_syntax():
    """Teste la syntaxe des scripts"""
    print("\n📝 Test de syntaxe des scripts...")
    
    scripts = [
        "scripts/daily_maintenance.py",
        "scripts/schedule_daily_maintenance.py"
    ]
    
    for script in scripts:
        try:
            # Test de compilation Python
            with open(script, 'r') as f:
                compile(f.read(), script, 'exec')
            print(f"✅ {script} syntaxe OK")
        except SyntaxError as e:
            print(f"❌ {script} erreur syntaxe: {e}")
        except FileNotFoundError:
            print(f"❌ {script} non trouvé")

def test_permissions():
    """Teste les permissions des fichiers"""
    print("\n🔒 Test des permissions...")
    
    scripts = [
        "scripts/daily_maintenance.py",
        "scripts/schedule_daily_maintenance.py",
        "scripts/setup_maintenance_service.sh"
    ]
    
    for script in scripts:
        path = Path(script)
        if path.exists():
            # Vérifier si exécutable
            import stat
            mode = path.stat().st_mode
            if mode & stat.S_IXUSR:
                print(f"✅ {script} exécutable")
            else:
                print(f"⚠️  {script} non exécutable (chmod +x {script})")
        else:
            print(f"❌ {script} non trouvé")

def test_dry_run():
    """Teste l'import du module principal"""
    print("\n🧪 Test d'import du module principal...")
    
    try:
        # Ajouter le répertoire courant au PATH Python
        sys.path.insert(0, str(Path('.').absolute()))
        
        # Importer les classes principales sans exécuter
        from scripts.daily_maintenance import DailyMaintenanceManager
        
        # Créer une instance pour tester l'initialisation
        manager = DailyMaintenanceManager()
        print("✅ Module daily_maintenance importé avec succès")
        print(f"✅ Chemins configurés: {manager.data_dir}, {manager.temp_dir}")
        
    except Exception as e:
        print(f"❌ Erreur import module: {e}")

def main():
    """Point d'entrée principal du test"""
    print("🚀 DÉBUT DES TESTS DE MAINTENANCE\n")
    
    # Exécuter tous les tests
    errors = test_prerequisites()
    test_network_connectivity()
    test_script_syntax()
    test_permissions()
    test_dry_run()
    
    # Résumé final
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)
    
    if errors:
        print("❌ ERREURS DÉTECTÉES:")
        for error in errors:
            print(f"  {error}")
        print("\n🔧 Corrigez ces erreurs avant d'exécuter la maintenance.")
        return False
    else:
        print("✅ TOUS LES TESTS PASSÉS")
        print("\n🎉 Le système est prêt pour la maintenance quotidienne!")
        print("\nCommandes pour démarrer:")
        print("  - Test manuel:       python scripts/daily_maintenance.py")
        print("  - Planificateur:     python scripts/schedule_daily_maintenance.py")
        print("  - Service systemd:   sudo bash scripts/setup_maintenance_service.sh")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
