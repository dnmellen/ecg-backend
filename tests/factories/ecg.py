from collections.abc import Sequence
from app.schemas.ecg import ECG, Signal
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
