# Guide de Séparation des Domaines

Ce guide explique la nouvelle structure de séparation des domaines Astronomy/Cosmology et Finance/Trading.

## 🎯 **Nouvelle Structure**

### **Navigation Flow :**
```
/landing (avec sélection de domaine intégrée) → /astronomy ou /finance
```

### **Pages Créées :**

#### **Pages Principales :**
- `/landing` - Page de garde avec sélection de domaine intégrée (HOME page)
- `/astronomy` - Assistant IA pour l'astronomie
- `/finance` - Assistant IA pour la finance

#### **Pages Leaderboard :**
- `/astronomy/leaderboard` - Classement des librairies astronomie
- `/finance/leaderboard` - Classement des librairies finance

## 📁 **Structure des Fichiers**

### **Données Séparées :**
```
app/data/
├── astronomy-libraries.json  # Données astronomie
├── finance-libraries.json    # Données finance
└── libraries.json           # Ancien fichier (à supprimer)
```

### **Utilitaires :**
```
app/utils/
└── domain-loader.ts         # Chargement des données par domaine
```

### **Pages :**
```
app/
├── landing/page.tsx (HOME page avec sélection de domaine)
├── astronomy/
│   ├── page.tsx
│   └── leaderboard/page.tsx
└── finance/
    ├── page.tsx
    └── leaderboard/page.tsx
```

## 🚀 **Fonctionnalités**

### **1. Sélecteur de Domaine**
- **Animation fluide** avec effets de survol
- **Cartes interactives** pour chaque domaine
- **Transition élégante** vers le domaine choisi

### **2. Pages Spécifiques par Domaine**
- **Interface adaptée** à chaque domaine
- **Métadonnées spécifiques** (description, mots-clés)
- **Chat IA spécialisé** pour le domaine

### **3. Leaderboards Séparés**
- **Classements dédiés** par domaine
- **Navigation fluide** entre chat et leaderboard
- **Bouton flottant** adaptatif

## 🔧 **Mise à Jour des Données**

### **Script de Mise à Jour :**
```bash
# Mettre à jour les données avec get100
python scripts/update-domain-data.py
```

### **Processus :**
1. Exécuter `get100.py` pour générer `last.csv`
2. Exécuter `update-domain-data.py` pour séparer les domaines
3. Les fichiers JSON sont automatiquement mis à jour

### **Filtres Utilisés :**

#### **Astronomie/Cosmologie :**
- astro, astropy, healpy, photutils, sky, gal, cosmo, cmb
- planck, tardis, lightkurve, astroquery, pypeit, poppy
- galsim, ultranest, pymultinest, zeus, radis, astronn
- presto, astroplan, sep, specutils, s2fft, stingray
- spacepy, pycbc, gwpy, einsteinpy, simonsobs, cmbant

#### **Finance/Trading :**
- finance, trading, portfolio, quant, zipline, yfinance, pyfolio
- empyrical, alphalens, mlfinlab, ffn, finquant, backtrader
- vnpy, tushare, akshare, ccxt, pandas-ta, ta-lib, finrl
- qlib, gplearn, pykalman, arch, statsmodels

## 🎨 **Animations et Design**

### **Sélecteur de Domaine :**
- **Effets de survol** avec rotation et échelle
- **Indicateurs de sélection** animés
- **Transitions fluides** entre états
- **Loading screen** pendant la navigation

### **Bouton Flottant :**
- **Navigation intelligente** selon la page actuelle
- **Texte adaptatif** (Chat ↔ Leaderboard)
- **Masqué** sur les pages de présentation

## 🔄 **Navigation**

### **Flux Utilisateur :**
1. **Landing** → Cliquer "Get Started"
2. **Domain Selector** → Choisir un domaine
3. **Domain Page** → Utiliser l'assistant IA
4. **Leaderboard** → Voir le classement
5. **Retour** → Navigation fluide entre les pages

### **Bouton Flottant :**
- **Sur `/astronomy`** → "Leaderboard" → `/astronomy/leaderboard`
- **Sur `/finance`** → "Leaderboard" → `/finance/leaderboard`
- **Sur leaderboard** → "Chat" → retour au domaine

## 📊 **Avantages de la Séparation**

### **1. Organisation Claire**
- Données séparées par domaine
- Interface adaptée à chaque spécialité
- Navigation intuitive

### **2. Performance**
- Chargement plus rapide (données réduites)
- Cache optimisé par domaine
- Bundle splitting automatique

### **3. Maintenabilité**
- Code modulaire et réutilisable
- Mise à jour indépendante des domaines
- Tests unitaires facilités

### **4. Expérience Utilisateur**
- Interface spécialisée
- Animations fluides
- Navigation claire

## 🛠 **Prochaines Étapes**

- [ ] Ajouter des métriques par domaine
- [ ] Créer des tests unitaires
- [ ] Optimiser les performances
- [ ] Ajouter des filtres avancés
- [ ] Intégrer des analytics par domaine 