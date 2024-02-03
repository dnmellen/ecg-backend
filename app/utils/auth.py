from datetime import datetime, timedelta, timezone

from fastapi.security import (
    OAuth2PasswordBearer,
)
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.schemas.user import Role, User, UserInDB
from app.config import settings
from app.models.user import UserDAL, User as UserModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    scopes={Role.ADMIN: "Create users", Role.USER: "Submit ECG data, view own data"},
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(db_session, username: str) -> UserInDB:
    user_dal = UserDAL(db_session)
    user = await user_dal.get_by_username(username)
    if user:
        return UserInDB.model_validate(user)


async def authenticate_user(db_session, username: str, password: str):
    user = await get_user(db_session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.oauth_token_secret, algorithm=settings.auth_algorithm
    )
    return encoded_jwt


async def create_user(
    db_session: Session, username: str, password: str, is_superuser: bool = False
) -> User:
    user_dal = UserDAL(db_session)
    user = await user_dal.create(
        UserModel(
            **UserInDB(
                username=username,
                hashed_password=get_password_hash(password),
                role=Role.ADMIN if is_superuser else Role.USER,
            ).model_dump()
        )
    )
    return User.model_validate(user)
