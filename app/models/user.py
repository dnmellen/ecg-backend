from typing import Literal, get_args
import uuid
from sqlalchemy import String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.dal import EntityDAL

from . import Base

Role = Literal["admin", "user"]


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, unique=True)
    role: Mapped[Role] = mapped_column(
        Enum(
            *get_args(Role),
            name="campaignstatus",
            create_constraint=True,
            validate_strings=True,
            nullable=False,
        )
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    ecgs: Mapped[list["ECG"]] = relationship(  # noqa F821
        "ECG", back_populates="user", cascade="all, delete-orphan"
    )


class UserDAL(EntityDAL[User]):
    """Data Access Layer for User entities"""

    model = User

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_by_field("username", username)
