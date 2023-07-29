from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form, Body
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import HTTPErrorDetails
from models.schemas.auth import UserCreate, User
from db.database import get_db
from db.redis_inj import get_redis
from services.crud.users import create_user, get_user_by_email, get_user_by_username
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
                     db: AsyncSession = Depends(get_db)):
    if not (user := await get_user_by_email(db=db, email=email)):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)
    if not verify_password(password=password, hashed_pass=user.password_hash):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)
    return create_access_token(subject=user.id), create_refresh_token(subject=user.id)


@router.post('/reroll')
async def reroll_tokens(refresh_token: Annotated[str, Body(embed=True)], redis: Redis = Depends(get_redis)):
    # TODO
    # для избежания проблемы с угоном рефреша (и с тем что угонщик сможет бесконечно получать аксесы по угнанному рефрешу) - нужно
    # писать в постгрю выданные рефреш токены.
    # (кейс взлома - Алиса работает, у неё Боб угоняет оба токена, Боб через время идёт менять рефреш на новые токены, гуляет с ними
    #  , в это время рефреш который у Алисы не сработает при обновлении аксесса, она логиниться и получают новую пару, но
    #  у Боба его полученный рефреш будет работать дальше)
    #
    # Чтобы этого избежать - нужно писать выданные рефреш токены, с отношением к юзеру, в таком случае кейс
    # Алиса работает, теряет оба токена, Боб роллит себе новый аксес по рефрешу, тем самым обновляя запись в постгре о рефреше -
    # Алиса не сможет получить новый аксес, т.к. по данныцм постгри рефреш у неё неактуальный, она логиниться заново, получает пару токенов,
    # актуальный рефреш Алисы заносится в постгрю, Боб сосёт бибу, профит.
    #
    #     план:
    #     написать модель для рефреш токенов в постгре DONE
    #     переделать миграции DONE
    #     круд для рефреш токенов
    #     дополнение ручек логин, логаут, рефреш токен
    #           (теперь не надо банить рефреш при обнове аксеса - мы защищены)??? че я написал, мб неправильноя строка

    # ВАЖНО - для того чтобы поддерживать схему на неск устройствах и оставаться безопасными - вводить в токены в постгрю отпечаток девайса
    # пусть это будет юзерагент
    # и должно быть ограничение на уникальность пары ЮА-ЮзерАйди, И ВАЖНО - девайс айди пишется в токены ТОЛЬКО в момент логина, так
    # при угоне токена и посл. роллов аксессов Боба - Алисин рефреш сразу инвалидируется, т.к. в постгре будет запись об актуальном рефреше который
    # сделал себе Боб. Алиса через 15 минут не сможет обновить аксесс - пойдет вводить логин и пароль, получит токены, актуальный токен для
    # этого устройства обновиться в постгре. ПРОФИТ

    if token := JWTBearer.verify_jwt(refresh_token) and not await check_blacklist(redis, refresh_token):
        await blacklisting(redis=redis, token=refresh_token)
        return create_access_token(subject=token['sub']), create_refresh_token(subject=token['sub'])
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Invalid token or expired token.")


@router.post('/logout')
async def logout(refresh_token: Annotated[str, Body(embed=True)], access_token: Annotated[str, Depends(JWTBearer())],
                 redis: Redis = Depends(get_redis)):
    if not await check_blacklist(redis=redis, token_or_jti=refresh_token):
        await blacklisting(redis=redis, token=refresh_token)
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    if not await check_blacklist(redis=redis, token_or_jti=access_token):
        await blacklisting(redis=redis, token=access_token)
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    return HTTPStatus.OK
