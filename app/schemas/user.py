from enum import Enum
from pydantic import UUID4, BaseModel, ConfigDict, Field
from app.config import settings


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., min_length=1)
    role: Role

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN


class User(BaseUser):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4


class UserInDB(BaseUser):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4 | None = None
    hashed_password: str


class UserCreate(BaseUser):
    password: str = Field(..., min_length=settings.auth_password_min_length)
