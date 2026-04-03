from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    email: Optional[str] = None
    password: Optional[str] = None


class UserOut(UserBase):
    id: int
    role: str
    team_id: Optional[int] = None

    class Config:
        from_attributes = True
