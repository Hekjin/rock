from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.attempt import AttemptCreate, AttemptResult
from app.schemas.question import OptionRead, QuestionCreate, QuestionRead
from app.schemas.quiz import (
    QuizCreate,
    QuizDetailRead,
    QuizRead,
    QuizUpdate,
)
from app.services.attempt_service import (
    AnswerCountMismatchError,
    AttemptService,
    QuizNotPublishedError,
)
from app.services.question_service import (
    InvalidCorrectIndexError,
    QuestionForbiddenError,
    QuestionNotFoundError,
    QuestionService,
    QuizAlreadyPublishedError,
)
from app.services.quiz_service import (
    QuizForbiddenError,
    QuizNoQuestionsError,
    QuizNotFoundError,
    QuizService,
)

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


def get_quiz_service(db: Annotated[Session, Depends(get_db)]) -> QuizService:
    return QuizService(db)


def get_question_service(
    db: Annotated[Session, Depends(get_db)],
) -> QuestionService:
    return QuestionService(db)


def get_attempt_service(
    db: Annotated[Session, Depends(get_db)],
) -> AttemptService:
    return AttemptService(db)


CurrentUser = Annotated[User, Depends(get_current_user)]
TeacherOrAdmin = Annotated[User, Depends(require_role("teacher", "admin"))]
StudentUser = Annotated[User, Depends(require_role("student"))]


@router.get("", response_model=list[QuizRead], status_code=status.HTTP_200_OK)
def list_quizzes(
    current_user: CurrentUser,
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> list[QuizRead]:
    return list(service.list_quizzes(current_user))


@router.post("", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
def create_quiz(
    data: QuizCreate,
    current_user: TeacherOrAdmin,
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> QuizRead:
    return service.create_quiz(data=data, teacher_id=current_user.id)


@router.get("/{quiz_id}", response_model=QuizDetailRead, status_code=status.HTTP_200_OK)
def get_quiz(
    quiz_id: int,
    current_user: CurrentUser,
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> QuizDetailRead:
    try:
        quiz = service.get_quiz(quiz_id=quiz_id, current_user=current_user)
    except QuizNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        ) from err

    is_student = current_user.role == "student"
    questions_data = []
    for q in quiz.questions:
        options_data = [
            OptionRead(
                id=o.id,
                option_text=o.option_text,
                is_correct=None if is_student else o.is_correct,
            )
            for o in q.options
        ]
        questions_data.append(
            QuestionRead(
                id=q.id,
                quiz_id=q.quiz_id,
                question_text=q.question_text,
                order=q.order,
                options=options_data,
            )
        )

    return QuizDetailRead(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        teacher_id=quiz.teacher_id,
        is_active=quiz.is_active,
        is_published=quiz.is_published,
        created_at=quiz.created_at,
        questions=questions_data,
    )


@router.patch("/{quiz_id}", response_model=QuizRead, status_code=status.HTTP_200_OK)
def update_quiz(
    quiz_id: int,
    data: QuizUpdate,
    current_user: TeacherOrAdmin,
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> QuizRead:
    try:
        return service.update_quiz(
            quiz_id=quiz_id, data=data, current_user=current_user
        )
    except QuizForbiddenError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(err)
        ) from err
    except QuizNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        ) from err


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    current_user: TeacherOrAdmin,
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> Response:
    try:
        service.delete_quiz(quiz_id=quiz_id, current_user=current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except QuizForbiddenError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(err)
        ) from err
    except QuizNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        ) from err


@router.post(
    "/{quiz_id}/questions",
    response_model=QuestionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    quiz_id: int,
    data: QuestionCreate,
    current_user: TeacherOrAdmin,
    service: Annotated[QuestionService, Depends(get_question_service)],
) -> QuestionRead:
    try:
        q = service.create_question(
            quiz_id=quiz_id, data=data, current_user=current_user
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
    except QuizAlreadyPublishedError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
    except InvalidCorrectIndexError as err:
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


@router.post(
    "/{quiz_id}/publish",
    response_model=QuizRead,
    status_code=status.HTTP_200_OK,
)
def publish_quiz(
    quiz_id: int,
    current_user: TeacherOrAdmin,
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> QuizRead:
    try:
        return service.publish_quiz(quiz_id=quiz_id, current_user=current_user)
    except QuizNoQuestionsError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
    except QuizForbiddenError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(err)
        ) from err
    except QuizNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err


@router.post(
    "/{quiz_id}/attempts",
    response_model=AttemptResult,
    status_code=status.HTTP_201_CREATED,
)
def create_attempt(
    quiz_id: int,
    data: AttemptCreate,
    current_user: StudentUser,
    service: Annotated[AttemptService, Depends(get_attempt_service)],
) -> AttemptResult:
    try:
        submission, total_q = service.submit_attempt(
            quiz_id=quiz_id, data=data, student_id=current_user.id
        )
        return AttemptResult(
            id=submission.id,
            quiz_id=submission.quiz_id,
            student_id=submission.student_id,
            score=submission.score,
            total_questions=total_q,
            submitted_at=submission.submitted_at,
        )
    except (QuizNotPublishedError, AnswerCountMismatchError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
