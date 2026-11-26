from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QuizTest(Base):
    __tablename__ = "quiz_tests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    teacher = relationship("User", backref="created_quizzes")
    questions = relationship(
        "QuizQuestion",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    __table_args__ = (
        CheckConstraint('"order" > 0', name="check_quiz_question_order_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    quiz = relationship("QuizTest", back_populates="questions")
    options = relationship(
        "QuizOption",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QuizOption(Base):
    __tablename__ = "quiz_options"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    question = relationship("QuizQuestion", back_populates="options")
