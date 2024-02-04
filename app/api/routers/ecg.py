from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep
from fastapi import APIRouter
from app.models.ecg import ECGDAL
from app.schemas.ecg import ECG


router = APIRouter(
    prefix="/api/ecgs",
    tags=["ecgs"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    response_model=list[ECG],
)
async def list_ecgs(
    current_user: CurrentUserDep,
    db_session: DBSessionDep,
) -> list[ECG]:
    """
    Get all ecgs for the current user
    """
    ecg_dal = ECGDAL(db_session)
    results = await ecg_dal.list_by_user(current_user.id)
    ecgs = [ECG(id=ecg.id, user=ecg.user_id) for ecg in results]
    return ecgs
