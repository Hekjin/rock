from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.attempt import AttemptResult
from app.services.attempt_service import AttemptService

router = APIRouter(prefix="/api/attempts", tags=["attempts"])


def get_attempt_service(
    db: Annotated[Session, Depends(get_db)],
) -> AttemptService:
    return AttemptService(db)


StudentUser = Annotated[User, Depends(require_role("student"))]


@router.get("/me", response_model=list[AttemptResult], status_code=status.HTTP_200_OK)
def get_my_attempts(
    current_user: StudentUser,
    service: Annotated[AttemptService, Depends(get_attempt_service)],
) -> list[AttemptResult]:
    submissions = service.get_student_attempts(student_id=current_user.id)
    return [
        AttemptResult(
            id=s.id,
            quiz_id=s.quiz_id,
            student_id=s.student_id,
            score=s.score,
            total_questions=len(s.quiz.questions) if s.quiz else None,
            submitted_at=s.submitted_at,
        )
        for s in submissions
    ]
