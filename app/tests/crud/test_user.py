from app.crud.user import (
    get_user_by_email,
    create_user,
    authenticate_user,
    get_user_by_id,
    update_user,
    delete_user,
    get_users_by_team_id,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password


def make_user(
    email: str = "test@example.com",
    hashed_password: str = "hashed_pass",
    full_name: str = "Test User",
    role: str = "user",
    is_active: bool = True,
    team_id: int | None = None,
) -> User:
    return User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        is_active=is_active,
        team_id=team_id,
    )


def test_get_user_by_email_found(db_session):
    user = make_user()
    db_session.add(user)
    db_session.commit()

    found_user = get_user_by_email(db_session, "test@example.com")

    assert found_user is not None
    assert found_user.email == "test@example.com"


def test_get_user_by_email_not_found(db_session):
    found_user = get_user_by_email(db_session, "missing@example.com")

    assert found_user is None


def test_create_user(db_session):
    user_in = UserCreate(
        email="newuser@example.com",
        password="12345678",
        full_name="New User",
    )

    created_user = create_user(db_session, user_in)

    assert created_user.id is not None
    assert created_user.email == "newuser@example.com"
    assert created_user.full_name == "New User"
    assert created_user.role == "user"
    assert created_user.hashed_password != "12345678"
    assert verify_password("12345678", created_user.hashed_password)


def test_authenticate_user_success(db_session):
    user_in = UserCreate(
        email="auth@example.com",
        password="qwerty123",
        full_name="Auth User",
    )
    create_user(db_session, user_in)

    auth_user = authenticate_user(db_session, "auth@example.com", "qwerty123")

    assert auth_user is not None
    assert auth_user.email == "auth@example.com"


def test_authenticate_user_wrong_password(db_session):
    user_in = UserCreate(
        email="auth2@example.com",
        password="qwerty123",
        full_name="Auth User 2",
    )
    create_user(db_session, user_in)

    auth_user = authenticate_user(db_session, "auth2@example.com", "wrongpass")

    assert auth_user is None


def test_authenticate_user_not_found(db_session):
    auth_user = authenticate_user(
        db_session,
        "missing@example.com",
        "12345678",
    )
    assert auth_user is None


def test_get_user_by_id_found(db_session):
    user = make_user(email="idtest@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    found_user = get_user_by_id(db_session, user.id)

    assert found_user is not None
    assert found_user.id == user.id


def test_get_user_by_id_not_found(db_session):
    found_user = get_user_by_id(db_session, 999)

    assert found_user is None


def test_update_user_full_name_and_email(db_session):
    user = make_user(email="old@example.com", full_name="Old Name")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_in = UserUpdate(
        email="new@example.com",
        full_name="New Name",
    )

    updated_user = update_user(db_session, user, user_in)

    assert updated_user.email == "new@example.com"
    assert updated_user.full_name == "New Name"


def test_update_user_password(db_session):
    user_in_create = UserCreate(
        email="passupdate@example.com",
        password="oldpassword",
        full_name="Password User",
    )
    user = create_user(db_session, user_in_create)

    user_in_update = UserUpdate(password="newpassword123")

    updated_user = update_user(db_session, user, user_in_update)

    assert verify_password("newpassword123", updated_user.hashed_password)
    assert not verify_password("oldpassword", updated_user.hashed_password)


def test_delete_user(db_session):
    user = make_user(email="delete@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    delete_user(db_session, user)

    deleted_user = get_user_by_id(db_session, user.id)
    assert deleted_user is None


def test_get_users_by_team_id(db_session):
    user1 = make_user(email="user1@example.com", team_id=1)
    user2 = make_user(email="user2@example.com", team_id=1)
    user3 = make_user(email="user3@example.com", team_id=2)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    users = get_users_by_team_id(db_session, 1)

    assert len(users) == 2
    emails = [user.email for user in users]
    assert "user1@example.com" in emails
    assert "user2@example.com" in emails
    assert "user3@example.com" not in emails
