from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnswerSubmit(BaseModel):
    question_id: int
    selected_option_id: int


class AttemptCreate(BaseModel):
    answers: list[AnswerSubmit] = Field(
        ..., min_length=1, description="Сұрақтарға жауаптар тізімі"
    )


class AttemptResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    student_id: int
    score: int | None
    total_questions: int | None = None
    submitted_at: datetime
