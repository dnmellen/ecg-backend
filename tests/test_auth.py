from httpx import AsyncClient
import pytest
from app.models.user import User


@pytest.mark.asyncio
async def test_get_auth_token(client: AsyncClient, admin_user: User) -> None:
    assert admin_user.role == "admin"
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "admin",
            "password": "admin",
            "scope": "admin",
            "grant_type": "password",
        },
    )

    assert response.status_code == 200
    assert response.json().get("access_token")
    assert response.json().get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_get_auth_token_user_not_admin(client: AsyncClient, user: User) -> None:
    assert user.role == "user"
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "user",
            "password": "user",
            "scope": "admin",
            "grant_type": "password",
        },
    )
    assert response.status_code == 400
    assert response.json().get("detail") == "User does not have admin permissions"
