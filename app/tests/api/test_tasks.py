from datetime import datetime
from types import SimpleNamespace

from app.api.task import router
from app.api import task as task_module
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


def test_get_tasks_admin_gets_all(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="admin")
    tasks = [
        SimpleNamespace(
            id=1,
            title="T1",
            description="Desc 1",
            deadline=datetime(2026, 4, 10, 10, 0, 0),
            status="open",
            author_id=1,
            executor_id=2,
            team_id=10,
            created_at=datetime(2026, 4, 1, 10, 0, 0),
        ),
        SimpleNamespace(
            id=2,
            title="T2",
            description="Desc 2",
            deadline=datetime(2026, 4, 11, 10, 0, 0),
            status="in_progress",
            author_id=1,
            executor_id=3,
            team_id=10,
            created_at=datetime(2026, 4, 1, 11, 0, 0),
        ),
    ]

    monkeypatch.setattr(task_module, "get_all_tasks", lambda db: tasks)

    client = _client(fake_db, current_user)
    response = client.get("/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_tasks_manager_without_team(fake_db):
    current_user = make_user(user_id=2, role="manager", team_id=None)

    client = _client(fake_db, current_user)
    response = client.get("/tasks/")

    assert response.status_code == 400
    assert response.json()["detail"] == "Manager is not in a team"


def test_create_task_executor_not_found(monkeypatch, fake_db):
    current_user = make_user(user_id=2, role="manager", team_id=10)

    monkeypatch.setattr(task_module, "get_user_by_id", lambda db, user_id: None)

    client = _client(fake_db, current_user)

    response = client.post(
        "/tasks/",
        json={
            "title": "Task 1",
            "description": "Desc",
            "deadline": "2026-04-10T10:00:00",
            "executor_id": 99,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Executor not found"


def test_create_task_executor_in_another_team(monkeypatch, fake_db):
    current_user = make_user(user_id=2, role="manager", team_id=10)
    executor = make_user(user_id=5, role="user", team_id=99)

    monkeypatch.setattr(task_module, "get_user_by_id", lambda db, user_id: executor)

    client = _client(fake_db, current_user)

    response = client.post(
        "/tasks/",
        json={
            "title": "Task 1",
            "description": "Desc",
            "deadline": "2026-04-10T10:00:00",
            "executor_id": 5,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Executor is not in your team"


def test_delete_task_only_author(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="user")
    task = SimpleNamespace(id=10, author_id=2)

    monkeypatch.setattr(task_module, "get_task_by_id", lambda db, task_id: task)

    client = _client(fake_db, current_user)
    response = client.delete("/tasks/10")

    assert response.status_code == 403
    assert response.json()["detail"] == "Only author can delete this task"


def test_change_status_only_executor(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="user")
    task = SimpleNamespace(id=10, executor_id=2, status="open")

    monkeypatch.setattr(task_module, "get_task_by_id", lambda db, task_id: task)

    client = _client(fake_db, current_user)
    response = client.patch("/tasks/10/status", params={"status_value": "done"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Only executor can change status"


def test_change_status_invalid_status(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="user")
    task = SimpleNamespace(id=10, executor_id=1, status="open")

    monkeypatch.setattr(task_module, "get_task_by_id", lambda db, task_id: task)

    client = _client(fake_db, current_user)
    response = client.patch("/tasks/10/status", params={"status_value": "bad_status"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status"


def test_add_comment_for_foreign_team(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="user", team_id=10)
    task = SimpleNamespace(id=10, team_id=99)

    monkeypatch.setattr(task_module, "get_task_by_id", lambda db, task_id: task)

    client = _client(fake_db, current_user)
    response = client.post("/tasks/10/comments", json={"text": "Hello"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Not your team task"


def test_get_task_not_found(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="admin")

    monkeypatch.setattr(task_module, "get_task_by_id", lambda db, task_id: None)

    client = _client(fake_db, current_user)
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
