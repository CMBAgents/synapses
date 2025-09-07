#!/usr/bin/env python3
"""
Script unifié pour la gestion complète des contextes
Remplace: generate-missing-contexts.py, generate-contexts-with-clone.py, 
         update-json-status.py, verify-context-structure.py, cleanup-duplicate-contexts.py,
         et les fonctionnalités de manage-contexts.py

Fonctionnalités unifiées:
1. ✅ Vérification de la structure des contextes
2. ✅ Génération des contextes manquants avec clonage Git
3. ✅ Nettoyage des doublons (racine et avancé)
4. ✅ Mise à jour des statuts JSON
5. ✅ Génération du module embedded-context.ts
6. ✅ Régénération de config.json
7. ✅ Gestion des hashes et détection des changements
"""

import os
import sys
import json
import csv
import hashlib
import subprocess
import tempfile
import shutil
import logging
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

class UnifiedContextManager:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "app" / "data"
        self.context_dir = self.base_dir / "public" / "context"
        self.app_context_dir = self.base_dir / "app" / "context"
        self.config_file = self.base_dir / "config.json"
        self.state_file = self.base_dir / "context_manager_state.json"
        self.temp_dir = self.base_dir / "temp" / "repos"
        
        # Créer les dossiers nécessaires
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Load state
        self.state = self.load_state()
        
        # Configuration des domaines - chargée depuis domain-config.json
        self.domains = self.load_domains_config()
        
    def setup_logging(self):
        """Configure le logging"""
        # Créer le dossier logs s'il n'existe pas
        logs_dir = self.base_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        # Effacer le fichier de log précédent pour éviter l'accumulation
        log_file = logs_dir / 'unified_context_manager.log'
        if log_file.exists():
            log_file.unlink()
            print(f"🧹 Fichier de log précédent effacé: {log_file}")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_file)),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_state(self) -> Dict:
        """Charge l'état précédent"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "last_check": None,
            "context_hashes": {},
            "last_update": None,
            "update_count": 0
        }
    
    def save_state(self):
        """Sauvegarde l'état actuel"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde état: {e}")
    
    def load_domains_config(self) -> List[str]:
        """Charge la configuration des domaines depuis config.json"""
        try:
            config_file = self.base_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    domains = config.get('domains', {}).get('supported', [])
                    self.logger.info(f"Domaines chargés depuis config.json: {domains}")
                    return domains
            else:
                self.logger.warning("Fichier config.json non trouvé, utilisation des domaines par défaut")
                return ["astronomy", "finance", "biochemistry", "machinelearning"]
        except Exception as e:
            self.logger.error(f"Erreur chargement configuration domaines: {e}")
            return ["astronomy", "finance", "biochemistry", "machinelearning"]
    
    def get_file_hash(self, filepath: Path) -> str:
        """Calcule le hash MD5 d'un fichier"""
        if not filepath.exists():
            return ""
        
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Erreur calcul hash {filepath}: {e}")
            return ""

    # ============================================================================
    # 1. VÉRIFICATION DE LA STRUCTURE DES CONTEXTES
    # ============================================================================
    
    def verify_context_structure(self) -> bool:
        """Vérifie que les fichiers de contexte sont dans la bonne structure"""
        self.logger.info("🔍 Vérification de la structure des contextes...")
        
        if not self.context_dir.exists():
            self.logger.error("public/context directory does not exist")
            return False
        
        # Vérifier les fichiers de contexte à la racine (ne doivent pas exister)
        root_context_files = []
        for file in self.context_dir.iterdir():
            if file.is_file() and file.name.endswith('-context.txt'):
                root_context_files.append(file.name)
        
        if root_context_files:
            self.logger.error(f"❌ Found {len(root_context_files)} context files in public/context root (should not exist):")
            for file in root_context_files:
                self.logger.error(f"  - {file}")
            return False
        
        # Vérifier les sous-répertoires de domaines
        total_contexts = 0
        
        for domain in self.domains:
            domain_dir = self.context_dir / domain
            if not domain_dir.exists():
                self.logger.warning(f"Domain directory {domain}/ does not exist")
                continue
                
            self.logger.info(f"Checking domain: {domain}")
            
            # Compter les fichiers de contexte dans le répertoire de domaine
            domain_files = []
            for file in domain_dir.iterdir():
                if file.is_file() and file.name.endswith('-context.txt'):
                    domain_files.append(file.name)
            
            self.logger.info(f"  Found {len(domain_files)} context files in {domain}/")
            total_contexts += len(domain_files)
        
        self.logger.info(f"✅ Structure verification completed. Total contexts: {total_contexts}")
        return True

    # ============================================================================
    # 2. GÉNÉRATION DES CONTEXTES MANQUANTS
    # ============================================================================
    
    def check_contextmaker_available(self) -> bool:
        """Vérifie si contextmaker est disponible"""
        try:
            import contextmaker
            # Vérifier la version et forcer la mise à jour si nécessaire
            import subprocess
            try:
                result = subprocess.run(
                    ["pip3", "install", "--upgrade", "contextmaker"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    self.logger.info("✅ contextmaker mis à jour vers la dernière version")
                else:
                    self.logger.warning(f"⚠️ Mise à jour de contextmaker échouée: {result.stderr}")
            except Exception as e:
                self.logger.warning(f"⚠️ Impossible de mettre à jour contextmaker: {e}")
            
            return True
        except ImportError:
            return False
    
    def check_git_available(self) -> bool:
        """Vérifie si git est disponible"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def clone_repository(self, owner: str, repo: str, package_name: str) -> bool:
        """Clone un repository GitHub"""
        try:
            repo_url = f"https://github.com/{owner}/{repo}.git"
            repo_dir = self.temp_dir / package_name
            
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            
            self.logger.info(f"🔄 Cloning {repo_url}...")
            
            result = subprocess.run([
                'git', 'clone', '--depth', '1', repo_url, str(repo_dir)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Successfully cloned {repo_url}")
                return True
            else:
                self.logger.error(f"❌ Failed to clone {repo_url}")
                self.logger.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ Timeout cloning {repo_url}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Exception cloning {repo_url}: {e}")
            return False
    
    def generate_context_with_contextmaker(self, package_name: str, lib_name: str, domain: str) -> Optional[str]:
        """Génère le contenu du contexte avec contextmaker"""
        try:
            repo_dir = self.temp_dir / package_name
            if not repo_dir.exists():
                self.logger.error(f"Repository directory not found: {repo_dir}")
                return None
            
            # Utiliser contextmaker.make() directement
            import contextmaker
            
            self.logger.info(f"🔄 Running contextmaker for {package_name}...")
            
            result = contextmaker.make(
                library_name=package_name,
                output_path=str(repo_dir),
                input_path=str(repo_dir),
                rough=True,
                extension='txt'
            )
            
            if result:
                # Le fichier généré sera nommé {package_name}.txt
                generated_file = repo_dir / f"{package_name}.txt"
                if generated_file.exists():
                    # Lire le contenu généré
                    with open(generated_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Nettoyer le fichier temporaire
                    generated_file.unlink()
                else:
                    self.logger.error(f"Generated file not found: {generated_file}")
                    return None
                
                self.logger.info(f"✅ Context file generated for {package_name}")
                return content
            else:
                self.logger.error(f"❌ Context file not created for {package_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Exception running contextmaker for {package_name}: {e}")
            return None
    
    def save_context_file(self, domain: str, lib_name: str, content: str) -> bool:
        """Sauvegarde le fichier de contexte"""
        try:
            domain_dir = self.context_dir / domain
            domain_dir.mkdir(parents=True, exist_ok=True)
            
            # Normaliser le nom de la bibliothèque
            normalized_name = lib_name.replace('/', '-').replace('_', '-')
            filename = f"{normalized_name}-context.txt"
            filepath = domain_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"✅ Context file saved: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saving context file: {e}")
            return False
    
    def get_existing_contexts(self) -> Dict[str, List[str]]:
        """Obtient la liste des contextes existants par domaine"""
        existing_contexts = {}
        
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                existing_contexts[domain] = []
                
                for context_file in domain_dir.glob("*.txt"):
                    # Extraire le nom de la bibliothèque du nom de fichier
                    filename = context_file.stem
                    
                    # Gérer les différents formats de noms de fichiers
                    if filename.endswith("-context"):
                        lib_name = filename[:-9]  # Supprimer "-context"
                    elif filename.endswith("_context"):
                        lib_name = filename[:-9]  # Supprimer "_context"
                    else:
                        # Pour les fichiers sans suffixe context (comme numcosmo.txt)
                        lib_name = filename
                    
                    existing_contexts[domain].append(lib_name)
        
        return existing_contexts
    
    def load_libraries_data(self) -> Dict[str, List[Dict]]:
        """Charge les données des bibliothèques depuis les fichiers JSON"""
        libraries = {}
        
        for domain in self.domains:
            json_file = self.data_dir / f"{domain}-libraries.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    libraries[domain] = data.get('libraries', [])
            else:
                libraries[domain] = []
        
        return libraries
    
    def extract_repo_info(self, github_url: str) -> Optional[Dict]:
        """Extrait les informations du repository depuis l'URL GitHub"""
        try:
            # Nettoyer l'URL
            url = github_url.strip()
            if not url.startswith('http'):
                url = f"https://{url}"
            
            # Extraire owner et repo
            if "github.com" in url:
                parts = url.split("github.com/")[1].split("/")
                if len(parts) >= 2:
                    owner = parts[0]
                    repo = parts[1].replace(".git", "")
                    return {"owner": owner, "repo": repo}
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting repo info from {github_url}: {e}")
            return None
    
    def generate_missing_contexts(self):
        """Génère les contextes manquants pour toutes les bibliothèques"""
        self.logger.info("🚀 Génération des contextes manquants...")
        
        # Vérifier que contextmaker et git sont disponibles
        if not self.check_contextmaker_available():
            self.logger.error("❌ Cannot continue without contextmaker")
            return
        
        if not self.check_git_available():
            self.logger.error("❌ Cannot continue without git")
            return
        
        # Charger les données existantes
        existing_contexts = self.get_existing_contexts()
        libraries_data = self.load_libraries_data()
        
        self.logger.info(f"Existing contexts: {existing_contexts}")
        self.logger.info(f"Found libraries: {list(libraries_data.keys())}")
        
        total_generated = 0
        
        for domain, libraries in libraries_data.items():
            self.logger.info(f"Processing domain: {domain}")
            
            existing_libs = existing_contexts.get(domain, [])
            
            for lib in libraries:
                lib_name = lib.get('name', '').replace('/', '-').replace('_', '-')
                github_url = lib.get('github_url', '')
                
                if not github_url:
                    self.logger.warning(f"No GitHub URL for {lib_name}")
                    continue
                
                # Vérifier si le contexte existe déjà (comparaison plus robuste)
                context_exists = False
                for existing_lib in existing_libs:
                    # Vérifier si le nom de la bibliothèque (sans namespace) correspond
                    if existing_lib in lib_name or lib_name.endswith(existing_lib):
                        context_exists = True
                        self.logger.info(f"Existing context for {lib_name} (matches {existing_lib}), skipped")
                        break
                
                if context_exists:
                    continue
                
                # Extraire les informations du repository
                repo_info = self.extract_repo_info(github_url)
                if not repo_info:
                    self.logger.error(f"Unable to extract repo info: {github_url}")
                    continue
                
                package_name = repo_info['repo']
                
                # 1. Cloner le repository
                if not self.clone_repository(repo_info['owner'], repo_info['repo'], package_name):
                    self.logger.error(f"Failed to clone {package_name}")
                    continue
                
                # 2. Générer le contenu du contexte avec contextmaker
                content = self.generate_context_with_contextmaker(package_name, lib_name, domain)
                
                if content:
                    # Sauvegarder le fichier
                    if self.save_context_file(domain, lib_name, content):
                        total_generated += 1
                    
                    # Pause pour éviter la surcharge
                    time.sleep(2)
                else:
                    self.logger.warning(f"Unable to generate context for {lib_name}")
        
        self.logger.info(f"Generation complete. {total_generated} new contexts created.")

    # ============================================================================
    # 3. NETTOYAGE DES DOUBLONS
    # ============================================================================
    
    def cleanup_duplicate_contexts_legacy(self):
        """Nettoyage legacy: Supprime les fichiers de contexte de public/context racine qui sont dans les sous-répertoires de domaines"""
        self.logger.info("🧹 Nettoyage legacy des doublons racine...")
        
        if not self.context_dir.exists():
            self.logger.info("public/context directory does not exist")
            return
        
        # Obtenir tous les fichiers de contexte dans public/context (niveau racine)
        root_context_files = []
        for file in self.context_dir.iterdir():
            if file.is_file() and file.name.endswith('-context.txt'):
                root_context_files.append(file.name)
        
        if not root_context_files:
            self.logger.info("No context files found in public/context root")
            return
        
        self.logger.info(f"Found {len(root_context_files)} context files in public/context root")
        
        # Vérifier chaque sous-répertoire de domaine
        files_to_remove = []
        
        for domain in self.domains:
            domain_dir = self.context_dir / domain
            if not domain_dir.exists():
                continue
                
            self.logger.info(f"Checking domain: {domain}")
            
            # Obtenir les fichiers de contexte dans le répertoire de domaine
            domain_files = []
            for file in domain_dir.iterdir():
                if file.is_file() and file.name.endswith('.txt'):
                    domain_files.append(file.name)
            
            self.logger.info(f"  Found {len(domain_files)} context files in {domain}/")
            
            # Trouver les doublons
            for root_file in root_context_files:
                if root_file in domain_files:
                    files_to_remove.append(self.context_dir / root_file)
                    self.logger.info(f"  Found duplicate: {root_file}")
        
        # Supprimer les fichiers dupliqués
        if files_to_remove:
            self.logger.info(f"Removing {len(files_to_remove)} duplicate files...")
            
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    self.logger.info(f"  Removed: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"  Error removing {file_path.name}: {e}")
            
            self.logger.info("Legacy cleanup completed successfully")
        else:
            self.logger.info("No duplicate files found to remove")
    
    def cleanup_all_duplicates(self):
        """Nettoyage avancé: Garde le contexte le plus long pour chaque bibliothèque"""
        self.logger.info("🧹 Nettoyage avancé des doublons...")
        
        for domain in self.domains:
            domain_dir = self.context_dir / domain
            if not domain_dir.exists():
                continue
            
            self.logger.info(f"Processing domain: {domain}")
            
            # Grouper les fichiers par bibliothèque
            library_files = {}
            
            for context_file in domain_dir.glob("*.txt"):
                if not context_file.name.endswith('.txt'):
                    continue
                
                # Extraire le nom de la bibliothèque
                lib_name = self.extract_library_name_from_filename(context_file.name)
                
                if lib_name not in library_files:
                    library_files[lib_name] = []
                
                library_files[lib_name].append(context_file)
            
            # Pour chaque bibliothèque, garder le fichier le plus long
            for lib_name, files in library_files.items():
                if len(files) > 1:
                    self.logger.info(f"  Found {len(files)} files for {lib_name}")
                    
                    # Trier par taille (le plus long en premier)
                    files.sort(key=lambda f: f.stat().st_size, reverse=True)
                    
                    # Garder le premier (le plus long) et supprimer les autres
                    for file_to_remove in files[1:]:
                        try:
                            file_to_remove.unlink()
                            self.logger.info(f"    Removed: {file_to_remove.name}")
                        except Exception as e:
                            self.logger.error(f"    Error removing {file_to_remove.name}: {e}")
    
    def extract_library_name_from_filename(self, filename: str) -> str:
        """Extrait le nom de la bibliothèque du nom de fichier"""
        # Supprimer les suffixes communs
        name = filename
        if name.endswith('-context.txt'):
            name = name[:-14]
        elif name.endswith('.txt'):
            name = name[:-4]
        
        # Gérer les différents patterns de nommage
        if '-' in name:
            parts = name.split('-')
            
            # Chercher la partie la plus descriptive
            if len(parts) >= 2:
                # Dernière partie pourrait être le nom de la bibliothèque
                potential_names = []
                potential_names.append(parts[-1])
                
                # Avant-dernière pourrait être le nom de la bibliothèque
                if len(parts) >= 3:
                    potential_names.append(parts[-2])
                
                # Cas spécial: "lesgourg-class-public" -> "class_public"
                if len(parts) >= 3 and parts[0] == 'lesgourg' and parts[1] == 'class':
                    return 'class_public'
                
                # Chercher la partie la plus descriptive
                for part in potential_names:
                    if len(part) > 2 and not part.startswith('astro') and not part.startswith('cosmo'):
                        return part
                
                # Fallback: retourner la dernière partie
                return parts[-1]
        
        return name
    
    def cleanup_duplicate_contexts(self):
        """Nettoie tous les contextes dupliqués"""
        self.logger.info("🧹 Début du nettoyage complet des contextes dupliqués...")
        
        # D'abord le nettoyage legacy (doublons racine)
        self.cleanup_duplicate_contexts_legacy()
        
        # Puis le nettoyage avancé (garder le plus long pour chaque bibliothèque)
        self.cleanup_all_duplicates()
        
        self.logger.info("✅ Nettoyage complet des contextes dupliqués terminé")

    # ============================================================================
    # 4. MISE À JOUR DES STATUTS JSON
    # ============================================================================
    
    def update_library_metadata(self):
        """Met à jour les métadonnées des bibliothèques pour tous les domaines"""
        self.logger.info("📝 Mise à jour des métadonnées des bibliothèques...")
        
        try:
            # Scanner les fichiers de contexte
            context_files = self.scan_context_files()
            
            # Mettre à jour tous les domaines
            for domain in self.domains:
                self.logger.info(f"  Mise à jour du domaine: {domain}")
                
                # Charger les données du domaine
                domain_data = self.load_domain_data(domain)
                
                # Mettre à jour les bibliothèques du domaine
                for lib in domain_data["libraries"]:
                    lib_name = lib["name"].replace("/", "-")
                    
                    # Chercher le fichier de contexte correspondant
                    has_context = False
                    context_filename = None
                    
                    for file_info in context_files.get(domain, []):
                        filename = file_info["filename"]
                        
                        # Extraire les parties du nom pour des correspondances flexibles
                        lib_parts = lib["name"].split("/")
                        lib_short = lib_parts[-1]  # Dernière partie
                        lib_first = lib_parts[0]   # Première partie
                        
                        # Vérifier si le fichier correspond à cette bibliothèque
                        if (filename == f"{lib_name}-context.txt" or 
                            filename == f"{lib_name}.txt" or
                            filename.startswith(f"{lib_name}-") and filename.endswith(".txt") or
                            filename == f"{lib_short}-context.txt" or
                            filename == f"{lib_short}.txt" or
                            filename == f"{lib_first}-context.txt" or
                            filename == f"{lib_first}.txt"):
                            has_context = True
                            context_filename = filename
                            break
                    
                    lib["hasContextFile"] = has_context
                    if has_context:
                        lib["contextFileName"] = context_filename
                    else:
                        # Supprimer la propriété si elle existe
                        if "contextFileName" in lib:
                            del lib["contextFileName"]
                
                # Sauvegarder le domaine
                domain_file = self.data_dir / f"{domain}-libraries.json"
                with open(domain_file, 'w') as f:
                    json.dump(domain_data, f, indent=2)
                
                self.logger.info(f"  ✅ {domain}: {len(domain_data['libraries'])} bibliothèques mises à jour")
            
            self.logger.info("✅ Métadonnées des bibliothèques mises à jour pour tous les domaines")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour métadonnées: {e}")
    
    def scan_context_files(self) -> Dict[str, List[Dict]]:
        """Scanne les fichiers de contexte"""
        context_files = {}
        
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                context_files[domain] = []
                
                for context_file in domain_dir.glob("*.txt"):
                    file_hash = self.get_file_hash(context_file)
                    context_files[domain].append({
                        "filename": context_file.name,
                        "path": str(context_file),
                        "hash": file_hash,
                        "size": context_file.stat().st_size
                    })
        
        return context_files
    
    def load_domain_data(self, domain: str) -> Dict:
        """Charge les données d'un domaine"""
        domain_json = self.data_dir / f"{domain}-libraries.json"
        if domain_json.exists():
            with open(domain_json, 'r') as f:
                return json.load(f)
        return {"libraries": [], "domain": domain}
    
    def load_astronomy_data(self) -> Dict:
        """Charge les données astronomy"""
        return self.load_domain_data("astronomy")
    
    def load_finance_data(self) -> Dict:
        """Charge les données finance"""
        return self.load_domain_data("finance")

    # ============================================================================
    # 5. GÉNÉRATION DU MODULE EMBEDDED-CONTEXT.TS
    # ============================================================================
    
    def generate_embedded_context(self):
        """Génère le module embedded-context.ts"""
        try:
            # Charger la configuration
            config = json.load(open(self.config_file, 'r'))
            programs = config.get("programs", [])
            
            # Générer le contenu embarqué
            combined_contexts = {}
            
            for program in programs:
                program_id = program.get("id")
                combined_context_file = program.get("combinedContextFile")
                
                if not program_id:
                    continue
                
                if combined_context_file and combined_context_file.startswith("/api/context/"):
                    # C'est un fichier de contexte dynamique
                    combined_contexts[program_id] = f"Context loaded from: {combined_context_file}"
                else:
                    # Pas de contexte défini
                    combined_contexts[program_id] = f"No context files defined for {program_id}"
            
            # Générer le contenu TypeScript
            context_lines = []
            for id, content in combined_contexts.items():
                context_lines.append(f"  '{id}': {json.dumps(content)},")
            
            ts_content = f"""// This file is auto-generated. Do not edit directly.
// Generated on {datetime.now().isoformat()}

/**
 * Embedded context content for each program
 * This avoids having to load context files at runtime
 */
export const embeddedContexts: Record<string, string> = {{
{chr(10).join(context_lines)}
}};

/**
 * Get the embedded context for a program
 * @param programId The ID of the program
 * @returns The embedded context content or undefined if not found
 */
export function getEmbeddedContext(programId: string): string | undefined {{
  return embeddedContexts[programId];
}}
"""
            
            # Écrire le fichier
            output_path = self.base_dir / "app" / "utils" / "embedded-context.ts"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(ts_content)
            
            self.logger.info(f"✅ Module embedded-context.ts généré: {output_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération embedded context: {e}")

    # ============================================================================
    # 6. RÉGÉNÉRATION DE CONFIG.JSON
    # ============================================================================
    
    def regenerate_config(self):
        """Régénère config.json"""
        try:
            script_path = self.base_dir / "scripts" / "core" / "generate-programs-from-libraries.py"
            
            if script_path.exists():
                result = subprocess.run(
                    ["python3", str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.base_dir
                )
                
                if result.returncode == 0:
                    self.logger.info("✅ config.json régénéré avec succès")
                    if result.stdout:
                        self.logger.info(f"Output: {result.stdout}")
                else:
                    self.logger.error(f"❌ Erreur régénération config: {result.stderr}")
            else:
                self.logger.error("❌ Script generate-programs-from-libraries.py introuvable")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur exécution script: {e}")

    # ============================================================================
    # 7. GESTION DES HASHES ET DÉTECTION DES CHANGEMENTS
    # ============================================================================
    
    def update_context_hashes(self):
        """Met à jour les hashes des contextes"""
        context_files = self.scan_context_files()
        
        for domain, files in context_files.items():
            for file_info in files:
                filename = file_info["filename"]
                file_hash = file_info["hash"]
                
                if domain not in self.state["context_hashes"]:
                    self.state["context_hashes"][domain] = {}
                
                self.state["context_hashes"][domain][filename] = file_hash
    
    def has_changes(self) -> bool:
        """Vérifie s'il y a des changements dans les fichiers de contexte"""
        current_files = self.scan_context_files()
        
        for domain, files in current_files.items():
            if domain not in self.state["context_hashes"]:
                return True
            
            for file_info in files:
                filename = file_info["filename"]
                current_hash = file_info["hash"]
                
                if filename not in self.state["context_hashes"][domain]:
                    return True
                
                if self.state["context_hashes"][domain][filename] != current_hash:
                    return True
        
        return False

    # ============================================================================
    # 8. EXÉCUTION PRINCIPALE UNIFIÉE
    # ============================================================================
    
    def run_full_update(self, force: bool = False):
        """Exécute la mise à jour complète unifiée"""
        self.logger.info("🚀 DÉBUT DE LA MISE À JOUR UNIFIÉE DES CONTEXTES")
        self.logger.info("=" * 60)
        
        try:
            # 1. Vérification de la structure
            self.logger.info("\n📋 ÉTAPE 1: Vérification de la structure des contextes")
            if not self.verify_context_structure():
                self.logger.warning("⚠️  Problèmes de structure détectés, mais continuation...")
            
            # 2. Génération des contextes manquants
            self.logger.info("\n🔄 ÉTAPE 2: Génération des contextes manquants")
            self.generate_missing_contexts()
            
            # 3. Nettoyage des doublons
            self.logger.info("\n🧹 ÉTAPE 3: Nettoyage des contextes dupliqués")
            self.cleanup_duplicate_contexts()
            
            # 4. Mise à jour des métadonnées
            self.logger.info("\n📝 ÉTAPE 4: Mise à jour des métadonnées")
            self.update_library_metadata()
            
            # 5. Régénération de config.json
            self.logger.info("\n⚙️  ÉTAPE 5: Régénération de config.json")
            self.regenerate_config()
            
            # 6. Génération du module embedded
            self.logger.info("\n📦 ÉTAPE 6: Génération du module embedded-context.ts")
            self.generate_embedded_context()
            
            # 7. Mise à jour des hashes et de l'état
            self.logger.info("\n💾 ÉTAPE 7: Mise à jour de l'état")
            self.update_context_hashes()
            self.state["last_update"] = datetime.now().isoformat()
            self.state["update_count"] += 1
            self.save_state()
            
            # 8. Nettoyage des repositories temporaires
            self.logger.info("\n🗑️  ÉTAPE 8: Nettoyage des repositories temporaires")
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("\n🎉 MISE À JOUR UNIFIÉE TERMINÉE AVEC SUCCÈS!")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la mise à jour unifiée: {e}")
            raise
        finally:
            # Mise à jour de la dernière vérification
            self.state["last_check"] = datetime.now().isoformat()
            self.save_state()
    
    def run_quick_update(self):
        """Exécute une mise à jour rapide (sans génération de contextes)"""
        self.logger.info("🚀 DÉBUT DE LA MISE À JOUR RAPIDE DES CONTEXTES")
        self.logger.info("=" * 50)
        
        try:
            # 1. Vérification de la structure
            self.logger.info("\n📋 ÉTAPE 1: Vérification de la structure des contextes")
            if not self.verify_context_structure():
                self.logger.warning("⚠️  Problèmes de structure détectés, mais continuation...")
            
            # 2. Nettoyage des doublons
            self.logger.info("\n🧹 ÉTAPE 2: Nettoyage des contextes dupliqués")
            self.cleanup_duplicate_contexts()
            
            # 3. Mise à jour des métadonnées
            self.logger.info("\n📝 ÉTAPE 3: Mise à jour des métadonnées")
            self.update_library_metadata()
            
            # 4. Régénération de config.json
            self.logger.info("\n⚙️  ÉTAPE 4: Régénération de config.json")
            self.regenerate_config()
            
            # 5. Génération du module embedded
            self.logger.info("\n📦 ÉTAPE 5: Génération du module embedded-context.ts")
            self.generate_embedded_context()
            
            # 6. Mise à jour des hashes et de l'état
            self.logger.info("\n💾 ÉTAPE 6: Mise à jour de l'état")
            self.update_context_hashes()
            self.state["last_update"] = datetime.now().isoformat()
            self.state["update_count"] += 1
            self.save_state()
            
            self.logger.info("\n🎉 MISE À JOUR RAPIDE TERMINÉE AVEC SUCCÈS!")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la mise à jour rapide: {e}")
            raise
        finally:
            # Mise à jour de la dernière vérification
            self.state["last_check"] = datetime.now().isoformat()
            self.save_state()
    
    def cleanup_pycache(self):
        """Nettoie tous les dossiers __pycache__ et fichiers .pyc"""
        self.logger.info("🧹 DÉBUT DU NETTOYAGE DES CACHES PYTHON")
        self.logger.info("=" * 50)
        
        try:
            # Trouver les éléments à nettoyer
            self.logger.info("🔍 Recherche des dossiers et fichiers à nettoyer...")
            pycache_dirs = self.find_pycache_dirs()
            pyc_files = self.find_pyc_files()
            
            self.logger.info(f"📁 Dossiers __pycache__ trouvés: {len(pycache_dirs)}")
            self.logger.info(f"📄 Fichiers .pyc trouvés: {len(pyc_files)}")
            
            if not pycache_dirs and not pyc_files:
                self.logger.info("✨ Aucun cache à nettoyer - projet déjà propre!")
                return {"pycache_dirs": 0, "pyc_files": 0, "total_cleaned": 0}
            
            # Nettoyer les dossiers __pycache__
            self.logger.info("\n🗑️  Suppression des dossiers __pycache__...")
            cleaned_dirs = self.cleanup_pycache_dirs(pycache_dirs)
            
            # Nettoyer les fichiers .pyc
            self.logger.info("\n🗑️  Suppression des fichiers .pyc...")
            cleaned_files = self.cleanup_pyc_files(pyc_files)
            
            # Résumé
            total_cleaned = cleaned_dirs + cleaned_files
            self.logger.info(f"\n📊 RÉSUMÉ DU NETTOYAGE:")
            self.logger.info("=" * 30)
            self.logger.info(f"✅ Dossiers __pycache__ supprimés: {cleaned_dirs}")
            self.logger.info(f"✅ Fichiers .pyc supprimés: {cleaned_files}")
            self.logger.info(f"✅ Total des éléments supprimés: {total_cleaned}")
            
            return {
                "pycache_dirs": cleaned_dirs,
                "pyc_files": cleaned_files,
                "total_cleaned": total_cleaned
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du nettoyage des caches: {e}")
            raise
    
    def find_pycache_dirs(self) -> list:
        """Trouve tous les dossiers __pycache__"""
        pycache_dirs = []
        
        for root, dirs, files in os.walk(self.base_dir):
            if '__pycache__' in dirs:
                pycache_path = Path(root) / '__pycache__'
                pycache_dirs.append(pycache_path)
        
        return pycache_dirs
    
    def find_pyc_files(self) -> list:
        """Trouve tous les fichiers .pyc"""
        pyc_files = []
        
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.pyc'):
                    pyc_path = Path(root) / file
                    pyc_files.append(pyc_path)
        
        return pyc_files
    
    def cleanup_pycache_dirs(self, pycache_dirs: list) -> int:
        """Nettoie les dossiers __pycache__"""
        cleaned_count = 0
        
        for pycache_dir in pycache_dirs:
            try:
                if pycache_dir.exists():
                    # Calculer la taille avant suppression
                    total_size = sum(f.stat().st_size for f in pycache_dir.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)
                    
                    # Supprimer le dossier
                    shutil.rmtree(pycache_dir)
                    self.logger.info(f"🗑️  Supprimé: {pycache_dir} ({size_mb:.2f} MB)")
                    cleaned_count += 1
                    
            except Exception as e:
                self.logger.error(f"❌ Erreur suppression {pycache_dir}: {e}")
        
        return cleaned_count
    
    def cleanup_pyc_files(self, pyc_files: list) -> int:
        """Nettoie les fichiers .pyc"""
        cleaned_count = 0
        
        for pyc_file in pyc_files:
            try:
                if pyc_file.exists():
                    # Calculer la taille avant suppression
                    size_bytes = pyc_file.stat().st_size
                    size_kb = size_bytes / 1024
                    
                    # Supprimer le fichier
                    pyc_file.unlink()
                    self.logger.info(f"🗑️  Supprimé: {pyc_file} ({size_kb:.2f} KB)")
                    cleaned_count += 1
                    
            except Exception as e:
                self.logger.error(f"❌ Erreur suppression {pyc_file}: {e}")
        
        return cleaned_count
    
    def cleanup_log_files(self):
        """Nettoie les anciens fichiers de logs"""
        self.logger.info("🧹 Nettoyage des fichiers de logs...")
        
        try:
            # Logs à nettoyer (anciens scripts supprimés)
            old_logs = [
                "cleanup_duplicates.log",
                "cleanup_pycache.log", 
                "context_generation.log",
                "context_manager.log",
                "json_status_update.log",
                "unified_context_manager.log"
            ]
            
            # Logs à conserver (scripts actifs)
            active_logs = [
                "maintenance.log",
                "scheduler.log"
            ]
            
            cleaned_count = 0
            total_size_mb = 0
            
            for log_file in old_logs:
                log_path = self.base_dir / log_file
                if log_path.exists():
                    try:
                        # Calculer la taille avant suppression
                        size_bytes = log_path.stat().st_size
                        size_mb = size_bytes / (1024 * 1024)
                        total_size_mb += size_mb
                        
                        # Supprimer le fichier
                        log_path.unlink()
                        self.logger.info(f"🗑️  Supprimé: {log_file} ({size_mb:.2f} MB)")
                        cleaned_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"❌ Erreur suppression {log_file}: {e}")
            
            # Nettoyer aussi les logs du dossier logs/ (plus de 7 jours)
            logs_dir = self.base_dir / "logs"
            if logs_dir.exists():
                cutoff_date = datetime.now() - timedelta(days=7)
                for log_file in logs_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        try:
                            size_bytes = log_file.stat().st_size
                            size_mb = size_bytes / (1024 * 1024)
                            total_size_mb += size_mb
                            
                            log_file.unlink()
                            self.logger.info(f"🗑️  Supprimé: logs/{log_file.name} ({size_mb:.2f} MB)")
                            cleaned_count += 1
                            
                        except Exception as e:
                            self.logger.error(f"❌ Erreur suppression logs/{log_file.name}: {e}")
            
            if cleaned_count > 0:
                self.logger.info(f"✅ Nettoyage des logs terminé: {cleaned_count} fichiers supprimés ({total_size_mb:.2f} MB)")
            else:
                self.logger.info("✨ Aucun log à nettoyer")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du nettoyage des logs: {e}")
    
    def cleanup_all(self):
        """Nettoie tout : caches Python, logs et contextes dupliqués"""
        self.logger.info("🧹 DÉBUT DU NETTOYAGE COMPLET")
        self.logger.info("=" * 50)
        
        try:
            # 1. Nettoyage des caches Python
            self.logger.info("\n🗑️  ÉTAPE 1: Nettoyage des caches Python")
            pycache_result = self.cleanup_pycache()
            
            # 2. Nettoyage des logs
            self.logger.info("\n🗑️  ÉTAPE 2: Nettoyage des logs")
            self.cleanup_log_files()
            
            # 3. Nettoyage des contextes dupliqués
            self.logger.info("\n🗑️  ÉTAPE 3: Nettoyage des contextes dupliqués")
            self.cleanup_duplicate_contexts()
            
            self.logger.info("\n🎉 NETTOYAGE COMPLET TERMINÉ!")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du nettoyage complet: {e}")
            raise

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gestionnaire unifié des contextes - Remplace tous les scripts de maintenance des contextes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 context-manager-unified.py --full           # Mise à jour complète avec génération de contextes
  python3 context-manager-unified.py --quick          # Mise à jour rapide sans génération
  python3 context-manager-unified.py --verify         # Vérification de la structure uniquement
  python3 context-manager-unified.py --cleanup        # Nettoyage des doublons uniquement
  python3 context-manager-unified.py --cleanup-pycache # Nettoyage des caches Python uniquement
  python3 context-manager-unified.py --cleanup-all    # Nettoyage complet (caches, logs et doublons)
        """
    )
    
    parser.add_argument("--full", action="store_true", help="Mise à jour complète avec génération de contextes")
    parser.add_argument("--quick", action="store_true", help="Mise à jour rapide sans génération")
    parser.add_argument("--verify", action="store_true", help="Vérification de la structure uniquement")
    parser.add_argument("--cleanup", action="store_true", help="Nettoyage des doublons uniquement")
    parser.add_argument("--cleanup-pycache", action="store_true", help="Nettoyage des caches Python uniquement")
    parser.add_argument("--cleanup-all", action="store_true", help="Nettoyage complet (caches, logs et doublons)")
    parser.add_argument("--base-dir", default=".", help="Répertoire de base")
    
    args = parser.parse_args()
    
    manager = UnifiedContextManager(args.base_dir)
    
    if args.verify:
        manager.verify_context_structure()
    elif args.cleanup:
        manager.cleanup_duplicate_contexts()
    elif args.cleanup_pycache:
        manager.cleanup_pycache()
    elif args.cleanup_all:
        manager.cleanup_all()
    elif args.quick:
        manager.run_quick_update()
    elif args.full:
        manager.run_full_update()
    else:
        # Par défaut, exécuter la mise à jour rapide
        manager.run_quick_update()

if __name__ == "__main__":
    main()
