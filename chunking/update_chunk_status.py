#!/usr/bin/env python3
"""
Script pour mettre à jour les fichiers JSON avec le statut de chunking
Ajoute un champ "chunked": true/false et "lastChunked": timestamp
"""

import json
from pathlib import Path
from datetime import datetime

# Chemins
project_root = Path(__file__).parent.parent
data_dir = project_root / "app" / "data"
chroma_dir = project_root / "chroma_db"
registry_file = chroma_dir / "chunk_registry.json"

print(" Mise à jour du statut de chunking dans les JSON")
print("=" * 60)

# Charger le registre des chunks
if not registry_file.exists():
    print(f" Registre non trouvé: {registry_file}")
    print("   Exécutez d'abord: python maintenance/steps/step7_reindex_rag.py")
    exit(1)

with open(registry_file, 'r') as f:
    registry = json.load(f)

print(f" Registre chargé: {len(registry['files'])} fichiers indexés")
print()

# Traiter chaque domaine
domains = ["astronomy", "biochemistry", "finance", "machinelearning"]
total_updated = 0

for domain in domains:
    json_file = data_dir / f"{domain}-libraries.json"
    
    if not json_file.exists():
        print(f"  Fichier non trouvé: {json_file.name}")
        continue
    
    # Charger le JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    libraries = data.get("libraries", [])
    updated_count = 0
    
    print(f" {domain.upper()}: {len(libraries)} bibliothèques")
    
    # Mettre à jour chaque bibliothèque
    for lib in libraries:
        context_file = lib.get("contextFileName", "")
        if not context_file:
            continue
        
        # Extraire le nom de la bibliothèque du fichier
        library_name = context_file.replace("-context.txt", "")
        file_key = f"{domain}/{library_name}"
        
        # Vérifier dans le registre
        if file_key in registry["files"]:
            chunk_info = registry["files"][file_key]
            lib["chunked"] = True
            lib["lastChunked"] = chunk_info.get("indexed_at", "unknown")
            lib["chunkCount"] = chunk_info.get("chunks", 0)
            lib["contextHash"] = chunk_info.get("hash", "")
            updated_count += 1
        else:
            lib["chunked"] = False
            lib["lastChunked"] = None
            lib["chunkCount"] = 0
            lib["contextHash"] = ""
    
    # Sauvegarder le JSON mis à jour
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    {updated_count} bibliothèques marquées comme 'chunked'")
    total_updated += updated_count

print()
print("=" * 60)
print(f" Total mis à jour: {total_updated} bibliothèques")
print("=" * 60)

