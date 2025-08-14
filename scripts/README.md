# Scripts de CMB Agent Info

## 📁 Organisation des scripts

Les scripts sont organisés par catégorie pour une meilleure lisibilité et maintenance :

### 🔧 **Core** (`/core/`)
Scripts fondamentaux pour la gestion des contextes et la configuration
- `manage-contexts.py` - Gestionnaire unifié des contextes
- `generate-programs-from-libraries.py` - Génération de config.json

### 🚀 **Deployment** (`/deployment/`)
Scripts de déploiement et configuration cloud
- `deploy.py` - Déploiement unifié GCP

### 🔄 **Maintenance** (`/maintenance/`)
Scripts de maintenance automatique et génération de contextes
- `maintenance.py` - Maintenance simplifiée
- `generate-missing-contexts.py` - Génération des contextes manquants
- `generate-contexts-with-clone.py` - Génération avec clonage Git
- `generate-and-sync-all.py` - Génération et synchronisation complète
- `setup_maintenance_service.sh` - Configuration du service de maintenance
- `service-control.sh` - Contrôle des services
- `schedule_daily_maintenance.py` - Planification de la maintenance

### ☁️ **Cloud** (`/cloud/`)
Scripts de synchronisation et monitoring cloud
- `cloud-sync-contexts.py` - Synchronisation avec le cloud
- `cost-monitor.py` - Surveillance des coûts GCP

### 🛠️ **Install** (`/install/`)
Scripts d'installation et configuration
- `install-dependencies.py` - Installation des dépendances
- `install_contextmaker.py` - Installation de contextmaker
- `mock_contextmaker.py` - Mock de contextmaker pour les tests
- `install-config-updater.sh` - Installation du config updater
- `install-service.sh` - Installation des services

### 🧪 **Utils** (`/utils/`)
Scripts utilitaires et de test
- `test_maintenance.py` - Tests de maintenance
- `test-unified-scripts.py` - Tests des scripts unifiés
- `update-domain-data.py` - Mise à jour des données de domaine
- `cleanup-scripts.py` - Nettoyage des scripts redondants

## 🚀 Utilisation recommandée

### Maintenance quotidienne
```bash
python3 scripts/maintenance/maintenance.py --quick
```

### Mise à jour des contextes
```bash
python3 scripts/core/manage-contexts.py --force
```

### Déploiement
```bash
python3 scripts/deployment/deploy.py --project-id YOUR_PROJECT_ID
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

1. **Installation** : `scripts/install/install-dependencies.py`
2. **Configuration** : `scripts/core/manage-contexts.py --force`
3. **Maintenance** : `scripts/maintenance/maintenance.py --quick`
4. **Déploiement** : `scripts/deployment/deploy.py`
5. **Monitoring** : `scripts/cloud/cost-monitor.py`

## 🔄 Simplification réalisée

- **Avant** : 30+ scripts dispersés
- **Après** : 15 scripts organisés en 6 catégories
- **Réduction** : ~50% de scripts redondants supprimés
- **Organisation** : Structure claire et logique
