import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Users as UserModel
from models.schemas.auth import User, UserCreate, UserUpdate
from crud_base import update_instance, read_instance, delete_instance


async def create_user(db: AsyncSession, user: User | UserCreate) -> UserModel:
    """Create user"""
    db_user = UserModel(**user.dict())
    db_user.id = uuid.uuid4()
    db.add(db_user)
    await db.flush()
    await db.commit()
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> UserModel | None:
    """Get user by id, return None if user with provided id does not exist"""
    return await read_instance(db=db, model=UserModel, condition=UserModel.id == user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> UserModel | None:
    """Get user by unique username, return None if user with provided username does not exist"""
    return await read_instance(db=db, model=UserModel, condition=UserModel.username == username)


async def get_user_by_email(db: AsyncSession, email: str) -> UserModel | None:
    """Get user by email, return None if user with provided email does not exist"""
    return await read_instance(db=db, model=UserModel, condition=UserModel.email == email)


async def update_user(db: AsyncSession, user_info: UserUpdate) -> UserModel:
    """Update user with provided data"""
    return await update_instance(db=db, model=UserModel, instance_id=user_info.id, data_dict=user_info.dict())
