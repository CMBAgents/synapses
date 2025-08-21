# Scripts de CMB Agent Info

## 📁 Organisation des scripts

Les scripts sont organisés par catégorie pour une meilleure lisibilité et maintenance :

### 🔧 **Core** (`/core/`)
Scripts fondamentaux pour la gestion des contextes et la configuration
- `generate-programs-from-libraries.py` - Génération de config.json

### 🔄 **Maintenance** (`/maintenance/`)
Scripts de maintenance automatique et génération de contextes
- `maintenance.py` - Maintenance simplifiée
- `context-manager-unified.py` - Gestionnaire unifié des contextes
- `generate-missing-contexts.py` - Génération des contextes manquants
- `generate-contexts-with-clone.py` - Génération avec clonage Git
- `generate-and-sync-all.py` - Génération et synchronisation complète
- `setup_maintenance_service.sh` - Configuration du service de maintenance
- `service-control.sh` - Contrôle des services
- `schedule_daily_maintenance.py` - Planification de la maintenance

### 🧪 **Utils** (`/utils/`)
Scripts utilitaires et de test
- `test_maintenance.py` - Tests de maintenance
- `test-unified-scripts.py` - Tests des scripts unifiés
- `update-domain-data.py` - Mise à jour des données de domaine
- `cleanup-scripts.py` - Nettoyage des scripts redondants
- `update-paths.py` - Mise à jour des chemins

## 🚀 Utilisation recommandée

### Maintenance quotidienne
```bash
python3 scripts/maintenance/maintenance.py --quick
```

### Mise à jour des contextes
```bash
python3 scripts/maintenance/context-manager-unified.py --force
```

### Génération de contextes manquants
```bash
python3 scripts/maintenance/generate-missing-contexts.py --domain astro
```

### Tests
```bash
python3 scripts/utils/test-unified-scripts.py
```

## 📋 Workflow typique

1. **Configuration** : `scripts/maintenance/context-manager-unified.py --force`
2. **Maintenance** : `scripts/maintenance/maintenance.py --quick`

## 🔄 Simplification réalisée

- **Avant** : 30+ scripts dispersés
- **Après** : Scripts essentiels organisés en 3 catégories
- **Réduction** : ~70% de scripts redondants supprimés
- **Organisation** : Structure claire et logique
