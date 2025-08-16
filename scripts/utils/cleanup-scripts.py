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
        # Scripts de gestion des contextes (remplacés par manage-contexts.py)
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
        
        # Scripts de déploiement (remplacés par deploy.py)
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
        "manage-contexts.py",
        "maintenance.py", 
        "deploy.py",
        
        # Scripts essentiels
        "generate-programs-from-libraries.py",
        "generate-missing-contexts.py",
        "generate-contexts-with-clone.py",
        "generate-and-sync-all.py",
        "cloud-sync-contexts.py",
        "cost-monitor.py",
        
        # Scripts d'installation et configuration
        "install-dependencies.py",
        "install_contextmaker.py",
        "mock_contextmaker.py",
        "install-config-updater.sh",
        "install-service.sh",
        "setup_maintenance_service.sh",
        "service-control.sh",
        "schedule_daily_maintenance.py",
        
        # Scripts de test
        "test_maintenance.py",
        
        # Scripts de données
        "update-domain-data.py",
        
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

### `manage-contexts.py`
Script unifié pour la gestion des contextes.
**Remplace:** update-context-status.js, update-context-auto.js, update-context-python.py, build-context.js, generate-context-module.js, update-config-from-contexts.py

**Utilisation:**
```bash
python3 scripts/manage-contexts.py --force
```

### `maintenance.py`
Script de maintenance simplifié.
**Remplace:** daily_maintenance.py, optimized-auto-update.py, monitor-updater.py

**Utilisation:**
```bash
# Maintenance complète
python3 scripts/maintenance.py

# Maintenance rapide
python3 scripts/maintenance.py --quick
```

### `deploy.py`
Script de déploiement unifié.
**Remplace:** deploy-gcp.sh, deploy-gcp-budget.sh, setup-deployment.sh, setup-budget-alerts.sh

**Utilisation:**
```bash
python3 scripts/deploy.py --project-id YOUR_PROJECT_ID
```

## Scripts essentiels

### Génération et configuration
- `generate-programs-from-libraries.py` - Génère config.json depuis les données JSON
- `generate-missing-contexts.py` - Génère les contextes manquants
- `generate-contexts-with-clone.py` - Génère les contextes avec clonage Git
- `generate-and-sync-all.py` - Génération et synchronisation complète

### Cloud et monitoring
- `cloud-sync-contexts.py` - Synchronisation avec le cloud
- `cost-monitor.py` - Surveillance des coûts GCP

### Installation et configuration
- `install-dependencies.py` - Installation des dépendances
- `install_contextmaker.py` - Installation de contextmaker
- `mock_contextmaker.py` - Mock de contextmaker pour les tests
- `install-config-updater.sh` - Installation du config updater
- `install-service.sh` - Installation des services
- `setup_maintenance_service.sh` - Configuration du service de maintenance
- `service-control.sh` - Contrôle des services
- `schedule_daily_maintenance.py` - Planification de la maintenance

### Tests et données
- `test_maintenance.py` - Tests de maintenance
- `update-domain-data.py` - Mise à jour des données de domaine

## Utilisation recommandée

### Maintenance quotidienne
```bash
python3 scripts/maintenance.py --quick
```

### Mise à jour des contextes
```bash
python3 scripts/manage-contexts.py --force
```

### Déploiement
```bash
python3 scripts/deploy.py --project-id YOUR_PROJECT_ID --budget 15.0
```

### Génération de contextes manquants
```bash
python3 scripts/generate-missing-contexts.py --domain astronomy
```
"""
    
    with open("scripts/README.md", "w") as f:
        f.write(doc_content)
    
    print(f"\n📝 Documentation créée: scripts/README.md")

if __name__ == "__main__":
    cleanup_scripts()
