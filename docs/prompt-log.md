# Prompt Log (4-сабақ)

## Сабақ мақсаты
5 қабатты таза архитектура (Clean Architecture) қаңқасын құру: `docs/layers.md` қабат картасын жасау, Mermaid диаграммасын сызу, бос пакеттерді және Ruff конфигурациясын орнату.

---

## Промпттар тізімі (Prompts)

### 1-промпт: Жоба стекі мен шектеулер
```text
Стек: FastAPI (backend/), PostgreSQL + SQLAlchemy 2 + Alembic,
Keycloak (OIDC: кіру, тіркелу, рөлдер student/teacher/admin),
жергілікті LLM — Ollama (app/llm/), pytest, Next.js 16 (web/), Nginx, Docker Compose.
Кеңейтілген: Redis кэш, RabbitMQ + worker.
Сам поймешь че дделать
```

### 2-промпт: Қабат картасын құру
```text
# Қабат картасы (4-сабақ)
| Қабат      | <1-әрекет: кім не істейді>     | <2-әрекет> |
| Router     | <ӘДІС /api/...> · <рөл>        |            |
| Schema     | <Кіріс> → <Шығыс>              |            |
| Service    | <ереже 1>; <ереже 2>           |            |
| Repository | <Объект>Repository.<әдіс>      |            |
| Model      | <кесте>                        |            |
| Қате→HTTP  | <жағдай> → <код>               |            |
## Біздің ереже
- Router-де SQL жоқ, service-те HTTPException жоқ
- Құпиялар тек .env-те
```

### 3-промпт: Чек-лист бойынша қаңқа мен тегті дайындау
```text
Чек-лист:
- docs/layers.md: 2 әрекет × 5 қабат, әр әрекетте кемінде бір қате → HTTP коды
- Картаның басында Mermaid сызбасы — GitHub-та сурет болып ашылады
- backend/app/-та 6 папка, әрқайсысында бос __init__.py
- .env компьютеріңізде бар, бірақ git status-та көрінбейді
- Endpoint, модель, SQL, main.py әзірге жоқ — тек қаңқа
- Коммит + тег lesson-04 + prompt log-та жазба
```

