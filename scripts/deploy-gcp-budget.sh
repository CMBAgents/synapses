#!/bin/bash

# GCP Budget-Optimized Deployment Script
# Coût estimé: ~$5-15/mois au lieu de $70-140/mois

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}💰 GCP Budget-Optimized Deployment${NC}"
echo -e "${BLUE}===================================${NC}"

# Configuration optimisée pour les coûts
PROJECT_ID=""
REGION="us-central1"  # Région la moins chère
MEMORY="512Mi"        # Au lieu de 2Gi
CPU="1"               # Au lieu de 2
MAX_INSTANCES="5"     # Au lieu de 10
MIN_INSTANCES="0"     # Scale to zero pour économiser

# Collecte des informations
echo -e "${YELLOW}📋 Configuration optimisée pour les coûts...${NC}"

# Project ID
while true; do
    echo -e "${BLUE}Project ID GCP:${NC}"
    read -p "Project ID: " PROJECT_ID
    if [[ -n "$PROJECT_ID" ]]; then
        break
    fi
done

# GitHub Token (optionnel)
echo -e "${BLUE}Token GitHub (optionnel):${NC}"
read -p "Token GitHub (ghp_...): " GITHUB_TOKEN

# Configuration des buckets
CONTEXTS_BUCKET="${PROJECT_ID}-contexts"
STATIC_BUCKET="${PROJECT_ID}-static"

echo -e "${GREEN}✅ Configuration optimisée:${NC}"
echo -e "   Mémoire: $MEMORY (au lieu de 2Gi)"
echo -e "   CPU: $CPU (au lieu de 2)"
echo -e "   Instances max: $MAX_INSTANCES (au lieu de 10)"
echo -e "   Scale to zero: activé"

# Créer la configuration
cat > budget-config.json << EOF
{
  "project_id": "$PROJECT_ID",
  "region": "$REGION",
  "buckets": {
    "contexts": "$CONTEXTS_BUCKET",
    "static": "$STATIC_BUCKET"
  },
  "resources": {
    "memory": "$MEMORY",
    "cpu": "$CPU",
    "max_instances": $MAX_INSTANCES,
    "min_instances": $MIN_INSTANCES
  },
  "optimization": {
    "scale_to_zero": true,
    "budget_friendly": true,
    "estimated_cost": "5-15/mois"
  },
  "github": {
    "token": "$GITHUB_TOKEN"
  }
}
EOF

# Variables d'environnement optimisées
cat > .env.local << EOF
# GCP Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_BUCKET=$CONTEXTS_BUCKET
GOOGLE_CLOUD_STATIC_BUCKET=$STATIC_BUCKET
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json

# GitHub Configuration
GITHUB_TOKEN=$GITHUB_TOKEN

# Next.js Configuration
NEXT_PUBLIC_GCP_BUCKET=$CONTEXTS_BUCKET
NEXT_PUBLIC_GCP_STATIC_BUCKET=$STATIC_BUCKET
NODE_ENV=production

# Optimizations
NEXT_TELEMETRY_DISABLED=1
EOF

# Script de déploiement optimisé
cat > deploy-budget.sh << 'EOF'
#!/bin/bash

# Script de déploiement optimisé pour les coûts

set -e

# Charger la configuration
CONFIG_FILE="budget-config.json"
PROJECT_ID=$(jq -r '.project_id' "$CONFIG_FILE")
REGION=$(jq -r '.region' "$CONFIG_FILE")
MEMORY=$(jq -r '.resources.memory' "$CONFIG_FILE")
CPU=$(jq -r '.resources.cpu' "$CONFIG_FILE")
MAX_INSTANCES=$(jq -r '.resources.max_instances' "$CONFIG_FILE")
MIN_INSTANCES=$(jq -r '.resources.min_instances' "$CONFIG_FILE")

echo "💰 Déploiement optimisé pour les coûts..."
echo "Project ID: $PROJECT_ID"
echo "Ressources: $MEMORY, $CPU CPU, $MIN_INSTANCES-$MAX_INSTANCES instances"

