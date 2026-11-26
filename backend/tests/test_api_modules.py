from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_auth_register_and_login():
    # 422 on short password
    res = client.post(
        "/api/auth/register",
        json={
            "username": "u1",
            "email": "u1@test.kz",
            "password": "123",
            "role": "student",
        },
    )
    assert res.status_code == 422

    # 422 on admin role in body
    res = client.post(
        "/api/auth/register",
        json={
            "username": "u2",
            "email": "u2@test.kz",
            "password": "password123",
            "role": "admin",
        },
    )
    assert res.status_code == 422

    rand_suffix = uuid4().hex[:8]
    unique_email = f"student_{rand_suffix}@test.kz"
    unique_username = f"user_{rand_suffix}"

    # 201 success
    res = client.post(
        "/api/auth/register",
        json={
            "username": unique_username,
            "email": unique_email,
            "password": "password123",
            "role": "student",
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert "password" not in body
    assert body["email"] == unique_email

    # 409 duplicate email
    res = client.post(
        "/api/auth/register",
        json={
            "username": f"another_{rand_suffix}",
            "email": unique_email,
            "password": "password123",
            "role": "student",
        },
    )
    assert res.status_code == 409

    # 200 login
    res = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "password123"},
    )
    assert res.status_code == 200

    # 401 wrong password
    res = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "wrong"},
    )
    assert res.status_code == 401


def test_users_admin_rules():
    # student -> 403
    res = client.get("/api/users", headers={"X-User-Email": "student@demo.kz"})
    assert res.status_code == 403

    # teacher -> 403
    res = client.get("/api/users", headers={"X-User-Email": "teacher@demo.kz"})
    assert res.status_code == 403

    # admin -> 200
    res = client.get("/api/users", headers={"X-User-Email": "admin@demo.kz"})
    assert res.status_code == 200
    users = res.json()
    admin_user = next(u for u in users if u["email"] == "admin@demo.kz")

    # change own role -> 400
    res = client.patch(
        f"/api/users/{admin_user['id']}",
        json={"role": "student"},
        headers={"X-User-Email": "admin@demo.kz"},
    )
    assert res.status_code == 400

    # delete self -> 400
    res = client.delete(
        f"/api/users/{admin_user['id']}",
        headers={"X-User-Email": "admin@demo.kz"},
    )
    assert res.status_code == 400


def test_quizzes_and_questions_and_attempts():
    # 1. Teacher creates quiz -> 201
    res = client.post(
        "/api/quizzes",
        json={"title": "Жаңа тест", "description": "Сипаттама"},
        headers={"X-User-Email": "teacher@demo.kz"},
    )
    assert res.status_code == 201
    quiz_id = res.json()["id"]

    # 2. Cannot publish without questions -> 400
    res = client.post(
        f"/api/quizzes/{quiz_id}/publish",
        headers={"X-User-Email": "teacher@demo.kz"},
    )
    assert res.status_code == 400

    # 3. Add question with correct_index >= len(options) -> 400
    res = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Сұрақ 1",
            "options": ["А", "Б"],
            "correct_index": 2,
        },
        headers={"X-User-Email": "teacher@demo.kz"},
    )
    assert res.status_code == 400

    # 4. Add valid question -> 201
    res = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Сұрақ 1",
            "options": ["А", "Б", "В"],
            "correct_index": 1,
        },
        headers={"X-User-Email": "teacher@demo.kz"},
    )
    assert res.status_code == 201
    question_data = res.json()
    q_id = question_data["id"]
    correct_opt_id = question_data["options"][1]["id"]

    # 5. Publish quiz -> 200
    res = client.post(
        f"/api/quizzes/{quiz_id}/publish",
        headers={"X-User-Email": "teacher@demo.kz"},
    )
    assert res.status_code == 200
    assert res.json()["is_published"] is True

    # 6. Cannot add questions to published quiz -> 400
    res = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Сұрақ 2",
            "options": ["А", "Б"],
            "correct_index": 0,
        },
        headers={"X-User-Email": "teacher@demo.kz"},
    )
    assert res.status_code == 400

    # 7. Student gets quiz -> doesn't see is_correct
    res = client.get(
        f"/api/quizzes/{quiz_id}",
        headers={"X-User-Email": "student@demo.kz"},
    )
    assert res.status_code == 200
    quiz_detail = res.json()
    for opt in quiz_detail["questions"][0]["options"]:
        assert opt["is_correct"] is None

    # 8. Student submits attempt with wrong answer count -> 400 or 422
    res = client.post(
        f"/api/quizzes/{quiz_id}/attempts",
        json={"answers": []},
        headers={"X-User-Email": "student@demo.kz"},
    )
    assert res.status_code in (400, 422)

    # 9. Student submits attempt with valid answers -> 201
    res = client.post(
        f"/api/quizzes/{quiz_id}/attempts",
        json={
            "answers": [
                {"question_id": q_id, "selected_option_id": correct_opt_id}
            ]
        },
        headers={"X-User-Email": "student@demo.kz"},
    )
    assert res.status_code == 201
    assert res.json()["score"] == 1

    # 10. Student checks my attempts -> 200
    res = client.get(
        "/api/attempts/me",
        headers={"X-User-Email": "student@demo.kz"},
    )
    assert res.status_code == 200
    assert len(res.json()) >= 1
