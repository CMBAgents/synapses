#!/usr/bin/env python3
"""
Étape 1: Mise à jour de tous les domaines
"""

import subprocess
import sys
import os
from pathlib import Path

# Charger les variables d'environnement depuis .env.local
def load_env_file():
    """Charge les variables d'environnement depuis .env.local"""
    env_file = Path(__file__).parent.parent.parent / '.env.local'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Charger les variables d'environnement
load_env_file()

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 1: Mise à jour de tous les domaines ===")
    
    try:
        # Utiliser le système unifié
        script_path = Path(__file__).parent.parent / "unified-domain-updater.py"
        if not script_path.exists():
            print(f"❌ Script unifié non trouvé: {script_path}")
            sys.exit(1)
        
        print("🔄 Exécution du système unifié de mise à jour des domaines...")
        
        # Vérifier si un token GitHub est disponible
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            print("✅ Token GitHub détecté, utilisation de l'API avec authentification")
            result = subprocess.run(
                ["python3", str(script_path), "--maintenance", "--token", github_token],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
        else:
            print("⚠️ Aucun token GitHub détecté, utilisation de l'API sans authentification (limite: 60 req/h)")
            result = subprocess.run(
                ["python3", str(script_path), "--maintenance"],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
        
        if result.returncode == 0:
            print("✅ Étape 1 terminée: tous les domaines mis à jour")
            if result.stdout:
                print("📋 Résultats de la mise à jour:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip() and ('✅' in line or '❌' in line or 'Mis à jour' in line):
                        print(f"   {line}")
        else:
            print(f"❌ Erreur lors de la mise à jour: {result.stderr}")
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors de la mise à jour des domaines")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur dans l'étape 1: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
