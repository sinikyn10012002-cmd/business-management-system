from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user
from app.models.user import User


def role_required(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return role_checker
