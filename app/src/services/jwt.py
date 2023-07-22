from functools import wraps
from datetime import datetime, timedelta
from typing import Union, Any

from jose import jwt

from core.config import SETTINGS


def create_token():
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
            to_encode = {"exp": exp_delta, "sub": str(kwargs['subject'])}
            encoded_jwt = jwt.encode(
                to_encode, SETTINGS.JWT.SECRET_KEY, SETTINGS.JWT.ALGORITHM
            )
            kwargs.update({
                '_encoded_jwt': encoded_jwt
            })
            return fn(*args, **kwargs)

        return decorator

    return wrapper


@create_token()
def create_access_token(subject: Union[str, Any], expires_delta: int = None, _encoded_jwt: str = None) -> str:
    return _encoded_jwt


@create_token()
def create_refresh_token(subject: Union[str, Any], expires_delta: int = None, _encoded_jwt: str = None) -> str:
    return _encoded_jwt
