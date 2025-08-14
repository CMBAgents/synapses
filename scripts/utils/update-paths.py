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
    
    # Anciens chemins vers nouveaux chemins
    path_mappings = {
        'scripts/manage-contexts.py': 'scripts/core/manage-contexts.py',
        'scripts/maintenance.py': 'scripts/maintenance/maintenance.py',
        'scripts/deploy.py': 'scripts/deployment/deploy.py',
        'scripts/generate-programs-from-libraries.py': 'scripts/core/generate-programs-from-libraries.py',
        'scripts/generate-missing-contexts.py': 'scripts/maintenance/generate-missing-contexts.py',
        'scripts/generate-contexts-with-clone.py': 'scripts/maintenance/generate-contexts-with-clone.py',
        'scripts/generate-and-sync-all.py': 'scripts/maintenance/generate-and-sync-all.py',
        'scripts/cloud-sync-contexts.py': 'scripts/cloud/cloud-sync-contexts.py',
        'scripts/cost-monitor.py': 'scripts/cloud/cost-monitor.py',
        'scripts/install-dependencies.py': 'scripts/install/install-dependencies.py',
        'scripts/install_contextmaker.py': 'scripts/install/install_contextmaker.py',
        'scripts/mock_contextmaker.py': 'scripts/install/mock_contextmaker.py',
        'scripts/install-config-updater.sh': 'scripts/install/install-config-updater.sh',
        'scripts/install-service.sh': 'scripts/install/install-service.sh',
        'scripts/setup_maintenance_service.sh': 'scripts/maintenance/setup_maintenance_service.sh',
        'scripts/service-control.sh': 'scripts/maintenance/service-control.sh',
        'scripts/schedule_daily_maintenance.py': 'scripts/maintenance/schedule_daily_maintenance.py',
        'scripts/test_maintenance.py': 'scripts/utils/test_maintenance.py',
        'scripts/test-unified-scripts.py': 'scripts/utils/test-unified-scripts.py',
        'scripts/update-domain-data.py': 'scripts/utils/update-domain-data.py',
        'scripts/cleanup-scripts.py': 'scripts/utils/cleanup-scripts.py',
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
    for script_file in base_dir.rglob("scripts/**/*"):
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
