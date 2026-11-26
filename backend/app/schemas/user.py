from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=64)
    role: str | None = Field(default=None)


class UserAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    created_at: datetime
