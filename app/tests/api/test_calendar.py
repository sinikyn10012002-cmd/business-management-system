from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.calendar import router
from app.api import calendar as calendar_module
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.tests.api.utils import make_user


def _client(fake_db, current_user):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: current_user
    return TestClient(app)


def test_get_calendar_day(monkeypatch, fake_db):
    current_user = make_user(user_id=1)

    monkeypatch.setattr(
        calendar_module,
        "build_day_calendar",
        lambda db, user_id, target_date: [
            {
                "item_type": "task",
                "id": 1,
                "title": "Task 1",
                "date": target_date,
                "time": "10:00",
                "status": "open",
            },
            {
                "item_type": "meeting",
                "id": 2,
                "title": "Meet 1",
                "date": target_date,
                "time": "12:00",
                "status": None,
            },
        ],
    )

    client = _client(fake_db, current_user)
    response = client.get("/calendar/day", params={"day": "2026-04-07"})

    assert response.status_code == 200
    assert response.json()["day"] == "2026-04-07"
    assert len(response.json()["items"]) == 2
    assert response.json()["items"][0]["item_type"] == "task"
    assert response.json()["items"][1]["item_type"] == "meeting"


def test_get_calendar_month(monkeypatch, fake_db):
    current_user = make_user(user_id=1)

    monkeypatch.setattr(
        calendar_module,
        "build_month_calendar",
        lambda db, user_id, year, month: [
            {"day": "2026-04-07", "items": []},
            {"day": "2026-04-08", "items": []},
        ],
    )

    client = _client(fake_db, current_user)
    response = client.get("/calendar/month", params={"year": 2026, "month": 4})

    assert response.status_code == 200
    assert response.json()["year"] == 2026
    assert response.json()["month"] == 4
    assert len(response.json()["days"]) == 2
