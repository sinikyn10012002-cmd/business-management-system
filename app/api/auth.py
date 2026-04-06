from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.token import LoginRequest, Token
from app.crud.user import (
    create_user,
    get_user_by_email,
    authenticate_user,
    update_user,
    delete_user,
)
from app.db.session import get_db
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.dependencies.roles import role_required


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    Регистрация нового пользователя.

    Проверяет, существует ли пользователь с таким email.
    Если email свободен — создает нового пользователя.

    :param user_in: Данные для регистрации (email, пароль, имя)
    :param db: Сессия базы данных
    :return: Созданный пользователь
    """
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    user = create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
def login(user_in: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """
    Аутентификация пользователя.

    Проверяет email и пароль. Если данные верны —
    возвращает JWT токен.

    :param user_in: Данные для входа (email, пароль)
    :param db: Сессия базы данных
    :return: JWT токен
    """
    user = authenticate_user(db, user_in.email, user_in.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    """
    Получить данные текущего авторизованного пользователя.

    :param current_user: Текущий пользователь
    :return: Данные пользователя
    """
    return current_user


@router.get("/admin-only")
def admin_only(current_user: User = Depends(role_required(["admin"]))) -> dict:
    """
    Доступ только для администратора.

    :param current_user: Текущий пользователь с ролью admin
    :return: Приветственное сообщение
    """
    return {"message": f"Hello, admin {current_user.email}"}


@router.patch("/me", response_model=UserRead)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Обновить данные текущего пользователя.

    Проверяет, не занят ли новый email другим пользователем.
    После этого обновляет данные пользователя.

    :param user_in: Новые данные пользователя
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Обновленный пользователь
    """
    if user_in.email is not None:
        existing_user = get_user_by_email(db, user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

    user = update_user(db, current_user, user_in)
    return user


@router.delete("/me")
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Удалить аккаунт текущего пользователя.

    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Сообщение об успешном удалении
    """
    delete_user(db, current_user)
    return {"detail": "Account deleted successfully"}
