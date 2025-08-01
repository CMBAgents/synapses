# 📋 Checklist de Déploiement GCP

## 🔧 Prérequis Système

### ✅ Google Cloud CLI
```bash
# Vérifier l'installation
gcloud --version

# Si non installé (macOS)
brew install google-cloud-sdk
```

### ✅ Node.js et npm
```bash
# Vérifier les versions
node --version  # >= 16
npm --version   # >= 8
```

### ✅ Python 3
```bash
# Vérifier la version
python3 --version  # >= 3.8
```

### ✅ Git
```bash
# Vérifier l'installation
git --version
```

## 🚀 Configuration Initiale

### ✅ Compte GCP
- [ ] Compte Google Cloud créé
- [ ] Facturation activée
- [ ] Projet GCP créé

### ✅ Authentification
```bash
# Initialiser gcloud
gcloud init

# S'authentifier
gcloud auth login
gcloud auth application-default login
```

## 📝 Informations Requises

### ✅ Project ID GCP
- **Format**: lettres minuscules, chiffres, tirets (6-30 caractères)
- **Exemple**: `mon-projet-cmbagent-123`
- **Où le trouver**: Console GCP → Sélecteur de projet

### ✅ Région GCP
- **Recommandé**: `us-central1` (coût optimal)
- **Alternatives**: 
  - `europe-west1` (Europe)
  - `asia-northeast1` (Asie)

### ✅ Token GitHub (optionnel mais recommandé)
- **URL**: https://github.com/settings/tokens
- **Permissions**: `repo`, `read:org`
- **Format**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### ✅ Configuration des ressources
- **Mémoire**: `2Gi` (recommandé)
- **CPU**: `2` (recommandé)
- **Instances max**: `10` (recommandé)

### ✅ Fréquence d'automatisation
- **Recommandé**: `1h` (toutes les heures)
- **Alternatives**: `30m`, `2h`, `6h`, `12h`

### ✅ Domaine personnalisé (optionnel)
- **Format**: `cmbagent.votre-domaine.com`
- **DNS**: Pointer vers Cloud Run

## 🔄 Configuration Automatisée

### ✅ Lancer le script de configuration
```bash
# Rendre exécutable
chmod +x scripts/setup-deployment.sh

# Lancer la configuration interactive
./scripts/setup-deployment.sh
```

### ✅ Vérifier les fichiers générés
- [ ] `deployment-config.json` - Configuration principale
- [ ] `.env.local` - Variables d'environnement
- [ ] `cloud-config.json` - Configuration cloud
- [ ] `deploy-custom.sh` - Script de déploiement
- [ ] `DEPLOYMENT_INFO.md` - Documentation

## 🚀 Déploiement

### ✅ Pré-déploiement
```bash
# Vérifier la configuration
gcloud config get-value project

# Activer les APIs requises
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
```

### ✅ Déploiement principal
```bash
# Déployer l'application
./deploy-custom.sh
```

### ✅ Vérification post-déploiement
```bash
# Obtenir l'URL du service
gcloud run services describe cmbagent-info --region=us-central1 --format="value(status.url)"

# Tester l'endpoint de santé
curl https://YOUR_SERVICE_URL/api/health
```

## 🔧 Configuration Avancée

### ✅ Buckets de stockage
```bash
# Vérifier les buckets créés
gsutil ls gs://YOUR_PROJECT_ID-contexts
gsutil ls gs://YOUR_PROJECT_ID-static

# Configurer CORS
gsutil cors set cors.json gs://YOUR_PROJECT_ID-contexts
gsutil cors set cors.json gs://YOUR_PROJECT_ID-static
```

### ✅ Service accounts
```bash
# Vérifier les permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:context-updater"
```

### ✅ Cloud Functions
```bash
# Vérifier la fonction de mise à jour
gcloud functions describe context-updater --region=us-central1

# Tester manuellement
curl -X POST https://YOUR_FUNCTION_URL
```

### ✅ Cloud Scheduler
```bash
# Vérifier le job programmé
gcloud scheduler jobs describe context-update-job --location=us-central1
```

## 📊 Monitoring et Logs

