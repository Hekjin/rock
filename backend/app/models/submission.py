from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    __table_args__ = (
        CheckConstraint("score >= 0", name="check_submission_score_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    quiz = relationship("QuizTest")
    student = relationship("User")
    answers = relationship(
        "SubmissionAnswer",
        back_populates="submission",
        cascade="all, delete-orphan",
    )


class SubmissionAnswer(Base):
    __tablename__ = "submission_answers"

    __table_args__ = (
        UniqueConstraint(
            "submission_id",
            "question_id",
            name="uq_submission_answer_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_option_id: Mapped[int | None] = mapped_column(
        ForeignKey("quiz_options.id", ondelete="SET NULL"),
        nullable=True,
    )

    submission = relationship("Submission", back_populates="answers")
    question = relationship("QuizQuestion")
    selected_option = relationship("QuizOption")
