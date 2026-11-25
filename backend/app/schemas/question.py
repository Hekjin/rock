from pydantic import BaseModel, ConfigDict, Field


class OptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    option_text: str
    is_correct: bool | None = None


class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=1)
    options: list[str] = Field(..., min_length=2, description="Кемінде 2 жауап нұсқасы")
    correct_index: int = Field(
        ..., ge=0, description="Дұрыс нұсқаның индексі (0-ден бастап)"
    )


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    options: list[str] | None = None
    correct_index: int | None = None


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    question_text: str
    order: int
    options: list[OptionRead] = []
