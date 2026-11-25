from sqlalchemy.orm import Session

from app.models.quiz import QuizOption, QuizQuestion, QuizTest
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionNotFoundError(Exception):
    pass


class QuestionForbiddenError(Exception):
    pass


class QuizAlreadyPublishedError(Exception):
    pass


class InvalidCorrectIndexError(Exception):
    pass


class QuestionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_question(
        self, quiz_id: int, data: QuestionCreate, current_user: User
    ) -> QuizQuestion:
        quiz = self.db.get(QuizTest, quiz_id)
        if not quiz:
            raise QuestionNotFoundError("Quiz not found")

        if current_user.role != "admin" and quiz.teacher_id != current_user.id:
            raise QuestionForbiddenError("Чужой тест")

        if quiz.is_published:
            raise QuizAlreadyPublishedError("В опубликованный тест нельзя")

        if data.correct_index >= len(data.options):
            raise InvalidCorrectIndexError("correct_index больше числа вариантов")

        order = len(quiz.questions) + 1
        question = QuizQuestion(
            quiz_id=quiz_id,
            question_text=data.question_text,
            order=order,
        )
        self.db.add(question)
        self.db.flush()

        for idx, text in enumerate(data.options):
            opt = QuizOption(
                question_id=question.id,
                option_text=text,
                is_correct=(idx == data.correct_index),
            )
            self.db.add(opt)

        self.db.commit()
        self.db.refresh(question)
        return question

    def update_question(
        self, question_id: int, data: QuestionUpdate, current_user: User
    ) -> QuizQuestion:
        question = self.db.get(QuizQuestion, question_id)
        if not question:
            raise QuestionNotFoundError("Question not found")

        quiz = question.quiz
        if current_user.role != "admin" and quiz.teacher_id != current_user.id:
            raise QuestionForbiddenError("Чужой тест")

        if quiz.is_published:
            raise QuizAlreadyPublishedError("Опубликованный тест")

        if data.question_text is not None:
            question.question_text = data.question_text

        if data.options is not None:
            if data.correct_index is None or data.correct_index >= len(data.options):
                raise InvalidCorrectIndexError("correct_index больше числа вариантов")

            # remove old options
            for opt in list(question.options):
                self.db.delete(opt)
            self.db.flush()

            for idx, text in enumerate(data.options):
                opt = QuizOption(
                    question_id=question.id,
                    option_text=text,
                    is_correct=(idx == data.correct_index),
                )
                self.db.add(opt)

        self.db.commit()
        self.db.refresh(question)
        return question

    def delete_question(self, question_id: int, current_user: User) -> None:
        question = self.db.get(QuizQuestion, question_id)
        if not question:
            raise QuestionNotFoundError("Question not found")

        quiz = question.quiz
        if current_user.role != "admin" and quiz.teacher_id != current_user.id:
            raise QuestionForbiddenError("Чужой тест")

        if quiz.is_published:
            raise QuizAlreadyPublishedError("Опубликованный тест")

        self.db.delete(question)
        self.db.commit()
