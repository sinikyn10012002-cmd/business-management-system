from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.teams import router
from app.api import teams as teams_module
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.tests.api.utils import make_user


def _client(fake_db, current_user):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: current_user
    return TestClient(app)


def test_join_team_success(monkeypatch, fake_db):
    current_user = make_user(user_id=1, team_id=None)
    team = SimpleNamespace(id=10, name="Alpha", code="ABC123")
    called = {"ok": False}

    monkeypatch.setattr(
        teams_module,
        "get_team_by_code",
        lambda db, code: team,
    )

    def fake_add_user_to_team(db, user, team_obj):
        called["ok"] = True

    monkeypatch.setattr(
        teams_module,
        "add_user_to_team",
        fake_add_user_to_team,
    )

    client = _client(fake_db, current_user)

    response = client.post("/teams/join", json={"code": "ABC123"})

    assert response.status_code == 200
    assert response.json()["detail"] == "You joined team Alpha"
    assert called["ok"] is True


def test_join_team_not_found(monkeypatch, fake_db):
    current_user = make_user(user_id=1, team_id=None)

    monkeypatch.setattr(
        teams_module,
        "get_team_by_code",
        lambda db, code: None,
    )

    client = _client(fake_db, current_user)

    response = client.post("/teams/join", json={"code": "BAD"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found"


def test_join_team_already_in_same_team(monkeypatch, fake_db):
    current_user = make_user(user_id=1, team_id=10)
    team = SimpleNamespace(id=10, name="Alpha", code="ABC123")

    monkeypatch.setattr(
        teams_module,
        "get_team_by_code",
        lambda db, code: team,
    )

    client = _client(fake_db, current_user)

    response = client.post("/teams/join", json={"code": "ABC123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "You are already in this team"


def test_join_team_already_in_another_team(monkeypatch, fake_db):
    current_user = make_user(user_id=1, team_id=99)
    team = SimpleNamespace(id=10, name="Alpha", code="ABC123")

    monkeypatch.setattr(
        teams_module,
        "get_team_by_code",
        lambda db, code: team,
    )

    client = _client(fake_db, current_user)

    response = client.post("/teams/join", json={"code": "ABC123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "You are already in another team"


def test_get_team_members_success(monkeypatch, fake_db):
    current_user = make_user(user_id=1, team_id=10)
    users = [
        make_user(user_id=1, email="a@test.com", team_id=10),
        make_user(user_id=2, email="b@test.com", team_id=10),
    ]

    monkeypatch.setattr(
        teams_module,
        "get_users_by_team_id",
        lambda db, team_id: users,
    )

    client = _client(fake_db, current_user)

    response = client.get("/teams/members")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_team_members_user_not_in_team(fake_db):
    current_user = make_user(user_id=1, team_id=None)

    client = _client(fake_db, current_user)

    response = client.get("/teams/members")

    assert response.status_code == 400
    assert response.json()["detail"] == "User is not in a team"


def test_change_user_role_user_not_found(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="admin", team_id=None)

    monkeypatch.setattr(
        teams_module,
        "get_user_by_id",
        lambda db, user_id: None,
    )

    client = _client(fake_db, current_user)

    response = client.patch(
        "/teams/role",
        json={"user_id": 99, "role": "manager"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_from_team_success(monkeypatch, fake_db):
    current_user = make_user(
        user_id=1,
        role="admin",
        team_id=None,
    )
    target_user = make_user(
        user_id=2,
        role="user",
        team_id=10,
    )
    called = {"ok": False}

    monkeypatch.setattr(
        teams_module,
        "get_user_by_id",
        lambda db, user_id: target_user,
    )

    def fake_remove_user_from_team(db, user):
        called["ok"] = True

    monkeypatch.setattr(
        teams_module,
        "remove_user_from_team",
        fake_remove_user_from_team,
    )

    client = _client(fake_db, current_user)

    response = client.delete("/teams/2")

    assert response.status_code == 200
    assert response.json()["detail"] == "User removed from team"
    assert called["ok"] is True
