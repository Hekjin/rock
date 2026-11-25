from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.quiz import QuizOption, QuizQuestion, QuizTest
from app.models.user import User


def seed_data() -> None:
    # 1. Create tables if not exist
    Base.metadata.create_all(bind=engine)
    print("Database tables ensured.")

    with SessionLocal() as db:
        users_data = [
            {
                "username": "teacher",
                "email": "teacher@demo.kz",
                "role": "teacher",
                "password": "password123",
            },
            {
                "username": "student",
                "email": "student@demo.kz",
                "role": "student",
                "password": "password123",
            },
            {
                "username": "admin",
                "email": "admin@demo.kz",
                "role": "admin",
                "password": "password123",
            },
        ]

        created_users = {}
        for u in users_data:
            existing = db.scalar(select(User).where(User.email == u["email"]))
            if not existing:
                user = User(
                    username=u["username"],
                    email=u["email"],
                    role=u["role"],
                    hashed_password=hash_password(u["password"]),
                )
                db.add(user)
                db.flush()
                created_users[u["role"]] = user
                print(f"Created user: {u['email']} ({u['role']})")
            else:
                created_users[u["role"]] = existing
                print(f"User already exists: {u['email']}")

        teacher = created_users.get("teacher")
        if teacher:
            existing_quiz = db.scalar(
                select(QuizTest).where(QuizTest.teacher_id == teacher.id)
            )
            if not existing_quiz:
                demo_quiz = QuizTest(
                    title="Демо тест (Математика)",
                    description="Жүйені тексеруге арналған бастапқы тест.",
                    teacher_id=teacher.id,
                    is_active=True,
                    is_published=True,
                )
                db.add(demo_quiz)
                db.flush()

                # Add a sample question with options
                q1 = QuizQuestion(
                    quiz_id=demo_quiz.id,
                    question_text="2 + 2 қанша болады?",
                    order=1,
                )
                db.add(q1)
                db.flush()

                opts = [
                    QuizOption(question_id=q1.id, option_text="3", is_correct=False),
                    QuizOption(question_id=q1.id, option_text="4", is_correct=True),
                    QuizOption(question_id=q1.id, option_text="5", is_correct=False),
                ]
                db.add_all(opts)
                print("Created demo published quiz with questions for teacher")
            else:
                print("Demo quiz already exists")

        db.commit()
        print("Seed completed successfully!")


if __name__ == "__main__":
    seed_data()
