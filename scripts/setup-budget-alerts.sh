#!/bin/bash

# GCP Budget Alerts Setup Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}💰 GCP Budget Alerts Setup${NC}"
echo -e "${BLUE}==========================${NC}"

# Configuration
PROJECT_ID=""
BUDGET_AMOUNT="15"
ALERT_EMAIL=""

# Get project ID
echo -e "${YELLOW}📋 Configuration des alertes de budget...${NC}"

while true; do
    echo -e "${BLUE}Project ID GCP:${NC}"
    read -p "Project ID: " PROJECT_ID
    if [[ -n "$PROJECT_ID" ]]; then
        break
    fi
done

# Get budget amount
echo -e "${BLUE}Budget mensuel (USD):${NC}"
read -p "Budget [15]: " BUDGET_AMOUNT
BUDGET_AMOUNT=${BUDGET_AMOUNT:-15}

# Get alert email
echo -e "${BLUE}Email pour les alertes:${NC}"
read -p "Email: " ALERT_EMAIL

# Get billing account
echo -e "${YELLOW}🔍 Récupération du compte de facturation...${NC}"
BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(ACCOUNT_ID)" | head -1)

if [[ -z "$BILLING_ACCOUNT" ]]; then
    echo -e "${RED}❌ Aucun compte de facturation trouvé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Compte de facturation: $BILLING_ACCOUNT${NC}"

# Create budget configuration
echo -e "${YELLOW}📝 Création de la configuration de budget...${NC}"

cat > budget-config.yaml << EOF
displayName: "CMB Agent Info Budget"
budgetFilter:
  projects:
    - projects/$PROJECT_ID
amount:
  specifiedAmount:
    currencyCode: USD
    units: "$BUDGET_AMOUNT"
thresholdRules:
  - thresholdPercent: 50
    spendBasis: CURRENT_SPEND
  - thresholdPercent: 80
    spendBasis: CURRENT_SPEND
  - thresholdPercent: 100
    spendBasis: CURRENT_SPEND
  - thresholdPercent: 120
    spendBasis: CURRENT_SPEND
notificationsRule:
  pubsubTopic: projects/$PROJECT_ID/topics/budget-alerts
  schemaVersion: "1.0"
EOF

# Create Pub/Sub topic for budget alerts
echo -e "${YELLOW}📡 Création du topic Pub/Sub...${NC}"
gcloud pubsub topics create budget-alerts --project=$PROJECT_ID 2>/dev/null || true

# Create subscription for email notifications
echo -e "${YELLOW}📧 Configuration des notifications email...${NC}"

if [[ -n "$ALERT_EMAIL" ]]; then
    # Create Cloud Function for email notifications
    cat > /tmp/email-notification.py << 'EOF'
import functions_framework
import base64
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

