#!/usr/bin/env python3
"""
Script unifié pour la gestion des contextes
Remplace: update-context-status.js, update-context-auto.js, update-context-python.py, 
         build-context.js, generate-context-module.js, update-config-from-contexts.py

Fonctionnalités:
1. Mise à jour des statuts des contextes dans les JSON
2. Génération du module embedded-context.ts
3. Copie des contextes vers public/context/
4. Mise à jour automatique de config.json
5. Détection des changements et mise à jour forcée
"""

import os
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ContextManager:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "app" / "data"
        self.context_dir = self.base_dir / "public" / "context"
        self.app_context_dir = self.base_dir / "app" / "context"
        self.config_file = self.base_dir / "config.json"
        self.state_file = self.base_dir / "context_manager_state.json"
        
        # Setup logging
        self.setup_logging()
        
        # Load state
        self.state = self.load_state()
        
    def setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('context_manager.log'),
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
                        "hash": file_hash,
                        "path": str(context_file)
                    })
        
        return context_files
    
    def has_changes(self) -> bool:
        """Vérifie s'il y a des changements"""
        current_context_files = self.scan_context_files()
        
        for domain, files in current_context_files.items():
            for file_info in files:
                filename = file_info["filename"]
                current_hash = file_info["hash"]
                previous_hash = self.state.get("context_hashes", {}).get(f"{domain}/{filename}")
                
                if current_hash != previous_hash:
                    self.logger.info(f"Fichier contexte modifié: {domain}/{filename}")
                    return True
        
        return False
    
    def update_context_hashes(self):
        """Met à jour les hashes des fichiers de contexte"""
        current_context_files = self.scan_context_files()
        
        for domain, files in current_context_files.items():
            for file_info in files:
                filename = file_info["filename"]
                current_hash = file_info["hash"]
                self.state["context_hashes"][f"{domain}/{filename}"] = current_hash
    
    def update_library_metadata(self):
        """Met à jour les métadonnées des bibliothèques"""
        try:
            # Charger les données
            astronomy_data = json.load(open(self.data_dir / "astronomy-libraries.json", 'r'))
            finance_data = json.load(open(self.data_dir / "finance-libraries.json", 'r'))
            
            # Scanner les fichiers de contexte
            context_files = self.scan_context_files()
            
            # Mettre à jour les bibliothèques astronomy
            for lib in astronomy_data["libraries"]:
                lib_name = lib["name"].split("/")[-1]
                context_filename = f"{lib_name}-context.txt"
                
                has_context = any(
                    file_info["filename"] == context_filename 
                    for file_info in context_files.get("astro", [])
                )
                
                lib["hasContextFile"] = has_context
                if has_context:
                    lib["contextFileName"] = context_filename
            
            # Mettre à jour les bibliothèques finance
            for lib in finance_data["libraries"]:
                lib_name = lib["name"].split("/")[-1]
                context_filename = f"{lib_name}-context.txt"
                
                has_context = any(
                    file_info["filename"] == context_filename 
                    for file_info in context_files.get("finance", [])
                )
                
                lib["hasContextFile"] = has_context
                if has_context:
                    lib["contextFileName"] = context_filename
            
            # Sauvegarder
            with open(self.data_dir / "astronomy-libraries.json", 'w') as f:
                json.dump(astronomy_data, f, indent=2)
            
            with open(self.data_dir / "finance-libraries.json", 'w') as f:
                json.dump(finance_data, f, indent=2)
            
            self.logger.info("Métadonnées des bibliothèques mises à jour")
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour métadonnées: {e}")
    
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
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(ts_content)
            
            self.logger.info(f"Module embedded-context.ts généré: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erreur génération embedded context: {e}")
    
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
                    self.logger.info("config.json régénéré avec succès")
                    self.logger.info(result.stdout)
                else:
                    self.logger.error(f"Erreur régénération config: {result.stderr}")
            else:
                self.logger.error("Script generate-programs-from-libraries.py introuvable")
                
        except Exception as e:
            self.logger.error(f"Erreur exécution script: {e}")
    
    def run_update(self, force: bool = False):
        """Exécute la mise à jour complète"""
        self.logger.info("Vérification des changements dans les fichiers de contexte...")
        
        if force or self.has_changes():
            if force:
                self.logger.info("Mise à jour forcée demandée...")
            else:
                self.logger.info("Changements détectés, mise à jour de la configuration...")
            
            # Mettre à jour les métadonnées
            self.update_library_metadata()
            
            # Régénérer config.json
            self.regenerate_config()
            
            # Générer le module embedded
            self.generate_embedded_context()
            
            # Mettre à jour les hashes
            self.update_context_hashes()
            
            # Mettre à jour l'état
            self.state["last_update"] = datetime.now().isoformat()
            self.state["update_count"] += 1
            self.save_state()
            
            self.logger.info("Configuration mise à jour avec succès")
        else:
            self.logger.info("Aucun changement détecté")
        
        self.state["last_check"] = datetime.now().isoformat()
        self.save_state()

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionnaire unifié des contextes")
    parser.add_argument("--force", action="store_true", help="Forcer la mise à jour même sans changements")
    parser.add_argument("--base-dir", default=".", help="Répertoire de base")
    
    args = parser.parse_args()
    
    manager = ContextManager(args.base_dir)
    manager.run_update(force=args.force)

if __name__ == "__main__":
    main()
