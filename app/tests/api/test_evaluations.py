from types import SimpleNamespace

from app.api.evaluations import router
from app.api import evaluations as evaluations_module
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.tests.api.utils import make_user, build_client


def _client(fake_db, current_user):
    return build_client(
        router,
        get_db_dep=get_db,
        get_current_user_dep=get_current_user,
        current_user=current_user,
        fake_db=fake_db,
    )


def test_evaluate_task_not_found(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="manager", team_id=10)

    monkeypatch.setattr(evaluations_module, "get_task_by_id", lambda db, task_id: None)

    client = _client(fake_db, current_user)

    response = client.post(
        "/evaluations/", json={"task_id": 1, "score": 5, "comment": "Good"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_evaluate_task_not_completed(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="manager", team_id=10)
    task = SimpleNamespace(id=1, status="open", team_id=10, executor_id=5)

    monkeypatch.setattr(evaluations_module, "get_task_by_id", lambda db, task_id: task)

    client = _client(fake_db, current_user)

    response = client.post(
        "/evaluations/", json={"task_id": 1, "score": 5, "comment": "Good"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Task is not completed"


def test_evaluate_task_foreign_team(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="manager", team_id=10)
    task = SimpleNamespace(id=1, status="done", team_id=99, executor_id=5)

    monkeypatch.setattr(evaluations_module, "get_task_by_id", lambda db, task_id: task)
    monkeypatch.setattr(
        evaluations_module, "get_evaluation_by_task_id", lambda db, task_id: None
    )

    client = _client(fake_db, current_user)

    response = client.post(
        "/evaluations/", json={"task_id": 1, "score": 5, "comment": "Good"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not your team task"


def test_evaluate_task_already_evaluated(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="manager", team_id=10)
    task = SimpleNamespace(id=1, status="done", team_id=10, executor_id=5)
    existing = SimpleNamespace(id=100)

    monkeypatch.setattr(
        evaluations_module,
        "get_task_by_id",
        lambda db, task_id: task,
    )
    monkeypatch.setattr(
        evaluations_module,
        "get_evaluation_by_task_id",
        lambda db, task_id: existing,
    )

    client = _client(fake_db, current_user)

    response = client.post(
        "/evaluations/", json={"task_id": 1, "score": 5, "comment": "Good"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Task already evaluated"


def test_average_score(monkeypatch, fake_db):
    current_user = make_user(user_id=5, role="user")
    monkeypatch.setattr(
        evaluations_module, "get_average_score", lambda db, user_id: 4.7
    )

    client = _client(fake_db, current_user)
    response = client.get("/evaluations/average")

    assert response.status_code == 200
    assert response.json()["average_score"] == 4.7
