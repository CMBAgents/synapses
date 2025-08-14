# 🔄 Maintenance Scripts

Scripts de maintenance automatique et génération de contextes.

## Scripts

### `maintenance.py`
Script de maintenance simplifié qui remplace 3 scripts redondants.

**Fonctionnalités :**
- Maintenance quotidienne des bibliothèques
- Génération des contextes manquants
- Mise à jour automatique de la configuration
- Nettoyage automatique

**Utilisation :**
```bash
# Maintenance complète (avec récupération ASCL)
python3 maintenance.py

# Maintenance rapide (sans récupération ASCL)
python3 maintenance.py --quick
```

### `generate-missing-contexts.py`
Génère les contextes manquants pour un domaine spécifique.

**Fonctionnalités :**
- Détection des contextes manquants
- Génération automatique avec contextmaker
- Mise à jour des métadonnées

**Utilisation :**
```bash
# Génération pour astronomy
python3 generate-missing-contexts.py --domain astro

# Génération pour finance
python3 generate-missing-contexts.py --domain finance
```

### `generate-contexts-with-clone.py`
Génère les contextes avec clonage Git des repositories.

**Fonctionnalités :**
- Clonage automatique des repositories
- Génération de contexte avec contextmaker
- Nettoyage des repositories temporaires

### `generate-and-sync-all.py`
Génération et synchronisation complète.

**Fonctionnalités :**
- Génération de tous les contextes
- Synchronisation avec le cloud
- Mise à jour complète de la configuration

### Scripts de service
- `setup_maintenance_service.sh` - Configuration du service de maintenance
- `service-control.sh` - Contrôle des services
- `schedule_daily_maintenance.py` - Planification de la maintenance

## Workflow de maintenance

1. **Maintenance rapide quotidienne :**
   ```bash
   python3 maintenance.py --quick
   ```

2. **Génération de contextes manquants :**
   ```bash
   python3 generate-missing-contexts.py --domain astro
   ```

3. **Maintenance complète hebdomadaire :**
   ```bash
   python3 maintenance.py
   ```

4. **Synchronisation complète :**
   ```bash
   python3 generate-and-sync-all.py
   ```
