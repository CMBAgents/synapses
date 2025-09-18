#!/usr/bin/env python3
"""
Étape 2 CORRIGÉE: Mise à jour des étoiles + Détection des modifications GitHub
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from github import Github
import time
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('.env.local')

def update_stars_for_domain(domain_name: str, github_token: str = None):
    """Met à jour les étoiles pour un domaine spécifique"""
    print(f"🔄 Mise à jour des étoiles pour le domaine {domain_name}...")
    
    # Charger le fichier JSON du domaine
    json_path = Path(__file__).parent.parent.parent / "app" / "data" / f"{domain_name}-libraries.json"
    if not json_path.exists():
        print(f"⚠️ Fichier {json_path} non trouvé")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraire la liste des bibliothèques
    libraries = data.get('libraries', [])
    if not libraries:
        print(f"⚠️ Aucune bibliothèque trouvée pour {domain_name}")
        return False
    
    # Initialiser GitHub client
    if github_token:
        g = Github(github_token)
    else:
        g = Github()
    
    updated_count = 0
    error_count = 0
    
    for lib in libraries:
        try:
            # Vérifier que lib est un dictionnaire
            if not isinstance(lib, dict):
                print(f"   ⚠️ Élément inattendu dans {domain_name}: {type(lib)}")
                continue
                
            # Extraire le nom du repo depuis l'URL GitHub
            github_url = lib.get('github_url', '')
            if not github_url or 'github.com' not in github_url:
                continue
            
            # Extraire owner/repo de l'URL
            parts = github_url.replace('https://github.com/', '').split('/')
            if len(parts) < 2:
                continue
            
            repo_name = f"{parts[0]}/{parts[1]}"
            
            # Récupérer les informations du repo
            repo = g.get_repo(repo_name)
            new_stars = repo.stargazers_count
            
            # Mettre à jour si les étoiles ont changé
            if lib.get('stars', 0) != new_stars:
                old_stars = lib.get('stars', 0)
                lib['stars'] = new_stars
                updated_count += 1
                print(f"   📈 {repo_name}: {old_stars} → {new_stars} étoiles")
            
            # Respecter les limites de taux
            time.sleep(0.1)
            
        except Exception as e:
            error_count += 1
            print(f"   ❌ Erreur pour {lib.get('name', 'unknown')}: {e}")
            continue
    
    # Sauvegarder les modifications
    if updated_count > 0:
        # Mettre à jour la liste des bibliothèques dans les données
        data['libraries'] = libraries
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ {updated_count} bibliothèques mises à jour pour {domain_name}")
    
    if error_count > 0:
        print(f"⚠️ {error_count} erreurs lors de la mise à jour")
    
    return updated_count > 0

def detect_github_changes(github_token=None):
    """Détecte les modifications GitHub et marque les contextes obsolètes"""
    print("🔍 Détection des modifications GitHub...")
    
    try:
        import requests
        import json
        from datetime import datetime
        
        # Charger l'état des commits
        state_file = Path(__file__).parent.parent.parent / "context_manager_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {}
        
        # S'assurer que repo_commits existe
        if 'repo_commits' not in state:
            state['repo_commits'] = {}
        
        domains = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
        total_checked = 0
        total_updated = 0
        
        for domain in domains:
            domain_file = Path(__file__).parent.parent.parent / "app" / "data" / f"{domain}-libraries.json"
            if not domain_file.exists():
                continue
                
            with open(domain_file, 'r', encoding='utf-8') as f:
                domain_data = json.load(f)
            
            if 'libraries' not in domain_data:
                continue
                
            domain_updated = 0
            for library in domain_data['libraries']:
                total_checked += 1
                
                # Vérifier si le repo a changé
                if check_repo_has_changed(library, state, github_token):
                    # Marquer le contexte comme manquant
                    library['hasContextFile'] = False
                    library['contextFileName'] = None
                    domain_updated += 1
                    total_updated += 1
            
            # Sauvegarder les modifications du domaine (préserver les métadonnées)
            if domain_updated > 0:
                # Préserver les métadonnées existantes si elles existent
                if 'domain' not in domain_data:
                    domain_data['domain'] = domain
                if 'description' not in domain_data:
                    # Charger la description depuis config.json ou utiliser une par défaut
                    domain_data['description'] = f"Top {domain} libraries"
                if 'keywords' not in domain_data:
                    domain_data['keywords'] = []
                
                with open(domain_file, 'w', encoding='utf-8') as f:
                    json.dump(domain_data, f, indent=2, ensure_ascii=False)
                print(f"   📝 {domain}: {domain_updated} contextes marqués pour régénération")
        
        # Sauvegarder l'état
        state['last_check'] = datetime.now().isoformat()
        # print(f"🔍 Debug: Sauvegarde du state avec {len(state.get('repo_commits', {}))} commits stockés")
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"✅ State sauvegardé avec {len(state.get('repo_commits', {}))} commits")
        
        print(f"✅ {total_checked} repos vérifiés, {total_updated} contextes marqués pour régénération")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la détection GitHub: {e}")
        return False

def check_repo_has_changed(library, state, github_token=None):
    """Vérifie si un repository a changé depuis la dernière génération de contexte"""
    try:
        # Récupérer l'URL GitHub
        github_url = library.get('github_url', '')
        if not github_url:
            return False
        
        # Récupérer le dernier commit SHA
        latest_commit = get_github_latest_commit(github_url, github_token)
        if not latest_commit:
            return False
        
        # Vérifier si on a déjà stocké le commit pour cette librairie
        lib_name = library.get('name', '')
        stored_commit = state.get('repo_commits', {}).get(lib_name)
        
        # Toujours sauvegarder le commit actuel (pour référence future)
        if 'repo_commits' not in state:
            state['repo_commits'] = {}
        state['repo_commits'][lib_name] = latest_commit
        # print(f"🔍 Debug: Commit stocké pour {lib_name}: {latest_commit[:8]}...")
        
        # Vérifier s'il y a eu un changement
        if stored_commit is not None and stored_commit != latest_commit:
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️ Erreur vérification changement repo {library.get('name', '')}: {e}")
        return False

def get_github_latest_commit(repo_url, github_token=None):
    """Récupère le dernier commit SHA d'un repository GitHub"""
    try:
        import requests
        # Convertir l'URL GitHub en format API
        if "github.com" in repo_url:
            repo_path = repo_url.replace(".git", "").replace("https://github.com/", "")
            api_url = f"https://api.github.com/repos/{repo_path}/commits"
            
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'
            
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                commits = response.json()
                if commits and len(commits) > 0:
                    return commits[0]["sha"]
            else:
                print(f"⚠️ API GitHub error for {repo_url}: {response.status_code}")
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération commit GitHub {repo_url}: {e}")
        return None

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 2: Mise à jour des étoiles + Détection des modifications GitHub ===")
    
    try:
        # Récupérer le token GitHub
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            print("✅ Token GitHub détecté et configuré")
        else:
            print("⚠️ Aucun token GitHub, utilisation de l'API sans authentification")
            print("🔍 Variables d'environnement disponibles:")
            for key, value in os.environ.items():
                if 'GITHUB' in key.upper() or 'TOKEN' in key.upper():
                    print(f"   {key}: {'***' if len(value) > 8 else value}")
        
        # Domaines à mettre à jour
        domains = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
        
        total_updated = 0
        for domain in domains:
            if update_stars_for_domain(domain, github_token):
                total_updated += 1
        
        print(f"📊 {total_updated}/{len(domains)} domaines mis à jour")
        
        # Détecter les modifications GitHub
        detect_github_changes(github_token)
        
        print("✅ Étape 2 terminée")
        
    except Exception as e:
        print(f"❌ Erreur dans l'étape 2: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
