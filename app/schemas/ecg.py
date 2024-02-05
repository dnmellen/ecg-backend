from enum import Enum
from datetime import date, datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field, Json


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


class AnalysisStatus(str, Enum):
    """Analysis status"""

    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DataAnalysis(BaseModel):
    """Data analysis"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4 | None = None
    ecg_id: UUID4
    created: datetime = Field(default_factory=datetime.now)
    finished: datetime | None = None
    name: str
    status: AnalysisStatus = Field(default=AnalysisStatus.CREATED)
    result: Json

    @property
    def duration(self) -> float:
        """Analysis duration"""
        return (self.finished - self.created).total_seconds()


class ECGDetail(ECG):
    """ECG data with signals"""

    model_config = ConfigDict(from_attributes=True)

    analyses: list[DataAnalysis]