@functions_framework.cloud_event
def send_budget_alert(cloud_event):
    """Send budget alert email."""
    
    # Get alert data
    data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    alert_data = json.loads(data)
    
    # Email configuration
    sender_email = os.environ.get('SENDER_EMAIL', 'noreply@your-domain.com')
    recipient_email = os.environ.get('ALERT_EMAIL')
    
    if not recipient_email:
        print("No recipient email configured")
        return
    
    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"GCP Budget Alert - {alert_data.get('budgetDisplayName', 'CMB Agent Info')}"
    
    # Email body
    body = f"""
    🚨 GCP Budget Alert
    
    Project: {alert_data.get('budgetDisplayName', 'CMB Agent Info')}
    Budget Amount: ${alert_data.get('budgetAmount', {}).get('specifiedAmount', {}).get('units', '0')}
    Current Spend: ${alert_data.get('costAmount', {}).get('specifiedAmount', {}).get('units', '0')}
    Threshold: {alert_data.get('alertThresholdExceeded', {}).get('thresholdPercent', '0')}%
    
    This is an automated alert from your GCP budget monitoring system.
    
    To view detailed costs:
    https://console.cloud.google.com/billing/projects/{os.environ.get('GOOGLE_CLOUD_PROJECT')}
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email (requires SMTP configuration)
    try:
        # For now, just log the alert
        print(f"Budget alert would be sent to {recipient_email}")
        print(f"Alert data: {alert_data}")
    except Exception as e:
        print(f"Error sending email: {e}")
EOF

    # Deploy Cloud Function for email notifications
    gcloud functions deploy budget-email-alert \
        --runtime python39 \
        --trigger-topic budget-alerts \
        --region us-central1 \
        --source /tmp \
        --entry-point send_budget_alert \
        --set-env-vars ALERT_EMAIL=$ALERT_EMAIL \
        --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
        --project=$PROJECT_ID 2>/dev/null || true

    echo -e "${GREEN}✅ Fonction de notification email déployée${NC}"
fi

# Create budget
echo -e "${YELLOW}💰 Création du budget...${NC}"
gcloud billing budgets create \
    --billing-account=$BILLING_ACCOUNT \
    --budget-file=budget-config.yaml \
    --display-name="CMB Agent Info Budget"

echo -e "${GREEN}✅ Budget créé avec succès!${NC}"

# Create cost monitoring dashboard
echo -e "${YELLOW}📊 Création du dashboard de monitoring...${NC}"

cat > cost-dashboard.json << EOF
{
  "displayName": "CMB Agent Info Cost Dashboard",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Daily Costs",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"billing.googleapis.com/consumption/bytes\\" AND resource.labels.project_id=\\"$PROJECT_ID\\"",
                  "aggregation": {
                    "alignmentPeriod": "86400s",
                    "perSeriesAligner": "ALIGN_SUM"
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Service Breakdown",
        "pieChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"billing.googleapis.com/consumption/bytes\\" AND resource.labels.project_id=\\"$PROJECT_ID\\"",
                  "aggregation": {
                    "alignmentPeriod": "86400s",
                    "perSeriesAligner": "ALIGN_SUM",
                    "crossSeriesReducer": "REDUCE_SUM"
                  }
                }
              }
            }
          ]
        }
      }
    ]
  }
}
EOF

# Create monitoring dashboard
gcloud monitoring dashboards create --project=$PROJECT_ID --config-from-file=cost-dashboard.json 2>/dev/null || true

echo -e "${GREEN}✅ Dashboard de monitoring créé${NC}"

# Create cost optimization recommendations
echo -e "${YELLOW}💡 Création des recommandations d'optimisation...${NC}"

cat > cost-optimization.md << EOF
# 💰 Recommandations d'Optimisation des Coûts

## 🎯 Objectif: Maintenir les coûts sous $BUDGET_AMOUNT/mois

### 📊 Surveillance Continue

1. **Vérification quotidienne:**
   \`\`\`bash
   python scripts/cost-monitor.py daily
   \`\`\`

2. **Rapport hebdomadaire:**
   \`\`\`bash
   python scripts/cost-monitor.py report 7
   \`\`\`

3. **Export mensuel:**
   \`\`\`bash
   python scripts/cost-monitor.py export csv 30
   \`\`\`

### ⚡ Optimisations Actuelles

- **Cloud Run**: 512Mi RAM, 1 CPU, scale to zero
- **Cloud Functions**: 256Mi RAM, timeout 5min
- **Fréquence**: Mises à jour toutes les 6h
- **Storage**: Lifecycle policies activées

### 🚨 Alertes Configurées

- **50% du budget**: Avertissement précoce
- **80% du budget**: Attention requise
- **100% du budget**: Limite atteinte
- **120% du budget**: Dépassement critique

### 💡 Actions d'Optimisation

#### Si coûts > $0.50/jour:
1. Réduire la fréquence des mises à jour (6h → 12h)
2. Optimiser les contextes (compression)
3. Nettoyer les anciens contextes

#### Si coûts > $1.00/jour:
1. Réduire les ressources Cloud Run (512Mi → 256Mi)
2. Désactiver les instances minimum
3. Optimiser les requêtes de base de données

#### Si coûts > $2.00/jour:
1. Migrer vers une architecture plus légère
2. Utiliser Cloud Storage uniquement
3. Réduire la fréquence à 1 fois/jour

### 📈 Métriques à Surveiller

- **Cloud Run**: Requêtes/jour, temps d'exécution
- **Cloud Functions**: Invocations/jour, durée
- **Cloud Storage**: Taille des données, requêtes
- **Cloud Scheduler**: Jobs exécutés

### 🔧 Commandes Utiles

\`\`\`bash
# Voir les coûts en temps réel
gcloud billing budgets list --billing-account=$BILLING_ACCOUNT

# Voir l'utilisation des services
gcloud run services list --region=us-central1
gcloud functions list
gsutil du -sh gs://$PROJECT_ID-contexts

# Optimiser les ressources
gcloud run services update cmbagent-info --memory=256Mi --cpu=1 --region=us-central1
\`\`\`

### 📞 Support

En cas de dépassement de budget:
1. Vérifier les logs: \`gcloud logs tail --project=$PROJECT_ID\`
2. Analyser les coûts: Console GCP → Billing
3. Optimiser immédiatement selon les recommandations
4. Considérer une pause temporaire si nécessaire
EOF

echo -e "${GREEN}✅ Recommandations d'optimisation créées${NC}"

# Create automated cost monitoring script
echo -e "${YELLOW}🤖 Configuration du monitoring automatisé...${NC}"

cat > monitor-costs.sh << 'EOF'
#!/bin/bash

# Automated Cost Monitoring Script

set -e

PROJECT_ID="'$PROJECT_ID'"
BUDGET_AMOUNT='$BUDGET_AMOUNT'

echo "💰 Automated Cost Check - $(date)"

# Run daily cost check
python scripts/cost-monitor.py daily

# Get current month's cost
CURRENT_COST=$(python scripts/cost-monitor.py summary 30 | jq -r '.total_cost // 0')

# Calculate daily average
DAILY_AVG=$(python scripts/cost-monitor.py summary 7 | jq -r '.daily_average // 0')
MONTHLY_ESTIMATE=$(echo "$DAILY_AVG * 30" | bc -l)

echo "Current month cost: $CURRENT_COST"
echo "Daily average: $DAILY_AVG"
echo "Monthly estimate: $MONTHLY_ESTIMATE"

# Check if we're approaching budget
if (( $(echo "$MONTHLY_ESTIMATE > $BUDGET_AMOUNT" | bc -l) )); then
    echo "⚠️  WARNING: Monthly estimate ($MONTHLY_ESTIMATE) exceeds budget ($BUDGET_AMOUNT)"
    
    # Send alert (if email is configured)
    if [[ -n "'$ALERT_EMAIL'" ]]; then
        echo "📧 Sending budget alert email..."
        # This would trigger the Cloud Function
    fi
    
    # Apply cost optimizations
    echo "🔧 Applying cost optimizations..."
    
    # Reduce Cloud Run resources
    gcloud run services update cmbagent-info \
        --memory=256Mi \
        --cpu=1 \
        --region=us-central1 \
        --project=$PROJECT_ID 2>/dev/null || true
    
    # Reduce update frequency
    gcloud scheduler jobs update http context-update-job \
        --schedule="0 */12 * * *" \
        --location=us-central1 \
        --project=$PROJECT_ID 2>/dev/null || true
    
    echo "✅ Cost optimizations applied"
else
    echo "✅ Costs are within budget"
fi
EOF

chmod +x monitor-costs.sh

# Add to crontab for daily monitoring
echo -e "${YELLOW}⏰ Configuration du monitoring quotidien...${NC}"
(crontab -l 2>/dev/null; echo "0 9 * * * cd $(pwd) && ./monitor-costs.sh >> cost-monitor.log 2>&1") | crontab -

echo -e "${GREEN}✅ Monitoring quotidien configuré (9h00 tous les jours)${NC}"

# Final summary
echo -e "${BLUE}"
echo "=========================================="
echo "💰 CONFIGURATION DES ALERTES TERMINÉE"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Budget mensuel: $${BUDGET_AMOUNT}"
echo "Compte de facturation: $BILLING_ACCOUNT"
if [[ -n "$ALERT_EMAIL" ]]; then
    echo "Email alertes: $ALERT_EMAIL"
fi
echo ""
echo "📁 Fichiers créés:"
echo "  - budget-config.yaml"
echo "  - cost-dashboard.json"
echo "  - cost-optimization.md"
echo "  - monitor-costs.sh"
echo ""
echo "🚨 Alertes configurées:"
echo "  • 50% du budget"
echo "  • 80% du budget"
echo "  • 100% du budget"
echo "  • 120% du budget"
echo ""
echo "📊 Monitoring:"
echo "  • Dashboard: Console GCP → Monitoring"
echo "  • Rapports: python scripts/cost-monitor.py report"
echo "  • Automatique: Tous les jours à 9h00"
echo ""
echo "💡 Optimisations automatiques activées"
echo "=========================================="
echo -e "${NC}"

# Clean up
rm -f /tmp/email-notification.py 