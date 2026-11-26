from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRegisterRequest(BaseModel):
    username: str = Field(
        ..., min_length=2, max_length=64, description="Пайдаланушы аты"
    )
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Email",
    )
    password: str = Field(..., min_length=6, description="Пароль (кемінде 6 таңба)")
    role: str = Field(default="student", description="Рөлі: student немесе teacher")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean == "admin":
            raise ValueError("admin рөлімен өздігінен тіркелуге болмайды")
        if v_clean not in ("student", "teacher"):
            raise ValueError("Рөл тек student немесе teacher болуы керек")
        return v_clean


class UserLoginRequest(BaseModel):
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Email",
    )
    password: str = Field(..., min_length=1, description="Пароль")


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    created_at: datetime
