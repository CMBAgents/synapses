#!/bin/bash

# Interactive GCP Deployment Setup Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Configuration Interactive pour le Déploiement GCP${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to validate input
validate_input() {
    local input="$1"
    local name="$2"
    if [[ -z "$input" ]]; then
        echo -e "${RED}❌ $name ne peut pas être vide${NC}"
        return 1
    fi
    return 0
}

# Function to validate project ID format
validate_project_id() {
    local project_id="$1"
    if [[ ! "$project_id" =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ ]]; then
        echo -e "${RED}❌ Project ID invalide. Format: lettres minuscules, chiffres, tirets (6-30 caractères)${NC}"
        return 1
    fi
    return 0
}

# Function to validate GitHub token
validate_github_token() {
    local token="$1"
    if [[ -n "$token" && ! "$token" =~ ^ghp_[a-zA-Z0-9]{36}$ ]]; then
        echo -e "${YELLOW}⚠️ Token GitHub invalide. Format attendu: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx${NC}"
        return 1
    fi
    return 0
}

echo -e "${YELLOW}📋 Collecte des informations de configuration...${NC}"

# 1. Project ID
while true; do
    echo -e "${BLUE}1. Project ID GCP:${NC}"
    echo -e "   Format: lettres minuscules, chiffres, tirets (ex: mon-projet-123)"
    read -p "   Project ID: " PROJECT_ID
    
    if validate_input "$PROJECT_ID" "Project ID" && validate_project_id "$PROJECT_ID"; then
        break
    fi
done

# 2. Region
echo -e "${BLUE}2. Région GCP:${NC}"
echo -e "   Options recommandées:"
echo -e "   - us-central1 (États-Unis, coût optimal)"
echo -e "   - europe-west1 (Europe, latence réduite)"
echo -e "   - asia-northeast1 (Asie, latence réduite)"
read -p "   Région [us-central1]: " REGION
REGION=${REGION:-us-central1}

# 3. GitHub Token (optionnel)
echo -e "${BLUE}3. Token GitHub (optionnel):${NC}"
echo -e "   Permet d'augmenter les limites d'API GitHub"
echo -e "   Créer un token: https://github.com/settings/tokens"
echo -e "   Permissions: repo, read:org"
read -p "   Token GitHub (ghp_...): " GITHUB_TOKEN

if [[ -n "$GITHUB_TOKEN" ]]; then
    if ! validate_github_token "$GITHUB_TOKEN"; then
        echo -e "${YELLOW}   Continuer sans token GitHub ? (y/n):${NC}"
        read -p "   " continue_without_token
        if [[ "$continue_without_token" != "y" ]]; then
            exit 1
        fi
        GITHUB_TOKEN=""
    fi
fi

# 4. Configuration des buckets
echo -e "${BLUE}4. Configuration des buckets:${NC}"
CONTEXTS_BUCKET="${PROJECT_ID}-contexts"
STATIC_BUCKET="${PROJECT_ID}-static"

echo -e "   Bucket contextes: ${GREEN}gs://$CONTEXTS_BUCKET${NC}"
echo -e "   Bucket statique: ${GREEN}gs://$STATIC_BUCKET${NC}"

# 5. Configuration des ressources
echo -e "${BLUE}5. Configuration des ressources:${NC}"
echo -e "   Mémoire Cloud Run (1Gi, 2Gi, 4Gi, 8Gi)"
read -p "   Mémoire [2Gi]: " MEMORY
MEMORY=${MEMORY:-2Gi}

echo -e "   CPU Cloud Run (1, 2, 4, 8)"
read -p "   CPU [2]: " CPU
CPU=${CPU:-2}

echo -e "   Instances max Cloud Run (1-100)"
read -p "   Instances max [10]: " MAX_INSTANCES
MAX_INSTANCES=${MAX_INSTANCES:-10}

# 6. Configuration de l'automatisation
echo -e "${BLUE}6. Configuration de l'automatisation:${NC}"
echo -e "   Fréquence de vérification des mises à jour"
echo -e "   Options: 15m, 30m, 1h, 2h, 6h, 12h, 1d"
read -p "   Fréquence [1h]: " UPDATE_FREQUENCY
UPDATE_FREQUENCY=${UPDATE_FREQUENCY:-1h}

# 7. Configuration du domaine (optionnel)
echo -e "${BLUE}7. Domaine personnalisé (optionnel):${NC}"
echo -e "   Exemple: cmbagent.votre-domaine.com"
read -p "   Domaine: " CUSTOM_DOMAIN

# 8. Configuration de monitoring
echo -e "${BLUE}8. Configuration du monitoring:${NC}"
echo -e "   Email pour les alertes (optionnel)"
read -p "   Email: " ALERT_EMAIL

# Génération des fichiers de configuration
echo -e "${YELLOW}📝 Génération des fichiers de configuration...${NC}"

# Créer le fichier de configuration principal
cat > deployment-config.json << EOF
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
    "max_instances": $MAX_INSTANCES
  },
  "automation": {
    "update_frequency": "$UPDATE_FREQUENCY"
  },
  "github": {
    "token": "$GITHUB_TOKEN"
  },
  "domain": {
    "custom": "$CUSTOM_DOMAIN"
  },
  "monitoring": {
    "alert_email": "$ALERT_EMAIL"
  }
}
EOF

# Créer le fichier .env.local
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

# Application Configuration
NEXT_PUBLIC_APP_URL=https://$CUSTOM_DOMAIN
EOF

# Mettre à jour cloud-config.json
cat > cloud-config.json << EOF
{
  "provider": "gcp",
  "bucket_name": "$CONTEXTS_BUCKET",
  "region": "$REGION",
  "project_id": "$PROJECT_ID",
  "static_bucket": "$STATIC_BUCKET",
  "sync_enabled": true,
  "backup_enabled": true,
  "credentials_file": "gcp-credentials.json",
  "github_token": "$GITHUB_TOKEN"
}
EOF

