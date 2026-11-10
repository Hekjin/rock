# Қабат картасы (4-сабақ)

```mermaid
flowchart TD
    Client["Клиент (Web)"] --> Router["Router (FastAPI)"]
    Router --> Schema["Schema (Pydantic DTO)"]
    Router --> Service["Service (Бизнес-логика)"]
    Service --> Repository["Repository (SQLAlchemy 2)"]
    Repository --> Model["Model (Кестелер)"]
    Service -.->|Domain Exception| Router
    Router -.->|HTTP Status (422, 404)| Client
```

| Қабат | Мұғалім жаңа тест жасайды (1-әрекет) | Оқушы тест жауаптарын тапсырады (2-әрекет) |
|---|---|---|
| **Router** | POST /api/v1/tests · мұғалім жаңа тест құрады | POST /api/v1/submissions · оқушы тест жауаптарын жібереді |
| **Schema** | QuizCreateRequest кірісінен QuizDetailResponse шығыс үлгісіне түрлендіру | SubmissionCreate кірісінен SubmissionResultResponse шығыс үлгісіне түрлендіру |
| **Service** | Сұрақтар санын тексеру; әр сұраққа дұрыс нұсқа бекіту | Тесттің белсенділігін тексеру; жауаптар бойынша балл есептеу |
| **Repository** | QuizRepository.create_quiz жаңа сұрақтар мен тестті сақтайды | SubmissionRepository.save_submission оқушының жауаптары мен балын сақтайды |
| **Model** | quiz_tests кестесі және оның сұрақтары quiz_questions | submissions кестесі және оның жауаптары submission_answers |
| **Қате→HTTP** | Сұрақтар дұрыс толтырылмаған жағдайда 422 қатесі қайтарылады | Тапсырылатын тест табылмаған жағдайда 404 қатесі қайтарылады |

## Біздің ереже
- Router-де SQL жоқ, service-те HTTPException жоқ
- Құпиялар тек .env-те
