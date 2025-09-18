#!/usr/bin/env python3
"""
Étape 3: Correction des noms de fichiers de contexte
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 3: Correction des noms de contexte ===")
    
    try:
        # Utiliser le script de correction des noms
        script_path = Path(__file__).parent.parent / "fix-context-names.py"
        if not script_path.exists():
            print("⚠️ Script fix-context-names.py non trouvé, passage de l'étape")
            return
        
        print("Exécution du correcteur de noms de contexte...")
        result = subprocess.run(
            ["python3", str(script_path)], 
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True, 
            text=True, 
            check=True
        )
        print("✅ Correction des noms de contexte terminée")
        if result.stdout:
            print("📋 Résultats de la correction:")
            for line in result.stdout.strip().split('\n'):
                if line.strip() and ('✅' in line or '📝' in line):
                    print(f"   {line}")
        
        print("✅ Étape 3 terminée")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la correction des noms: {e.stderr}")
        # Ne pas faire échouer la maintenance pour cette étape
    except Exception as e:
        print(f"❌ Erreur dans l'étape 3: {e}")
        # Ne pas faire échouer la maintenance pour cette étape

if __name__ == "__main__":
    main()
