from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionRead


class QuizCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Тест атауы")
    description: str | None = Field(
        default=None, max_length=2000, description="Тест сипаттамасы"
    )


class QuizUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class QuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    teacher_id: int
    is_active: bool
    is_published: bool
    created_at: datetime


class QuizDetailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    teacher_id: int
    is_active: bool
    is_published: bool
    created_at: datetime
    questions: list[QuestionRead] = []
