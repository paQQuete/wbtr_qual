import uuid as builtin_uuid
from typing import Optional


from models.schemas.base import BaseSchemaModel, BaseFullModelMixin


class UserBase(BaseSchemaModel):
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]




class UserCreate(UserBase):
    password_hash: str


class UserUpdate(UserBase):
    id: builtin_uuid.UUID
    username: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class User(UserBase, BaseFullModelMixin):
    id: builtin_uuid.UUID

    class Config:
        orm_mode = True
