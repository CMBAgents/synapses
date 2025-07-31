# Guide de la Page de Garde (Landing Page)

Ce guide explique les différentes options pour créer une page de garde avant d'arriver sur la page principale de votre application.

## Structure Actuelle

```
app/
├── page.tsx              # Page d'accueil (redirige vers /landing)
├── landing/
│   └── page.tsx          # Page de garde principale
├── main/
│   └── page.tsx          # Application principale
├── main-with-modal/
│   └── page.tsx          # Application avec modal de bienvenue
└── ui/
    └── welcome-modal.tsx # Composant modal de bienvenue
```

## Options Disponibles

### Option 1: Page de Garde Séparée (Recommandée)

**URLs:**
- `/` → redirige vers `/landing`
- `/landing` → page de garde
- `/main` → application principale

**Avantages:**
- ✅ Séparation claire entre présentation et fonctionnalité
- ✅ SEO optimisé
- ✅ Navigation intuitive
- ✅ Facile à personnaliser

**Utilisation:**
1. Les utilisateurs arrivent sur `/landing`
2. Ils cliquent sur "Get Started" pour aller sur `/main`
3. Navigation fluide entre les pages

### Option 2: Modal de Bienvenue

**URLs:**
- `/main-with-modal` → application avec modal de bienvenue

**Avantages:**
- ✅ Expérience intégrée
- ✅ Pas de changement de page
- ✅ Modal réutilisable
- ✅ Mémorisation de la visite

**Fonctionnalités:**
- Modal s'affiche automatiquement pour les nouveaux visiteurs
- Bouton "Welcome Guide" pour revoir le modal
- Sauvegarde dans localStorage

## Personnalisation

### Modifier la Page de Garde

Éditez `app/landing/page.tsx` pour :
- Changer le design
- Ajouter des sections
- Modifier le contenu
- Ajouter des animations

### Modifier le Modal

Éditez `app/ui/welcome-modal.tsx` pour :
- Changer l'apparence
- Ajouter des fonctionnalités
- Modifier le comportement

### Changer la Redirection

Pour changer la page d'accueil par défaut, modifiez `app/page.tsx` :

```typescript
// Rediriger vers la page principale directement
redirect('/main');

// Ou vers la version avec modal
redirect('/main-with-modal');
```

## Styles et Thème

Toutes les pages utilisent :
- `styles/background.module.css` pour l'arrière-plan
- Classes Tailwind CSS pour le styling
- Thème sombre/clair automatique

## Déploiement

Les pages sont automatiquement générées par Next.js :
- `/landing` → accessible via `yourdomain.com/landing`
- `/main` → accessible via `yourdomain.com/main`
- `/main-with-modal` → accessible via `yourdomain.com/main-with-modal`

## Recommandations

1. **Pour un site public** : Utilisez l'Option 1 (page séparée)
2. **Pour une application interne** : Utilisez l'Option 2 (modal)
3. **Pour un MVP** : Commencez avec l'Option 1, puis évoluez

## Prochaines Étapes

- [ ] Ajouter des analytics
- [ ] Optimiser le SEO
- [ ] Ajouter des animations
- [ ] Créer des variantes A/B
- [ ] Intégrer un système de feedback 