from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form, Body, Header
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import HTTPErrorDetails
from models.schemas.auth import UserCreate, User
from db.database import get_db
from db.redis_inj import get_redis
from services.crud.users import create_user, get_user_by_email, get_user_by_username
from services.crud.refresh_tokens import create_token, get_tokens_by_user_id, get_token_by_token, \
    update_token_by_ua_uid, \
    delete_token, get_token_by_ua_uid
from services.password import get_hashed_password, verify_password
from services.jwt import create_access_token, create_refresh_token, JWTBearer, blacklisting, check_blacklist

router = APIRouter()


@router.post('/signup', response_model=User)
async def signup_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db=db, email=data.email) or await get_user_by_username(db=db, username=data.username):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=HTTPErrorDetails.CONFLICT.value)

    data.password_hash = get_hashed_password(data.password_hash)
    return await create_user(db=db, user=data)


@router.post('/login')
async def login_user(email: Annotated[str, Form()], password: Annotated[str, Form()],
                     db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis), user_agent: str = Header()):
    if not (user := await get_user_by_email(db=db, email=email)):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)
    if not verify_password(password=password, hashed_pass=user.password_hash):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)

    access, refresh = create_access_token(subject=user.id, useragent=user_agent), \
        create_refresh_token(subject=user.id, useragent=user_agent)

    if old_refresh_model_instance := await get_token_by_ua_uid(db=db, useragent=user_agent, user_id=user.id):
        await blacklisting(redis=redis, token=old_refresh_model_instance.refresh_token)
        await update_token_by_ua_uid(db=db, new_token=refresh, user_id=user.id, useragent=user_agent)
    else:
        await create_token(db=db, refresh_token=refresh, useragent=user_agent, user_id=user.id)
    return access, refresh


@router.post('/reroll')
async def reroll_tokens(refresh_token: Annotated[str, Body(embed=True)],
                        redis: Redis = Depends(get_redis), db: AsyncSession = Depends(get_db),
                        user_agent: str = Header()):
    if (token := JWTBearer.verify_jwt(refresh_token)) and not await check_blacklist(redis, refresh_token):
        access, refresh = create_access_token(subject=token['sub'], useragent=user_agent), \
            create_refresh_token(subject=token['sub'], useragent=user_agent)
        await update_token_by_ua_uid(db=db, new_token=refresh, user_id=token['sub'], useragent=token['useragent'])
        await blacklisting(redis=redis, token=refresh_token)
        return access, refresh
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Invalid token or expired token.")


@router.post('/logout')
async def logout(access_token: Annotated[str, Depends(JWTBearer())], user_agent: str = Header(),
                 redis: Redis = Depends(get_redis), db: AsyncSession = Depends(get_db)):
    if (access_payload := JWTBearer.verify_jwt(access_token)) and not await check_blacklist(redis, access_token):
        refresh_token_orm_instance = await get_token_by_ua_uid(db=db, useragent=user_agent, user_id=access_payload['sub'])
        await blacklisting(redis=redis, token=refresh_token_orm_instance.refresh_token)
        await blacklisting(redis=redis, token=access_token)
        await delete_token(db=db, refresh_token=refresh_token_orm_instance.refresh_token)
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    return HTTPStatus.OK
