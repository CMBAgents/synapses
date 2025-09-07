#!/usr/bin/env python3
import json
import re
import os

def create_program_id(name):
    """Créer un ID de programme à partir du nom"""
    return re.sub(r'[^a-z0-9]', '-', name.lower()).replace('-+', '-').strip('-')

def create_program_from_library(library, domain):
    """Créer un programme à partir d'une bibliothèque"""
    program_id = create_program_id(library['name'])
    
    return {
        "id": program_id,
        "name": library['name'].split('/')[-1],  # Prendre seulement la dernière partie du nom
        "description": f"{library['name']} - {'Astrophysics' if domain == 'astronomy' else domain.title()} library with {library['stars']} stars",
        "contextFiles": [],
        "combinedContextFile": f"/api/context/{domain}/{library['contextFileName']}" if library.get('hasContextFile') else None,
        "docsUrl": library['github_url'],
        "extraSystemPrompt": f"You are an expert on {library['name']}. Use the provided documentation to help users with this {'astrophysics' if domain == 'astronomy' else domain} library."
    }

def main():
    # Charger les données des bibliothèques
    with open('app/data/astronomy-libraries.json', 'r') as f:
        astronomy_data = json.load(f)
    
    with open('app/data/finance-libraries.json', 'r') as f:
        finance_data = json.load(f)
    
    with open('app/data/biochemistry-libraries.json', 'r') as f:
        biochemistry_data = json.load(f)
    
    with open('app/data/machinelearning-libraries.json', 'r') as f:
        machinelearning_data = json.load(f)
    
    # Créer les programmes pour l'astrophysique
    astronomy_programs = [create_program_from_library(lib, 'astronomy') 
                         for lib in astronomy_data['libraries']]
    
    # Créer les programmes pour la finance
    finance_programs = [create_program_from_library(lib, 'finance') 
                       for lib in finance_data['libraries']]
    
    # Créer les programmes pour la biochimie
    biochemistry_programs = [create_program_from_library(lib, 'biochemistry') 
                            for lib in biochemistry_data['libraries']]
    
    # Créer les programmes pour le machine learning
    machinelearning_programs = [create_program_from_library(lib, 'machinelearning') 
                               for lib in machinelearning_data['libraries']]
    
    # Combiner tous les programmes
    all_programs = astronomy_programs + finance_programs + biochemistry_programs + machinelearning_programs
    
    # Charger la configuration existante
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Préserver la section domains si elle existe
    domains_section = config.get('domains', {})
    
    # Remplacer les programmes existants
    config['programs'] = all_programs
    
    # Pas de programme par défaut
    config['defaultProgram'] = ""
    
    # Restaurer la section domains si elle existait
    if domains_section:
        config['domains'] = domains_section
    
    # Sauvegarder la nouvelle configuration
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Généré {len(all_programs)} programmes:")
    print(f"   - Astronomy: {len(astronomy_programs)} programmes")
    print(f"   - Finance: {len(finance_programs)} programmes")
    print(f"   - Biochemistry: {len(biochemistry_programs)} programmes")
    print(f"   - Machine Learning: {len(machinelearning_programs)} programmes")
    print(f"   - Programme par défaut: Aucun")
    print(f"\n📁 Configuration sauvegardée dans: config.json")

if __name__ == "__main__":
    main() 