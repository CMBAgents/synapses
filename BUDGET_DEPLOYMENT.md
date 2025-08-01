# 💰 Déploiement Optimisé pour les Coûts

## 🎯 Optimisations Appliquées

### Ressources Réduites
- **Mémoire**: 512Mi (au lieu de 2Gi)
- **CPU**: 1 (au lieu de 2)
- **Instances max**: 5 (au lieu de 10)
- **Scale to zero**: Activé

### Automatisation Optimisée
- **Fréquence**: Toutes les 6h (au lieu de toutes les heures)
- **Cloud Function**: 256Mi (au lieu de 2Gi)
- **Timeout**: 5 minutes (au lieu de 15)

## 📊 Coûts Estimés

| Service | Coût Estimé | Gratuit jusqu'à |
|---------|-------------|-----------------|
| Cloud Run | -8/mois | 2M requêtes/mois |
| Cloud Storage | -3/mois | 5GB/mois |
| Cloud Functions | -2/mois | 2M invocations/mois |
| Cloud Scheduler | Gratuit | 3 jobs |
| **TOTAL** | **-13/mois** | - |

## 🚀 Déploiement

```bash
# Configuration
./scripts/deploy-gcp-budget.sh

# Déploiement
./deploy-budget.sh
```

## ⚡ Performance

- **Démarrage à froid**: ~10-15 secondes
- **Requêtes chaudes**: <1 seconde
- **Disponibilité**: 99.9%+
- **Scale automatique**: 0-5 instances

## 🔄 Mises à jour

- **Automatique**: Toutes les 6h
- **Manuel**: `curl -X POST FUNCTION_URL`
- **Logs**: `gcloud logs tail --project=cmbagent-info`

## 💡 Conseils d'économie

1. **Surveiller l'usage**: Console GCP → Billing
2. **Alertes de budget**: Configurer des alertes
3. **Optimiser les contextes**: Compresser si nécessaire
4. **Cache local**: Utiliser le cache navigateur

## 🆘 Support

- **Logs**: `gcloud logs tail --project=cmbagent-info`
- **Health check**: `curl SERVICE_URL/api/health`
- **Coûts**: Console GCP → Billing → Reports
