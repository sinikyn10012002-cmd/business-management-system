# Business Management System

Автоматизированная система управления бизнесом (упрощённая версия) на FastAPI.

##  Описание

Система предназначена для управления командами, задачами, встречами и оценками сотрудников.

Реализована ролевая модель:
- user — выполняет задачи
- manager — управляет задачами
- admin — управляет системой

---

##  Функционал

###  Аутентификация
- Регистрация пользователя
- Авторизация (JWT)
- Получение текущего пользователя
- Обновление профиля
- Удаление аккаунта

###  Команды
- Создание команды (admin)
- Добавление пользователей
- Просмотр участников

###  Задачи
- Создание задач
- Назначение исполнителя
- Изменение статуса (open / in_progress / done)
- Комментарии к задачам

###  Встречи
- Создание встреч
- Добавление участников

###  Оценки
- Оценка выполненных задач (1–5)
- Расчёт средней оценки

###  Календарь
- Отображение событий

###  Админка
- Управление пользователями, задачами, командами и др.

---

##  Стек технологий

- FastAPI
- SQLAlchemy 2.0
- Alembic
- SQLite / PostgreSQL
- JWT (python-jose)
- Passlib (pbkdf2_sha256)
- Jinja2
- Docker

---

##  Структура проекта

```
app/
  api/
  core/
  crud/
  db/
  dependencies/
  models/
  schemas/
  static/
  templates/
  tests/
  admin.py
  main.py
```

---

##  Установка и запуск

### Локально

```bash
git clone <repo>
cd project

python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

### Docker

```bash
docker-compose up --build
```

---

##  Переменные окружения

```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

##  API

Swagger:
- http://localhost:8000/docs
- http://localhost:8000/redoc

---

##  Основные эндпоинты

### Auth
- POST /auth/register
- POST /auth/login
- GET /auth/me
- PATCH /auth/me
- DELETE /auth/me

### Teams
- /teams/...

### Tasks
- /tasks/...

### Meetings
- /meetings/...

### Evaluations
- /evaluations/...

---

##  Примеры запросов

### Регистрация

```json
POST /auth/register

{
  "email": "test@example.com",
  "password": "123456",
  "full_name": "Test User"
}
```

---

### Логин

```json
POST /auth/login

{
  "email": "test@example.com",
  "password": "123456"
}
```

---

##  Безопасность

- Хеширование паролей: pbkdf2_sha256
- JWT авторизация
- Проверка ролей

---

##  Тестирование

```bash
pytest
pytest --cov=app
```

---

##  Админка

Доступ:
```
/admin
```

---

##  Автор

Ivan Sinitsyn
