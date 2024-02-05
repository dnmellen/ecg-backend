import ijson
from fastapi.params import File
from pydantic import ValidationError
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep
from fastapi import APIRouter, HTTPException, UploadFile
from app.models.ecg import ECGDAL, Signal as SignalModel, ECG as ECGModel
from app.schemas.ecg import ECG, ECGDetail, Signal
from app.utils.core import BufferedStorage
from app.config import settings


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


@router.post(
    "/",
    response_model=ECG,
    status_code=201,
)
async def create_ecg(
    current_user: CurrentUserDep, db_session: DBSessionDep, file: UploadFile = File(...)
) -> ECG:
    """
    Create a new ecg
    """
    ecg_dal = ECGDAL(db_session)

    async def create_signals_callback(signals: list[Signal]) -> None:
        await ecg_dal.create_bulk(
            [
                SignalModel(
                    ecg_id=s.ecg,
                    date=s.date,
                    name=s.name,
                    signal_value=s.signal_value,
                    signal_value_index=s.signal_value_index,
                )
                for s in signals
            ]
        )

    signal_buffer = BufferedStorage[Signal](
        max_size=settings.max_signal_buffer,
        on_buffer_full_callback=create_signals_callback,
    )

    # Process the streamed JSON using ijson
    ecg_id: str | None = None
    ecg_date: str | None = None
    signal_value_index: int = 0
    signal_value: int | None = None
    lead_name: str | None = None

    try:
        parser = ijson.parse(file.file)
        for prefix, event, value in parser:
            match (prefix, event, value):
                case ("id", "string", _):
                    ecg_id = value

                    # Create a new ECG
                    try:
                        ecg_obj = ECG(id=ecg_id, user=current_user.id)
                    except ValidationError:
                        raise HTTPException(status_code=422, detail="Invalid input")
                    if existing_ecg := (
                        await ecg_dal.get_by_user(current_user.id, ecg_id)
                    ):
                        await ecg_dal.delete(existing_ecg)

                    await ecg_dal.create(ECGModel(id=ecg_obj.id, user_id=ecg_obj.user))

                case ("date", "string", _):
                    ecg_date = value
                case ("leads.item.name", "string", _):
                    lead_name = value
                case ("leads.item.signal", "start_array", _):
                    signal_value_index = 0
                case ("leads.item.signal", "end_array", _):
                    lead_name = None
                case ("leads.item.signal.item", "number", _):
                    signal_value = value

                    # Save the signal to the database
                    await signal_buffer.append(
                        Signal(
                            ecg=ecg_id,
                            date=ecg_date,
                            name=lead_name,
                            signal_value=signal_value,
                            signal_value_index=signal_value_index,
                        )
                    )

                    signal_value_index += 1
                case _:
                    pass
    except ijson.JSONError:
        raise HTTPException(status_code=422, detail="Invalid input")

    # Flush the remaining signals
    await signal_buffer.flush()

    if not ecg_id:
        raise HTTPException(status_code=422, detail="Invalid input")

    return ECG(id=ecg_id, user=current_user.id)


@router.get(
    "/{ecg_id}",
    response_model=ECG,
)
async def get_ecg(
    current_user: CurrentUserDep,
    ecg_id: str,
    db_session: DBSessionDep,
) -> ECGDetail:
    """
    Get an ecg by id with data insights
    """
    ecg_dal = ECGDAL(db_session)
    if not (ecg := await ecg_dal.get_by_user(current_user.id, ecg_id)):
        raise HTTPException(status_code=404, detail="ECG not found")
    return ECGDetail(id=ecg.id, user=ecg.user_id)
