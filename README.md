# Org Structure — Projet complet

```
org-complete/
├── org-api/        → API REST FastAPI + PostgreSQL
└── org-frontend/   → Dashboard React (Vite, dark mode)
```

---

## Démarrage rapide

### 1. Backend (API + base de données)

```bash
cd org-api
cp .env.example .env
docker-compose up --build
```

API disponible sur : http://localhost:8000  
Documentation Swagger : http://localhost:8000/docs

### 2. Frontend (dans un autre terminal)

```bash
cd org-frontend
npm install
npm run dev
```

Dashboard disponible sur : http://localhost:3000

---

## Architecture

```
org-api/
├── Dockerfile + docker-compose.yml
├── alembic/         migrations SQL
└── app/
    ├── api/         routes FastAPI
    ├── core/        config, database
    ├── models/      SQLAlchemy ORM
    ├── schemas/     Pydantic v2
    ├── services/    logique métier
    └── repositories/ accès base de données

org-frontend/
└── src/
    ├── api/         client HTTP
    ├── components/  Sidebar, DeptDetail, modals
    └── hooks/       useToast
```

## Tests backend

```bash
cd org-api
pip install -r requirements.txt
pytest -v
```
