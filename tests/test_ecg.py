from io import BytesIO
import json
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

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
        assert response.json() == {
            "id": json.loads(json_input)["id"],
            "user": str(user.id),
        }

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
