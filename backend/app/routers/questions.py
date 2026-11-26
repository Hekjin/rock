from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.question import OptionRead, QuestionRead, QuestionUpdate
from app.services.question_service import (
    InvalidCorrectIndexError,
    QuestionForbiddenError,
    QuestionNotFoundError,
    QuestionService,
    QuizAlreadyPublishedError,
)

router = APIRouter(prefix="/api/questions", tags=["questions"])


def get_question_service(
    db: Annotated[Session, Depends(get_db)],
) -> QuestionService:
    return QuestionService(db)


TeacherOrAdmin = Annotated[User, Depends(require_role("teacher", "admin"))]


@router.patch(
    "/{question_id}",
    response_model=QuestionRead,
    status_code=status.HTTP_200_OK,
)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    current_user: TeacherOrAdmin,
    service: Annotated[QuestionService, Depends(get_question_service)],
) -> QuestionRead:
    try:
        q = service.update_question(
            question_id=question_id, data=data, current_user=current_user
        )
        return QuestionRead(
            id=q.id,
            quiz_id=q.quiz_id,
            question_text=q.question_text,
            order=q.order,
            options=[
                OptionRead(id=o.id, option_text=o.option_text, is_correct=o.is_correct)
                for o in q.options
            ],
        )
    except (QuizAlreadyPublishedError, InvalidCorrectIndexError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
    except QuestionForbiddenError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(err)
        ) from err
    except QuestionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    current_user: TeacherOrAdmin,
    service: Annotated[QuestionService, Depends(get_question_service)],
) -> Response:
    try:
        service.delete_question(question_id=question_id, current_user=current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except QuizAlreadyPublishedError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
    except QuestionForbiddenError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(err)
        ) from err
    except QuestionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
