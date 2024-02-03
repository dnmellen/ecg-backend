from datetime import timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies.core import DBSessionDep
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.auth import Token
from app.schemas.user import Role
from app.utils.auth import authenticate_user, create_access_token
from app.config import settings

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/token",
    response_model=Token,
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: DBSessionDep,
) -> Token:
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.auth_access_token_expire_minutes)

    if Role.ADMIN in form_data.scopes:
        if user.role != Role.ADMIN:
            raise HTTPException(
                status_code=400, detail="User does not have admin permissions"
            )

    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