# Créer le script de déploiement personnalisé
cat > deploy-custom.sh << 'EOF'
#!/bin/bash

# Script de déploiement personnalisé généré automatiquement

set -e

# Charger la configuration
CONFIG_FILE="deployment-config.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Fichier de configuration $CONFIG_FILE non trouvé"
    exit 1
fi

# Extraire les valeurs
PROJECT_ID=$(jq -r '.project_id' "$CONFIG_FILE")
REGION=$(jq -r '.region' "$CONFIG_FILE")
CONTEXTS_BUCKET=$(jq -r '.buckets.contexts' "$CONFIG_FILE")
STATIC_BUCKET=$(jq -r '.buckets.static' "$CONFIG_FILE")
MEMORY=$(jq -r '.resources.memory' "$CONFIG_FILE")
CPU=$(jq -r '.resources.cpu' "$CONFIG_FILE")
MAX_INSTANCES=$(jq -r '.resources.max_instances' "$CONFIG_FILE")
UPDATE_FREQUENCY=$(jq -r '.automation.update_frequency' "$CONFIG_FILE")
GITHUB_TOKEN=$(jq -r '.github.token' "$CONFIG_FILE")
CUSTOM_DOMAIN=$(jq -r '.domain.custom' "$CONFIG_FILE")

echo "🚀 Déploiement avec configuration personnalisée..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Buckets: $CONTEXTS_BUCKET, $STATIC_BUCKET"

# Vérifier que gcloud est configuré
if ! gcloud config get-value project >/dev/null 2>&1; then
    echo "❌ gcloud non configuré. Exécutez: gcloud init"
    exit 1
fi

# Déployer avec les paramètres personnalisés
gcloud run deploy cmbagent-info \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "GOOGLE_CLOUD_BUCKET=$CONTEXTS_BUCKET" \
    --set-env-vars "GOOGLE_CLOUD_STATIC_BUCKET=$STATIC_BUCKET" \
    --set-env-vars "GITHUB_TOKEN=$GITHUB_TOKEN" \
    --memory="$MEMORY" \
    --cpu="$CPU" \
    --max-instances="$MAX_INSTANCES" \
    --timeout=900

echo "✅ Déploiement terminé!"
EOF

chmod +x deploy-custom.sh

# Créer le fichier de documentation
cat > DEPLOYMENT_INFO.md << EOF
# 📋 Informations de Déploiement

## Configuration Générée

- **Project ID**: $PROJECT_ID
- **Region**: $REGION
- **Buckets**: 
  - Contextes: gs://$CONTEXTS_BUCKET
  - Statique: gs://$STATIC_BUCKET
- **Ressources**: $MEMORY, $CPU CPU, max $MAX_INSTANCES instances
- **Fréquence mise à jour**: $UPDATE_FREQUENCY

## Fichiers Créés

- \`deployment-config.json\` - Configuration principale
- \`.env.local\` - Variables d'environnement
- \`cloud-config.json\` - Configuration cloud
- \`deploy-custom.sh\` - Script de déploiement personnalisé

## Étapes Suivantes

1. **Initialiser GCP:**
   \`\`\`bash
   gcloud init
   gcloud config set project $PROJECT_ID
   \`\`\`

2. **Déployer:**
   \`\`\`bash
   ./deploy-custom.sh
   \`\`\`

3. **Configurer le domaine (optionnel):**
   \`\`\`bash
   gcloud run domain-mappings create --service=cmbagent-info --domain=$CUSTOM_DOMAIN --region=$REGION
   \`\`\`

## Monitoring

- **Logs**: \`gcloud logs tail --project=$PROJECT_ID\`
- **Console**: https://console.cloud.google.com/run/detail/$REGION/cmbagent-info
- **Health Check**: https://YOUR_SERVICE_URL/api/health

## Coûts Estimés

- **Cloud Run**: ~$5-20/mois (selon l'usage)
- **Cloud Storage**: ~$1-5/mois (selon la taille des contextes)
- **Cloud Functions**: ~$1-3/mois (mises à jour automatiques)
- **Total estimé**: ~$7-28/mois

## Support

En cas de problème:
1. Vérifier les logs: \`gcloud logs tail --project=$PROJECT_ID\`
2. Tester l'endpoint de santé
3. Vérifier les permissions IAM
4. Consulter la documentation: \`gcp-deployment-guide.md\`
EOF

echo -e "${GREEN}✅ Configuration terminée!${NC}"
echo -e "${BLUE}"
echo "=========================================="
echo "📋 RÉSUMÉ DE LA CONFIGURATION"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Buckets: $CONTEXTS_BUCKET, $STATIC_BUCKET"
echo "Ressources: $MEMORY, $CPU CPU, max $MAX_INSTANCES instances"
echo "Fréquence mise à jour: $UPDATE_FREQUENCY"
if [[ -n "$CUSTOM_DOMAIN" ]]; then
    echo "Domaine: $CUSTOM_DOMAIN"
fi
if [[ -n "$ALERT_EMAIL" ]]; then
    echo "Email alertes: $ALERT_EMAIL"
fi
echo ""
echo "📁 Fichiers créés:"
echo "  - deployment-config.json"
echo "  - .env.local"
echo "  - cloud-config.json"
echo "  - deploy-custom.sh"
echo "  - DEPLOYMENT_INFO.md"
echo ""
echo "🚀 Prochaines étapes:"
echo "  1. gcloud init"
echo "  2. gcloud config set project $PROJECT_ID"
echo "  3. ./deploy-custom.sh"
echo "=========================================="
echo -e "${NC}" 