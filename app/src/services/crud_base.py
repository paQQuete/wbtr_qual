import uuid

from sqlalchemy import select, ClauseElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound


async def read_instance(db: AsyncSession, model, condition: ClauseElement):
    """Get an object by condition, return None if user with provided condition does not exist"""
    instance = await db.execute(select(model).where(condition))
    instance = instance.scalar()
    return instance if instance else None


async def update_instance(db: AsyncSession, model, instance_id: uuid.UUID, data_dict: dict):
    """Update an object, raise exception if the object with instance_id doesn't exist"""
    result = await db.execute(select(model).where(model.id == instance_id))
    instance = result.scalars().first()

    if instance:
        for key, value in data_dict.items():
            if value is not None:
                setattr(instance, key, value)
            await db.commit()
        await db.refresh(instance)
        return instance
    else:
        raise NoResultFound('Object with provided id does not exist')


async def delete_instance(db: AsyncSession, model, instance_id: uuid.UUID) -> str:
    """Delete an object, raise exception if the object with instance_id doesn't exist"""
    result = await db.execute(select(model).where(model.id == instance_id))
    instance = result.scalars().first()

    if instance is None:
        raise NoResultFound(f"No {model.__name__} found with id {instance_id}")

    await db.delete(instance)
    await db.commit()

    return f"{model.__name__} with id {instance_id} deleted successfully"
