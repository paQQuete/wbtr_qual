from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form, Body
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import HTTPErrorDetails
from models.schemas.auth import UserCreate, User
from db.database import get_db
from db.redis_inj import get_redis
from services.crud.users import create_user, get_user_by_email, get_user_by_username
from services.password import get_hashed_password, verify_password
from services.jwt import create_access_token, create_refresh_token, JWTBearer, blacklisting

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post('/signup', response_model=User)
async def signup_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db=db, email=data.email) or await get_user_by_username(db=db, username=data.username):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=HTTPErrorDetails.CONFLICT.value)

    data.password_hash = get_hashed_password(data.password_hash)
    return await create_user(db=db, user=data)


@router.post('/login')
async def login_user(email: Annotated[str, Form()], password: Annotated[str, Form()],
                     db: AsyncSession = Depends(get_db)):
    if not (user := await get_user_by_email(db=db, email=email)):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)
    if not verify_password(password=password, hashed_pass=user.password_hash):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)
    return create_access_token(subject=user.id), create_refresh_token(subject=user.id)


@router.post('/just_check')
async def check_token(token=Depends(JWTBearer())):
    return token


@router.post('/logout')
async def logout(refresh_token: str, access_token=Depends(JWTBearer()), redis: Redis = Depends(get_redis)):
    await blacklisting(redis=redis, token_or_jti=refresh_token)
    await blacklisting(redis=redis, token_or_jti=access_token)
    return HTTPStatus.OK


@router.post('/logout_debug')
async def logout_debg(refresh_token: Annotated[str, Body(embed=True)], access_token: Annotated[str, Depends(oauth2_scheme)],
                      redis: Redis = Depends(get_redis)):
    await blacklisting(redis=redis, token_or_jti=refresh_token)
    await blacklisting(redis=redis, token_or_jti=access_token)
    # TODO
    #  File "/home/boris/PycharmProjects/wbtr_qual/app/src/api/v1/auth.py", line 56, in logout_debg
    #     await blacklisting(redis=redis, token_or_jti=access_token)
    #   File "/home/boris/PycharmProjects/wbtr_qual/app/src/services/jwt.py", line 74, in blacklisting
    #     token = jwt.decode(
    #             ^^^^^^^^^^^
    #   File "/home/boris/PycharmProjects/wbtr_qual/venv/lib/python3.11/site-packages/jose/jwt.py", line 157, in decode
    #     _validate_claims(
    #   File "/home/boris/PycharmProjects/wbtr_qual/venv/lib/python3.11/site-packages/jose/jwt.py", line 481, in _validate_claims
    #     _validate_exp(claims, leeway=leeway)
    #   File "/home/boris/PycharmProjects/wbtr_qual/venv/lib/python3.11/site-packages/jose/jwt.py", line 314, in _validate_exp
    #     raise ExpiredSignatureError("Signature has expired.")
    # jose.exceptions.ExpiredSignatureError: Signature has expired.
    return HTTPStatus.OK
