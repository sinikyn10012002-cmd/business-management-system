from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.meetings import router
from app.api import meetings as meetings_module
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.tests.api.utils import make_user, build_client


def _client(fake_db, current_user):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: current_user
    return TestClient(app)


def test_create_meeting_overlap(monkeypatch, fake_db):
    current_user = make_user(user_id=1, role="user")

    monkeypatch.setattr(
        meetings_module,
        "has_meeting_overlap",
        lambda db, user_id, start_time, end_time: user_id == 2,
    )

    client = _client(fake_db, current_user)

    response = client.post(
        "/meetings/",
        json={
            "title": "Sync",
            "description": "Daily sync",
            "start_time": "2026-04-07T10:00:00",
            "end_time": "2026-04-07T11:00:00",
            "participant_ids": [2, 3],
        },
    )

    assert response.status_code == 400
    assert "уже есть встреча" in response.json()["detail"]


def test_get_my_meetings(monkeypatch, fake_db):
    current_user = make_user(user_id=1)
    meetings = [
        {
            "id": 1,
            "title": "Meet 1",
            "description": "Desc",
            "start_time": "2026-04-07T10:00:00",
            "end_time": "2026-04-07T11:00:00",
            "organizer_id": 1,
            "participants": [
                {
                    "id": 1,
                    "email": "user1@test.com",
                    "full_name": "User One",
                },
                {
                    "id": 2,
                    "email": "user2@test.com",
                    "full_name": "User Two",
                },
            ],
        }
    ]

    monkeypatch.setattr(
        meetings_module, "get_user_meetings", lambda db, user_id: meetings
    )

    client = _client(fake_db, current_user)
    response = client.get("/meetings/my")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Meet 1"
    assert len(response.json()[0]["participants"]) == 2


def test_cancel_meeting_not_found(monkeypatch, fake_db):
    current_user = make_user(user_id=1)
    monkeypatch.setattr(
        meetings_module, "get_meeting_by_id", lambda db, meeting_id: None
    )

    client = _client(fake_db, current_user)
    response = client.delete("/meetings/5")

    assert response.status_code == 404
    assert response.json()["detail"] == "Встреча не найдена"


def test_cancel_meeting_only_organizer(monkeypatch, fake_db):
    current_user = make_user(user_id=1)
    meeting = SimpleNamespace(id=5, organizer_id=2)

    monkeypatch.setattr(
        meetings_module, "get_meeting_by_id", lambda db, meeting_id: meeting
    )

    client = _client(fake_db, current_user)
    response = client.delete("/meetings/5")

    assert response.status_code == 403
    assert response.json()["detail"] == "Только организатор может отменить встречу"
