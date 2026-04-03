from pydantic import BaseModel, field_validator


class ChangeUserRole(BaseModel):
    user_id: int
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        allowed_roles = {"manager", "user"}
        if value not in allowed_roles:
            raise ValueError("Role must be 'manager' or 'user'")
        return value
