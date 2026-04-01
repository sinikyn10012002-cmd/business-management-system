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
from app.dependencies.auth import get_current_user, role_required


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
def login(user_in: LoginRequest, db: Session = Depends(get_db)):
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
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


# @router.get("/me", response_model=UserRead)
# def read_me(current_user: User = Depends(get_current_user)):
#    return current_user


@router.get("/admin-only")
def admin_only(current_user: User = Depends(role_required(["admin"]))):
    return {"message": f"Hello, admin {current_user.email}"}


@router.patch("/me", response_model=UserRead)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_in.email is not None:
        existing_user = get_user_by_email(db, user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = update_user(db, current_user, user_in)
        return user


@router.delete("/me")
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_user(db, current_user)
    return {"detail": "Account deleted successfully"}