### ✅ Logs en temps réel
```bash
# Logs Cloud Run
gcloud logs tail --project=YOUR_PROJECT_ID --filter="resource.type=cloud_run_revision"

# Logs Cloud Functions
gcloud logs tail --project=YOUR_PROJECT_ID --filter="resource.type=cloud_function"
```

### ✅ Monitoring
- [ ] Console GCP: https://console.cloud.google.com/run/detail/us-central1/cmbagent-info
- [ ] Logs: https://console.cloud.google.com/logs
- [ ] Monitoring: https://console.cloud.google.com/monitoring

### ✅ Alertes (optionnel)
```bash
# Créer une politique d'alerte
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

## 🔒 Sécurité

### ✅ IAM et permissions
- [ ] Service account avec permissions minimales
- [ ] Buckets avec accès restreint
- [ ] HTTPS obligatoire

### ✅ Variables d'environnement
- [ ] Pas de secrets dans le code
- [ ] Utilisation de Secret Manager (optionnel)

### ✅ CORS configuré
- [ ] Buckets avec CORS approprié
- [ ] Headers de sécurité

## 💰 Optimisation des coûts

### ✅ Lifecycle policies
```bash
# Appliquer la politique de cycle de vie
gsutil lifecycle set lifecycle.json gs://YOUR_PROJECT_ID-contexts
```

### ✅ Scaling configuré
- [ ] Minimum instances: 0
- [ ] Maximum instances: 10
- [ ] Timeout: 900s

### ✅ Monitoring des coûts
- [ ] Budget alerts configurés
- [ ] Dashboard de coûts activé

## 🧪 Tests

### ✅ Tests fonctionnels
```bash
# Test de l'endpoint de santé
curl -f https://YOUR_SERVICE_URL/api/health

# Test de génération de contexte
python scripts/auto-update-contexts.py once

# Test de synchronisation cloud
python scripts/cloud-sync-contexts.py
```

### ✅ Tests de charge (optionnel)
```bash
# Test simple avec ab (Apache Bench)
ab -n 100 -c 10 https://YOUR_SERVICE_URL/
```

## 📚 Documentation

### ✅ Fichiers de documentation
- [ ] `DEPLOYMENT_INFO.md` - Informations spécifiques
- [ ] `gcp-deployment-guide.md` - Guide complet
- [ ] `CONTEXT_GENERATION_GUIDE.md` - Guide des contextes

### ✅ URLs importantes
- [ ] Service URL: `https://YOUR_SERVICE_URL`
- [ ] Console GCP: `https://console.cloud.google.com`
- [ ] Documentation: `DEPLOYMENT_INFO.md`

## 🔄 Maintenance

### ✅ Mises à jour automatiques
- [ ] Cloud Function fonctionne
- [ ] Cloud Scheduler actif
- [ ] Logs sans erreurs

### ✅ Sauvegarde
- [ ] Contextes sauvegardés dans Cloud Storage
- [ ] Configuration sauvegardée
- [ ] Scripts de restauration

### ✅ Monitoring continu
- [ ] Alertes configurées
- [ ] Logs surveillés
- [ ] Métriques suivies

## 🆘 Support

### ✅ En cas de problème
1. **Vérifier les logs**: `gcloud logs tail --project=YOUR_PROJECT_ID`
2. **Tester l'endpoint de santé**: `curl https://YOUR_SERVICE_URL/api/health`
3. **Vérifier les permissions IAM**
4. **Consulter la documentation**: `DEPLOYMENT_INFO.md`
5. **Vérifier la facturation GCP**

### ✅ Commandes utiles
```bash
# Redémarrer le service
gcloud run services update cmbagent-info --region=us-central1

# Voir les variables d'environnement
gcloud run services describe cmbagent-info --region=us-central1 --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"

# Mettre à jour les contextes manuellement
python scripts/auto-update-contexts.py once
```

---

## ✅ Checklist Finale

- [ ] Tous les prérequis installés
- [ ] Configuration GCP complète
- [ ] Application déployée et accessible
- [ ] Automatisation configurée
- [ ] Monitoring activé
- [ ] Tests passés
- [ ] Documentation à jour
- [ ] Support configuré

**🎉 Votre application est prête pour la production !** 