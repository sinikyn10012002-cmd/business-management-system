from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.team import TeamCreate, TeamRead, JoinTeam
from app.crud.team import (
    create_team,
    get_team_by_code,
    add_user_to_team,
    remove_user_from_team,
)
from app.dependencies.roles import role_required
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserOut
from app.crud.user import get_users_by_team_id, get_user_by_id
from app.schemas.role import ChangeUserRole
from app.crud.role import update_user_role

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamRead)
def create_new_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("admin")),
):
    team = create_team(db, team_in.name)
    return team


@router.post("/join")
def join_team(
    data: JoinTeam,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = get_team_by_code(db, data.code)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if current_user.team_id == team.id:
        raise HTTPException(
            status_code=400,
            detail="You are already in this team",
        )

    if current_user.team_id is not None:
        raise HTTPException(
            status_code=400,
            detail="You are already in another team",
        )

    add_user_to_team(db, current_user, team)

    return {"detail": f"You joined team {team.name}"}


@router.get("/members", response_model=list[UserOut])
def get_team_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in a team",
        )

    members = get_users_by_team_id(db, current_user.team_id)
    return members


@router.patch("/role")
def change_user_role(
    data: ChangeUserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("admin")),
):
    user = get_user_by_id(db, data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change admin role",
        )

    if user.team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in a team",
        )

    update_user_role(db, user, data.role)

    return {"detail": f"User role updated to {data.role}"}


@router.delete("/{user_id}")
def delete_user_from_team(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("admin")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot remove himself from team",
        )

    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove admin from team",
        )

    if user.team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in a team",
        )

    remove_user_from_team(db, user)

    return {"detail": "User removed from team"}
