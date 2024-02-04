from enum import Enum
from datetime import date

from pydantic import UUID4, BaseModel, ConfigDict


class LeadName(str, Enum):
    """12-ECG lead names"""

    I = "I"  # noqa: E741
    II = "II"
    III = "III"
    aVR = "aVR"
    aVL = "aVL"
    aVF = "aVF"
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"


class Signal(BaseModel):
    """ECG signal data"""

    model_config = ConfigDict(from_attributes=True)

    ecg: UUID4
    date: date
    name: LeadName
    signal_value: int
    signal_value_index: int


class ECG(BaseModel):
    """ECG data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user: UUID4
