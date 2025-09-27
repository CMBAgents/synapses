#!/usr/bin/env python3
"""
Étape 4 CORRIGÉE: Génération des contextes manquants UNIQUEMENT
"""

import subprocess
import sys
import json
import os
from pathlib import Path

def generate_missing_contexts():
    """Génère les contextes manquants pour toutes les bibliothèques"""
    print("🔄 Génération des contextes manquants...")
    
    try:
        import json
        import shutil
        from pathlib import Path
        
        # Charger les données existantes
        existing_contexts = get_existing_contexts()
        libraries_data = load_libraries_data()
        
        print(f"📚 Contextes existants: {existing_contexts}")
        print(f"📚 Bibliothèques trouvées: {list(libraries_data.keys())}")
        
        total_generated = 0
        
        for domain, libraries in libraries_data.items():
            print(f"🔄 Traitement du domaine: {domain}")
            
            existing_libs = existing_contexts.get(domain, [])
            
            for lib in libraries:
                github_url = lib.get('github_url', '')
                
                # Utiliser les métadonnées existantes au lieu de reconstruire
                if not github_url or lib.get('hasContextFile', False):
                    continue
                
                # Utiliser le nom de fichier existant ou construire un nom par défaut
                context_file_name = lib.get('contextFileName')
                if context_file_name:
                    # Vérifier si le fichier existe déjà
                    context_path = Path(__file__).parent.parent.parent / "public" / "context" / domain / context_file_name
                    if context_path.exists():
                        continue
                else:
                    # Fallback : construire le nom si pas de métadonnée
                    lib_name = lib.get('name', '').split('/')[-1]
                    context_file_name = f"{lib_name}-context.txt"
                    context_path = Path(__file__).parent.parent.parent / "public" / "context" / domain / context_file_name
                    if context_path.exists():
                        continue
                
                # Extraire le nom du repository (après le dernier /)
                lib_name = lib.get('name', '').split('/')[-1]
                print(f"🔄 Génération du contexte pour {lib.get('name', lib_name)}...")
                
                # Cloner le repository
                repo_dir = Path(__file__).parent.parent.parent / "temp" / "repos" / lib_name
                if repo_dir.exists():
                    shutil.rmtree(repo_dir)
                
                repo_dir.mkdir(parents=True, exist_ok=True)
                
                # Cloner le repo
                clone_result = subprocess.run([
                    'git', 'clone', '--depth', '1', github_url, str(repo_dir)
                ], capture_output=True, text=True, timeout=300)
                
                if clone_result.returncode != 0:
                    print(f"❌ Erreur clonage {lib_name}: {clone_result.stderr}")
                    continue
                
                # Générer le contexte avec contextmaker via Python (fonctionne partout)
                try:
                    # Générer dans temp/contexts/ d'abord
                    temp_contexts_dir = Path(__file__).parent.parent.parent / "temp" / "contexts"
                    temp_contexts_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Utiliser contextmaker en ligne de commande (comme pour skyfield)
                    result = subprocess.run([
                        'contextmaker', lib_name, 
                        '--output', str(temp_contexts_dir),
                        '--input_path', str(repo_dir),
                        '--rough'
                    ], capture_output=True, text=True, timeout=300, 
                    env={**os.environ, 'PATH': '/Library/Frameworks/Python.framework/Versions/3.12/bin:' + os.environ.get('PATH', '')})
                    
                    # Chercher le fichier généré dans temp/contexts/
                    generated_file = temp_contexts_dir / f"{lib_name}.txt"
                    
                    if result.returncode == 0 and generated_file.exists():
                        # Copier le fichier vers le domaine final
                        generated_file.rename(context_path)
                        success = True
                    else:
                        success = False
                        print(f"❌ Échec contextmaker pour {lib_name}: {result.stderr}")
                    
                    if success and context_path.exists():
                        # Mettre à jour les métadonnées
                        lib['hasContextFile'] = True
                        lib['contextFileName'] = context_file_name
                        
                        total_generated += 1
                        print(f"✅ Contexte généré pour {lib_name}")
                    else:
                        print(f"❌ Échec génération contexte pour {lib_name}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print(f"❌ Timeout contextmaker pour {lib_name}")
                except Exception as e:
                    print(f"❌ Erreur contextmaker pour {lib_name}: {e}")
                
                # Nettoyer le repo temporaire
                if repo_dir.exists():
                    shutil.rmtree(repo_dir)
        
        # Sauvegarder les métadonnées mises à jour (préserver domain, description, keywords)
        for domain, libraries in libraries_data.items():
            domain_file = Path(__file__).parent.parent.parent / "app" / "data" / f"{domain}-libraries.json"
            
            # Charger les métadonnées existantes
            existing_data = {}
            if domain_file.exists():
                with open(domain_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Préserver les métadonnées existantes
            updated_data = {
                "libraries": libraries,
                "domain": existing_data.get("domain", domain),
                "description": existing_data.get("description", f"Top {domain} libraries"),
                "keywords": existing_data.get("keywords", [])
            }
            
            with open(domain_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {total_generated} contextes générés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des contextes: {e}")
        return False

def get_existing_contexts():
    """Récupère la liste des contextes existants"""
    existing = {}
    context_dir = Path(__file__).parent.parent.parent / "public" / "context"
    
    for domain_dir in context_dir.iterdir():
        if domain_dir.is_dir():
            domain = domain_dir.name
            existing[domain] = []
            for context_file in domain_dir.glob("*-context.txt"):
                lib_name = context_file.stem.replace("-context", "")
                existing[domain].append(lib_name)
    
    return existing

def load_libraries_data():
    """Charge les données de toutes les bibliothèques"""
    libraries_data = {}
    data_dir = Path(__file__).parent.parent.parent / "app" / "data"
    
    for domain in ['astronomy', 'biochemistry', 'finance', 'machinelearning']:
        domain_file = data_dir / f"{domain}-libraries.json"
        if domain_file.exists():
            with open(domain_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'libraries' in data:
                    libraries_data[domain] = data['libraries']
    
    return libraries_data

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 4: Génération des contextes manquants ===")
    
    try:
        if generate_missing_contexts():
            print("✅ Étape 4 terminée")
        else:
            print("❌ Étape 4 échouée")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erreur dans l'étape 4: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
