#!/usr/bin/env python3
"""
Script pour installer ou configurer contextmaker

Ce script tente d'installer contextmaker et configure un fallback 
vers mock_contextmaker si l'installation échoue.
"""

import subprocess
import sys
import os
from pathlib import Path

def try_install_contextmaker():
    """Tente d'installer contextmaker via pip"""
    print("🔄 Tentative d'installation de contextmaker...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "contextmaker"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ contextmaker installé avec succès")
            return True
        else:
            print(f"❌ Échec installation contextmaker: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def setup_mock_contextmaker():
    """Configure le mock contextmaker comme fallback"""
    print("🔧 Configuration du mock contextmaker...")
    
    try:
        # Créer un lien symbolique ou copier le script mock
        mock_script = Path("scripts/mock_contextmaker.py")
        
        if not mock_script.exists():
            print("❌ Script mock_contextmaker.py introuvable")
            return False
        
        # Rendre le script exécutable
        os.chmod(mock_script, 0o755)
        
        # Créer un wrapper contextmaker dans le PATH local
        wrapper_script = Path("contextmaker")
        with open(wrapper_script, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
import sys
import subprocess
script_path = "{mock_script.absolute()}"
subprocess.run([sys.executable, script_path] + sys.argv[1:])
""")
        
        os.chmod(wrapper_script, 0o755)
        
        print("✅ Mock contextmaker configuré")
        print("⚠️  Utilisation du mode mock - installez le vrai contextmaker pour la production")
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration mock: {e}")
        return False

def test_contextmaker():
    """Teste si contextmaker fonctionne"""
    print("🧪 Test de contextmaker...")
    
    try:
        result = subprocess.run(['contextmaker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ contextmaker fonctionne: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ contextmaker ne répond pas correctement")
            return False
            
    except FileNotFoundError:
        print("❌ Commande contextmaker introuvable")
        return False

def main():
    """Point d'entrée principal"""
    print("🚀 Installation/Configuration de contextmaker")
    print("=" * 50)
    
    # Vérifier si contextmaker est déjà installé et fonctionne
    if test_contextmaker():
        print("🎉 contextmaker est déjà disponible et fonctionne!")
        return True
    
    # Tentative d'installation via pip
    if try_install_contextmaker():
        if test_contextmaker():
            print("🎉 Installation réussie!")
            return True
    
    # Fallback vers mock
    print("\n🔄 Installation impossible, configuration du mode mock...")
    if setup_mock_contextmaker():
        if test_contextmaker():
            print("🎉 Mode mock configuré avec succès!")
            return True
    
    print("❌ Impossible de configurer contextmaker")
    print("\nOptions manuelles:")
    print("1. Installer contextmaker: pip install contextmaker")
    print("2. Utiliser le mock: python scripts/mock_contextmaker.py")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
