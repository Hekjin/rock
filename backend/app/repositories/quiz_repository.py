from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.quiz import QuizTest


class QuizRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, skip: int = 0, limit: int = 100) -> Sequence[QuizTest]:
        stmt = select(QuizTest).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def get(self, quiz_id: int) -> QuizTest | None:
        return self.db.get(QuizTest, quiz_id)

    def create(self, quiz: QuizTest) -> QuizTest:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def save(self, quiz: QuizTest) -> QuizTest:
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete(self, quiz: QuizTest) -> None:
        self.db.delete(quiz)
        self.db.commit()
