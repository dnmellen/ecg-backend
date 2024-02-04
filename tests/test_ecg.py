from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ecg import ECGDAL, SignalDAL
from app.schemas.user import User
from app.models import ECG as ECGModel, Signal as SignalModel

from tests.factories.ecg import generate_signals


@pytest.mark.asyncio
async def test_list_ecgs(
    db_session: AsyncSession, user: User, authenticated_client_user: AsyncClient
) -> None:
    # Create ECG
    ecg_dal = ECGDAL(db_session)
    ecg = await ecg_dal.create(ECGModel(user_id=user.id))

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
            for s in generate_signals(ecg.id, 10)
        )
    )

    response = await authenticated_client_user.get("/api/ecgs/")
    assert response.status_code == 200
    assert response.json() == [{"id": str(ecg.id), "user": str(user.id)}]
