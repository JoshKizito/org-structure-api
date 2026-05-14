# OrgChart Frontend

Dashboard React (Vite) pour l'API organisationnelle.

## Stack
- React 18 + Vite 5
- CSS Modules (dark mode, design tokens)
- Lucide React (icônes)
- IBM Plex Mono + DM Sans

## Lancement

```bash
cd org-frontend
npm install
npm run dev       # http://localhost:3000
```

> L'API doit tourner sur `http://localhost:8000`  
> Le proxy Vite redirige automatiquement `/api` → `http://localhost:8000`

## Build production

```bash
npm run build     # génère dist/
npm run preview   # prévisualise le build
```

## Fonctionnalités

- Arbre des départements dans la sidebar (récursif, recherche)
- Détail d'un département : stats, sous-départements, liste d'employés
- Créer / modifier / supprimer un département
- Ajouter des employés
- Suppression en cascade ou avec réaffectation des employés
- Toasts de feedback
- Rafraîchissement manuel
