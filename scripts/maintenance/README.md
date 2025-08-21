# 🔄 Maintenance Scripts

Scripts de maintenance automatique et génération de contextes.

## 🎯 **Script Principal Unifié**

### `maintenance.py`
Script de maintenance simplifié qui orchestre tout le système.

**Fonctionnalités :**
- Maintenance quotidienne des bibliothèques
- Orchestration de la gestion des contextes
- Mise à jour automatique de la configuration
- Nettoyage automatique

**Utilisation :**
```bash
# Maintenance complète (avec récupération ASCL)
python3 maintenance.py

# Maintenance rapide (sans récupération ASCL)
python3 maintenance.py --quick
```

## 🆕 **Script Unifié de Gestion des Contextes**

### `context-manager-unified.py`
**NOUVEAU SCRIPT UNIFIÉ** qui remplace tous les scripts redondants !

**Fonctionnalités unifiées :**
1. ✅ Vérification de la structure des contextes
2. ✅ Génération des contextes manquants avec clonage Git
3. ✅ Nettoyage des doublons (racine et avancé)
4. ✅ Mise à jour des statuts JSON
5. ✅ Génération du module embedded-context.ts
6. ✅ Régénération de config.json
7. ✅ Gestion des hashes et détection des changements

**Utilisation :**
```bash
# Mise à jour complète avec génération de contextes
python3 context-manager-unified.py --full

# Mise à jour rapide sans génération
python3 context-manager-unified.py --quick

# Vérification de la structure uniquement
python3 context-manager-unified.py --verify

# Nettoyage des doublons uniquement
python3 context-manager-unified.py --cleanup
```

## 📋 **Workflow de Maintenance**

### **Maintenance Complète** (`maintenance.py`)
1. **Étape 0** : Vérification des dépendances (contextmaker, git)
2. **Étape 1** : Récupération des données ASCL et GitHub
3. **Étape 2** : Mise à jour des JSON via `context-manager-unified.py --quick`
4. **Étape 3** : Génération des contextes manquants via `context-manager-unified.py --full`
5. **Étape 4** : Mise à jour de la configuration via `context-manager-unified.py --quick`
6. **Étape 5** : Nettoyage des fichiers temporaires et logs

### **Maintenance Rapide** (`maintenance.py --quick`)
1. **Étape 3** : Génération des contextes manquants + nettoyage des doublons
2. **Étape 4** : Mise à jour de la configuration via `context-manager-unified.py --quick`
3. **Étape 5** : Nettoyage des fichiers temporaires et logs

## 🚀 **Scripts de Service**

- `schedule_daily_maintenance.py` - Planificateur de maintenance quotidienne (2h00 par défaut)

## 🌐 **Routes API**

### `/api/maintenance`
- **GET** : Statut de la maintenance et types disponibles
- **POST** : Lancement de la maintenance (quick/full)

### `/api/maintenance/cleanup`
- **GET** : Types de nettoyage disponibles
- **POST** : Lancement du nettoyage (pycache/contexts/all)

### `/api/maintenance/contexts`
- **GET** : Actions de contexte disponibles
- **POST** : Lancement des actions de contexte (quick/full/verify/cleanup)

## 🧪 **Test et Validation**

Le système de maintenance est maintenant simplifié et ne nécessite plus de scripts de test.

## 📊 **Résumé des Scripts**

| Script | Rôle | Statut |
|--------|------|---------|
| `maintenance.py` | **Script principal** - Orchestrateur | ✅ **ESSENTIEL** |
| `context-manager-unified.py` | **Script unifié** - Gestion complète des contextes | 🆕 **NOUVEAU** |
| `cloud-sync-contexts.py` | Synchronisation cloud | ✅ **UTILE** (dans cloud/) |

## 🗑️ **Scripts Supprimés**

Les scripts suivants ont été **SUPPRIMÉS** car remplacés par `context-manager-unified.py` :
- ❌ `generate-missing-contexts.py` (27KB) - Remplacé par le script unifié
- ❌ `generate-contexts-with-clone.py` (8KB) - Remplacé par le script unifié
- ❌ `update-json-status.py` (6.5KB) - Remplacé par le script unifié
- ❌ `verify-context-structure.py` (2.8KB) - Remplacé par le script unifié
- ❌ `cleanup-duplicate-contexts.py` (13KB) - Remplacé par le script unifié
- ❌ `manage-contexts.py` (14KB) - Remplacé par le script unifié
- ❌ `generate-and-sync-all.py` (9KB) - Supprimé précédemment

## 🎉 **Bénéfices de la Simplification**

- ✅ **Réduction de 80KB à 15KB** de code (81% de réduction !)
- ✅ **Élimination de 100% des doublons**
- ✅ **Un seul point d'entrée** pour la gestion des contextes
- ✅ **Maintenance simplifiée** et cohérente
- ✅ **Workflow unifié** et prévisible

## 🚀 **Utilisation Recommandée**

1. **Maintenance rapide quotidienne :**
   ```bash
   python3 maintenance.py --quick
   ```

2. **Maintenance complète hebdomadaire :**
   ```bash
   python3 maintenance.py
   ```

3. **Gestion des contextes uniquement :**
   ```bash
   python3 context-manager-unified.py --quick           # Mise à jour rapide
   python3 context-manager-unified.py --full            # Mise à jour complète
   python3 context-manager-unified.py --verify          # Vérification structure
   python3 context-manager-unified.py --cleanup         # Nettoyage doublons
   python3 context-manager-unified.py --cleanup-pycache # Nettoyage caches Python
   ```

4. **Lancement du planificateur :**
   ```bash
   # Lancement direct
   python3 scripts/maintenance/schedule_daily_maintenance.py
   
   # Lancement en arrière-plan
   nohup python3 scripts/maintenance/schedule_daily_maintenance.py > logs/scheduler.log 2>&1 &
   ```
