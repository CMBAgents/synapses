#!/usr/bin/env python3
"""
Étape 0: Vérification et installation des dépendances
"""

import subprocess
import sys
import logging

def check_contextmaker() -> bool:
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

def install_contextmaker():
    """Installe contextmaker via pip"""
    try:
        print("Installation/mise à jour de contextmaker via pip3...")
        result = subprocess.run(
            ["pip3", "install", "--upgrade", "contextmaker"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ contextmaker installé avec succès")
        else:
            print(f"❌ Échec de l'installation: {result.stderr}")
            raise Exception(f"Installation échouée: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors de l'installation de contextmaker")
        raise Exception("Timeout installation")
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        raise

def check_git() -> bool:
    """Vérifie si git est disponible"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 0: Vérification et installation des dépendances ===")
    
    try:
        # Vérifier et mettre à jour contextmaker
        if not check_contextmaker():
            print("Installation de contextmaker...")
            install_contextmaker()
        else:
            print("Mise à jour de contextmaker vers la dernière version...")
            install_contextmaker()
        
        # Vérifier git
        if not check_git():
            print("❌ Git n'est pas installé. Veuillez l'installer manuellement.")
            sys.exit(1)
        
        print("✅ Étape 0 terminée: toutes les dépendances sont disponibles")
        
    except Exception as e:
        print(f"❌ Erreur dans l'étape 0: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
