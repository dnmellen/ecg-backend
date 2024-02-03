from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentAdminUserDep, CurrentUserDep
from app.schemas.user import Role, User, UserCreate
from fastapi import APIRouter

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
    return await create_user_func(
        db_session,
        new_user.username,
        new_user.password,
        is_superuser=new_user.role == Role.ADMIN,
    )
