from pydantic import UUID4
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentAdminUserDep, CurrentUserDep
from app.models.user import UserDAL
from app.schemas.user import Role, User, UserCreate
from fastapi import APIRouter, HTTPException

from app.utils.auth import get_user, create_user as create_user_func

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/me",
    response_model=User,
)
async def user_details(
    current_user: CurrentUserDep,
    db_session: DBSessionDep,
):
    """
    Get any user details
    """
    user = await get_user(db_session, current_user.username)
    return user


@router.post("/", response_model=User, status_code=201)
async def create_user(
    current_user: CurrentAdminUserDep,
    new_user: UserCreate,
    db_session: DBSessionDep,
) -> User:
    """
    Create a new user
    """
    user_dal = UserDAL(db_session)
    if await user_dal.get_by_username(new_user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    return await create_user_func(
        db_session,
        new_user.username,
        new_user.password,
        is_superuser=new_user.role == Role.ADMIN,
    )


@router.delete("/{user_id}", response_model=User)
async def delete_user(
    current_user: CurrentAdminUserDep,
    db_session: DBSessionDep,
    user_id: UUID4,
) -> User:
    """
    Delete a user
    """
    user_dal = UserDAL(db_session)
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    user = await user_dal.get(user_id)
    if user:
        await user_dal.delete(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get(
    "/",
    response_model=list[User],
)
async def list_users(
    current_user: CurrentAdminUserDep,
    db_session: DBSessionDep,
) -> list[User]:
    """
    Get all users
    """
    user_dal = UserDAL(db_session)
    results = await user_dal.list()
    return [e[0] for e in results]
