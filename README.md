# 🔧 Система управления автосервисом

Веб-приложение для автоматизации работы сети автомастерских. Три роли: **Клиент**, **Мастер смены**, **Администратор**.

## Технологический стек

| Слой | Технология |
|------|------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic |
| База данных | PostgreSQL 15 |
| Auth | JWT (python-jose, bcrypt) |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS 3 |
| Deploy | Docker + Docker Compose |

---

## 🚀 Быстрый старт (Docker — рекомендуется)

### 1. Клонировать репозиторий
```bash
git clone https://github.com/ВАШ_АККАУНТ/ВАШ_РЕПОЗИТОРИЙ.git
cd ВАШ_РЕПОЗИТОРИЙ
```

### 2. Запустить через Docker Compose
```bash
docker-compose up --build -d
```

Это автоматически:
- Запустит PostgreSQL
- Запустит backend и выполнит миграции (`alembic upgrade head`)
- Соберёт и запустит frontend

### 3. Открыть в браузере
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

### 4. Первый вход
| Email | Пароль | Роль |
|-------|--------|------|
| `admin@autoservice.ru` | `admin123` | Администратор |

> Администратор создаёт остальных пользователей через раздел «Пользователи»

---

## 💻 Разработка без Docker

### Backend

```bash
cd backend

# 1. Создать виртуальное окружение
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать файл .env
cp .env.example .env
# Отредактируйте .env — укажите DATABASE_URL и SECRET_KEY

# 4. Создать БД PostgreSQL (если не создана)
# psql -U postgres -c "CREATE DATABASE autoservice;"

# 5. Применить миграции и seed
alembic upgrade head

# 6. Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# 1. Установить зависимости
npm install

# 2. Создать .env
cp .env.example .env
# VITE_API_URL=http://localhost:8000

# 3. Запустить dev-сервер
npm run dev
# Откроется на http://localhost:3000
```

---

## 📁 Структура проекта

```
auto-workshop-system/
├── backend/
│   ├── app/
│   │   ├── main.py          # точка входа FastAPI
│   │   ├── config.py        # настройки (DATABASE_URL, JWT)
│   │   ├── database.py      # подключение PostgreSQL
│   │   ├── dependencies.py  # JWT-auth, role_required()
│   │   ├── models/          # ORM-модели (User, Order, Payment...)
│   │   ├── schemas/         # Pydantic-валидация
│   │   └── routers/         # API-эндпоинты
│   ├── alembic/             # миграции БД
│   ├── tests/               # pytest
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios-клиенты
│   │   ├── components/      # Navbar, Toast
│   │   ├── pages/           # все страницы
│   │   └── store/           # Zustand (auth)
│   ├── .env.example
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 📋 Роли и доступ

| Функция | Клиент | Мастер смены | Администратор |
|---------|--------|--------------|---------------|
| Создание заявки | ✓ | ✓ | ✓ |
| Просмотр своих заявок | ✓ | — | ✓ |
| Просмотр всех заявок | — | ✓ | ✓ |
| Обработка заявок | — | ✓ | ✓ |
| Удаление заявок | — | ✓ | ✓ |
| Страница оплаты (заглушка) | ✓ | — | — |
| Просмотр услуг | ✓ | — | ✓ |
| Редактирование услуг | — | — | ✓ |
| Отчёты | — | Частично | ✓ |
| Управление пользователями | — | — | ✓ |

---

## 🗄️ База данных

После `alembic upgrade head` создаются таблицы:
- `roles` — роли (client, master, admin)
- `users` — пользователи
- `services` — классификатор услуг
- `orders` — заявки
- `order_services` — связь заявка-услуга
- `payments` — заглушки платежей

---

## 🧪 Тесты

```bash
cd backend
pytest tests/ -v
```

---

## 💾 Сохранить в репозиторий GitHub

```bash
# Инициализация (если ещё нет git)
git init
git add .
git commit -m "Initial: полная система управления автосервисом"

# Привязать к GitHub репозиторию
git remote add origin https://github.com/ВАШ_АККАУНТ/ВАШ_РЕПОЗИТОРИЙ.git
git branch -M main
git push -u origin main

# Последующие обновления:
git add .
git commit -m "Описание изменений"
git push
```

---

## ⚙️ Переменные окружения

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://postgres:secret@localhost:5432/autoservice
SECRET_KEY=ваш-длинный-секретный-ключ
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (`frontend/.env`)
```
VITE_API_URL=http://localhost:8000
```
