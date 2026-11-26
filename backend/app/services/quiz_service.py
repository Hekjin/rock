from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.quiz import QuizTest
from app.models.user import User
from app.schemas.quiz import QuizCreate, QuizUpdate


class QuizNotFoundError(Exception):
    pass


class QuizForbiddenError(Exception):
    pass


class QuizNoQuestionsError(Exception):
    pass


class QuizService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_quizzes(self, current_user: User) -> Sequence[QuizTest]:
        if current_user.role == "student":
            stmt = select(QuizTest).where(QuizTest.is_published.is_(True))
        elif current_user.role == "teacher":
            stmt = select(QuizTest).where(
                or_(
                    QuizTest.teacher_id == current_user.id,
                    QuizTest.is_published.is_(True),
                )
            )
        else:  # admin
            stmt = select(QuizTest)

        return self.db.scalars(stmt.order_by(QuizTest.id)).all()

    def get_quiz(self, quiz_id: int, current_user: User) -> QuizTest:
        quiz = self.db.get(QuizTest, quiz_id)
        if not quiz:
            raise QuizNotFoundError("Quiz not found")

        if current_user.role == "student" and not quiz.is_published:
            raise QuizNotFoundError("Quiz not found")

        return quiz

    def create_quiz(self, data: QuizCreate, teacher_id: int) -> QuizTest:
        quiz = QuizTest(
            title=data.title,
            description=data.description,
            teacher_id=teacher_id,
            is_active=True,
            is_published=False,
        )
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def update_quiz(
        self, quiz_id: int, data: QuizUpdate, current_user: User
    ) -> QuizTest:
        quiz = self.db.get(QuizTest, quiz_id)
        if not quiz:
            raise QuizNotFoundError("Quiz not found")

        if current_user.role != "admin" and quiz.teacher_id != current_user.id:
            raise QuizForbiddenError("Чужой тест")

        if data.title is not None:
            quiz.title = data.title
        if data.description is not None:
            quiz.description = data.description

        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete_quiz(self, quiz_id: int, current_user: User) -> None:
        quiz = self.db.get(QuizTest, quiz_id)
        if not quiz:
            raise QuizNotFoundError("Quiz not found")

        if current_user.role != "admin" and quiz.teacher_id != current_user.id:
            raise QuizForbiddenError("Чужой тест")

        self.db.delete(quiz)
        self.db.commit()

    def publish_quiz(self, quiz_id: int, current_user: User) -> QuizTest:
        quiz = self.db.get(QuizTest, quiz_id)
        if not quiz:
            raise QuizNotFoundError("Quiz not found")

        if current_user.role != "admin" and quiz.teacher_id != current_user.id:
            raise QuizForbiddenError("Чужой тест")

        if not quiz.questions:
            raise QuizNoQuestionsError("Тест без вопросов нельзя опубликовать")

        quiz.is_published = True
        self.db.commit()
        self.db.refresh(quiz)
        return quiz
