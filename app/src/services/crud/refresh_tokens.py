from __future__ import annotations

import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from models.models import RefreshTokens as RefreshTokensModel
from services.crud.base import update_instance, read_instance, delete_instance, read_batch_instance


async def create_token(db: AsyncSession, refresh_token: str, useragent: str, user_id: uuid.UUID) -> RefreshTokensModel:
    """Create row with refresh token"""
    db_token = RefreshTokensModel(user_id=user_id, refresh_token=refresh_token,
                                  useragent=useragent)
    db_token.id = uuid.uuid4()
    db.add(db_token)
    await db.flush()
    await db.commit()
    return db_token


async def get_token_by_token(db: AsyncSession, refresh_token: str) -> RefreshTokensModel | None:
    """Get token by refresh_token, return None if token does not exist"""
    return await read_instance(db=db, model=RefreshTokensModel,
                               condition=RefreshTokensModel.refresh_token == refresh_token)


async def get_token_by_ua_uid(db: AsyncSession, useragent: str, user_id: uuid.UUID) -> RefreshTokensModel:
    return await read_instance(db=db, model=RefreshTokensModel,
                               condition=RefreshTokensModel.useragent == useragent and RefreshTokensModel.user_id == user_id)


async def get_tokens_by_user_id(db: AsyncSession, refresh_token: dict) -> list[RefreshTokensModel] | None:
    """Get refresh tokens by user id from provided token, return None if refresh tokens for this user do not exist
    :param refresh_token: decoded token payload dictionary
    :return: JWT access token
    """
    return await read_batch_instance(db=db, model=RefreshTokensModel,
                               condition=RefreshTokensModel.user_id == refresh_token['sub'])


async def update_token_by_ua_uid(db: AsyncSession, new_token: str, user_id: uuid.UUID, useragent) -> RefreshTokensModel:
    instance = await read_instance(db=db, model=RefreshTokensModel,
                                   condition=RefreshTokensModel.user_id == user_id and RefreshTokensModel.useragent == useragent)
    if instance:
        return await update_instance(
            db=db, model=RefreshTokensModel, instance_id=instance.id, data_dict={
                "user_id": user_id,
                "useragent": useragent,
                "updated_at": datetime.datetime.utcnow(),
                "refresh_token": new_token
            }
        )
    else:
        raise NoResultFound


async def delete_token(db: AsyncSession, refresh_token: str):
    """

    :param db:
    :param refresh_token: encoded JWT
    :return:
    """
    instance = await read_instance(db=db, model=RefreshTokensModel,
                                   condition=RefreshTokensModel.refresh_token == refresh_token)
    return await delete_instance(db=db, model=RefreshTokensModel, instance_id=instance.id)
