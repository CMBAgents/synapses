#!/usr/bin/env python3
"""
Script de test pour générer le contexte de pixell
en utilisant la nouvelle structure contextmaker.make()
"""

import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path

def clone_pixell_repo():
    """Clone le repository pixell dans un dossier temporaire"""
    print("🔄 Clonage du repository pixell...")
    
    # Créer un dossier temporaire pour le clone
    temp_dir = Path("temp/repos/pixell")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Si le dossier existe déjà, le supprimer pour un clone frais
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Cloner le repository
    repo_url = "https://github.com/simonsobs/pixell.git"
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(temp_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ Repository cloné avec succès dans {temp_dir}")
            return temp_dir
        else:
            print(f"❌ Erreur lors du clonage: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors du clonage")
        return None
    except Exception as e:
        print(f"❌ Exception lors du clonage: {e}")
        return None

def generate_pixell_context(repo_dir):
    """Génère le contexte de pixell avec contextmaker.make()"""
    print("🔄 Génération du contexte avec contextmaker.make()...")
    
    # Créer le dossier de sortie
    output_dir = Path("public/context/astronomy")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Définir le chemin de sortie
    output_file = output_dir / "pixell-context.txt"
    
    try:
        # Importer contextmaker
        import contextmaker
        
        print(f"📋 Paramètres contextmaker.make():")
        print(f"  - library_name: pixell")
        print(f"  - output_path: {output_file}")
        print(f"  - input_path: {repo_dir}")
        print(f"  - rough: True")
        
        # Appeler contextmaker.make() avec la nouvelle structure
        result = contextmaker.make(
            library_name="pixell",
            output_path=str(output_file),
            input_path=str(repo_dir),
            rough=True,
        )
        
        print(f"📊 Résultat contextmaker: {result}")
        
        # Vérifier que le fichier a été créé
        if result and output_file.exists():
            print(f"✅ Contexte généré avec succès: {output_file}")
            
            # Lire et afficher les premières lignes
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 Taille du fichier: {len(content)} caractères")
            print("📄 Premières lignes:")
            print("=" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("=" * 50)
            
            return True
        else:
            print(f"❌ Fichier de contexte non trouvé: {output_file}")
            return False
            
    except ImportError:
        print("❌ contextmaker n'est pas installé")
        print("   Installez-le avec: pip install contextmaker")
        return False
    except Exception as e:
        print(f"❌ Exception lors de la génération: {e}")
        return False

def cleanup_temp_repo(repo_dir):
    """Nettoie le repository temporaire"""
    try:
        shutil.rmtree(repo_dir)
        print(f"🧹 Repository temporaire supprimé: {repo_dir}")
    except Exception as e:
        print(f"⚠️  Impossible de supprimer le repository temporaire: {e}")

def main():
    """Point d'entrée principal"""
    print("🚀 Test de génération de contexte pour pixell")
    print("=" * 60)
    
    # Étape 1: Cloner le repository
    repo_dir = clone_pixell_repo()
    if not repo_dir:
        print("❌ Impossible de cloner le repository")
        return 1
    
    try:
        # Étape 2: Générer le contexte
        success = generate_pixell_context(repo_dir)
        
        if success:
            print("🎉 Contexte de pixell généré avec succès!")
            print(f"📁 Fichier créé: public/context/astronomy/pixell-context.txt")
        else:
            print("💥 Échec de la génération du contexte")
            return 1
            
    finally:
        # Étape 3: Nettoyer le repository temporaire
        cleanup_temp_repo(repo_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
