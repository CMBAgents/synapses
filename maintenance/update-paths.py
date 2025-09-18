#!/usr/bin/env python3
"""
Script pour mettre à jour les chemins dans les autres scripts
après la réorganisation du dossier scripts
"""

import os
import re
from pathlib import Path

def update_paths_in_file(filepath: Path):
    """Met à jour les chemins dans un fichier"""
    if not filepath.exists():
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Anciens chemins vers nouveaux chemins (seulement les scripts existants)
    path_mappings = {
        'maintenance/maintenance.py': 'maintenance/maintenance/maintenance.py',
        'maintenance/generate-programs-from-libraries.py': 'maintenance/core/generate-programs-from-libraries.py',
        'maintenance/generate-missing-contexts.py': 'maintenance/maintenance/generate-missing-contexts.py',
        'maintenance/generate-contexts-with-clone.py': 'maintenance/maintenance/generate-contexts-with-clone.py',
        'maintenance/generate-and-sync-all.py': 'maintenance/maintenance/generate-and-sync-all.py',
        'maintenance/setup_maintenance_service.sh': 'maintenance/maintenance/setup_maintenance_service.sh',
        'maintenance/service-control.sh': 'maintenance/maintenance/service-control.sh',
        'maintenance/schedule_daily_maintenance.py': 'maintenance/maintenance/schedule_daily_maintenance.py',
        'maintenance/test_maintenance.py': 'maintenance/utils/test_maintenance.py',
        'maintenance/test-unified-scripts.py': 'maintenance/utils/test-unified-scripts.py',
        'maintenance/update-domain-data.py': 'maintenance/utils/update-domain-data.py',
        'maintenance/cleanup-scripts.py': 'maintenance/utils/cleanup-scripts.py',
    }
    
    updated_content = content
    for old_path, new_path in path_mappings.items():
        updated_content = updated_content.replace(old_path, new_path)
    
    if updated_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ Mis à jour: {filepath}")
        return True
    
    return False

def main():
    """Met à jour tous les fichiers du projet"""
    base_dir = Path(".")
    
    # Fichiers à mettre à jour
    files_to_update = [
        "package.json",
        "README.md",
        "docs/README.md",
        "docs/DEPLOYMENT_CHECKLIST.md",
        "docs/DAILY_MAINTENANCE_GUIDE.md",
    ]
    
    # Ajouter tous les fichiers Python et shell dans scripts
    for script_file in base_dir.rglob("maintenance/**/*"):
        if script_file.is_file() and script_file.suffix in ['.py', '.sh', '.js', '.ts']:
            files_to_update.append(str(script_file))
    
    updated_count = 0
    
    for file_path in files_to_update:
        if Path(file_path).exists():
            if update_paths_in_file(Path(file_path)):
                updated_count += 1
    
    print(f"\n📊 Résumé:")
    print(f"   - Fichiers mis à jour: {updated_count}")
    print(f"   - Fichiers vérifiés: {len(files_to_update)}")

if __name__ == "__main__":
    main()
