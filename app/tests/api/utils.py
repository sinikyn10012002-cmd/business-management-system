from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient


def make_user(
    user_id: int = 1,
    email: str = "user@test.com",
    role: str = "user",
    team_id: int | None = None,
    full_name: str = "Test User",
):
    return SimpleNamespace(
        id=user_id,
        email=email,
        role=role,
        team_id=team_id,
        full_name=full_name,
    )


def build_client(
    router,
    get_db_dep=None,
    get_current_user_dep=None,
    current_user=None,
    fake_db=None,
):
    app = FastAPI()
    app.include_router(router)

    if get_db_dep is not None:
        app.dependency_overrides[get_db_dep] = lambda: fake_db

    if get_current_user_dep is not None and current_user is not None:
        app.dependency_overrides[get_current_user_dep] = lambda: current_user

    return TestClient(app)
