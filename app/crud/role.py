from sqlalchemy.orm import Session
from app.models.user import User


def update_user_role(db: Session, user: User, role: str) -> User:
    user.role = role
    db.commit()
    db.refresh(user)
    return user
