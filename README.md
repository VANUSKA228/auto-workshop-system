# Система управления автосервисом

Веб-приложение для автоматизации работы сети автомастерских. ТЗ v2.0.

## Технологический стек

| Слой | Технология |
|------|------------|
| Backend | Python 3.11+, FastAPI 0.110+, SQLAlchemy 2.0, Alembic |
| БД | PostgreSQL 15 |
| Auth | JWT (python-jose, passlib[bcrypt]) |
| Frontend | React 18, TypeScript 5, Vite 5, Tailwind CSS |
| Deploy | Docker + Docker Compose |

## Быстрый старт (Docker)

```bash
docker-compose up -d
```

- Backend: http://localhost:8000  
- Frontend: http://localhost:3000  
- API Docs: http://localhost:8000/docs  

## Разработка без Docker

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### БД (PostgreSQL)
Создай БД `autoservice`, пользователь `postgres`, пароль `secret`.  
Или измени `DATABASE_URL` в `backend/.env`.

---

## План работ по ролям

### Что сделать мне (Backend)

1. **Создать `.env`** в `backend/` с `DATABASE_URL` и `SECRET_KEY`
2. **Запустить миграции**: `alembic upgrade head`
3. **Создать seed-данные**: роли (client, master, admin) и первого admin-пользователя
4. **Протестировать эндпоинты** через `/docs`
5. **Добавить тесты** в `backend/tests/` (pytest)
6. Доработать логику `/reports/personal` и `/reports/finance` по ТЗ
7. Реализовать пагинацию и фильтры в `GET /orders/` (limit/offset уже есть)

Подробные комментарии — в каждом файле бэкенда (main.py, auth.py, models, dependencies).

---

### Что сделать Семёну (Database)

1. **Проверить миграцию** `alembic/versions/001_initial_schema.py`
2. **Создать seed-миграцию** для `roles` и первого admin
3. **Добавить индексы** (в моделях и миграциях):
   - Составной `(status, created_at DESC)` на `orders`
   - `idx_users_email` (уже есть)
   - Индекс на `master_id` для отчётов
4. **Проверить ForeignKey** и `ON DELETE` в `order_services`, `payments`
5. **Проверить уникальность** `email` в `users`
6. При изменениях: `alembic revision --autogenerate -m "описание"`

Зоны с комментариями `# ЗОНА РАБОТЫ СЕМЁНА` — в `backend/app/models/` и `backend/alembic/`.

---

### Что сделать Исламу (Frontend)

1. **Настроить проброс токена** — уже в `api/axiosInstance.ts`, проверь
2. **Страницы из раздела 6 ТЗ**:
   - `/login` — готово (валидация Yup, redirect)
   - `/orders` — базовая таблица есть, добавить фильтры, модалку деталей
   - `/orders/new` — форма есть, доработать ФИО, телефон, email
   - `/payment` — заглушка, добавить маски карты (react-input-mask)
   - `/services` — таблица, admin: кнопки добавления/редактирования
   - `/users` — заглушка, реализовать CRUD
   - `/reports` — блоки отчётов
3. **Navbar** — скрывать пункты по роли (уже частично)
4. **Badge статусов** — цвета по ТЗ (new=серый, in_progress=синий, in_repair=оранжевый, done=зелёный)
5. **Toast-уведомления** — заменить `alert` на toast (правый верхний угол, 4 сек)
6. **Модалка «Обработать заявку»** для Master — PATCH статуса и мастера

Зоны с комментариями `// ЗОНА РАБОТЫ ИСЛАМА` — в `api/axiosInstance.ts`, `App.tsx`, страницах.

---

## Структура проекта

```
auto-workshop-system/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── models/
│   │   ├── schemas/
│   │   └── routers/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── store/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```
