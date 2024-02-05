import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ecg import ECGDAL, ECG as ECGModel
from app.processors.num_crosses_zero import NumCrossesZeroSignalProcessor
from app.schemas.user import User
from tests.factories.ecg import generate_ecg_with_random_signals
from app.schemas.ecg import AnalysisStatus


@pytest.mark.asyncio
async def test_num_crosses_zero_signal_processor(
    db_session: AsyncSession, user: User
) -> None:
    ecg_id = await generate_ecg_with_random_signals(db_session, user)
    processor = NumCrossesZeroSignalProcessor(db_session)
    data_analysis = await processor.process(ecg_id)
    assert data_analysis.ecg_id == ecg_id
    assert data_analysis.name == "num_crosses_zero"
    assert data_analysis.status == AnalysisStatus.COMPLETED
    assert data_analysis.result, "Result should not be empty"
    assert len(data_analysis.result) == 12, "Result should have 12 leads"


@pytest.mark.asyncio
async def test_num_crosses_zero_signal_processor_empty_ecg(
    db_session: AsyncSession,
    user: User,
) -> None:
    ecg_dal = ECGDAL(db_session)
    ecg_id = uuid.uuid4()
    await ecg_dal.create(ECGModel(id=ecg_id, user_id=user.id))
    processor = NumCrossesZeroSignalProcessor(db_session)
    data_analysis = await processor.process(ecg_id)
    assert data_analysis.ecg_id == ecg_id
    assert data_analysis.name == "num_crosses_zero"
    assert data_analysis.status == AnalysisStatus.COMPLETED
    assert data_analysis.result == {}
