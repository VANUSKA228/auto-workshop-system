# Система управления автосервисом

Веб-приложение для автоматизации работы сети автосервисов.

## Быстрый запуск

1. Убедитесь, что установлен Docker и Docker Compose
2. Откройте терминал в папке проекта
3. Выполните команду:

```bash
docker-compose up --build
```

4. После запуска откройте в браузере: http://localhost:3000

## Доступ к системе

### Готовые учётные записи

**Администратор:**
- Email: `admin@autoservice.ru`
- Пароль: `admin123`
- Права: полный доступ ко всем функциям

**Мастер смены (Москва — Центральная):**
- Email: `master.moscow1@autoservice.ru`
- Пароль: `master123`

**Мастер смены (Санкт-Петербург — Невский):**
- Email: `master.spb1@autoservice.ru`
- Пароль: `master123`

**Клиенты (тестовые):**
- Email: `client1.moscow@autoservice.ru` / Пароль: `client123`
- Email: `client2.spb@autoservice.ru` / Пароль: `client123`

### Регистрация нового клиента

На странице входа нажмите "Зарегистрироваться как клиент" и заполните форму.

## Что работает в системе

- Авторизация и регистрация пользователей
- Просмотр и управление заявками
- Назначение техников на заявки
- Управление мастерскими и услугами
- Отчёты по выполненным работам

## Тестирование

Запуск тестов:

```bash
docker-compose exec backend pytest -v
```

### Что тестируется

**test_auth.py (16 тестов):**
- `test_login_success_admin` — вход администратора
- `test_login_success_master` — вход мастера
- `test_login_success_client` — вход клиента
- `test_login_wrong_password` — неверный пароль
- `test_login_wrong_email` — несуществующий email
- `test_login_invalid_email_format` — неверный формат email
- `test_protected_route_without_token` — доступ без токена
- `test_protected_route_with_valid_token` — доступ с валидным токеном
- `test_protected_route_with_invalid_token` — доступ с невалидным токеном
- `test_client_self_register_success` — успешная регистрация клиента
- `test_client_register_duplicate_email` — дубликат email
- `test_client_register_invalid_workshop` — несуществующая мастерская
- `test_client_register_missing_required_fields` — отсутствующие поля
- `test_client_register_short_password` — короткий пароль
- `test_client_register_invalid_email` — неверный email
- `test_client_register_and_login` — регистрация и вход

**test_workshops.py (7 тестов):**
- `test_list_workshops_public_without_auth` — публичный список без авторизации
- `test_list_workshops_public_with_auth` — публичный список с авторизацией
- `test_list_workshops_admin` — список для админа
- `test_list_workshops_master` — список для мастера
- `test_list_workshops_without_auth` — доступ к списку без авторизации (запрещён)
- `test_get_workshop_by_id_admin` — получение мастерской по ID
- `test_get_nonexistent_workshop` — получение несуществующей мастерской

## Полезные команды

**Остановка системы:**
```bash
docker-compose down
```

**Полный сброс (удаление базы данных):**
```bash
docker-compose down -v
docker-compose up --build
```

**Просмотр логов:**
```bash
docker-compose logs -f
```

## Технологии

- Backend: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React 18, TypeScript, Vite, Tailwind CSS
- Auth: JWT токены, bcrypt хеширование паролей

## Структура проекта

```
├── backend/          # Серверная часть (FastAPI)
│   ├── app/          # Основной код приложения
│   ├── tests/        # Тесты
│   └── alembic/      # Миграции базы данных
├── frontend/         # Клиентская часть (React)
│   └── src/          # Исходный код
└── docker-compose.yml # Конфигурация Docker
```

## Решение проблем

**Порты заняты:**
- Проверьте, что порты 3000, 8000, 5432 свободны
- Закройте приложения, использующие эти порты

**Ошибки подключения к базе:**
```bash
docker-compose down -v
docker-compose up --build
```
