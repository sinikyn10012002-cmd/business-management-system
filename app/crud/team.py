import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.team import Team
from app.models.user import User


def generate_team_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_team(db: Session, name: str) -> Team:
    code = generate_team_code()

    team = Team(
        name=name,
        code=code,
    )

    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team_by_code(db: Session, code: str) -> Team | None:
    result = db.execute(select(Team).where(Team.code == code))
    return result.scalar_one_or_none()


def add_user_to_team(db: Session, user: User, team: Team):
    user.team_id = team.id
    db.commit()
    db.refresh(user)
    return user


def remove_user_from_team(db: Session, user: User) -> User:
    user.team_id = None
    user.role = "user"
    db.commit()
    db.refresh(user)
    return user
