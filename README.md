# Org Structure — Полный проект

```
org-complete/
├── org-api/        → REST API FastAPI + PostgreSQL
└── org-frontend/   → Dashboard React (Vite, тёмная тема)
```

---

## Быстрый старт

### 1. Бэкенд (API + база данных)

```bash
cd org-api
cp .env.example .env
docker-compose up --build
```

API доступен по адресу : http://localhost:8000  
Документация Swagger : http://localhost:8000/docs

### 2. Фронтенд (в другом терминале)

```bash
cd org-frontend
npm install
npm run dev
```

Dashboard доступен по адресу : http://localhost:3000

---

## Архитектура

```
org-api/
├── Dockerfile + docker-compose.yml
├── alembic/         SQL-миграции
└── app/
    ├── api/         маршруты FastAPI
    ├── core/        конфигурация, база данных
    ├── models/      SQLAlchemy ORM
    ├── schemas/     Pydantic v2
    ├── services/    бизнес-логика
    └── repositories/ доступ к базе данных

org-frontend/
└── src/
    ├── api/         HTTP-клиент
    ├── components/  Sidebar, DeptDetail, модальные окна
    └── hooks/       useToast
```

## Тесты бэкенда

```bash
cd org-api
pip install -r requirements.txt
pytest -v
```