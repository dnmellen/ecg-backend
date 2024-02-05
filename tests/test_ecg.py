from io import BytesIO
import json
from unittest.mock import MagicMock
import uuid
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.processors import process_signals_task
from app.processors.num_crosses_zero import NumCrossesZeroSignalProcessor

from app.schemas.user import User

from tests.factories.ecg import generate_ecg_with_random_signals, generate_ecg_input


@pytest.mark.asyncio
async def test_list_ecgs(
    db_session: AsyncSession, user: User, authenticated_client_user: AsyncClient
) -> None:
    # Create ECG
    ecg_id = await generate_ecg_with_random_signals(db_session, user)

    response = await authenticated_client_user.get("/api/ecgs/")
    assert response.status_code == 200
    assert response.json() == [{"id": str(ecg_id), "user": str(user.id)}]


@pytest.mark.parametrize(
    "json_input, status_code",
    [
        (generate_ecg_input(num_signals=500), 201),  # valid input
        ("{}", 422),  # empty input
        ("", 422),  # empty input
        (json.dumps({"id": "123"}), 422),  # missing signals
        ("asdijasoidas", 422),  # invalid json
    ],
)
@pytest.mark.asyncio
async def test_create_ecg(
    db_session: AsyncSession,
    user: User,
    authenticated_client_user: AsyncClient,
    mock_process_tasks: MagicMock,
    json_input: str,
    status_code: int,
) -> None:
    # File like object with json_input data
    input_file = BytesIO(json_input.encode())

    response = await authenticated_client_user.post(
        "/api/ecgs/", files={"file": input_file}
    )
    assert response.status_code == status_code
    if status_code == 201:
        ecg_id = json.loads(json_input)["id"]
        assert response.json() == {
            "id": ecg_id,
            "user": str(user.id),
        }

        # Ensure a task was created
        mock_process_tasks.assert_called_once()

    await (
        db_session.rollback()
    )  # rollback the transaction to avoid side effects between parametrized tests


@pytest.mark.asyncio
async def test_create_ecg_twice(
    db_session: AsyncSession, user: User, authenticated_client_user: AsyncClient
) -> None:
    # Generate random ECG input
    json_input = generate_ecg_input(num_signals=500)

    for _ in range(2):
        # File like object with json_input data
        input_file = BytesIO(json_input.encode())

        response = await authenticated_client_user.post(
            "/api/ecgs/", files={"file": input_file}
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": json.loads(json_input)["id"],
            "user": str(user.id),
        }


@pytest.mark.parametrize(
    "create_ecg, run_task, status_code",
    [
        (True, True, 200),  # valid input
        (True, False, 200),  # valid input, no task
        (False, False, 404),  # invalid input, no task
    ],
)
@pytest.mark.asyncio
async def test_get_ecg_detail(
    db_session: AsyncSession,
    user: User,
    authenticated_client_user: AsyncClient,
    create_ecg: bool,
    run_task: bool,
    status_code: int,
) -> None:
    # Create ECG
    if create_ecg:
        ecg_id = await generate_ecg_with_random_signals(db_session, user)
    else:
        ecg_id = uuid.uuid4()

    # Process signals manually
    if run_task:
        processor = NumCrossesZeroSignalProcessor(db_session)
        await process_signals_task(processor, ecg_id)

    # Get ECG detail
    response = await authenticated_client_user.get(f"/api/ecgs/{ecg_id}")
    assert response.status_code == status_code
    if response.status_code == 200:
        data = response.json()
        assert data["id"] == str(ecg_id)
        assert data["user"] == str(user.id)
        if run_task:
            assert len(data["analyses"]) == 1
            assert data["analyses"][0]["name"] == "num_crosses_zero"
            assert data["analyses"][0]["status"] == "completed"
            assert data["analyses"][0]["result"].keys() == {
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
            }
        else:
            assert len(data["analyses"]) == 0
    await (
        db_session.rollback()
    )  # rollback the transaction to avoid side effects between parametrized tests
