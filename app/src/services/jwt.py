import uuid
from functools import wraps
from datetime import datetime, timedelta
from typing import Union, Any

from jose import jwt
from redis.asyncio.client import Redis

from core.config import SETTINGS


def _create_token():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            exp_delta = kwargs.get('expires_delta', None)
            token_type = 'access' if fn.__name__ == 'create_access_token' else 'refresh'
            if exp_delta:
                exp_delta = datetime.utcnow() + timedelta(minutes=exp_delta)
            else:
                exp_delta = datetime.utcnow() + timedelta(
                    minutes=SETTINGS.JWT.ACCESS_TOKEN_EXPIRE_MINUTES
                    if token_type == 'access' else SETTINGS.JWT.REFRESH_TOKEN_EXPIRE_MINUTES
                )
            to_encode = {
                "exp": exp_delta,
                "sub": str(kwargs['subject']),
                "iss": SETTINGS.PROJECT,
                "nbf": datetime.utcnow(),
                "jti": uuid.uuid4(),
                "iat": datetime.utcnow()
            }
            encoded_jwt = jwt.encode(
                to_encode, SETTINGS.JWT.SECRET_KEY, SETTINGS.JWT.ALGORITHM
            )
            kwargs.update({
                '_encoded_jwt': encoded_jwt
            })
            return fn(*args, **kwargs)

        return decorator

    return wrapper


@_create_token()
def create_access_token(subject: Union[str, Any], expires_delta: int = None, _encoded_jwt: str = None) -> str:
    """

    :param subject: id of user
    :param expires_delta: expires in minutes
    :param _encoded_jwt:
    :return: JWT access token
    """
    return _encoded_jwt


@_create_token()
def create_refresh_token(subject: Union[str, Any], expires_delta: int = None, _encoded_jwt: str = None) -> str:
    """

    :param subject: id of user
    :param expires_delta: expires in minutes
    :param _encoded_jwt:
    :return: JWT refresh token
    """
    return _encoded_jwt


async def blacklisting(redis: Redis, token_or_jti: Union[uuid.UUID, str]) -> bool:
    if isinstance(token_or_jti, str):
        await redis.set(
            name=(token := jwt.decode(
                token_or_jti,
                key=SETTINGS.JWT.SECRET_KEY,
                algorithms=SETTINGS.JWT.ALGORITHM
            )['payload']['jti']),
            value=True,
            exat=token['payload']['exp'] - str(datetime.utcnow().timestamp())
        )
        return True
    elif isinstance(token_or_jti, uuid.UUID):
        await redis.set(name=token_or_jti, exat=SETTINGS.JWT.REFRESH_TOKEN_EXPIRE_MINUTES * 60)
        return True


async def check_blacklist(redis: Redis, token_or_jti: Union[uuid.UUID, str]) -> bool:
    if isinstance(token_or_jti, str):
        bltoken = await redis.get(name=jwt.decode(token_or_jti,
                                                  key=SETTINGS.JWT.SECRET_KEY,
                                                  algorithms=SETTINGS.JWT.ALGORITHM)['payload']['jti'])
        return True if bltoken else False
    elif isinstance(token_or_jti, uuid.UUID):
        bltoken = await redis.get(name=token_or_jti)
        return True if bltoken else False
