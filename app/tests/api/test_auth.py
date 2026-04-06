from types import SimpleNamespace

from app.api.auth import router
from app.api import auth as auth_module
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.tests.api.utils import build_client


def make_auth_user(
    user_id: int = 1,
    email: str = "user@test.com",
    full_name: str | None = "Test User",
    role: str = "user",
    is_active: bool = True,
):
    return SimpleNamespace(
        id=user_id,
        email=email,
        full_name=full_name,
        role=role,
        is_active=is_active,
    )


def test_register_success(monkeypatch, fake_db):
    created_user = make_auth_user(
        user_id=1,
        email="new@test.com",
        full_name="New User",
        role="user",
        is_active=True,
    )

    monkeypatch.setattr(auth_module, "get_user_by_email", lambda db, email: None)
    monkeypatch.setattr(auth_module, "create_user", lambda db, user_in: created_user)

    client = build_client(router, get_db_dep=get_db, fake_db=fake_db)

    response = client.post(
        "/auth/register",
        json={
            "email": "new@test.com",
            "password": "12345678",
            "full_name": "New User",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "new@test.com"


def test_register_duplicate_email(monkeypatch, fake_db):
    existing_user = make_auth_user(
        user_id=1,
        email="exists@test.com",
        full_name="User",
        role="user",
        is_active=True,
    )

    monkeypatch.setattr(
        auth_module, "get_user_by_email", lambda db, email: existing_user
    )

    client = build_client(router, get_db_dep=get_db, fake_db=fake_db)

    response = client.post(
        "/auth/register",
        json={
            "email": "exists@test.com",
            "password": "12345678",
            "full_name": "User",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success(monkeypatch, fake_db):
    user = make_auth_user(
        user_id=10,
        email="user@test.com",
        full_name="Test User",
        role="user",
        is_active=True,
    )

    monkeypatch.setattr(
        auth_module, "authenticate_user", lambda db, email, password: user
    )
    monkeypatch.setattr(auth_module, "create_access_token", lambda data: "test-token")

    client = build_client(router, get_db_dep=get_db, fake_db=fake_db)

    response = client.post(
        "/auth/login",
        json={
            "email": "user@test.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "test-token"
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(monkeypatch, fake_db):
    monkeypatch.setattr(
        auth_module, "authenticate_user", lambda db, email, password: None
    )

    client = build_client(router, get_db_dep=get_db, fake_db=fake_db)

    response = client.post(
        "/auth/login",
        json={
            "email": "bad@test.com",
            "password": "wrong",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_read_me(fake_db):
    current_user = make_auth_user(
        user_id=1,
        email="me@test.com",
        full_name="Me User",
        role="user",
        is_active=True,
    )

    client = build_client(
        router,
        get_db_dep=get_db,
        get_current_user_dep=get_current_user,
        current_user=current_user,
        fake_db=fake_db,
    )

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"


def test_update_me_success(monkeypatch, fake_db):
    current_user = make_auth_user(
        user_id=1,
        email="old@test.com",
        full_name="Old Name",
        role="user",
        is_active=True,
    )
    updated_user = make_auth_user(
        user_id=1,
        email="new@test.com",
        full_name="New Name",
        role="user",
        is_active=True,
    )

    monkeypatch.setattr(auth_module, "get_user_by_email", lambda db, email: None)
    monkeypatch.setattr(
        auth_module, "update_user", lambda db, user, user_in: updated_user
    )

    client = build_client(
        router,
        get_db_dep=get_db,
        get_current_user_dep=get_current_user,
        current_user=current_user,
        fake_db=fake_db,
    )

    response = client.patch(
        "/auth/me",
        json={
            "email": "new@test.com",
            "full_name": "New Name",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "new@test.com"


def test_update_me_duplicate_email(monkeypatch, fake_db):
    current_user = make_auth_user(
        user_id=1,
        email="me@test.com",
        full_name="Me User",
        role="user",
        is_active=True,
    )
    another_user = make_auth_user(
        user_id=2,
        email="taken@test.com",
        full_name="Taken User",
        role="user",
        is_active=True,
    )

    monkeypatch.setattr(
        auth_module, "get_user_by_email", lambda db, email: another_user
    )

    client = build_client(
        router,
        get_db_dep=get_db,
        get_current_user_dep=get_current_user,
        current_user=current_user,
        fake_db=fake_db,
    )

    response = client.patch(
        "/auth/me",
        json={"email": "taken@test.com"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_delete_me(monkeypatch, fake_db):
    current_user = make_auth_user(
        user_id=1,
        email="me@test.com",
        full_name="Me User",
        role="user",
        is_active=True,
    )
    called = {"deleted": False}

    def fake_delete_user(db, user):
        called["deleted"] = True

    monkeypatch.setattr(auth_module, "delete_user", fake_delete_user)

    client = build_client(
        router,
        get_db_dep=get_db,
        get_current_user_dep=get_current_user,
        current_user=current_user,
        fake_db=fake_db,
    )

    response = client.delete("/auth/me")

    assert response.status_code == 200
    assert response.json()["detail"] == "Account deleted successfully"
    assert called["deleted"] is True