# Vérifier gcloud
if ! gcloud config get-value project >/dev/null 2>&1; then
    echo "❌ gcloud non configuré. Exécutez: gcloud init"
    exit 1
fi

# Activer les APIs (gratuit)
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com

# Créer buckets (gratuit jusqu'à 5GB)
gsutil mb -l $REGION gs://$PROJECT_ID-contexts 2>/dev/null || true
gsutil mb -l $REGION gs://$PROJECT_ID-static 2>/dev/null || true

# Configurer CORS
cat > /tmp/cors.json << 'CORS_EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
CORS_EOF

gsutil cors set /tmp/cors.json gs://$PROJECT_ID-contexts
gsutil cors set /tmp/cors.json gs://$PROJECT_ID-static

# Créer service account (gratuit)
SERVICE_ACCOUNT="context-updater"
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create $SERVICE_ACCOUNT --display-name="Context Updater" 2>/dev/null || true

# Permissions minimales
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.objectAdmin"

# Credentials
gcloud iam service-accounts keys create gcp-credentials.json \
    --iam-account=$SERVICE_ACCOUNT_EMAIL 2>/dev/null || true

# Déployer avec configuration optimisée
gcloud run deploy cmbagent-info \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "GOOGLE_CLOUD_BUCKET=$PROJECT_ID-contexts" \
    --set-env-vars "GOOGLE_CLOUD_STATIC_BUCKET=$PROJECT_ID-static" \
    --set-env-vars "GITHUB_TOKEN=$GITHUB_TOKEN" \
    --memory=$MEMORY \
    --cpu=$CPU \
    --max-instances=$MAX_INSTANCES \
    --min-instances=$MIN_INSTANCES \
    --timeout=300 \
    --concurrency=80 \
    --service-account=$SERVICE_ACCOUNT_EMAIL

# Obtenir l'URL
SERVICE_URL=$(gcloud run services describe cmbagent-info --region=$REGION --format="value(status.url)")

echo "✅ Déploiement optimisé terminé!"
echo "🌐 URL: $SERVICE_URL"
echo "💰 Coût estimé: $5-15/mois"

# Configuration de l'automatisation légère
echo "🔄 Configuration de l'automatisation légère..."

# Cloud Function optimisée (gratuit jusqu'à 2M invocations/mois)
cat > /tmp/function-main.py << 'FUNC_EOF'
import functions_framework
import subprocess
import os

