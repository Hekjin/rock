from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.quiz import QuizOption, QuizTest
from app.models.submission import Submission, SubmissionAnswer
from app.schemas.attempt import AttemptCreate


class QuizNotPublishedError(Exception):
    pass


class AnswerCountMismatchError(Exception):
    pass


class AttemptService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def submit_attempt(
        self, quiz_id: int, data: AttemptCreate, student_id: int
    ) -> tuple[Submission, int]:
        quiz = self.db.get(QuizTest, quiz_id)
        if not quiz or not quiz.is_published:
            raise QuizNotPublishedError("Тест табылмады немесе жарияланбаған")

        questions = {q.id: q for q in quiz.questions}
        if len(data.answers) != len(questions):
            raise AnswerCountMismatchError(
                "Число ответов не совпадает с числом вопросов"
            )

        score = 0
        submission = Submission(
            quiz_id=quiz_id,
            student_id=student_id,
            score=0,
        )
        self.db.add(submission)
        self.db.flush()

        for ans in data.answers:
            if ans.question_id not in questions:
                raise AnswerCountMismatchError(
                    f"Question {ans.question_id} not in quiz"
                )

            opt = self.db.get(QuizOption, ans.selected_option_id)
            if opt and opt.question_id == ans.question_id and opt.is_correct:
                score += 1

            sub_ans = SubmissionAnswer(
                submission_id=submission.id,
                question_id=ans.question_id,
                selected_option_id=ans.selected_option_id,
            )
            self.db.add(sub_ans)

        submission.score = score
        self.db.commit()
        self.db.refresh(submission)
        return submission, len(questions)

    def get_student_attempts(self, student_id: int) -> Sequence[Submission]:
        stmt = (
            select(Submission)
            .where(Submission.student_id == student_id)
            .order_by(Submission.submitted_at.desc())
        )
        return self.db.scalars(stmt).all()
