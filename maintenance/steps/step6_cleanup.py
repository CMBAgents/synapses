#!/usr/bin/env python3
"""
Étape 6: Nettoyage
"""

import shutil
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_temp_repos():
    """Nettoie les repositories temporaires"""
    temp_dir = Path(__file__).parent.parent.parent / "temp" / "repos"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Repositories temporaires nettoyés")

def cleanup_old_logs():
    """Nettoie les anciens logs (garder seulement 7 jours)"""
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    if not logs_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=7)
    cleaned_count = 0
    
    for log_file in logs_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_date.timestamp():
            try:
                log_file.unlink()
                cleaned_count += 1
            except Exception as e:
                print(f"⚠️ Erreur suppression {log_file.name}: {e}")
    
    if cleaned_count > 0:
        print(f"✅ {cleaned_count} anciens logs supprimés")
    else:
        print("✅ Aucun ancien log à nettoyer")

def cleanup_orphaned_contexts():
    """Nettoie les fichiers de contexte orphelins (qui ne correspondent plus à des bibliothèques)"""
    print("🔄 Recherche des contextes orphelins...")
    
    base_path = Path(__file__).parent.parent.parent
    context_dir = base_path / "public" / "context"
    data_dir = base_path / "app" / "data"
    
    if not context_dir.exists():
        print("✅ Aucun dossier context trouvé")
        return
    
    total_orphaned = 0
    
    # Parcourir tous les domaines
    for domain_dir in context_dir.iterdir():
        if not domain_dir.is_dir():
            continue
            
        domain = domain_dir.name
        print(f"🔄 Vérification du domaine: {domain}")
        
        # Charger les bibliothèques du domaine
        domain_file = data_dir / f"{domain}-libraries.json"
        if not domain_file.exists():
            print(f"⚠️ Fichier {domain}-libraries.json non trouvé, suppression de tous les contextes")
            # Supprimer tous les contextes du domaine
            for context_file in domain_dir.glob("*.txt"):
                try:
                    context_file.unlink()
                    total_orphaned += 1
                    print(f"🗑️ Supprimé: {context_file.name}")
                except Exception as e:
                    print(f"❌ Erreur suppression {context_file.name}: {e}")
            continue
        
        # Charger les données du domaine
        try:
            with open(domain_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                libraries = data.get('libraries', [])
        except Exception as e:
            print(f"❌ Erreur lecture {domain_file}: {e}")
            continue
        
        # Créer la liste des contextes attendus
        expected_contexts = set()
        for lib in libraries:
            # Générer les noms de fichiers possibles (même logique que dans l'API)
            patterns = [
                f"{lib['name'].replace('/', '-').replace('_', '-')}-context.txt",
                f"{lib['name'].split('/')[-1]}-context.txt",
                f"{lib['name'].split('/')[-1].replace('-', '-')}-context.txt",
                f"{lib['name'].split('/')[-1].split('-')[-1]}-context.txt",
                f"{lib['name'].split('/')[-1].split('-')[-1]}-context.txt",
                f"{lib['name'].replace('/', '-').replace('_', '-')}-context.txt",
                f"{lib['name'].replace('/', '-').replace('_', '-')}-context.txt",
                f"{lib['name'].split('/')[-1]}.txt",
                f"{lib['name'].split('/')[-1]}.txt",
                f"{lib['name'].split('/')[-1]}.txt",
                f"{lib['name'].replace('/', '-').replace('.', '-')}-context.txt"
            ]
            expected_contexts.update(patterns)
        
        # Trouver les contextes orphelins
        orphaned_count = 0
        for context_file in domain_dir.glob("*.txt"):
            if context_file.name not in expected_contexts:
                try:
                    context_file.unlink()
                    orphaned_count += 1
                    total_orphaned += 1
                    print(f"🗑️ Orphelin supprimé: {context_file.name}")
                except Exception as e:
                    print(f"❌ Erreur suppression {context_file.name}: {e}")
        
        if orphaned_count > 0:
            print(f"✅ {orphaned_count} contextes orphelins supprimés pour {domain}")
        else:
            print(f"✅ Aucun contexte orphelin pour {domain}")
    
    if total_orphaned > 0:
        print(f"✅ Total: {total_orphaned} contextes orphelins supprimés")
    else:
        print("✅ Aucun contexte orphelin trouvé")

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 6: Nettoyage ===")
    
    try:
        # Nettoyer les repositories temporaires
        cleanup_temp_repos()
        
        # Nettoyer les logs anciens
        cleanup_old_logs()
        
        # Nettoyer les contextes orphelins
        cleanup_orphaned_contexts()
        
        print("✅ Étape 6 terminée")
        
    except Exception as e:
        print(f"❌ Erreur dans l'étape 6: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
