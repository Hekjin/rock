from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.health import HealthRead

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthRead)
def get_health(db: Annotated[Session, Depends(get_db)]) -> HealthRead:
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "disconnected"

    return HealthRead(status="ok", environment=f"db: {db_status}")