@functions_framework.http
def update_contexts(request):
    """Fonction optimisée pour les mises à jour."""
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/credentials.json'
    os.environ['GOOGLE_CLOUD_PROJECT'] = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
    os.environ['GOOGLE_CLOUD_BUCKET'] = os.environ.get('GOOGLE_CLOUD_BUCKET', '')
    
    try:
        # Exécution optimisée
        result = subprocess.run([
            'python', '-c', 
            'import sys; sys.path.append("/workspace"); from scripts.auto_update_contexts import AutoContextUpdater; updater = AutoContextUpdater(); updater.check_and_update_contexts()'
        ], capture_output=True, text=True, timeout=300)
        
        return {
            'status': 'success' if result.returncode == 0 else 'error',
            'stdout': result.stdout[-500:],  # Limiter la taille
            'stderr': result.stderr[-500:]
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
FUNC_EOF

# Déployer fonction optimisée
gcloud functions deploy context-updater \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --region $REGION \
    --source /tmp \
    --entry-point update_contexts \
    --timeout 300s \
    --memory 256Mi \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "GOOGLE_CLOUD_BUCKET=$PROJECT_ID-contexts"

# Scheduler (gratuit jusqu'à 3 jobs)
FUNCTION_URL=$(gcloud functions describe context-updater --region=$REGION --format="value(httpsTrigger.url)")

gcloud scheduler jobs create http context-update-job \
    --schedule="0 */6 * * *" \
    --uri="$FUNCTION_URL" \
    --http-method=POST \
    --location=$REGION \
    --description="Mise à jour contextes (toutes les 6h)"

echo "✅ Automatisation configurée (toutes les 6h au lieu de toutes les heures)"

# Nettoyage
rm -f /tmp/cors.json /tmp/function-main.py

echo ""
echo "💰 OPTIMISATIONS APPLIQUÉES:"
echo "   • Mémoire réduite: $MEMORY (au lieu de 2Gi)"
echo "   • CPU réduit: $CPU (au lieu de 2)"
echo "   • Instances max: $MAX_INSTANCES (au lieu de 10)"
echo "   • Scale to zero: activé"
echo "   • Fréquence: toutes les 6h (au lieu de toutes les heures)"
echo "   • Cloud Function: 256Mi (au lieu de 2Gi)"
echo ""
echo "📊 COÛTS ESTIMÉS:"
echo "   • Cloud Run: ~$2-8/mois"
echo "   • Cloud Storage: ~$1-3/mois (gratuit jusqu'à 5GB)"
echo "   • Cloud Functions: ~$1-2/mois (gratuit jusqu'à 2M invocations)"
echo "   • Cloud Scheduler: Gratuit (jusqu'à 3 jobs)"
echo "   • TOTAL: ~$4-13/mois"
EOF

chmod +x deploy-budget.sh

# Créer la documentation
cat > BUDGET_DEPLOYMENT.md << EOF
# 💰 Déploiement Optimisé pour les Coûts

## 🎯 Optimisations Appliquées

### Ressources Réduites
- **Mémoire**: $MEMORY (au lieu de 2Gi)
- **CPU**: $CPU (au lieu de 2)
- **Instances max**: $MAX_INSTANCES (au lieu de 10)
- **Scale to zero**: Activé

### Automatisation Optimisée
- **Fréquence**: Toutes les 6h (au lieu de toutes les heures)
- **Cloud Function**: 256Mi (au lieu de 2Gi)
- **Timeout**: 5 minutes (au lieu de 15)

## 📊 Coûts Estimés

| Service | Coût Estimé | Gratuit jusqu'à |
|---------|-------------|-----------------|
| Cloud Run | $2-8/mois | 2M requêtes/mois |
| Cloud Storage | $1-3/mois | 5GB/mois |
| Cloud Functions | $1-2/mois | 2M invocations/mois |
| Cloud Scheduler | Gratuit | 3 jobs |
| **TOTAL** | **$4-13/mois** | - |

## 🚀 Déploiement

\`\`\`bash
# Configuration
./scripts/deploy-gcp-budget.sh

# Déploiement
./deploy-budget.sh
\`\`\`

## ⚡ Performance

- **Démarrage à froid**: ~10-15 secondes
- **Requêtes chaudes**: <1 seconde
- **Disponibilité**: 99.9%+
- **Scale automatique**: 0-5 instances

## 🔄 Mises à jour

- **Automatique**: Toutes les 6h
- **Manuel**: \`curl -X POST FUNCTION_URL\`
- **Logs**: \`gcloud logs tail --project=$PROJECT_ID\`

## 💡 Conseils d'économie

1. **Surveiller l'usage**: Console GCP → Billing
2. **Alertes de budget**: Configurer des alertes
3. **Optimiser les contextes**: Compresser si nécessaire
4. **Cache local**: Utiliser le cache navigateur

## 🆘 Support

- **Logs**: \`gcloud logs tail --project=$PROJECT_ID\`
- **Health check**: \`curl SERVICE_URL/api/health\`
- **Coûts**: Console GCP → Billing → Reports
EOF

echo -e "${GREEN}✅ Configuration optimisée créée!${NC}"
echo -e "${BLUE}"
echo "=========================================="
echo "💰 CONFIGURATION OPTIMISÉE POUR LES COÛTS"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Ressources: $MEMORY, $CPU CPU, $MIN_INSTANCES-$MAX_INSTANCES instances"
echo "Fréquence: Toutes les 6h"
echo "Coût estimé: $4-13/mois (au lieu de $70-140/mois)"
echo ""
echo "📁 Fichiers créés:"
echo "  - budget-config.json"
echo "  - .env.local"
echo "  - deploy-budget.sh"
echo "  - BUDGET_DEPLOYMENT.md"
echo ""
echo "🚀 Déploiement:"
echo "  ./deploy-budget.sh"
echo "=========================================="
echo -e "${NC}" 