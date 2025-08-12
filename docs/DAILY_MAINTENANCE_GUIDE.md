# Guide de Maintenance Quotidienne

Ce guide explique comment utiliser le système de maintenance automatique pour maintenir à jour les données du site CMB Agent Info.

## Vue d'ensemble

Le système de maintenance quotidienne automatise les tâches suivantes :

1. **Récupération des données** : Télécharge les dernières informations sur les librairies depuis ASCL
2. **Mise à jour des métadonnées** : Compare et met à jour les fichiers JSON avec les nouvelles librairies
3. **Génération de contextes** : Crée ou met à jour les fichiers de contexte pour les librairies
4. **Nettoyage** : Supprime les repositories temporaires clonés

## Structure des fichiers

```
scripts/
├── daily_maintenance.py           # Script principal de maintenance
├── schedule_daily_maintenance.py  # Planificateur automatique
└── setup_maintenance_service.sh   # Installation du service systemd

logs/
├── daily_maintenance.log         # Logs de la maintenance
└── scheduler.log                 # Logs du planificateur
```

## Installation et Configuration

### 1. Prérequis

```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Installer contextmaker (remplacez par votre méthode d'installation)
pip install contextmaker

# S'assurer que git est installé
git --version
```

### 2. Permissions

```bash
# Rendre les scripts exécutables
chmod +x scripts/daily_maintenance.py
chmod +x scripts/schedule_daily_maintenance.py
chmod +x scripts/setup_maintenance_service.sh
```

### 3. Test manuel

```bash
# Tester la maintenance manuellement
cd /path/to/cmbagent-info
python scripts/daily_maintenance.py
```

## Utilisation

### Option 1: Exécution manuelle

```bash
# Maintenance ponctuelle
python scripts/daily_maintenance.py
```

### Option 2: Planificateur Python

```bash
# Démarrer le planificateur (maintenance à 2h00 chaque jour)
python scripts/schedule_daily_maintenance.py
```

### Option 3: Service systemd (recommandé pour production)

```bash
# Installer et configurer le service
sudo bash scripts/setup_maintenance_service.sh

# Vérifier le statut
sudo systemctl status cmbagent-maintenance

# Voir les logs en temps réel
sudo journalctl -u cmbagent-maintenance -f
```

## Configuration

### Modifier l'heure de maintenance

Éditez `scripts/schedule_daily_maintenance.py` :

```python
MAINTENANCE_TIME = "03:30"  # Format HH:MM
```

### Personnaliser les mots-clés de filtrage

Éditez `scripts/daily_maintenance.py`, méthode `_filter_astronomy_repos` :

```python
keywords = [
    "astro", "astropy", "healpy", "photutils", 
    # Ajoutez vos mots-clés ici
]
```

### Ajuster les timeouts

Dans `daily_maintenance.py` :

```python
# Timeout pour le clonage Git
timeout=300  # 5 minutes

# Timeout pour contextmaker  
timeout=300  # 5 minutes
```

## Fonctionnement détaillé

### Étape 1: Récupération des données

1. Télécharge les données depuis `https://ascl.net/code/json`
2. Extrait les URLs GitHub avec regex
3. Récupère le nombre d'étoiles en parallèle (4 workers)
4. Filtre selon les mots-clés astronomie/cosmologie
5. Sélectionne le top 100 par nombre d'étoiles

### Étape 2: Mise à jour du JSON

1. Compare les nouvelles librairies avec `app/data/astronomy-libraries.json`
2. Identifie les nouvelles librairies et celles supprimées
3. Préserve les statuts de contexte existants
4. Met à jour le fichier JSON avec les nouvelles données

### Étape 3: Gestion des contextes

Pour chaque librairie :

- **Nouvelle librairie** : Génère un contexte si `hasContextFile = false`
- **Librairie existante** : Vérifie les commits du dernier mois via l'API GitHub
- **Commits récents détectés** : Régénère le contexte

Le processus pour chaque contexte :
1. Clone le repository en `temp/repos/`
2. Exécute `contextmaker package_name --output path --input-path temp_dir`
3. Met à jour le JSON avec `hasContextFile = true`
4. Nettoie le repository temporaire

### Étape 4: Nettoyage

Supprime tous les repositories clonés dans `temp/repos/`

## Monitoring et dépannage

### Consulter les logs

```bash
# Logs de maintenance
tail -f logs/daily_maintenance.log

# Logs du planificateur
tail -f logs/scheduler.log

# Logs du service systemd
sudo journalctl -u cmbagent-maintenance -f
```

### Erreurs communes

#### contextmaker non trouvé
```bash
❌ Erreur: contextmaker n'est pas installé ou disponible
```
**Solution** : Installer contextmaker avec `pip install contextmaker`

#### Erreur de permissions
```bash
❌ Permission denied
```
**Solution** : Vérifier les permissions des dossiers et fichiers

#### Timeout de clonage
```bash
❌ Erreur clonage: timeout
```
**Solution** : Vérifier la connexion internet ou augmenter le timeout

#### API Rate limiting GitHub
```bash
❌ API rate limit exceeded  
```
**Solution** : Attendre ou configurer un token GitHub pour des limites plus élevées

### Vérification de l'état

```bash
# Vérifier les fichiers générés
ls -la app/data/astronomy-libraries.json
ls -la public/context/astronomy/

# Vérifier la date de dernière mise à jour
grep "last_updated" app/data/astronomy-libraries.json
```

## Personnalisation

### Ajouter d'autres domaines

1. Dupliquer la logique pour le domaine `finance`
2. Créer les filtres appropriés
3. Ajuster les chemins de fichiers

### Modifier la fréquence

Pour une maintenance bi-quotidienne, éditez `schedule_daily_maintenance.py` :

```python
schedule.every(12).hours.do(run_daily_maintenance)
```

### Ajouter des notifications

Ajoutez dans `daily_maintenance.py` après la maintenance :

```python
# Envoyer email/Slack/Discord notification
send_notification(success, stats)
```

## Sécurité

- Le service systemd s'exécute avec l'utilisateur `www-data`
- Les logs sont accessibles uniquement aux utilisateurs autorisés
- Aucune donnée sensible n'est stockée dans les logs
- Les repositories temporaires sont nettoyés après usage

## Performances

- **Durée typique** : 10-30 minutes selon le nombre de librairies
- **Ressources** : ~500MB RAM pendant l'exécution
- **Réseau** : ~100MB de téléchargement (clonages Git)
- **Stockage** : ~50MB de logs par mois

## Support

En cas de problème :

1. Consulter les logs détaillés
2. Tester manuellement chaque étape
3. Vérifier les prérequis et permissions
4. Redémarrer le service si nécessaire

```bash
sudo systemctl restart cmbagent-maintenance
```
