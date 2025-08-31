# Dossier Gestion

Ce dossier contient tous les fichiers de gestion et de configuration qui ne sont pas directement liés à la logique métier du projet.

## Structure

### Configuration
- `budget-config.json` - Configuration pour déploiement optimisé des coûts GCP
- `cloud-config.json` - Configuration pour stockage cloud (S3, GCS, HTTP)
- `cors.json` - Configuration CORS pour les buckets cloud
- `lifecycle.json` - Configuration du cycle de vie des objets cloud
- `gcp-credentials.json` - Credentials Google Cloud Platform

### Déploiement
- `deploy-budget.sh` - Script de déploiement optimisé pour les coûts
- `deployment-config/` - Configurations de déploiement spécifiques

### État et Logs
- `updater_state.json` - État de l'updater automatique
- `config_update_state.json` - État des mises à jour de configuration
- `conversion.log` - Logs de conversion
- `config_update.log` - Logs de mise à jour de configuration
- `optimized_update.log` - Logs de mise à jour optimisée

### Dossiers de données
- `logs/` - Logs du système
- `temp/` - Fichiers temporaires

## Utilisation

Les scripts du projet ont été mis à jour pour référencer ces fichiers dans le dossier `gestion/`. 
Aucune modification n'est nécessaire dans votre workflow habituel.

## Maintenance

- Les fichiers de configuration peuvent être modifiés directement dans ce dossier
- Les logs sont automatiquement gérés par les scripts
- Les fichiers temporaires sont nettoyés automatiquement
