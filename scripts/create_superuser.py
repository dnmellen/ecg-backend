import asyncio
from functools import wraps
from typing import Annotated
import typer
from app.utils.auth import create_user
from app.models.database import sessionmanager


def typer_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@typer_async
async def create_superuser(
    username: str,
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
) -> None:
    async with sessionmanager.session() as db_session:
        user = await create_user(db_session, username, password, is_superuser=True)
        print(f"Superuser {user.username} created successfully!")


if __name__ == "__main__":
    typer.run(create_superuser)
