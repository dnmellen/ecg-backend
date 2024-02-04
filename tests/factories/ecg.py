from collections.abc import Sequence
import json
from app.schemas.ecg import ECG, LeadName, Signal
from polyfactory.factories.pydantic_factory import ModelFactory
from faker import Faker


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
    return (SignalFactory.build(ecg=ecg_id, signal_value_index=k) for k in range(count))


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
