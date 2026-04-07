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

alembic revision --autogenerate -m "init"
alembic upgrade head

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

## 📌 Примечание

Все защищённые эндпоинты требуют:

Authorization: Bearer <access_token>

### Auth
- POST /auth/register — регистрация
- POST /auth/login — авторизация (получение JWT)
- GET /auth/me — текущий пользователь
- PATCH /auth/me — обновление профиля
- DELETE /auth/me — удаление аккаунта
- GET /auth/admin-only — доступ только для admin

### Teams

- POST /teams/ — создать команду (admin)
- POST /teams/join — вступить в команду по коду
- GET /teams/members — получить участников команды
- PATCH /teams/role — изменить роль пользователя
- DELETE /teams/{user_id} — удалить пользователя из команды

### Tasks

- GET /tasks/ — список задач
- POST /tasks/ — создать задачу
- GET /tasks/{task_id} — получить задачу
- PATCH /tasks/{task_id} — обновить задачу (автор)
- DELETE /tasks/{task_id} — удалить задачу (автор)

### Статусы задач

- PATCH /tasks/{task_id}/status — изменить статус задачи

### Комментарии

- POST /tasks/{task_id}/comments — добавить комментарий
- GET /tasks/{task_id}/comments — получить комментарии

### Meetings

- POST /meetings/ — создать встречу
- GET /meetings/my — мои встречи
- DELETE /meetings/{meeting_id} — отменить встречу (организатор)

### Calendar

- GET /calendar/day — события за день
- GET /calendar/month — события за месяц

### Evaluations

- POST /evaluations/ — оценить задачу
- GET /evaluations/my — мои оценки
- GET /evaluations/average — средняя оценка
- GET /evaluations/average-by-period — средняя оценка за период

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

##  Админ-панель

В проекте реализована административная панель на базе SQLAdmin, позволяющая управлять всеми основными сущностями системы.

Доступ осуществляется по адресу:

```
/admin
```

### Доступные модели

### Через админ-панель можно просматривать и редактировать:

- Users
- Teams
- Tasks
- Evaluations
- Meetings
- Task Comments

### Возможности

- Просмотр всех записей
- Редактирование данных
- Удаление записей
- Поиск и сортировка
- Работа со связями (ForeignKey)

### Ограничения

Пользователей нельзя создавать через админку

Создание пользователей отключено:

в админке нет формы создания User
доступно только редактирование и удаление

Причина:

пароль в системе хранится в захешированном виде
при создании через админку невозможно корректно применить хеширование
это может привести к невалидным пользователям

Поэтому пользователи создаются только через API:

```
POST /auth/register
```

### Безопасность

админка работает поверх основной системы авторизации
доступ к данным контролируется через роли и backend-логику
пароли хранятся с использованием безопасного алгоритма (pbkdf2_sha256)

---
##  Автор

Ivan Sinitsyn
