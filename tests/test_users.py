import uuid
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Role, UserDAL
from app.schemas.user import User


@pytest.mark.asyncio
async def test_user_detail(authenticated_client_user: AsyncClient) -> None:
    response = await authenticated_client_user.get("/api/users/me")
    assert response.status_code == 200
    assert response.json().get("role") == "user"


@pytest.mark.parametrize(
    "username, password, role, expected_status_code",
    [
        ("test_user", "test_password", "admin", 201),  # admin user
        ("test_user", "test_password", "user", 201),  # regular user
        ("test_user", "test_password", "", 422),  # empty role
        ("test_user", "", "admin", 422),  # empty password
        ("test_user", "aaa", "admin", 422),  # password too short
        ("", "test_password", "admin", 422),  # empty username
        ("", "", "admin", 422),  # empty username and password
        ("", "", "", 422),  # empty username, password and role
        ("test_user", "test_password", "unknown", 422),  # unknown role
    ],
)
@pytest.mark.asyncio
async def test_user_create(
    authenticated_client_admin: AsyncClient,
    db_session: AsyncSession,
    username: str,
    password: str,
    role: Role,
    expected_status_code: int,
) -> None:
    response = await authenticated_client_admin.post(
        "/api/users/",
        json={"username": username, "password": password, "role": role},
    )
    assert response.status_code == expected_status_code, response.text
    if expected_status_code == 201:
        assert response.json().get("username") == username
        assert response.json().get("role") == role

    await (
        db_session.rollback()
    )  # rollback the transaction to avoid side effects between parametrized tests


@pytest.mark.asyncio
async def test_user_create_no_admin_permissions(
    authenticated_client_user: AsyncClient,
) -> None:
    response = await authenticated_client_user.post(
        "/api/users/",
        json={"username": "test_user", "password": "test_password", "role": "user"},
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Not enough permissions"


@pytest.mark.asyncio
async def test_user_create_already_exists(
    authenticated_client_admin: AsyncClient,
    user: User,
    db_session: AsyncSession,
) -> None:
    response = await authenticated_client_admin.post(
        "/api/users/",
        json={"username": user.username, "password": "user", "role": "user"},
    )
    assert response.status_code == 400
    assert response.json().get("detail") == "Username already registered"


@pytest.mark.parametrize(
    "username, status_code",
    [
        ("admin", 400),  # admin user (delete yourself)
        ("user", 200),  # regular user,
        ("unknown", 404),  # unknown user
    ],
)
@pytest.mark.asyncio
async def test_user_delete(
    authenticated_client_admin: AsyncClient,
    user: User,
    db_session: AsyncSession,
    username: str,
    status_code: int,
) -> None:
    user_dal = UserDAL(db_session)
    user_to_delete = await user_dal.get_by_username(username)
    user_id = user_to_delete.id if user_to_delete else uuid.uuid4()
    response = await authenticated_client_admin.delete(f"/api/users/{user_id}")
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json().get("username") == user_to_delete.username
        assert (await user_dal.get_by_username(user_to_delete.username)) is None


@pytest.mark.asyncio
async def test_list_users(
    authenticated_client_admin: AsyncClient,
    user: User,
    admin_user: User,
) -> None:
    response = await authenticated_client_admin.get("/api/users/")
    assert response.status_code == 200
    assert {e["username"] for e in response.json()} == {
        user.username,
        admin_user.username,
    }
