import asyncio
from contextlib import ExitStack
from unittest.mock import MagicMock
from httpx import AsyncClient

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from pytest_mock import MockerFixture
from app.config import settings
from app.models.database import Base, get_db_session, sessionmanager
from app.main import app as actual_app
from asyncpg import Connection
from sqlalchemy_utils import create_database, database_exists, drop_database
from app.schemas.user import User

from app.utils.auth import create_user

asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def app():
    with ExitStack():
        yield actual_app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(app=actual_app, base_url="http://test") as c:
        yield c


def run_migrations(connection: Connection):
    config = Config("app/alembic.ini")
    config.set_main_option("script_location", "app/alembic")
    config.set_main_option("sqlalchemy.url", settings.database_url)
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs("head", rev)

    context = MigrationContext.configure(
        connection, opts={"target_metadata": Base.metadata, "fn": upgrade}
    )

    with context.begin_transaction():
        with Operations.context(context):
            context.run_migrations()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Recreate test DB
    sync_db_url = settings.database_url.replace("+asyncpg", "")
    if database_exists(sync_db_url):
        drop_database(sync_db_url)
    create_database(sync_db_url)

    # Run alembic migrations on test DB
    async with sessionmanager.connect() as connection:
        await connection.run_sync(run_migrations)

    yield

    # Teardown
    if sessionmanager._engine is not None:
        await sessionmanager.close()


# Each test function is a clean slate
@pytest.fixture(scope="function", autouse=True)
async def transactional_session():
    async with sessionmanager.session() as session:
        try:
            await session.begin()
            yield session
        finally:
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())
            await session.commit()


@pytest.fixture(scope="function")
async def db_session(transactional_session):
    yield transactional_session


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, db_session):
    async def get_db_session_override():
        yield db_session

    app.dependency_overrides[get_db_session] = get_db_session_override


@pytest.fixture(scope="function")
async def admin_user(app, db_session) -> User:
    user = await create_user(db_session, "admin", "admin", is_superuser=True)
    return user


@pytest.fixture(scope="function")
async def user(app, db_session) -> User:
    user = await create_user(db_session, "user", "user", is_superuser=False)
    return user


@pytest.fixture(scope="function")
async def authenticated_client_admin(client, admin_user) -> AsyncClient:
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "admin",
            "password": "admin",
            "scope": "admin",
            "grant_type": "password",
        },
    )
    access_token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest.fixture(scope="function")
async def authenticated_client_user(client, user) -> AsyncClient:
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "user",
            "password": "user",
            "scope": "user",
            "grant_type": "password",
        },
    )
    access_token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest.fixture(scope="function", autouse=True)
def mock_process_tasks(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("app.api.routers.ecg.process_signals", MagicMock())
