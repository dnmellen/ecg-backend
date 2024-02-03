from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from pydantic import ValidationError
from app import models
from app.api.dependencies.core import DBSessionDep
from app.schemas.auth import TokenData
from app.utils.auth import get_user, oauth2_scheme
from jose import JWTError, jwt

from app.config import settings


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: DBSessionDep,
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, settings.oauth_token_secret, algorithms=[settings.auth_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = await get_user(db_session, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


CurrentUserDep = Annotated[models.User, Security(get_current_user, scopes=["user"])]
CurrentAdminUserDep = Annotated[
    models.User, Security(get_current_user, scopes=["admin"])
]
