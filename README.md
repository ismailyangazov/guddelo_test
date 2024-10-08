
Задача: создать RESTful API для регистрации, авторизации и управления записями пользователей

## Технологии и инструменты

* Python 3.9
* FastAPI
* Redis
* PostgreSQL
* JWT-токены для проверки авторизации пользователей
* Slowapi для ограничения количества запросов

## Функциональность

### Регистрация пользователя

* POST-запрос на `/register`: регистрирует нового пользователя.

### Авторизация пользователя

* POST-запрос на `/login`: авторизует пользователя и возвращает JWT-токен.

### Разлогинивание пользователя

* POST-запрос на `/logout`: разлогинивает пользователя и удаляет JWT-токен.

### Создание новой задачи

* POST-запрос на `/tasks`: создает новую задачу для текущего пользователя.

### Получение списка всех задач

* GET-запрос на `/tasks`: возвращает список всех задач для текущего пользователя.

### Получение конкретной задачи

* GET-запрос на `/tasks/{task_id}`: возвращает конкретную задачу для текущего пользователя.

### Изменение задачи

* PUT-запрос на `/tasks/{task_id}`: изменяет задачу для текущего пользователя.

### Удаление задачи

* DELETE-запрос на `/tasks/{task_id}`: удаляет задачу для текущего пользователя.

## Ограничения количества запросов

Чтобы предотвратить слишком частый доступ к API, используется slowapi с лимитом 100 запросов в минуту.

## Запуск приложения

Чтобы запустить приложение, необходимо выполнить следующие команды:

1. Создать и активировать виртуальное окружение: `python -m venv venv` и `. venv/bin/activate`
2. Установить необходимые зависимости: `pip install -r requirements.txt`
3. Создать базу данных PostgreSQL: `createdb database`
4. Импортировать данные в базу данных: `psql -d database < data.sql`
5. Запустить приложение: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Docker

```bash
docker build -t my-fastapi-app .
```

```bash
docker run -p 8000:8000 my-fastapi-app
```

## Выполнение запросов к API

Чтобы выполнить запросы к API, необходимо использовать команду `curl` или любое другое ПО для отправки HTTP-запросов.


### Регистрация пользователя

* POST-запрос на `/register`: регистрирует нового пользователя.
```bash
curl -X 'POST' \
  http://localhost:8000/register \
  -H 'Content-Type: application/json' \
  -d '{"username": "user1", "password": "password1"}'
```

### Авторизация пользователя

* POST-запрос на `/login`: авторизует пользователя и возвращает JWT-токен.
```bash
curl -X 'POST' \
  http://localhost:8000/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "user1", "password": "password1"}'
```

### Разлогинивание пользователя

* POST-запрос на `/logout`: разлогинивает пользователя и удаляет JWT-токен.
```bash
curl -X 'POST' \
  http://localhost:8000/logout \
  -H 'Authorization: Bearer <JWT-токен>'
```

### Создание новой задачи

* POST-запрос на `/tasks`: создает новую задачу для текущего пользователя.
```bash
curl -X 'POST' \
  http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "Новая задача", "description": "Описание новой задачи"}'
  -H 'Authorization: Bearer <JWT-токен>'
```

### Получение списка всех задач

* GET-запрос на `/tasks`: возвращает список всех задач для текущего пользователя.
```bash
curl -X 'GET' \
  http://localhost:8000/tasks \
  -H 'Authorization: Bearer <JWT-токен>'
```

### Получение конкретной задачи

* GET-запрос на `/tasks/{task_id}`: возвращает конкретную задачу для текущего пользователя.
```bash
curl -X 'GET' \
  http://localhost:8000/tasks/1 \
  -H 'Authorization: Bearer <JWT-токен>'
```

### Изменение задачи

* PUT-запрос на `/tasks/{task_id}`: изменяет задачу для текущего пользователя.
```bash
curl -X 'PUT' \
  http://localhost:8000/tasks/1 \
  -H 'Content-Type: application/json' \
  -d '{"title": "Измененная задача", "description": "Описание измененной задачи"}'
  -H 'Authorization: Bearer <JWT-токен>'
```

### Удаление задачи

* DELETE-запрос на `/tasks/{task_id}`: удаляет задачу для текущего пользователя.
```bash
curl -X 'DELETE' \
  http://localhost:8000/tasks/1 \
  -H 'Authorization: Bearer <JWT-токен>'
```
