import os

from datetime import datetime, timedelta

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlalchemy import select

########################################################################################

from quantumion.server.model import Token, User

from quantumion.server.database import UserInDB, db_dependency

########################################################################################

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

########################################################################################


def generate_token(username, user_id):
    expires = datetime.utcnow() + timedelta(
        minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    encode = {"id": user_id, "sub": username, "exp": expires}
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if not username is None and not user_id is None:
            return User(username=username, user_id=user_id)
        raise JWTError

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


user_dependency = Annotated[User, Depends(current_user)]

# ########################################################################################


@auth_router.post("/token")
async def request_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    query = await db.execute(
        select(UserInDB).filter(UserInDB.username == form_data.username)
    )
    user_in_db = query.scalars().first()
    if (
        user_in_db
        and pwd_context.verify(form_data.password, user_in_db.hashed_password)
        and not user_in_db.disabled
    ):
        token = generate_token(user_in_db.username, user_in_db.user_id)
        return Token(access_token=token, token_type="bearer")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
