# rock
# Платформа для тестирования учеников

Веб-платформа, которая использует искусственный интеллект для создания тестов. Ученики проходят сгенерированные тесты и отправляют ответы, а учителя получают доступ к ответам и результатам.

## Как работает платформа

1. ИИ генерирует тест.
2. Ученики проходят тест и отправляют ответы.
3. Учителя просматривают ответы и результаты учеников.

## Роли пользователей

- **Ученик** — проходит тесты и отправляет ответы.
- **Учитель** — просматривает ответы и результаты учеников.
- **Администратор** — управляет пользователями, ролями и настройками платформы.

## Технологии

- **Backend:** FastAPI
- **Frontend:** Next.js 16
- **База данных:** PostgreSQL, SQLAlchemy 2, Alembic
- **Авторизация:** Keycloak (OIDC)
- **ИИ:** Ollama — локальная языковая модель для генерации тестов
- **Тестирование приложения:** pytest
- **Инфраструктура:** Nginx, Docker Compose
- **Дополнительно:** Redis, RabbitMQ и фоновые задачи

## Архитектура: Қабат картасы (4-сабақ)

Проект строго следует принципу чистой 5-слойной архитектуры:
- **Router (`app/api/v1/routers/`):** Приём HTTP-запросов, проверка ролей (`student`/`teacher`/`admin`), вызов Service, трансляция исключений в HTTP-коды (`Қате→HTTP`). **Никакого SQL в Router!**
- **Schema (`app/schemas/`):** Pydantic DTO (Кіріс → Шығыс).
- **Service (`app/services/`):** Чистая бизнес-логика. **Никаких HTTPException в Service!** Выбрасываются только кастомные доменные исключения.
- **Repository (`app/repositories/`):** Единственная точка работы с базой данных (SQLAlchemy 2).
- **Model (`app/models/`):** Таблицы базы данных (DeclarativeBase).

> **Мызғымас ережелер:**
> 1. Router-де SQL жоқ, service-те HTTPException жоқ.
> 2. Құпиялар тек `.env`-те.

## Запуск проекта

### 1. Настройка окружения
Скопируйте шаблон переменных окружения:
```bash
cp .env.example .env
```

### 2. Запуск контейнеров через Docker Compose
```bash
docker compose up -d --build
```

### 3. Применение миграций базы данных
```bash
docker compose exec backend alembic upgrade head
```

### 4. Загрузка модели в Ollama
```bash
docker compose exec ollama ollama pull llama3:8b
```

### 5. Запуск тестов backend
```bash
docker compose exec backend pytest
```

## Доступ к сервисам
- Веб-платформа: http://localhost
- Документация FastAPI Swagger: http://localhost/docs (или http://localhost:8000/api/v1/docs)
- RabbitMQ Management: http://localhost:15672 (guest / guest)
