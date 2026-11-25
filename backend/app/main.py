from fastapi import FastAPI

from app.core.config import settings
from app.routers.attempts import router as attempts_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.questions import router as questions_router
from app.routers.quiz import router as quiz_router
from app.routers.users import router as users_router

app = FastAPI(
    title=settings.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    swagger_ui_init_oauth={
        "usePkceWithCookie": True,
        "clientId": settings.keycloak_client_id,
        "appName": settings.app_name,
        "scopes": "openid profile email",
    },
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(quiz_router)
app.include_router(questions_router)
app.include_router(attempts_router)
