from collections.abc import Sequence
import json
import uuid
from app.models.ecg import ECGDAL, ECG as ECGModel, SignalDAL, Signal as SignalModel
from app.schemas.ecg import ECG, LeadName, Signal
from polyfactory.factories.pydantic_factory import ModelFactory
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import User


class ECGFactory(ModelFactory[ECG]):
    __faker__ = Faker()


class SignalFactory(ModelFactory[Signal]):
    __faker__ = Faker()

    @classmethod
    def name(cls) -> str:
        return cls.__faker__.random_element(
            elements=[
                "I",
                "II",
                "III",
                "aVR",
                "aVL",
                "aVF",
                "V1",
                "V2",
                "V3",
                "V4",
                "V5",
                "V6",
            ]
        )

    @classmethod
    def signal_value(cls) -> int:
        return cls.__faker__.random_int(min=-100, max=100)


def generate_signals(ecg_id, count) -> Sequence[Signal]:
    return (
        SignalFactory.build(ecg=ecg_id, signal_value_index=k, name=lead_name.value)
        for k in range(count)
        for lead_name in LeadName
    )


def generate_ecg_input(num_signals: int = 100) -> str:
    """Generate a JSON string for an ECG input"""
    faker = Faker()
    lead_names = [e.value for e in LeadName]
    data = {
        "id": faker.uuid4(),
        "date": str(faker.date_this_month()),
        "leads": [
            {
                "name": name,
                "signal": [
                    faker.random_int(min=-100, max=100) for _ in range(num_signals)
                ],
            }
            for name in lead_names
        ],
    }
    return json.dumps(data)


async def generate_ecg_with_random_signals(
    db_session: AsyncSession, user: User, num_signals: int = 10
) -> uuid.UUID:
    """Generate a ECG with random signals"""
    ecg_dal = ECGDAL(db_session)
    ecg_id = uuid.uuid4()
    await ecg_dal.create(ECGModel(id=ecg_id, user_id=user.id))

    # Generate signals
    signal_dal = SignalDAL(db_session)
    await signal_dal.create_bulk(
        (
            SignalModel(
                ecg_id=s.ecg,
                date=s.date,
                name=s.name,
                signal_value=s.signal_value,
                signal_value_index=s.signal_value_index,
            )
            for s in generate_signals(ecg_id, num_signals)
        )
    )
    return ecg_id
