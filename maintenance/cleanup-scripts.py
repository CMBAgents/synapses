#!/usr/bin/env python3
"""
Script de nettoyage pour supprimer les scripts redondants
Après la création des scripts unifiés, ce script supprime les anciens scripts
"""

import os
import shutil
from pathlib import Path

def cleanup_scripts():
    """Supprime les scripts redondants"""
    
    # Scripts à supprimer (redondants ou obsolètes)
    scripts_to_remove = [
        # Scripts de gestion des contextes (remplacés par context-manager-unified.py)
        "update-context-status.js",
        "update-context-auto.js", 
        "update-context-python.py",
        "build-context.js",
        "generate-context-module.js",
        "update-config-from-contexts.py",
        
        # Scripts de maintenance (remplacés par maintenance.py)
        "daily_maintenance.py",
        "optimized-auto-update.py",
        "monitor-updater.py",
        
        # Scripts de déploiement (supprimés)
        "deploy-gcp.sh",
        "deploy-gcp-budget.sh",
        "setup-deployment.sh",
        "setup-budget-alerts.sh",
        
        # Doublons
        "generate-programs-from-libraries.js",  # Doublon de la version Python
        
        # Scripts de validation (peuvent être fusionnés)
        "validate-config.js",
        "validate-config.ts",
    ]
    
    # Scripts à garder (essentiels)
    scripts_to_keep = [
        # Scripts unifiés (nouveaux)
        "maintenance_modular.py", 
        
        # Scripts essentiels
        "generate-programs-from-libraries.py",
        "generate-missing-contexts.py",
        "generate-contexts-with-clone.py",
        "generate-and-sync-all.py",
        
        # Scripts de configuration
        "setup_maintenance_service.sh",
        "service-control.sh",
        "schedule_daily_maintenance.py",
        
        # Scripts de test
        "test_maintenance.py",
        "test-unified-scripts.py",
        
        # Scripts de données
        "update-domain-data.py",
        "update-paths.py",
        
        # Script de nettoyage lui-même
        "cleanup-scripts.py",
    ]
    
    scripts_dir = Path("scripts")
    
    print("🧹 Nettoyage des scripts redondants...")
    print("=" * 50)
    
    # Vérifier les scripts à supprimer
    removed_count = 0
    for script in scripts_to_remove:
        script_path = scripts_dir / script
        if script_path.exists():
            try:
                script_path.unlink()
                print(f"🗑️  Supprimé: {script}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Erreur suppression {script}: {e}")
        else:
            print(f"ℹ️  Non trouvé: {script}")
    
    print(f"\n✅ {removed_count} scripts supprimés")
    
    # Lister les scripts restants
    print("\n📋 Scripts conservés:")
    print("-" * 30)
    
    remaining_scripts = []
    for script_file in scripts_dir.glob("*"):
        if script_file.is_file() and script_file.name not in scripts_to_remove:
            remaining_scripts.append(script_file.name)
    
    for script in sorted(remaining_scripts):
        print(f"✅ {script}")
    
    print(f"\n📊 Résumé:")
    print(f"   - Scripts supprimés: {removed_count}")
    print(f"   - Scripts conservés: {len(remaining_scripts)}")
    print(f"   - Total: {len(remaining_scripts) + removed_count}")
    
    # Créer un fichier de documentation
    create_documentation(remaining_scripts)

def create_documentation(scripts):
    """Crée une documentation des scripts restants"""
    
    doc_content = """# Scripts de CMB Agent Info

## Scripts unifiés (nouveaux)

### `context-manager-unified.py`
Script unifié pour la gestion des contextes.
**Remplace:** update-context-status.js, update-context-auto.js, update-context-python.py, build-context.js, generate-context-module.js, update-config-from-contexts.py

**Utilisation:**
```bash
python3 maintenance/context-manager-unified.py --force
```

### `maintenance_modular.py`
Script de maintenance modulaire.
**Remplace:** maintenance.py, context-manager-unified.py, daily_maintenance.py, optimized-auto-update.py, monitor-updater.py

**Utilisation:**
```bash
# Maintenance complète
python3 maintenance/maintenance_modular.py --mode full

# Maintenance rapide
python3 maintenance/maintenance_modular.py --mode quick
```

## Scripts essentiels

### Génération et configuration
- `generate-programs-from-libraries.py` - Génère config.json depuis les données JSON
- `generate-missing-contexts.py` - Génère les contextes manquants
- `generate-contexts-with-clone.py` - Génère les contextes avec clonage Git
- `generate-and-sync-all.py` - Génération et synchronisation complète

### Configuration et services
- `setup_maintenance_service.sh` - Configuration du service de maintenance
- `service-control.sh` - Contrôle des services
- `schedule_daily_maintenance.py` - Planification de la maintenance

### Tests et données
- `test_maintenance.py` - Tests de maintenance
- `test-unified-scripts.py` - Tests des scripts unifiés
- `update-domain-data.py` - Mise à jour des données de domaine
- `update-paths.py` - Mise à jour des chemins

## Utilisation recommandée

### Maintenance quotidienne
```bash
python3 maintenance/maintenance_modular.py --mode quick
```

### Mise à jour des contextes
```bash
python3 maintenance/maintenance_modular.py --mode full
```

### Génération de contextes manquants
```bash
python3 maintenance/generate-missing-contexts.py --domain astronomy
```
"""
    
    with open("maintenance/README.md", "w") as f:
        f.write(doc_content)
    
    print(f"\n📝 Documentation créée: maintenance/README.md")

if __name__ == "__main__":
    cleanup_scripts()
