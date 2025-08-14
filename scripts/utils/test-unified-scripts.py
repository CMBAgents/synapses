#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les scripts unifiés fonctionnent
"""

import subprocess
import sys
from pathlib import Path

def test_script(script_name: str, args: list = None) -> bool:
    """Teste un script"""
    if args is None:
        args = []
    
    script_path = Path("scripts") / script_name
    
    if not script_path.exists():
        print(f"❌ Script non trouvé: {script_name}")
        return False
    
    try:
        print(f"🧪 Test de {script_name}...")
        result = subprocess.run(
            ["python3", str(script_path)] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {script_name} fonctionne")
            return True
        else:
            print(f"❌ {script_name} échoué: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_name} timeout")
        return False
    except Exception as e:
        print(f"❌ {script_name} erreur: {e}")
        return False

def main():
    """Tests principaux"""
    print("🧪 Tests des scripts unifiés")
    print("=" * 40)
    
    tests = [
        # Test du gestionnaire de contextes
        ("manage-contexts.py", ["--help"]),
        
        # Test de la maintenance (version rapide)
        ("maintenance.py", ["--help"]),
        
        # Test du déploiement (version help)
        ("deploy.py", ["--help"]),
        
        # Test du nettoyage
        ("cleanup-scripts.py", []),
    ]
    
    passed = 0
    total = len(tests)
    
    for script_name, args in tests:
        if test_script(script_name, args):
            passed += 1
        print()
    
    print("📊 Résumé des tests:")
    print(f"   - Tests réussis: {passed}/{total}")
    print(f"   - Taux de succès: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 Tous les tests sont passés!")
        return True
    else:
        print("❌ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
