import datetime
from typing import Annotated, Sequence
import uuid
from sqlalchemy import Date, ForeignKey, Integer, String, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.dal import EntityDAL

from . import Base

uuidpk = Annotated[uuid.UUID, mapped_column(primary_key=True)]


class ECG(Base):
    __tablename__ = "ecg"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id")
    )
    user: Mapped["User"] = relationship("User", back_populates="ecgs")  # noqa F821

    signals: Mapped[list["Signal"]] = relationship(
        "Signal", back_populates="ecg", cascade="all, delete-orphan"
    )  # noqa F821


class ECGDAL(EntityDAL[ECG]):
    """Data Access Layer for ECG entities"""

    model = ECG

    async def get_by_user(self, user: uuid.UUID, egc_id: uuid.UUID) -> ECG | None:
        try:
            return (await self.list(and_(ECG.user_id == user, ECG.id == egc_id)))[0][0]
        except IndexError:
            return None

    async def list_by_user(self, user: uuid.UUID) -> Sequence[ECG]:
        return (e[0] for e in await self.list(ECG.user_id == user))


class Signal(Base):
    __tablename__ = "ecg_signal"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ecg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ecg.id"))
    ecg: Mapped[ECG] = relationship("ECG", back_populates="signals")
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    signal_value: Mapped[int] = mapped_column(Integer, nullable=False)
    signal_value_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # __table_args__ = (UniqueConstraint("ecg", "date", "name", "signal_value_index"),)


class SignalDAL(EntityDAL[Signal]):
    """Data Access Layer for Signal entities"""

    model = Signal

    async def get_by_ecg(self, ecg: uuid.UUID) -> Sequence[Signal]:
        return await self.list(Signal.ecg_id == ecg)
