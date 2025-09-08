#!/usr/bin/env python3
"""
Script pour corriger les noms de fichiers de contexte dans les JSON
et s'assurer que la correspondance entre les noms de bibliothèques
et les fichiers de contexte est correcte.
"""

import os
import json
import re
from pathlib import Path

def normalize_library_name(library_name):
    """Normalise le nom de la bibliothèque pour correspondre au fichier de contexte"""
    # Remplacer les caractères spéciaux par des tirets
    normalized = library_name.replace('/', '-').replace('_', '-').replace('.', '-')
    return f"{normalized}-context.txt"

def find_context_file_for_library(library_name, context_files):
    """Trouve le fichier de contexte correspondant à une bibliothèque"""
    
    # Cas spéciaux de correspondance
    special_mappings = {
        "mperrin/poppy": "spacetelescope-poppy-context.txt",
        "trasal/frbpoppy": "trasal-frbpoppy-context.txt",
        "rbvi/ChimeraX": "rbvi-ChimeraX-context.txt",
        "schrodinger/pymol-open-source": "schrodinger-pymol-open-source-context.txt",
    }
    
    # Vérifier d'abord les correspondances spéciales
    if library_name in special_mappings:
        expected_file = special_mappings[library_name]
        if expected_file in context_files:
            return expected_file
    
    # Essayer plusieurs patterns de correspondance
    patterns = [
        # Pattern exact avec tirets
        normalize_library_name(library_name),
        # Pattern avec seulement le nom du repo
        f"{library_name.split('/')[-1]}-context.txt",
        # Pattern avec remplacement des underscores
        f"{library_name.replace('/', '-').replace('_', '-')}-context.txt",
        # Pattern avec remplacement des points
        f"{library_name.replace('/', '-').replace('.', '-')}-context.txt",
        # Pattern simplifié (juste le nom du repo)
        f"{library_name.split('/')[-1].replace('_', '-')}-context.txt",
    ]
    
    # Chercher le fichier correspondant
    for pattern in patterns:
        if pattern in context_files:
            return pattern
    
    # Si aucun pattern ne correspond, chercher par similarité
    library_repo = library_name.split('/')[-1].lower()
    for context_file in context_files:
        context_name = context_file.replace('-context.txt', '').lower()
        if library_repo in context_name or context_name in library_repo:
            return context_file
    
    return None

def update_domain_json(domain):
    """Met à jour le JSON d'un domaine"""
    json_path = f"app/data/{domain}-libraries.json"
    context_dir = f"public/context/{domain}"
    
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return False
    
    if not os.path.exists(context_dir):
        print(f"❌ Context directory not found: {context_dir}")
        return False
    
    # Lire le JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Lister les fichiers de contexte existants
    context_files = []
    for file in os.listdir(context_dir):
        if file.endswith('.txt'):
            context_files.append(file)
    
    print(f"📁 Found {len(context_files)} context files in {context_dir}")
    
    # Mettre à jour chaque bibliothèque
    updated_count = 0
    for library in data.get('libraries', []):
        library_name = library.get('name', '')
        if not library_name:
            continue
        
        # Trouver le fichier de contexte correspondant
        context_file = find_context_file_for_library(library_name, context_files)
        
        if context_file:
            # Mettre à jour les métadonnées
            old_has_context = library.get('hasContextFile', False)
            old_context_file = library.get('contextFileName', '')
            
            library['hasContextFile'] = True
            library['contextFileName'] = context_file
            
            if not old_has_context or old_context_file != context_file:
                print(f"✅ {library_name}: {old_context_file or 'None'} → {context_file}")
                updated_count += 1
        else:
            # Pas de fichier de contexte trouvé
            if library.get('hasContextFile', False):
                print(f"❌ {library_name}: No context file found, removing hasContextFile")
                library['hasContextFile'] = False
                if 'contextFileName' in library:
                    del library['contextFileName']
                updated_count += 1
    
    # Sauvegarder le JSON mis à jour
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"📝 Updated {updated_count} libraries in {domain}")
    return True

def main():
    """Fonction principale"""
    print("🔧 Correction des noms de fichiers de contexte...")
    
    domains = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
    
    for domain in domains:
        print(f"\n📋 Processing domain: {domain}")
        update_domain_json(domain)
    
    print("\n✅ Correction terminée!")

if __name__ == "__main__":
    main()
