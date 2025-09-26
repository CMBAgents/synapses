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
    """Normalise le nom de la bibliothèque vers le format strict {owner}-{repo}-context.txt"""
    # Séparer owner et repo
    if '/' not in library_name:
        return f"{library_name}-context.txt"
    
    owner, repo = library_name.split('/', 1)
    
    # Normaliser les caractères spéciaux
    owner_clean = owner.replace('_', '-').replace('.', '-')
    repo_clean = repo.replace('_', '-').replace('.', '-')
    
    return f"{owner_clean}-{repo_clean}-context.txt"

def find_context_file_for_library(library_name, context_files):
    """Trouve le fichier de contexte correspondant à une bibliothèque avec format strict"""
    
    # Format strict : {owner}-{repo}-context.txt
    expected_file = normalize_library_name(library_name)
    
    # Vérifier d'abord le format strict
    if expected_file in context_files:
        return expected_file
    
    # Fallback : chercher par similarité pour les anciens noms
    library_repo = library_name.split('/')[-1].lower()
    for context_file in context_files:
        context_name = context_file.replace('-context.txt', '').lower()
        if library_repo in context_name or context_name in library_repo:
            return context_file
    
    return None

def detect_duplicate_contexts(domain_data):
    """Détecte les contextes partagés ou en doublon"""
    duplicates = {}
    context_usage = {}
    
    for library in domain_data.get('libraries', []):
        context_file = library.get('contextFileName')
        if context_file:
            if context_file not in context_usage:
                context_usage[context_file] = []
            context_usage[context_file].append(library['name'])
    
    # Identifier les doublons
    for context_file, libraries in context_usage.items():
        if len(libraries) > 1:
            duplicates[context_file] = libraries
    
    return duplicates

def resolve_duplicates(duplicates, context_files):
    """Résout les doublons en créant des noms uniques"""
    resolutions = {}
    
    for context_file, libraries in duplicates.items():
        print(f"🔍 Doublon détecté: {context_file} utilisé par {libraries}")
        
        for library_name in libraries:
            # Générer le nom unique pour chaque bibliothèque
            unique_name = normalize_library_name(library_name)
            if unique_name != context_file:
                resolutions[library_name] = {
                    'old_context': context_file,
                    'new_context': unique_name,
                    'needs_rename': unique_name not in context_files
                }
                print(f"   📝 {library_name}: {context_file} → {unique_name}")
    
    return resolutions

def update_domain_json(domain):
    """Met à jour le JSON d'un domaine avec système de nommage unique strict"""
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
    
    # 1. Détecter les doublons
    duplicates = detect_duplicate_contexts(data)
    if duplicates:
        print(f"🔍 Doublons détectés dans {domain}:")
        for context_file, libraries in duplicates.items():
            print(f"   📄 {context_file}: {libraries}")
        
        # 2. Résoudre les doublons
        resolutions = resolve_duplicates(duplicates, context_files)
        
        # 3. Appliquer les résolutions
        for library_name, resolution in resolutions.items():
            # Trouver la bibliothèque dans les données
            for library in data.get('libraries', []):
                if library.get('name') == library_name:
                    library['contextFileName'] = resolution['new_context']
                    if resolution['needs_rename']:
                        print(f"   ⚠️ {library_name}: Fichier {resolution['old_context']} doit être renommé en {resolution['new_context']}")
                    break
    
    # 4. Mettre à jour chaque bibliothèque avec format strict
    updated_count = 0
    for library in data.get('libraries', []):
        library_name = library.get('name', '')
        if not library_name:
            continue
        
        # Générer le nom strict attendu
        expected_context = normalize_library_name(library_name)
        current_context = library.get('contextFileName', '')
        
        # Chercher le fichier de contexte correspondant (format strict ou ancien)
        context_file = find_context_file_for_library(library_name, context_files)
        
        if context_file:
            # Vérifier si le fichier doit être renommé
            if context_file != expected_context:
                # Renommer le fichier vers le format strict
                old_path = os.path.join(context_dir, context_file)
                new_path = os.path.join(context_dir, expected_context)
                
                if os.path.exists(old_path) and not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    print(f"📁 Renamed: {context_file} → {expected_context}")
                    # Mettre à jour la liste des fichiers
                    context_files.remove(context_file)
                    context_files.append(expected_context)
                elif os.path.exists(new_path):
                    # Le fichier avec le bon nom existe déjà, supprimer l'ancien
                    if os.path.exists(old_path):
                        os.remove(old_path)
                        print(f"🗑️ Removed duplicate: {context_file}")
            
            # Mettre à jour les métadonnées
            old_has_context = library.get('hasContextFile', False)
            old_context_file = library.get('contextFileName', '')
            
            library['hasContextFile'] = True
            library['contextFileName'] = expected_context
            
            if not old_has_context or old_context_file != expected_context:
                print(f"✅ {library_name}: {old_context_file or 'None'} → {expected_context}")
                updated_count += 1
        else:
            # Pas de fichier de contexte trouvé
            if library.get('hasContextFile', False):
                print(f"❌ {library_name}: No context file found for {expected_context}, removing hasContextFile")
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
