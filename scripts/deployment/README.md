# 🚀 Deployment Scripts

Scripts de déploiement et configuration cloud.

## Scripts

### `deploy.py`
Script de déploiement unifié qui remplace 4 scripts redondants.

**Fonctionnalités :**
- Déploiement GCP (Cloud Run, Storage, etc.)
- Configuration des alertes de budget
- Installation des services
- Configuration de la surveillance

**Utilisation :**
```bash
# Déploiement complet
python3 deploy.py --project-id YOUR_PROJECT_ID

# Déploiement avec options personnalisées
python3 deploy.py \
  --project-id YOUR_PROJECT_ID \
  --region us-central1 \
  --budget 15.0 \
  --no-monitoring \
  --no-budget-alerts
```

**Options :**
- `--project-id` : ID du projet GCP (requis)
- `--region` : Région GCP (défaut: us-central1)
- `--budget` : Montant du budget en USD (défaut: 15.0)
- `--no-monitoring` : Désactiver la surveillance
- `--no-budget-alerts` : Désactiver les alertes de budget

## Étapes de déploiement

1. **Vérification des prérequis :**
   - Google Cloud CLI
   - Node.js et npm
   - Python 3

2. **Configuration du projet :**
   - Définition du projet GCP
   - Activation des APIs nécessaires

3. **Création des ressources :**
   - Buckets de stockage
   - Configuration des permissions

4. **Build et déploiement :**
   - Build de l'application
   - Déploiement sur Cloud Run

5. **Configuration post-déploiement :**
   - Alertes de budget
   - Surveillance
   - Services système

## Workflow de déploiement

```bash
# 1. Vérifier les prérequis
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Déployer
python3 deploy.py --project-id YOUR_PROJECT_ID

# 3. Vérifier le déploiement
gcloud run services list
gcloud storage ls
```
